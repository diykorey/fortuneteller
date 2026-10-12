"""Rung 3's confident calls: each walk-forward call with a probability, a drift probability and a
band, from what came before it."""

import random
from statistics import quantiles

import pytest

from fortuneteller.stats import binomial_range, sign_flip_p, theil_sen
from fortuneteller.study import (
    COIN_BRIER,
    HONEST,
    MIN_CALLS,
    NOT_HONEST,
    TOO_CLOSE,
    TOO_FEW,
    ConfidentCall,
    Prediction,
    confident_calls,
    grade_confidence,
)

STEP = 0.1


def _releases(count: int, follows: float, seed: int = 11) -> list[tuple[int, str, float, float]]:
    # Surprises around zero; each move goes the surprise's way with probability ``follows``, its size
    # in proportion to the surprise, plus a little noise.
    rng = random.Random(seed)
    releases = []
    for i in range(count):
        surprise = round(rng.gauss(0, 0.15), 2)
        way = 1 if rng.random() < follows else -1
        releases.append((i, f"r{i}", surprise, way * 0.01 * surprise + rng.gauss(0, 0.0002)))
    return releases


@pytest.fixture(scope="module")
def planted() -> list[ConfidentCall]:
    return confident_calls(_releases(400, 0.8), expected_sign=1, step=STEP)


def test_a_link_right_on_80_percent_of_calls_states_about_80(planted: list[ConfidentCall]) -> None:
    # given 400 planted releases whose moves follow 80% of surprises, replayed
    stated = [c.probability for c in planted if c.probability is not None]

    # when / then its last 100 stated probabilities average near 80%
    assert len(stated) >= 100
    assert 0.75 <= sum(stated[-100:]) / 100 <= 0.85


def test_planted_moves_land_in_their_band_about_half_the_time(
    planted: list[ConfidentCall],
) -> None:
    # given the planted calls that carry a band
    banded = [c for c in planted if c.band is not None]

    # when each move is checked against its band
    inside = sum(c.band[0] <= c.call.move <= c.band[1] for c in banded if c.band)

    # then about half land inside
    assert 0.4 <= inside / len(banded) <= 0.6


def test_the_first_calls_state_nothing_and_later_ones_their_record(
    planted: list[ConfidentCall],
) -> None:
    # given the planted calls and the releases behind them
    releases = _releases(400, 0.8)
    first = planted[MIN_CALLS]

    # when / then the first MIN_CALLS calls carry nothing, and the next states the smoothed record
    # of those before it, the share of earlier noticeable releases that closed its way, and the
    # slope's move plus the quartiles of their misses
    assert all(c.probability is c.drift is c.band is None for c in planted[:MIN_CALLS])
    right = sum(c.call.right for c in planted[:MIN_CALLS])
    earlier = [r for r in releases[: first.call.event_id] if abs(r[2]) >= STEP]
    with_it = sum(first.call.direction * r[3] > 0 for r in earlier)
    assert first.probability == (right + 1) / (MIN_CALLS + 2)
    assert first.drift == (with_it + 1) / (len(earlier) + 2)
    slope = theil_sen([r[2] for r in earlier], [r[3] for r in earlier])
    low, _, high = quantiles([r[3] - slope * r[2] for r in earlier], n=4, method="inclusive")
    middle = slope * first.call.surprise
    assert first.band == (middle + low, middle + high)


def test_nothing_at_or_after_a_call_changes_its_numbers() -> None:
    # given 120 releases; for three calls with a probability, two versions: the call's own move
    # reversed and doubled, and new releases after it
    releases = _releases(120, 0.8, seed=4)
    calls = [c for c in confident_calls(releases, 1, STEP) if c.probability is not None]
    rng = random.Random(9)

    def numbers(versions: list[tuple[int, str, float, float]], at: int) -> list[object]:
        return [
            (c.probability, c.drift, c.band)
            for c in confident_calls(versions, 1, STEP)
            if c.call.event_id == at
        ]

    # when each is replayed
    differing = []
    for c in (calls[0], calls[len(calls) // 2], calls[-1]):
        at = c.call.event_id
        event_id, month, surprise, move = releases[at]
        tail = [(121 + i, f"t{i}", rng.gauss(0, 0.3), rng.gauss(0, 0.01)) for i in range(5)]
        changed = [*releases[:at], (event_id, month, surprise, -2 * move), *tail]
        if numbers(changed, at) != [(c.probability, c.drift, c.band)]:
            differing.append(at)

    # then no call's probability, drift or band depends on its own move or anything after it
    assert differing == []


def test_a_call_whose_earlier_noticeable_surprises_are_all_equal_has_no_band() -> None:
    # given a link whose noticeable surprises are all 0.2 and whose moves follow 85% of them; the
    # small surprises vary, so the gate can still open
    rng = random.Random(7)
    releases = []
    for i in range(160):
        surprise = 0.2 if i % 2 else round(rng.uniform(-0.05, 0.05), 3)
        way = 1 if rng.random() < 0.85 else -1
        releases.append((i, f"r{i}", surprise, way * 0.01 * surprise + rng.gauss(0, 0.0002)))

    # when it is replayed
    stated = [c for c in confident_calls(releases, 1, STEP) if c.probability is not None]

    # then its calls state a probability but no band
    assert stated
    assert all(c.band is None for c in stated)


def _graded(
    n: int, stated: float, drift: float, right_in_10: int, inside_in_4: int = 2
) -> list[ConfidentCall]:
    # n up calls stating ``stated`` and ``drift``; ``right_in_10`` of every 10 close up, and
    # ``inside_in_4`` of every 4 moves land in their band
    calls = []
    for i in range(n):
        move = 0.01 if i % 10 < right_in_10 else -0.01
        band = (move - 0.001, move + 0.001) if i % 4 < inside_in_4 else (move + 1, move + 2)
        calls.append(ConfidentCall(Prediction(i, "2020-01", 0.2, 1, move), stated, drift, band))
    return calls


def test_the_binomial_range_and_the_sign_flip_test() -> None:
    # given / when / then 48 calls at 65% allow 25 to 37 right, and differences all one way are
    # unlikely by chance while balanced ones are not
    assert binomial_range(48, 0.65) == (25, 37)
    assert binomial_range(80, 0.5) == (31, 49)
    assert sign_flip_p([0.01] * 30) < 0.001
    assert sign_flip_p([0.01, -0.01] * 15) > 0.4


def test_a_link_right_as_often_as_it_says_and_beating_drift_is_honest() -> None:
    # given 200 calls stating 70%, right on 70%, against a drift of 50%; half the moves in band
    # when they are graded
    g = grade_confidence(_graded(200, 0.7, 0.5, 7), STEP)

    # then every check passes
    assert (g.verdict, g.failed) == (HONEST, ())
    assert (g.calls, g.right, g.inside, g.banded) == (200, 140, 100, 200)


def test_a_link_no_better_than_the_drift_is_not_honest() -> None:
    # given calls all up stating 55%, on moves that close up 60% of the time whatever the surprise,
    # which the drift states
    # when they are graded
    g = grade_confidence(_graded(200, 0.55, 0.6, 6), STEP)

    # then the link does not beat drift
    assert g.brier >= g.drift_brier
    assert (g.verdict, g.failed) == (NOT_HONEST, ("drift",))


def test_a_band_half_as_wide_as_it_should_be_is_not_honest() -> None:
    # given an honest link whose bands hold only a quarter of the moves
    # when they are graded
    g = grade_confidence(_graded(200, 0.7, 0.5, 7, inside_in_4=1), STEP)

    # then the band check fails
    assert (g.verdict, g.failed) == (NOT_HONEST, ("band",))


def test_a_link_stating_75_percent_but_right_half_the_time_is_not_calibrated() -> None:
    # given calls stating 75%, right on 50%, against a drift of 50%
    # when they are graded
    g = grade_confidence(_graded(100, 0.75, 0.5, 5), STEP)

    # then its group is outside the allowed range, and it is not better than a coin either
    assert [(x.label, x.calls, x.passes) for x in g.groups if x.calls] == [
        ("70% and over", 100, False)
    ]
    assert g.verdict == NOT_HONEST
    assert "calibration" in g.failed


def test_a_slight_edge_on_few_calls_is_too_close_to_tell() -> None:
    # given 40 calls stating 60%, right on 60%, against a drift of 55%
    # when they are graded
    g = grade_confidence(_graded(40, 0.6, 0.55, 6), STEP)

    # then it beats both, but not clearly
    assert g.brier < g.drift_brier < COIN_BRIER
    assert g.verdict == TOO_CLOSE


def test_calls_without_a_probability_are_not_graded_and_too_few_is_said() -> None:
    # given 29 calls with a probability and 20 without
    calls = [ConfidentCall(Prediction(i, "m", 0.2, 1, 0.01), None, None, None) for i in range(20)]
    calls += _graded(29, 0.7, 0.5, 7)

    # when they are graded
    g = grade_confidence(calls, STEP)

    # then only the 29 count, and they are too few
    assert (g.calls, g.verdict) == (29, TOO_FEW)


def test_hit_rate_by_size_splits_at_twice_the_step() -> None:
    # given two calls under twice the step (one right) and one at it (right)
    calls = [
        ConfidentCall(Prediction(1, "m", 0.1, 1, 0.01), 0.6, 0.5, None),
        ConfidentCall(Prediction(2, "m", -0.19, -1, 0.01), 0.6, 0.5, None),
        ConfidentCall(Prediction(3, "m", 0.2, 1, 0.01), 0.6, 0.5, None),
    ]

    # when / then
    assert grade_confidence(calls, STEP).by_size == ((1, 2), (1, 1))
