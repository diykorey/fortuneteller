"""Shared statistics: ranks, rank correlation, robust slope, least squares and the permutation
test."""

import random

import pytest

from fortuneteller.stats import (
    PERMUTATIONS,
    least_squares,
    permutation_p,
    ranks,
    spearman,
    spearman_permutation_p,
    theil_sen,
)


def test_tied_values_share_the_average_of_their_ranks() -> None:
    # given values with a tie in the middle
    values = [10.0, 30.0, 20.0, 20.0]

    # when they are ranked
    result = ranks(values)

    # then the two 20s share ranks 2 and 3
    assert result == [1.0, 4.0, 2.5, 2.5]


@pytest.mark.parametrize(("y", "expected"), [([1, 4, 9, 16], 1.0), ([16, 9, 4, 1], -1.0)])
def test_rank_correlation_is_one_for_any_rising_relation(y: list[float], expected: float) -> None:
    # given a relation that always rises, or always falls, but not along a line
    x = [1.0, 2.0, 3.0, 4.0]

    # when the rank correlation is computed
    result = spearman(x, y)

    # then it is exactly +1 or -1
    assert result == pytest.approx(expected)


def test_the_robust_slope_ignores_one_wild_point() -> None:
    # given points on y = 3x + 1, and one crash-day outlier
    x = [float(i) for i in range(10)]
    y = [3 * v + 1 for v in x]
    y[5] = -100.0

    # when the Theil-Sen slope is computed
    slope = theil_sen(x, y)

    # then it is still 3
    assert slope == pytest.approx(3.0)


def test_permutation_p_counts_the_real_result_as_one_of_the_draws() -> None:
    # given an observed value no draw ever reaches
    # when its p is computed
    p = permutation_p(1.0, lambda _rng: 0.0)

    # then p is the smallest possible, one in permutations + 1
    assert p == pytest.approx(1 / (PERMUTATIONS + 1))


def test_permutation_p_is_the_same_on_every_run() -> None:
    # given a draw that depends on the random numbers
    def draw(rng: random.Random) -> float:
        return rng.random()

    # when the same p is computed twice
    first, second = permutation_p(0.5, draw), permutation_p(0.5, draw)

    # then the fixed seed makes them identical, and about half the draws reach 0.5
    assert first == second
    assert first == pytest.approx(0.5, abs=0.02)


def _noisy_line(slope: float, seed: int, n: int = 300) -> tuple[list[float], list[float]]:
    rng = random.Random(seed)
    x = [rng.gauss(0, 1) for _ in range(n)]
    return x, [slope * v + rng.gauss(0, 1) for v in x]


def test_a_planted_relation_in_the_expected_direction_is_significant() -> None:
    # given moves built as 3 x surprise plus noise
    x, y = _noisy_line(3.0, seed=1)

    # when its one-sided p is computed for an expected rise, and for an expected fall
    rising = spearman_permutation_p(x, y, expected_sign=1)
    falling = spearman_permutation_p(x, y, expected_sign=-1)

    # then the rise is as significant as the test allows, and the fall is not significant at all
    assert rising == pytest.approx(1 / (PERMUTATIONS + 1))
    assert falling > 0.99


def test_no_relation_is_not_significant() -> None:
    # given moves unrelated to the surprises
    x, y = _noisy_line(0.0, seed=2)

    # when its p is computed one-sided and two-sided
    one_sided = spearman_permutation_p(x, y, expected_sign=1)
    two_sided = spearman_permutation_p(x, y, expected_sign=0)

    # then neither passes p < 0.01
    assert one_sided > 0.01
    assert two_sided > 0.01


def test_a_falling_relation_is_found_by_the_two_sided_test() -> None:
    # given moves built as -3 x surprise plus noise, with no expected direction
    x, y = _noisy_line(-3.0, seed=3)

    # when its two-sided p is computed
    p = spearman_permutation_p(x, y, expected_sign=0)

    # then it is significant
    assert p < 0.01


def test_least_squares_recovers_planted_coefficients() -> None:
    # given 40 rows of three inputs and y = 20 + 0.5·a − 2·b + 0.3·c exactly
    rng = random.Random(1)
    rows = [[rng.uniform(-300, 300), rng.uniform(-50, 50), rng.uniform(0, 400)] for _ in range(40)]
    y = [20 + 0.5 * a - 2 * b + 0.3 * c for a, b, c in rows]

    # when the fit is made
    coefficients = least_squares(rows, y)

    # then the intercept and every slope come back
    assert coefficients == pytest.approx([20, 0.5, -2, 0.3], abs=1e-9)


def test_least_squares_refuses_a_column_that_is_a_mix_of_the_others() -> None:
    # given a third input that is always the first plus twice the second
    rows = [[float(i), float(i % 7), float(i + 2 * (i % 7))] for i in range(20)]
    y = [float(i * i) for i in range(20)]

    # when / then the fit is refused
    with pytest.raises(ValueError, match="singular"):
        least_squares(rows, y)
