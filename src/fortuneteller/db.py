"""Thin SQL helper over DuckDB — the one module that owns the connection and typed access.

No ORM: Pydantic models go in, parameterized SQL runs, typed models come back. Everything
downstream (the CLI, the M0-07 seed loader, M1 lookups) calls in here rather than touching DuckDB
directly. Every helper takes an optional ``con`` so tests can inject an in-memory connection; when
omitted it opens ``settings.db_path`` via :func:`get_connection`. Out of scope: migrations, async.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import duckdb
from pydantic import BaseModel

from .config import settings
from .models import EffectSizeSeed, Instrument

# Identifiers can't be parameter-bound, so any table name we interpolate is checked against this
# fixed set first — values are always passed as ``?`` parameters.
_TABLES: frozenset[str] = frozenset(
    {
        "event_types",
        "instruments",
        "effect_size_seed",
        "news_sources",
        "countries",
        "event_instances",
        "observations",
        "effect_size_matrix",
    }
)

_M = TypeVar("_M", bound=BaseModel)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the DuckDB store at ``settings.db_path``, creating parent directories."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(settings.db_path))


def init_db(con: duckdb.DuckDBPyConnection | None = None) -> None:
    """Run ``settings.schema_path`` to create every table (the DDL is idempotent)."""
    connection = con if con is not None else get_connection()
    connection.execute(settings.schema_path.read_text())


def insert_models(
    table: str,
    rows: Sequence[BaseModel],
    con: duckdb.DuckDBPyConnection | None = None,
    replace: bool = False,
) -> int:
    """Insert Pydantic ``rows`` into ``table`` and return how many were written.

    With ``replace=True`` emit ``INSERT OR REPLACE`` so a row whose primary key already exists is
    overwritten rather than rejected — this is what makes the seed load idempotent.
    """
    if table not in _TABLES:
        raise ValueError(f"unknown table: {table!r}")
    if not rows:
        return 0
    connection = con if con is not None else get_connection()
    fields = list(type(rows[0]).model_fields)
    columns = ", ".join(fields)
    placeholders = ", ".join(["?"] * len(fields))
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    sql = f"{verb} INTO {table} ({columns}) VALUES ({placeholders})"
    connection.executemany(sql, [[getattr(row, field) for field in fields] for row in rows])
    return len(rows)


def get_instrument(symbol: str, con: duckdb.DuckDBPyConnection | None = None) -> Instrument | None:
    """Return the ``Instrument`` with this symbol, or ``None`` if absent."""
    connection = con if con is not None else get_connection()
    cur = connection.execute("SELECT * FROM instruments WHERE symbol = ?", [symbol])
    return _fetch_one(Instrument, cur)


def get_effect_size(
    event_type: str, instrument: str, con: duckdb.DuckDBPyConnection | None = None
) -> EffectSizeSeed | None:
    """Return the effect-size seed row for this (event_type, instrument) pair, or ``None``."""
    connection = con if con is not None else get_connection()
    cur = connection.execute(
        "SELECT * FROM effect_size_seed WHERE event_type = ? AND instrument = ?",
        [event_type, instrument],
    )
    return _fetch_one(EffectSizeSeed, cur)


def first_effect_size(con: duckdb.DuckDBPyConnection | None = None) -> EffectSizeSeed | None:
    """Return any one effect-size seed row, or ``None`` if the table is empty."""
    connection = con if con is not None else get_connection()
    cur = connection.execute("SELECT * FROM effect_size_seed LIMIT 1")
    return _fetch_one(EffectSizeSeed, cur)


def count_rows(table: str, con: duckdb.DuckDBPyConnection | None = None) -> int:
    """Return the number of rows in ``table``."""
    if table not in _TABLES:
        raise ValueError(f"unknown table: {table!r}")
    connection = con if con is not None else get_connection()
    row = connection.execute(f"SELECT count(*) FROM {table}").fetchone()
    assert row is not None  # count(*) always returns exactly one row
    return int(row[0])


def _fetch_one(cls: type[_M], cur: duckdb.DuckDBPyConnection) -> _M | None:
    """Build a single model from a cursor, matching columns to fields by name."""
    row = cur.fetchone()
    if row is None:
        return None
    description = cur.description
    if description is None:
        raise RuntimeError("query produced no column description")
    columns = [str(column[0]) for column in description]
    return cls(**dict(zip(columns, row, strict=True)))
