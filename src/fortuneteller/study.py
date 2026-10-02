"""Event study over US CPI releases — MVP step 1 onward (see ``docs/steps/step-1-releases.md``).

Step 1: fetch the CPI initial-release history from FRED in one request, parse it into dated
records, map each to an ``EventInstance``, and store them. Each record keeps both dates, because the
reference month (what was measured) and the release date (when the market saw it) are about six
weeks apart.

Step 2 (see ``docs/steps/step-2-prices.md``): fetch each instrument's daily closes from Yahoo and
parse them into dated closes, the date read in the exchange's own time zone, and store them; then
measure each instrument's move around each CPI release into ``observations``.

Step 3 (see ``docs/steps/step-3-raw-move.md``): compare each instrument's moves on CPI days with its
moves on all other days.
"""

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.parse
import urllib.request
from bisect import bisect_left
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Any, NamedTuple
from zoneinfo import ZoneInfo

import duckdb

from . import db
from .models import DailyBar, EventInstance, Observation

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
CPI_SERIES_ID = "CPIAUCSL"
MISSING_VALUE = "."

# Exact keys from data/seed/event_types.csv and countries.csv — joins match on these strings.
CPI_EVENT_TYPE = "CPI / inflation surprise"
CPI_COUNTRY = "United States"
CPI_RELEASE_TIME = time(8, 30)
CPI_RELEASE_ZONE = ZoneInfo("America/New_York")
FIRST_RELEASE = "first_release"

# FRED release dates checked against BLS and found wrong, by reference month. Every date from 1994
# matches BLS's release archive; a sample of earlier years matches BLS's printed schedules except
# these. Source for each: the BLS schedule cited beside it.
RELEASE_DATE_CORRECTIONS = {
    # FRED: Sunday 1992-12-13. BLS: "November — December 11" (CPI Detailed Report, May 1992).
    date(1992, 11, 1): date(1992, 12, 11),
}

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
# A reply that is not the expected JSON shape raises one of these while it is read.
MALFORMED_REPLY = (ValueError, KeyError, IndexError, TypeError)
# Network failures urllib does not wrap in URLError, e.g. a read that times out or a dropped reply.
NETWORK_FAILURE = (OSError, http.client.HTTPException)

# Yahoo refuses requests without a browser-like User-Agent.
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}


class PriceSeries(NamedTuple):
    ticker: str
    unit: str


# The five MVP instruments, keyed by the exact symbol in data/seed/instruments.csv, with the Yahoo
# ticker each is read from and the unit its move is measured in: pct for prices, bps for the yield.
# Order matters: observations are numbered by position in this table.
MVP_PRICE_SERIES = {
    "SPY / ES": PriceSeries("^GSPC", "pct"),
    "UST10Y / ZN": PriceSeries("^TNX", "bps"),
    "DXY": PriceSeries("DX-Y.NYB", "pct"),
    "GC / XAU": PriceSeries("GC=F", "pct"),
    "VIX": PriceSeries("^VIX", "pct"),
}

# A close more than this many calendar days from the release is not "the day before" or "the
# reaction": four admits Friday -> Tuesday after a Monday holiday and rejects a hole in the data.
MAX_CLOSE_GAP_DAYS = 4
BEFORE_HISTORY = "before_history"
NO_CLOSE_NEARBY = "no_close_nearby"
YAHOO = "yahoo"
DAILY_CLOSE = "daily_close"


@dataclass(frozen=True)
class CpiRelease:
    reference_month: date
    released: date
    value: float


@dataclass(frozen=True)
class DailyClosingPrice:
    day: date
    price: float


@dataclass
class ReleaseCounts:
    """For one instrument: how many CPI releases were measured, and how many skipped and why."""

    measured: int = 0
    skipped_before_history: int = 0
    skipped_no_close_nearby: int = 0


class FredError(RuntimeError):
    pass


class YahooError(RuntimeError):
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


def store_daily_bars(
    instrument: str,
    ticker: str,
    closes: Sequence[DailyClosingPrice],
    con: duckdb.DuckDBPyConnection | None = None,
) -> int:
    """Write one instrument's closes to ``daily_bars``; re-running overwrites by (instrument, day)."""
    source = f"yahoo:{ticker}"
    bars = [
        DailyBar(instrument=instrument, day=c.day, close=c.price, source=source) for c in closes
    ]
    return db.insert_models("daily_bars", bars, con=con, replace=True)


def load_daily_bars(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, int]:
    """Fetch, parse and store every MVP instrument's daily closes; return the count per instrument.

    All five are fetched and parsed before any is stored, so a failure on one leaves ``daily_bars``
    as it was rather than half-refreshed.
    """
    fetched: dict[str, tuple[str, list[DailyClosingPrice]]] = {}
    for instrument, (ticker, _unit) in MVP_PRICE_SERIES.items():
        payload = fetch_daily_bars(ticker)
        try:
            closes = parse_daily_bars(payload)
        except YahooError as exc:
            raise YahooError(f"{ticker}: {exc}") from None
        if not closes:
            raise YahooError(f"Yahoo sent no usable closes for {ticker}")
        fetched[instrument] = (ticker, closes)
    return {
        instrument: store_daily_bars(instrument, ticker, closes, con=con)
        for instrument, (ticker, closes) in fetched.items()
    }


def closing_price_before_after(
    closes: Sequence[DailyClosingPrice], release_date: date
) -> tuple[DailyClosingPrice, DailyClosingPrice] | str:
    """The last close before the release date and the first on or after it, or why there is none.

    ``closes`` must be in date order. Returns ``BEFORE_HISTORY`` when no close precedes the release,
    and ``NO_CLOSE_NEARBY`` when the reaction close is missing or either close is more than
    ``MAX_CLOSE_GAP_DAYS`` from the release.
    """
    i = bisect_left(closes, release_date, key=lambda close: close.day)
    if i == 0:
        return BEFORE_HISTORY
    if i == len(closes):
        return NO_CLOSE_NEARBY
    before, after = closes[i - 1], closes[i]
    if (release_date - before.day).days > MAX_CLOSE_GAP_DAYS:
        return NO_CLOSE_NEARBY
    if (after.day - release_date).days > MAX_CLOSE_GAP_DAYS:
        return NO_CLOSE_NEARBY
    return before, after


def release_move(before: DailyClosingPrice, after: DailyClosingPrice, unit: str) -> float:
    """The move from ``before`` to ``after``: relative for prices, in basis points for yields."""
    if unit == "bps":
        return (after.price - before.price) * 100
    if unit == "pct":
        return after.price / before.price - 1
    raise ValueError(f"unknown unit {unit!r}: expected 'pct' or 'bps'")


def build_observations(
    con: duckdb.DuckDBPyConnection | None = None,
) -> tuple[list[Observation], dict[str, ReleaseCounts]]:
    """Measure every MVP instrument around every stored CPI release, from ``daily_bars``."""
    events = db.fetch_all(
        EventInstance,
        "SELECT * FROM event_instances WHERE event_type = ? ORDER BY event_id",
        [CPI_EVENT_TYPE],
        con=con,
    )
    observations: list[Observation] = []
    release_counts: dict[str, ReleaseCounts] = {}
    for position, (instrument, (_ticker, unit)) in enumerate(MVP_PRICE_SERIES.items()):
        bars = db.fetch_all(
            DailyBar,
            "SELECT * FROM daily_bars WHERE instrument = ? ORDER BY day",
            [instrument],
            con,
        )
        if not bars:
            raise ValueError(f"no daily_bars for {instrument}: load its prices first")
        closes = [DailyClosingPrice(bar.day, bar.close) for bar in bars]
        counts = release_counts[instrument] = ReleaseCounts()
        for event in events:
            # event_ts is naive UTC; the release date is the New York calendar date.
            release_date = event.event_ts.replace(tzinfo=UTC).astimezone(CPI_RELEASE_ZONE).date()
            pair = closing_price_before_after(closes, release_date)
            if pair == BEFORE_HISTORY:
                counts.skipped_before_history += 1
                continue
            if isinstance(pair, str):
                counts.skipped_no_close_nearby += 1
                continue
            before, after = pair
            counts.measured += 1
            observations.append(
                Observation(
                    # Unique only while event_id is: the same CPI-only caveat as event_id itself.
                    obs_id=event.event_id * 10 + position,
                    event_id=event.event_id,
                    instrument=instrument,
                    px_t0=before.price,
                    ret_unit=unit,
                    ret_5m=None,
                    ret_1h=None,
                    ret_1d=release_move(before, after, unit),
                    ret_1w=None,
                    abn_ret_1d=None,
                    car=None,
                    peak_move=None,
                    half_life_min=None,
                    realized_dir=None,
                    data_source=YAHOO,
                    quality=DAILY_CLOSE,
                )
            )
    return observations, release_counts


def store_observations(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, ReleaseCounts]:
    """Rebuild the CPI observations: the table ends up holding exactly what this run measured."""
    connection = con if con is not None else db.get_connection()
    observations, release_counts = build_observations(con=connection)
    db.replace_rows(
        "observations",
        observations,
        "event_id IN (SELECT event_id FROM event_instances WHERE event_type = ?)",
        [CPI_EVENT_TYPE],
        con=connection,
    )
    return release_counts


def daily_moves(closes: Sequence[DailyClosingPrice], unit: str) -> dict[date, float]:
    """Each day's absolute move from the previous close, keyed by the day.

    ``closes`` must be in date order. A pair more than ``MAX_CLOSE_GAP_DAYS`` apart is a hole in the
    data, not a day, and is skipped.
    """
    return {
        after.day: abs(release_move(before, after, unit))
        for before, after in zip(closes, closes[1:], strict=False)
        if (after.day - before.day).days <= MAX_CLOSE_GAP_DAYS
    }


def cpi_days(closes: Sequence[DailyClosingPrice], release_dates: Iterable[date]) -> set[date]:
    """The days whose move is a CPI release's reaction: the close step 2 pairs each release with."""
    days = set()
    for release_date in release_dates:
        pair = closing_price_before_after(closes, release_date)
        if not isinstance(pair, str):
            days.add(pair[1].day)
    return days
