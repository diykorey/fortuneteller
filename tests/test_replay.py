"""M0-R-05 golden + intent tests — the fast dev loop encoded as deterministic assertions.

Each fixture in ``fixtures/*.json`` is replayed against the seeded temp DB (never
``data/fortuneteller.duckdb``) and asserted byte-exact against its ``<id>.golden.json``. A separate
intent test checks each fixture's ``expect`` directions, so a wrong-direction regression cannot be
silently blessed by ``--update-golden``. Regenerate goldens with ``pytest --update-golden`` (or
``FT_UPDATE_GOLDEN=1``) then read the git diff to confirm the change was intended.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pytest

from fortuneteller.replay.engine import replay, warnings_to_json
from fortuneteller.replay.models import Fixture

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
FIXTURE_PATHS = sorted(
    path for path in FIXTURES_DIR.glob("*.json") if not path.name.endswith(".golden.json")
)
FIXTURE_IDS = [path.stem for path in FIXTURE_PATHS]


def _load(path: Path) -> Fixture:
    return Fixture.model_validate_json(path.read_text())


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS, ids=FIXTURE_IDS)
def test_golden_matches(
    fixture_path: Path, seeded_con: duckdb.DuckDBPyConnection, request: pytest.FixtureRequest
) -> None:
    # given a committed fixture and the seeded reference data
    fixture = _load(fixture_path)
    golden_path = fixture_path.with_suffix(".golden.json")
    # when the deterministic core replays it
    produced = warnings_to_json(replay(fixture, con=seeded_con))
    update = (
        request.config.getoption("--update-golden") or os.environ.get("FT_UPDATE_GOLDEN") == "1"
    )
    if update:
        golden_path.write_text(produced)
    # then the serialized warnings match the golden byte-for-byte
    assert produced == golden_path.read_text()


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS, ids=FIXTURE_IDS)
def test_intent_directions(
    fixture_path: Path, seeded_con: duckdb.DuckDBPyConnection
) -> None:
    # given a fixture that declares expected directions
    fixture = _load(fixture_path)
    if not fixture.expect:
        pytest.skip("no expect block")
    # when it is replayed
    by_symbol = {w.instrument: w.direction for w in replay(fixture, con=seeded_con)}
    # then every expected direction holds
    for symbol, expected in fixture.expect.items():
        assert by_symbol[symbol] == expected


def test_replay_is_byte_deterministic(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given the war fixture
    fixture = _load(FIXTURES_DIR / "war-oil-shock-2026.json")
    # when it is replayed twice
    first = warnings_to_json(replay(fixture, con=seeded_con))
    second = warnings_to_json(replay(fixture, con=seeded_con))
    # then the two runs are byte-identical
    assert first == second


def test_conditional_cell_stays_conditional(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given a hot CPI fixture (surprise_sd > 0) over conditional seed cells
    fixture = _load(FIXTURES_DIR / "cpi-hot-2026-03.json")
    # when it is replayed
    warnings = replay(fixture, con=seeded_con)
    # then each conditional cell stays "conditional" with an "above" surprise_sign (M1 resolves it)
    assert all(w.direction == "conditional" for w in warnings)
    assert all(w.surprise_sign == "above" for w in warnings)


def test_missing_cell_is_no_edge(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given a fixture whose (event_type, instrument) pair has no seed cell
    fixture = _load(FIXTURES_DIR / "no-edge-2026.json")
    # when it is replayed
    (warning,) = replay(fixture, con=seeded_con)
    # then it degrades to an honest "no edge" warning rather than raising
    assert warning.direction == "mixed"
    assert warning.magnitude == "no edge vs market-implied"
    assert warning.confidence == "low"
