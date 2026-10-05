"""Surprise: CPI's month-over-month change as first published, and how far it landed from expected."""

import json
import urllib.error
import urllib.parse
from datetime import date
from pathlib import Path
from typing import NoReturn

import duckdb
import pytest
from pydantic import SecretStr

from fortuneteller import db, sources, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import (
    ACTUAL,
    CORE,
    CORE_CPI_SERIES_ID,
    HEADLINE,
    NOWCAST,
    ClevelandError,
    CpiRelease,
    FredError,
    NowcastPoint,
    parse_level,
    parse_nowcasts,
)
from fortuneteller.models import EventInstance
from fortuneteller.study import (
    NOWCAST_BASELINE,
    MonthlyChange,
    actual_mismatches,
    build_surprises,
    first_published_changes,
    load_first_published_changes,
    nowcast_expectations,
    published_actuals,
    to_event_instance,
    trend_expectations,
)


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


NOWCAST_2022 = Path(__file__).parent / "data" / "cleveland_nowcast_2022.json"


def test_the_nowcast_file_becomes_dated_points_per_measure() -> None:
    # given the Cleveland Fed's file for August and December 2022
    payload = NOWCAST_2022.read_bytes()

    # when it is parsed
    points = parse_nowcasts(payload)

    # then each value has its full date, even where December's path runs into January
    assert (
        NowcastPoint(date(2022, 8, 1), CORE, ACTUAL, date(2022, 9, 13), 0.567267801202265) in points
    )
    assert (
        NowcastPoint(date(2022, 8, 1), CORE, NOWCAST, date(2022, 9, 12), 0.479891397462036)
        in points
    )
    assert (
        NowcastPoint(date(2022, 12, 1), CORE, ACTUAL, date(2023, 1, 12), 0.302600094645844)
        in points
    )
    assert {point.measure for point in points} == {CORE, HEADLINE}


@pytest.mark.parametrize(
    "payload",
    [b"<html>moved</html>", b'[{"chart": {}}]', b'[{"chart": {"subcaption": "2022-8"}}]'],
)
def test_a_nowcast_file_of_another_shape_is_refused(payload: bytes) -> None:
    # given a reply that is not the expected chart data
    # when / then it is refused with the source named
    with pytest.raises(ClevelandError):
        parse_nowcasts(payload)


def test_the_expected_value_is_the_last_nowcast_before_the_release_day() -> None:
    # given nowcasts for August 2022 made on Friday, Monday, and the Tuesday of the release
    august = date(2022, 8, 1)
    points = [
        NowcastPoint(august, CORE, NOWCAST, date(2022, 9, 9), 0.40),
        NowcastPoint(august, CORE, NOWCAST, date(2022, 9, 12), 0.45),
        NowcastPoint(august, CORE, NOWCAST, date(2022, 9, 13), 0.60),
    ]

    # when the expected value is taken for a Tuesday release, and for a Monday one
    tuesday = nowcast_expectations(points, {august: date(2022, 9, 13)})
    monday = nowcast_expectations(points, {august: date(2022, 9, 12)})

    # then it is the day before's nowcast, never one made on the release day itself
    assert tuesday == {(CORE, august): 0.45}
    assert monday == {(CORE, august): 0.40}


def test_the_real_file_gives_august_2022_s_expected_core_change() -> None:
    # given the Cleveland Fed's file and the August 2022 release day
    points = parse_nowcasts(NOWCAST_2022.read_bytes())

    # when the expected value is taken
    expected = nowcast_expectations(points, {date(2022, 8, 1): date(2022, 9, 13)})

    # then core was expected to rise 0.48%, against the 0.57% published
    assert expected[(CORE, date(2022, 8, 1))] == pytest.approx(0.479891397462036)


def test_a_month_without_a_nowcast_before_its_release_has_no_expected_value() -> None:
    # given the August 2022 nowcasts and a release date before the first of them
    points = parse_nowcasts(NOWCAST_2022.read_bytes())

    # when the expected value is taken
    expected = nowcast_expectations(points, {date(2022, 8, 1): date(2022, 7, 1)})

    # then there is none
    assert (CORE, date(2022, 8, 1)) not in expected


def test_changes_that_differ_from_cleveland_s_actual_are_named() -> None:
    # given Cleveland's published actuals and our changes, one of them off by 0.02 pp
    points = parse_nowcasts(NOWCAST_2022.read_bytes())
    ours = [
        MonthlyChange(date(2022, 8, 1), date(2022, 9, 13), 0.567267801202265 + 0.005),
        MonthlyChange(date(2022, 12, 1), date(2023, 1, 12), 0.302600094645844 + 0.02),
    ]

    # when they are compared within 0.01 pp
    mismatches = actual_mismatches(ours, published_actuals(points), CORE)

    # then only December is named
    assert mismatches == [date(2022, 12, 1)]


def test_the_nowcast_request_reports_a_failure_as_cleveland_s(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given a network that refuses the connection
    def refuse(*_args: object, **_kwargs: object) -> NoReturn:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(sources.urllib.request, "urlopen", refuse)

    # when / then the failure names the source
    with pytest.raises(ClevelandError, match="Cleveland Fed request failed"):
        sources.fetch_nowcasts()


def _changes(*percents: float, start: tuple[int, int] = (2021, 1)) -> list[MonthlyChange]:
    month, changes = date(*start, 1), []
    for percent in percents:
        changes.append(MonthlyChange(month, date(month.year, month.month, 28), percent))
        month = date(month.year + month.month // 12, month.month % 12 + 1, 1)
    return changes


def test_the_trend_is_the_average_of_the_previous_twelve_months() -> None:
    # given thirteen months of changes: 0.1 to 1.2, then 2.0
    changes = _changes(*(m / 10 for m in range(1, 13)), 2.0)

    # when the trend is computed
    trend = trend_expectations(changes)

    # then only the thirteenth month has a full year behind it, and expects its average
    assert trend == {date(2022, 1, 1): pytest.approx(0.65)}


def test_the_trend_averages_the_months_that_exist_around_a_gap() -> None:
    # given fourteen months of 0.2, with the eighth never published
    changes = [change for i, change in enumerate(_changes(*[0.2] * 14)) if i != 7]

    # when the trend is computed
    trend = trend_expectations(changes)

    # then the months whose year includes the gap still get a trend, from eleven values
    assert trend == {date(2022, 1, 1): pytest.approx(0.2), date(2022, 2, 1): pytest.approx(0.2)}


def _event(month: date, released: date) -> EventInstance:
    return to_event_instance(CpiRelease(month, released, 100.0))


def test_a_surprise_row_is_actual_minus_expected_for_its_release() -> None:
    # given August 2022 core, released 2022-09-13, and a nowcast of 0.48 made the day before
    august, released = date(2022, 8, 1), date(2022, 9, 13)
    changes = {CORE: [MonthlyChange(august, released, 0.57)]}
    points = [NowcastPoint(august, CORE, NOWCAST, date(2022, 9, 12), 0.48)]

    # when the surprises are built against the stored release
    rows = build_surprises([_event(august, released)], changes, points)

    # then there is one nowcast row, too early in history for a trend, 0.09 pp hot
    assert [(r.event_id, r.measure, r.baseline, r.actual_mom, r.expected_mom) for r in rows] == [
        (202208, CORE, NOWCAST_BASELINE, 0.57, 0.48)
    ]
    assert rows[0].surprise == pytest.approx(0.09)


def test_a_change_released_on_another_day_than_its_stored_release_is_refused() -> None:
    # given a core change released a day after the stored CPI release
    august = date(2022, 8, 1)
    changes = {CORE: [MonthlyChange(august, date(2022, 9, 14), 0.57)]}

    # when / then the surprises are refused rather than paired with the wrong day
    with pytest.raises(ValueError, match="2022-08"):
        build_surprises([_event(august, date(2022, 9, 13))], changes, [])


def test_a_change_without_a_stored_release_asks_for_the_releases() -> None:
    # given a change for a month whose release is not stored
    changes = {CORE: [MonthlyChange(date(2022, 8, 1), date(2022, 9, 13), 0.57)]}

    # when / then the message says which load to run
    with pytest.raises(ValueError, match="load-releases"):
        build_surprises([], changes, [])


def _nowcast_file(month: str, actual_core: float) -> bytes:
    # One Cleveland record: a core nowcast on 09/12 and the published core change on 09/13.
    record = {
        "chart": {"subcaption": month},
        "categories": [{"category": [{"label": "09/12"}, {"label": "09/13"}]}],
        "dataset": [
            {"seriesname": "Core CPI Inflation", "data": [{"value": "0.48"}, {"value": ""}]},
            {
                "seriesname": "Actual Core CPI Inflation",
                "data": [{"value": ""}, {"value": str(actual_core)}],
            },
        ],
    }
    return json.dumps([record]).encode()


def _sources_answer(monkeypatch: pytest.MonkeyPatch, actual_core: float) -> None:
    # Core: 0.2% a month through 2022-07, then a hot 0.57% August, released 2022-09-13.
    changes = [
        MonthlyChange(change.reference_month, released_on(change.reference_month), change.percent)
        for change in _changes(*[0.2] * 19, 0.57, start=(2021, 1))
    ]

    def load(_key: str, series_id: str) -> list[MonthlyChange]:
        return changes if series_id == CORE_CPI_SERIES_ID else []

    monkeypatch.setattr(study, "load_first_published_changes", load)
    monkeypatch.setattr(sources, "fetch_nowcasts", lambda: _nowcast_file("2022-8", actual_core))


def released_on(month: date) -> date:
    following = date(month.year + month.month // 12, month.month % 12 + 1, 13)
    while following.weekday() >= 5:
        following = date(following.year, following.month, following.day + 1)
    return following


def _store_events(con: duckdb.DuckDBPyConnection) -> None:
    months = [change.reference_month for change in _changes(*[0.0] * 20, start=(2021, 1))]
    study.store_cpi_releases([CpiRelease(m, released_on(m), 100.0) for m in months], con=con)


def test_loading_stores_each_surprise_once_however_often_it_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given 20 stored releases, their core changes, and Cleveland agreeing on August 2022
    _sources_answer(monkeypatch, actual_core=0.57)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _store_events(con)

    # when the surprises are loaded twice
    study.load_surprises("key", con=con)
    rows = study.load_surprises("key", con=con)

    # then the eight months with a year behind them have a trend row, August a nowcast row too
    assert db.count_rows("cpi_surprises", con=con) == len(rows) == 9
    august = con.execute(
        "SELECT baseline, surprise FROM cpi_surprises WHERE event_id = 202208 ORDER BY baseline"
    ).fetchall()
    assert august == [
        (NOWCAST_BASELINE, pytest.approx(0.09)),
        (study.TREND_12M, pytest.approx(0.37)),
    ]


def test_loading_refuses_when_a_change_differs_from_cleveland_s(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given Cleveland publishing August 2022 core 0.05 pp away from ours
    _sources_answer(monkeypatch, actual_core=0.62)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _store_events(con)

    # when / then nothing is stored, and the month is named
    with pytest.raises(ValueError, match="core: .* 2022-08"):
        study.load_surprises("key", con=con)
    assert db.count_rows("cpi_surprises", con=con) == 0


def test_loading_needs_the_releases_first() -> None:
    # given an empty store
    con = duckdb.connect(":memory:")
    db.init_db(con=con)

    # when / then the message says which load to run
    with pytest.raises(ValueError, match="load-releases"):
        study.load_surprises("key", con=con)


def test_load_surprises_prints_a_line_per_measure_and_baseline(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given stored releases, a FRED key, and the sources answering
    _sources_answer(monkeypatch, actual_core=0.57)
    _store_events(db.get_connection())
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))

    # when the command runs
    code = main(["load-surprises"])

    # then it reports how many surprises each measure has against each expected value
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out == [
        "core      trend_12m    8 surprises, 2022-01 … 2022-08",
        "core      nowcast      1 surprises, 2022-08 … 2022-08",
    ]


def test_load_surprises_reports_a_refusal_on_one_line(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a FRED key and an empty store
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))

    # when the command runs
    code = main(["load-surprises"])

    # then it stops with one line naming the load to run first
    assert code == 1
    assert "run `fortuneteller load-releases` first" in capsys.readouterr().err
