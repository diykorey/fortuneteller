import collections
import csv
import hashlib
import sys

csv.field_size_limit(10**7)
texts = list(csv.DictReader(open(sys.argv[1])))
first = {r["id"]: int(r["score"]) for r in csv.DictReader(open("docs/steps/severity-scores.csv"))}
second = {r["id"]: int(r["score"]) for r in csv.DictReader(open("docs/steps/severity-second.csv"))}


def side(s: int) -> int:
    return -1 if s <= -2 else 1 if s >= 2 else 0


items = collections.Counter(
    i for r in texts for i in set(r["items"].split(",")) & {"2.05", "3.02", "5.02", "7.01", "8.01"}
)
lengths = sorted(len(r["text"]) for r in texts)
print(
    "texts",
    len(texts),
    "by item",
    dict(sorted(items.items())),
    "length",
    lengths[0],
    lengths[len(lengths) // 2],
    lengths[-1],
)
print("with a press release", sum("Press release: " in r["text"] for r in texts))
print("texts.csv SHA-256", hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())
d = collections.Counter(first.values())
print(
    "scores",
    len(first),
    " ".join(f"{k}:{d[k]}" for k in sorted(d)),
    "bad",
    sum(side(s) == -1 for s in first.values()),
    "good",
    sum(side(s) == 1 for s in first.values()),
)
bad701 = [r for r in texts if side(first[r["id"]]) == -1 and "7.01" in r["items"].split(",")]
print(
    "bad 7.01",
    len(bad701),
    "with a press release",
    sum("Press release: " in r["text"] for r in bad701),
)
pairs = [(first[k], v) for k, v in second.items()]
print(
    "second reading",
    len(pairs),
    "within 2",
    sum(abs(a - b) <= 2 for a, b in pairs),
    "same side",
    sum(side(a) == side(b) for a, b in pairs),
    "equal",
    sum(a == b for a, b in pairs),
)
