"""Step 20, part 2's sets and texts (docs/steps/article-to-trigger.md).

`sets` lists every row of docs/steps/article-to-trigger-set.csv from part 1's dataset and coding;
`fetch SPLIT` fetches that split's texts into a directory and appends each fetch to
docs/steps/article-to-trigger-fetch.csv. Only `fetch test` reads a test address, and only after the
rules are frozen. `count SPLIT` prints each row's last answer in the log, by expected kind.

Usage:
  uv run --with openpyxl python -I scripts/article_texts.py sets DATASET.xlsx
  uv run python -I scripts/article_texts.py fetch dev|test TEXT_DIR
  uv run python -I scripts/article_texts.py count dev|test
  uv run python -I scripts/article_texts.py read dev|test TEXT_DIR STORE
"""

import csv
import gzip
import html
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs" / "steps"
SET = DOCS / "article-to-trigger-set.csv"
LOG = DOCS / "article-to-trigger-fetch.csv"
CODING = DOCS / "ceo-scandals-coding.csv"
SEED = Path(__file__).resolve().parent.parent / "data" / "seed" / "ceo_scandals.csv"

URL = re.compile(r"https?://[^\s,;\"'<>]+")
LOGIN = re.compile(r"login\?url=|idm\.oclc\.org|ezproxy|\.lp\.hscl\.")
SEC_UA = "research-client admin@example.com"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
HIDDEN = re.compile(r"<(script|style|noscript|head)\b.*?</\1\s*>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
TEXT_TYPES = ("text/html", "text/plain", "application/xhtml+xml", "text/xml")
ARCHIVE_PAUSE = 20
LOG_HEAD = ["dismissal_dataset_id", "address", "fetched_at", "via", "words", "reason"]


def _address(row: dict) -> str:
    urls = [u.rstrip(".)") for c in ("sources", "eight_ks") for u in URL.findall(row[c] or "")]
    usable = [u for u in urls if not LOGIN.search(u)]
    return (usable or urls or [""])[0]


def _iso(value) -> str:
    return value.date().isoformat() if value else ""


def _words(name: str) -> list[str]:
    return [
        w.strip(",").lower() for w in name.split() if len(w.strip(",.")) > 1 and not w.endswith(".")
    ]


def sets(xlsx: str) -> None:
    from openpyxl import load_workbook

    sheet = load_workbook(xlsx, read_only=True).worksheets[0].iter_rows(values_only=True)
    head = next(sheet)
    rows = {r["dismissal_dataset_id"]: r for r in (dict(zip(head, v)) for v in sheet)}
    coding = list(csv.DictReader(CODING.open(newline="")))
    seed = list(csv.DictReader(SEED.open(newline="")))

    def ticker(ceo: str) -> str:
        found = [
            s["ticker"]
            for s in seed
            if {_words(s["ceo"])[0], [w for w in _words(s["ceo"]) if w not in ("ii", "jr")][-1]}
            <= set(_words(ceo))
        ]
        assert len(found) == 1, (ceo, found)
        return found[0]

    kept = {
        int(c["dismissal_dataset_id"]): ticker(c["ceo"]) for c in coding if c["decision"] == "kept"
    }
    coded_out = [
        int(c["dismissal_dataset_id"]) for c in coding if c["reason"] == "not the CEO's own conduct"
    ]
    pool = sorted(
        i for i, r in rows.items() if r["departure_code"] in (1, 2, 3, 5, 6) and _address(r)
    )
    negatives = coded_out + random.Random(20261114).sample(pool, 100)
    assert len(kept) == 26 and len(coded_out) == 179 and len(set(negatives)) == 279

    def order(i: int) -> tuple[str, int]:
        r = rows[i]
        return (_iso(r["date_departure_announced"]) or _iso(r["left_ceo_office"]), i)

    out = []
    for kind, ids in (("ceo", list(kept)), ("none", negatives)):
        for n, i in enumerate(sorted(ids, key=order)):
            r = rows[i]
            split = "dev" if n % 2 == 0 else "test"
            out.append(
                [i, _address(r), split, kind, kept.get(i, ""), _iso(r["date_departure_announced"])]
            )
    with SET.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(
            ["dismissal_dataset_id", "address", "split", "expected_kind", "ticker", "day"]
        )
        writer.writerows(sorted(out))


def _get(url: str) -> tuple[str, bytes]:
    host = urllib.parse.urlsplit(url).hostname
    # EDGAR asks for a contact; the archive refuses a browser's name from a script (HTTP 429).
    agent = SEC_UA if host in ("sec.gov", "www.sec.gov", "web.archive.org") else BROWSER_UA
    headers = {"User-Agent": agent, "Accept-Encoding": "gzip", "Accept": "text/html,*/*"}
    archive = urllib.parse.urlsplit(url).hostname == "web.archive.org"
    for wait in (60, 120, 240, None):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as reply:
                body = reply.read()
                if reply.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                time.sleep(ARCHIVE_PAUSE if archive else 1)
                return reply.headers.get_content_type(), body
        except urllib.error.HTTPError as e:
            # The archive's rate limit means "later", not "no text": wait and ask again.
            if not (archive and e.code == 429 and wait):
                raise
            time.sleep(wait)
    raise AssertionError("unreachable")


def _text(url: str) -> tuple[str, int, str]:
    """The page's words, their count, and why it is counted out ("" if it is not)."""
    try:
        kind, body = _get(url)
    except urllib.error.HTTPError as e:
        time.sleep(1)
        return "", 0, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - every failure is a reason, logged
        time.sleep(1)
        return "", 0, f"fetch failed ({type(e).__name__})"
    if kind not in TEXT_TYPES:
        return "", 0, f"not a text page ({kind})"
    raw = body.decode("utf-8", "replace")
    text = re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", HIDDEN.sub(" ", raw)))).strip()
    words = len(WORD.findall(text))
    return text, words, "" if words >= 100 else "under 100 words"


def _first_capture(url: str) -> tuple[str, str]:
    """The first capture's stamp, or why there is none."""
    query = urllib.parse.urlencode(
        {"url": url, "filter": "statuscode:200", "limit": "1", "output": "json"}
    )
    try:
        _, body = _get(f"https://web.archive.org/cdx/search/cdx?{query}")
        found = json.loads(body or b"[]")
    except urllib.error.HTTPError as e:
        return "", f"archive HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - every failure is a reason, logged
        return "", f"archive failed ({type(e).__name__})"
    return (found[1][1], "") if len(found) > 1 else ("", "no capture")


def fetch(split: str, text_dir: str) -> None:
    out = Path(text_dir)
    out.mkdir(parents=True, exist_ok=True)
    last = {}
    if LOG.exists():
        last = {r["dismissal_dataset_id"]: r["reason"] for r in csv.DictReader(LOG.open())}
    # A row is fetched until it has an answer other than a rate limit, so a run can resume.
    rows = [
        r
        for r in csv.DictReader(SET.open(newline=""))
        if r["split"] == split and last.get(r["dismissal_dataset_id"], "HTTP 429") == "HTTP 429"
    ]
    new = not LOG.exists()
    with LOG.open("a", newline="") as file:
        log = csv.writer(file, lineterminator="\n")
        if new:
            log.writerow(LOG_HEAD)
        for row in rows:
            url, row_id = row["address"], row["dismissal_dataset_id"]
            at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            if LOGIN.search(url):
                log.writerow([row_id, url, at, "none", 0, "library login"])
                continue
            text, words, reason = _text(url)
            log.writerow([row_id, url, at, "browser", words, reason])
            if reason:
                stamp, reason = _first_capture(url)
                at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                if not stamp:
                    log.writerow([row_id, url, at, "archive", 0, reason])
                else:
                    text, words, reason = _text(f"https://web.archive.org/web/{stamp}id_/{url}")
                    log.writerow([row_id, url, at, f"archive {stamp}", words, reason])
            file.flush()
            if not reason:
                (out / f"{row_id}.txt").write_text(text)
            print(row_id, words, reason or "text", flush=True)


def count(split: str) -> None:
    """Each row's last answer in the log, by expected kind: a text (from the page or the archive)
    or the reason it is counted out."""
    kinds = {r["dismissal_dataset_id"]: r for r in csv.DictReader(SET.open(newline=""))}
    last = {r["dismissal_dataset_id"]: r for r in csv.DictReader(LOG.open(newline=""))}
    tally: dict[tuple[str, str], int] = {}
    for row_id, row in kinds.items():
        if row["split"] != split:
            continue
        answer = last.get(row_id)
        if answer is None:
            what = "not fetched"
        elif answer["reason"]:
            what = answer["reason"].split(" (")[0]
        else:
            what = "text, " + ("page" if answer["via"] == "browser" else "archive")
        key = (row["expected_kind"], what)
        tally[key] = tally.get(key, 0) + 1
    for (kind, what), n in sorted(tally.items()):
        print(f"{kind}\t{what}\t{n}")


def read(split: str, text_dir: str, store: str) -> None:
    """The rule's counts on a split (docs/steps/article-to-trigger.md): a positive is read only as
    ceo; a negative read as either kind counts toward the 5% bar; the day on read positives with a
    set day, right if it is that day or, for a time at or after 16:00, the next S&P 500 trading
    day; the ticker right, empty or wrong against the set, each wrong one listed for the hand
    check."""
    from bisect import bisect_right
    from datetime import date

    import duckdb

    from fortuneteller.study import article_day, read_article

    with duckdb.connect(store, read_only=True) as con:
        days = [
            r[0]
            for r in con.execute(
                "select day from daily_bars where instrument = 'SPY / ES' order by day"
            ).fetchall()
        ]
    texts = Path(text_dir)
    with_text = {"ceo": 0, "none": 0}
    read_as = {("ceo", "ceo"): 0, ("ceo", "conduct"): 0, ("none", "ceo"): 0, ("none", "conduct"): 0}
    ticker = {"right": 0, "empty": 0, "wrong": 0}
    day = {"right": 0, "wrong": 0}
    for row in csv.DictReader(SET.open(newline="")):
        path = texts / f"{row['dismissal_dataset_id']}.txt"
        if row["split"] != split or not path.exists():
            continue
        kind = row["expected_kind"]
        with_text[kind] += 1
        reading = read_article(path.read_text())
        if reading is not None:
            read_as[(kind, reading.kind)] += 1
        line = f"{row['dismissal_dataset_id']} {kind} read {reading.kind if reading else 'none'}"
        if kind == "ceo" and reading is not None and reading.kind == "ceo":
            what = (
                "empty"
                if not reading.ticker
                else ("right" if reading.ticker == row["ticker"] else "wrong")
            )
            ticker[what] += 1
            line += f" ticker {reading.ticker or '-'} ({what}, set {row['ticker']})"
            filed = article_day(reading, days)
            if row["day"]:
                want = date.fromisoformat(row["day"])
                late = reading.at is not None and reading.at.hour >= 16
                after = days[bisect_right(days, want)] if late else want
                verdict = "right" if filed in (want, after) else "wrong"
                day[verdict] += 1
                line += f" day {filed} ({verdict}, set {want})"
            else:
                line += f" day {filed} (no set day)"
        if kind == "ceo" or reading is not None:
            print(line)
    positives, negatives = with_text["ceo"], with_text["none"]
    misread = read_as[("none", "ceo")] + read_as[("none", "conduct")]
    print(f"positives with a text: {positives}; read as ceo: {read_as[('ceo', 'ceo')]}", end="")
    print(f"; read as the second kind: {read_as[('ceo', 'conduct')]}")
    print(f"negatives with a text: {negatives}; read as either kind: {misread}", end="")
    print(f" (ceo {read_as[('none', 'ceo')]}, the second kind {read_as[('none', 'conduct')]})")
    print(f"ticker on positives read: {ticker}; day on those with a set day: {day}")
    if positives < 10:
        verdict = "too few texts"
    elif read_as[("ceo", "ceo")] >= 0.75 * positives and misread <= 0.05 * negatives:
        verdict = "reads"
    else:
        verdict = "doesn't read"
    print(f"by the rule: {verdict}")


if __name__ == "__main__":
    if sys.argv[1] == "sets":
        sets(sys.argv[2])
    elif sys.argv[1] == "read" and sys.argv[2] in ("dev", "test"):
        read(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "count" and sys.argv[2] in ("dev", "test"):
        count(sys.argv[2])
    elif sys.argv[1] == "fetch" and sys.argv[2] in ("dev", "test"):
        fetch(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
