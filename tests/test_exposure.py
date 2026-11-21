import importlib.util
from datetime import date, timedelta
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "exposure_check.py"


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("exposure_check", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_groups_are_cut_at_the_rubric_s_scores() -> None:
    # given four members' scores
    scores = {"A": 5.0, "B": 3.0, "C": 0.0, "D": -3.0}

    # when they are cut at +3 and -3
    found = _script().groups(scores, 3, -3)

    # then the high group is A and B, the low D
    assert (found.high, found.low) == (["A", "B"], ["D"])


def test_the_sector_score_leaves_the_member_out() -> None:
    # given three members in one SIC major group and one alone in another
    scores = {"A": 4.0, "B": 2.0, "C": 0.0, "D": 5.0}
    sic = {"A": "1311", "B": "1381", "C": "1389", "D": "7372"}

    # when each is given its sector's score
    found = _script().sector_scores(scores, sic)

    # then each is the mean of the others in its group, and the lone member is left out
    assert found == {"A": 1.0, "B": 2.0, "C": 3.0}


def test_the_spread_is_the_high_mean_less_the_low_mean() -> None:
    # given excess moves on one day for two high and one low member, one high member missing it
    day = date(2020, 3, 9)
    script = _script()
    g = script.Groups(["A", "B", "E"], ["C"])
    moves = {"A": {day: 0.04}, "B": {day: 0.02}, "C": {day: -0.01}}

    # when the spread is taken
    found = script.spread(g, moves, day)

    # then it is the mean of A and B less C, the missing member skipped
    assert abs(found - 0.04) < 1e-12


def test_the_base_counts_the_504_closes_before_2020_with_the_kind_s_sign() -> None:
    # given 604 closes, 504 of them before 2020 with the high group ahead on every fourth
    script = _script()
    start = date(2020, 1, 1) - timedelta(days=504)
    days = [start + timedelta(days=i) for i in range(604)]
    g = script.Groups(["A"], ["B"])
    moves = {
        "A": {d: (0.01 if i % 4 == 0 else -0.01) for i, d in enumerate(days)},
        "B": dict.fromkeys(days, 0.0),
    }

    # when a cell with no events is measured
    found = script.measure(g, moves, days, [], 1, 10)

    # then its base is a quarter, and it has no events
    assert (found.base, found.n) == (0.25, 0)


def test_the_walk_forward_grades_only_once_the_events_before_answer() -> None:
    # given 40 events all right against a base of a half
    script = _script()

    # when they are walked forward
    hits, graded, held = script.walk_forward([True] * 40, 0.5)

    # then the first graded is the one after 10 right (p of 10 of 10 is under 0.01), and it holds
    assert (hits, graded, held) == (30, 30, True)
