"""Shared pytest fixtures for the M0-08 smoke tests."""

import json
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, expectations, flows, sources
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
    monkeypatch.setattr(settings, "calls_path", tmp_path / "calls.csv")
    monkeypatch.setattr(settings, "guesses_dir", tmp_path / "guesses")
    monkeypatch.setattr(expectations, "fetch_calendars", lambda days, cache_dir: ([], []))

    def refuse(url: str, what: str, timeout: float) -> bytes:
        raise AssertionError(f"a test asked {what}")

    monkeypatch.setattr(sources, "_calendar_get", refuse)
    # No statement is ahead on a test's day unless the test says so.
    monkeypatch.setattr(flows.StatementFlow, "ahead", lambda self, cache_dir, now: None)


@pytest.fixture
def fred_breakeven(monkeypatch: pytest.MonkeyPatch) -> None:
    # FRED answers the breakeven with four closes around 2022-09-13, the Yahoo fixtures' days, and
    # a key is set; every other FRED series is refused, so no test reaches FRED
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))
    observations = [
        {"date": "2022-09-09", "value": "2.54"},
        {"date": "2022-09-12", "value": "2.56"},
        {"date": "2022-09-13", "value": "2.63"},
        {"date": "2022-09-14", "value": "."},
        {"date": "2022-09-15", "value": "2.60"},
    ]

    def fetch(api_key: str, series_id: str, timeout: float = 30.0) -> bytes:
        if series_id != "T5YIE":
            raise AssertionError(f"a test asked FRED for {series_id}")
        return json.dumps({"observations": observations}).encode()

    monkeypatch.setattr(sources, "fetch_series", fetch)
