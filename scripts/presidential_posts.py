"""Build a seed of the president's trade-post days from one archive dump.

The Trump Twitter Archive's dump writes data/seed/presidential_posts.csv
(docs/steps/presidential-posts.md); CNN's Truth Social archive writes
data/seed/presidential_posts_2.csv (docs/steps/presidential-posts-2.md).

Usage: uv run python scripts/presidential_posts.py <path to one archive's JSON dump>
"""

import csv
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
IN_OFFICE = datetime(2017, 1, 20, 12, 0, tzinfo=NEW_YORK)
SECOND_TERM = datetime(2025, 1, 20, 12, 0, tzinfo=NEW_YORK)
SECOND_TERM_CUTOFF = datetime(2026, 10, 31, 0, 0, tzinfo=NEW_YORK)
TOPIC = re.compile(r"\btariff|\btrade[\s-]+war|\btrade[\s-]+deal", re.IGNORECASE)
RATE = re.compile(r"\d\s*(%|percent)", re.IGNORECASE)
LINK = re.compile(r"https?://\S+")
SEED = Path("data/seed/presidential_posts.csv")
SEED_2 = Path("data/seed/presidential_posts_2.csv")


def names_rate(text: str) -> bool:
    """A number with % or percent within 60 characters of "tariff"."""
    for match in re.finditer(r"tariff", text, re.IGNORECASE):
        window = text[max(0, match.start() - 60) : match.end() + 60]
        if RATE.search(window):
            return True
    return False


def matching_tweets(dump: list[dict[str, str]]) -> list[tuple[datetime, bool]]:
    """Each in-office matching tweet's New York time, truncated to the minute, and whether it names a rate."""
    found = []
    for tweet in dump:
        if tweet["isRetweet"] != "f":
            continue
        text = LINK.sub("", html.unescape(tweet["text"])).strip()
        if text.startswith(("RT @", '"', "“")):
            continue
        posted = (
            datetime.fromisoformat(tweet["date"])
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(NEW_YORK)
        )
        if posted < IN_OFFICE or not TOPIC.search(text):
            continue
        found.append((posted.replace(second=0, microsecond=0), names_rate(text)))
    return sorted(found)


def matching_truth_posts(dump: list[dict[str, str]]) -> list[tuple[datetime, bool]]:
    """Each second-term matching post's New York time, truncated to the minute, and whether it names a rate."""
    found = []
    for post in dump:
        text = LINK.sub("", html.unescape(post["content"] or "")).strip()
        if not text or text.startswith(("RT @", "RT:", '"', "“")):
            continue
        posted = datetime.fromisoformat(post["created_at"]).astimezone(NEW_YORK)
        if not SECOND_TERM <= posted < SECOND_TERM_CUTOFF or not TOPIC.search(text):
            continue
        found.append((posted.replace(second=0, microsecond=0), names_rate(text)))
    return sorted(found)


def main() -> int:
    dump = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if dump and "isRetweet" in dump[0]:
        posts, seed = matching_tweets(dump), SEED
    elif dump and "created_at" in dump[0]:
        posts, seed = matching_truth_posts(dump), SEED_2
    else:
        raise SystemExit("unknown archive: its posts have neither isRetweet nor created_at")
    days: dict[str, list[tuple[datetime, bool]]] = {}
    for posted, rate in posts:
        days.setdefault(posted.date().isoformat(), []).append((posted, rate))
    with seed.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "time", "posts", "rate_time"])
        for day, found in sorted(days.items()):
            rate_times = [posted for posted, rate in found if rate]
            writer.writerow(
                [
                    day,
                    f"{found[0][0]:%H:%M}",
                    len(found),
                    f"{rate_times[0]:%H:%M}" if rate_times else "",
                ]
            )
    print(f"{sum(len(t) for t in days.values())} posts on {len(days)} days written to {seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
