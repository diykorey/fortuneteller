"""Step 37's seed: S&P 500 members' forward splits from 2011, each dated by the first 8-K naming its
ratio (docs/steps/stock-splits.md).

`fetch DIR SEC_DIR` saves under DIR Yahoo's splits for every ticker of data/seed/sp500.csv, then
for each forward split from 2011 the SEC's full-text search for the company's 8-Ks with "stock
split" in the 120 days before the split day, and each hit's document, under ten requests a second.
SEC_DIR is step 36's: its ticker list and filing indexes give the filer number, and each 8-K's
acceptance minute and items. `seed DIR SEC_DIR` writes data/seed/stock_splits.csv and prints the
counts and the 8-Ks passed over.

Usage: uv run python -I scripts/stock_splits.py fetch DIR SEC_DIR
       uv run python -I scripts/stock_splits.py seed DIR SEC_DIR
"""

import csv
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, date, datetime, time, timedelta
from math import gcd
from zoneinfo import ZoneInfo
from pathlib import Path
from time import sleep

FIRST = date(2011, 1, 3)
LEAD_DAYS = 365
NEW_YORK = ZoneInfo("America/New_York")
MONTHS = {
    m[:3].lower(): i
    for i, m in enumerate(
        "January February March April May June July August September October November December".split(),
        1,
    )
}
DATELINE = re.compile(
    r"\b(" + "|".join(m.capitalize() for m in MONTHS) + r")[a-z]*\.?\s+(\d{1,2}),\s+(\d{4})"
)
YAHOO = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    "?period1=1262304000&period2=1798761600&interval=1mo&events=split"
)
SEARCH = (
    "https://efts.sec.gov/LATEST/search-index?q=%22stock%20split%22&forms=8-K"
    "&ciks={cik:010d}&dateRange=custom&startdt={start}&enddt={end}"
)
DOCUMENT = "https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{name}"
SEC_HEADERS = {"User-Agent": "research-client admin@example.com", "Accept-Encoding": "identity"}
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "fifteen": 15, "twenty": 20, "twenty-five": 25, "fifty": 50,
}  # fmt: skip
NUMBER = r"(\d+|" + "|".join(sorted(WORDS, key=len, reverse=True)) + ")"
RATIO = re.compile(NUMBER + r"[\s-]*(?:-|\s)for(?:-|\s)[\s-]*" + NUMBER, re.IGNORECASE)


# Splits the 8-Ks date late, read by hand from the first public news of the split (step 37, step
# 1, amended 2026-11-20 by the owner): (ticker, the split day's year) to the New York day, minute
# and kind. A time not given is 20:00, as step 20's, unless a filing that day bounds it earlier.
BY_HAND = {
    ("WEC", 2011): ("2011-01-20", "20:00", "alone"),
    ("BALL", 2011): ("2011-01-26", "20:00", "alone"),
    ("FMC", 2012): ("2012-04-24", "16:15", "alone"),
    ("KO", 2012): ("2012-04-25", "09:08", "alone"),
    ("CME", 2012): ("2012-05-24", "18:27", "alone"),
    ("CRM", 2013): ("2013-01-25", "16:21", "alone"),
    ("VFC", 2013): ("2013-10-21", "07:00", "with a report"),
    ("FISV", 2013): ("2013-11-21", "09:42", "alone"),
    ("CTSH", 2014): ("2014-02-05", "06:16", "with a report"),
    ("NFLX", 2015): ("2015-04-10", "16:04", "alone"),
    ("CF", 2015): ("2015-05-15", "20:00", "alone"),
    ("MNST", 2016): ("2016-10-14", "08:16", "alone"),
    ("BALL", 2017): ("2017-04-26", "16:05", "alone"),
    ("FISV", 2018): ("2018-02-22", "20:00", "alone"),
    ("EW", 2020): ("2020-03-09", "16:06", "alone"),
    ("MCHP", 2021): ("2021-06-16", "17:52", "alone"),
    ("RJF", 2021): ("2021-08-25", "15:12", "alone"),
    ("DXCM", 2022): ("2022-03-25", "09:00", "alone"),
    ("TSLA", 2022): ("2022-03-28", "06:06", "alone"),
    ("TECH", 2022): ("2022-09-01", "07:00", "alone"),
    ("COO", 2024): ("2023-12-07", "16:20", "with a report"),
    ("DECK", 2024): ("2024-07-12", "09:07", "alone"),
    ("ORLY", 2025): ("2025-03-13", "16:32", "alone"),
    ("CVNA", 2026): ("2026-03-13", "09:01", "alone"),
}


def _get(url: str, path: Path, headers: dict[str, str], pause: float) -> bytes:
    """``url``'s body, saved at ``path``; a server error is asked twice more, 5 seconds apart."""
    for attempt in range(3):
        if path.exists():
            break
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as reply:
                path.write_bytes(reply.read())
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == 2:
                raise
            sleep(5)
        sleep(pause)
    return path.read_bytes()


def _ciks(sec: Path) -> dict[str, int]:
    sys.path.insert(0, str(Path(__file__).parent))
    from sec_8k_times import UNLISTED

    listing = json.loads((sec / "company_tickers.json").read_text())
    return UNLISTED | {row["ticker"]: int(row["cik_str"]) for row in listing.values()}


def _tickers() -> list[str]:
    with Path("data/seed/sp500.csv").open(newline="") as handle:
        return sorted({row["ticker"] for row in csv.DictReader(handle)})


def splits(folder: Path, ticker: str) -> list[tuple[date, int, int]]:
    """Yahoo's forward splits of ``ticker`` from FIRST: the split day and the ratio."""
    path = folder / "yahoo" / f"{ticker}.json"
    if not path.exists():
        return []
    result = (json.loads(path.read_text()).get("chart") or {}).get("result") or []
    events = (result[0].get("events") or {}).get("splits") or {} if result else {}
    found = []
    for event in events.values():
        day = datetime.fromtimestamp(event["date"], UTC).date()
        num, den = int(event["numerator"]), int(event["denominator"])
        if day >= FIRST and num > den and is_split(num, den):
            found.append((day, num, den))
    return sorted(found)


def is_split(num: int, den: int) -> bool:
    """A split's ratio, both terms 20 or under once reduced; Yahoo writes a spin-off's price
    adjustment as a split too (Agilent's Keysight in 2014, 1398:1000)."""
    g = gcd(num, den)
    return num // g <= 20 and den // g <= 20


def _search_path(folder: Path, cik: int, day: date) -> Path:
    return folder / "search" / f"{cik}-{day.isoformat()}-{LEAD_DAYS}.json"


def fetch(folder: Path, sec: Path) -> None:
    for sub in ("yahoo", "search", "docs"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
    ciks, missing = _ciks(sec), []
    for ticker in _tickers():
        try:
            _get(
                YAHOO.format(ticker=ticker), folder / "yahoo" / f"{ticker}.json", YAHOO_HEADERS, 0.5
            )
        except urllib.error.HTTPError as error:
            missing.append(f"{ticker} {error.code}")
            continue
        for day, _, _ in splits(folder, ticker):
            if ticker not in ciks:
                continue
            cik = ciks[ticker]
            start = (day - timedelta(days=LEAD_DAYS)).isoformat()
            url = SEARCH.format(cik=cik, start=start, end=(day - timedelta(days=1)).isoformat())
            try:
                hits = json.loads(_get(url, _search_path(folder, cik, day), SEC_HEADERS, 0.2))
            except urllib.error.HTTPError as error:
                print(f"{ticker} {day}: search failed, HTTP {error.code}")
                continue
            for hit in hits["hits"]["hits"]:
                accession, name = hit["_id"].split(":")
                document = DOCUMENT.format(cik=cik, folder=accession.replace("-", ""), name=name)
                try:
                    _get(document, folder / "docs" / f"{accession}-{name}", SEC_HEADERS, 0.2)
                except urllib.error.HTTPError as error:
                    print(f"{ticker} {day} {accession} {name}: HTTP {error.code}")
    print(f"{len(_tickers())} tickers; Yahoo had nothing for {len(missing)}: " + " ".join(missing))


def _filings(sec: Path, cik: int) -> dict[str, tuple[datetime, list[str]]]:
    """Each 8-K's acceptance moment (UTC) and items, by accession number."""
    found: dict[str, tuple[datetime, list[str]]] = {}
    index_path = sec / f"CIK{cik:010d}.json"
    if not index_path.exists():
        return found
    index = json.loads(index_path.read_text())
    parts = [index["filings"]["recent"]]
    parts += [json.loads((sec / f["name"]).read_text()) for f in index["filings"]["files"]]
    for part in parts:
        for i, form in enumerate(part["form"]):
            if form == "8-K":
                stamp = part["acceptanceDateTime"][i].replace("Z", "+00:00")
                found[part["accessionNumber"][i]] = (
                    datetime.fromisoformat(stamp).astimezone(UTC),
                    part["items"][i].split(","),
                )
    return found


def names_ratio(text: str, num: int, den: int) -> str:
    """``yes`` when the text names ``num``-for-``den``, else ``another ratio`` or ``no ratio``."""
    plain = re.sub(r"<[^>]+>|&nbsp;|&#160;", " ", text)
    seen = set()
    for m in RATIO.finditer(plain):
        a, b = (int(x) if x.isdigit() else WORDS[x.lower()] for x in m.groups())
        seen.add((a, b))
    if (num, den) in seen:
        return "yes"
    return "another ratio" if seen else "no ratio"


def dateline(name: str, text: str) -> date | None:
    """A press release's own date: the first date in an exhibit 99's opening, none in the 8-K's
    own document, whose first date is the event's, often the board's day before the news."""
    if "99" not in name:
        return None
    plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|&nbsp;|&#160;", " ", text))[:3000]
    if m := DATELINE.search(plain):
        try:
            return date(int(m[3]), MONTHS[m[1][:3].lower()], int(m[2]))
        except ValueError:
            return None
    return None


def announced(filed: datetime, name: str, text: str) -> tuple[datetime, bool]:
    """The announcement's moment (UTC): the filing's, or, when the press release is dated before
    the filing's New York day, that date at 20:00 New York (a time unknown, as step 20's)."""
    day = dateline(name, text)
    if day is not None and day < filed.astimezone(NEW_YORK).date():
        return datetime.combine(day, time(20), NEW_YORK).astimezone(UTC), True
    return filed, False


def members_on(day: date, changes: list[dict[str, str]]) -> set[str]:
    held: set[str] = set()
    for row in changes:
        if date.fromisoformat(row["day"]) <= day:
            (held.add if row["change"] == "in" else held.discard)(row["ticker"])
    return held


def seed(folder: Path, sec: Path) -> None:
    with Path("data/seed/sp500.csv").open(newline="") as handle:
        changes = list(csv.DictReader(handle))
    ciks, out, left, passed = _ciks(sec), [], Counter(), []
    asked, seen, by_dateline, by_hand = 0, set(), 0, 0
    for ticker in _tickers():
        for day, num, den in splits(folder, ticker):
            asked += 1
            if ticker not in ciks:
                left["no filer number"] += 1
                continue
            cik = ciks[ticker]
            path = _search_path(folder, cik, day)
            if not path.exists():
                left["not searched"] += 1
                continue
            filings = _filings(sec, cik)
            found = []
            for hit in json.loads(path.read_text())["hits"]["hits"]:
                accession, name = hit["_id"].split(":")
                if accession not in filings:
                    continue
                doc = folder / "docs" / f"{accession}-{name}"
                text = doc.read_text(errors="replace") if doc.exists() else ""
                why = names_ratio(text, num, den) if doc.exists() else "not fetched"
                if why == "yes":
                    filed, items = filings[accession]
                    at, dated = announced(filed, name, text)
                    found.append((at, dated, items, accession))
                else:
                    passed.append((why, f"{ticker} {day} {num}-for-{den} {accession} {name}"))
            if not found:
                left["no 8-K"] += 1
                continue
            at, dated, items, accession = min(found)
            hand = BY_HAND.get((ticker, day.year))
            if hand is not None:
                when = datetime.fromisoformat(f"{hand[0]}T{hand[1]}").replace(tzinfo=NEW_YORK)
                at, dated, items = (
                    when.astimezone(UTC),
                    False,
                    ["2.02"] if hand[2] == "with a report" else [],
                )
                by_hand += 1
            if (cik, day) in seen:
                left["the same filer's split under another ticker"] += 1
                continue
            seen.add((cik, day))
            by_dateline += dated
            if ticker not in members_on(at.date(), changes):
                left["not a member that day"] += 1
                continue
            kind = "with a report" if "2.02" in items else "alone"
            ratio = f"{num}-for-{den}"
            out.append(
                (at.date().isoformat(), at.strftime("%H:%M"), ticker, ratio, day, kind, accession)
            )
    out.sort()
    with Path("data/seed/stock_splits.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "time", "ticker", "ratio", "split_day", "kind", "accession"])
        writer.writerows(out)
    kinds = Counter(row[5] for row in out)
    print(
        f"{asked} forward splits asked; wrote {len(out)}: "
        + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items()))
    )
    print(
        f"dated by the press release's own date, the time unknown: {by_dateline}; by hand: {by_hand}"
    )
    print("left out: " + ", ".join(f"{why} {n}" for why, n in sorted(left.items())))
    reasons = Counter(why for why, _ in passed)
    print("8-K documents passed over: " + ", ".join(f"{k} {n}" for k, n in sorted(reasons.items())))
    for why, line in passed[:10]:
        print(f"  {why}: {line}")


if __name__ == "__main__":
    command, folder, sec = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    if command == "fetch":
        fetch(folder, sec)
    elif command == "seed":
        seed(folder, sec)
