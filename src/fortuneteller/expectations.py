"""Expected values and surprises (docs/steps/event-flows.md).

An event flow gives each event's ``Actual`` per measure; every ``ExpectationSource`` gives its
``Expectation`` for some of them; ``build_surprises`` checks each expectation against its event and
actual, then stores ``actual − expected``. A new source is one class and one line in
``EXPECTATION_SOURCES``. Nothing here knows which event types exist.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from . import sources, stats
from .models import EventInstance, Surprise
from .sources import NEW_YORK, PAYROLLS


@dataclass(frozen=True)
class Actual:
    """One measure as first published in an event: CPI's change in percent, payrolls' in thousands.

    ``period`` is the month measured. It is the event's own month, except for a month first
    published in a later month's release (October 2025 payrolls, with November): that one feeds the
    trend but gets no surprise of its own.
    """

    event_id: int
    measure: str
    period: date
    value: float
    unit: str


@dataclass(frozen=True)
class Expectation:
    """What ``source`` expected ``measure`` to be in an event, and when that was known (naive UTC)."""

    event_id: int
    measure: str
    source: str
    value: float
    unit: str
    known_at: datetime


class ExpectationSource(Protocol):
    name: str
    label: str

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]: ...


def previous_month(month: date) -> date:
    return date(month.year - 1, 12, 1) if month.month == 1 else date(month.year, month.month - 1, 1)


@dataclass(frozen=True)
class MonthlyChange:
    """One month's change as first published: CPI in percent (``0.4`` is +0.4%), payrolls in
    thousands of jobs."""

    reference_month: date
    released: date
    change: float


def first_published_payroll_changes(
    vintages: Mapping[date, Mapping[date, float]], since: date
) -> list[MonthlyChange]:
    """Each month's payroll change as BLS first published it, from ``since`` on, oldest first.

    Payrolls revise the two months before in every release, so the change is the month's first
    level minus the previous month's level as it stood that same day, revised or not.
    """
    changes: list[MonthlyChange] = []
    for month in sorted(vintages):
        levels = vintages[month]
        earlier = vintages.get(previous_month(month), {})
        if month < since or not levels:
            continue
        released = min(levels)
        known = [day for day in earlier if day <= released]
        if not known:
            continue
        changes.append(MonthlyChange(month, released, levels[released] - earlier[max(known)]))
    return changes


# The jobs-report forecast's inputs (docs/steps/nfp-forecast.md), each as first published.

# ADP's private payrolls on FRED, read in thousands of jobs: the old method to May 2022, the new one
# from September 2022, with ADP paused in between.
ADP_SERIES = (("NPPTTL", 1.0), ("ADPMNUSNERSA", 0.001))
# ADP's first print comes 20 to 45 days after its month starts. A month first seen later is history
# republished (at the start of FRED's record in 2011, at the relaunch in 2022): nobody had it in time.
ADP_FIRST_PRINT_DAYS = 50
CLAIMS_SERIES = "IC4WSA"


def adp_changes(
    vintages: Mapping[str, Mapping[date, Mapping[date, float]]],
) -> dict[date, MonthlyChange]:
    """ADP's change for each month, in thousands, as first published in time for its jobs report."""
    changes: dict[date, MonthlyChange] = {}
    for series_id, scale in ADP_SERIES:
        for change in first_published_payroll_changes(vintages[series_id], date.min):
            if (change.released - change.reference_month).days <= ADP_FIRST_PRINT_DAYS:
                changes[change.reference_month] = MonthlyChange(
                    change.reference_month, change.released, change.change * scale
                )
    return changes


def survey_week(month: date) -> date:
    """The last day (a Saturday) of the week that includes the 12th: the jobs report's survey week."""
    twelfth = month.replace(day=12)
    return twelfth + timedelta(days=(5 - twelfth.weekday()) % 7)


def claims_changes(first_prints: Iterable[sources.FirstRelease]) -> dict[date, MonthlyChange]:
    """For each month, the change in 4-week-average initial claims, in thousands, from the previous
    month's survey week to its own, both as first printed; known when the month's week came out.

    ``first_prints`` are FRED first releases keyed by each week's last day.
    """
    weeks = {release.reference_month: release for release in first_prints}
    changes: dict[date, MonthlyChange] = {}
    for week, release in weeks.items():
        month = week.replace(day=1)
        earlier = weeks.get(survey_week(previous_month(month)))
        if survey_week(month) == week and earlier is not None:
            change = (release.value - earlier.value) / 1000
            changes[month] = MonthlyChange(month, release.released, change)
    return changes


def load_model_inputs(api_key: str) -> tuple[dict[date, MonthlyChange], dict[date, MonthlyChange]]:
    """ADP's and the claims' monthly changes from FRED, each as first published."""
    vintages = {
        series_id: sources.parse_vintages(sources.fetch_vintages(api_key, series_id), series_id)
        for series_id, _scale in ADP_SERIES
    }
    payload = sources.fetch_first_releases(api_key, series_id=CLAIMS_SERIES)
    weeks, _valueless = sources.parse_first_releases(payload, CLAIMS_SERIES)
    return adp_changes(vintages), claims_changes(weeks)


def event_month(event: EventInstance) -> date:
    """The month an event measures: its ``detail``, ``YYYY-MM``."""
    return date.fromisoformat(f"{event.detail}-01")


def own_actuals(events: Iterable[EventInstance], actuals: Iterable[Actual]) -> list[Actual]:
    """The actuals that are their event's own month: the ones a surprise can be built for."""
    months = {event.event_id: event_month(event) for event in events}
    return [actual for actual in actuals if months.get(actual.event_id) == actual.period]


TREND_12M = "trend_12m"
TREND_MONTHS = 12


class Trend12m:
    """The average of the previous 12 months' first-published values, for any measure, within one
    event type from one country: UK CPI's core never enters US CPI's trend.

    Only months announced before the event count, so the trend uses only what was known then:
    October 2025 payrolls, published with November, are not in November's. A month gets a trend
    once a full year of history lies behind it; a month missing inside the year is skipped, and the
    rest are averaged.
    """

    name = TREND_12M
    label = "the 12-month trend"

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        announced = {event.event_id: event.event_ts for event in events}
        origin = {event.event_id: (event.event_type, event.country) for event in events}
        expected: list[Expectation] = []
        for group in dict.fromkeys((origin[a.event_id], a.measure) for a in actuals):
            _origin, measure = group
            by_period = {a.period: a for a in actuals if (origin[a.event_id], a.measure) == group}
            first = min(by_period)
            for actual in own_actuals(events, by_period.values()):
                window = [actual.period]
                for _ in range(TREND_MONTHS):
                    window.append(previous_month(window[-1]))
                if window[-1] < first:
                    continue
                at = announced[actual.event_id]
                known = [
                    by_period[m]
                    for m in window[1:]
                    if m in by_period and announced[by_period[m].event_id] < at
                ]
                if known:
                    expected.append(
                        Expectation(
                            actual.event_id,
                            measure,
                            self.name,
                            sum(k.value for k in known) / len(known),
                            actual.unit,
                            max(announced[k.event_id] for k in known),
                        )
                    )
        return expected


NOWCAST_BASELINE = "nowcast"


def nowcast_expectations(
    points: Iterable[sources.NowcastPoint], release_dates: Mapping[date, date]
) -> dict[tuple[str, date], tuple[date, float]]:
    """The last nowcast made before each month's release day, with its day, keyed by (measure,
    month).

    A nowcast made on the release day itself may already know the number, so it is never used.
    """
    latest: dict[tuple[str, date], tuple[date, float]] = {}
    for point in points:
        released = release_dates.get(point.reference_month)
        if point.kind != sources.NOWCAST or released is None or point.day >= released:
            continue
        key = (point.measure, point.reference_month)
        if key not in latest or point.day > latest[key][0]:
            latest[key] = (point.day, point.percent)
    return latest


def end_of_day(day: date, zone: ZoneInfo) -> datetime:
    """The last second of a day in ``zone``, as naive UTC: when a day-only value was surely known."""
    return datetime.combine(day, time(23, 59, 59), tzinfo=zone).astimezone(UTC).replace(tzinfo=None)


class ClevelandNowcast:
    """The Cleveland Fed's CPI nowcast: the last one made before the release day, 2013 on."""

    name = NOWCAST_BASELINE
    label = "the Cleveland Fed's nowcast"
    zone = NEW_YORK

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        measures = {sources.CORE, sources.HEADLINE}
        wanted = [a for a in own_actuals(events, actuals) if a.measure in measures]
        if not wanted:
            return []
        by_id = {event.event_id: event for event in events}
        release_dates = {
            actual.period: by_id[actual.event_id]
            .event_ts.replace(tzinfo=UTC)
            .astimezone(self.zone)
            .date()
            for actual in wanted
        }
        latest = nowcast_expectations(
            sources.parse_nowcasts(sources.fetch_nowcasts()), release_dates
        )
        return [
            Expectation(
                actual.event_id,
                actual.measure,
                self.name,
                value,
                actual.unit,
                end_of_day(day, self.zone),
            )
            for actual in wanted
            if (key := (actual.measure, actual.period)) in latest
            for day, value in [latest[key]]
        ]


PAYROLL_MODEL = "payroll_model"
# A fit needs this many earlier reports with every input (docs/steps/nfp-forecast.md).
MODEL_MIN_REPORTS = 36
# COVID's prints (April 2020: −20.5M) would dominate every later fit: these months are not fitted
# on, though their reports are still forecast.
COVID_MONTHS = (date(2020, 3, 1), date(2021, 4, 1))


@dataclass(frozen=True)
class _ModelReport:
    actual: Actual
    announced: datetime
    inputs: tuple[float, float, float]
    inputs_known: datetime


class PayrollModel:
    """The jobs report's free forecast: payrolls on ADP's change, the claims change and the
    12-month trend, each as first published, refitted by least squares before every report on
    earlier reports only. Known when its newest input, or newest report fitted on, came out."""

    name = PAYROLL_MODEL
    label = "the payroll model"
    zone = NEW_YORK

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        payrolls = [a for a in actuals if a.measure == PAYROLLS]
        if not payrolls:
            return []
        adp, claims = load_model_inputs(api_key)
        trend = {t.event_id: t for t in Trend12m().expectations(events, payrolls, api_key)}
        announced = {event.event_id: event.event_ts for event in events}
        reports = sorted(
            (
                _ModelReport(
                    actual,
                    announced[actual.event_id],
                    (adp[month].change, claims[month].change, trend[actual.event_id].value),
                    max(
                        end_of_day(adp[month].released, self.zone),
                        end_of_day(claims[month].released, self.zone),
                        trend[actual.event_id].known_at,
                    ),
                )
                for actual in own_actuals(events, payrolls)
                if (month := actual.period) in adp and month in claims and actual.event_id in trend
            ),
            key=lambda report: report.announced,
        )
        expected: list[Expectation] = []
        for report in reports:
            fitted = [
                earlier
                for earlier in reports
                if earlier.announced < report.announced
                and not COVID_MONTHS[0] <= earlier.actual.period <= COVID_MONTHS[1]
            ]
            if len(fitted) < MODEL_MIN_REPORTS:
                continue
            intercept, *slopes = stats.least_squares(
                [f.inputs for f in fitted], [f.actual.value for f in fitted]
            )
            value = intercept + sum(b * x for b, x in zip(slopes, report.inputs, strict=True))
            known_at = max(report.inputs_known, max(f.announced for f in fitted))
            actual = report.actual
            expected.append(
                Expectation(
                    actual.event_id, actual.measure, self.name, value, actual.unit, known_at
                )
            )
        return expected


EXPECTATION_SOURCES: list[ExpectationSource] = [Trend12m(), ClevelandNowcast(), PayrollModel()]


def build_surprises(
    events: Sequence[EventInstance],
    actuals: Sequence[Actual],
    expectations: Sequence[Expectation],
    surprise_types: Iterable[str],
) -> list[Surprise]:
    """One ``surprises`` row per expectation, after checking it against its event and actual.

    Refuses everything, naming each failure, if an expectation names an event not stored or of a
    type without a surprise, has no actual for its measure, is in another unit, or was not known
    strictly before the announcement. Rows follow the actuals' order, then the sources'.
    """
    types = set(surprise_types)
    by_id = {event.event_id: event for event in events}
    own = {(a.event_id, a.measure): a for a in own_actuals(events, actuals)}
    problems: list[str] = []
    for e in expectations:
        event = by_id.get(e.event_id)
        where = f"{e.source} {e.measure} for event {e.event_id}"
        if event is None or event.event_type not in types:
            problems.append(f"{where}: no stored event with a surprise")
            continue
        actual = own.get((e.event_id, e.measure))
        if actual is None:
            problems.append(f"{where}: no actual for {e.measure}")
        elif actual.unit != e.unit:
            problems.append(f"{where}: in {e.unit}, the actual in {actual.unit}")
        if e.known_at >= event.event_ts:
            problems.append(
                f"{where}: known {e.known_at}, not before the event at {event.event_ts}"
            )
    if problems:
        raise ValueError("expectations refused: " + "; ".join(problems))
    by_actual: dict[tuple[int, str], list[Expectation]] = {}
    for e in expectations:
        by_actual.setdefault((e.event_id, e.measure), []).append(e)
    return [
        Surprise(
            event_id=actual.event_id,
            measure=actual.measure,
            baseline=e.source,
            actual_mom=actual.value,
            expected_mom=e.value,
            surprise=actual.value - e.value,
        )
        for actual in own.values()
        for e in by_actual.get((actual.event_id, actual.measure), [])
    ]
