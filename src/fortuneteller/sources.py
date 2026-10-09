"""The outside sources: request each one's data and parse the reply into plain records.

FRED (``docs/steps/step-1-releases.md``): the CPI and jobs-report release histories, each value as
first published with its release date. Yahoo (``docs/steps/step-2-prices.md``): each instrument's
daily closes, by trading date in the exchange's own time zone. The Cleveland Fed: CPI nowcasts.
The Federal Reserve (``docs/steps/rung-1-more-events.md``): the days it announced its decisions.
Nothing here touches the database.
"""

from __future__ import annotations

import http.client
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

# Every release time and market close in this project is New York's.
NEW_YORK = ZoneInfo("America/New_York")


# A reply that is not the expected JSON shape raises one of these while it is read.
MALFORMED_REPLY = (ValueError, KeyError, IndexError, TypeError)
# Network failures urllib does not wrap in URLError, e.g. a read that times out or a dropped reply.
NETWORK_FAILURE = (OSError, http.client.HTTPException)


# FRED


FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
CPI_SERIES_ID = "CPIAUCSL"
CORE_CPI_SERIES_ID = "CPILFESL"
NFP_SERIES_ID = "PAYEMS"
MISSING_VALUE = "."

# FRED release dates checked against BLS and found wrong, by series and reference month. CPI: every
# date from 1994 matches BLS's release archive, and a sample of earlier years its printed schedules,
# except these. NFP: every date from 1994 matches BLS's release texts. Source beside each.
RELEASE_DATE_CORRECTIONS: dict[str, dict[date, date]] = {
    CPI_SERIES_ID: {
        # FRED: Sunday 1992-12-13. BLS: "November — December 11" (CPI Detailed Report, May 1992).
        date(1992, 11, 1): date(1992, 12, 11),
    },
}


@dataclass(frozen=True)
class FirstRelease:
    reference_month: date
    released: date
    value: float


class FredError(RuntimeError):
    pass


def _fred_get(api_key: str, params: dict[str, str], timeout: float) -> bytes:
    """One FRED observations request; any failure becomes a ``FredError`` with the key redacted."""
    if not api_key:
        raise FredError("the FRED API key is empty")
    query = {**params, "api_key": api_key, "file_type": "json"}
    url = f"{FRED_OBSERVATIONS_URL}?{urllib.parse.urlencode(query)}"
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


def fetch_first_releases(
    api_key: str, series_id: str = CPI_SERIES_ID, timeout: float = 30.0
) -> bytes:
    """Return the raw FRED response: each month of a CPI series as first published, with its date."""
    params = {
        "series_id": series_id,
        # 4 = initial release only: per reference month, the value as first printed.
        "output_type": "4",
        "realtime_start": "1776-07-04",
        "realtime_end": "9999-12-31",
    }
    return _fred_get(api_key, params, timeout)


def fetch_vintages(api_key: str, series_id: str, timeout: float = 120.0) -> bytes:
    """Return the raw FRED response: every level of a series as it stood on each release day."""
    params = {
        "series_id": series_id,
        # 3 = new and revised: one column per release day, holding the months published that day.
        "output_type": "3",
        "realtime_start": "1776-07-04",
        "realtime_end": "9999-12-31",
    }
    return _fred_get(api_key, params, timeout)


def parse_vintages(payload: bytes, series_id: str) -> dict[date, dict[date, float]]:
    """Parse a FRED new-and-revised response: each month's levels, keyed by the day each came out.

    Columns are named ``<series_id>_YYYYMMDD``; an empty cell means the month was not published or
    revised that day.
    """
    prefix = f"{series_id}_"
    try:
        document: Any = json.loads(payload)
        observations: list[dict[str, str]] = document["observations"]
        if document["count"] != len(observations):
            raise FredError(f"FRED reported {document['count']} rows but sent {len(observations)}")
        return {
            date.fromisoformat(row["date"]): {
                datetime.strptime(column.removeprefix(prefix), "%Y%m%d").date(): float(value)
                for column, value in row.items()
                if column.startswith(prefix) and value != MISSING_VALUE
            }
            for row in observations
        }
    except MALFORMED_REPLY as exc:
        raise FredError(f"FRED sent an unexpected reply: {exc!r}") from None


def fetch_level_as_of(
    api_key: str, series_id: str, month: date, as_of: date, timeout: float = 30.0
) -> bytes:
    """Return the raw FRED response: one month's level as it stood on ``as_of``."""
    params = {
        "series_id": series_id,
        "observation_start": month.isoformat(),
        "observation_end": month.isoformat(),
        "realtime_start": as_of.isoformat(),
        "realtime_end": as_of.isoformat(),
    }
    return _fred_get(api_key, params, timeout)


def parse_level(payload: bytes) -> float:
    """Parse a FRED reply that must hold exactly one valued row, as ``fetch_level_as_of`` asks."""
    try:
        observations: list[dict[str, str]] = json.loads(payload)["observations"]
        if len(observations) != 1 or observations[0]["value"] == MISSING_VALUE:
            raise FredError(f"FRED sent {observations!r}, not one value")
        return float(observations[0]["value"])
    except MALFORMED_REPLY as exc:
        raise FredError(f"FRED sent an unexpected reply: {exc!r}") from None


def parse_first_releases(payload: bytes, series_id: str) -> tuple[list[FirstRelease], list[date]]:
    """Parse a FRED initial-release response into records, plus the months printed with no value.

    Raises if a release date is not after its reference month — the sign that the series view,
    not the initial-release view, was fetched — or falls on a weekend, which BLS never publishes on.
    Release dates known to be wrong in FRED are replaced from ``series_id``'s entry in
    ``RELEASE_DATE_CORRECTIONS``.
    """
    corrections = RELEASE_DATE_CORRECTIONS.get(series_id, {})
    try:
        document: Any = json.loads(payload)
        observations: list[dict[str, str]] = document["observations"]
        if document["count"] != len(observations):
            raise FredError(f"FRED reported {document['count']} rows but sent {len(observations)}")

        releases: list[FirstRelease] = []
        valueless: list[date] = []
        for row in observations:
            reference_month = date.fromisoformat(row["date"])
            released = date.fromisoformat(row["realtime_start"])
            released = corrections.get(reference_month, released)
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
            releases.append(FirstRelease(reference_month, released, float(row["value"])))
        return releases, valueless
    except MALFORMED_REPLY as exc:
        raise FredError(f"FRED sent an unexpected reply: {exc!r}") from None


# Yahoo


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
# Yahoo refuses requests without a browser-like User-Agent; the Fed's pages are sent it too.
BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0"}


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
    request = urllib.request.Request(url, headers=BROWSER_HEADERS)
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


# Cleveland Fed


CLEVELAND_NOWCAST_URL = (
    "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json"
)
CORE = "core"
HEADLINE = "headline"
# The jobs report's measure (rung 1): the monthly change in non-farm payrolls, in thousands.
PAYROLLS = "payrolls"
NOWCAST = "nowcast"
ACTUAL = "actual"
# The chart series step 4 reads, by name in the file; the PCE series are left out.
CLEVELAND_SERIES = {
    "Core CPI Inflation": (CORE, NOWCAST),
    "CPI Inflation": (HEADLINE, NOWCAST),
    "Actual Core CPI Inflation": (CORE, ACTUAL),
    "Actual CPI Inflation": (HEADLINE, ACTUAL),
}


@dataclass(frozen=True)
class NowcastPoint:
    """One value from the Cleveland Fed's chart: a month's CPI change in percent, as estimated on
    ``day`` (``NOWCAST``) or as published that day (``ACTUAL``)."""

    reference_month: date
    measure: str
    kind: str
    day: date
    percent: float


class ClevelandError(RuntimeError):
    pass


def fetch_nowcasts(timeout: float = 30.0) -> bytes:
    """Return the raw Cleveland Fed chart data: every month's daily nowcast path since 2013."""
    try:
        with urllib.request.urlopen(CLEVELAND_NOWCAST_URL, timeout=timeout) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as exc:
        raise ClevelandError(f"Cleveland Fed returned HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise ClevelandError(f"Cleveland Fed request failed: {exc.reason}") from None
    except NETWORK_FAILURE as exc:
        raise ClevelandError(f"Cleveland Fed request failed: {exc}") from None


def parse_nowcasts(payload: bytes) -> list[NowcastPoint]:
    """Parse the Cleveland Fed's chart data into dated values.

    One record per reference month, with day labels as ``MM/DD`` and no year. A month's path runs
    from that month up to three months on, so a label month before the reference month belongs to
    the next year (December's path ends in January).
    """
    try:
        records: Any = json.loads(payload)
        points: list[NowcastPoint] = []
        for record in records:
            year, month = (int(part) for part in record["chart"]["subcaption"].split("-"))
            labels = [c["label"] for c in record["categories"][0]["category"] if not c.get("vline")]
            days = [
                date(year if int(m) >= month else year + 1, int(m), int(d))
                for m, d in (label.split("/") for label in labels)
            ]
            for series in record["dataset"]:
                if series["seriesname"] not in CLEVELAND_SERIES:
                    continue
                measure, kind = CLEVELAND_SERIES[series["seriesname"]]
                values = series["data"]
                if len(values) != len(days):
                    raise ClevelandError(f"{year}-{month}: {len(values)} values, {len(days)} days")
                points += [
                    NowcastPoint(date(year, month, 1), measure, kind, day, float(value["value"]))
                    for day, value in zip(days, values, strict=True)
                    if value["value"]
                ]
        return points
    except MALFORMED_REPLY as exc:
        raise ClevelandError(f"Cleveland Fed sent an unexpected reply: {exc!r}") from None


# Federal Reserve


FED_HISTORY_URL = "https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm"
FED_CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# A year page's heading per meeting, in the forms the pages use: "January 29-30 Meeting - 2008",
# "January 31-February 1 Meeting - 1995", "April/May 30-1 Meeting - 2013",
# "March 15 (unscheduled) Meeting - 2020", "October 4 (unscheduled) - 2019",
# "March 19 (notation vote) - 2020", "January 21 Conference Call - 2008".
# From this meeting on, the Fed issued a statement after every one, change or not.
EVERY_MEETING_STATEMENT = date(1999, 5, 18)
FOMC_HEADING = re.compile(
    r"\s*(?P<month>[A-Za-z/]+)\s+(?P<first>\d+)(?:-(?:(?P<last_month>[A-Za-z]+)\s+)?(?P<last>\d+))?"
    r"\s*(?:\((?P<note>[^)]*)\))?\s*(?P<kind>Meeting|Conference Call)?\s*-\s*(?P<year>\d{4})"
)
STATEMENT_LINK = re.compile(r'href="[^"]*?(\d{8})[^"]*"[^>]*>\s*Statement')
CALENDAR_STATEMENT = re.compile(r"Statement:.*?pressreleases/monetary(\d{8})a\.htm", re.S)


@dataclass(frozen=True)
class FomcDecision:
    """A day the Fed announced a policy decision; unscheduled ones came between meetings."""

    day: date
    scheduled: bool


class FedError(RuntimeError):
    pass


def fed_history_url(year: int) -> str:
    return FED_HISTORY_URL.format(year=year)


def fetch_fed_page(url: str, timeout: float = 30.0) -> bytes:
    """Return one of the Fed's calendar pages."""
    request = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as exc:
        raise FedError(f"the Fed returned HTTP {exc.code} for {url}") from None
    except urllib.error.URLError as exc:
        raise FedError(f"the Fed request for {url} failed: {exc.reason}") from None
    except NETWORK_FAILURE as exc:
        raise FedError(f"the Fed request for {url} failed: {exc}") from None


def _day(digits: str) -> date:
    return date(int(digits[:4]), int(digits[4:6]), int(digits[6:]))


def parse_fomc_history(payload: bytes) -> list[FomcDecision]:
    """Parse one of the Fed's year pages (1994–2020) into its decisions, oldest first.

    A meeting or call that issued a statement is a decision on the statement's date: the day the
    market heard it (the call of 2008-01-21 was announced on the 22nd). A scheduled meeting with
    no statement before May 1999 is a decision on its last day: the Fed then announced only
    changes, and the market watched for one. Cancelled meetings, notation votes, calls without a
    statement and later meetings without one (2003-09-15, a briefing) are not decisions.
    """
    html = payload.decode("utf-8", errors="replace")
    blocks = re.split(r"<h5[^>]*>", html)[1:]
    if not blocks:
        raise FedError("the Fed's year page lists no FOMC meetings")
    decisions: dict[date, bool] = {}
    for block in blocks:
        heading, body = block.split("</h5>", 1)
        match = FOMC_HEADING.match(heading)
        if match is None:
            raise FedError(f"unrecognised FOMC heading: {heading.strip()!r}")
        note = (match["note"] or "").lower()
        if note in ("cancelled", "notation vote"):
            continue
        scheduled = match["kind"] == "Meeting" and note != "unscheduled"
        statement = STATEMENT_LINK.search(body.split("<h5", 1)[0])
        if statement:
            decisions.setdefault(_day(statement[1]), scheduled)
        elif scheduled:
            month = match["last_month"] or match["month"].split("/")[-1]
            day = date(
                int(match["year"]),
                MONTHS.index(month[:3]) + 1,
                int(match["last"] or match["first"]),
            )
            if day < EVERY_MEETING_STATEMENT:
                decisions.setdefault(day, True)
    return [FomcDecision(day, scheduled) for day, scheduled in sorted(decisions.items())]


def parse_fomc_calendar(payload: bytes) -> list[FomcDecision]:
    """Parse the Fed's current calendar (2021 on): each meeting with a statement, on its date.

    Meetings still to come have no statement yet, so they are not decisions.
    """
    html = payload.decode("utf-8", errors="replace")
    rows = re.split(r'class="(?:fomc-meeting--shaded )?row fomc-meeting"', html)[1:]
    if not rows:
        raise FedError("the Fed's calendar lists no FOMC meetings")
    decisions: dict[date, bool] = {}
    for row in rows:
        statement = CALENDAR_STATEMENT.search(row)
        if statement:
            decisions.setdefault(_day(statement[1]), "unscheduled" not in row[:600])
    return [FomcDecision(day, scheduled) for day, scheduled in sorted(decisions.items())]


def fetch_series(api_key: str, series_id: str, timeout: float = 30.0) -> bytes:
    """Return the raw FRED response: a series' observations as they stand today."""
    return _fred_get(api_key, {"series_id": series_id}, timeout)


def parse_series(payload: bytes) -> list[tuple[date, float]]:
    """Parse a FRED observations response into (date, value), skipping days with no value."""
    try:
        observations: list[dict[str, str]] = json.loads(payload)["observations"]
        return [
            (date.fromisoformat(row["date"]), float(row["value"]))
            for row in observations
            if row["value"] != MISSING_VALUE
        ]
    except MALFORMED_REPLY as exc:
        raise FredError(f"FRED sent an unexpected reply: {exc!r}") from None
