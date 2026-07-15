"""M1-02 contract tests — the surprise_response mapping + completed CPI slice.

Locks the new reference table's keys to the canonical seed CSVs, asserts the CPI core slice is
complete in both effect_size_seed and surprise_response, and that the loader stays idempotent.
"""

from __future__ import annotations

import duckdb

from fortuneteller import db, seed

CPI = "CPI / inflation surprise"
CORE_INSTRUMENTS = {"SPY / ES", "BUND / FGBL", "DXY", "GC / XAU", "VIX"}


def _seeded_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    seed.load_all(con=con)
    return con


def test_every_surprise_response_key_is_canonical() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when every surprise_response key is checked against the canonical seed CSVs
    keys = con.execute("SELECT event_type, instrument FROM surprise_response").fetchall()
    # then each event_type and instrument exists in event_types.csv / instruments.csv
    assert keys, "surprise_response should not be empty"
    for event_type, instrument in keys:
        assert db.get_event_type(str(event_type), con=con) is not None
        assert db.get_instrument(str(instrument), con=con) is not None


def test_cpi_core_slice_is_complete() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when the CPI cells are gathered from both reference tables
    effect_cells = {
        str(row[0])
        for row in con.execute(
            "SELECT instrument FROM effect_size_seed WHERE event_type = ?", [CPI]
        ).fetchall()
    }
    response_cells = {
        str(row[0])
        for row in con.execute(
            "SELECT instrument FROM surprise_response WHERE event_type = ?", [CPI]
        ).fetchall()
    }
    # then all five core instruments are present in each
    assert CORE_INSTRUMENTS <= effect_cells
    assert response_cells == CORE_INSTRUMENTS


def test_get_surprise_response_returns_typed_row() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when the canonical CPI x SPY cell is looked up
    row = db.get_surprise_response(CPI, "SPY / ES", con=con)
    # then a typed row with the expected mapping comes back
    assert row is not None
    assert row.hot_direction == "down"
    assert row.regime_sensitive == "yes"


def test_loader_is_idempotent() -> None:
    # given a store already fully seeded once
    con = _seeded_connection()
    before = db.count_rows("surprise_response", con=con)
    # when load_all runs a second time
    counts = seed.load_all(con=con)
    # then the row count is unchanged (INSERT OR REPLACE, no duplicates)
    assert db.count_rows("surprise_response", con=con) == before
    assert counts["surprise_response"] == len(CORE_INSTRUMENTS)
