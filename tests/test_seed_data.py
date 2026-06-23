"""Tests for the M0-06 seed CSV contracts (data/seed/*.csv).

The CSVs are committed reference data; these tests lock the contract so a drifted header or an
invalid enum value fails CI. Each seed file is checked against two canonical sources: its
``schema.sql`` table columns (M0-04) and its M0-03 Pydantic model (enums + types).
"""

import csv
from pathlib import Path

import duckdb
import pytest
from pydantic import BaseModel

from fortuneteller.config import settings
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
    # when compared to the contracted set
    expected = {filename for filename, _table, _model in SEED_TABLES}
    # then exactly the five contracted files are present
    assert actual == expected


def test_seed_dir_path_is_data_seed() -> None:
    # given the configured seed directory
    # when its path is inspected
    # then it points at data/seed (the committed reference data)
    assert settings.seed_dir == Path("data/seed")
