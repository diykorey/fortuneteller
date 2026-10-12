"""Rung 2's walk-forward: each release predicted only from the releases before it."""

import random

from fortuneteller.study import Prediction, is_open, walk_forward

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


def test_a_link_that_follows_80_percent_of_surprises_opens_and_grades_near_80() -> None:
    # given 200 releases whose moves follow 80% of surprises
    releases = _releases(200, 0.8)

    # when they are replayed
    predictions = walk_forward(releases, expected_sign=1, step=STEP)

    # then it predicts most noticeable releases, and is right about 80% of the time
    noticeable = sum(abs(r[2]) >= STEP for r in releases)
    right = sum(p.right for p in predictions) / len(predictions)
    assert len(predictions) > 0.7 * noticeable
    assert 0.7 < right < 0.9


def test_a_link_with_no_relation_rarely_opens() -> None:
    # given 200 releases whose moves ignore the surprise
    rng = random.Random(5)
    releases = [(i, f"r{i}", round(rng.gauss(0, 0.15), 2), rng.gauss(0, 0.01)) for i in range(200)]

    # when they are replayed
    predictions = walk_forward(releases, expected_sign=1, step=STEP)

    # then it stays silent on almost every release
    noticeable = sum(abs(r[2]) >= STEP for r in releases)
    assert len(predictions) < 0.1 * noticeable


def test_each_decision_uses_only_the_releases_before_it() -> None:
    # given releases that follow 80% of surprises
    releases = _releases(120, 0.8)

    # when they are replayed
    predicted = {p.event_id for p in walk_forward(releases, expected_sign=1, step=STEP)}

    # then every noticeable release is predicted exactly when the link is open on those before it
    for i, (event_id, _month, surprise, _move) in enumerate(releases):
        if abs(surprise) < STEP:
            continue
        earlier = releases[:i]
        expected = is_open([e[2] for e in earlier], [e[3] for e in earlier], 1, STEP)
        assert (event_id in predicted) == expected, event_id


def test_nothing_at_or_after_a_release_changes_the_calls_before_it() -> None:
    # given releases that follow 80% of surprises, and the same with release 60's move and every
    # later surprise and move replaced
    releases = _releases(120, 0.8)
    rng = random.Random(9)
    changed = releases[:60] + [(60, "r60", releases[60][2], -releases[60][3])]
    changed += [(i, f"r{i}", rng.gauss(0, 0.3), rng.gauss(0, 0.01)) for i in range(61, 120)]

    # when both are replayed
    before = walk_forward(releases, 1, STEP)
    after = walk_forward(changed, 1, STEP)

    # then the calls up to release 60 are the same
    def calls(predictions: list[Prediction]) -> list[tuple[int, int]]:
        return [(p.event_id, p.direction) for p in predictions if p.event_id <= 60]

    assert calls(after) == calls(before)


def test_a_link_with_too_little_history_is_closed() -> None:
    # given no earlier releases, or only small surprises
    # when / then the gate stays closed
    assert not is_open([], [], 1, STEP)
    assert not is_open([0.01, 0.02, 0.03], [0.1, 0.2, 0.3], 1, STEP)


def test_a_link_expected_to_fall_predicts_against_the_surprise() -> None:
    # given 150 releases whose moves go against 80% of surprises, as stocks on a hot CPI print
    releases = [(i, m, s, -move) for i, m, s, move in _releases(150, 0.8)]

    # when they are replayed with an expected sign of -1
    predictions = walk_forward(releases, expected_sign=-1, step=STEP)

    # then each call is the opposite of the surprise's sign, and mostly right
    assert predictions
    assert all(p.direction == (-1 if p.surprise > 0 else 1) for p in predictions)
    assert sum(p.right for p in predictions) / len(predictions) > 0.7
