"""Step 35's additions: Wikipedia's changes to the S&P 500 at a fixed revision
(docs/steps/sp500-additions.md).

`fetch DIR` saves the revision's wikitext as DIR/REVISION.txt. `seed DIR` writes
data/seed/sp500_additions.csv from it: each company added, at 17:15 New York on the day S&P
announced it (from the row's reference), in UTC as the earnings' seed, and prints the rows left out and why.

`names DIR` prints each kept ticker's name on Yahoo beside the row's, saving each reply as
DIR/names/TICKER.json, for a ticker that now names another company to be read by hand.

Usage: uv run python -I scripts/sp500_additions.py fetch DIR
       uv run python -I scripts/sp500_additions.py seed DIR
       uv run python -I scripts/sp500_additions.py names DIR
"""

import csv
import json
import re
import sys
import time as clock
import urllib.request
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

REVISION = 1385951946
URL = "https://en.wikipedia.org/w/index.php?oldid={rev}&action=raw"
HEADERS = {"User-Agent": "fortuneteller-research/0.1"}
YAHOO = {"User-Agent": "Mozilla/5.0"}
SEED = Path("data/seed/sp500_additions.csv")
NEW_YORK = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
ANNOUNCED = time(17, 15)
MAX_LEAD_DAYS = 40
# A reference that is S&P's own release: its publisher, website or address.
S_AND_P = r"S&P Global|S&P Dow Jones|spglobal\.com|spice-indices|PR Newswire|prnewswire"
# Where S&P first said a company would join without a day and named the day in a later release,
# the first (written by hand, docs/steps/sp500-additions.md).
FIRST_SAID = {("TSLA", date(2020, 12, 21)): date(2020, 11, 16)}
# Tickers that name another company on Yahoo now, read by hand from `names` (2026-11-20).
ANOTHER_NOW = {"CSRA", "INFO", "NWSA"}
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=5d&interval=1d"


def fetch(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(URL.format(rev=REVISION), headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as reply:
        (folder / f"{REVISION}.txt").write_bytes(reply.read())
    print(f"saved revision {REVISION}")


def rows(text: str) -> list[list[str]]:
    """The changes table's rows, each its cells: effective day, added ticker and name, removed
    ticker and name, reason, references."""
    table = text[text.index('id="changes"') : text.index("==See also==")]
    found = []
    for row in table.split("\n|-")[1:]:
        cells = [c.strip() for c in re.split(r"\n\|\|?|\|\|", "\n" + row.strip("\n"))][1:]
        if len(cells) >= 6 and not cells[0].startswith("!"):
            found.append(cells)
    return found


def effective(cell: str) -> date | None:
    try:
        return datetime.strptime(re.sub(r"\s+", " ", cell), "%B %d, %Y").date()
    except ValueError:
        return None


def announced(refs: str, day: date) -> date | None:
    """S&P's release day from the row's references, the first of S&P's own: the date in its
    address, else its ``date=``; none unless 1 to MAX_LEAD_DAYS days before ``day``, since S&P
    announces at least a session ahead. A news article's date is not used."""
    for ref in refs.split("<ref")[1:]:
        found = None
        if m := re.search(r"press\.spglobal\.com/(\d{4})-(\d{2})-(\d{2})", ref):
            found = date(int(m[1]), int(m[2]), int(m[3]))
        elif m := re.search(r"/announcements/(\d{4})(\d{2})(\d{2})-", ref):
            found = date(int(m[1]), int(m[2]), int(m[3]))
        elif re.search(S_AND_P, ref) and (
            m := re.search(r"\|\s*date\s*=\s*([A-Z][a-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})", ref)
        ):
            value = m[1]
            if "-" in value:
                found = date.fromisoformat(value)
            else:
                found = datetime.strptime(value, "%B %d, %Y").date()
        if found is not None and 1 <= (day - found).days <= MAX_LEAD_DAYS:
            return found
    return None


def seed(folder: Path) -> None:
    text = (folder / f"{REVISION}.txt").read_text()
    kept, left = [], Counter()
    names: dict[str, str] = {}
    for cells in rows(text):
        day = effective(cells[0])
        ticker = re.sub(r"[^A-Z.\-]", "", cells[1])
        if day is None:
            left["no effective day"] += 1
            continue
        if not ticker:
            continue
        on = FIRST_SAID.get((ticker, day)) or announced(" ".join(cells[5:]), day)
        if on is None:
            left["no S&P release dated 1 to 40 days before"] += 1
            continue
        if ticker.replace(".", "-") in ANOTHER_NOW:
            left["another company now"] += 1
            continue
        at = datetime.combine(on, ANNOUNCED, tzinfo=NEW_YORK).astimezone(UTC)
        ticker = ticker.replace(".", "-")
        kept.append((at.date().isoformat(), at.strftime("%H:%M"), ticker, "added", day.isoformat()))
        names[ticker] = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", cells[2])
    kept = sorted(set(kept))
    with SEED.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "time", "ticker", "kind", "effective"])
        writer.writerows(kept)
    print(f"wrote {len(kept)} additions to {SEED}")
    print("left out: " + ", ".join(f"{why} {n}" for why, n in sorted(left.items())))
    (folder / "names.json").write_text(json.dumps(names, indent=0, sort_keys=True))


def names(folder: Path) -> None:
    """Each kept ticker's Yahoo name beside the row's; none where Yahoo has no closes."""
    rows_names = json.loads((folder / "names.json").read_text())
    saved = folder / "names"
    saved.mkdir(exist_ok=True)
    for ticker, name in sorted(rows_names.items()):
        path = saved / f"{ticker}.json"
        if not path.exists():
            request = urllib.request.Request(CHART.format(t=ticker), headers=YAHOO)
            try:
                with urllib.request.urlopen(request, timeout=30) as reply:
                    path.write_bytes(reply.read())
            except OSError as exc:
                path.write_text(json.dumps({"error": str(exc)}))
            clock.sleep(0.5)
        reply_json = json.loads(path.read_text())
        meta = ((reply_json.get("chart") or {}).get("result") or [{}])[0].get("meta", {})
        print(f"{ticker:6} | {name} | {meta.get('longName') or meta.get('shortName') or 'none'}")


if __name__ == "__main__":
    command, folder = sys.argv[1], Path(sys.argv[2])
    if command == "fetch":
        fetch(folder)
    elif command == "seed":
        seed(folder)
    elif command == "names":
        names(folder)
