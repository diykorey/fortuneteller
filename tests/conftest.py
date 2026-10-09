"""Shared pytest fixtures for the M0-08 smoke tests."""

from pathlib import Path

import pytest

from fortuneteller import db, expectations
from fortuneteller.config import settings


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # given settings.db_path redirected to a throwaway temp file (test_ prefix marks the artifact)
    db_path = tmp_path / "test_fortuneteller.duckdb"
    monkeypatch.setattr(settings, "db_path", db_path)
    # when the schema is applied to the fresh temp store
    db.init_db()
    # then tests get an initialized, empty on-disk DB that never touches data/fortuneteller.duckdb
    return db_path


@pytest.fixture(autouse=True)
def no_calendars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Nasdaq's and TradingView's calendars are never asked in tests, and nothing is cached in data/;
    # a test that needs calendar rows patches expectations.fetch_calendars itself.
    monkeypatch.setattr(settings, "cache_dir", tmp_path / "cache")
    monkeypatch.setattr(expectations, "fetch_calendars", lambda days, cache_dir: ([], []))
