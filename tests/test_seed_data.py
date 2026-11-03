"""Tests for the M0-06 seed CSV contracts (data/seed/*.csv).

The CSVs are committed reference data; these tests lock the contract so a drifted header or an
invalid enum value fails CI. Each seed file is checked against two canonical sources: its
``schema.sql`` table columns (M0-04) and its M0-03 Pydantic model (enums + types).
"""

import csv
import re
from datetime import date
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
