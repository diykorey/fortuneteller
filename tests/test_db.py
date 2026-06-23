"""Tests for the M0-05 database helper (db.py)."""

from pathlib import Path

import duckdb
import pytest

from fortuneteller import db
from fortuneteller.config import settings
from fortuneteller.models import EffectSizeSeed, Instrument

EXPECTED_TABLES = {
    "event_types",
    "instruments",
    "effect_size_seed",
    "news_sources",
    "countries",
    "event_instances",
    "observations",
    "effect_size_matrix",
}


def _seeded_connection() -> duckdb.DuckDBPyConnection:
    # given a fresh in-memory store with the schema applied
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    return con


def test_init_db_creates_file_and_tables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # given a temp DB path (test_ prefix marks it as a throwaway artifact)
    db_path = tmp_path / "test_fortuneteller.duckdb"
    monkeypatch.setattr(settings, "db_path", db_path)
    # when init_db runs against the default (now temp) path
    db.init_db()
    # then the file exists and holds all eight tables
    assert db_path.exists()
    con = duckdb.connect(str(db_path))
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES


def test_get_instrument_roundtrips() -> None:
    # given a known Instrument inserted into a seeded store
    con = _seeded_connection()
    instrument = Instrument(
        symbol="SPY / ES", name="S&P 500", asset_class="equity_index", region="us"
    )
    db.insert_models("instruments", [instrument], con=con)
    # when it is read back by symbol
    fetched = db.get_instrument("SPY / ES", con=con)
    # then an equal model comes back
    assert fetched == instrument


def test_get_instrument_missing_returns_none() -> None:
    # given a seeded but empty instruments table
    con = _seeded_connection()
    # when an unknown symbol is queried
    # then None is returned
    assert db.get_instrument("DOES / NOT EXIST", con=con) is None


def test_get_effect_size_roundtrips() -> None:
    # given a known effect-size seed row inserted into a seeded store
    con = _seeded_connection()
    seed = EffectSizeSeed(
        event_type="CPI / inflation surprise",
        instrument="SPY / ES",
        direction="conditional",
        typical_magnitude="0.5-1.5%",
        reaction_half_life="minutes_hours",
        direction_confidence="high",
        surprise_dependent="yes",
    )
    db.insert_models("effect_size_seed", [seed], con=con)
    # when it is read back by its composite key
    fetched = db.get_effect_size("CPI / inflation surprise", "SPY / ES", con=con)
    # then an equal model comes back
    assert fetched == seed


def test_get_effect_size_missing_returns_none() -> None:
    # given a seeded but empty effect_size_seed table
    con = _seeded_connection()
    # when an unknown pair is queried
    # then None is returned
    assert db.get_effect_size("nope", "nope", con=con) is None


def test_insert_models_returns_count_and_count_rows_agree() -> None:
    # given two instruments
    con = _seeded_connection()
    rows = [
        Instrument(symbol="SPY / ES", name="S&P 500", asset_class="equity_index", region="us"),
        Instrument(symbol="VIX", name="Volatility", asset_class="volatility", region="us"),
    ]
    # when they are inserted
    inserted = db.insert_models("instruments", rows, con=con)
    # then the returned count and count_rows both report two
    assert inserted == 2
    assert db.count_rows("instruments", con=con) == 2


def test_insert_models_empty_is_noop() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when an empty sequence is inserted
    # then it writes nothing and reports zero
    assert db.insert_models("instruments", [], con=con) == 0
    assert db.count_rows("instruments", con=con) == 0


def test_unknown_table_is_rejected() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when an unknown table name is used
    # then it raises rather than building SQL
    with pytest.raises(ValueError):
        db.count_rows("instruments; DROP TABLE instruments", con=con)
    with pytest.raises(ValueError):
        db.insert_models("not_a_table", [], con=con)
