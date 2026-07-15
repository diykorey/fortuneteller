"""Prediction core — the deterministic middle stages the replay harness runs (M1).

Pure, offline functions: standardized-surprise computation (M1-01, :mod:`.surprise`) and the
conditional-direction resolver (M1-03, :mod:`.direction`). No network, no clock, no LLM — the
scheduled-macro CPI slice is fully determined by the surprise sign + rate regime + per-instrument
rules, so the replay harness keeps its byte-for-byte guarantee. Free-text LLM classification of
unscheduled events is M4, and lives elsewhere.
"""

from .direction import resolve_direction
from .surprise import compute_surprise, standardize, surprise_sign

__all__ = ["compute_surprise", "resolve_direction", "standardize", "surprise_sign"]
