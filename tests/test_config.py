"""Tests for the M0-02 configuration module."""

from pathlib import Path

import pytest

from fortuneteller.config import Settings, settings


def test_defaults() -> None:
    # given the default settings singleton
    # when reading its paths
    # then they match the documented defaults
    assert settings.db_path == Path("data/fortuneteller.duckdb")
    assert settings.seed_dir == Path("data/seed")
    assert settings.schema_path == Path("schema.sql")


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    # given an FT_-prefixed environment override
    monkeypatch.setenv("FT_DB_PATH", "/tmp/x.duckdb")
    # when a fresh Settings instance is constructed
    overridden = Settings()
    # then the override wins
    assert overridden.db_path == Path("/tmp/x.duckdb")


def test_fred_api_key_is_declared_and_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    # given a FRED key in the environment
    monkeypatch.setenv("FT_FRED_API_KEY", "0123456789abcdef0123456789abcdef")
    # when settings are built
    configured = Settings()
    # then the key is readable at the call site
    assert configured.fred_api_key is not None
    assert configured.fred_api_key.get_secret_value() == "0123456789abcdef0123456789abcdef"
    # then it never renders itself, so a traceback cannot leak it
    assert "0123456789abcdef" not in repr(configured)
    assert "0123456789abcdef" not in str(configured.fred_api_key)


def test_fred_api_key_optional() -> None:
    # given no FRED key configured
    # when settings are built without one
    configured = Settings(fred_api_key=None)
    # then it is absent rather than an error — the key is only needed by the FRED loader
    assert configured.fred_api_key is None
