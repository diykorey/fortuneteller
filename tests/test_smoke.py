"""M0-08 smoke tests — the M0 'done when' encoded as automated tests.

These exercise the default-path flow end-to-end: the ``tmp_db`` fixture redirects
``settings.db_path`` at a throwaway on-disk DuckDB file, so ``init_db`` / ``load_all`` / the typed
lookups all run against the temp store and never touch ``data/fortuneteller.duckdb``.
"""

from pathlib import Path

import polars as pl

from fortuneteller import db, seed
from fortuneteller.config import settings
from fortuneteller.models import EffectSizeSeed, Instrument

ALL_TABLES = [
    "event_types",
    "instruments",
    "effect_size_seed",
    "news_sources",
    "countries",
    "event_instances",
    "observations",
    "effect_size_matrix",
]


def test_init_db_creates_all_tables_empty(tmp_db: Path) -> None:
    # given a freshly initialized temp DB (the tmp_db fixture ran init_db)
    # when each of the eight tables is counted before any seeding
    # then every table exists and holds zero rows
    assert {table: db.count_rows(table) for table in ALL_TABLES} == dict.fromkeys(ALL_TABLES, 0)


def test_load_all_counts_match_csv_rows(tmp_db: Path) -> None:
    # given the committed seed CSVs and an initialized temp DB
    expected = {
        table: pl.read_csv(settings.seed_dir / filename).height
        for filename, _model, table in seed.SEED_TABLES
    }
    # when every seed table is loaded into the temp DB
    counts = seed.load_all()
    # then the returned counts equal each CSV's data-row count
    assert counts == expected


def test_post_seed_core_tables_populated(tmp_db: Path) -> None:
    # given a fully seeded temp DB
    seed.load_all()
    # when the core reference tables are counted
    # then both hold at least one row
    assert db.count_rows("instruments") > 0
    assert db.count_rows("effect_size_seed") > 0


def test_get_effect_size_returns_model(tmp_db: Path) -> None:
    # given a fully seeded temp DB
    seed.load_all()
    # when the canonical CPI x SPY effect-size row is looked up
    row = db.get_effect_size("CPI / inflation surprise", "SPY / ES")
    # then a typed EffectSizeSeed comes back
    assert isinstance(row, EffectSizeSeed)


def test_instrument_round_trips_through_temp_db(tmp_db: Path) -> None:
    # given an Instrument written to the temp DB via the default path
    instrument = Instrument(
        symbol="TEST / RT", name="Round Trip", asset_class="equity_index", region="us"
    )
    db.insert_models("instruments", [instrument])
    # when it is read back by symbol
    fetched = db.get_instrument("TEST / RT")
    # then an equal model comes back
    assert fetched == instrument
