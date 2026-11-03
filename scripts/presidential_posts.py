"""Build data/seed/presidential_posts.csv from the Trump Twitter Archive dump (docs/steps/presidential-posts.md).

Usage: uv run python scripts/presidential_posts.py <path to the archive's JSON dump>
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
TOPIC = re.compile(r"\btariff|\btrade[\s-]+war|\btrade[\s-]+deal", re.IGNORECASE)
RATE = re.compile(r"\d\s*(%|percent)", re.IGNORECASE)
LINK = re.compile(r"https?://\S+")
SEED = Path("data/seed/presidential_posts.csv")


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


def main() -> int:
    dump = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    days: dict[str, list[tuple[datetime, bool]]] = {}
    for posted, rate in matching_tweets(dump):
        days.setdefault(posted.date().isoformat(), []).append((posted, rate))
    with SEED.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["day", "time", "posts", "rate_time"])
        for day, tweets in sorted(days.items()):
            rate_times = [posted for posted, rate in tweets if rate]
            writer.writerow(
                [
                    day,
                    f"{tweets[0][0]:%H:%M}",
                    len(tweets),
                    f"{rate_times[0]:%H:%M}" if rate_times else "",
                ]
            )
    print(f"{sum(len(t) for t in days.values())} tweets on {len(days)} days written to {SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
