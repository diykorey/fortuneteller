"""The days a flow shares with other flows: per flow, and the distinct days in all.

Usage: uv run python scripts/shared_days.py FLOW
"""

import sys
from collections import Counter

from fortuneteller import db, flows


def main(name: str) -> None:
    con = db.get_connection()
    flow = flows.flow_named(name)
    days = {flows.release_date(e) for e in flows.stored_events(flow, con=con)}
    shared: set = set()
    by = Counter()
    for other in flows.EVENT_FLOWS:
        if other is flow:
            continue
        hit = {flows.release_date(e) for e in flows.stored_events(other, con=con)} & days
        if hit:
            by[other.label] = len(hit)
            shared |= hit
    print(f"{flow.label}: {len(days)} days, {len(shared)} shared with another flow")
    for label, n in by.most_common():
        print(f"  {label} {n}")


if __name__ == "__main__":
    main(sys.argv[1])
