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
from pydantic import SecretStr

from fortuneteller import db, flows, sources
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import (
    FomcDecision,
    CPI_SERIES_ID,
    FirstRelease,
    FredError,
    parse_first_releases,
)
from fortuneteller.flows import (
    CPI_EVENT_TYPE,
    store_releases,
    to_event_instance,
)

FIXTURE = Path(__file__).parent / "data" / "fred_cpi_initial_release.json"
# Shaped like FRED's reply for PAYEMS: October and November 2025 first published on one day.
NFP_FIXTURE = Path(__file__).parent / "data" / "fred_nfp_initial_release.json"


def _fred_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    def fetch(_key: str, series_id: str) -> bytes:
        return (NFP_FIXTURE if series_id == sources.NFP_SERIES_ID else FIXTURE).read_bytes()

    monkeypatch.setattr(sources, "fetch_first_releases", fetch)


def _payload(mutate: Any = None) -> bytes:
    document = json.loads(FIXTURE.read_bytes())
    if mutate is not None:
        mutate(document)
    return json.dumps(document).encode()


def test_release_date_comes_from_realtime_start_not_reference_month() -> None:
    # given the saved FRED initial-release response
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, _ = parse_first_releases(payload, CPI_SERIES_ID)

    # then the first print is dated by publication, six weeks after the month it measures
    assert releases[0] == FirstRelease(date(1972, 7, 1), date(1972, 8, 22), 125.31)
    assert all(r.released > r.reference_month for r in releases)


def test_valueless_print_is_skipped_and_reported() -> None:
    # given a response where 2025-10 was published without a number
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, valueless = parse_first_releases(payload, CPI_SERIES_ID)

    # then that month is reported, not stored, and every other row survives
    assert valueless == [date(2025, 10, 1)]
    assert date(2025, 10, 1) not in {r.reference_month for r in releases}
    assert len(releases) == 6


def test_shared_release_date_and_irregular_schedule_are_kept() -> None:
    # given rows with a shared release date, a corrected release date, and a 62-day lag
    payload = FIXTURE.read_bytes()

    # when it is parsed
    releases, _ = parse_first_releases(payload, CPI_SERIES_ID)

    # then each is kept as published
    by_month = {r.reference_month: r for r in releases}
    assert by_month[date(2025, 11, 1)].released == date(2025, 12, 18)
    assert by_month[date(1992, 11, 1)].released == date(1992, 12, 11)
    assert by_month[date(1995, 12, 1)].released == date(1996, 2, 1)
    assert releases[-1] == FirstRelease(date(2026, 8, 1), date(2026, 9, 11), 334.131)


def test_release_on_its_reference_month_is_rejected() -> None:
    # given a row dated by reference month, as the plain series view would return it
    def series_view(document: dict[str, Any]) -> None:
        document["observations"][0]["realtime_start"] = document["observations"][0]["date"]

    payload = _payload(series_view)

    # when / then parsing refuses it
    with pytest.raises(FredError, match="1972-07-01"):
        parse_first_releases(payload, CPI_SERIES_ID)


def test_truncated_response_is_rejected() -> None:
    # given a response whose count disagrees with the rows sent
    def truncate(document: dict[str, Any]) -> None:
        document["observations"].pop()

    payload = _payload(truncate)

    # when / then parsing refuses it
    with pytest.raises(FredError, match="reported 7 rows but sent 6"):
        parse_first_releases(payload, CPI_SERIES_ID)


def test_http_error_does_not_leak_the_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # given FRED rejecting the request and echoing the key back in both the URL and the body
    key = "abcdef0123456789abcdef0123456789"
    url = f"{sources.FRED_OBSERVATIONS_URL}?api_key={key}"
    body = f'{{"error_message": "Bad Request. {url}"}}'.encode()

    def reject(*_args: Any, **_kwargs: Any) -> NoReturn:
        raise urllib.error.HTTPError(url, 400, "Bad Request", Message(), io.BytesIO(body))

    monkeypatch.setattr(sources.urllib.request, "urlopen", reject)

    # when the fetch fails
    with pytest.raises(FredError) as caught:
        sources.fetch_first_releases(key)

    # then neither the message nor the exception chain carries the key
    assert "HTTP 400" in str(caught.value)
    assert key not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def _events_by_month() -> dict[str, datetime]:
    releases, _ = parse_first_releases(FIXTURE.read_bytes(), CPI_SERIES_ID)
    return {
        r.reference_month.strftime("%Y-%m"): to_event_instance(r, CPI_EVENT_TYPE).event_ts
        for r in releases
    }


def test_event_ts_is_release_day_at_0830_new_york_in_naive_utc() -> None:
    # given prints released in summer time, in winter, and during the 1974 year-round summer time
    # when they are mapped to events
    event_ts = _events_by_month()

    # then each lands on its release day at 08:30 New York, expressed as naive UTC
    assert event_ts["2026-08"] == datetime(2026, 9, 11, 12, 30)
    assert event_ts["2025-11"] == datetime(2025, 12, 18, 13, 30)
    assert event_ts["1973-12"] == datetime(1974, 1, 22, 12, 30)
    assert all(ts.tzinfo is None for ts in event_ts.values())


def test_event_is_keyed_by_type_and_release_day_and_names_its_month() -> None:
    # given the November 2025 print, first published on 2025-12-18
    release = FirstRelease(date(2025, 11, 1), date(2025, 12, 18), 325.031)

    # when the print is mapped
    event = to_event_instance(release, CPI_EVENT_TYPE)

    # then the id is CPI's code and the release day, and the detail names the month measured
    assert event.event_id == 1_2025_12_18
    assert event.detail == "2025-11"
    assert event.event_ts.date() == date(2025, 12, 18)
    assert event.actual == 325.031
    assert event.scheduled
    assert event.quality == "first_release"
    assert event.consensus is None
    assert event.surprise is None


def test_event_ids_are_stable_and_unique() -> None:
    # given every print in the fixture, including two sharing a release date
    releases, _ = parse_first_releases(FIXTURE.read_bytes(), CPI_SERIES_ID)

    # when they are mapped twice
    first = [to_event_instance(r, CPI_EVENT_TYPE).event_id for r in releases]
    second = [to_event_instance(r, CPI_EVENT_TYPE).event_id for r in releases]

    # then the ids repeat exactly and never collide
    assert first == second
    assert len(set(first)) == len(first)


def test_event_keys_match_the_seed_reference_tables() -> None:
    # given the committed event-type and country CSVs
    def column(filename: str, name: str) -> set[str]:
        with (settings.seed_dir / filename).open(newline="", encoding="utf-8") as handle:
            return {row[name] for row in csv.DictReader(handle)}

    # when a mapped event is built
    event = to_event_instance(
        FirstRelease(date(2026, 8, 1), date(2026, 9, 11), 334.131), CPI_EVENT_TYPE
    )

    # then its join keys exist exactly as written
    assert event.event_type in column("event_types.csv", "event_type")
    assert event.country in column("countries.csv", "country")


def _store(time_zone: str = "UTC") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{time_zone}'")
    db.init_db(con=con)
    releases, _ = parse_first_releases(FIXTURE.read_bytes(), CPI_SERIES_ID)
    store_releases(CPI_EVENT_TYPE, releases, con=con)
    return con


def test_rerunning_the_store_changes_no_row_count() -> None:
    # given the fixture releases already stored once
    con = _store()
    releases, _ = parse_first_releases(FIXTURE.read_bytes(), CPI_SERIES_ID)

    # when they are stored again
    written = store_releases(CPI_EVENT_TYPE, releases, con=con)

    # then every row is overwritten in place, not appended
    assert written == 6
    assert db.count_rows("event_instances", con=con) == 6


def test_event_ts_round_trips_as_utc_under_a_non_utc_session() -> None:
    # given a store whose session time zone is not UTC, as on a developer machine
    con = _store("Europe/Kyiv")

    # when the August 2026 print is read back
    row = con.execute("SELECT event_ts FROM event_instances WHERE event_id = 120260911").fetchone()

    # then it is still 08:30 New York in UTC, not shifted to the session zone
    assert row == (datetime(2026, 9, 11, 12, 30),)


def test_load_releases_prints_count_range_and_skipped_months(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a configured key, FRED answering with the saved response, and two Fed decisions
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))
    _fred_answers(monkeypatch)
    decisions = [FomcDecision(date(2020, 3, 3), False), FomcDecision(date(2020, 3, 18), True)]
    monkeypatch.setattr(flows, "load_fomc_decisions", lambda _key: decisions)

    # when the command runs twice
    first = main(["load-releases"])
    second = main(["load-releases"])

    # then each run reports the same load, and the table holds one row per print and decision
    assert (first, second) == (0, 0)
    report = "loaded 6 CPI releases, 1972-08-22 … 2026-09-11\n"
    report += "  skipped 1 printed without a value: 2025-10\n"
    report += "loaded 3 NFP releases, 2025-11-20 … 2026-01-09\n"
    report += "  1 first published with a later month: 2025-10\n"
    report += "loaded 2 Fed decisions, 2020-03-03 … 2020-03-18 (1 unscheduled)\n"
    assert capsys.readouterr().out == report * 2
    assert db.count_rows("event_instances", con=db.get_connection()) == 11


def test_load_releases_stores_nothing_when_any_flow_fails(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given FRED answering for CPI and NFP, and the Fed's pages failing
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))
    _fred_answers(monkeypatch)

    def unreachable(_key: str) -> NoReturn:
        raise sources.FedError("the Fed's page did not answer")

    monkeypatch.setattr(flows, "load_fomc_decisions", unreachable)

    # when the command runs
    code = main(["load-releases"])

    # then it fails with the Fed named, and not even CPI's releases are stored
    assert code == 1
    assert "the Fed's page did not answer" in capsys.readouterr().err
    assert db.count_rows("event_instances", con=db.get_connection()) == 0


def test_load_releases_without_a_key_fails_before_fetching(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given no key configured
    monkeypatch.setattr(settings, "fred_api_key", None)

    def fetch(_key: str, series_id: str) -> NoReturn:
        raise AssertionError("fetched without a key")

    monkeypatch.setattr(sources, "fetch_first_releases", fetch)

    # when the command runs
    code = main(["load-releases"])

    # then it exits non-zero and says which setting is missing
    assert code == 1
    assert "FT_FRED_API_KEY" in capsys.readouterr().err


def test_load_releases_with_an_empty_key_fails_before_fetching(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the key set to an empty value, as a bare FT_FRED_API_KEY= line in .env gives
    monkeypatch.setattr(settings, "fred_api_key", SecretStr(""))

    def fetch(_key: str, series_id: str) -> NoReturn:
        raise AssertionError("fetched with an empty key")

    monkeypatch.setattr(sources, "fetch_first_releases", fetch)

    # when the command runs
    code = main(["load-releases"])

    # then it exits non-zero and says which setting is missing
    assert code == 1
    assert "FT_FRED_API_KEY" in capsys.readouterr().err


def test_fetch_refuses_an_empty_key() -> None:
    # given an empty key, which would also make error redaction replace every empty substring
    # when / then the fetch refuses before any request is made
    with pytest.raises(FredError, match="empty"):
        sources.fetch_first_releases("")


def test_load_releases_reports_a_fred_failure(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given FRED rejecting the request
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))

    def fetch(_key: str, series_id: str) -> NoReturn:
        raise FredError("FRED returned HTTP 400: Bad Request")

    monkeypatch.setattr(sources, "fetch_first_releases", fetch)

    # when the command runs
    code = main(["load-releases"])

    # then it exits non-zero with the reason and writes nothing
    assert code == 1
    assert "HTTP 400" in capsys.readouterr().err
    assert db.count_rows("event_instances", con=db.get_connection()) == 0


def test_non_json_fred_reply_is_a_fred_error() -> None:
    # given FRED answering with something that is not JSON
    # when / then parsing reports it as a FRED failure, not a JSON traceback
    with pytest.raises(FredError, match="unexpected reply"):
        parse_first_releases(b"<html>Service Unavailable</html>", CPI_SERIES_ID)


def test_fred_read_timeout_is_a_fred_error_without_the_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given a connection that stalls, with the key in the failing URL
    key = "abcdef0123456789abcdef0123456789"

    def stall(url: str, timeout: float) -> NoReturn:
        raise TimeoutError(f"timed out fetching {url}")

    monkeypatch.setattr(sources.urllib.request, "urlopen", stall)

    # when the fetch fails
    with pytest.raises(FredError) as caught:
        sources.fetch_first_releases(key)

    # then the error is a FRED failure that does not carry the key
    assert "timed out" in str(caught.value)
    assert key not in str(caught.value)


def test_load_releases_reports_a_malformed_reply(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a configured key and FRED answering with something that is not JSON
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))
    monkeypatch.setattr(sources, "fetch_first_releases", lambda _key, series_id: b"not json")

    # when the command runs
    code = main(["load-releases"])

    # then it exits non-zero with a message instead of a traceback
    assert code == 1
    assert "load-releases:" in capsys.readouterr().err


def test_known_wrong_release_date_is_corrected_from_bls() -> None:
    # given FRED dating the November 1992 print Sunday 1992-12-13
    payload = FIXTURE.read_bytes()

    # when the response is parsed
    releases, _ = parse_first_releases(payload, CPI_SERIES_ID)

    # then the date BLS scheduled and published, Friday 1992-12-11, is used instead
    by_month = {r.reference_month: r for r in releases}
    assert by_month[date(1992, 11, 1)].released == date(1992, 12, 11)


def test_release_date_on_a_weekend_is_rejected() -> None:
    # given a print FRED dates on a Saturday, with no correction known for it
    def saturday(document: dict[str, Any]) -> None:
        document["observations"][0]["realtime_start"] = "1972-08-19"

    payload = _payload(saturday)

    # when / then parsing refuses it: BLS does not publish CPI on weekends
    with pytest.raises(FredError, match="1972-07-01: released Saturday 1972-08-19"):
        parse_first_releases(payload, CPI_SERIES_ID)


def test_two_event_types_on_the_same_day_get_different_ids() -> None:
    # given the CPI code and another type's code on one day
    day = date(2022, 9, 13)

    # when the ids are built
    cpi = flows.event_id(flows.CPI_EVENT_TYPE, day)

    # then the type code leads, so another type on that day cannot collide
    assert cpi == 1_2022_09_13
    assert cpi // 10**8 == flows.CpiFlow.type_code


def test_months_first_published_on_one_day_are_one_release() -> None:
    # given October and November 2025 payrolls, both first published on 2025-12-16
    releases, _ = parse_first_releases(NFP_FIXTURE.read_bytes(), sources.NFP_SERIES_ID)

    # when they are reduced to one release per day
    kept, carried = flows.one_release_per_day(releases)

    # then the release day is November's event, and October is reported as carried by it
    assert [r.reference_month for r in kept] == [
        date(2025, 9, 1),
        date(2025, 11, 1),
        date(2025, 12, 1),
    ]
    assert [r.reference_month for r in carried] == [date(2025, 10, 1)]


def test_two_releases_on_one_day_are_refused_rather_than_overwritten() -> None:
    # given October and November 2025 payrolls on one day, not yet merged
    releases, _ = parse_first_releases(NFP_FIXTURE.read_bytes(), sources.NFP_SERIES_ID)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)

    # when / then storing them is refused: they would share an event_id
    with pytest.raises(ValueError, match="two releases on one day"):
        flows.store_releases(flows.NFP_EVENT_TYPE, releases, con=con)


def test_a_date_correction_belongs_to_its_own_series() -> None:
    # given a payrolls release for November 1992, the month CPI's date is corrected for
    payload = json.dumps(
        {
            "count": 1,
            "observations": [
                {"date": "1992-11-01", "realtime_start": "1992-12-04", "value": "108000"}
            ],
        }
    ).encode()

    # when it is parsed as payrolls
    releases, _ = parse_first_releases(payload, sources.NFP_SERIES_ID)

    # then FRED's date stands: CPI's correction does not apply to another series
    assert releases[0].released == date(1992, 12, 4)


def test_a_payrolls_release_is_keyed_with_its_own_type_code() -> None:
    # given the September 2026 jobs report, released 2026-10-02
    release = FirstRelease(date(2026, 9, 1), date(2026, 10, 2), 160000.0)

    # when it is mapped
    event = to_event_instance(release, flows.NFP_EVENT_TYPE)

    # then it is an NFP event at 08:30 New York, keyed 2 + its release day
    assert event.event_id == 2_2026_10_02
    assert event.event_type == "NFP / labor data"
    assert event.event_ts == datetime(2026, 10, 2, 12, 30)
