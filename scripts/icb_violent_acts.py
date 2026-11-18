"""Step 26's seed: every crisis since 1970 that a violent act set off (docs/steps/war.md).

Reads the International Crisis Behavior project's version 16 files, the system-level
`icb1v16.csv` (the crisis's trigger date) and the actor-level `icb2v16.csv` (what each actor's
trigger was), keeps each crisis whose earliest actor's trigger (`triggr`) is 9, a violent act,
and writes data/seed/war.csv; a crisis with no trigger day is left out and named.

Usage: uv run python scripts/icb_violent_acts.py ICB1_CSV ICB2_CSV
"""

import csv
import sys
from datetime import date
from pathlib import Path

SEED = Path("data/seed/war.csv")
FROM_YEAR = 1970
VIOLENT_ACT = "9"


def _rows(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main(icb1: str, icb2: str) -> None:
    trigger = ("yrtrig", "motrig", "datrig")
    violent = {
        r["crisno"]
        for r in _rows(icb2)
        if tuple(r[k] for k in trigger) == (r["systrgyr"], r["systrgmo"], r["systrgda"])
        and r["triggr"] == VIOLENT_ACT
    }
    kept = []
    for r in _rows(icb1):
        if r["crisno"] not in violent or int(float(r["yrtrig"])) < FROM_YEAR:
            continue
        try:
            day = date(*(int(float(r[k])) for k in trigger))
        except ValueError:
            print(f"left out, no day: {r['crisname']} {r['yrtrig']}-{r['motrig']}-{r['datrig']}")
            continue
        kept.append((day, r["crisname"].strip()))
    kept.sort()
    with SEED.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["day", "time", "kind", "crisis"])
        writer.writerows([day.isoformat(), "04:00", "violent act", name] for day, name in kept)
    print(f"wrote {len(kept)} rows to {SEED}, {kept[0][0]} … {kept[-1][0]}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
