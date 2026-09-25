"""Parse and fetch tests for the CPI initial-release history, against a trimmed real FRED response."""

import io
import json
import urllib.error
from datetime import date
from email.message import Message
from pathlib import Path
from typing import Any, NoReturn

import pytest

from fortuneteller import study
from fortuneteller.study import CpiRelease, FredError, parse_cpi_releases

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
    assert len(releases) == 5


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
    with pytest.raises(FredError, match="reported 6 rows but sent 5"):
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
