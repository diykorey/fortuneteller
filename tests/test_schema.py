"""Tests for the M0-04 database schema (schema.sql)."""

import duckdb

from fortuneteller.config import settings

EXPECTED_TABLES = {
    "event_types",
    "instruments",
    "effect_size_seed",
    "surprise_response",
    "news_sources",
    "countries",
    "event_instances",
    "observations",
    "effect_size_matrix",
}


def test_schema_creates_all_tables() -> None:
    # given a fresh in-memory DuckDB connection and the schema file
    con = duckdb.connect(":memory:")
    sql = settings.schema_path.read_text()
    # when the schema is executed
    con.execute(sql)
    # then every declared table exists
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES


def test_schema_is_idempotent() -> None:
    # given a connection that already ran the schema once
    con = duckdb.connect(":memory:")
    sql = settings.schema_path.read_text()
    con.execute(sql)
    # when re-applied (CREATE TABLE IF NOT EXISTS)
    con.execute(sql)
    # then it still succeeds with the same tables
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES
