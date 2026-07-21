"""Shared pytest fixtures for the M0-08 smoke tests and the M0-R replay tests."""

from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, seed
from fortuneteller.config import settings


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="rewrite episodes/*.golden.json from current replay() output",
    )


@pytest.fixture
def seeded_con() -> Iterator[duckdb.DuckDBPyConnection]:
    # given an in-memory DuckDB with the schema applied and every seed CSV loaded
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    seed.load_all(con=con)
    # then replay tests get the seeded reference data without touching data/fortuneteller.duckdb
    yield con
    con.close()


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # given settings.db_path redirected to a throwaway temp file (test_ prefix marks the artifact)
    db_path = tmp_path / "test_fortuneteller.duckdb"
    monkeypatch.setattr(settings, "db_path", db_path)
    # when the schema is applied to the fresh temp store
    db.init_db()
    # then tests get an initialized, empty on-disk DB that never touches data/fortuneteller.duckdb
    return db_path
