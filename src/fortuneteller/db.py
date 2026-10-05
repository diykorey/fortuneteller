"""Thin SQL helper over DuckDB — the one module that owns the connection and typed access.

No ORM: Pydantic models go in, SQL runs, typed models come back. Reads bind values as ``?``
parameters; writes send the rows as one temporary Parquet file, because binding them one row at a
time took about four minutes for the 58,000 daily bars. The SQL keeps to what DuckDB and Postgres
share (``ON CONFLICT`` upserts, ``information_schema``); the one DuckDB-only call is
``read_parquet``. Everything downstream (the CLI, the M0-07 seed loader, M1 lookups) calls in here
rather than touching DuckDB directly. Every helper takes an optional ``con`` so tests can inject an
in-memory connection; when omitted it opens ``settings.db_path`` via :func:`get_connection`. Out of
scope: migrations, async.
"""

from __future__ import annotations

import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

import duckdb
import polars as pl
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
        "daily_bars",
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

    With ``replace=True`` a row whose primary key already exists is overwritten rather than rejected
    (``ON CONFLICT … DO UPDATE``, which DuckDB and Postgres share) — this is what makes every load
    idempotent. Rows that repeat a key among themselves are rejected before anything is written: a
    bulk upsert would silently keep only one of them.
    """
    if table not in _TABLES:
        raise ValueError(f"unknown table: {table!r}")
    if not rows:
        return 0
    connection = con if con is not None else get_connection()
    fields = list(type(rows[0]).model_fields)
    columns = ", ".join(fields)
    # infer_schema_length=None: a column empty in the first rows and filled later keeps its type.
    frame = pl.DataFrame([row.model_dump() for row in rows], infer_schema_length=None)
    key = _primary_key(table, connection)
    if key and frame.select(key).is_duplicated().any():
        raise ValueError(f"{table}: the rows to insert repeat a key ({', '.join(key)})")
    sql = f"INSERT INTO {table} ({columns}) SELECT {columns} FROM read_parquet(?)"
    if replace:
        if not key:
            raise ValueError(f"{table}: replace=True needs a primary key to match rows on")
        updates = ", ".join(f"{f} = EXCLUDED.{f}" for f in fields if f not in key)
        action = f"DO UPDATE SET {updates}" if updates else "DO NOTHING"
        sql += f" ON CONFLICT ({', '.join(key)}) {action}"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "rows.parquet"
        frame.write_parquet(path)
        connection.execute(sql, [str(path)])
    return len(rows)


def _primary_key(table: str, con: duckdb.DuckDBPyConnection) -> list[str]:
    rows = con.execute(
        "SELECT kcu.column_name FROM information_schema.table_constraints AS tc "
        "JOIN information_schema.key_column_usage AS kcu "
        "ON kcu.constraint_name = tc.constraint_name "
        "AND kcu.table_schema = tc.table_schema AND kcu.table_name = tc.table_name "
        "WHERE tc.table_name = ? AND tc.constraint_type = 'PRIMARY KEY' "
        "ORDER BY kcu.ordinal_position",
        [table],
    ).fetchall()
    return [row[0] for row in rows]


def replace_rows(
    table: str,
    rows: Sequence[BaseModel],
    where: str,
    params: Sequence[object] = (),
    con: duckdb.DuckDBPyConnection | None = None,
) -> int:
    """Delete the rows of ``table`` matching ``where``, then insert ``rows``, in one transaction.

    For tables rebuilt from their source on every run: an upsert alone would keep rows the new run
    no longer produces. ``where`` is SQL from this codebase, never from outside; its values go in ``params``.
    """
    if table not in _TABLES:
        raise ValueError(f"unknown table: {table!r}")
    connection = con if con is not None else get_connection()
    connection.begin()
    try:
        connection.execute(f"DELETE FROM {table} WHERE {where}", list(params))
        written = insert_models(table, rows, con=connection)
    except Exception:
        connection.rollback()
        raise
    connection.commit()
    return written


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


def fetch_all(
    cls: type[_M],
    sql: str,
    params: Sequence[object] = (),
    con: duckdb.DuckDBPyConnection | None = None,
) -> list[_M]:
    """Run ``sql`` with ``params`` bound as ``?`` and build one ``cls`` per row, by column name."""
    connection = con if con is not None else get_connection()
    cur = connection.execute(sql, list(params))
    columns = _columns(cur)
    return [cls(**dict(zip(columns, row, strict=True))) for row in cur.fetchall()]


def _fetch_one(cls: type[_M], cur: duckdb.DuckDBPyConnection) -> _M | None:
    """Build a single model from a cursor, matching columns to fields by name."""
    row = cur.fetchone()
    if row is None:
        return None
    return cls(**dict(zip(_columns(cur), row, strict=True)))


def _columns(cur: duckdb.DuckDBPyConnection) -> list[str]:
    description = cur.description
    if description is None:
        raise RuntimeError("query produced no column description")
    return [str(column[0]) for column in description]
