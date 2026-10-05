"""The outside sources: request each one's data and parse the reply into plain records.

FRED (``docs/steps/step-1-releases.md``): the CPI release history, each value as first published
with its release date. Yahoo (``docs/steps/step-2-prices.md``): each instrument's daily closes, by
trading date in the exchange's own time zone. Nothing here touches the database.
"""

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo


# A reply that is not the expected JSON shape raises one of these while it is read.
MALFORMED_REPLY = (ValueError, KeyError, IndexError, TypeError)
# Network failures urllib does not wrap in URLError, e.g. a read that times out or a dropped reply.
NETWORK_FAILURE = (OSError, http.client.HTTPException)


# FRED


FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
CPI_SERIES_ID = "CPIAUCSL"
MISSING_VALUE = "."

# FRED release dates checked against BLS and found wrong, by reference month. Every date from 1994
# matches BLS's release archive; a sample of earlier years matches BLS's printed schedules except
# these. Source for each: the BLS schedule cited beside it.
RELEASE_DATE_CORRECTIONS = {
    # FRED: Sunday 1992-12-13. BLS: "November — December 11" (CPI Detailed Report, May 1992).
    date(1992, 11, 1): date(1992, 12, 11),
}


@dataclass(frozen=True)
class CpiRelease:
    reference_month: date
    released: date
    value: float


class FredError(RuntimeError):
    pass


def fetch_cpi_releases(api_key: str, timeout: float = 30.0) -> bytes:
    """Return the raw FRED response: every CPI print as first published, with its release date."""
    if not api_key:
        raise FredError("the FRED API key is empty")
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
    except NETWORK_FAILURE as exc:
        raise FredError(f"FRED request failed: {exc}".replace(api_key, "<redacted>")) from None


def parse_cpi_releases(payload: bytes) -> tuple[list[CpiRelease], list[date]]:
    """Parse a FRED initial-release response into records, plus the months printed with no value.

    Raises if a release date is not after its reference month — the sign that the series view,
    not the initial-release view, was fetched — or falls on a weekend, which BLS never publishes on.
    Release dates known to be wrong in FRED are replaced from ``RELEASE_DATE_CORRECTIONS``.
    """
    try:
        document: Any = json.loads(payload)
        observations: list[dict[str, str]] = document["observations"]
        if document["count"] != len(observations):
            raise FredError(f"FRED reported {document['count']} rows but sent {len(observations)}")

        releases: list[CpiRelease] = []
        valueless: list[date] = []
        for row in observations:
            reference_month = date.fromisoformat(row["date"])
            released = date.fromisoformat(row["realtime_start"])
            released = RELEASE_DATE_CORRECTIONS.get(reference_month, released)
            if released <= reference_month:
                raise FredError(f"{reference_month}: released {released}, not after its month")
            if released.weekday() >= 5:
                raise FredError(
                    f"{reference_month}: released {released:%A} {released}, a weekend; "
                    "check it against BLS and add it to RELEASE_DATE_CORRECTIONS"
                )
            if row["value"] == MISSING_VALUE:
                valueless.append(reference_month)
                continue
            releases.append(CpiRelease(reference_month, released, float(row["value"])))
        return releases, valueless
    except MALFORMED_REPLY as exc:
        raise FredError(f"FRED sent an unexpected reply: {exc!r}") from None


# Yahoo


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
# Yahoo refuses requests without a browser-like User-Agent.
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}


@dataclass(frozen=True)
class DailyClosingPrice:
    day: date
    price: float


class YahooError(RuntimeError):
    pass


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
    except NETWORK_FAILURE as exc:
        raise YahooError(f"Yahoo request for {ticker} failed: {exc}") from None


def parse_daily_bars(payload: bytes, today: date | None = None) -> list[DailyClosingPrice]:
    """Parse a Yahoo chart response into closes by trading date, oldest first.

    Each bar's timestamp is read as a date in the exchange's own time zone, named in the response:
    the dollar index and gold are stamped at midnight New York time, which any other zone can put
    on the previous day. Yahoo's ``gmtoffset`` is today's offset, not the bar's, so it is not used.
    Bars with no close, bars dated on a weekend, and today's bar (still trading, so its close is not
    final; ``today`` defaults to the exchange's current date) are dropped. Two bars on one date
    are rejected: that is what a misread time zone looks like.
    """
    try:
        document: Any = json.loads(payload)
        chart = document["chart"]
        if chart.get("error"):
            raise YahooError(f"Yahoo returned an error: {chart['error']}")
        result = chart["result"][0]
        zone = ZoneInfo(result["meta"]["exchangeTimezoneName"])
        today = today if today is not None else datetime.now(zone).date()
        timestamps: list[int] = result.get("timestamp", [])
        closes: list[float | None] = result["indicators"]["quote"][0]["close"]
        if len(timestamps) != len(closes):
            raise YahooError(f"Yahoo sent {len(timestamps)} timestamps but {len(closes)} closes")

        by_day: dict[date, float] = {}
        for timestamp, close in zip(timestamps, closes, strict=True):
            if close is None:
                continue
            day = datetime.fromtimestamp(timestamp, zone).date()
            if day.weekday() >= 5 or day >= today:
                continue
            if day in by_day:
                raise YahooError(f"Yahoo sent two bars on {day}")
            by_day[day] = close
        return [DailyClosingPrice(day, by_day[day]) for day in sorted(by_day)]
    except MALFORMED_REPLY as exc:
        raise YahooError(f"Yahoo sent an unexpected reply: {exc!r}") from None
