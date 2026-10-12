"""Rung 2's walk-forward: each release predicted only from the releases before it."""

import random
from datetime import date
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, expectations, flows
from fortuneteller.__main__ import main
from fortuneteller.sources import CORE, FirstRelease

from fortuneteller.stats import binomial_p
from fortuneteller.study import (
    DOESNT_HOLD,
    HOLDS,
    TOO_FEW,
    Prediction,
    grade,
    is_open,
    walk_forward,
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


def test_the_binomial_p_is_the_chance_a_coin_does_as_well() -> None:
    # given a few records
    # when / then the one-sided chance of doing at least as well with a fair coin
    assert binomial_p(10, 10) == 1 / 1024
    assert binomial_p(5, 10) == 638 / 1024
    assert binomial_p(0, 0) == 1.0


def _made(rights: int, wrongs: int) -> list[Prediction]:
    # Every prediction says up; the right ones' moves are up, the wrong ones' down.
    return [Prediction(i, "2020-01", 0.2, 1, 0.01) for i in range(rights)] + [
        Prediction(rights + i, "2020-01", 0.2, 1, -0.01) for i in range(wrongs)
    ]


@pytest.mark.parametrize(
    ("rights", "wrongs", "verdict"),
    [(20, 5, TOO_FEW), (40, 10, HOLDS), (340, 260, DOESNT_HOLD), (33, 17, DOESNT_HOLD)],
)
def test_a_link_holds_only_on_enough_predictions_right_often_enough(
    rights: int, wrongs: int, verdict: str
) -> None:
    # given a record: too short; 80% of 50; 57% of 600, significant but under 60%; 66% of 50,
    # over 60% but not significant (p 0.016)
    # when it is graded
    g = grade(_made(rights, wrongs), expected_sign=1)

    # then the verdict follows the rule
    assert (g.predictions, g.right, g.verdict) == (rights + wrongs, rights, verdict)


def test_the_baseline_is_the_expected_direction_whatever_the_surprise() -> None:
    # given four calls of a link expected to rise: two say down on a falling day, two up on rising
    made = [
        Prediction(1, "m", -0.2, -1, -0.01),
        Prediction(2, "m", -0.2, -1, -0.01),
        Prediction(3, "m", 0.2, 1, 0.01),
        Prediction(4, "m", 0.2, 1, 0.01),
    ]

    # when it is graded
    g = grade(made, expected_sign=1)

    # then the link was right on all four, always saying up only on two
    assert (g.right, g.always_right, g.first) == (4, 2, "m")


def _store_consensus_history(con: duckdb.DuckDBPyConnection) -> None:
    # 156 monthly CPI releases, 2010 to 2022, with a consensus surprise; each market follows 85% of them
    # in its expected direction.
    rng = random.Random(3)
    months = [date(2010 + i // 12, i % 12 + 1, 1) for i in range(156)]
    releases = [
        FirstRelease(m, date(m.year + m.month // 12, m.month % 12 + 1, 14), 1.0) for m in months
    ]
    flows.store_releases(flows.CPI_FLOW, releases, con=con)
    for event in flows.stored_events(flows.CPI_FLOW, con=con):
        surprise = round(rng.gauss(0, 0.15), 2)
        con.execute(
            "INSERT INTO surprises VALUES (?, ?, ?, 0, 0, ?)",
            [event.event_id, CORE, expectations.NASDAQ_CONSENSUS, surprise],
        )
        way = 1 if rng.random() < 0.85 else -1
        for instrument, sign in flows.EXPECTED_SIGN.items():
            move = (sign or 1) * way * 0.01 * surprise + rng.gauss(0, 0.0002)
            con.execute(
                "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
                "VALUES (?, ?, 'pct', ?)",
                [event.event_id, instrument, move],
            )


def test_predict_prints_each_link_s_record_and_verdict(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a CPI history whose markets follow 85% of consensus surprises
    _store_consensus_history(db.get_connection())

    # when the walk-forward is printed
    code = main(["predict", "--event", "cpi"])

    # then every link with a direction gets a row in both tables, and the yield holds
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert (
        out[0]
        == "core against Nasdaq's consensus: each release predicted only from the ones before it"
    )
    assert [line for line in out if line.startswith("walk-forward")] == [
        "walk-forward (all)",
        "walk-forward (without 2020-03 … 2021-04)",
    ]
    rows = [line for line in out if line.startswith("UST10Y / ZN")]
    assert len(rows) == 2 and all(row.endswith(" holds") for row in rows)
    predicted = [int(row.split()[5]) for row in rows]
    assert predicted[0] > predicted[1]
    assert sum(line.startswith(("SPY", "UST10Y", "DXY", "VIX")) for line in out) == 8
    assert not any(line.startswith("GC / XAU") for line in out)


def test_predict_asks_for_the_loads_it_needs(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given nothing stored

    # when the walk-forward is asked for
    code = main(["predict", "--event", "nfp"])

    # then it names the loads to run
    assert code == 1
    assert "load-surprises" in capsys.readouterr().err
