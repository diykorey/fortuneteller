"""Surprise: CPI's month-over-month change as first published, and how far it landed from expected."""

import json
import urllib.parse
from datetime import date

import pytest

from fortuneteller import sources, study
from fortuneteller.sources import CORE_CPI_SERIES_ID, CpiRelease, FredError, parse_level
from fortuneteller.study import MonthlyChange, first_published_changes, load_first_published_changes


def _release(month: tuple[int, int], released: tuple[int, int, int], level: float) -> CpiRelease:
    return CpiRelease(date(*month, 1), date(*released), level)


def test_a_month_s_change_is_its_level_over_the_previous_month_s() -> None:
    # given two consecutive first-published levels
    releases = [
        _release((2022, 7), (2022, 8, 10), 100.0),
        _release((2022, 8), (2022, 9, 13), 100.5),
    ]

    # when the changes are computed
    changes = first_published_changes(releases, revised_previous={})

    # then August rose 0.5%, and July, with no June, has no change
    assert changes == [MonthlyChange(date(2022, 8, 1), date(2022, 9, 13), pytest.approx(0.5))]


def test_january_is_measured_against_december_as_revised_that_day() -> None:
    # given December first published at 100.0, but revised to 100.2 on the day January came out
    releases = [
        _release((2022, 12), (2023, 1, 12), 100.0),
        _release((2023, 1), (2023, 2, 14), 100.5),
    ]

    # when the changes are computed with that revised level
    changes = first_published_changes(releases, revised_previous={date(2023, 1, 1): 100.2})

    # then January's change is the one BLS published, against the revised December
    assert changes[0].percent == pytest.approx((100.5 / 100.2 - 1) * 100)


def test_january_without_its_revised_december_is_refused() -> None:
    # given a January release and no revised December for it
    releases = [
        _release((2022, 12), (2023, 1, 12), 100.0),
        _release((2023, 1), (2023, 2, 14), 100.5),
    ]

    # when / then the change is refused rather than measured against the wrong December
    with pytest.raises(ValueError, match="2023-01"):
        first_published_changes(releases, revised_previous={})


def test_a_month_after_a_missing_month_has_no_change() -> None:
    # given September and November 2025, with October never published
    releases = [
        _release((2025, 8), (2025, 9, 11), 100.0),
        _release((2025, 9), (2025, 10, 24), 100.3),
        _release((2025, 11), (2025, 12, 18), 100.5),
    ]

    # when the changes are computed
    changes = first_published_changes(releases, revised_previous={})

    # then September has one, and November, with no October to compare with, has none
    assert [change.reference_month for change in changes] == [date(2025, 9, 1)]


def test_a_level_as_of_a_date_is_read_from_one_row() -> None:
    # given FRED's reply for one month as it stood on one day
    payload = json.dumps({"count": 1, "observations": [{"date": "2022-12-01", "value": "301.460"}]})

    # when it is parsed
    level = parse_level(payload.encode())

    # then the level is that row's value
    assert level == 301.46


@pytest.mark.parametrize(
    "observations",
    [[], [{"date": "2022-12-01", "value": "."}], [{"date": "2022-12-01", "value": "1"}] * 2],
)
def test_a_level_reply_without_exactly_one_value_is_refused(
    observations: list[dict[str, str]],
) -> None:
    # given a reply with no row, a missing value, or two rows
    payload = json.dumps({"count": len(observations), "observations": observations}).encode()

    # when / then it is refused
    with pytest.raises(FredError):
        parse_level(payload)


def test_loading_asks_for_each_january_s_december_as_of_its_release_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given FRED answering with three first releases and, for the level request, a revised December
    releases = {
        "count": 3,
        "observations": [
            {"date": "2022-11-01", "realtime_start": "2022-12-13", "value": "100.0"},
            {"date": "2022-12-01", "realtime_start": "2023-01-12", "value": "100.1"},
            {"date": "2023-01-01", "realtime_start": "2023-02-14", "value": "100.5"},
        ],
    }
    requested: list[dict[str, list[str]]] = []

    def fetch(_key: str, series_id: str, month: date, as_of: date) -> bytes:
        requested.append({"series": [series_id], "month": [str(month)], "as_of": [str(as_of)]})
        return json.dumps({"count": 1, "observations": [{"date": "x", "value": "100.2"}]}).encode()

    monkeypatch.setattr(sources, "fetch_cpi_releases", lambda _key, series_id: _dump(releases))
    monkeypatch.setattr(sources, "fetch_level_as_of", fetch)

    # when the core changes are loaded
    changes = load_first_published_changes("key", CORE_CPI_SERIES_ID)

    # then only January needed the revised December, asked for as of January's release day
    assert requested == [
        {"series": [CORE_CPI_SERIES_ID], "month": ["2022-12-01"], "as_of": ["2023-02-14"]}
    ]
    assert [round(change.percent, 3) for change in changes] == [0.1, round(0.3 / 100.2 * 100, 3)]


def test_the_level_request_asks_for_one_month_on_one_day(monkeypatch: pytest.MonkeyPatch) -> None:
    # given urlopen replaced by a stand-in that records the URL
    seen: list[str] = []

    class Reply:
        def __enter__(self) -> "Reply":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return b"{}"

    def answer(url: str, timeout: float) -> Reply:
        seen.append(url)
        return Reply()

    monkeypatch.setattr(sources.urllib.request, "urlopen", answer)

    # when December 2022 core is requested as of 2023-02-14
    sources.fetch_level_as_of("key", CORE_CPI_SERIES_ID, date(2022, 12, 1), date(2023, 2, 14))

    # then the request pins both the observation and the vintage to that month and that day
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(seen[0]).query)
    assert query["series_id"] == [CORE_CPI_SERIES_ID]
    assert query["observation_start"] == query["observation_end"] == ["2022-12-01"]
    assert query["realtime_start"] == query["realtime_end"] == ["2023-02-14"]


def _dump(document: dict[str, object]) -> bytes:
    return json.dumps(document).encode()


def test_each_measure_reads_its_own_fred_series() -> None:
    # given the two CPI measures step 4 uses
    # when their FRED series are looked up
    series = study.MEASURE_SERIES

    # then core is CPILFESL, and headline is CPIAUCSL, the series step 1 loads
    assert series == {"core": CORE_CPI_SERIES_ID, "headline": sources.CPI_SERIES_ID}
