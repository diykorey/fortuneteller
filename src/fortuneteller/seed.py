"""Seed loader — read the committed reference CSVs, validate, and populate the store.

Each ``data/seed/*.csv`` is read with Polars, coerced row-by-row into its Pydantic model (so a bad
value fails loudly, naming the file and row), then written via :func:`db.insert_models`. The load is
idempotent: ``INSERT OR REPLACE`` overwrites rows by primary key, so re-running ``fortuneteller seed``
is safe. Out of scope: the fact tables (``event_instances`` / ``observations``), which stay empty in M0.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl
from pydantic import BaseModel, ValidationError

from . import db
from .config import settings
from .models import Country, EffectSizeSeed, EventType, Instrument, NewsSource

# (csv filename, model, table) — the five reference tables loaded at seed time.
SEED_TABLES: list[tuple[str, type[BaseModel], str]] = [
    ("event_types.csv", EventType, "event_types"),
    ("instruments.csv", Instrument, "instruments"),
    ("effect_size_seed.csv", EffectSizeSeed, "effect_size_seed"),
    ("news_sources.csv", NewsSource, "news_sources"),
    ("countries.csv", Country, "countries"),
]


def _load_csv(path: Path, model: type[BaseModel]) -> list[BaseModel]:
    """Validate every data row of ``path`` against ``model``, naming file+row on failure."""
    frame = pl.read_csv(path)
    rows: list[BaseModel] = []
    errors: list[str] = []
    first_error: ValidationError | None = None
    # Line 1 is the header, so the first data row is line 2.
    for line_no, record in enumerate(frame.iter_rows(named=True), start=2):
        try:
            rows.append(model.model_validate(record))
        except ValidationError as exc:
            first_error = first_error or exc
            errors.append(f"{path.name}:{line_no}: {exc}")
    if errors:
        raise ValueError("seed validation failed:\n" + "\n".join(errors)) from first_error
    return rows


def load_all(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, int]:
    """Load every seed CSV into the store and return ``{table: row_count}`` (idempotent)."""
    connection = con if con is not None else db.get_connection()
    counts: dict[str, int] = {}
    for filename, model, table in SEED_TABLES:
        rows = _load_csv(settings.seed_dir / filename, model)
        counts[table] = db.insert_models(table, rows, con=connection, replace=True)
    return counts


def query_demo(con: duckdb.DuckDBPyConnection | None = None) -> EffectSizeSeed | None:
    """Return the canonical CPI x SPY effect-size row (or any row) for the query-demo command."""
    connection = con if con is not None else db.get_connection()
    return db.get_effect_size(
        "CPI / inflation surprise", "SPY / ES", con=connection
    ) or db.first_effect_size(con=connection)
