"""M1-01 tests — surprise computation (compute_surprise / standardize / surprise_sign)."""

from __future__ import annotations

import statistics

from fortuneteller.predict.surprise import (
    MAX_WINDOW,
    MIN_HISTORY,
    compute_surprise,
    standardize,
    surprise_sign,
)


def test_compute_surprise_is_signed_actual_minus_consensus() -> None:
    # given a consensus and a hotter actual
    # when the surprise is computed
    # then it is the signed gap actual - consensus
    assert compute_surprise(consensus=3.1, actual=3.4) == 3.4 - 3.1
    assert compute_surprise(consensus=3.1, actual=2.8) == 2.8 - 3.1


def test_standardize_reproduces_hand_computed_sd() -> None:
    # given a synthetic history (alternating +2 / -2) with a known sample stdev
    history = [2.0, -2.0] * (MIN_HISTORY // 2)
    # when a surprise of 3.0 is standardized against it
    result = standardize(3.0, history)
    # then it equals surprise / stdev(history) exactly
    assert result == 3.0 / statistics.stdev(history)


def test_standardize_uses_only_the_last_window() -> None:
    # given a long history whose early values are wild but whose last MAX_WINDOW are ±2
    tail = [2.0, -2.0] * (MAX_WINDOW // 2)
    history = [1000.0] * 50 + tail
    # when standardized
    result = standardize(3.0, history)
    # then only the trailing window counts, so the wild prefix is ignored
    assert result == 3.0 / statistics.stdev(tail)


def test_standardize_returns_none_for_short_history() -> None:
    # given fewer than MIN_HISTORY surprises
    history = [1.0, -1.0]
    # when standardized
    # then there isn't enough signal, so None comes back
    assert standardize(3.0, history) is None


def test_standardize_returns_none_for_zero_stdev() -> None:
    # given a long but flat history (no dispersion)
    history = [1.0] * MIN_HISTORY
    # when standardized
    # then dividing by a zero stdev is undefined, so None comes back
    assert standardize(3.0, history) is None


def test_surprise_sign_reads_the_sign() -> None:
    # given standardized surprises of each sign (and the None / zero no-signal cases)
    # when their sign is read
    # then positive is "above", negative "below", and zero / None "unknown"
    assert surprise_sign(1.8) == "above"
    assert surprise_sign(-1.6) == "below"
    assert surprise_sign(0.0) == "unknown"
    assert surprise_sign(None) == "unknown"
