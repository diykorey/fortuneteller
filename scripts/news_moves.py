"""Step 40's matrix: S&P 500 members' big moves against the 8-K items filed with them
(docs/steps/news-moves.md).

`matrix SEC_DIR` prints, for each item, its member-days, big moves up and down, big share, lift
and up share, on all its days and on its days with no 2.02, and the counts left out. `sample
SEC_DIR` prints the sample's big moves with no 8-K. Both read the store at FT_DB_PATH.

Usage: uv run python scripts/news_moves.py matrix|sample SEC_DIR
"""

import csv
import json
import sys
from bisect import bisect_left, bisect_right
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from statistics import pstdev
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from nasdaq_earnings import symbol  # noqa: E402
from sec_8k_times import MORE_FILERS, UNLISTED  # noqa: E402

from fortuneteller import db, stats  # noqa: E402
from fortuneteller.study import EXCESS_OVER, excess_spans, stored_closes  # noqa: E402

FIRST = date(2011, 1, 3)
NEW_YORK = ZoneInfo("America/New_York")
CLOSE = time(16, 0)
BASE, DEVIATIONS, FLOOR, LIFT, P = 504, 3.0, 30, 3.0, 0.01
SAMPLE = 40
MEMBERS = Path("data/seed/sp500.csv")


def window_day(stamp: datetime, days: list[date]) -> date | None:
    """The trading day whose window holds an 8-K accepted at ``stamp``: after 16:00:00 New York
    on the close before, up to 16:00:00 on the day."""
    local = stamp.astimezone(NEW_YORK)
    find = bisect_right if local.time() > CLOSE else bisect_left
    i = find(days, local.date())
    return days[i] if i < len(days) else None


def big(move: float, before: list[float]) -> bool:
    """A move at least DEVIATIONS standard deviations of the BASE moves before it."""
    return abs(move) >= DEVIATIONS * pstdev(before)


def items_by_day(sec: Path, ciks: list[int], days: list[date]) -> dict[date, set[str]]:
    """The items of the filer's 8-Ks (not 8-K/A), by the trading day whose window holds each."""
    found: dict[date, set[str]] = {}
    for cik in ciks:
        path = sec / f"CIK{cik:010d}.json"
        if not path.exists():
            continue
        index = json.loads(path.read_text())
        parts = [index["filings"]["recent"]]
        parts += [json.loads((sec / f["name"]).read_text()) for f in index["filings"]["files"]]
        for part in parts:
            for i, form in enumerate(part["form"]):
                if form != "8-K":
                    continue
                stamp = datetime.fromisoformat(part["acceptanceDateTime"][i].replace("Z", "+00:00"))
                day = window_day(stamp, days)
                if day is not None:
                    found.setdefault(day, set()).update(part["items"][i].split(","))
    return found


def membership() -> dict[str, list[tuple[date, date]]]:
    """Each ticker's spans in the S&P 500 by data/seed/sp500.csv, the end exclusive."""
    spans: dict[str, list[tuple[date, date]]] = {}
    joined: dict[str, date] = {}
    with MEMBERS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            day = date.fromisoformat(row["day"])
            if row["change"] == "in":
                joined[row["ticker"]] = day
            elif row["ticker"] in joined:
                spans.setdefault(row["ticker"], []).append((joined.pop(row["ticker"]), day))
    for ticker, day in joined.items():
        spans.setdefault(ticker, []).append((day, date.max))
    return spans


def member_days(sec: Path) -> tuple[list[tuple[date, str, float, bool, set[str]]], Counter[str]]:
    """Every member-day with a base: (day, ticker, excess move, big, items), and the counts left
    out. One member-day per filer: of two share classes, the first ticker by name."""
    listing = json.loads((sec / "company_tickers.json").read_text())
    ciks = UNLISTED | {row["ticker"]: int(row["cik_str"]) for row in listing.values()}
    con = db.get_connection()
    index = stored_closes(EXCESS_OVER, con=con)
    days = [close.day for close in index]
    rows, out, seen = [], Counter[str](), set()
    for ticker, spans in sorted(membership().items()):
        cik = ciks.get(ticker)
        if cik is None or not (sec / f"CIK{cik:010d}.json").exists():
            out["no filer"] += 1
            continue
        try:
            closes = stored_closes(symbol(ticker), con=con)
        except ValueError:
            out["no closes"] += 1
            continue
        items = items_by_day(sec, [cik, *MORE_FILERS.get(ticker, [])], days)
        moves = sorted((day, span.move) for day, span in excess_spans(closes, index, 1).items())
        for k in range(BASE, len(moves)):
            day, move = moves[k]
            if day < FIRST or not any(a <= day < b for a, b in spans):
                continue
            if (cik, day) in seen:
                out["second class"] += 1
                continue
            seen.add((cik, day))
            before = [m for _, m in moves[k - BASE : k]]
            rows.append((day, ticker, move, big(move, before), items.get(day, set())))
    return rows, out


def two_sided(k: int, n: int, rate: float) -> float:
    return min(
        1.0, 2 * min(stats.binomial_tail(k, n, rate), 1 - stats.binomial_tail(k + 1, n, rate))
    )


def line(
    name: str, rows: list[tuple[date, str, float, bool, set[str]]], share: float, up: float
) -> str:
    n = len(rows)
    ups = sum(1 for r in rows if r[3] and r[2] > 0)
    downs = sum(1 for r in rows if r[3] and r[2] < 0)
    moved = ups + downs
    lift = moved / n / share if n else 0.0
    p_big = stats.binomial_tail(moved, n, share)
    p_dir = two_sided(ups, moved, up) if moved else 1.0
    goes = n >= FLOOR and lift >= LIFT and p_big < P
    direction = moved >= FLOOR and p_dir < P
    return (
        f"{name:<14}{n:>9}{ups:>7}{downs:>7}{moved / n if n else 0:>9.2%}{lift:>7.2f}"
        f"{p_big:>10.2g}{ups / moved if moved else 0:>8.1%}{p_dir:>10.2g}"
        f"{'  goes' if goes else ''}{'  direction' if direction else ''}"
    )


def matrix(sec: Path) -> None:
    rows, out = member_days(sec)
    moved = [r for r in rows if r[3]]
    share = len(moved) / len(rows)
    up = sum(1 for r in moved if r[2] > 0) / len(moved)
    print(f"member-days {len(rows)}, big {len(moved)} ({share:.2%}), up share {up:.1%}")
    print("left out (tickers): " + ", ".join(f"{k} {v}" for k, v in sorted(out.items())))
    counts = Counter(item for r in rows for item in r[4])
    items = sorted(i for i, c in counts.items() if c >= FLOOR and i)
    rare = {i for i in counts if i not in items}
    print(
        f"{'row':<14}{'days':>9}{'up':>7}{'down':>7}{'big':>9}{'lift':>7}{'p':>10}{'up of big':>8}{'p dir':>10}"
    )
    for item in items:
        print(line(item, [r for r in rows if item in r[4]], share, up))
        print(
            line("  no 2.02", [r for r in rows if item in r[4] and "2.02" not in r[4]], share, up)
        )
    print(line("other", [r for r in rows if r[4] & rare], share, up))
    print(line("any 8-K", [r for r in rows if r[4]], share, up))
    print(line("no 8-K", [r for r in rows if not r[4]], share, up))
    with_202 = sum(1 for r in moved if "2.02" in r[4])
    print(f"big moves with 2.02: {with_202} of {len(moved)} ({with_202 / len(moved):.1%})")
    tested = [i for i in items if i != "9.01"]
    print(f"chance line: {len(tested)} item rows x {P} = {len(tested) * P:.2f}, each test")


def sample(sec: Path) -> None:
    rows, _ = member_days(sec)
    unfiled = sorted((r for r in rows if r[3] and not r[4]), key=lambda r: (r[0], r[1]))
    n = len(unfiled) // SAMPLE
    print(f"big moves with no 8-K: {len(unfiled)}, n = {n}")
    for k in range(1, SAMPLE + 1):
        day, ticker, move, _, _ = unfiled[k * n - 1]
        print(f"{k * n},{day},{ticker},{move:+.4f}")


if __name__ == "__main__":
    command, folder = sys.argv[1], Path(sys.argv[2])
    {"matrix": matrix, "sample": sample}[command](folder)
