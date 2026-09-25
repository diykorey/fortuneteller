"""Event study over US CPI releases — MVP step 1 onward (see ``docs/step-1-releases.md``).

Today: fetch the CPI initial-release history from FRED in one request, parse it into dated
records, and map each to an ``EventInstance``. Each record keeps both dates, because the reference
month (what was measured) and the release date (when the market saw it) are about six weeks apart.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from .models import EventInstance

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
CPI_SERIES_ID = "CPIAUCSL"
MISSING_VALUE = "."

# Exact keys from data/seed/event_types.csv and countries.csv — joins match on these strings.
CPI_EVENT_TYPE = "CPI / inflation surprise"
CPI_COUNTRY = "United States"
CPI_RELEASE_TIME = time(8, 30)
CPI_RELEASE_ZONE = ZoneInfo("America/New_York")
FIRST_RELEASE = "first_release"


@dataclass(frozen=True)
class CpiRelease:
    reference_month: date
    released: date
    value: float


class FredError(RuntimeError):
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
