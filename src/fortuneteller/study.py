"""Event study over US CPI releases — MVP step 1 onward (see ``docs/steps/step-1-releases.md``).

Step 1: fetch the CPI initial-release history from FRED in one request, parse it into dated
records, map each to an ``EventInstance``, and store them. Each record keeps both dates, because the
reference month (what was measured) and the release date (when the market saw it) are about six
weeks apart.

Step 2 (see ``docs/steps/step-2-prices.md``): fetch each instrument's daily closes from Yahoo and
parse them into dated closes, the date read in the exchange's own time zone, and store them.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import duckdb

from . import db
from .models import DailyBar, EventInstance

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
CPI_SERIES_ID = "CPIAUCSL"
MISSING_VALUE = "."

# Exact keys from data/seed/event_types.csv and countries.csv — joins match on these strings.
CPI_EVENT_TYPE = "CPI / inflation surprise"
CPI_COUNTRY = "United States"
CPI_RELEASE_TIME = time(8, 30)
CPI_RELEASE_ZONE = ZoneInfo("America/New_York")
FIRST_RELEASE = "first_release"

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
# Yahoo refuses requests without a browser-like User-Agent.
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}

# The five MVP instruments, keyed by the exact symbol in data/seed/instruments.csv, with the Yahoo
# ticker each is read from. Order matters: step 2 numbers observations by position in this table.
MVP_TICKERS = {
    "SPY / ES": "^GSPC",
    "UST10Y / ZN": "^TNX",
    "DXY": "DX-Y.NYB",
    "GC / XAU": "GC=F",
    "VIX": "^VIX",
}


@dataclass(frozen=True)
class CpiRelease:
    reference_month: date
    released: date
    value: float


@dataclass(frozen=True)
class DailyClose:
    day: date
    close: float


class FredError(RuntimeError):
    pass


class YahooError(RuntimeError):
    pass


def fetch_cpi_releases(api_key: str, timeout: float = 30.0) -> bytes:
    """Return the raw FRED response: every CPI print as first published, with its release date."""
    params = {
        "series_id": CPI_SERIES_ID,
        "api_key": api_key,
        "file_type": "json",
        # 4 = initial release only: per reference month, the value as first printed.
        "output_type": "4",
        "realtime_start": "1776-07-04",
        "realtime_end": "9999-12-31",
    }
    url = f"{FRED_OBSERVATIONS_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as exc:
        # FRED echoes the request URL, key included, in its error body.
        detail = exc.read().decode("utf-8", errors="replace")
        message = f"FRED returned HTTP {exc.code}: {detail}".replace(api_key, "<redacted>")
        raise FredError(message) from None
    except urllib.error.URLError as exc:
        raise FredError(
            f"FRED request failed: {exc.reason}".replace(api_key, "<redacted>")
        ) from None


def parse_cpi_releases(payload: bytes) -> tuple[list[CpiRelease], list[date]]:
    """Parse a FRED initial-release response into records, plus the months printed with no value.

    Raises if a release date is not after its reference month — the sign that the series view,
    not the initial-release view, was fetched.
    """
    document: Any = json.loads(payload)
    observations: list[dict[str, str]] = document["observations"]
    if document["count"] != len(observations):
        raise FredError(f"FRED reported {document['count']} rows but sent {len(observations)}")

    releases: list[CpiRelease] = []
    valueless: list[date] = []
    for row in observations:
        reference_month = date.fromisoformat(row["date"])
        released = date.fromisoformat(row["realtime_start"])
        if released <= reference_month:
            raise FredError(f"{reference_month}: released {released}, not after its month")
        if row["value"] == MISSING_VALUE:
            valueless.append(reference_month)
            continue
        releases.append(CpiRelease(reference_month, released, float(row["value"])))
    return releases, valueless


def to_event_instance(release: CpiRelease) -> EventInstance:
    """Map one release to its ``event_instances`` row, keyed by reference month (``YYYYMM``).

    ``event_ts`` is naive UTC: DuckDB converts an aware datetime written to a ``TIMESTAMP`` column
    into the session time zone, so the offset is applied here and then dropped.
    """
    published = datetime.combine(release.released, CPI_RELEASE_TIME, tzinfo=CPI_RELEASE_ZONE)
    return EventInstance(
        # YYYYMM is unique only within CPI. event_id is the key of the whole table, so a second
        # event type keyed this way would collide and replace=True would silently overwrite CPI rows.
        # Before adding one, replace this with a key generic across event types, e.g. a
        # deterministic hash of (event_type, detail).
        event_id=release.reference_month.year * 100 + release.reference_month.month,
        event_type=CPI_EVENT_TYPE,
        event_ts=published.astimezone(UTC).replace(tzinfo=None),
        country=CPI_COUNTRY,
        detail=release.reference_month.strftime("%Y-%m"),
        scheduled=True,
        consensus=None,
        actual=release.value,
        surprise=None,
        surprise_sd=None,
        surprise_source=None,
        priced_in_prior=None,
        vix_t0=None,
        rate_regime=None,
        quality=FIRST_RELEASE,
    )


def store_cpi_releases(
    releases: Sequence[CpiRelease], con: duckdb.DuckDBPyConnection | None = None
) -> int:
    """Write the releases to ``event_instances``; re-running overwrites by ``event_id``."""
    events = [to_event_instance(release) for release in releases]
    return db.insert_models("event_instances", events, con=con, replace=True)


def fetch_daily_bars(ticker: str, timeout: float = 30.0) -> bytes:
    """Return the raw Yahoo chart response: the ticker's whole daily history."""
    params = {"period1": "0", "period2": "9999999999", "interval": "1d"}
    url = f"{YAHOO_CHART_URL}{urllib.parse.quote(ticker, safe='')}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=YAHOO_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as exc:
        raise YahooError(f"Yahoo returned HTTP {exc.code} for {ticker}") from None
    except urllib.error.URLError as exc:
        raise YahooError(f"Yahoo request for {ticker} failed: {exc.reason}") from None


def parse_daily_bars(payload: bytes) -> list[DailyClose]:
    """Parse a Yahoo chart response into closes by trading date, oldest first.

    Each bar's timestamp is read as a date in the exchange's own time zone, named in the response:
    the dollar index and gold are stamped at midnight New York time, which any other zone can put
    on the previous day. Yahoo's ``gmtoffset`` is today's offset, not the bar's, so it is not used.
    Bars with no close, and bars dated on a weekend, are dropped.
    """
    document: Any = json.loads(payload)
    chart = document["chart"]
    if chart.get("error"):
        raise YahooError(f"Yahoo returned an error: {chart['error']}")
    result = chart["result"][0]
    zone = ZoneInfo(result["meta"]["exchangeTimezoneName"])
    timestamps: list[int] = result.get("timestamp", [])
    closes: list[float | None] = result["indicators"]["quote"][0]["close"]
    if len(timestamps) != len(closes):
        raise YahooError(f"Yahoo sent {len(timestamps)} timestamps but {len(closes)} closes")

    by_day: dict[date, float] = {}
    for timestamp, close in zip(timestamps, closes, strict=True):
        if close is None:
            continue
        day = datetime.fromtimestamp(timestamp, zone).date()
        if day.weekday() >= 5:
            continue
        by_day[day] = close
    return [DailyClose(day, by_day[day]) for day in sorted(by_day)]


def store_daily_bars(
    instrument: str,
    ticker: str,
    closes: Sequence[DailyClose],
    con: duckdb.DuckDBPyConnection | None = None,
) -> int:
    """Write one instrument's closes to ``daily_bars``; re-running overwrites by (instrument, day)."""
    source = f"yahoo:{ticker}"
    bars = [
        DailyBar(instrument=instrument, day=c.day, close=c.close, source=source) for c in closes
    ]
    return db.insert_models("daily_bars", bars, con=con, replace=True)


def load_daily_bars(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, int]:
    """Fetch, parse and store every MVP instrument's daily closes; return the count per instrument."""
    return {
        instrument: store_daily_bars(
            instrument, ticker, parse_daily_bars(fetch_daily_bars(ticker)), con=con
        )
        for instrument, ticker in MVP_TICKERS.items()
    }
