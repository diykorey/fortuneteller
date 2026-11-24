"""Step 34's source: Yahoo's earningsHistory beside step 31's Nasdaq kinds
(docs/steps/earnings-same-day.md).

`fetch DIR [TICKER...]` asks Yahoo once for each of today's Dow members, or the tickers given, and
saves each reply as DIR/ASKED/TICKER.json, ASKED the minute asked (UTC); step 2 runs it every 30
minutes on a report's evening from the crontab. `agree DIR NASDAQ_DIR` matches each saved
quarter to step 31's report of the same ticker and fiscal quarter and prints both kinds, the
agreement, and the scale check, Nasdaq's figures read from data/cache/figures/earnings.csv,
which `nasdaq_earnings.py seed` writes.

Usage: uv run python -I scripts/yahoo_earnings.py fetch DIR [TICKER...]
       uv run python -I scripts/yahoo_earnings.py agree DIR NASDAQ_DIR
"""

import csv
import http.cookiejar
import json
import sys
import time
import urllib.request
from datetime import UTC, date, datetime
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
SUMMARY = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{t}?modules=earningsHistory&crumb={c}"
BAR = 2.0
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def quarter_key(end: str) -> str:
    """Yahoo's quarter end (2026-10-31) as Nasdaq's fiscalQuarterEnding (Oct/2026)."""
    day = date.fromisoformat(end)
    return f"{MONTHS[day.month - 1]}/{day.year}"


def kind(actual: float | None, estimate: float | None) -> str | None:
    """Nasdaq's way: (EPS - estimate) / |estimate| in percent, at ±2%; none without both."""
    if actual is None or estimate is None or estimate == 0:
        return None
    surprise = (actual - estimate) / abs(estimate) * 100
    if surprise >= BAR:
        return "above"
    if surprise <= -BAR:
        return "below"
    return "as expected"


def members_today() -> list[str]:
    members: set[str] = set()
    with Path("data/seed/dow.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if date.fromisoformat(row["day"]) <= date.today():
                (members.add if row["change"] == "in" else members.discard)(row["ticker"])
    return sorted(members)


def fetch(folder: Path, tickers: list[str]) -> None:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    try:
        opener.open(urllib.request.Request("https://fc.yahoo.com", headers=UA), timeout=30)
    except OSError:
        pass  # fc.yahoo.com answers 404, but sets the cookie
    request = urllib.request.Request(
        "https://query1.finance.yahoo.com/v1/test/getcrumb", headers=UA
    )
    crumb = opener.open(request, timeout=30).read().decode()
    asked = folder / datetime.now(UTC).strftime("%Y-%m-%dT%H%M")
    asked.mkdir(parents=True, exist_ok=True)
    for ticker in tickers or members_today():
        url = SUMMARY.format(t=ticker, c=crumb)
        reply = opener.open(urllib.request.Request(url, headers=UA), timeout=30).read()
        (asked / f"{ticker}.json").write_bytes(reply)
        time.sleep(1)
    print(f"{len(list(asked.glob('*.json')))} replies in {asked}")


def quarters(reply: Path) -> list[dict]:
    result = json.loads(reply.read_text())["quoteSummary"]["result"][0]
    return result["earningsHistory"]["history"]


def raw(entry: dict, name: str) -> float | None:
    value = entry.get(name) or {}
    return value.get("raw")


def nasdaq_quarters(folder: Path) -> dict[tuple[str, str], date]:
    """Each (ticker, fiscal quarter) on Nasdaq's saved pages, with its page's day."""
    found: dict[tuple[str, str], date] = {}
    for page in sorted(folder.glob("*.json")):
        rows = (json.loads(page.read_text()).get("data") or {}).get("rows") or []
        for row in rows:
            if row.get("fiscalQuarterEnding"):
                found[(row["symbol"], row["fiscalQuarterEnding"])] = date.fromisoformat(page.stem)
    return found


def agree(folder: Path, nasdaq: Path) -> None:
    newest = sorted(p for p in folder.iterdir() if p.is_dir() and len(list(p.glob("*.json"))) > 1)[
        -1
    ]
    pages = nasdaq_quarters(nasdaq)
    with Path("data/cache/figures/earnings.csv").open(newline="") as handle:
        seed = list(csv.DictReader(handle))
    matched, same, scale_off, not_yet, unmatched = [], 0, [], 0, []
    for reply in sorted(newest.glob("*.json")):
        ticker = reply.stem
        for entry in quarters(reply):
            key = quarter_key(entry["quarter"]["fmt"])
            actual, estimate = raw(entry, "epsActual"), raw(entry, "epsEstimate")
            yahoo = kind(actual, estimate)
            if yahoo is None:
                not_yet += 1
                continue
            day = pages.get((ticker, key))
            rows = [
                r
                for r in seed
                if day is not None
                and r["ticker"] == ticker
                and abs((date.fromisoformat(r["day"]) - day).days) <= 1
            ]
            if not rows:
                unmatched.append(f"{ticker} {key}")
                continue
            row = rows[0]
            matched.append(
                (
                    ticker,
                    key,
                    row["day"],
                    row["eps"],
                    row["forecast"],
                    row["kind"],
                    actual,
                    estimate,
                    yahoo,
                )
            )
            same += row["kind"] == yahoo
            assert actual is not None and estimate is not None
            ours = (actual - estimate) / abs(estimate) * 100
            theirs = raw(entry, "surprisePercent")
            if theirs is None or abs(ours - 100 * theirs) > 0.1:
                scale_off.append(f"{ticker} {key} {ours:.2f} vs {theirs}")
    print(f"asked {newest.name}")
    print(
        "ticker quarter day nasdaq_eps nasdaq_forecast nasdaq_kind yahoo_eps yahoo_estimate yahoo_kind"
    )
    for m in matched:
        print(" ".join(str(x) for x in m))
    n = len(matched)
    print(f"matched {n}; same kind {same} ({100 * same / n:.1f}%)" if n else "matched 0")
    print(f"not yet {not_yet}; unmatched {len(unmatched)}: {', '.join(unmatched)}")
    print(f"scale off by more than 0.1 point: {len(scale_off)} {'; '.join(scale_off)}")


if __name__ == "__main__":
    command, folder = sys.argv[1], Path(sys.argv[2])
    if command == "fetch":
        fetch(folder, sys.argv[3:])
    elif command == "agree":
        agree(folder, Path(sys.argv[3]))
