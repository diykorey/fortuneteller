"""Step 42's texts: each S&P 500 member's 2019 10-K business section (docs/steps/exposure-scores.md).

`fetch SEC_DIR OUT` takes the members of 2020-01-02 from data/seed/sp500.csv, one per filer, finds
each one's last 10-K filed before 2020 in the saved submissions files (step 36's SEC_DIR), saves
its primary document to OUT/html/ (one request a second, skipping what is saved), and writes
OUT/texts.csv: id, ticker, cik, filed, sic, names, tickers, text (only id and text go to the
model), the text Item 1's first 12,000 characters with
the company's names and tickers replaced by "the company". It prints the counts left out and the blind test: every text filed before
2020, none of its names or tickers left in it.

Usage: uv run python scripts/tenk_business.py fetch SEC_DIR OUT
"""

import csv
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

DAY = date(2020, 1, 2)
MEMBERS = Path("data/seed/sp500.csv")
HEADERS = {"User-Agent": "research-client admin@example.com", "Accept-Encoding": "identity"}
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}"
LIMIT = 12_000
SUFFIXES = r"(,?\s+(inc|incorporated|corp|corporation|co|company|ltd|limited|plc|n\.?v|s\.?a|l\.?p|holdings?|group|the))+\.?$"
COMPANY = "the company"
COMMON = {
    "american",
    "general",
    "united",
    "first",
    "international",
    "national",
    "southern",
    "northern",
    "western",
    "eastern",
    "public",
    "consolidated",
    "global",
    "life",
    "best",
    "home",
    "state",
    "royal",
    "central",
    "pioneer",
    "advanced",
    "applied",
    "digital",
}


def members_on(day: date) -> list[str]:
    """The S&P 500's tickers on ``day`` by data/seed/sp500.csv's dated changes."""
    members: set[str] = set()
    with MEMBERS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if date.fromisoformat(row["day"]) <= day:
                (members.add if row["change"] == "in" else members.discard)(row["ticker"])
    return sorted(members)


def plain(page: str) -> str:
    """The page's text: tags dropped, entities read, white space folded."""
    page = re.sub(r"(?is)<(script|style).*?</\1>", " ", page)
    page = re.sub(r"(?s)<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page)).strip()


def business(text: str) -> str:
    """Item 1's text: the longest stretch from an *Item 1* heading (or *Items 1 and 2*) to the next
    *Item 1A*, *1B*, *2* or *3*, so the table of contents' short entry is passed over."""
    heading = r"(?i)\bitems?\s*1(\s*\.?\s*(and|&)\s*2)?\s*[.:\-—–]?\s+(?!\d)"
    best = ""
    for start in (m.end() for m in re.finditer(heading, text)):
        end = re.search(r"(?i)\bitem\s*(1a|1b|2|3)\s*[.:\-—–]?\s", text[start:])
        part = text[start : start + end.start()] if end else ""
        if len(part) > len(best):
            best = part
    return best.strip()


def _names(name: str) -> list[str]:
    """The company's name, its name without a corporate suffix, and the first word of that unless
    a common word, longest first."""
    short = re.sub(SUFFIXES, "", name.strip(), flags=re.I).strip(" ,.")
    first = short.split()[0].strip(",.&") if short else ""
    names = {name.strip(), short}
    if len(first) >= 4 and first.lower() not in COMMON:
        names.add(first)
    return [each for each in sorted(names, key=len, reverse=True) if len(each) >= 3]


def blind(text: str, name: str, tickers: list[str]) -> str:
    """``text`` with the company's name, its name without a corporate suffix, and its tickers
    replaced by "the company"."""
    for each in _names(name):
        text = re.sub(rf"(?<!\w){re.escape(each)}(?!\w)", COMPANY, text, flags=re.I)
    for ticker in tickers:
        text = re.sub(_ticker(ticker), COMPANY, text)
    return text


def _ticker(ticker: str) -> str:
    """A ticker as a word; one of one or two letters only in brackets or quotes, where it is
    plainly the ticker and not a word such as "A"."""
    if len(ticker) >= 3:
        return rf"\b{re.escape(ticker)}\b"
    return rf"(?<=[(“\"]){re.escape(ticker)}(?=[)”\"])"


def check(out: Path) -> list[str]:
    """The blind test: each text filed before 2020, with none of its company's names or tickers."""
    listing = {}
    found = []
    for row in csv.DictReader((out / "texts.csv").open(newline="")):
        listing.setdefault(row["cik"], []).append(row)
        if row["filed"] >= "2020-01-01":
            found.append(f"{row['id']} filed {row['filed']}")
        for name in row.get("names", "").split("|"):
            if name and re.search(rf"(?<!\w){re.escape(name)}(?!\w)", row["text"], flags=re.I):
                found.append(f"{row['id']} names {name}")
        for ticker in row.get("tickers", "").split("|"):
            if ticker and re.search(_ticker(ticker), row["text"]):
                found.append(f"{row['id']} ticker {ticker}")
    return found


def last_10k(index: dict, sec: Path) -> tuple[str, str, str] | None:
    """The last 10-K filed before 2020: its accession, primary document and filing day."""
    parts = [index["filings"]["recent"]]
    parts += [json.loads((sec / f["name"]).read_text()) for f in index["filings"]["files"]]
    found = [
        (part["filingDate"][i], part["accessionNumber"][i], part["primaryDocument"][i])
        for part in parts
        for i, form in enumerate(part["form"])
        if form == "10-K" and part["filingDate"][i] < "2020-01-01"
    ]
    if not found:
        return None
    filed, accession, document = max(found)
    return accession, document, filed


def fetch(sec: Path, out: Path) -> None:
    listing = json.loads((sec / "company_tickers.json").read_text())
    ciks = {row["ticker"]: int(row["cik_str"]) for row in listing.values()}
    (out / "html").mkdir(parents=True, exist_ok=True)
    rows, seen, left = [], set(), {"no filer": 0, "second class": 0, "no 10-K": 0, "no Item 1": 0}
    for ticker in members_on(DAY):
        cik = ciks.get(ticker)
        path = sec / f"CIK{cik:010d}.json" if cik else None
        if path is None or not path.exists():
            left["no filer"] += 1
            continue
        if cik in seen:
            left["second class"] += 1
            continue
        seen.add(cik)
        index = json.loads(path.read_text())
        filing = last_10k(index, sec)
        if filing is None:
            left["no 10-K"] += 1
            continue
        accession, document, filed = filing
        saved = out / "html" / f"{cik}-{accession}.html"
        if not saved.exists():
            url = ARCHIVE.format(cik=cik, accession=accession.replace("-", ""), document=document)
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=60) as response:
                saved.write_bytes(response.read())
            time.sleep(1)
        text = business(plain(saved.read_text(errors="replace")))
        if len(text) < 500:
            left["no Item 1"] += 1
            continue
        tickers = [t for t, c in ciks.items() if c == cik]
        rows.append(
            {
                "id": f"M{len(rows) + 1:03d}",
                "ticker": ticker,
                "cik": cik,
                "filed": filed,
                "sic": index.get("sic", ""),
                "names": "|".join(_names(index["name"])),
                "tickers": "|".join(tickers),
                "text": blind(text, index["name"], tickers)[:LIMIT],
            }
        )
    with (out / "texts.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} texts; left out: " + ", ".join(f"{k} {v}" for k, v in left.items()))
    found = check(out)
    print(f"blind test: {len(found)} found" + "".join(f"\n  {each}" for each in found[:20]))


if __name__ == "__main__":
    command, sec_dir, out_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    fetch(sec_dir, out_dir)
