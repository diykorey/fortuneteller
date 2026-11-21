import csv
import sys
import duckdb
from datetime import date

csv.field_size_limit(10**7)
store, texts = sys.argv[1], sys.argv[2]
scores = {r["id"]: int(r["score"]) for r in csv.DictReader(open("docs/steps/severity-scores.csv"))}
rows = sorted((r for r in csv.DictReader(open(texts))), key=lambda r: (r["day"], r["ticker"]))
raw = duckdb.connect(store, read_only=True)
spy = [
    d
    for (d,) in raw.execute(
        "select day from daily_bars where instrument='SPY / ES' order by day"
    ).fetchall()
]
for label, test in (("first bad", lambda s: s <= -2), ("first good", lambda s: s >= 2)):
    r = next(r for r in rows if test(scores[r["id"]]))
    day = date.fromisoformat(r["day"])
    before = max(d for d in spy if d < day)

    def ret(t):
        got = dict(
            raw.execute(
                "select day, close from daily_bars where instrument=? and day in (?, ?)",
                [t, before, day],
            ).fetchall()
        )
        return got[day] / got[before] - 1

    stock, idx = ret(r["ticker"]), ret("SPY / ES")
    print(
        f"{label}: {r['id']} {r['ticker']} {day} items {r['items']} score {scores[r['id']]}; close before {before};"
        f" stock {stock:+.4%}, SPY {idx:+.4%}, excess {stock - idx:+.6f}"
    )
