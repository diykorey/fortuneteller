"""Step 31's reports: Nasdaq's earnings calendar, one page a weekday (docs/steps/earnings.md).

`fetch DIR [LAST]` saves each weekday's page from 2008-01-02 to LAST (2026-11-18 if not given)
as DIR/YYYY-MM-DD.json, one request a second, skipping pages already saved but those within
REFETCH_DAYS of today, which Nasdaq may still be filling (docs/steps/earnings-current.md).
`seed DIR SEC_DIR [LAST]` writes data/seed/earnings.csv
from the saved pages, data/seed/dow.csv and the filing indexes `scripts/sec_8k_times.py` saved:
each member's report with a kind and an 8-K with Item 2.02, and prints the reports left out.

With `--members FILE --out FILE --first DAY` (step 36, docs/steps/earnings-sp500.md) `seed` keeps
another index's members from DAY and writes FILE; a member with no filing index saved is *no 8-K*.

Usage: uv run python -I scripts/nasdaq_earnings.py fetch DIR [LAST]
       uv run python -I scripts/nasdaq_earnings.py seed DIR SEC_DIR [LAST] [--members FILE --out FILE --first DAY]
"""

import csv
import json
import sys
import time
import urllib.request
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

FIRST, LAST = date(2008, 1, 2), date(2026, 11, 18)
# Nasdaq fills a report's EPS a day or more after it, so a page this recent is fetched again.
REFETCH_DAYS = 21
URL = "https://api.nasdaq.com/api/calendar/earnings?date={day}"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
SEED = Path("data/seed/earnings.csv")
NEW_YORK = ZoneInfo("America/New_York")
BAR = 2.0


def weekdays(last: date = LAST, first: date = FIRST) -> list[date]:
    days, day = [], first
    while day <= last:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def refetched(day: date, today: date) -> bool:
    """Whether a saved page of ``day`` is fetched again on ``today``: within REFETCH_DAYS."""
    return (today - day).days <= REFETCH_DAYS


def fetch(folder: Path, last: date = LAST) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    failed = []
    today = date.today()
    for day in weekdays(last):
        path = folder / f"{day.isoformat()}.json"
        if path.exists() and not refetched(day, today):
            continue
        request = urllib.request.Request(URL.format(day=day.isoformat()), headers=HEADERS)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=30) as reply:
                    path.write_bytes(reply.read())
                break
            except OSError as exc:
                if attempt == 2:
                    failed.append(f"{day}: {exc}")
                time.sleep(5)
        time.sleep(1)
    print(f"{len(list(folder.glob('*.json')))} pages saved; {len(failed)} failed")
    for line in failed:
        print(line)


def kind(surprise: str) -> str | None:
    """The spec's kind: above at +2% or more, below at -2% or less, as expected between."""
    try:
        value = float(surprise)
    except ValueError:
        return None
    if value >= BAR:
        return "above"
    if value <= -BAR:
        return "below"
    return "as expected"


def members_on(day: date, changes: list[dict[str, str]]) -> set[str]:
    """The Dow's members on ``day`` by data/seed/dow.csv's dated changes."""
    members: set[str] = set()
    for row in changes:
        if date.fromisoformat(row["day"]) <= day:
            (members.add if row["change"] == "in" else members.discard)(row["ticker"])
    return members


def nearest(day: date, stamps: list[datetime]) -> datetime | None:
    """Of the 8-Ks accepted within a day of ``day`` (New York days), the nearest; ties the earliest."""
    near = [s for s in stamps if abs((s.astimezone(NEW_YORK).date() - day).days) <= 1]
    if not near:
        return None
    return min(near, key=lambda s: (abs((s.astimezone(NEW_YORK).date() - day).days), s))


def symbol(ticker: str) -> str:
    """Nasdaq's symbol as the seeds write it, Yahoo's way (BRK.B and BRK/B as BRK-B)."""
    return ticker.replace(".", "-").replace("/", "-")


def filings(sec: Path, members_file: Path = Path("data/seed/dow.csv")) -> dict[str, list[datetime]]:
    """Each member's 8-Ks with Item 2.02, by its symbol, as the SEC accepted them (UTC)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sec_8k_times import MORE_FILERS, UNLISTED

    listing = json.loads((sec / "company_tickers.json").read_text())
    ciks = UNLISTED | {row["ticker"]: int(row["cik_str"]) for row in listing.values()}
    with members_file.open(newline="") as handle:
        tickers = sorted({row["ticker"] for row in csv.DictReader(handle)})
    stamps: dict[str, list[datetime]] = {}
    for ticker in tickers:
        found: list[datetime] = []
        filers = [ciks[ticker], *MORE_FILERS.get(ticker, [])] if ticker in ciks else []
        for cik in filers:
            if not (sec / f"CIK{cik:010d}.json").exists():
                continue
            index = json.loads((sec / f"CIK{cik:010d}.json").read_text())
            parts = [index["filings"]["recent"]]
            parts += [json.loads((sec / f["name"]).read_text()) for f in index["filings"]["files"]]
            for part in parts:
                for i, form in enumerate(part["form"]):
                    if form == "8-K" and "2.02" in part["items"][i].split(","):
                        stamp = part["acceptanceDateTime"][i].replace("Z", "+00:00")
                        found.append(datetime.fromisoformat(stamp).astimezone(UTC))
        stamps[ticker] = sorted(found)
    return stamps


def seed(
    folder: Path,
    sec: Path,
    last: date = LAST,
    members_file: Path = Path("data/seed/dow.csv"),
    out: Path = SEED,
    first: date = FIRST,
) -> None:
    with members_file.open(newline="") as handle:
        changes = list(csv.DictReader(handle))
    stamps = filings(sec, members_file)
    rows, left = [], Counter()
    missing: list[str] = []
    for day in weekdays(last, first):
        path = folder / f"{day.isoformat()}.json"
        if not path.exists():
            left["day not fetched"] += 1
            continue
        page = json.loads(path.read_text())
        members = members_on(day, changes)
        for row in (page.get("data") or {}).get("rows") or []:
            ticker = symbol(row["symbol"])
            if ticker not in members:
                continue
            k = kind(row.get("surprise", ""))
            if k is None:
                left["no kind"] += 1
                continue
            at = nearest(day, stamps.get(ticker, []))
            if at is None:
                left["no 8-K"] += 1
                missing.append(f"{day} {ticker}")
                continue
            rows.append(
                (
                    at.date().isoformat(),
                    at.strftime("%H:%M"),
                    ticker,
                    row["eps"].strip("$"),
                    row["epsForecast"].strip("$"),
                    row["surprise"],
                    k,
                )
            )
    rows = sorted(set(rows))
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "time", "ticker", "eps", "forecast", "surprise", "kind"])
        writer.writerows(rows)
    kinds = Counter(r[6] for r in rows)
    print(
        f"wrote {len(rows)} reports to {out}: "
        + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items()))
    )
    print("left out: " + ", ".join(f"{why} {n}" for why, n in sorted(left.items())))
    print("no 8-K: " + ", ".join(missing))


if __name__ == "__main__":
    command, folder = sys.argv[1], Path(sys.argv[2])
    if command == "fetch":
        fetch(folder, *(date.fromisoformat(a) for a in sys.argv[3:4]))
    elif command == "seed":
        args, options = sys.argv[3:], {}
        while "--" in "".join(a[:2] for a in args):
            i = next(i for i, a in enumerate(args) if a.startswith("--"))
            options[args[i][2:]] = args[i + 1]
            del args[i : i + 2]
        seed(
            folder,
            Path(args[0]),
            *(date.fromisoformat(a) for a in args[1:2]),
            **({"members_file": Path(options["members"])} if "members" in options else {}),
            **({"out": Path(options["out"])} if "out" in options else {}),
            **({"first": date.fromisoformat(options["first"])} if "first" in options else {}),
        )
