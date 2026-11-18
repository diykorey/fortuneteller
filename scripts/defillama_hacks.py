"""Step 27's seed: every hack of $100 million or more on DefiLlama's list (docs/steps/crypto.md).

Reads the list as saved from https://api.llama.fi/hacks (a JSON array; each hack's `date` is its
day at 00:00 UTC, `amount` the dollars taken, `name` the target) and writes data/seed/crypto.csv.

Usage: uv run python scripts/defillama_hacks.py HACKS_JSON
"""

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

SEED = Path("data/seed/crypto.csv")
LINE = 100_000_000


def main(path: str) -> None:
    with open(path, encoding="utf-8") as file:
        hacks = json.load(file)
    kept = sorted(
        (datetime.fromtimestamp(h["date"], UTC).date(), h["name"].strip(), round(h["amount"]))
        for h in hacks
        if (h.get("amount") or 0) >= LINE
    )
    with SEED.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["day", "time", "kind", "target", "amount"])
        writer.writerows(
            [day.isoformat(), "04:00", "hack", name, amount] for day, name, amount in kept
        )
    print(f"wrote {len(kept)} rows to {SEED}, {kept[0][0]} … {kept[-1][0]}")


if __name__ == "__main__":
    main(sys.argv[1])
