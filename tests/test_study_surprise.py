"""Surprise: CPI's month-over-month change as first published, and how far it landed from expected."""

import json
import random
import urllib.error
import urllib.parse
from datetime import date
from pathlib import Path
from typing import NoReturn

import duckdb
import pytest
from pydantic import SecretStr

from fortuneteller import db, flows, sources, study
from fortuneteller.__main__ import describe_surprise_tracking, main
from fortuneteller.config import settings
from fortuneteller.sources import (
    ACTUAL,
    CORE,
    CORE_CPI_SERIES_ID,
    HEADLINE,
    NOWCAST,
    ClevelandError,
    FirstRelease,
    FredError,
    NowcastPoint,
    parse_level,
    parse_nowcasts,
)
from fortuneteller.expectations import (
    NOWCAST_BASELINE,
    TREND_12M,
    Actual,
    Expectation,
    Trend12m,
    build_surprises,
    end_of_day,
    event_month,
    nowcast_expectations,
)
from fortuneteller.models import Surprise, EventInstance
from fortuneteller.flows import (
    CPI_EVENT_TYPE,
    CPI_FLOW,
    PERCENT,
    MonthlyChange,
    actual_mismatches,
    first_published_changes,
    load_first_published_changes,
    published_actuals,
    to_actuals,
    to_event_instance,
)
from fortuneteller.study import (
    DOESNT_TRACK,
    TRACKS,
    SurpriseTracking,
    UNCLEAR,
    track_pairs,
    track_verdict,
)


def _release(month: tuple[int, int], released: tuple[int, int, int], level: float) -> FirstRelease:
    return FirstRelease(date(*month, 1), date(*released), level)


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
    assert changes[0].change == pytest.approx((100.5 / 100.2 - 1) * 100)


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

    monkeypatch.setattr(sources, "fetch_first_releases", lambda _key, series_id: _dump(releases))
    monkeypatch.setattr(sources, "fetch_level_as_of", fetch)

    # when the core changes are loaded
    changes = load_first_published_changes("key", CORE_CPI_SERIES_ID)

    # then only January needed the revised December, asked for as of January's release day
    assert requested == [
        {"series": [CORE_CPI_SERIES_ID], "month": ["2022-12-01"], "as_of": ["2023-02-14"]}
    ]
    assert [round(change.change, 3) for change in changes] == [0.1, round(0.3 / 100.2 * 100, 3)]


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
    series = flows.MEASURE_SERIES

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
    assert tuesday == {(CORE, august): (date(2022, 9, 12), 0.45)}
    assert monday == {(CORE, august): (date(2022, 9, 9), 0.40)}


def test_the_real_file_gives_august_2022_s_expected_core_change() -> None:
    # given the Cleveland Fed's file and the August 2022 release day
    points = parse_nowcasts(NOWCAST_2022.read_bytes())

    # when the expected value is taken
    expected = nowcast_expectations(points, {date(2022, 8, 1): date(2022, 9, 13)})

    # then core was expected to rise 0.48%, against the 0.57% published
    assert expected[(CORE, date(2022, 8, 1))][1] == pytest.approx(0.479891397462036)


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


def trend_expectations(changes: list[MonthlyChange]) -> dict[date, float]:
    events = [_event(change.reference_month, change.released) for change in changes]
    actuals = to_actuals(changes, CPI_FLOW, CORE, PERCENT, events)
    months = {event.event_id: event_month(event) for event in events}
    return {
        months[expectation.event_id]: expectation.value
        for expectation in Trend12m().expectations(events, actuals, "key")
    }


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
    return to_event_instance(FirstRelease(month, released, 100.0), CPI_FLOW)


def test_a_surprise_row_is_actual_minus_expected_for_its_release() -> None:
    # given August 2022 core, released 2022-09-13, and a nowcast of 0.48 made the day before
    august, released = date(2022, 8, 1), date(2022, 9, 13)
    event = _event(august, released)
    actual = Actual(event.event_id, CORE, august, 0.57, PERCENT)
    nowcast = Expectation(
        event.event_id, CORE, NOWCAST_BASELINE, 0.48, PERCENT, end_of_day(date(2022, 9, 12))
    )

    # when the surprises are built against the stored release
    rows = build_surprises([event], [actual], [nowcast], [CPI_EVENT_TYPE])

    # then there is one nowcast row, 0.09 pp hot
    assert [(r.event_id, r.measure, r.baseline, r.actual_mom, r.expected_mom) for r in rows] == [
        (1_2022_09_13, CORE, NOWCAST_BASELINE, 0.57, 0.48)
    ]
    assert rows[0].surprise == pytest.approx(0.09)


def _refusal(**changed: object) -> str:
    august = date(2022, 8, 1)
    event = _event(august, date(2022, 9, 13))
    actual = Actual(event.event_id, CORE, august, 0.57, PERCENT)
    fields: dict[str, object] = {
        "event_id": event.event_id,
        "measure": CORE,
        "source": NOWCAST_BASELINE,
        "value": 0.48,
        "unit": PERCENT,
        "known_at": end_of_day(date(2022, 9, 12)),
    }
    fields.update(changed)
    with pytest.raises(ValueError) as refused:
        build_surprises([event], [actual], [Expectation(**fields)], [CPI_EVENT_TYPE])
    return str(refused.value)


@pytest.mark.parametrize(
    ("changed", "reason"),
    [
        ({"event_id": 1_2022_09_14}, "no stored event with a surprise"),
        ({"measure": "headline"}, "no actual for headline"),
        ({"unit": "thousands"}, "in thousands, the actual in percent"),
        ({"known_at": end_of_day(date(2022, 9, 13))}, "not before the event"),
    ],
)
def test_an_expectation_that_does_not_fit_its_event_is_refused(
    changed: dict[str, object], reason: str
) -> None:
    # given August 2022's release and actual, and a nowcast broken in exactly one way

    # when / then the surprises are refused with that reason
    assert reason in _refusal(**changed)


def test_an_expectation_for_an_event_without_a_surprise_is_refused() -> None:
    # given August 2022's release stored, but its type not among those with a surprise
    august = date(2022, 8, 1)
    event = _event(august, date(2022, 9, 13))
    actual = Actual(event.event_id, CORE, august, 0.57, PERCENT)
    nowcast = Expectation(
        event.event_id, CORE, NOWCAST_BASELINE, 0.48, PERCENT, end_of_day(date(2022, 9, 12))
    )

    # when / then it is refused
    with pytest.raises(ValueError, match="no stored event with a surprise"):
        build_surprises([event], [actual], [nowcast], [])


def test_a_change_released_on_another_day_than_its_stored_release_is_refused() -> None:
    # given a core change released a day after the stored CPI release
    august = date(2022, 8, 1)
    changes = [MonthlyChange(august, date(2022, 9, 14), 0.57)]

    # when / then the actuals are refused rather than paired with the wrong day
    with pytest.raises(ValueError, match="2022-08"):
        to_actuals(changes, CPI_FLOW, CORE, PERCENT, [_event(august, date(2022, 9, 13))])


def test_a_change_without_a_stored_release_asks_for_the_releases() -> None:
    # given a change for a month whose release is not stored
    changes = [MonthlyChange(date(2022, 8, 1), date(2022, 9, 13), 0.57)]

    # when / then the message says which load to run
    with pytest.raises(ValueError, match="load-releases"):
        to_actuals(changes, CPI_FLOW, CORE, PERCENT, [])


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
        MonthlyChange(change.reference_month, released_on(change.reference_month), change.change)
        for change in _changes(*[0.2] * 19, 0.57, start=(2021, 1))
    ]

    def load(_key: str, series_id: str) -> list[MonthlyChange]:
        return changes if series_id == CORE_CPI_SERIES_ID else []

    monkeypatch.setattr(flows, "load_first_published_changes", load)
    monkeypatch.setattr(sources, "fetch_nowcasts", lambda: _nowcast_file("2022-8", actual_core))


def released_on(month: date) -> date:
    following = date(month.year + month.month // 12, month.month % 12 + 1, 13)
    while following.weekday() >= 5:
        following = date(following.year, following.month, following.day + 1)
    return following


def _store_events(con: duckdb.DuckDBPyConnection) -> None:
    months = [change.reference_month for change in _changes(*[0.0] * 20, start=(2021, 1))]
    flows.store_releases(
        CPI_FLOW, [FirstRelease(m, released_on(m), 100.0) for m in months], con=con
    )


def test_loading_stores_each_surprise_once_however_often_it_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given 20 stored releases, their core changes, and Cleveland agreeing on August 2022
    _sources_answer(monkeypatch, actual_core=0.57)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _store_events(con)

    # when the surprises are loaded twice
    flows.load_surprises("key", con=con)
    rows = flows.load_surprises("key", con=con)

    # then the eight months with a year behind them have a trend row, August a nowcast row too
    assert db.count_rows("surprises", con=con) == len(rows) == 9
    august = con.execute(
        "SELECT baseline, surprise FROM surprises WHERE event_id = 120220913 ORDER BY baseline"
    ).fetchall()
    assert august == [
        (NOWCAST_BASELINE, pytest.approx(0.09)),
        (TREND_12M, pytest.approx(0.37)),
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
        flows.load_surprises("key", con=con)
    assert db.count_rows("surprises", con=con) == 0


def test_loading_needs_the_releases_first() -> None:
    # given an empty store
    con = duckdb.connect(":memory:")
    db.init_db(con=con)

    # when / then the message says which load to run
    with pytest.raises(ValueError, match="load-releases"):
        flows.load_surprises("key", con=con)


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
        "core      trend_12m    8 surprises, released 2022-02-14 … 2022-09-13",
        "core      nowcast      1 surprises, released 2022-09-13 … 2022-09-13",
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


@pytest.mark.parametrize(
    ("p", "hit_rate", "expected"),
    [
        (0.009, 0.60, TRACKS),
        (0.009, 0.59, UNCLEAR),
        (0.01, 0.75, UNCLEAR),
        (0.20, 0.50, DOESNT_TRACK),
        (0.0001, None, UNCLEAR),
    ],
)
def test_tracking_needs_significance_and_a_hit_rate(
    p: float, hit_rate: float | None, expected: str
) -> None:
    # given a p-value and a hit rate (None for gold, which has no expected direction)
    # when the verdict is read
    result = track_verdict(p, hit_rate)

    # then "tracks" needs both, "unclear" one, "doesn't" neither; gold can reach "unclear" at most
    assert result == expected


def _planted(slope: float, seed: int, n: int = 300) -> tuple[list[float], list[float]]:
    rng = random.Random(seed)
    surprises = [rng.gauss(0, 0.15) for _ in range(n)]
    return surprises, [slope * s + rng.gauss(0, 0.3) for s in surprises]


def test_a_move_built_from_the_surprise_tracks_it() -> None:
    # given moves built as 3 x surprise plus noise, for an instrument expected to rise
    surprises, moves = _planted(3.0, seed=1)

    # when the pairs are measured
    result = track_pairs(surprises, moves, expected_sign=1, judged=True, step=0.1)

    # then the relation is found, its slope is about 0.3 per 0.1 pp, and the verdict is "tracks"
    assert result.verdict == TRACKS
    assert result.rank_corr > 0.5
    assert result.slope == pytest.approx(0.3, rel=0.2)
    assert result.n == 300


def test_the_same_moves_shuffled_do_not_track() -> None:
    # given the planted moves, shuffled across releases
    surprises, moves = _planted(3.0, seed=1)
    random.Random(7).shuffle(moves)

    # when the pairs are measured
    result = track_pairs(surprises, moves, expected_sign=1, judged=True, step=0.1)

    # then nothing is found
    assert result.verdict != TRACKS
    assert result.p > 0.01


def test_a_fall_tracks_where_a_fall_is_expected() -> None:
    # given moves that fall with the surprise, for an instrument expected to fall (the S&P 500)
    surprises, moves = _planted(-3.0, seed=2)

    # when the pairs are measured
    result = track_pairs(surprises, moves, expected_sign=-1, judged=True, step=0.1)

    # then it tracks, and the correlation reads positive: "as expected"
    assert result.verdict == TRACKS
    assert result.rank_corr > 0.5


def test_the_hit_rate_counts_only_noticeable_surprises() -> None:
    # given two small surprises that went the wrong way, and two noticeable ones that went right
    surprises, moves = [0.05, -0.05, 0.2, -0.3], [-1.0, 1.0, 1.0, -1.0]

    # when the pairs are measured
    result = track_pairs(surprises, moves, expected_sign=1, judged=False, step=0.1)

    # then the hit rate is 2 of 2, and context rows carry no verdict
    assert (result.hit_rate, result.hit_n) == (1.0, 2)
    assert result.verdict is None


def test_without_an_expected_direction_there_is_no_hit_rate() -> None:
    # given gold, with no agreed direction
    surprises, moves = _planted(-3.0, seed=3)

    # when the pairs are measured
    result = track_pairs(surprises, moves, expected_sign=0, judged=True, step=0.1)

    # then the two-sided test finds the relation, but with no hit rate it is only "unclear"
    assert result.hit_rate is None
    assert result.p < 0.01
    assert result.verdict == UNCLEAR


def test_measuring_twice_gives_the_same_result() -> None:
    # given one set of pairs
    surprises, moves = _planted(1.0, seed=4)

    # when they are measured twice
    first = track_pairs(surprises, moves, expected_sign=1, judged=True, step=0.1)
    second = track_pairs(surprises, moves, expected_sign=1, judged=True, step=0.1)

    # then the results are identical
    assert first == second


def test_each_instrument_is_measured_against_each_measure_and_baseline() -> None:
    # given stored surprises and moves for one release
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    month = date(2022, 8, 1)
    flows.store_releases(CPI_FLOW, [FirstRelease(month, date(2022, 9, 13), 100.0)], con=con)
    surprises = [
        Surprise(
            event_id=1_2022_09_13,
            measure=m,
            baseline=b,
            actual_mom=0.5,
            expected_mom=0.4,
            surprise=0.1,
        )
        for m in (CORE, HEADLINE)
        for b in (TREND_12M, NOWCAST_BASELINE)
    ]
    db.insert_models("surprises", surprises, con=con)
    con.execute(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
        "SELECT 120220913, unnest(?), 'pct', 0.01",
        [list(study.MVP_PRICE_SERIES)],
    )

    # when the pairs are gathered
    pairs = study.surprise_pairs(flows.COMBINATIONS, con=con)

    # then core against the trend comes first, and every instrument has its one pair
    assert list(pairs)[0] == (CORE, TREND_12M)
    assert len(pairs) == 4
    assert all(p == ([0.1], [0.01]) for by in pairs.values() for p in by.values())


def test_the_report_shows_the_verdict_table_then_the_context_and_the_rule() -> None:
    # given one verdict row per unit, a gold row without a hit rate, and one context row
    yield_row = SurpriseTracking(342, 0.21, 0.0001, 0.64, 180, 1.2, TRACKS)
    tracked = SurpriseTracking(342, 0.21, 0.0001, 0.64, 180, 0.012, TRACKS)
    gold = SurpriseTracking(311, 0.05, 0.4, None, 0, -0.0003, DOESNT_TRACK)
    context = SurpriseTracking(155, 0.30, 0.0002, 0.7, 60, 0.002, None)
    results = {
        (CORE, TREND_12M): {"UST10Y / ZN": yield_row, "SPY / ES": tracked, "GC / XAU": gold},
        (CORE, NOWCAST_BASELINE): {"DXY": context},
    }

    # when the report is written
    lines = describe_surprise_tracking(results, flows.CPI_SURPRISE_RULE)

    # then units, expected directions and the missing hit rate read plainly
    assert lines[:5] == [
        "core against the 12-month trend",
        "instrument   n    expected  rank corr  p       hit rate (n)  per 0.1pp  verdict",
        "UST10Y / ZN  342  up        0.21       0.0001  64% (180)     1.2 bp     tracks",
        "SPY / ES     342  down      0.21       0.0001  64% (180)     1.20%      tracks",
        "GC / XAU     311  either    0.05       0.4000  —             -0.03%     doesn't",
    ]
    assert "DXY          core      nowcast    155  0.30       0.0002  70% (60)" in lines
    assert lines[-1].startswith("tracks = corr as expected, p < 0.01, hit rate >= 60%")


def _store_tracking_data(con: duckdb.DuckDBPyConnection) -> None:
    # 40 releases; each instrument's move is 0.01 x its expected sign x the core surprise, plus noise.
    rng = random.Random(9)
    months = [change.reference_month for change in _changes(*[0.0] * 40, start=(2020, 1))]
    flows.store_releases(
        CPI_FLOW, [FirstRelease(m, released_on(m), 100.0) for m in months], con=con
    )
    surprises, observations = [], []
    for m in months:
        event_id = flows.event_id(flows.CPI_FLOW, released_on(m))
        surprise = rng.gauss(0, 0.2)
        surprises += [
            Surprise(
                event_id=event_id,
                measure=measure,
                baseline=baseline,
                actual_mom=0.3,
                expected_mom=0.3 - surprise,
                surprise=surprise,
            )
            for measure, baseline in flows.COMBINATIONS
        ]
        for instrument in study.MVP_PRICE_SERIES:
            sign = flows.EXPECTED_SIGN[instrument] or 1
            move = 0.01 * sign * surprise + rng.gauss(0, 0.0005)
            observations.append((event_id, instrument, move))
    db.insert_models("surprises", surprises, con=con)
    con.executemany(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'pct', ?)",
        observations,
    )


def test_surprise_prints_a_verdict_per_instrument_and_the_context(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given releases, moves and surprises stored, every move following the surprise
    _store_tracking_data(db.get_connection())

    # when the command runs
    code = main(["surprise"])

    # then four instruments track, gold is unclear at most, and every context row is printed
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert sum(line.endswith(" tracks") for line in out) == 4
    assert sum(" nowcast " in line or " trend_12m " in line for line in out) == 15


@pytest.mark.parametrize(
    ("stored", "missing"),
    [(0, "load-releases"), (1, "load-prices"), (2, "load-surprises")],
)
def test_surprise_names_the_load_to_run_first(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], stored: int, missing: str
) -> None:
    # given a store missing releases, prices, or surprises
    con = db.get_connection()
    if stored >= 1:
        flows.store_releases(
            CPI_FLOW, [FirstRelease(date(2022, 8, 1), date(2022, 9, 13), 100.0)], con=con
        )
    if stored >= 2:
        con.execute(
            "INSERT INTO observations (event_id, instrument, ret_1d) VALUES (120220913, 'DXY', 0.0)"
        )

    # when the command runs
    code = main(["surprise"])

    # then it stops with one line naming the command to run first
    assert code == 1
    assert f"`fortuneteller {missing}` first" in capsys.readouterr().err


def _jobs_answer(monkeypatch: pytest.MonkeyPatch, months: list[date]) -> list[FirstRelease]:
    # Payrolls rise by 100k every month, each printed on the 5th of the next and never revised.
    releases = [
        FirstRelease(m, date(m.year + m.month // 12, m.month % 12 + 1, 5), 1000.0 + 100 * i)
        for i, m in enumerate(months)
    ]
    rows = []
    for i, release in enumerate(releases):
        row = {"date": release.reference_month.isoformat()}
        row[f"PAYEMS_{release.released:%Y%m%d}"] = str(release.value)
        if i + 1 < len(releases):
            row[f"PAYEMS_{releases[i + 1].released:%Y%m%d}"] = str(release.value)
        rows.append(row)
    payload = json.dumps({"count": len(rows), "observations": rows}).encode()
    monkeypatch.setattr(sources, "fetch_vintages", lambda _key, _series: payload)
    return releases


def test_loading_adds_payroll_surprises_when_jobs_reports_are_stored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the CPI setup, and 15 stored jobs reports rising 100k a month
    _sources_answer(monkeypatch, actual_core=0.57)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _store_events(con)
    months = [date(2021 + i // 12, i % 12 + 1, 1) for i in range(15)]
    flows.store_releases(flows.NFP_FLOW, _jobs_answer(monkeypatch, months), con=con)

    # when the surprises are loaded
    flows.load_surprises("key", con=con)

    # then the two months with a full year behind them were exactly on trend
    payrolls = con.execute(
        "SELECT actual_mom, expected_mom, surprise FROM surprises WHERE measure = 'payrolls'"
    ).fetchall()
    assert payrolls == [(100.0, 100.0, 0.0), (100.0, 100.0, 0.0)]


def test_loading_refuses_a_jobs_report_stored_unlike_fred_s_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the CPI setup, and March 2021's jobs report stored 1k off what FRED first printed
    _sources_answer(monkeypatch, actual_core=0.57)
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _store_events(con)
    months = [date(2021 + i // 12, i % 12 + 1, 1) for i in range(15)]
    releases = _jobs_answer(monkeypatch, months)
    releases[2] = FirstRelease(releases[2].reference_month, releases[2].released, 1201.0)
    flows.store_releases(flows.NFP_FLOW, releases, con=con)

    # when / then nothing is stored, and the month is named
    with pytest.raises(ValueError, match="payrolls: .* 2021-03"):
        flows.load_surprises("key", con=con)
    assert db.count_rows("surprises", con=con) == 0


def test_surprise_refuses_the_fed(tmp_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # given nothing stored

    # when the Fed's surprise is asked for
    code = main(["surprise", "--event", "fomc"])

    # then it is refused with the reason: no free record of what the market expected
    assert code == 1
    assert "no surprise" in capsys.readouterr().err


def test_surprise_for_jobs_asks_for_its_surprises_first(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given CPI's tracking data stored, but no payroll surprises
    _store_tracking_data(db.get_connection())

    # when the jobs report's tracking is asked for
    code = main(["surprise", "--event", "nfp"])

    # then it says which load to run instead of printing an empty table
    assert code == 1
    assert "nfp" in capsys.readouterr().err


def test_the_jobs_report_has_its_own_signs_cut_off_and_no_context_table() -> None:
    # given one tracked yield row
    row = SurpriseTracking(400, 0.2, 0.0001, 0.65, 300, 1.5, TRACKS)

    # when the jobs report's tracking is written
    lines = describe_surprise_tracking(
        {(flows.PAYROLLS, TREND_12M): {"UST10Y / ZN": row}}, flows.NFP_SURPRISE_RULE
    )

    # then it is payrolls against the trend, per 50k, and the rule follows straight after
    assert lines[:3] == [
        "payrolls against the 12-month trend",
        "instrument   n    expected  rank corr  p       hit rate (n)  per 50k    verdict",
        "UST10Y / ZN  400  up        0.20       0.0001  65% (300)     1.5 bp     tracks",
    ]
    assert "context, no verdict" not in lines
