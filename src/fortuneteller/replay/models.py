"""Fixture & Warning models — the typed contract for a replayable scenario and its output (M0-R-01).

Reuses the M0-03 enums (``Direction`` / ``HalfLife`` / ``Confidence``) rather than redefining them,
so the harness reads the same canonical vocabulary as the seed data. Every model forbids unknown
fields, so a malformed fixture fails loudly naming the offending key.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..models import Confidence, Direction, HalfLife


class _ReplayModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FixtureEvent(_ReplayModel):
    """An already-detected, classified event plus the regime context the core needs."""

    event_type: str
    t0: datetime
    scheduled: bool
    consensus: float | None = None
    actual: float | None = None
    surprise_sd: float | None = None
    vix_t0: float | None = None
    rate_regime: str | None = None


class Fixture(_ReplayModel):
    """One replayable scenario: an event, the instruments to predict, and optional intent."""

    id: str
    event: FixtureEvent
    instruments: list[str]
    expect: dict[str, Direction] | None = None


class Warning(_ReplayModel):
    """The structured, assertable output of ``replay`` for a single instrument.

    ``direction`` is ``"conditional"`` (not a concrete up/down) for conditional cells at M0-R;
    ``surprise_sign`` carries the standardized-surprise direction. ``as_of`` is set from the
    fixture's ``t0``, never ``now()`` — this is what keeps replay byte-for-byte deterministic.
    """

    instrument: str
    direction: Direction
    magnitude: str
    half_life: HalfLife | None
    confidence: Confidence
    event_type: str
    surprise_sign: Literal["above", "below", "unknown"]
    as_of: datetime
    disclaimer: str
