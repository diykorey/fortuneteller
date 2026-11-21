"""Step 45 (docs/steps/sp500-on-the-page.md): the page's *ask* for the S&P 500's three kinds,
measured once on a store holding the members' closes (FT_DB_PATH) and frozen in
data/seed/ask_sp500.json with the day it was measured.

Usage: uv run python scripts/ask_sp500.py DAY
"""

import json
import sys

from fortuneteller import db
from fortuneteller.__main__ import FOLLOWS_NOUNS, SP500_ASK, SP500_FLOWS, ask_entry, market_names


def main(day: str) -> None:
    con = db.get_connection()
    names = market_names()
    entries = []
    for name in SP500_FLOWS:
        entries.append(ask_entry(name, FOLLOWS_NOUNS[name], con, names))
        print(f"{name}: {len(entries[-1]['cells'])} cells", flush=True)
    SP500_ASK.write_text(
        json.dumps({"measured": day, "ask": entries}, indent=1, ensure_ascii=False) + "\n"
    )
    print(f"written {SP500_ASK}")


if __name__ == "__main__":
    main(sys.argv[1])
