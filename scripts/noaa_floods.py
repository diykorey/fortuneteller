"""Step 30's seed: the US floods of NOAA's billion-dollar list that have a day (docs/steps/floods.md).

Reads NOAA's Billion-Dollar Weather and Climate Disasters list, 1980 to 2024, as archived (the
copy the spec names, with its sha256), and writes data/seed/floods.csv: every row whose
`Disaster` is `Flooding`, at its `Begin Date`, but a row that begins on the first of a month and
lasts 30 days or more, which is a season, not a day.

Usage: uv run python -I scripts/noaa_floods.py EVENTS_CSV
"""

import csv
import sys
from datetime import date, datetime
from pathlib import Path

SEED = Path("data/seed/floods.csv")
SEASON_DAYS = 30


def _day(text: str) -> date:
    return datetime.strptime(text, "%Y%m%d").date()


def is_season(begin: date, end: date) -> bool:
    """The spec's rule: a row from a month's first lasting 30 days or more has no day."""
    return begin.day == 1 and (end - begin).days >= SEASON_DAYS


def main(path: str) -> None:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    start = next(n for n, line in enumerate(lines) if line.startswith("Name,"))
    rows = []
    for row in csv.DictReader(lines[start:]):
        if row["Disaster"] != "Flooding":
            continue
        begin, end = _day(row["Begin Date"]), _day(row["End Date"])
        if is_season(begin, end):
            continue
        rows.append((begin.isoformat(), row["Name"], row["CPI-Adjusted Cost"]))
    rows.sort()
    with SEED.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "name", "cost"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} floods to {SEED}, {rows[0][0]} … {rows[-1][0]}")


if __name__ == "__main__":
    main(sys.argv[1])
