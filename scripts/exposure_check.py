"""Step 42's test of the exposure scores (docs/steps/exposure-scores.md).

`exposure_check.py COMMIT TEXTS` reads docs/steps/exposure-scores.csv as committed at COMMIT,
prints its SHA-256, and for each rubric, kind and span tests, on the events from 2020-01-01 in the
store at FT_DB_PATH, whether the spread (the high scorers' mean excess move less the low
scorers') has the kind's sign: the cell's answer, its placebo and walk-forward, and the same for
the sector baseline, the members' SIC major groups read from TEXTS (step 1's texts.csv).

Usage: uv run python scripts/exposure_check.py COMMIT TEXTS
"""

import csv
import hashlib
import io
import subprocess
import sys
from bisect import bisect_left
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import NamedTuple

from fortuneteller import db, flows, stats, study
from fortuneteller.__main__ import follows_kinds

SCORES = "docs/steps/exposure-scores.csv"
FROM = datetime(2020, 1, 1)
INDEX = "SPY / ES"
MIN_EVENTS, P_ANSWER, P_ADDS = 10, 0.01, 0.05
HOLD_SHARE, HOLD_OVER, HOLD_GRADED = 0.60, 0.10, 30
SPANS = {"day": 1, "week": 5}
# Per rubric: its flows' kinds with the sign each implies, and the cuts for the high and low groups.
CELLS = {
    "oil": ({"opec": {study.OIL_UP: 1, study.OIL_DOWN: -1}}, 3, -3),
    "rates": (
        {
            "cpi": {study.ABOVE: 1, study.BELOW: -1},
            "fomc": {study.HIKE: 1, study.CUT: -1},
        },
        3,
        -3,
    ),
    "consumer": ({"retail": {study.ABOVE: 1, study.BELOW: -1}}, 3, 0),
}


class Groups(NamedTuple):
    high: list[str]
    low: list[str]


def groups(scores: Mapping[str, float], high: float, low: float) -> Groups:
    """The members scoring ``high`` or more, and those scoring ``low`` or less."""
    return Groups(
        sorted(t for t, s in scores.items() if s >= high),
        sorted(t for t, s in scores.items() if s <= low),
    )


def sector_scores(scores: Mapping[str, float], sic: Mapping[str, str]) -> dict[str, float]:
    """Each member's score replaced by the mean of the other members of its SIC major group; a
    member alone in its group is left out."""
    by_group: dict[str, list[str]] = defaultdict(list)
    for ticker in scores:
        by_group[sic.get(ticker, "")[:2]].append(ticker)
    out = {}
    for ticker in scores:
        others = [scores[t] for t in by_group[sic.get(ticker, "")[:2]] if t != ticker]
        if others and sic.get(ticker):
            out[ticker] = sum(others) / len(others)
    return out


def spread(g: Groups, moves: Mapping[str, Mapping[date, float]], day: date) -> float | None:
    """The high group's mean excess move on the span keyed ``day`` less the low group's; none
    when either group has no member with that span."""
    hi = [moves[t][day] for t in g.high if day in moves.get(t, {})]
    lo = [moves[t][day] for t in g.low if day in moves.get(t, {})]
    if not hi or not lo:
        return None
    return sum(hi) / len(hi) - sum(lo) / len(lo)


def right(value: float | None, sign: int) -> bool:
    return value is not None and value * sign > 0


def answers(k: int, n: int, base: float) -> tuple[bool, float]:
    """Whether ``k`` right of ``n`` answers by the rule, and its chance against ``base``."""
    if n < MIN_EVENTS:
        return False, float("nan")
    p = stats.binomial_tail(k, n, base)
    return p < P_ANSWER, p


def walk_forward(results: Sequence[bool], base: float) -> tuple[int, int, bool]:
    """Each event graded by the answer the events before it give; right, graded and holds."""
    graded = hits = 0
    for i, result in enumerate(results):
        if answers(sum(results[:i]), i, base)[0]:
            graded += 1
            hits += result
    held = (
        graded >= HOLD_GRADED
        and hits / graded >= HOLD_SHARE
        and hits / graded >= base + HOLD_OVER
        and stats.binomial_tail(hits, graded, base) < P_ANSWER
    )
    return hits, graded, held


class Cell(NamedTuple):
    n: int
    k: int
    base: float
    answered: bool
    p: float
    period: bool
    walk: tuple[int, int, bool]
    results: list[bool]


def measure(
    g: Groups,
    moves: Mapping[str, Mapping[date, float]],
    days: Sequence[date],
    reactions: Sequence[int],
    sign: int,
    reach: int,
) -> Cell:
    """One cell: its events' spreads at the index closes ``reactions``, the base on the 504 closes
    before 2020, the placebo shifted by ``reach`` closes either way, and the walk-forward."""
    first = bisect_left(days, FROM.date())
    before = days[max(first - study.BASE_CLOSES, 0) : first]
    on_base = [s for d in before if (s := spread(g, moves, d)) is not None]
    base = sum(s * sign > 0 for s in on_base) / len(on_base) if on_base else float("nan")
    values = [spread(g, moves, days[r]) for r in reactions]
    kept = [(r, v) for r, v in zip(reactions, values, strict=True) if v is not None]
    results = [right(v, sign) for _, v in kept]
    answered, p = answers(sum(results), len(results), base)
    period = False
    if answered:
        reacted = set(reactions)
        for shift in (-reach, reach):
            moved = [
                spread(g, moves, days[i])
                for r, _ in kept
                if 0 <= (i := r + shift) < len(days) and i not in reacted
            ]
            moved_results = [right(v, sign) for v in moved if v is not None]
            if answers(sum(moved_results), len(moved_results), base)[0]:
                period = True
    return Cell(
        len(results),
        sum(results),
        base,
        answered,
        p,
        period,
        walk_forward(results, base),
        results,
    )


def adds(own: Sequence[bool], sector: Sequence[bool]) -> tuple[int, int, float]:
    """The sign test on the events where the two disagree: own right, of those, and its chance."""
    differ = [(a, b) for a, b in zip(own, sector, strict=True) if a != b]
    k = sum(a for a, _ in differ)
    p = stats.binomial_tail(k, len(differ), 0.5) if differ else float("nan")
    return k, len(differ), p


def main(commit: str, texts: str) -> None:
    text = subprocess.run(
        ["git", "show", f"{commit}:{SCORES}"], capture_output=True, text=True, check=True
    ).stdout
    print(f"scores: {SCORES} at {commit}, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    by_rubric: dict[str, dict[str, float]] = defaultdict(dict)
    for row in csv.DictReader(io.StringIO(text)):
        by_rubric[row["rubric"]][row["ticker"]] = float(row["score"])
    csv.field_size_limit(10**7)
    with open(texts, newline="") as handle:
        sic = {row["ticker"]: row["sic"] for row in csv.DictReader(handle)}
    con = db.get_connection()
    index = study.stored_closes(INDEX, con=con)
    days = [c.day for c in index]
    members = sorted(by_rubric["oil"])
    closes = {}
    for ticker in members:
        try:
            closes[ticker] = study.stored_closes(ticker, con=con)
        except ValueError:
            continue
    print(f"members scored {len(members)}, with closes {len(closes)}")
    moves = {
        name: {
            t: {d: s.move for d, s in study.excess_spans(c, index, n).items()}
            for t, c in closes.items()
        }
        for name, n in SPANS.items()
    }
    loaded = {}
    for kinds_of, _, _ in CELLS.values():
        for flow_name in kinds_of:
            loaded[flow_name] = follows_kinds(flows.flow_named(flow_name), con)
    answered = adds_count = cells = 0
    print(
        "rubric    kind            span  hi/lo   n   right  base   p        answer  period  "
        "walk           | sector: hi/lo  n  right  answer | adds k/d  p"
    )
    for rubric, (kinds_of, high, low) in CELLS.items():
        scores = {t: s for t, s in by_rubric[rubric].items() if t in closes}
        own = groups(scores, high, low)
        sector = groups(sector_scores(scores, sic), high, low)
        for flow_name, signs in kinds_of.items():
            events, kinds, _ = loaded[flow_name]
            for kind, sign in signs.items():
                firsts = sorted(
                    study.first_reaction_day(e, study.STOCK)
                    for e in events
                    if e.event_ts >= FROM and kinds.get(e.event_id) == kind
                )
                reactions = sorted({i for d in firsts if (i := bisect_left(days, d)) < len(days)})
                for span, n in SPANS.items():
                    cells += 1
                    reach = max(study.PLACEBO_SHIFT, n)
                    a = measure(own, moves[span], days, reactions, sign, reach)
                    b = measure(sector, moves[span], days, reactions, sign, reach)
                    k, d, p_adds = (
                        adds(a.results, b.results) if a.n == b.n else (0, 0, float("nan"))
                    )
                    answered += a.answered
                    adds_count += p_adds < P_ADDS
                    walk = f"{a.walk[0]}/{a.walk[1]} {'holds' if a.walk[2] else '-'}"
                    print(
                        f"{rubric:<9} {flow_name + ' ' + kind:<15} {span:<5} "
                        f"{len(own.high):>2}/{len(own.low):<3} {a.n:>3} {a.k:>5}  {a.base:.3f}  "
                        f"{a.p:<8.4f} {'yes' if a.answered else 'no':<7} "
                        f"{'period' if a.period else '-':<7} {walk:<14} | "
                        f"{len(sector.high):>2}/{len(sector.low):<3} {b.n:>3} {b.k:>5}  "
                        f"{'yes' if b.answered else 'no':<6} | {k}/{d} {p_adds:.4f}"
                    )
    print(
        f"cells {cells}; answer {answered} (chance line {P_ANSWER * cells:.2f}); "
        f"adds {adds_count} (chance line {P_ADDS * cells:.2f})"
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
