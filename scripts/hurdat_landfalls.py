"""Step 28's seed: each storm's first US landfall as a hurricane since 1970 (docs/steps/weather.md).

Reads the National Hurricane Center's HURDAT2 Atlantic record as downloaded from
https://www.nhc.noaa.gov/data/hurdat/ and writes data/seed/hurricanes.csv: a row marked `L` (a
landfall) with status `HU` (a hurricane) whose place is on the US mainland or the Florida Keys,
the earliest such row of each storm.

Usage: uv run python scripts/hurdat_landfalls.py HURDAT2_TXT
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

SEED = Path("data/seed/hurricanes.csv")
FROM_YEAR = 1970


def on_us_coast(lat: float, lon: float) -> bool:
    """The spec's place rule: the US mainland or the Keys, not the Bahamas, Mexico or Canada."""
    if not (24.4 <= lat < 47.5 and lon <= -66.9):
        return False
    if lat < 32 and lon > -80.0:
        return False
    return not (lon < -96.5 and lat < 25.95)


def main(path: str) -> None:
    first: dict[str, tuple[datetime, str, int, float, float]] = {}
    storm = name = ""
    for line in open(path, encoding="utf-8"):
        part = [p.strip() for p in line.split(",")]
        if part[0].startswith("AL"):
            storm, name = part[0], part[1]
            continue
        if part[2] != "L" or part[3] != "HU" or storm in first:
            continue
        lat, lon = float(part[4][:-1]), -float(part[5][:-1])
        at = datetime.strptime(part[0] + part[1], "%Y%m%d%H%M")
        if at.year >= FROM_YEAR and on_us_coast(lat, lon):
            first[storm] = (at, name, int(part[6]), lat, lon)
    kept = sorted(first.values())
    with SEED.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["day", "time", "kind", "storm", "knots", "lat", "lon"])
        writer.writerows(
            [at.date().isoformat(), at.strftime("%H:%M"), "landfall", name.title(), knots, lat, lon]
            for at, name, knots, lat, lon in kept
        )
    print(f"wrote {len(kept)} rows to {SEED}, {kept[0][0].date()} … {kept[-1][0].date()}")


if __name__ == "__main__":
    main(sys.argv[1])
