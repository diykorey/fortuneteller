"""Step 59 (docs/steps/crypto-weekends.md): bitcoin's and ether's weekend closes stored, read only
to grade a guess; every measurement reads weekdays alone."""

import json
from datetime import UTC, date, datetime
from pathlib import Path
import duckdb
import pytest

import fortuneteller.__main__ as cli
from fortuneteller import db, sources, study
from fortuneteller.sources import DailyClosingPrice, parse_daily_bars

# DX-Y.NYB, Wed 1992-12-09 … Wed 1992-12-16, with an empty Sunday bar on 1992-12-13.
DXY_1992 = Path(__file__).parent / "data" / "yahoo_dx_y_nyb_1992_12.json"


def _with_sunday() -> bytes:
    document = json.loads(DXY_1992.read_bytes())
    document["chart"]["result"][0]["indicators"]["quote"][0]["close"][3] = 90.0
    return json.dumps(document).encode()


def _store() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute("SET TimeZone = 'UTC'")
    db.init_db(con=con)
    return con


def _row(stated: str, market: str, made: datetime, **extra: str) -> dict[str, str]:
    row = {
        "stated": stated,
        "market": market,
        "horizon": "week",
        "direction": "up",
        "last": "2026-12-04",
        "tag": "momentum",
        "confidence": "low",
        "grade": "",
        "move": "",
        "base_rate": "",
        "guesser": "news",
        "prompt": "news-1",
        "made": made.isoformat(),
    }
    return row | extra


# 14:00 New York on Saturday 2026-11-28 is 19:00 UTC, before bitcoin's close at 23:59 UTC.
SATURDAY_DRAFT = datetime(2026, 11, 28, 19, 0, tzinfo=UTC)


def test_the_parser_keeps_a_weekend_close_only_when_asked() -> None:
    # given a Yahoo reply whose Sunday bar carries a close
    payload = _with_sunday()

    # when parsed as a weekday market and as a crypto market
    weekdays = {c.day for c in parse_daily_bars(payload)}
    every_day = {c.day for c in parse_daily_bars(payload, weekends=True)}

    # then only the second keeps Sunday
    assert date(1992, 12, 13) not in weekdays
    assert every_day - weekdays == {date(1992, 12, 13)}


def test_the_loader_stores_weekend_closes_for_bitcoin_and_ether_alone(
    monkeypatch: pytest.MonkeyPatch, fred_breakeven: None
) -> None:
    # given Yahoo answering every ticker with the bars holding a Sunday close
    monkeypatch.setattr(sources, "fetch_daily_bars", lambda _ticker: _with_sunday())
    con = _store()

    # when every market is loaded
    counts = study.load_daily_bars("test-key", con=con)

    # then bitcoin and ether hold seven closes, the other Yahoo markets six
    yahoo = {
        m for m, s in study.MVP_PRICE_SERIES.items() if not s.ticker.startswith(study.FRED_PREFIX)
    }
    assert {m: counts[m] for m in study.CRYPTO} == {"BTC": 7, "ETH": 7}
    assert {counts[m] for m in yahoo - set(study.CRYPTO)} == {6}


def test_every_reader_but_a_guess_s_grade_sees_weekdays_alone() -> None:
    # given bitcoin's closes stored on Friday, Saturday and Sunday
    con = _store()
    days = (date(2026, 11, 27), date(2026, 11, 28), date(2026, 11, 29))
    closes = [DailyClosingPrice(d, 100.0 + i) for i, d in enumerate(days)]
    study.store_daily_bars("BTC", "BTC-USD", closes, con=con)

    # when read as a measurement, as the latest close, and as a guess's grade
    measured = study.stored_closes("BTC", con)
    until = study.stored_until(con)
    graded = study.stored_closes("BTC", con, weekends=True)

    # then the weekend is seen by the grade alone
    assert [c.day for c in measured] == [date(2026, 11, 27)]
    assert until == date(2026, 11, 27)
    assert [c.day for c in graded] == list(days)


def test_a_saturday_crypto_guess_starts_from_saturday_s_close_and_counts() -> None:
    # given an up bitcoin guess drafted Saturday 2026-11-28 at 14:00 New York, to Friday 12-04,
    # and bitcoin's every-day closes from Friday 11-27
    row = _row("2026-11-28", "BTC", SATURDAY_DRAFT, base_rate="0.5")
    prices = {27: 100.0, 28: 90.0, 29: 95.0, 30: 96.0}
    every_day = [DailyClosingPrice(date(2026, 11, d), p) for d, p in prices.items()]
    every_day += [DailyClosingPrice(date(2026, 12, d), 92.0) for d in range(1, 5)]

    # when its start is read, it is graded and the records are made
    start = cli.guess_start(row)
    graded = cli.grade_guesses([row], lambda _m: every_day)[0]
    record = cli.guess_record([graded], "tag")

    # then it starts from Saturday's 90, after it was made, and is a counted try
    assert start == date(2026, 11, 28)
    assert (graded["grade"], graded["move"]) == ("came true", "90 to 92")
    assert record[0]["guesses"] == 1
    assert cli.counted_guesses([graded]) == [graded]


def test_a_saturday_crypto_guess_s_base_rate_reads_weekdays_after_its_start() -> None:
    # given the Saturday bitcoin guess and an uneven run of weekday closes before it
    row = _row("2026-11-28", "BTC", SATURDAY_DRAFT)
    october = [date(2026, 10, d) for d in range(1, 31)]
    weekdays = [DailyClosingPrice(d, 50.0 + d.day * 7 % 11) for d in october if d.weekday() < 5]

    # when its base rate is filled
    filled = cli.with_base_rates([row], lambda _m: weekdays)[0]

    # then over the five weekdays from Monday 11-30 to Friday 12-04, from weekday closes
    expected = study.base_rate(weekdays, date(2026, 11, 28), 5, "up")
    assert expected is not None
    assert expected != study.base_rate(weekdays, date(2026, 11, 28), 4, "up")
    assert filled["base_rate"] == f"{expected:.4f}"


@pytest.mark.parametrize(
    ("stated", "market", "made", "start", "counted"),
    [
        ("2026-11-28", "SPY / ES", SATURDAY_DRAFT, date(2026, 11, 30), False),
        ("2026-11-22", "BTC", datetime(2026, 11, 22, 19, 0, tzinfo=UTC), date(2026, 11, 23), True),
        ("2026-11-27", "BTC", datetime(2026, 11, 27, 19, 0, tzinfo=UTC), date(2026, 11, 27), True),
    ],
)
def test_other_guesses_keep_their_start_and_count(
    stated: str, market: str, made: datetime, start: date, counted: bool
) -> None:
    # given a Saturday S&P 500 guess, bitcoin's of Sunday 2026-11-22, before the schedule, and a
    # bitcoin guess drafted at 14:00 New York on Friday 2026-11-27
    row = _row(stated, market, made, grade="came true", base_rate="0.5")

    # when its start is read and the guesses counted
    # then the S&P 500's waits for Monday and is left out, the Sunday before the schedule starts
    # Monday as before, and Friday's starts Friday
    assert cli.guess_start(row) == start
    assert (cli.counted_guesses([row]) == [row]) is counted


def test_the_weekend_rule_spares_ether_and_not_brent() -> None:
    # given a Saturday ether row and a Saturday Brent row
    # when the weekend rule reads them
    # then ether's is no weekend draft and Brent's is
    assert not cli.weekend_draft({"stated": "2026-11-28", "market": "ETH"})
    assert cli.weekend_draft({"stated": "2026-11-28", "market": "BRN"})
