"""Surprise computation — pipeline stage 5 (M1-01).

Pure functions, no clock / IO / randomness: turn a release's ``consensus`` / ``actual`` into a
signed surprise, standardize it against recent history, and read its sign. The standardized surprise
is what the conditional-direction resolver (M1-03) and the replay engine act on. ``surprise_sign``
is the single source of truth the replay engine reads too, so the harness keeps one convention.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from typing import Literal

# Standardize against the most recent surprises only; too short a window isn't enough signal.
MIN_HISTORY = 24
MAX_WINDOW = 36


def compute_surprise(consensus: float, actual: float) -> float:
    """Signed surprise — how far the release landed from consensus (``actual - consensus``)."""
    return actual - consensus


def standardize(surprise: float, history: Sequence[float]) -> float | None:
    """Surprise in standard deviations of recent history, or ``None`` when it can't be computed.

    Uses the last ``MAX_WINDOW`` historical surprises; returns ``None`` if fewer than
    ``MIN_HISTORY`` are available or their standard deviation is zero (no dispersion to divide by).
    """
    window = list(history[-MAX_WINDOW:])
    if len(window) < MIN_HISTORY:
        return None
    spread = statistics.stdev(window)
    if spread == 0:
        return None
    return surprise / spread


def surprise_sign(surprise_sd: float | None) -> Literal["above", "below", "unknown"]:
    """Standardized-surprise direction: ``above`` if positive, ``below`` if negative, else unknown."""
    if surprise_sd is None:
        return "unknown"
    if surprise_sd > 0:
        return "above"
    if surprise_sd < 0:
        return "below"
    return "unknown"
