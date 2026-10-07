"""Expected values and surprises (docs/steps/event-flows.md).

An event flow gives each event's ``Actual`` per measure; every ``ExpectationSource`` gives its
``Expectation`` for some of them; ``build_surprises`` checks each expectation against its event and
actual, then stores ``actual − expected``. A new source is one class and one line in
``EXPECTATION_SOURCES``. Nothing here knows which event types exist.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Protocol

from . import sources
from .models import EventInstance, Surprise
from .sources import NEW_YORK


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
    """The average of the previous 12 months' first-published values, for any measure.

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
        expected: list[Expectation] = []
        for measure in dict.fromkeys(actual.measure for actual in actuals):
            by_period = {a.period: a for a in actuals if a.measure == measure}
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


def end_of_day(day: date) -> datetime:
    """The last second of a New York day, as naive UTC: when a day-only value was surely known."""
    return (
        datetime.combine(day, time(23, 59, 59), tzinfo=NEW_YORK)
        .astimezone(UTC)
        .replace(tzinfo=None)
    )


class ClevelandNowcast:
    """The Cleveland Fed's CPI nowcast: the last one made before the release day, 2013 on."""

    name = NOWCAST_BASELINE
    label = "the Cleveland Fed's nowcast"

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
            .astimezone(NEW_YORK)
            .date()
            for actual in wanted
        }
        latest = nowcast_expectations(
            sources.parse_nowcasts(sources.fetch_nowcasts()), release_dates
        )
        return [
            Expectation(
                actual.event_id, actual.measure, self.name, value, actual.unit, end_of_day(day)
            )
            for actual in wanted
            if (key := (actual.measure, actual.period)) in latest
            for day, value in [latest[key]]
        ]


EXPECTATION_SOURCES: list[ExpectationSource] = [Trend12m(), ClevelandNowcast()]


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
