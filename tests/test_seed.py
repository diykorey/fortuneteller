"""Tests for the M0-07 seed loader (seed.py)."""

from pathlib import Path

import duckdb
import polars as pl
import pytest
from pydantic import ValidationError

from fortuneteller import db, seed
from fortuneteller.config import settings
from fortuneteller.models import EffectSizeSeed


def _seeded_connection() -> duckdb.DuckDBPyConnection:
    # given a fresh in-memory store with the schema applied
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    return con


def test_load_all_counts_match_csv_rows() -> None:
    # given a schema-only store and the committed seed CSVs
    con = _seeded_connection()
    expected = {
        table: pl.read_csv(settings.seed_dir / filename).height
        for filename, _model, table in seed.SEED_TABLES
    }
    # when every seed table is loaded
    counts = seed.load_all(con=con)
    # then the returned counts equal each CSV's data-row count
    assert counts == expected
    assert all(count > 0 for count in counts.values())


def test_load_all_is_idempotent() -> None:
    # given a store already fully seeded once
    con = _seeded_connection()
    first = seed.load_all(con=con)
    # when load_all runs a second time
    second = seed.load_all(con=con)
    # then it succeeds (no primary-key collision) and reports identical counts
    assert second == first


def test_query_demo_returns_canonical_row() -> None:
    # given a fully seeded store
    con = _seeded_connection()
    seed.load_all(con=con)
    # when the demo lookup runs
    row = seed.query_demo(con=con)
    # then it returns the canonical CPI x SPY effect-size row
    assert row is not None
    assert row.event_type == "CPI / inflation surprise"
    assert row.instrument == "SPY / ES"


def test_malformed_enum_value_names_file_and_row(tmp_path: Path) -> None:
    # given an effect-size CSV whose first data row has an invalid direction enum
    csv = tmp_path / "effect_size_seed.csv"
    header = ",".join(EffectSizeSeed.model_fields)
    bad_values = [
        "CPI / inflation surprise",
        "SPY / ES",
        "sideways",
        "0.5-1.5%",
        "minutes_hours",
        "high",
        "~62%",
        "yes",
        "placeholder seed",
    ]
    csv.write_text(f"{header}\n{','.join(bad_values)}\n")
    # when the loader validates it
    with pytest.raises(ValueError) as excinfo:
        seed._load_csv(csv, EffectSizeSeed)
    # then the error names the file and the offending row (line 2), caused by a ValidationError
    message = str(excinfo.value)
    assert "effect_size_seed.csv" in message
    assert "2" in message
    assert isinstance(excinfo.value.__cause__, ValidationError)
