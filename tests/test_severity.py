import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path
from types import ModuleType

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _script() -> ModuleType:
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("severity_check", SCRIPTS / "severity_check.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_side_cut_is_minus_two_and_plus_two() -> None:
    # given scores across the scale
    side = _script().side

    # when each is given its side
    # then -2 and below are bad, +2 and above good, the rest neither
    assert [side(s) for s in (-5, -2, -1, 0, 1, 2, 5)] == [-1, -1, 0, 0, 0, 1, 1]


def test_the_base_pools_each_member_s_spans_before_2020() -> None:
    # given two members over 604 closes, one up on every close and one on none before 2020
    script = _script()
    start = date(2020, 1, 1) - timedelta(days=504)
    days = [start + timedelta(days=i) for i in range(604)]
    moves = {"A": dict.fromkeys(days, 0.01), "B": dict.fromkeys(days, -0.01)}

    # when the base for up is taken
    # then it is half: 504 up of 1,008
    assert script.base_share(moves, days, 1) == 0.5


def test_a_cell_counts_the_filings_that_moved_the_score_s_way() -> None:
    # given 12 bad filings, 11 followed by a fall and one by a rise, against a base of a half
    script = _script()
    days = [date(2021, 1, 1) + timedelta(days=i) for i in range(100)]
    filings = [script.Filing(days[20 + 5 * i], f"T{i}", "8.01", -3) for i in range(12)]
    moves = {f.ticker: {f.day: (0.02 if i == 0 else -0.02)} for i, f in enumerate(filings)}

    # when the cell is measured
    cell = script.measure(filings, moves, days, -1, 0.5)

    # then 11 of 12 are right, and it answers
    assert (cell.n, cell.k, cell.answered) == (12, 11, True)
