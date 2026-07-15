"""The ``replay()`` core plus the thin IO helpers the CLI wraps it in (M0-R-02).

``replay`` is a pure function: a fixture in, a list of :class:`Warning` out, over the read-only
seeded DuckDB. It looks up each ``(event_type, instrument)`` cell in ``effect_size_seed`` — a
non-conditional cell resolves to its concrete seed direction, a ``conditional`` cell stays
``"conditional"`` (M1 resolves it), and a missing cell yields an honest "no edge" warning instead of
raising. ``surprise_sign`` and ``as_of`` come straight from the fixture, so the same inputs always
serialize to identical bytes. Everything below the core (``load_fixture`` / ``validate_keys`` /
the serializers) is the surface the ``replay`` CLI subcommand calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import duckdb
from pydantic import ValidationError

from .. import db
from ..models import Confidence, Direction
from .models import Fixture, Warning

DISCLAIMER = "Not investment advice."
NO_EDGE_MAGNITUDE = "no edge vs market-implied"


def _surprise_sign(surprise_sd: float | None) -> Literal["above", "below", "unknown"]:
    """Standardized-surprise direction: ``above`` if positive, ``below`` if negative, else unknown."""
    if surprise_sd is None:
        return "unknown"
    if surprise_sd > 0:
        return "above"
    if surprise_sd < 0:
        return "below"
    return "unknown"


def replay(fixture: Fixture, con: duckdb.DuckDBPyConnection | None = None) -> list[Warning]:
    """Run one fixture through the deterministic core, one ``Warning`` per instrument, in order."""
    event = fixture.event
    surprise_sign = _surprise_sign(event.surprise_sd)
    warnings: list[Warning] = []
    for symbol in fixture.instruments:
        cell = db.get_effect_size(event.event_type, symbol, con=con)
        if cell is None:
            # No seed cell for this pair — emit an honest "no edge" warning, never raise.
            warnings.append(
                Warning(
                    instrument=symbol,
                    direction=Direction.mixed,
                    magnitude=NO_EDGE_MAGNITUDE,
                    half_life=None,
                    confidence=Confidence.low,
                    event_type=event.event_type,
                    surprise_sign=surprise_sign,
                    as_of=event.t0,
                    disclaimer=DISCLAIMER,
                )
            )
            continue
        # Found: use the seed direction as-is — concrete for non-conditional cells, "conditional"
        # for conditional cells (turning that into up/down is M1's enrichment).
        warnings.append(
            Warning(
                instrument=symbol,
                direction=cell.direction,
                magnitude=cell.typical_magnitude,
                half_life=cell.reaction_half_life,
                confidence=cell.direction_confidence,
                event_type=event.event_type,
                surprise_sign=surprise_sign,
                as_of=event.t0,
                disclaimer=DISCLAIMER,
            )
        )
    return warnings


def load_fixture(path: Path) -> Fixture:
    """Parse + validate a fixture file, raising a legible error naming the file on failure."""
    try:
        return Fixture.model_validate_json(path.read_text())
    except ValidationError as exc:
        raise ValueError(f"invalid fixture {path.name}: {exc}") from exc


def validate_keys(fixture: Fixture, con: duckdb.DuckDBPyConnection | None = None) -> None:
    """Reject fixtures whose event_type / instruments aren't canonical seed keys (vs a missing cell)."""
    if db.get_event_type(fixture.event.event_type, con=con) is None:
        raise ValueError(
            f"unknown event_type {fixture.event.event_type!r}: not in data/seed/event_types.csv"
        )
    for symbol in fixture.instruments:
        if db.get_instrument(symbol, con=con) is None:
            raise ValueError(f"unknown instrument {symbol!r}: not in data/seed/instruments.csv")


def warnings_to_json(warnings: list[Warning]) -> str:
    """Serialize warnings to the canonical JSON used by the golden files (trailing newline)."""
    return json.dumps([w.model_dump(mode="json") for w in warnings], indent=2) + "\n"


def warnings_to_table(warnings: list[Warning]) -> str:
    """Render warnings as a padded human-readable table for the default (non-``--json``) output."""
    headers = ["instrument", "direction", "magnitude", "half_life", "confidence", "surprise_sign"]
    rows: list[list[str]] = [
        [
            w.instrument,
            str(w.direction),
            w.magnitude,
            str(w.half_life) if w.half_life is not None else "-",
            str(w.confidence),
            w.surprise_sign,
        ]
        for w in warnings
    ]
    widths = [
        max([len(headers[i]), *(len(row[i]) for row in rows)]) for i in range(len(headers))
    ]
    lines = ["  ".join(header.ljust(widths[i]) for i, header in enumerate(headers))]
    lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    lines.extend(
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) for row in rows
    )
    return "\n".join(lines)
