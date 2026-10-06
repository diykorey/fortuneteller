"""Release-day moves: the close before each CPI release, and the move to the first close after it."""

from datetime import date, datetime
from pathlib import Path
from typing import NoReturn

import duckdb
import pytest

from fortuneteller import db, flows, sources
from fortuneteller.__main__ import describe_release_counts, main
from fortuneteller.models import DailyBar
from fortuneteller.sources import (
    FirstRelease,
    YahooError,
    DailyClosingPrice,
    parse_daily_bars,
)
from fortuneteller.flows import (
    CPI_EVENT_TYPE,
    store_releases,
    to_event_instance,
)
from fortuneteller.study import (
    BEFORE_HISTORY,
    MVP_PRICE_SERIES,
    NO_CLOSE_NEARBY,
    ReleaseCounts,
    closing_price_before_after,
    release_move,
    store_observations,
)

GSPC_2022 = Path(__file__).parent / "data" / "yahoo_gspc_2022_09.json"
# August 2022 CPI: released 2022-09-13, the S&P 500's worst day in two years.
HOT_PRINT = FirstRelease(date(2022, 8, 1), date(2022, 9, 13), 296.171)


def _closes(*days: tuple[int, int, int]) -> list[DailyClosingPrice]:
    return [DailyClosingPrice(date(*day), 100.0 + i) for i, day in enumerate(days)]


def test_weekday_release_uses_the_previous_trading_day_and_the_same_day() -> None:
    # given closes on Monday 2022-09-12 and Tuesday 2022-09-13
    closes = _closes((2022, 9, 12), (2022, 9, 13))

    # when the pair around a Tuesday release is found
    pair = closing_price_before_after(closes, date(2022, 9, 13))

    # then the move runs from Monday's close to Tuesday's
    assert pair == (closes[0], closes[1])


def test_sunday_release_uses_friday_and_monday() -> None:
    # given closes on Friday 1992-12-11 and Monday 1992-12-14
    closes = _closes((1992, 12, 11), (1992, 12, 14))

    # when the pair around the Sunday 1992-12-13 release is found
    pair = closing_price_before_after(closes, date(1992, 12, 13))

    # then the first reaction is Monday's close
    assert pair == (closes[0], closes[1])


def test_four_day_gap_after_a_long_weekend_is_kept() -> None:
    # given a Friday close and the next on Tuesday, after a Monday holiday
    closes = _closes((2024, 5, 24), (2024, 5, 28))

    # when the pair around a Tuesday release is found
    pair = closing_price_before_after(closes, date(2024, 5, 28))

    # then Friday, four days back, still counts as the close before
    assert pair == (closes[0], closes[1])


def test_five_day_gap_is_skipped() -> None:
    # given the real 1978 hole: a close on Friday 05-26, none on Tuesday 05-30, then Wednesday 05-31
    closes = _closes((1978, 5, 26), (1978, 5, 31))

    # when the pair around the Wednesday 1978-05-31 release is found
    pair = closing_price_before_after(closes, date(1978, 5, 31))

    # then five days back is too far to call it the day before
    assert pair == NO_CLOSE_NEARBY


def test_next_close_too_far_after_the_release_is_skipped() -> None:
    # given a close the day before a release and the next one a week later
    closes = _closes((2022, 9, 12), (2022, 9, 20))

    # when / then there is no reaction close within reach
    assert closing_price_before_after(closes, date(2022, 9, 13)) == NO_CLOSE_NEARBY


def test_release_before_or_on_the_first_close_is_before_history() -> None:
    # given gold's history starting on 2000-08-30
    closes = _closes((2000, 8, 30), (2000, 8, 31))

    # when / then releases before or on that first day have no close before them
    assert closing_price_before_after(closes, date(1990, 1, 12)) == BEFORE_HISTORY
    assert closing_price_before_after(closes, date(2000, 8, 30)) == BEFORE_HISTORY


def test_release_after_the_last_close_is_skipped_not_an_error() -> None:
    # given closes that end before a release
    closes = _closes((2026, 9, 10), (2026, 9, 11))

    # when / then a later release has no reaction close yet
    assert closing_price_before_after(closes, date(2026, 10, 14)) == NO_CLOSE_NEARBY


def test_move_is_relative_for_prices_and_in_basis_points_for_yields() -> None:
    # given the S&P 500 and the 10-year yield on 2022-09-12 and 2022-09-13
    spx = (
        DailyClosingPrice(date(2022, 9, 12), 4110.41),
        DailyClosingPrice(date(2022, 9, 13), 3932.69),
    )
    tnx = (DailyClosingPrice(date(2022, 9, 12), 3.362), DailyClosingPrice(date(2022, 9, 13), 3.422))

    # when their moves are computed
    # then the price falls 4.32% and the yield rises 6 bps
    assert release_move(*spx, "pct") == pytest.approx(-0.0432, abs=1e-4)
    assert release_move(*tnx, "bps") == pytest.approx(6.0)


def test_unknown_unit_is_rejected() -> None:
    # given two closes and a misspelt unit
    closes = _closes((2022, 9, 12), (2022, 9, 13))

    # when / then the move is refused rather than quietly computed as a percentage
    with pytest.raises(ValueError, match="unknown unit 'bp'"):
        release_move(closes[0], closes[1], "bp")


def _store(
    time_zone: str = "UTC", closes: dict[str, list[DailyClosingPrice]] | None = None
) -> duckdb.DuckDBPyConnection:
    # Every MVP instrument gets the S&P 500 closes around the hot print unless overridden.
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{time_zone}'")
    db.init_db(con=con)
    store_releases(CPI_EVENT_TYPE, [HOT_PRINT], con=con)
    spx = parse_daily_bars(GSPC_2022.read_bytes())
    for instrument in MVP_PRICE_SERIES:
        bars = _bars(instrument, (closes or {}).get(instrument, spx))
        db.insert_models("daily_bars", bars, con=con)
    return con


def _bars(instrument: str, closes: list[DailyClosingPrice]) -> list[DailyBar]:
    return [DailyBar(instrument=instrument, day=c.day, close=c.price, source="s") for c in closes]


def _spx_row(con: duckdb.DuckDBPyConnection) -> dict[str, object]:
    cursor = con.execute("SELECT * FROM observations WHERE instrument = 'SPY / ES'")
    row = cursor.fetchone()
    assert row is not None
    return dict(zip([c[0] for c in cursor.description or []], row, strict=True))


def test_known_day_is_measured_through_the_store() -> None:
    # given the hot print released 2022-09-13, closes around it, and a non-UTC session
    con = _store("Europe/Kyiv")

    # when the observations are built
    release_counts = store_observations(con=con)

    # then the S&P 500 row holds the close before and the 4.32% fall
    observation = _spx_row(con)
    assert observation["event_id"] == 1_2022_09_13
    assert observation["px_t0"] == pytest.approx(4110.41)
    assert observation["ret_unit"] == "pct"
    assert observation["ret_1d"] == pytest.approx(-0.0432, abs=1e-4)
    assert observation["data_source"] == "yahoo"
    assert observation["quality"] == "daily_close"
    assert observation["ret_5m"] is None and observation["abn_ret_1d"] is None
    assert release_counts[CPI_EVENT_TYPE]["SPY / ES"] == ReleaseCounts(measured=1)


def test_yield_move_is_stored_in_basis_points() -> None:
    # given the 10-year yield on the day before and the day of the hot print
    tnx = [DailyClosingPrice(date(2022, 9, 12), 3.362), DailyClosingPrice(date(2022, 9, 13), 3.422)]
    con = _store(closes={"UST10Y / ZN": tnx})

    # when the observations are built
    store_observations(con=con)

    # then the row belongs to the release and is measured in bps
    row = con.execute(
        "SELECT event_id, ret_unit, ret_1d FROM observations WHERE instrument = 'UST10Y / ZN'"
    ).fetchone()
    assert row == (1_2022_09_13, "bps", pytest.approx(6.0))


def test_release_before_an_instruments_history_is_counted_not_stored() -> None:
    # given gold prices that start only after the hot print
    gold = [
        DailyClosingPrice(date(2022, 10, 3), 1702.0),
        DailyClosingPrice(date(2022, 10, 4), 1731.0),
    ]
    con = _store(closes={"GC / XAU": gold})

    # when the observations are built
    release_counts = store_observations(con=con)

    # then gold has no row, and the counts say why
    assert release_counts[CPI_EVENT_TYPE]["GC / XAU"] == ReleaseCounts(skipped_before_history=1)
    rows = con.execute("SELECT count(*) FROM observations WHERE instrument = 'GC / XAU'").fetchone()
    assert rows == (0,)


def test_instrument_without_any_prices_fails_loudly() -> None:
    # given no VIX prices at all, as if its load had failed
    con = _store(closes={"VIX": []})

    # when / then building refuses, rather than calling every release "before VIX's history"
    with pytest.raises(ValueError, match="no daily_bars for VIX"):
        store_observations(con=con)


def test_a_release_after_the_close_is_measured_from_that_close() -> None:
    # given the hot print stamped 22:00 New York time on 09-13, after the S&P 500 closed
    con = _store()
    late = to_event_instance(HOT_PRINT, CPI_EVENT_TYPE).model_copy(
        update={"event_ts": datetime(2022, 9, 14, 2, 0)}
    )
    db.insert_models("event_instances", [late], con=con, replace=True)

    # when the observations are built
    store_observations(con=con)

    # then the move starts at 09-13's close, the last one before the print, not 09-12's
    assert _spx_row(con)["px_t0"] == pytest.approx(3932.69, abs=0.01)


def test_rebuilding_removes_a_row_that_no_longer_applies() -> None:
    # given an S&P 500 observation built for the hot print
    con = _store()
    store_observations(con=con)

    # when the closes before the release disappear and the observations are rebuilt
    con.execute("DELETE FROM daily_bars WHERE instrument = 'SPY / ES' AND day < DATE '2022-09-13'")
    release_counts = store_observations(con=con)

    # then the old row is gone, so the table matches what this run measured
    assert release_counts[CPI_EVENT_TYPE]["SPY / ES"] == ReleaseCounts(skipped_before_history=1)
    rows = con.execute("SELECT count(*) FROM observations WHERE instrument = 'SPY / ES'").fetchone()
    assert rows == (0,)
    assert db.count_rows("observations", con=con) == 4


def test_rerunning_changes_no_count_and_events_can_still_be_reloaded() -> None:
    # given observations already built for the hot print
    con = _store()
    store_observations(con=con)

    # when the observations are rebuilt and the events they point at are stored again
    store_observations(con=con)
    store_releases(CPI_EVENT_TYPE, [HOT_PRINT], con=con)

    # then nothing is duplicated and the foreign key does not block the event reload
    assert db.count_rows("observations", con=con) == 5
    assert db.count_rows("event_instances", con=con) == 1


def test_every_event_type_is_measured_and_counted_on_its_own() -> None:
    # given a jobs report on the same day as the hot print
    con = _store()
    store_releases(flows.NFP_EVENT_TYPE, [HOT_PRINT], con=con)

    # when the observations are built
    release_counts = store_observations(con=con)

    # then both events are measured, and each type's releases are counted separately
    rows = con.execute("SELECT DISTINCT event_id FROM observations ORDER BY 1").fetchall()
    assert rows == [(1_2022_09_13,), (2_2022_09_13,)]
    assert list(release_counts) == [CPI_EVENT_TYPE, flows.NFP_EVENT_TYPE]
    assert release_counts[flows.NFP_EVENT_TYPE]["SPY / ES"] == ReleaseCounts(measured=1)


DXY_1992 = Path(__file__).parent / "data" / "yahoo_dx_y_nyb_1992_12.json"


def _yahoo_answers(monkeypatch: pytest.MonkeyPatch, gold: Path = GSPC_2022) -> None:
    # Every ticker answers with the S&P 500 bars around the hot print; gold can be overridden.
    def fetch(ticker: str) -> bytes:
        return (gold if ticker == "GC=F" else GSPC_2022).read_bytes()

    monkeypatch.setattr(sources, "fetch_daily_bars", fetch)


def test_load_prices_prints_counts_per_instrument_and_in_total(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the hot print loaded, and gold's saved prices ending decades before it
    store_releases(CPI_EVENT_TYPE, [HOT_PRINT])
    _yahoo_answers(monkeypatch, gold=DXY_1992)

    # when the command runs twice
    first = main(["load-prices"])
    second = main(["load-prices"])

    # then both runs report the same measurement, and nothing is duplicated
    assert (first, second) == (0, 0)
    report = (
        "CPI / inflation surprise\n"
        "SPY / ES     1 observations\n"
        "UST10Y / ZN  1 observations\n"
        "DXY          1 observations\n"
        "GC / XAU     0 observations, 1 skipped (no close within 4 days)\n"
        "VIX          1 observations\n"
        "5 instruments × 1 releases = 4 observations\n"
    )
    assert capsys.readouterr().out == report * 2
    assert db.count_rows("observations") == 4


def test_load_prices_needs_the_releases_first(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given no CPI releases loaded
    def fetch(_ticker: str) -> NoReturn:
        raise AssertionError("fetched prices with no releases to measure")

    monkeypatch.setattr(sources, "fetch_daily_bars", fetch)

    # when the command runs
    code = main(["load-prices"])

    # then it stops before fetching and says what to run first
    assert code == 1
    assert "run `fortuneteller load-releases` first" in capsys.readouterr().err


def test_load_prices_reports_a_yahoo_failure(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the releases loaded and Yahoo rejecting the request
    store_releases(CPI_EVENT_TYPE, [HOT_PRINT])

    def fetch(ticker: str) -> NoReturn:
        raise YahooError(f"Yahoo returned HTTP 404 for {ticker}")

    monkeypatch.setattr(sources, "fetch_daily_bars", fetch)

    # when the command runs
    code = main(["load-prices"])

    # then it exits non-zero with the reason, and measures nothing
    assert code == 1
    assert "HTTP 404 for ^GSPC" in capsys.readouterr().err
    assert db.count_rows("observations") == 0


def test_each_skip_reason_is_named() -> None:
    # given counts with both kinds of skip, as for gold and the 10-year yield on real data
    counts = ReleaseCounts(measured=312, skipped_before_history=337, skipped_no_close_nearby=2)

    # when the line is written
    line = describe_release_counts("GC / XAU", counts)

    # then each skip says why
    assert line == (
        "GC / XAU     312 observations, 337 skipped (before its history), "
        "2 skipped (no close within 4 days)"
    )


def test_load_prices_reports_a_malformed_reply(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the releases loaded and Yahoo answering with a page that is not JSON
    store_releases(CPI_EVENT_TYPE, [HOT_PRINT])
    monkeypatch.setattr(sources, "fetch_daily_bars", lambda _ticker: b"<html>consent</html>")

    # when the command runs
    code = main(["load-prices"])

    # then it exits non-zero with a message instead of a traceback, and stores nothing
    assert code == 1
    assert "load-prices:" in capsys.readouterr().err
    assert db.count_rows("daily_bars") == 0
