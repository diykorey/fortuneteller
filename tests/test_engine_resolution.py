"""M1-04 tests — replay() resolves conditional cells, independent of the golden files.

Asserts the engine wires the M1-03 resolver into the deterministic core: a hot CPI fixture's
conditional cells become concrete directions, a cool fixture's the inverses, an in-line fixture's
honest ``mixed`` — driven by the resolver, not by a committed golden snapshot.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from fortuneteller.replay.engine import replay
from fortuneteller.replay.models import Fixture

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _replay_by_symbol(name: str, con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    fixture = Fixture.model_validate_json((FIXTURES_DIR / name).read_text())
    return {w.instrument: str(w.direction) for w in replay(fixture, con=con)}


def test_hot_cpi_resolves_conditional_cells(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given the hot CPI fixture over the five core conditional cells
    # when it is replayed
    by_symbol = _replay_by_symbol("cpi-hot-2026-03.json", seeded_con)
    # then every cell is concrete (never "conditional") and matches the resolved read
    assert "conditional" not in by_symbol.values()
    assert by_symbol == {
        "SPY / ES": "down",
        "BUND / FGBL": "down",
        "DXY": "up",
        "GC / XAU": "down",
        "VIX": "up",
    }


def test_cool_cpi_resolves_to_inverses(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given the cool CPI fixture
    # when it is replayed
    by_symbol = _replay_by_symbol("cpi-cool-2026-04.json", seeded_con)
    # then each cell is the inverse of the hot read
    assert by_symbol == {
        "SPY / ES": "up",
        "BUND / FGBL": "up",
        "DXY": "down",
        "GC / XAU": "up",
        "VIX": "down",
    }


def test_in_line_cpi_resolves_to_mixed(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given the in-line CPI fixture (surprise present but ~0)
    # when it is replayed
    by_symbol = _replay_by_symbol("cpi-inline-2026-05.json", seeded_con)
    # then every cell is an honest "mixed" — a scheduled no-edge, not the "conditional" placeholder
    assert set(by_symbol.values()) == {"mixed"}
