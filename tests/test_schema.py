"""Tests for the M0-04 database schema (schema.sql)."""

import duckdb

from fortuneteller.config import settings

EXPECTED_TABLES = {
    "event_types",
    "instruments",
    "effect_size_seed",
    "news_sources",
    "countries",
    "event_instances",
    "observations",
    "effect_size_matrix",
    "daily_bars",
    "cpi_surprises",
}


def test_schema_creates_all_ten_tables() -> None:
    # given a fresh in-memory DuckDB connection and the schema file
    con = duckdb.connect(":memory:")
    sql = settings.schema_path.read_text()
    # when the schema is executed
    con.execute(sql)
    # then all ten tables exist
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES


def test_schema_is_idempotent() -> None:
    # given a connection that already ran the schema once
    con = duckdb.connect(":memory:")
    sql = settings.schema_path.read_text()
    con.execute(sql)
    # when re-applied (CREATE TABLE IF NOT EXISTS)
    con.execute(sql)
    # then it still succeeds with the same ten tables
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES


def test_daily_bars_is_keyed_by_instrument_and_calendar_date() -> None:
    # given the schema applied to a fresh store
    con = duckdb.connect(":memory:")
    con.execute(settings.schema_path.read_text())

    # when the daily_bars columns and primary key are read back
    columns = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'daily_bars' ORDER BY ordinal_position"
    ).fetchall()
    key = con.execute(
        "SELECT constraint_column_names FROM duckdb_constraints() "
        "WHERE table_name = 'daily_bars' AND constraint_type = 'PRIMARY KEY'"
    ).fetchone()

    # then day is a DATE, so no session time zone can shift it, and one bar per instrument per day
    assert columns == [
        ("instrument", "VARCHAR"),
        ("day", "DATE"),
        ("close", "DOUBLE"),
        ("source", "VARCHAR"),
    ]
    assert key == (["instrument", "day"],)


def test_cpi_surprises_holds_one_row_per_release_measure_and_baseline() -> None:
    # given the schema applied to a fresh store
    con = duckdb.connect(":memory:")
    con.execute(settings.schema_path.read_text())

    # when the cpi_surprises columns and primary key are read back
    columns = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'cpi_surprises' ORDER BY ordinal_position"
    ).fetchall()
    key = con.execute(
        "SELECT constraint_column_names FROM duckdb_constraints() "
        "WHERE table_name = 'cpi_surprises' AND constraint_type = 'PRIMARY KEY'"
    ).fetchone()

    # then each release has at most one surprise per measure and baseline
    assert columns == [
        ("event_id", "BIGINT"),
        ("measure", "VARCHAR"),
        ("baseline", "VARCHAR"),
        ("actual_mom", "DOUBLE"),
        ("expected_mom", "DOUBLE"),
        ("surprise", "DOUBLE"),
    ]
    assert key == (["event_id", "measure", "baseline"],)
