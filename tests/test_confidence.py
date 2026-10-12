"""Rung 3's confident calls: each walk-forward call with a probability, a drift probability and a
band, from what came before it."""

import random

import pytest

from fortuneteller.study import MIN_CALLS, ConfidentCall, confident_calls

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
    # of those before it and the share of earlier noticeable releases that closed its way
    assert all(c.probability is c.drift is c.band is None for c in planted[:MIN_CALLS])
    right = sum(c.call.right for c in planted[:MIN_CALLS])
    earlier = [r for r in releases[: first.call.event_id] if abs(r[2]) >= STEP]
    with_it = sum(first.call.direction * r[3] > 0 for r in earlier)
    assert first.probability == (right + 1) / (MIN_CALLS + 2)
    assert first.drift == (with_it + 1) / (len(earlier) + 2)


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
