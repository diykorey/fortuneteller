"""Step 43's test of the filing scores (docs/steps/filing-severity.md).

`severity_check.py COMMIT TEXTS` reads docs/steps/severity-scores.csv as committed at COMMIT,
prints its SHA-256, and for bad and good filings, on the day and over the week, tests whether the
member's excess move from the close before its window's day has the score's sign: the cell's
answer, its placebo and walk-forward, and the same per item code (reported only). The filings'
days, tickers and items come from TEXTS (step 1's texts.csv); closes from the store at FT_DB_PATH.

Usage: uv run python scripts/severity_check.py COMMIT TEXTS
"""

import csv
import hashlib
import io
import subprocess
import sys
from bisect import bisect_left
from collections.abc import Mapping, Sequence
from datetime import date
from typing import NamedTuple

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nasdaq_earnings import symbol  # noqa: E402

from fortuneteller import db, stats, study  # noqa: E402

SCORES = "docs/steps/severity-scores.csv"
FROM = date(2020, 1, 1)
INDEX = "SPY / ES"
MIN_FILINGS, P_ANSWER = 10, 0.01
HOLD_SHARE, HOLD_OVER, HOLD_GRADED = 0.60, 0.10, 30
SPANS = {"day": 1, "week": 5}
SHIFT = study.PLACEBO_SHIFT
BAD, GOOD = -2, 2
ITEMS = ("2.05", "3.02", "5.02", "7.01", "8.01")


class Filing(NamedTuple):
    day: date
    ticker: str
    items: str
    score: int


def side(score: int) -> int:
    """The expected sign: −1 for a bad score, +1 for a good one, 0 for neither."""
    return -1 if score <= BAD else 1 if score >= GOOD else 0


def answers(k: int, n: int, base: float) -> tuple[bool, float]:
    if n < MIN_FILINGS:
        return False, float("nan")
    p = stats.binomial_tail(k, n, base)
    return p < P_ANSWER, p


def walk_forward(results: Sequence[bool], base: float) -> tuple[int, int, bool]:
    """Each filing graded once the filings before it answer; right, graded and holds."""
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


def base_share(moves: Mapping[str, Mapping[date, float]], days: Sequence[date], sign: int) -> float:
    """The share, pooled over every member once and each of its spans keyed at one of the 504
    index closes before 2020, with the sign ``sign``."""
    first = bisect_left(days, FROM)
    before = days[max(first - study.BASE_CLOSES, 0) : first]
    values = [m[d] for m in moves.values() for d in before if d in m]
    return sum(v * sign > 0 for v in values) / len(values) if values else float("nan")


def reaction(days: Sequence[date], day: date) -> int | None:
    i = bisect_left(days, day)
    return i if i < len(days) and days[i] == day else None


class Cell(NamedTuple):
    n: int
    k: int
    base: float
    answered: bool
    p: float
    period: bool
    walk: tuple[int, int, bool]


def measure(
    filings: Sequence[Filing],
    moves: Mapping[str, Mapping[date, float]],
    days: Sequence[date],
    sign: int,
    base: float,
) -> Cell:
    """One cell over ``filings`` (all on ``sign``'s side), in day order."""
    filed = {(f.ticker, f.day) for f in filings}
    results, kept = [], []
    for f in sorted(filings):
        move = moves.get(f.ticker, {}).get(f.day)
        if move is not None:
            results.append(move * sign > 0)
            kept.append(f)
    answered, p = answers(sum(results), len(results), base)
    period = False
    if answered:
        for shift in (-SHIFT, SHIFT):
            moved = []
            for f in kept:
                r = reaction(days, f.day)
                if r is None or not 0 <= r + shift < len(days):
                    continue
                d = days[r + shift]
                if (f.ticker, d) in filed:
                    continue
                m = moves.get(f.ticker, {}).get(d)
                if m is not None:
                    moved.append(m * sign > 0)
            if answers(sum(moved), len(moved), base)[0]:
                period = True
    return Cell(len(results), sum(results), base, answered, p, period, walk_forward(results, base))


def main(commit: str, texts: str) -> None:
    text = subprocess.run(
        ["git", "show", f"{commit}:{SCORES}"], capture_output=True, text=True, check=True
    ).stdout
    print(f"scores: {SCORES} at {commit}, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    scores = {row["id"]: int(row["score"]) for row in csv.DictReader(io.StringIO(text))}
    csv.field_size_limit(10**7)
    with open(texts, newline="") as handle:
        filings = [
            Filing(date.fromisoformat(r["day"]), r["ticker"], r["items"], scores[r["id"]])
            for r in csv.DictReader(handle)
            if r["id"] in scores
        ]
    con = db.get_connection()
    index = study.stored_closes(INDEX, con=con)
    days = [c.day for c in index]
    closes = {}
    for ticker in sorted({f.ticker for f in filings}):
        try:
            closes[ticker] = study.stored_closes(symbol(ticker), con=con)
        except ValueError:
            continue
    sides = {s: sum(side(f.score) == s for f in filings) for s in (-1, 0, 1)}
    print(
        f"filings scored {len(filings)}, members with closes {len(closes)} of "
        f"{len({f.ticker for f in filings})}; bad {sides[-1]}, neither {sides[0]}, good {sides[1]}"
    )
    moves = {
        span: {
            t: {d: s.move for d, s in study.excess_spans(c, index, n).items()}
            for t, c in closes.items()
        }
        for span, n in SPANS.items()
    }
    print("cell             span  n    right  base   p        answer  period  walk (right/graded)")
    answered = cells = 0
    for name, sign in (("bad, down", -1), ("good, up", 1)):
        for span in SPANS:
            base = base_share(moves[span], days, sign)
            group = [f for f in filings if side(f.score) == sign]
            c = measure(group, moves[span], days, sign, base)
            cells += 1
            answered += c.answered
            walk = f"{c.walk[0]}/{c.walk[1]} {'holds' if c.walk[2] else '-'}"
            print(
                f"{name:<16} {span:<5} {c.n:>3}  {c.k:>4}  {c.base:.3f}  {c.p:<8.4f} "
                f"{'yes' if c.answered else 'no':<7} {'period' if c.period else '-':<7} {walk}"
            )
            for item in ITEMS:
                sub = [f for f in group if item in f.items.split(",")]
                s = measure(sub, moves[span], days, sign, base)
                print(
                    f"  item {item:<10} {span:<5} {s.n:>3}  {s.k:>4}  {s.base:.3f}  "
                    f"{s.p:<8.4f} {'yes' if s.answered else 'no':<7} (reported)"
                )
    print(f"cells {cells}; answer {answered} (chance line {P_ANSWER * cells:.2f})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
