"""Statistics shared by the measurements: pure functions on lists of numbers, no database.

Steps 3 and 4 both ask "could chance alone give this?" with a permutation test; it lives here once.
No dependency beyond the standard library.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from math import sqrt
from operator import mul
from statistics import median

# 10,000 draws put the smallest possible p at about 0.0001; the fixed seed makes every run identical.
PERMUTATIONS = 10_000
PERMUTATION_SEED = 3


def permutation_p(
    observed: float,
    draw: Callable[[random.Random], float],
    permutations: int = PERMUTATIONS,
    seed: int = PERMUTATION_SEED,
) -> float:
    """The share of random draws at least as large as ``observed``, counting the real one.

    ``draw`` builds one result from relabelled data. Counting the real labelling as a draw keeps
    ``p`` above zero: its smallest value is ``1 / (permutations + 1)``.
    """
    rng = random.Random(seed)
    as_large = sum(draw(rng) >= observed for _ in range(permutations))
    return (as_large + 1) / (permutations + 1)


def median_not_drawn(pool: Sequence[float], drawn: Sequence[int]) -> float:
    """The median of ``pool`` without the positions in ``drawn``, both sorted, without copying it."""

    def kth_not_drawn(k: int) -> float:
        position = k
        for i in drawn:
            if i > position:
                break
            position += 1
        return pool[position]

    rest = len(pool) - len(drawn)
    return (kth_not_drawn((rest - 1) // 2) + kth_not_drawn(rest // 2)) / 2


def ranks(values: Sequence[float]) -> list[float]:
    """Each value's rank, 1 for the smallest; tied values share the average of their ranks."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        for i in order[start : end + 1]:
            result[i] = (start + end) / 2 + 1
        start = end + 1
    return result


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return float(sum(map(mul, a, b)))


def _centred(values: Sequence[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [v - mean for v in values]


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rank correlation: +1 if ``y`` always rises with ``x``, -1 if it always falls."""
    cx, cy = _centred(ranks(x)), _centred(ranks(y))
    return _dot(cx, cy) / sqrt(_dot(cx, cx) * _dot(cy, cy))


def spearman_permutation_p(
    x: Sequence[float],
    y: Sequence[float],
    expected_sign: int,
    permutations: int = PERMUTATIONS,
    seed: int = PERMUTATION_SEED,
) -> float:
    """How often shuffling ``x`` across the pairs gives a rank correlation at least as strong.

    One-sided in the expected direction (``expected_sign`` +1 or -1); two-sided, on the absolute
    correlation, when no direction is expected (0). Shuffling leaves each rank vector's spread
    unchanged, so only the cross product is recomputed per draw.
    """
    cx, cy = _centred(ranks(x)), _centred(ranks(y))
    scale = sqrt(_dot(cx, cx) * _dot(cy, cy))

    def strength(shuffled: Sequence[float]) -> float:
        rho = _dot(shuffled, cy) / scale
        return abs(rho) if expected_sign == 0 else expected_sign * rho

    shuffled = list(cx)

    def draw(rng: random.Random) -> float:
        rng.shuffle(shuffled)
        return strength(shuffled)

    return permutation_p(strength(cx), draw, permutations, seed)


def theil_sen(x: Sequence[float], y: Sequence[float]) -> float:
    """The median slope over every pair of points with different ``x``: a line one wild point
    cannot drag."""
    slopes = [
        (y[j] - y[i]) / (x[j] - x[i])
        for i in range(len(x))
        for j in range(i + 1, len(x))
        if x[j] != x[i]
    ]
    return median(slopes)
