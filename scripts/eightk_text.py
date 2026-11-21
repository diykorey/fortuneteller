"""Step 43's sample and texts: S&P 500 members' 8-Ks of 2020 to 2025 (docs/steps/filing-severity.md).

`fetch SEC_DIR OUT` lists every member-day from 2020-01-01 to 2025-12-31 whose window holds an 8-K
carrying item 2.05, 3.02, 5.02, 7.01 or 8.01 and none carrying 2.02, takes the first such filing
of each, draws the sample, saves each filing's primary document and first exhibit 99 to
OUT/html/ (one request a second, skipping what is saved), and writes OUT/texts.csv: id, day,
ticker, cik, accession, items, names, tickers, text (only id and text go to the model). It prints
the counts left out and the sample and blind tests. Reads the index's closes at FT_DB_PATH.

Usage: uv run python scripts/eightk_text.py fetch SEC_DIR OUT
"""

import csv
import json
import random
import re
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_moves import MORE_FILERS, UNLISTED, membership, window_day  # noqa: E402
from tenk_business import HEADERS, _names, _ticker, blind, plain  # noqa: E402

from fortuneteller import db  # noqa: E402
from fortuneteller.study import stored_closes  # noqa: E402

FIRST, LAST = date(2020, 1, 1), date(2025, 12, 31)
ITEMS = {"2.05", "3.02", "5.02", "7.01", "8.01"}
ALWAYS = {"2.05", "3.02"}
RESULTS = "2.02"
SIZE, SEED, PART = 400, 43, 4_000
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{name}"
INDEX = "{accession}-index.htm"
ITEM = re.compile(r"(?i)\bitem\s*\d\.\d\d\b")


class Filing(NamedTuple):
    day: date
    ticker: str
    cik: int
    accession: str
    document: str
    items: str
    accepted: str


def filings(index: dict, sec: Path) -> list[tuple[datetime, str, str, str]]:
    """A filer's 8-Ks (not 8-K/A): acceptance time, accession, primary document, items."""
    parts = [index["filings"]["recent"]]
    parts += [json.loads((sec / f["name"]).read_text()) for f in index["filings"]["files"]]
    return [
        (
            datetime.fromisoformat(part["acceptanceDateTime"][i].replace("Z", "+00:00")),
            part["accessionNumber"][i],
            part["primaryDocument"][i],
            part["items"][i],
        )
        for part in parts
        for i, form in enumerate(part["form"])
        if form == "8-K"
    ]


def pick(
    day_filings: list[tuple[datetime, str, str, str]],
) -> tuple[datetime, str, str, str] | None:
    """A member-day's filing: none if any carries 2.02, else the first filed carrying one of the
    five items."""
    if any(RESULTS in f[3].split(",") for f in day_filings):
        return None
    kept = sorted(f for f in day_filings if ITEMS & set(f[3].split(",")))
    return kept[0] if kept else None


def draw(found: list[Filing]) -> list[Filing]:
    """Every 2.05 or 3.02 member-day, and the rest of the sample drawn from the others; sorted by
    day and ticker."""
    found = sorted(found, key=lambda f: (f.day, f.ticker))
    always = [f for f in found if ALWAYS & set(f.items.split(","))]
    others = [f for f in found if not ALWAYS & set(f.items.split(","))]
    chosen = always + random.Random(SEED).sample(others, SIZE - len(always))
    return sorted(chosen, key=lambda f: (f.day, f.ticker))


def from_item(text: str) -> str:
    """The text from its first item heading, past the cover page; empty if it has none."""
    found = ITEM.search(text)
    return text[found.start() :] if found else ""


def exhibit(page: str) -> str | None:
    """The first exhibit 99's file name in a filing's index page."""
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        if len(cells) >= 4 and re.sub(r"<[^>]+>", "", cells[3]).strip().startswith("EX-99"):
            link = re.search(r'href="[^"]*/([^/"]+)"', cells[2])
            if link:
                return link.group(1)
    return None


def leaks(row: dict[str, str]) -> bool:
    """Whether a text still holds one of its company's names or tickers."""
    names = [n for n in row["names"].split("|") if n]
    tickers = [t for t in row["tickers"].split("|") if t]
    return any(
        re.search(rf"(?<!\w){re.escape(n)}(?!\w)", row["text"], flags=re.I) for n in names
    ) or any(re.search(_ticker(t), row["text"]) for t in tickers)


def _get(url: str, path: Path) -> str:
    if not path.exists():
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=60) as response:
            path.write_bytes(response.read())
        time.sleep(1)
    return path.read_text(errors="replace")


def listing(sec: Path) -> tuple[list[Filing], dict[str, int]]:
    """Every member-day's filing in the period, and the counts left out."""
    tickers = json.loads((sec / "company_tickers.json").read_text())
    ciks = UNLISTED | {row["ticker"]: int(row["cik_str"]) for row in tickers.values()}
    days = [c.day for c in stored_closes("SPY / ES", con=db.get_connection())]
    out = {"no filer": 0, "results that day": 0}
    found, seen = [], set()
    for ticker, spans in sorted(membership().items()):
        cik = ciks.get(ticker)
        if cik is None or not (sec / f"CIK{cik:010d}.json").exists():
            out["no filer"] += 1
            continue
        by_day: dict[date, list[tuple[datetime, str, str, str]]] = {}
        for each in [cik, *MORE_FILERS.get(ticker, [])]:
            path = sec / f"CIK{each:010d}.json"
            if path.exists():
                for f in filings(json.loads(path.read_text()), sec):
                    day = window_day(f[0], days)
                    if day is not None and FIRST <= day <= LAST:
                        by_day.setdefault(day, []).append(f)
        for day, day_filings in by_day.items():
            if not any(a <= day < b for a, b in spans) or (cik, day) in seen:
                continue
            chosen = pick(day_filings)
            if chosen is None:
                out["results that day"] += any(ITEMS & set(f[3].split(",")) for f in day_filings)
                continue
            seen.add((cik, day))
            stamp, accession, document, items = chosen
            found.append(Filing(day, ticker, cik, accession, document, items, stamp.isoformat()))
    return found, out


def fetch(sec: Path, out: Path) -> None:
    found, left = listing(sec)
    sample = draw(found)
    print(f"member-days with a filing {len(found)}; sampled {len(sample)}; left out: {left}")
    (out / "html").mkdir(parents=True, exist_ok=True)
    rows, counts = [], {"no item heading": 0, "no exhibit 99": 0, "stub": 0}
    names_of = {}
    for i, f in enumerate(sample, 1):
        folder = f.accession.replace("-", "")
        stem = out / "html" / f"{f.cik}-{f.accession}"
        index_path = sec / f"CIK{f.cik:010d}.json"
        if f.cik not in names_of:
            names_of[f.cik] = json.loads(index_path.read_text())["name"]
        main = from_item(
            plain(
                _get(
                    ARCHIVE.format(cik=f.cik, folder=folder, name=f.document),
                    stem.with_suffix(".main.html"),
                )
            )
        )
        page = _get(
            ARCHIVE.format(cik=f.cik, folder=folder, name=INDEX.format(accession=f.accession)),
            stem.with_suffix(".index.html"),
        )
        name = exhibit(page)
        release = ""
        if name:
            url = ARCHIVE.format(cik=f.cik, folder=folder, name=name)
            release = plain(_get(url, stem.with_suffix(".ex99.html")))
        counts["no item heading"] += not main
        counts["no exhibit 99"] += name is None
        tickers = [f.ticker]
        text = main[:PART] + (("\n\nPress release: " + release[:PART]) if release else "")
        text = blind(text, names_of[f.cik], tickers)
        counts["stub"] += len(text) < 500
        rows.append(
            {
                "id": f"F{i:03d}",
                "day": f.day.isoformat(),
                "ticker": f.ticker,
                "cik": f.cik,
                "accession": f.accession,
                "items": f.items,
                "names": "|".join(_names(names_of[f.cik])),
                "tickers": "|".join(tickers),
                "text": text,
            }
        )
    with (out / "texts.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"texts {len(rows)}; {counts}")
    found_blind = [r["id"] for r in rows if leaks(r)]
    print(f"blind test: {len(found_blind)} found {found_blind[:10]}")
    redrawn = draw(found)
    print(
        f"sample test: draw reproduced {redrawn == sample}; one per member-day "
        f"{len({(f.cik, f.day) for f in sample}) == len(sample)}; items kept "
        f"{all(ITEMS & set(f.items.split(',')) and RESULTS not in f.items.split(',') for f in sample)}"
    )


if __name__ == "__main__":
    fetch(Path(sys.argv[2]), Path(sys.argv[3]))
