"""Conditional-direction resolver — surprise sign + regime → concrete direction (M1-03).

The headline M1 enrichment: turn a ``conditional`` seed cell into a concrete up / down for the
scheduled-macro CPI slice, deterministically and offline (no LLM, no network). An above-consensus
surprise resolves to the cell's ``hot_direction``; a below-consensus surprise to its inverse; an
unknown / in-line surprise or a missing mapping stays ``mixed`` (honest "no edge" — never invent a
direction). Regime-sensitive cells apply the documented "good news is bad news" override: in a
rate-cut-hungry regime a benign (below-consensus) print stops being risk-on and inverts back.

The regime override here is a deliberately simple, placeholder model over illustrative seed data —
precise, calibrated regime handling is M2/M3. The rules and cells are driven by
``docs/event-polarity-and-classifier-prompts.md`` (overriding rules) and M1-02's ``surprise_response``.
"""

from __future__ import annotations

import duckdb

from .. import db
from ..models import Direction

# Rate regimes where the market is hungry for cuts, so a benign print is "good news is bad news".
_EASING_HUNGRY_REGIMES = frozenset({"easing-hungry", "cut-hungry"})


def _invert(direction: Direction) -> Direction:
    """Flip up↔down; ``mixed`` (and anything else) stays put — there's no edge to flip."""
    if direction is Direction.up:
        return Direction.down
    if direction is Direction.down:
        return Direction.up
    return Direction.mixed


def resolve_direction(
    event_type: str,
    instrument: str,
    surprise_sign: str,
    rate_regime: str | None,
    con: duckdb.DuckDBPyConnection | None = None,
) -> Direction:
    """Resolve a conditional cell to a concrete direction, or ``mixed`` when there is no edge."""
    cell = db.get_surprise_response(event_type, instrument, con=con)
    if cell is None:
        return Direction.mixed  # no mapping → no edge; never invent a direction

    if surprise_sign == "above":
        # A hot print is already the risk-off read the base hot_direction encodes.
        return cell.hot_direction
    if surprise_sign == "below":
        direction = _invert(cell.hot_direction)
        # "Good news is bad news": in a rate-cut-hungry regime a benign print stops being risk-on
        # for a regime-sensitive instrument, so invert it back.
        if cell.regime_sensitive == "yes" and rate_regime in _EASING_HUNGRY_REGIMES:
            direction = _invert(direction)
        return direction
    # "unknown" / in-line / genuinely undetermined → honest no-edge.
    return Direction.mixed
