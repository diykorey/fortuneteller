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
