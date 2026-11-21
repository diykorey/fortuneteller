"""Step 41's test of the expert's rules (docs/steps/expert-hypotheses.md).

`expert_check.py COMMIT` reads docs/steps/expert-hypotheses.csv as committed at COMMIT, prints its
SHA-256, and tests each rule on its events from 2020-01-01 in the store at FT_DB_PATH: the rule's
cell as `follows` answers it on the kept events, the same rule without its condition, and whether
it passes and holds by the spec's bars.

Usage: uv run python scripts/expert_check.py COMMIT
"""

import csv
import hashlib
import io
import subprocess
import sys
from bisect import bisect_left
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from fortuneteller import db, flows, stats, study
from fortuneteller.__main__ import FollowsUnavailable, follows_kinds, follows_of
from fortuneteller.models import EventInstance
from fortuneteller.sources import DailyClosingPrice

RULES = "docs/steps/expert-hypotheses.csv"
FROM = datetime(2020, 1, 1)
MIN_EVENTS, P_ANSWER, P_ADDS = 10, 0.01, 0.05
COMPANY, VS_INDEX = "company", "vs S&P 500"
COMPANY_FLOWS = {"earnings", "earnings500", "ceo", "additions", "splits"}
OTHER_WINDOW = 21


def testable(rule: dict[str, str], kinds_of: Mapping[str, Sequence[str]]) -> bool:
    """Whether every value of ``rule`` is one the spec's rule language allows."""
    flow, condition, market = rule["flow"], rule["condition"], rule["market"]
    markets = set(study.MVP_PRICE_SERIES) - {"COIN"}
    if flow not in kinds_of or rule["kind"] not in kinds_of[flow]:
        return False
    if (market == COMPANY) != (flow in COMPANY_FLOWS) or (
        market != COMPANY and market not in markets
    ):
        return False
    if rule["span"] not in study.SPANS or rule["direction"] not in (study.UP, study.DOWN):
        return False
    if condition == "none":
        return True
    if condition == "move":
        on_ok = rule["on"] in markets or (rule["on"] == COMPANY and flow in COMPANY_FLOWS)
        try:
            float(rule["threshold"])
        except ValueError:
            return False
        return on_ok and rule["closes"] in ("21", "63") and rule["side"] in ("above", "below")
    if condition == "event":
        other = rule["other_flow"]
        return (
            other in kinds_of
            and rule["other_kind"] in kinds_of[other]
            and (
                other,
                rule["other_kind"],
            )
            != (flow, rule["kind"])
        )
    return False


def close_before(closes: Sequence[DailyClosingPrice], reaction: date) -> int | None:
    """The index of the last close before the reaction day ``reaction``."""
    days = [c.day for c in closes]
    i = bisect_left(days, reaction) - 1
    return i if i >= 0 else None


def move_before(
    closes: Sequence[DailyClosingPrice], reaction: date, n: int, unit: str
) -> float | None:
    """The market's move over the ``n`` closes ending at the close before ``reaction``, in the
    rule's unit: percent for a price, basis points for a yield."""
    b = close_before(closes, reaction)
    if b is None or b < n:
        return None
    move = study.release_move(closes[b - n], closes[b], unit)
    return move * 100 if unit == "pct" else move


def meets(
    event: EventInstance,
    rule: dict[str, str],
    closes: dict[str, list[DailyClosingPrice]],
    others: list[EventInstance],
) -> bool:
    """Whether ``event`` meets the rule's condition, read at the close before its reaction close."""
    condition = rule["condition"]
    if condition == "none":
        return True
    if condition == "move":
        on = rule["on"]
        if on == COMPANY:
            ticker = (event.detail or "").split(" ")[0]
            series, prices = study.STOCK, closes.get(ticker)
        else:
            series, prices = study.MVP_PRICE_SERIES[on], closes.get(on)
        if not prices:
            return False
        move = move_before(
            prices, study.first_reaction_day(event, series), int(rule["closes"]), series.unit
        )
        if move is None:
            return False
        threshold = float(rule["threshold"])
        return move > threshold if rule["side"] == "above" else move < threshold
    index = closes["SPY / ES"]
    series = study.MVP_PRICE_SERIES["SPY / ES"]
    b = close_before(index, study.first_reaction_day(event, series))
    if b is None:
        return False
    first = index[max(b - OTHER_WINDOW + 1, 0)].day
    return any(first <= study.first_reaction_day(o, series) <= index[b].day for o in others)


def cell(
    flow: flows.EventFlow,
    events: list[EventInstance],
    kinds: dict[int, str],
    order: Sequence[str],
    rule: dict[str, str],
    con: Any,
) -> study.Follow | None:
    """The rule's cell as `follows` answers it on ``kinds``' events alone."""
    if not kinds:
        return None
    _, cells = follows_of(flow, events, kinds, order, con)
    market = VS_INDEX if rule["market"] == COMPANY else rule["market"]
    for kind, span, name, follow in cells:
        if kind == rule["kind"] and span == rule["span"] and name == market:
            return follow
    return None


def share(follow: study.Follow | None, direction: str) -> tuple[int, int]:
    if follow is None:
        return 0, 0
    return follow.counts[direction], sum(follow.counts.values())


def main(commit: str) -> None:
    text = subprocess.run(
        ["git", "show", f"{commit}:{RULES}"], capture_output=True, text=True, check=True
    ).stdout
    print(f"rules: {RULES} at {commit}, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    rules = list(csv.DictReader(io.StringIO(text)))
    con = db.get_connection()
    loaded: dict[
        str, tuple[flows.EventFlow, list[EventInstance], dict[int, str], Sequence[str]]
    ] = {}
    for name in sorted(
        {r["flow"] for r in rules} | {r["other_flow"] for r in rules if r["other_flow"]}
    ):
        try:
            flow = flows.flow_named(name)
            loaded[name] = (flow, *follows_kinds(flow, con))
        except (FollowsUnavailable, ValueError, KeyError):
            continue
    kinds_of = {name: tuple(order) for name, (_, _, _, order) in loaded.items()}
    closes: dict[str, list[DailyClosingPrice]] = {}
    for rule in rules:
        if rule["condition"] == "move" and rule["on"] == COMPANY:
            _, events, _, _ = loaded[rule["flow"]]
            for e in events:
                ticker = (e.detail or "").split(" ")[0]
                if ticker not in closes:
                    try:
                        closes[ticker] = study.stored_closes(ticker, con=con)
                    except ValueError:
                        closes[ticker] = []
    for name in study.MVP_PRICE_SERIES:
        if name != "COIN":
            closes[name] = study.stored_closes(name, con=con)
    tested = passed = held = 0
    print(
        "id  cond   n  dir/n   answer      chance   period  plain dir/n  adds p   walk        passes holds"
    )
    for rule in rules:
        if not testable(rule, kinds_of):
            print(f"{rule['id']:>2}  untestable")
            continue
        tested += 1
        flow, events, kinds, order = loaded[rule["flow"]]
        recent = [e for e in events if e.event_ts >= FROM and kinds.get(e.event_id) == rule["kind"]]
        others = []
        if rule["condition"] == "event":
            _, o_events, o_kinds, _ = loaded[rule["other_flow"]]
            others = [e for e in o_events if o_kinds.get(e.event_id) == rule["other_kind"]]
        kept = {e.event_id: rule["kind"] for e in recent if meets(e, rule, closes, others)}
        plain = {e.event_id: rule["kind"] for e in recent}
        got = cell(flow, events, kept, order, rule, con)
        k, n = share(got, rule["direction"])
        if rule["condition"] == "none":
            base_k, base_n, adds_p = k, n, 0.0
        else:
            base = cell(flow, events, plain, order, rule, con)
            base_k, base_n = share(base, rule["direction"])
            adds_p = stats.binomial_tail(k, n, base_k / base_n) if n and base_n else 1.0
        passes = (
            got is not None
            and n >= MIN_EVENTS
            and got.answer == rule["direction"]
            and got.chance < P_ANSWER
            and not got.period
            and adds_p < P_ADDS
        )
        holds = passes and got is not None and got.verdict == study.HOLDS
        passed += passes
        held += holds
        answer = got.answer if got else study.TOO_FEW
        chance = got.chance if got else float("nan")
        walk = f"{got.right}/{got.graded} {got.verdict}" if got else "-"
        print(
            f"{rule['id']:>2}  {rule['condition']:<5}{n:>4}  {k:>3}/{n:<4} {answer:<11} {chance:>7.4f}"
            f"  {'yes' if got and got.period else '-':<6}  {base_k:>4}/{base_n:<5} {adds_p:>7.4f}"
            f"  {walk:<16} {'PASS' if passes else '-':<6} {'HOLDS' if holds else '-'}"
        )
    print(
        f"testable {tested} of {len(rules)}; pass {passed}; hold {held}; chance line {tested * P_ANSWER:.2f}"
    )


if __name__ == "__main__":
    main(sys.argv[1])
