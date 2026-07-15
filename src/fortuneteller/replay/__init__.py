"""Replay harness — the deterministic, offline fast dev loop (M0-R).

A fixture (``fixtures/<id>.json``) carries an already-detected event plus its regime context; the
pure :func:`replay` core runs stages 5–8 (surprise → effect-size lookup → warning) and emits a list
of :class:`Warning`. No network, no clock, no randomness — same inputs yield identical bytes, which
is what makes the golden-file tests possible. Turning ``conditional`` cells into a concrete up/down
is M1's job; here they stay ``"conditional"`` alongside the standardized-surprise sign.
"""

from .engine import replay
from .models import Fixture, FixtureEvent, Warning

__all__ = ["Fixture", "FixtureEvent", "Warning", "replay"]
