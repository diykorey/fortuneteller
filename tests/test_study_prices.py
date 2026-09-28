"""Daily closes from Yahoo: fetch, parse and store, on trimmed real responses."""

import csv
import io
import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from datetime import date
from email.message import Message
from pathlib import Path
from typing import Any, NoReturn

import duckdb
import pytest

from fortuneteller import db, study
from fortuneteller.config import settings
from fortuneteller.models import DailyBar
from fortuneteller.study import (
    MVP_TICKERS,
    DailyClose,
    YahooError,
    load_daily_bars,
    parse_daily_bars,
    store_daily_bars,
)

DATA = Path(__file__).parent / "data"
# DX-Y.NYB, Wed 1992-12-09 … Wed 1992-12-16: bars stamped at midnight New York time, and an empty
# Sunday bar on 1992-12-13, the day CPI was released on a Sunday.
DXY_1992 = DATA / "yahoo_dx_y_nyb_1992_12.json"
# ^GSPC, Fri 2022-09-09 … Wed 2022-09-14: the hot CPI print of 2022-09-13.
GSPC_2022 = DATA / "yahoo_gspc_2022_09.json"


def _payload(path: Path, mutate: Any = None) -> bytes:
    document = json.loads(path.read_bytes())
    if mutate is not None:
        mutate(document["chart"])
    return json.dumps(document).encode()


@pytest.fixture
def pacific_time(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("TZ", "America/Los_Angeles")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


def test_bar_date_is_read_in_the_exchange_time_zone(pacific_time: None) -> None:
    # given dollar-index bars stamped at midnight New York time, parsed on a US Pacific machine,
    # where each stamp is still the previous evening
    payload = DXY_1992.read_bytes()

    # when they are parsed
    closes = parse_daily_bars(payload)

    # then every close keeps its New York trading date, not the Pacific one a day earlier
    assert [c.day for c in closes] == [
        date(1992, 12, 9),
        date(1992, 12, 10),
        date(1992, 12, 11),
        date(1992, 12, 14),
        date(1992, 12, 15),
        date(1992, 12, 16),
    ]
    assert closes[3] == DailyClose(date(1992, 12, 14), 89.70999908447266)


def test_bar_without_a_close_is_dropped() -> None:
    # given the real Sunday 1992-12-13 bar, which carries no close
    payload = DXY_1992.read_bytes()

    # when the bars are parsed
    days = {c.day for c in parse_daily_bars(payload)}

    # then that day is absent rather than stored as zero
    assert date(1992, 12, 13) not in days


def test_weekend_bar_is_dropped_even_with_a_close() -> None:
    # given the Sunday bar edited to carry a close (no real weekend bar has one today)
    def fill_sunday(chart: dict[str, Any]) -> None:
        chart["result"][0]["indicators"]["quote"][0]["close"][3] = 90.0

    payload = _payload(DXY_1992, fill_sunday)

    # when the bars are parsed
    days = {c.day for c in parse_daily_bars(payload)}

    # then a weekend date is still not a trading day
    assert date(1992, 12, 13) not in days
    assert len(days) == 6


def test_closes_come_out_oldest_first_with_known_values() -> None:
    # given the S&P 500 around the hot CPI print of 2022-09-13
    payload = GSPC_2022.read_bytes()

    # when the bars are parsed
    closes = parse_daily_bars(payload)

    # then the closes match the published index levels, in date order
    assert [c.day for c in closes] == sorted(c.day for c in closes)
    by_day = {c.day: c.close for c in closes}
    assert by_day[date(2022, 9, 12)] == pytest.approx(4110.41)
    assert by_day[date(2022, 9, 13)] == pytest.approx(3932.69)


def test_error_response_is_rejected() -> None:
    # given Yahoo answering with an error instead of a chart
    def not_found(chart: dict[str, Any]) -> None:
        chart["result"] = None
        chart["error"] = {"code": "Not Found", "description": "No data found"}

    payload = _payload(GSPC_2022, not_found)

    # when / then parsing refuses it
    with pytest.raises(YahooError, match="Not Found"):
        parse_daily_bars(payload)


def test_misaligned_response_is_rejected() -> None:
    # given a response with one more timestamp than closes
    def truncate(chart: dict[str, Any]) -> None:
        chart["result"][0]["indicators"]["quote"][0]["close"].pop()

    payload = _payload(GSPC_2022, truncate)

    # when / then parsing refuses it rather than pairing dates with the wrong closes
    with pytest.raises(YahooError, match="4 timestamps but 3 closes"):
        parse_daily_bars(payload)


def test_fetch_asks_for_the_whole_daily_history(monkeypatch: pytest.MonkeyPatch) -> None:
    # given Yahoo answering with the saved response
    seen: list[urllib.request.Request] = []

    def answer(request: urllib.request.Request, timeout: float) -> io.BytesIO:
        seen.append(request)
        return io.BytesIO(GSPC_2022.read_bytes())

    monkeypatch.setattr(study.urllib.request, "urlopen", answer)

    # when a ticker with special characters is fetched
    body = study.fetch_daily_bars("^GSPC")

    # then the ticker is escaped, the full daily range is requested with a browser User-Agent
    assert body == GSPC_2022.read_bytes()
    url = seen[0].full_url
    assert url.startswith("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?")
    assert "period1=0" in url and "interval=1d" in url
    assert seen[0].get_header("User-agent") == "Mozilla/5.0"


def test_fetch_failure_names_the_ticker(monkeypatch: pytest.MonkeyPatch) -> None:
    # given Yahoo rejecting the request
    def reject(request: urllib.request.Request, timeout: float) -> NoReturn:
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", Message(), io.BytesIO())

    monkeypatch.setattr(study.urllib.request, "urlopen", reject)

    # when / then the fetch fails with an error that says which ticker and why
    with pytest.raises(YahooError, match=r"HTTP 404 for DX-Y\.NYB"):
        study.fetch_daily_bars("DX-Y.NYB")


def _store(time_zone: str = "UTC") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{time_zone}'")
    db.init_db(con=con)
    return con


def _answer_from_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    # The dollar index answers with its own saved bars; every other ticker with the S&P 500's.
    def fetch(ticker: str) -> bytes:
        return (DXY_1992 if ticker == "DX-Y.NYB" else GSPC_2022).read_bytes()

    monkeypatch.setattr(study, "fetch_daily_bars", fetch)


def test_store_writes_one_row_per_close_with_its_symbol_and_source() -> None:
    # given the S&P 500 closes around 2022-09-13 and an empty store
    con = _store()
    closes = parse_daily_bars(GSPC_2022.read_bytes())

    # when they are stored as the SPY / ES instrument
    written = store_daily_bars("SPY / ES", "^GSPC", closes, con=con)

    # then each close is a row keyed by the canonical symbol, traceable to its vendor ticker
    assert written == 4
    row = con.execute(
        "SELECT instrument, day, close, source FROM daily_bars WHERE day = DATE '2022-09-13'"
    ).fetchone()
    assert row == ("SPY / ES", date(2022, 9, 13), pytest.approx(3932.69), "yahoo:^GSPC")


def test_day_round_trips_unchanged_under_a_non_utc_session() -> None:
    # given a store whose session time zone is not UTC, as on a developer machine
    con = _store("Europe/Kyiv")
    closes = parse_daily_bars(DXY_1992.read_bytes())

    # when the dollar-index closes are stored and read back
    store_daily_bars("DXY", "DX-Y.NYB", closes, con=con)
    days = [r[0] for r in con.execute("SELECT day FROM daily_bars ORDER BY day").fetchall()]

    # then every trading date is exactly the one parsed
    assert days == [c.day for c in closes]


def test_loading_all_five_twice_changes_no_row_count(monkeypatch: pytest.MonkeyPatch) -> None:
    # given Yahoo answering from the saved responses
    _answer_from_fixtures(monkeypatch)
    con = _store()

    # when every MVP instrument is loaded twice
    first = load_daily_bars(con=con)
    second = load_daily_bars(con=con)

    # then each run reports the same counts per instrument, and the second adds nothing
    assert (
        first
        == second
        == {
            "SPY / ES": 4,
            "UST10Y / ZN": 4,
            "DXY": 6,
            "GC / XAU": 4,
            "VIX": 4,
        }
    )
    assert db.count_rows("daily_bars", con=con) == 22


def test_tickers_cover_the_mvp_instruments_by_exact_symbol() -> None:
    # given the committed instruments CSV
    with (settings.seed_dir / "instruments.csv").open(newline="", encoding="utf-8") as handle:
        symbols = {row["symbol"] for row in csv.DictReader(handle)}

    # when the MVP ticker table is compared with it
    # then all five instruments are there, each spelled exactly as the join key
    assert list(MVP_TICKERS) == ["SPY / ES", "UST10Y / ZN", "DXY", "GC / XAU", "VIX"]
    assert set(MVP_TICKERS) <= symbols


def test_daily_bar_model_matches_the_table() -> None:
    # given the schema applied to a fresh store
    con = _store()

    # when the table's columns are read back
    columns = [
        r[0]
        for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'daily_bars' ORDER BY ordinal_position"
        ).fetchall()
    ]

    # then the model writes exactly those columns, in that order
    assert list(DailyBar.model_fields) == columns
