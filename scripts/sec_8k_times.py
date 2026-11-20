"""Step 31's minutes: each member's 8-Ks with Item 2.02 from the SEC's filing index
(docs/steps/earnings.md).

`fetch DIR` saves the SEC's ticker list and each member's filing index, its older pages included,
under DIR, under ten requests a second. The current index, which holds the newest 8-Ks, is
fetched again each time (docs/steps/earnings-current.md); the older pages are kept as saved. A member renamed keeps its filer number; two whose reports
Nasdaq files under one symbol name both numbers here.

Usage: uv run python -I scripts/sec_8k_times.py fetch DIR
"""

import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

HEADERS = {"User-Agent": "research-client admin@example.com", "Accept-Encoding": "identity"}
TICKERS = "https://www.sec.gov/files/company_tickers.json"
INDEX = "https://data.sec.gov/submissions/{name}"
# Filers whose reports Nasdaq lists under a member's symbol of today: old DuPont under DD, old
# General Motors under GM, and the filers before a holding company was put on top (Disney in 2019,
# Exxon Mobil in 2026).
MORE_FILERS = {"DD": [30554], "GM": [40730], "DIS": [1001039], "XOM": [34088]}
# A member no longer listed, so not in the SEC's ticker list: Walgreens, taken private in 2025.
UNLISTED = {"WBA": 1618921}


def _get(url: str, path: Path, again: bool = False) -> bytes:
    if again or not path.exists():
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=60) as reply:
            path.write_bytes(reply.read())
        time.sleep(0.2)
    return path.read_bytes()


def members() -> list[str]:
    with Path("data/seed/dow.csv").open(newline="") as handle:
        return sorted({row["ticker"] for row in csv.DictReader(handle)})


def fetch(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    listing = json.loads(_get(TICKERS, folder / "company_tickers.json"))
    ciks = UNLISTED | {row["ticker"]: int(row["cik_str"]) for row in listing.values()}
    for ticker in members():
        for cik in [ciks[ticker], *MORE_FILERS.get(ticker, [])]:
            name = f"CIK{cik:010d}.json"
            index = json.loads(_get(INDEX.format(name=name), folder / name, again=True))
            for page in index["filings"]["files"]:
                _get(INDEX.format(name=page["name"]), folder / page["name"])
        print(ticker, ciks[ticker], MORE_FILERS.get(ticker, []))


if __name__ == "__main__":
    command, folder = sys.argv[1], Path(sys.argv[2])
    if command == "fetch":
        fetch(folder)
