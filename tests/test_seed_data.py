"""Tests for the M0-06 seed CSV contracts (data/seed/*.csv).

The CSVs are committed reference data; these tests lock the contract so a drifted header or an
invalid enum value fails CI. Each seed file is checked against two canonical sources: its
``schema.sql`` table columns (M0-04) and its M0-03 Pydantic model (enums + types).
"""

import csv
import importlib.util
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import duckdb
import pytest
from pydantic import BaseModel

from fortuneteller.config import settings
from fortuneteller.study import MVP_PRICE_SERIES
from fortuneteller.models import (
    Country,
    EffectSizeSeed,
    EventType,
    Instrument,
    NewsSource,
)

# Each seed CSV, its schema.sql table, and the M0-03 model that types its rows.
SEED_TABLES: list[tuple[str, str, type[BaseModel]]] = [
    ("event_types.csv", "event_types", EventType),
    ("instruments.csv", "instruments", Instrument),
    ("effect_size_seed.csv", "effect_size_seed", EffectSizeSeed),
    ("news_sources.csv", "news_sources", NewsSource),
    ("countries.csv", "countries", Country),
]

_IDS = [filename for filename, _table, _model in SEED_TABLES]


def _schema_columns(table: str) -> list[str]:
    """Return ``table``'s columns, in definition order, from the M0-04 schema DDL."""
    con = duckdb.connect(":memory:")
    con.execute(settings.schema_path.read_text())
    return [str(row[0]) for row in con.execute(f"DESCRIBE {table}").fetchall()]


def _read_csv(filename: str) -> tuple[list[str], list[dict[str, str]]]:
    """Return the header and data rows of a seed CSV, decoded as UTF-8."""
    path = settings.seed_dir / filename
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows


@pytest.mark.parametrize(("filename", "table", "model"), SEED_TABLES, ids=_IDS)
def test_header_matches_schema_columns(filename: str, table: str, model: type[BaseModel]) -> None:
    # given a seed CSV and its schema table's columns
    schema_cols = _schema_columns(table)
    # when the CSV header is read
    header, _rows = _read_csv(filename)
    # then the header equals the table's columns exactly (order included)
    assert header == schema_cols


@pytest.mark.parametrize(("filename", "table", "model"), SEED_TABLES, ids=_IDS)
def test_file_is_utf8(filename: str, table: str, model: type[BaseModel]) -> None:
    # given the raw bytes of a seed CSV
    raw = (settings.seed_dir / filename).read_bytes()
    # when they are decoded as UTF-8
    # then decoding succeeds (a non-UTF-8 byte would raise UnicodeDecodeError)
    raw.decode("utf-8")


@pytest.mark.parametrize(("filename", "table", "model"), SEED_TABLES, ids=_IDS)
def test_rows_nonempty_and_valid(filename: str, table: str, model: type[BaseModel]) -> None:
    # given the rows of a seed CSV
    _header, rows = _read_csv(filename)
    # then there is at least one data row
    assert len(rows) >= 1
    # and every row validates against its M0-03 model (enums, ranges, extra="forbid")
    for row in rows:
        # when empty cells map to None so optional columns stay unset
        data = {key: (value if value != "" else None) for key, value in row.items()}
        model(**data)


def test_seed_dir_has_no_unexpected_csvs() -> None:
    # given the committed seed CSVs
    actual = {path.name for path in settings.seed_dir.glob("*.csv")}
    # when compared to the contracted set: the seed tables, the dated-shock flows' own files and the
    # Fed statement's dictionary
    expected = {filename for filename, _table, _model in SEED_TABLES} | {
        "elections.csv",
        "tariffs.csv",
        "debt_limit.csv",
        "summits.csv",
        "presidential_posts.csv",
        "presidential_posts_2.csv",
        "ceo_scandals.csv",
        "opec.csv",
        "war.csv",
        "crypto.csv",
        "hurricanes.csv",
        "floods.csv",
        "dow.csv",
        "earnings.csv",
        "sp500_additions.csv",
        "boe-changes.csv",
        "fomc_sentiment_dictionary.csv",
    }
    # then exactly those files are present
    assert actual == expected


def test_seed_dir_path_is_data_seed() -> None:
    # given the configured seed directory
    # when its path is inspected
    # then it points at data/seed (the committed reference data)
    assert settings.seed_dir == Path("data/seed")


# Every instrument measured (study.MVP_PRICE_SERIES). These symbols are join keys: step 2 looks
# each one up by exact string, so a rename or a typo silently breaks the measurement.
@pytest.mark.parametrize("symbol", list(MVP_PRICE_SERIES))
def test_mvp_instrument_resolves_by_exact_symbol(symbol: str) -> None:
    # given the committed instruments CSV
    with (settings.seed_dir / "instruments.csv").open(newline="", encoding="utf-8") as handle:
        symbols = {row["symbol"] for row in csv.DictReader(handle)}
    # when an MVP instrument is looked up by its canonical symbol
    # then it is present exactly as written
    assert symbol in symbols


def test_every_ceo_scandal_s_company_is_a_single_stock_instrument() -> None:
    # given the committed CEO scandals and instruments
    with (settings.seed_dir / "ceo_scandals.csv").open(newline="", encoding="utf-8") as handle:
        tickers = [row["ticker"] for row in csv.DictReader(handle)]
    with (settings.seed_dir / "instruments.csv").open(newline="", encoding="utf-8") as handle:
        classes = {row["symbol"]: row["asset_class"] for row in csv.DictReader(handle)}
    # when each scandal's ticker is looked up
    # then it is there exactly as written, a single stock, and no company is listed twice
    assert all(classes.get(ticker) == "single_stock" for ticker in tickers)
    assert len(set(tickers)) == len(tickers)


def test_tariff_rows_are_federal_register_documents_since_2018() -> None:
    # given the committed tariff actions
    with (settings.seed_dir / "tariffs.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    # when their days and document numbers are read
    days = [date.fromisoformat(row["signing_day"]) for row in rows]
    numbers = [row["document_number"] for row in rows]
    # then each is a Federal Register number, once, signed since 2018 and by today, in date order
    assert all(re.fullmatch(r"20\d\d-\d{5}", number) for number in numbers)
    assert len(set(numbers)) == len(numbers)
    assert date(2018, 1, 1) <= min(days) and max(days) <= date.today()
    assert days == sorted(days)
    assert all(row["title"].strip() == row["title"] and row["title"] for row in rows)


def test_debt_limit_rows_are_public_laws_cleared_since_1970() -> None:
    # given the committed debt-limit laws
    with (settings.seed_dir / "debt_limit.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their numbers, kinds and days are read
    numbers = [row["public_law"] for row in rows]
    cleared = [date.fromisoformat(row["cleared"]) for row in rows]
    signed = [date.fromisoformat(row["signed"]) for row in rows]
    # then each is a public law, once, of a known kind, cleared in order since 1970 and by its signing
    assert header == ["cleared", "time", "signed", "public_law", "action", "vehicle"]
    assert all(re.fullmatch(r"\d{2,3}-\d{1,3}", number) for number in numbers)
    assert len(set(numbers)) == len(numbers)
    assert {row["action"] for row in rows} <= {"raise", "temporary", "suspend"}
    assert {row["vehicle"] for row in rows} <= {"debt", "rider"}
    assert all(re.fullmatch(r"[0-2]\d:[0-5]\d", row["time"]) for row in rows)
    assert cleared == sorted(cleared) and cleared[0] >= date(1970, 6, 29)
    assert all(c <= s for c, s in zip(cleared, signed, strict=True))


def test_summit_rows_are_g7_and_g20_summits_since_1975() -> None:
    # given the committed summits
    with (settings.seed_dir / "summits.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their last days and sources are read
    days = [date.fromisoformat(row["last_day"]) for row in rows]
    sources = [row["source_url"] for row in rows]
    # then each is a G7 or G20 summit with its rule's hour and its page, once, in order, by today
    assert header == ["last_day", "time", "summit", "source_url"]
    assert all(re.fullmatch(r"G(7|20) \S.*", row["summit"]) for row in rows)
    assert {row["time"] for row in rows} <= {"08:00", "20:00"}
    assert all(re.fullmatch(r"https://www\.g(7|20)\.utoronto\.ca/\S+", s) for s in sources)
    assert len(set(days)) == len(days) and len(set(sources)) == len(sources)
    assert days == sorted(days) and days[0] >= date(1975, 11, 17) and days[-1] <= date.today()


def test_opec_rows_are_kanzigs_announcements_with_their_kind() -> None:
    # given the committed OPEC announcements
    with (settings.seed_dir / "opec.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days and kinds are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    kinds = {row["day"]: row["kind"] for row in rows}
    # then the vintage's 169 days are there once, in order, at the rule's hour, each with a kind,
    # and four days checked by hand against the news carry the oil market's reading
    assert header == ["day", "time", "kind"]
    assert len(rows) == 169 and len(set(days)) == 169 and days == sorted(days)
    assert (days[0], days[-1]) == (date(1983, 7, 19), date(2025, 12, 1))
    assert {row["time"] for row in rows} == {"08:00"}
    assert set(kinds.values()) == {"oil up", "oil down"}
    assert [kinds[d] for d in ("2014-11-27", "2016-11-30", "2020-04-12", "2022-10-05")] == [
        "oil down",
        "oil up",
        "oil up",
        "oil up",
    ]


def test_boe_changes_are_the_bank_s_bank_rate_changes_since_2008() -> None:
    # given the committed Bank Rate changes
    with (settings.seed_dir / "boe-changes.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days and rates are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    rates = {row["day"]: float(row["rate"]) for row in rows}
    # then 34 changes are there once, in order, each a change from the one before, and the
    # days checked by hand carry the Bank's rate, the two emergency cuts of 2020 among them
    assert header == ["day", "time", "rate"]
    assert len(rows) == 34 and len(set(days)) == 34 and days == sorted(days)
    assert (days[0], days[-1]) == (date(2008, 2, 7), date(2026, 11, 5))
    values = [float(row["rate"]) for row in rows]
    assert all(a != b for a, b in zip(values, values[1:], strict=False))
    assert {d: rates[d] for d in ("2009-03-05", "2016-08-04", "2020-03-11", "2020-03-19")} == {
        "2009-03-05": 0.5,
        "2016-08-04": 0.25,
        "2020-03-11": 0.25,
        "2020-03-19": 0.1,
    }
    assert "2020-03-26" not in rates
    assert {row["day"]: row["time"] for row in rows}["2020-03-11"] == "07:00"


def test_tweet_days_are_inside_the_first_term() -> None:
    # given the committed tweet days
    with (settings.seed_dir / "presidential_posts.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days, times and counts are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    # then each is a day of the first term, once and in order, with its times and at least one tweet
    assert header == ["day", "time", "posts", "rate_time"]
    assert days == sorted(set(days))
    assert date(2017, 1, 20) <= days[0] and days[-1] <= date(2021, 1, 8)
    assert all(re.fullmatch(r"[0-2]\d:[0-5]\d", row["time"]) for row in rows)
    assert all(re.fullmatch(r"([0-2]\d:[0-5]\d)?", row["rate_time"]) for row in rows)
    assert all(row["rate_time"] == "" or row["rate_time"] >= row["time"] for row in rows)
    assert all(int(row["posts"]) >= 1 for row in rows)


def test_post_days_are_inside_the_second_term_window() -> None:
    # given the committed second-term post days
    with (settings.seed_dir / "presidential_posts_2.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days, times and counts are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    # then each is a day of the window, once and in order, with its times and at least one post
    assert header == ["day", "time", "posts", "rate_time"]
    assert days == sorted(set(days))
    assert date(2025, 1, 20) <= days[0] and days[-1] <= date(2026, 10, 30)
    assert all(re.fullmatch(r"[0-2]\d:[0-5]\d", row["time"]) for row in rows)
    assert all(re.fullmatch(r"([0-2]\d:[0-5]\d)?", row["rate_time"]) for row in rows)
    assert all(row["rate_time"] == "" or row["rate_time"] >= row["time"] for row in rows)
    assert all(int(row["posts"]) >= 1 for row in rows)


def test_war_rows_are_icb_s_crises_a_violent_act_set_off_since_1970() -> None:
    # given the committed violent acts
    with (settings.seed_dir / "war.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days and crises are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    crises = {row["day"]: row["crisis"] for row in rows}
    # then the 137 crises are in order on 136 days at the rule's hour, one kind, and the five rows
    # named before measuring are there
    assert header == ["day", "time", "kind", "crisis"]
    assert len(rows) == 137 and len(set(days)) == 136 and days == sorted(days)
    assert (days[0], days[-1]) == (date(1970, 11, 22), date(2021, 4, 28))
    assert {row["time"] for row in rows} == {"04:00"}
    assert {row["kind"] for row in rows} == {"violent act"}
    assert [
        crises[d] for d in ("1970-11-22", "1990-08-02", "2001-09-11", "2001-12-13", "2020-09-27")
    ] == [
        "CONAKRY RAID",
        "GULF WAR",
        "AFGHANISTAN/US",
        "INDIA PARLIAMENT ATTACK",
        "SECOND NAGORNO-KARABAKH WAR",
    ]


def test_crypto_rows_are_defillama_s_hacks_of_100_million_or_more() -> None:
    # given the committed hacks
    with (settings.seed_dir / "crypto.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days and targets are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    targets = {row["day"]: (row["target"], int(row["amount"])) for row in rows}
    # then the 44 hacks are in order on 44 days at the rule's hour, one kind, each at least the
    # line, and the four rows named before measuring are there
    assert header == ["day", "time", "kind", "target", "amount"]
    assert len(rows) == 44 and len(set(days)) == 44 and days == sorted(days)
    assert (days[0], days[-1]) == (date(2014, 2, 7), date(2026, 10, 29))
    assert {row["time"] for row in rows} == {"04:00"}
    assert {row["kind"] for row in rows} == {"hack"}
    assert all(int(row["amount"]) >= 100_000_000 for row in rows)
    assert [targets[d] for d in ("2018-01-26", "2022-03-23", "2022-11-12", "2025-02-21")] == [
        ("Coincheck", 534_000_000),
        ("Ronin Bridge", 624_000_000),
        ("FTX", 450_000_000),
        ("Bybit", 1_400_000_000),
    ]


def test_hurricane_rows_are_first_us_landfalls_since_1970() -> None:
    # given the committed landfalls
    with (settings.seed_dir / "hurricanes.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days, storms and places are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    named = {row["day"]: (row["time"], row["storm"], int(row["knots"])) for row in rows}
    places = [(float(row["lat"]), float(row["lon"])) for row in rows]
    # then the 79 landfalls are in order on 79 days, one kind, each a hurricane, each inside the
    # place rule, the five named before measuring there and the foreign landfalls named not
    assert header == ["day", "time", "kind", "storm", "knots", "lat", "lon"]
    assert len(rows) == 79 and len(set(days)) == 79 and days == sorted(days)
    assert (days[0], days[-1]) == (date(1970, 8, 3), date(2024, 10, 10))
    assert {row["kind"] for row in rows} == {"landfall"}
    assert all(int(row["knots"]) >= 64 for row in rows)
    assert all(
        24.4 <= lat < 47.5
        and lon <= -66.9
        and not (lat < 32 and lon > -80.0)
        and not (lon < -96.5 and lat < 25.95)
        for lat, lon in places
    )
    assert [
        named[d] for d in ("1992-08-24", "2005-09-24", "2008-09-13", "2017-08-26", "2022-09-28")
    ] == [
        ("08:40", "Andrew", 145),
        ("07:40", "Rita", 100),
        ("07:00", "Ike", 95),
        ("03:00", "Harvey", 115),
        ("02:00", "Ian", 110),
    ]
    assert not {
        "2016-10-07",
        "2022-11-09",
        "2019-09-01",
        "2017-09-20",
        "2017-09-09",
        "2021-08-21",
    } & set(named)


def test_flood_rows_are_the_billion_dollar_list_s_floods_with_a_day() -> None:
    # given the committed floods
    with (settings.seed_dir / "floods.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)
    # when their days, names and costs are read
    days = [date.fromisoformat(row["day"]) for row in rows]
    named = {row["day"]: (row["name"], float(row["cost"])) for row in rows}
    # then the 39 floods are in order on 39 days, each at its begin day, the six season rows out
    assert header == ["day", "name", "cost"]
    assert len(rows) == 39 and len(set(days)) == 39 and days == sorted(days)
    assert (days[0], days[-1]) == (date(1980, 4, 10), date(2024, 6, 16))
    assert named["2024-06-16"] == ("Upper Midwest Flooding (June 2024)", 1113.0)
    assert {"1997-01-01", "2015-10-01"} <= set(named)
    assert not {
        "1982-12-01",
        "1995-01-01",
        "2008-04-01",
        "2010-03-01",
        "2011-04-01",
        "2011-05-01",
    } & set(named)


def _dow_members(day: date) -> set[str]:
    # the Dow's members on ``day`` by data/seed/dow.csv's dated changes
    members: set[str] = set()
    with (settings.seed_dir / "dow.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if date.fromisoformat(row["day"]) <= day:
                (members.add if row["change"] == "in" else members.discard)(row["ticker"])
    return members


def test_dow_members_change_on_their_days_and_stay_thirty() -> None:
    # given the members' dated changes
    # when the members are read on two change days and the days before them
    days = [date(2013, 9, 20), date(2013, 9, 23), date(2008, 9, 19), date(2008, 9, 22)]
    before13, after13, before08, after08 = (_dow_members(d) for d in days)

    # then Goldman Sachs, Visa and Nike replace Alcoa, Bank of America and Hewlett-Packard, Kraft
    # (Mondelez today) replaces AIG, and there are 30 each time
    assert after13 - before13 == {"GS", "V", "NKE"}
    assert before13 - after13 == {"HWM", "BAC", "HPQ"}
    assert (after08 - before08, before08 - after08) == ({"MDLZ"}, {"AIG"})
    assert all(len(m) == 30 for m in (before13, after13, before08, after08))


def test_earnings_rows_are_members_reports_with_their_kind() -> None:
    # given the committed reports
    with (settings.seed_dir / "earnings.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = list(reader)

    # when each row's kind is read against its surprise
    def kind(surprise: float) -> str:
        return "above" if surprise >= 2.0 else "below" if surprise <= -2.0 else "as expected"

    # then every row is a member's on its day (a day either side, the 8-K's), its kind the
    # surprise's at ±2%, and Microsoft's report of 2026-10-28 is at its 8-K's minute
    assert header == ["day", "time", "ticker", "eps", "forecast", "surprise", "kind"]
    assert all(row["kind"] == kind(float(row["surprise"])) for row in rows)
    assert (kind(2.0), kind(1.9), kind(-2.0)) == ("above", "as expected", "below")
    assert all(
        any(
            row["ticker"] in _dow_members(date.fromisoformat(row["day"]) + timedelta(days=d))
            for d in (-1, 0, 1)
        )
        for row in rows
    )
    msft = [r for r in rows if r["ticker"] == "MSFT" and r["day"] == "2026-10-28"]
    assert [(r["time"], r["kind"]) for r in msft] == [("20:04", "above")]


def test_the_8_k_kept_is_the_nearest_to_the_calendar_s_day() -> None:
    # given the seed script, and three 8-Ks with Item 2.02: 20 days before, the day before and the
    # calendar's day
    spec = importlib.util.spec_from_file_location(
        "nasdaq_earnings", Path(__file__).parents[1] / "scripts" / "nasdaq_earnings.py"
    )
    assert spec is not None and spec.loader is not None
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    stamps = [
        datetime(2026, 10, 8, 20, 0, tzinfo=UTC),
        datetime(2026, 10, 27, 20, 0, tzinfo=UTC),
        datetime(2026, 10, 28, 20, 4, tzinfo=UTC),
    ]

    # when the one for the calendar's 2026-10-28 is chosen, and for a day with none near
    kept = script.nearest(date(2026, 10, 28), stamps)
    none = script.nearest(date(2026, 9, 1), stamps)

    # then the calendar's own day wins, and a pre-announcement 20 days before is never taken
    assert kept == stamps[2]
    assert none is None
    assert script.nearest(date(2026, 10, 9), stamps[:1]) == stamps[0]


def test_earnings_refresh_fetches_again_the_last_three_weeks_and_takes_the_last_day() -> None:
    # given step 33's script
    spec = importlib.util.spec_from_file_location(
        "nasdaq_earnings", Path(__file__).parents[1] / "scripts" / "nasdaq_earnings.py"
    )
    assert spec is not None and spec.loader is not None
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    today = date(2026, 11, 23)

    # when it decides which saved pages to fetch again and which weekdays to read
    days = script.weekdays(date(2026, 11, 20))

    # then 21 days back is fetched again, 22 is kept, and the last day is the one given
    assert script.refetched(date(2026, 11, 2), today) is True
    assert script.refetched(date(2026, 11, 1), today) is False
    assert days[-1] == date(2026, 11, 20)
    assert script.weekdays()[-1] == date(2026, 11, 18)


def test_yahoo_s_quarter_matches_nasdaq_s_and_its_kind_is_nasdaq_s_way() -> None:
    # given step 34's script
    spec = importlib.util.spec_from_file_location(
        "yahoo_earnings", Path(__file__).parents[1] / "scripts" / "yahoo_earnings.py"
    )
    assert spec is not None and spec.loader is not None
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    # when Walmart's newest quarter and three surprises are read
    key = script.quarter_key("2026-10-31")
    kinds = [script.kind(0.65, 0.63627), script.kind(0.65, 0.64), script.kind(-0.34, -0.21)]

    # then the quarter is Nasdaq's, and a report without both figures is not yet a kind
    assert key == "Oct/2026"
    assert kinds == ["above", "as expected", "below"]
    assert script.kind(None, 0.64) is None


def test_sp500_additions_are_announced_ahead_one_kind_one_row_a_ticker_a_day() -> None:
    # given step 35's seed (docs/steps/sp500-additions.md)
    with (settings.seed_dir / "sp500_additions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    # when each row's announcement is set against its effective day
    leads = [(date.fromisoformat(r["effective"]) - date.fromisoformat(r["day"])).days for r in rows]
    per_day = [(r["day"], r["ticker"]) for r in rows]

    # then every one is 1 to 40 days ahead, of the one kind, a ticker once a day, none reused since
    assert len(rows) == 191
    assert all(1 <= lead <= 40 for lead in leads)
    assert {r["kind"] for r in rows} == {"added"}
    assert len(per_day) == len(set(per_day))
    assert not {"CSRA", "INFO", "NWSA"} & {r["ticker"] for r in rows}
