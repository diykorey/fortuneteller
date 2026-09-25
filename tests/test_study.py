"""CPI initial-release history: fetch, parse, and map to events, on a trimmed real response."""

import csv
import io
import json
import urllib.error
from datetime import date, datetime
from email.message import Message
from pathlib import Path
from typing import Any, NoReturn

import duckdb
import pytest

from fortuneteller import db, study
from fortuneteller.config import settings
from fortuneteller.study import (
    CpiRelease,
    FredError,
    parse_cpi_releases,
    store_cpi_releases,
    to_event_instance,
)

FIXTURE = Path(__file__).parent / "data" / "fred_cpi_initial_release.json"


def _payload(mutate: Any = None) -> bytes:
    document = json.loads(FIXTURE.read_bytes())
    if mutate is not None:
        mutate(document)
    return json.dumps(document).encode()


def test_release_date_comes_from_realtime_start_not_reference_month() -> None:
    # given the saved FRED initial-release response
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, _ = parse_cpi_releases(payload)

    # then the first print is dated by publication, six weeks after the month it measures
    assert releases[0] == CpiRelease(date(1972, 7, 1), date(1972, 8, 22), 125.31)
    assert all(r.released > r.reference_month for r in releases)


def test_valueless_print_is_skipped_and_reported() -> None:
    # given a response where 2025-10 was published without a number
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, valueless = parse_cpi_releases(payload)

    # then that month is reported, not stored, and every other row survives
    assert valueless == [date(2025, 10, 1)]
    assert date(2025, 10, 1) not in {r.reference_month for r in releases}
    assert len(releases) == 6


def test_shared_release_date_and_irregular_schedule_are_kept() -> None:
    # given rows with a shared release date, a Sunday release, and a 62-day lag
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, _ = parse_cpi_releases(payload)

    # then each is kept as published
    by_month = {r.reference_month: r for r in releases}
    assert by_month[date(2025, 11, 1)].released == date(2025, 12, 18)
    assert by_month[date(1992, 11, 1)].released == date(1992, 12, 13)
    assert by_month[date(1995, 12, 1)].released == date(1996, 2, 1)
    assert releases[-1] == CpiRelease(date(2026, 8, 1), date(2026, 9, 11), 334.131)


def test_release_on_its_reference_month_is_rejected() -> None:
    # given a row dated by reference month, as the plain series view would return it
    def series_view(document: dict[str, Any]) -> None:
        document["observations"][0]["realtime_start"] = document["observations"][0]["date"]

    payload = _payload(series_view)

    # when / then parsing refuses it
    with pytest.raises(FredError, match="1972-07-01"):
        parse_cpi_releases(payload)


def test_truncated_response_is_rejected() -> None:
    # given a response whose count disagrees with the rows sent
    def truncate(document: dict[str, Any]) -> None:
        document["observations"].pop()

    payload = _payload(truncate)

    # when / then parsing refuses it
    with pytest.raises(FredError, match="reported 7 rows but sent 6"):
        parse_cpi_releases(payload)


def test_http_error_does_not_leak_the_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # given FRED rejecting the request and echoing the key back in both the URL and the body
    key = "abcdef0123456789abcdef0123456789"
    url = f"{study.FRED_OBSERVATIONS_URL}?api_key={key}"
    body = f'{{"error_message": "Bad Request. {url}"}}'.encode()

    def reject(*_args: Any, **_kwargs: Any) -> NoReturn:
        raise urllib.error.HTTPError(url, 400, "Bad Request", Message(), io.BytesIO(body))

    monkeypatch.setattr(study.urllib.request, "urlopen", reject)

    # when the fetch fails
    with pytest.raises(FredError) as caught:
        study.fetch_cpi_releases(key)

    # then neither the message nor the exception chain carries the key
    assert "HTTP 400" in str(caught.value)
    assert key not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def _events_by_month() -> dict[str, datetime]:
    releases, _ = parse_cpi_releases(FIXTURE.read_bytes())
    return {e.detail or "": e.event_ts for e in map(to_event_instance, releases)}


def test_event_ts_is_release_day_at_0830_new_york_in_naive_utc() -> None:
    # given prints released in summer time, in winter, and during the 1974 year-round summer time
    # when they are mapped to events
    event_ts = _events_by_month()

    # then each lands on its release day at 08:30 New York, expressed as naive UTC
    assert event_ts["2026-08"] == datetime(2026, 9, 11, 12, 30)
    assert event_ts["2025-11"] == datetime(2025, 12, 18, 13, 30)
    assert event_ts["1973-12"] == datetime(1974, 1, 22, 12, 30)
    assert all(ts.tzinfo is None for ts in event_ts.values())


def test_event_is_keyed_by_reference_month_and_dated_by_release() -> None:
    # given the two prints first published on the same day
    release = CpiRelease(date(2025, 11, 1), date(2025, 12, 18), 325.031)

    # when the print is mapped
    event = to_event_instance(release)

    # then the id and detail name the month measured, the timestamp the day it was published
    assert event.event_id == 202511
    assert event.detail == "2025-11"
    assert event.event_ts.date() == date(2025, 12, 18)
    assert event.actual == 325.031
    assert event.scheduled
    assert event.quality == "first_release"
    assert event.consensus is None
    assert event.surprise is None


def test_event_ids_are_stable_and_unique() -> None:
    # given every print in the fixture, including two sharing a release date
    releases, _ = parse_cpi_releases(FIXTURE.read_bytes())

    # when they are mapped twice
    first = [to_event_instance(r).event_id for r in releases]
    second = [to_event_instance(r).event_id for r in releases]

    # then the ids repeat exactly and never collide
    assert first == second
    assert len(set(first)) == len(first)


def test_event_keys_match_the_seed_reference_tables() -> None:
    # given the committed event-type and country CSVs
    def column(filename: str, name: str) -> set[str]:
        with (settings.seed_dir / filename).open(newline="", encoding="utf-8") as handle:
            return {row[name] for row in csv.DictReader(handle)}

    # when a mapped event is built
    event = to_event_instance(CpiRelease(date(2026, 8, 1), date(2026, 9, 11), 334.131))

    # then its join keys exist exactly as written
    assert event.event_type in column("event_types.csv", "event_type")
    assert event.country in column("countries.csv", "country")


def _store(time_zone: str = "UTC") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{time_zone}'")
    db.init_db(con=con)
    releases, _ = parse_cpi_releases(FIXTURE.read_bytes())
    store_cpi_releases(releases, con=con)
    return con


def test_rerunning_the_store_changes_no_row_count() -> None:
    # given the fixture releases already stored once
    con = _store()
    releases, _ = parse_cpi_releases(FIXTURE.read_bytes())

    # when they are stored again
    written = store_cpi_releases(releases, con=con)

    # then every row is overwritten in place, not appended
    assert written == 6
    assert db.count_rows("event_instances", con=con) == 6


def test_event_ts_round_trips_as_utc_under_a_non_utc_session() -> None:
    # given a store whose session time zone is not UTC, as on a developer machine
    con = _store("Europe/Kyiv")

    # when the August 2026 print is read back
    row = con.execute("SELECT event_ts FROM event_instances WHERE event_id = 202608").fetchone()

    # then it is still 08:30 New York in UTC, not shifted to the session zone
    assert row == (datetime(2026, 9, 11, 12, 30),)
