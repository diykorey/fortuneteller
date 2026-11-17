"""Step 24's one check: the IMF's decisions against the oil market's surprise (docs/steps/opec.md).

Reads docs/steps/opec-imf.csv (the IMF's coding of OPEC meetings, Pescatori and Nazer 2022, table
7, *neutral* written *hold*), keeps the stored OPEC announcements on those days, and prints
`follows`' table for them twice, by the IMF's decision and by the surprise's sign, each with its
count of answered cells, Brent's day left out.

Usage: uv run python scripts/opec_imf.py
"""

import csv
from pathlib import Path

from fortuneteller import db, flows, study
from fortuneteller.__main__ import describe_follows

IMF = Path("docs/steps/opec-imf.csv")
DECISIONS = ("cut", "hold", "boost")
MARKED = (study.KIND_SPAN, study.KIND_MARKET)


def main() -> None:
    with IMF.open(newline="") as file:
        imf = {row["day"]: row["decision"] for row in csv.DictReader(file)}
    con = db.get_connection()
    stored = flows.stored_events(flows.OPEC_FLOW, con=con)
    matched = [e for e in stored if flows.release_date(e).isoformat() in imf]
    print(f"IMF meetings: {len(imf)}; on a day of the list: {len(matched)}")
    runs = (
        (
            "by the IMF's decision",
            DECISIONS,
            {e.event_id: imf[flows.release_date(e).isoformat()] for e in matched},
        ),
        ("by the surprise's sign", study.OPEC_KINDS, study.detail_kinds(matched)),
    )
    for title, order, kinds in runs:
        events, cells = study.follow_decisions(flows.OPEC_FLOW, kinds, order, con=con)
        print(f"\n{title}")
        for line in describe_follows(
            events, kinds, cells, order, "OPEC announcements", marked=MARKED
        ):
            print(line)
        answered = sum(
            f.answer in study.OUTCOMES for _, span, market, f in cells if (span, market) != MARKED
        )
        print(f"answered cells {title}: {answered}")


if __name__ == "__main__":
    main()
