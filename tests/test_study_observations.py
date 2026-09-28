"""Release-day moves: the close before each CPI release, and the move to the first close after it."""

from datetime import date
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db
from fortuneteller.models import DailyBar, EventInstance
from fortuneteller.study import (
    BEFORE_HISTORY,
    NO_CLOSE_NEARBY,
    CpiRelease,
    ReleaseCounts,
    DailyClosingPrice,
    closing_price_before_after,
    parse_daily_bars,
    release_move,
    store_cpi_releases,
    store_observations,
    to_event_instance,
)

GSPC_2022 = Path(__file__).parent / "data" / "yahoo_gspc_2022_09.json"
# August 2022 CPI: released 2022-09-13, the S&P 500's worst day in two years.
HOT_PRINT = CpiRelease(date(2022, 8, 1), date(2022, 9, 13), 296.171)


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


def _store(time_zone: str = "UTC") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{time_zone}'")
    db.init_db(con=con)
    store_cpi_releases([HOT_PRINT], con=con)
    return con


def _bars(instrument: str, closes: list[DailyClosingPrice]) -> list[DailyBar]:
    return [DailyBar(instrument=instrument, day=c.day, close=c.price, source="s") for c in closes]


def test_known_day_is_measured_through_the_store() -> None:
    # given the hot print released 2022-09-13, S&P 500 closes around it, and a non-UTC session
    con = _store("Europe/Kyiv")
    db.insert_models(
        "daily_bars", _bars("SPY / ES", parse_daily_bars(GSPC_2022.read_bytes())), con=con
    )

    # when the observations are built
    release_counts = store_observations(con=con)

    # then the S&P 500 row holds the close before and the 4.32% fall, and the others have no history
    cursor = con.execute("SELECT * FROM observations")
    row = cursor.fetchone()
    assert row is not None
    observation = dict(zip([c[0] for c in cursor.description or []], row, strict=True))
    assert observation["obs_id"] == 2022080
    assert observation["event_id"] == 202208
    assert observation["instrument"] == "SPY / ES"
    assert observation["px_t0"] == pytest.approx(4110.41)
    assert observation["ret_unit"] == "pct"
    assert observation["ret_1d"] == pytest.approx(-0.0432, abs=1e-4)
    assert observation["data_source"] == "yahoo"
    assert observation["quality"] == "daily_close"
    assert observation["ret_5m"] is None and observation["abn_ret_1d"] is None
    assert release_counts["SPY / ES"] == ReleaseCounts(measured=1)
    assert release_counts["VIX"] == ReleaseCounts(skipped_before_history=1)


def test_yield_move_is_stored_in_basis_points() -> None:
    # given the 10-year yield on the day before and the day of the hot print
    con = _store()
    tnx = [DailyClosingPrice(date(2022, 9, 12), 3.362), DailyClosingPrice(date(2022, 9, 13), 3.422)]
    db.insert_models("daily_bars", _bars("UST10Y / ZN", tnx), con=con)

    # when the observations are built
    store_observations(con=con)

    # then the row is numbered by the instrument's position and measured in bps
    row = con.execute("SELECT obs_id, ret_unit, ret_1d FROM observations").fetchone()
    assert row == (2022081, "bps", pytest.approx(6.0))


def test_rerunning_changes_no_count_and_events_can_still_be_reloaded() -> None:
    # given observations already built for the hot print
    con = _store()
    db.insert_models(
        "daily_bars", _bars("SPY / ES", parse_daily_bars(GSPC_2022.read_bytes())), con=con
    )
    store_observations(con=con)

    # when the observations are rebuilt and the events they point at are stored again
    store_observations(con=con)
    store_cpi_releases([HOT_PRINT], con=con)

    # then nothing is duplicated and the foreign key does not block the event reload
    assert db.count_rows("observations", con=con) == 1
    assert db.count_rows("event_instances", con=con) == 1


def test_events_of_other_types_are_not_measured() -> None:
    # given a non-CPI event on the same day as the hot print
    con = _store()
    other = to_event_instance(HOT_PRINT).model_copy(
        update={"event_id": 1, "event_type": "NFP / labor data"}
    )
    db.insert_models("event_instances", [EventInstance.model_validate(other.model_dump())], con=con)
    db.insert_models(
        "daily_bars", _bars("SPY / ES", parse_daily_bars(GSPC_2022.read_bytes())), con=con
    )

    # when the observations are built
    store_observations(con=con)

    # then only the CPI event is measured
    rows = con.execute("SELECT event_id FROM observations").fetchall()
    assert rows == [(202208,)]
