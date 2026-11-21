import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path
from types import ModuleType

from fortuneteller.models import EventInstance
from fortuneteller.sources import DailyClosingPrice

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "expert_test.py"


def _script() -> ModuleType:
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("expert_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _closes(prices: list[float]) -> list[DailyClosingPrice]:
    return [DailyClosingPrice(date(2024, 1, 1 + i), p) for i, p in enumerate(prices)]


def _rule(**values: str) -> dict[str, str]:
    rule = dict.fromkeys(("on", "closes", "side", "threshold", "other_flow", "other_kind"), "")
    rule |= {"flow": "cpi", "kind": "above", "condition": "none", "market": "SPY / ES"}
    rule |= {"span": "day", "direction": "up"}
    return rule | values


def test_a_condition_s_move_ends_at_the_close_before_the_reaction_close() -> None:
    # given 23 closes, flat to the 22nd, and a jump on the 23rd, the reaction close
    closes = _closes([100.0] * 22 + [150.0])
    move_before = _script().move_before

    # when the 21-close move before the reaction day is read
    move = move_before(closes, date(2024, 1, 23), 21, "pct")

    # then the jump is not in it, and a yield's move is in basis points
    assert move == 0.0
    assert move_before(_closes([1.0] * 21 + [1.5, 9.0]), date(2024, 1, 23), 21, "bps") == 50.0
    assert move_before(closes, date(2024, 1, 10), 21, "pct") is None


def test_only_the_rule_language_is_testable() -> None:
    # given the kinds of two flows
    kinds_of = {"cpi": ("above", "as expected", "below"), "earnings500": ("above", "below")}
    testable = _script().testable

    # when rules in and outside the language are judged
    # then a plain rule, a move and an event on another kind are testable
    assert testable(_rule(), kinds_of)
    move = {"condition": "move", "on": "UST5Y / ZF", "closes": "63", "side": "above"}
    assert testable(_rule(**move, threshold="50"), kinds_of)
    assert testable(_rule(condition="event", other_flow="cpi", other_kind="below"), kinds_of)
    # and a wrong span, closes, market, kind or the rule's own kind as its event are not
    assert not testable(_rule(span="quarter"), kinds_of)
    assert not testable(_rule(**{**move, "closes": "30"}, threshold="50"), kinds_of)
    assert not testable(_rule(market="company"), kinds_of)
    assert not testable(_rule(kind="hot"), kinds_of)
    assert not testable(_rule(condition="event", other_flow="cpi", other_kind="above"), kinds_of)
    assert not testable(_rule(flow="earnings500", market="SPY / ES"), kinds_of)


def test_a_move_condition_is_met_above_or_below_its_threshold() -> None:
    # given an index up 10% over the 21 closes before an event's reaction day
    prices = [100.0] * 2 + [110.0] * 21
    closes = {"SPY / ES": _closes(prices)}
    event = EventInstance(
        event_id=1,
        event_type="CPI / inflation surprise",
        event_ts=datetime(2024, 1, 23, 13, 30),
        country="US",
        detail=None,
        scheduled=True,
        consensus=None,
        actual=None,
        surprise=None,
        surprise_sd=None,
        surprise_source=None,
        priced_in_prior=None,
        vix_t0=None,
        rate_regime=None,
        quality="first_release",
    )
    meets = _script().meets
    rule = _rule(condition="move", on="SPY / ES", closes="21")

    # when the rule asks for a rise above 5% and above 15%, and a fall below 0%
    # then only the first is met
    assert meets(event, {**rule, "side": "above", "threshold": "5"}, closes, [])
    assert not meets(event, {**rule, "side": "above", "threshold": "15"}, closes, [])
    assert not meets(event, {**rule, "side": "below", "threshold": "0"}, closes, [])
