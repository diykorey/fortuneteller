import importlib.util
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "news_moves.py"


def _script() -> ModuleType:
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("news_moves", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _utc(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def test_an_8k_falls_to_the_close_whose_window_holds_it_in_new_york_time() -> None:
    # given trading days around a summer and a winter weekend
    days = [date(2024, 7, 11), date(2024, 7, 12), date(2024, 7, 15), date(2024, 1, 11)]
    days.sort()
    window = _script().window_day

    # when 8-Ks accepted around 16:00 New York, given in UTC, are placed
    # then 16:00:00 is the day's, 16:00:01 the next close's, in summer (UTC-4) and winter (UTC-5)
    assert window(_utc("2024-07-11T20:00:00"), days) == date(2024, 7, 11)
    assert window(_utc("2024-07-11T20:00:01"), days) == date(2024, 7, 12)
    assert window(_utc("2024-07-11T20:01:00"), days) == date(2024, 7, 12)
    assert window(_utc("2024-01-11T21:00:00"), days) == date(2024, 1, 11)
    assert window(_utc("2024-01-10T21:01:00"), days) == date(2024, 1, 11)
    # and a Saturday's 8-K and a Friday evening's fall to Monday
    assert window(_utc("2024-07-13T15:00:00"), days) == date(2024, 7, 15)
    assert window(_utc("2024-07-12T20:01:00"), days) == date(2024, 7, 15)


def test_a_big_move_is_three_deviations_of_the_moves_before_or_more() -> None:
    # given moves before of +1 and -1 points, a deviation of 1 point
    before = [0.01, -0.01] * 252
    big = _script().big

    # when moves at, beyond and under three deviations are judged
    # then three deviations or more is big, either way, and under it is not
    assert big(0.03, before)
    assert big(-0.031, before)
    assert not big(0.0299, before)
