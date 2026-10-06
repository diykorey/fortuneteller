"""Event flows (docs/steps/event-flows.md): one per event type, each fetching from its own source,
running its own checks, and returning the common records.

``EventFlow.events`` gives the ``event_instances`` rows (step 1, rung 1); ``EventFlow.actuals``
gives each event's first-published ``Actual`` per measure (step 4, rung 1). A new event type is one
flow and one line in ``EVENT_FLOWS``; prices, raw move and the surprise apply to it from there.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Protocol

import duckdb

from . import db, sources
from .expectations import (
    EXPECTATION_SOURCES,
    NOWCAST_BASELINE,
    TREND_12M,
    Actual,
    build_surprises,
    event_month,
    previous_month,
)
from .models import EventInstance, Surprise
from .sources import NEW_YORK, FirstRelease


# Step 1 — the CPI release history from FRED (docs/steps/step-1-releases.md).


# Exact keys from data/seed/event_types.csv and countries.csv — joins match on these strings.
CPI_EVENT_TYPE = "CPI / inflation surprise"
NFP_EVENT_TYPE = "NFP / labor data"
FOMC_EVENT_TYPE = "Central-bank decision"
UNITED_STATES = "United States"
# CPI and the jobs report both come out at 08:30 New York time.
RELEASE_TIME = time(8, 30)
FIRST_RELEASE = "first_release"
# Each event type's leading digit in event_id; the rest is the release day, so ids from different
# types never collide and sort by date within a type.
EVENT_TYPE_CODES = {CPI_EVENT_TYPE: 1, NFP_EVENT_TYPE: 2, FOMC_EVENT_TYPE: 3}
# The FRED series each scheduled data release is read from, as first published.
RELEASE_SERIES = {CPI_EVENT_TYPE: sources.CPI_SERIES_ID, NFP_EVENT_TYPE: sources.NFP_SERIES_ID}


def event_id(event_type: str, released: date) -> int:
    """The ``event_instances`` key: type code, then the release day (CPI 2022-09-13 → 120220913)."""
    day = released.year * 10_000 + released.month * 100 + released.day
    return EVENT_TYPE_CODES[event_type] * 100_000_000 + day


def event_date(event_id: int) -> date:
    """The release day an ``event_id`` was built from."""
    day = event_id % 100_000_000
    return date(day // 10_000, day // 100 % 100, day % 100)


def to_event_instance(release: FirstRelease, event_type: str) -> EventInstance:
    """Map one release to its ``event_instances`` row, keyed by event type and release day.

    ``event_ts`` is naive UTC: DuckDB converts an aware datetime written to a ``TIMESTAMP`` column
    into the session time zone, so the offset is applied here and then dropped.
    """
    published = datetime.combine(release.released, RELEASE_TIME, tzinfo=NEW_YORK)
    return EventInstance(
        event_id=event_id(event_type, release.released),
        event_type=event_type,
        event_ts=published.astimezone(UTC).replace(tzinfo=None),
        country=UNITED_STATES,
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


def one_release_per_day(
    releases: Sequence[FirstRelease],
) -> tuple[list[FirstRelease], list[FirstRelease]]:
    """The newest month first published on each release day, and the earlier months it carried.

    A release day is one event: the market reacts to it once. When a release carries two months
    for the first time (October 2025's payrolls came out with November's, after the shutdown), the
    event is the newer month.
    """
    newest: dict[date, FirstRelease] = {}
    for release in releases:
        current = newest.get(release.released)
        if current is None or release.reference_month > current.reference_month:
            newest[release.released] = release
    kept = sorted(newest.values(), key=lambda release: release.reference_month)
    carried = [release for release in releases if release not in kept]
    return kept, carried


def store_releases(
    event_type: str,
    releases: Sequence[FirstRelease],
    con: duckdb.DuckDBPyConnection | None = None,
) -> int:
    """Write one event type's releases to ``event_instances``; re-running overwrites by key.

    Two releases on one day would share an ``event_id``; ``one_release_per_day`` merges them first.
    """
    if len({release.released for release in releases}) != len(releases):
        raise ValueError(f"{event_type}: two releases on one day; merge them first")
    return store_events([to_event_instance(release, event_type) for release in releases], con=con)


def store_events(
    events: Sequence[EventInstance], con: duckdb.DuckDBPyConnection | None = None
) -> int:
    """Write events to ``event_instances``; re-running overwrites by key."""
    if len({event.event_id for event in events}) != len(events):
        raise ValueError("two events share an event_id; merge them first")
    return db.insert_models("event_instances", events, con=con, replace=True)


# Fed decisions (docs/steps/rung-1-more-events.md). From 1994, the first decision announced the day
# it was made; the year pages run to 2020, the current calendar from 2021.
FED_HISTORY_YEARS = range(1994, 2021)
# When each decision's statement came out, New York time: 14:15 until the first at 14:00, on
# 2013-03-20, and then 14:00. The 1994-2006 times come from Gürkaynak, Sack & Swanson's
# appendix (2005) and Swanson's account of 14:15 through March 2011; 2006-2015 from the minutes
# ("to be released at"); since 2016 from the statements themselves.
FOMC_TIME_UNTIL_2013 = time(14, 15)
FOMC_TIME = time(14, 0)
FOMC_TIME_FROM = date(2013, 3, 20)
FOMC_ANNOUNCED_AT = {
    date(1994, 2, 4): time(11, 5),
    date(1994, 4, 18): time(10, 6),
    date(1994, 8, 16): time(13, 18),
    date(1996, 3, 26): time(11, 39),
    date(1998, 10, 15): time(15, 15),
    date(2001, 1, 3): time(13, 13),
    date(2001, 4, 18): time(10, 54),
    date(2001, 9, 17): time(8, 20),
    # The 2007-08 calls were announced in the morning; the hour is not published. The call on
    # 2007-08-10 began at 08:45; the cut of 2007-08-17 came "before the market opens".
    date(2007, 8, 10): time(9, 15),
    date(2007, 8, 17): time(8, 15),
    date(2008, 1, 22): time(8, 30),
    date(2008, 3, 11): time(8, 30),
    date(2008, 10, 8): time(7, 0),
    date(2010, 5, 9): time(21, 15),
    # 2011-2012 statements on press-conference days.
    date(2011, 4, 27): time(12, 30),
    date(2011, 6, 22): time(12, 30),
    date(2011, 11, 2): time(12, 30),
    date(2012, 1, 25): time(12, 30),
    date(2012, 4, 25): time(12, 30),
    date(2012, 6, 20): time(12, 30),
    date(2012, 9, 13): time(12, 30),
    date(2012, 12, 12): time(12, 30),
    date(2019, 10, 11): time(11, 0),
    date(2020, 3, 3): time(10, 0),
    date(2020, 3, 15): time(17, 0),
}
FED_CALENDAR = "fed_calendar"
# The target rate the Fed sets: one rate until 2008-12-15, the top of a range from 2008-12-16.
TARGET_RATE_SERIES = (
    ("DFEDTAR", date(1994, 1, 1), date(2008, 12, 15)),
    ("DFEDTARU", date(2008, 12, 16), date.max),
)
# A new target takes effect up to a weekend after it is announced (since 2017, the next day).
TARGET_EFFECT_DAYS = 3


def fomc_announced_at(day: date) -> time:
    """The New York time the decision of ``day`` was announced."""
    if day in FOMC_ANNOUNCED_AT:
        return FOMC_ANNOUNCED_AT[day]
    return FOMC_TIME if day >= FOMC_TIME_FROM else FOMC_TIME_UNTIL_2013


def fomc_event_instance(decision: sources.FomcDecision) -> EventInstance:
    """Map one Fed decision to its ``event_instances`` row, at the time it was announced."""
    announced = datetime.combine(decision.day, fomc_announced_at(decision.day), tzinfo=NEW_YORK)
    return EventInstance(
        event_id=event_id(FOMC_EVENT_TYPE, decision.day),
        event_type=FOMC_EVENT_TYPE,
        event_ts=announced.astimezone(UTC).replace(tzinfo=None),
        country=UNITED_STATES,
        detail="scheduled meeting" if decision.scheduled else "unscheduled",
        scheduled=decision.scheduled,
        consensus=None,
        actual=None,
        surprise=None,
        surprise_sd=None,
        surprise_source=None,
        priced_in_prior=None,
        vix_t0=None,
        rate_regime=None,
        quality=FED_CALENDAR,
    )


def unmatched_target_changes(
    decisions: Iterable[sources.FomcDecision], rates: Sequence[tuple[date, float]]
) -> list[date]:
    """Days the target rate changed with no decision announced that day or shortly before.

    A change with no decision means the calendar is missing a meeting.
    """
    days = {decision.day for decision in decisions}
    changes = [
        day for (_, before), (day, after) in zip(rates, rates[1:], strict=False) if after != before
    ]
    return [
        day
        for day in changes
        if not any(day - timedelta(days=lag) in days for lag in range(TARGET_EFFECT_DAYS + 1))
    ]


def load_fomc_decisions(api_key: str) -> list[sources.FomcDecision]:
    """Every Fed decision since 1994, refused if a target-rate change has no decision."""
    pages = [sources.fetch_fed_page(sources.fed_history_url(year)) for year in FED_HISTORY_YEARS]
    calendar = sources.fetch_fed_page(sources.FED_CALENDAR_URL)
    decisions = [d for page in pages for d in sources.parse_fomc_history(page)]
    decisions += sources.parse_fomc_calendar(calendar)
    rates = []
    for series_id, start, end in TARGET_RATE_SERIES:
        series = sources.parse_series(sources.fetch_series(api_key, series_id))
        rates += [(day, value) for day, value in series if start <= day <= end]
    if unmatched := unmatched_target_changes(decisions, rates):
        days = ", ".join(str(day) for day in unmatched)
        raise ValueError(f"the target rate changed with no Fed decision on {days}")
    return sorted(decisions, key=lambda decision: decision.day)


def store_fomc_decisions(
    decisions: Sequence[sources.FomcDecision], con: duckdb.DuckDBPyConnection | None = None
) -> int:
    """Write the Fed's decisions to ``event_instances``; re-running overwrites by key."""
    events = [fomc_event_instance(decision) for decision in decisions]
    return db.insert_models("event_instances", events, con=con, replace=True)


def stored_events(
    event_type: str, con: duckdb.DuckDBPyConnection | None = None
) -> list[EventInstance]:
    """The stored events of one type, oldest first."""
    return db.fetch_all(
        EventInstance,
        "SELECT * FROM event_instances WHERE event_type = ? ORDER BY event_id",
        [event_type],
        con=con,
    )


def release_date(event: EventInstance) -> date:
    """The New York calendar date the release came out; ``event_ts`` is naive UTC."""
    return event.event_ts.replace(tzinfo=UTC).astimezone(NEW_YORK).date()


# Step 4 — each event's actuals (docs/steps/step-4-surprise.md).


# Core decides step 4's verdicts; headline is context. Each is read from its own FRED series.
MEASURE_SERIES = {sources.CORE: sources.CORE_CPI_SERIES_ID, sources.HEADLINE: sources.CPI_SERIES_ID}
# The jobs report's measure (rung 1): the monthly change in non-farm payrolls, in thousands.
PAYROLLS = "payrolls"


@dataclass(frozen=True)
class MonthlyChange:
    """One month's change as first published: CPI in percent (``0.4`` is +0.4%), payrolls in
    thousands of jobs."""

    reference_month: date
    released: date
    change: float


def first_published_changes(
    releases: Sequence[FirstRelease], revised_previous: Mapping[date, float]
) -> list[MonthlyChange]:
    """Each month's change as BLS first published it, oldest first.

    A month is compared with the previous month's first-published level, except January: it comes
    out on the day BLS revises its seasonal factors, so December's level that day comes from
    ``revised_previous``, keyed by the January month. A month whose previous month has no level
    (the first month, or after a month never published, like October 2025) gets no change.
    """
    levels = {release.reference_month: release.value for release in releases}
    changes: list[MonthlyChange] = []
    for release in sorted(releases, key=lambda release: release.reference_month):
        month = release.reference_month
        if previous_month(month) not in levels:
            continue
        if month.month == 1:
            if month not in revised_previous:
                raise ValueError(f"{month:%Y-%m}: no December level as revised on its release day")
            previous = revised_previous[month]
        else:
            previous = levels[previous_month(month)]
        changes.append(MonthlyChange(month, release.released, (release.value / previous - 1) * 100))
    return changes


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


def payroll_level_mismatches(
    vintages: Mapping[date, Mapping[date, float]], events: Iterable[EventInstance]
) -> list[date]:
    """Stored jobs reports whose first-published level or day differs from FRED's revision history.

    The stored ``actual`` comes from FRED's first-release view, the vintages from its
    new-and-revised view; a release on which the two disagree would give a wrong change.
    """
    missed = []
    for event in events:
        month = date.fromisoformat(f"{event.detail}-01")
        levels = vintages.get(month, {})
        first = min(levels, default=None)
        if first != release_date(event) or first is None or levels[first] != event.actual:
            missed.append(month)
    return missed


def load_first_published_changes(api_key: str, series_id: str) -> list[MonthlyChange]:
    """Fetch a CPI series' first releases and each January's revised December, then the changes."""
    releases, _valueless = sources.parse_first_releases(
        sources.fetch_first_releases(api_key, series_id=series_id), series_id
    )
    months = {release.reference_month for release in releases}
    revised_previous = {
        release.reference_month: sources.parse_level(
            sources.fetch_level_as_of(
                api_key, series_id, previous_month(release.reference_month), release.released
            )
        )
        for release in releases
        if release.reference_month.month == 1 and previous_month(release.reference_month) in months
    }
    return first_published_changes(releases, revised_previous)


# Our first-published change and Cleveland's published one may differ by rounding, not by more.
ACTUAL_TOLERANCE_PP = 0.01


def published_actuals(points: Iterable[sources.NowcastPoint]) -> dict[tuple[str, date], float]:
    """Cleveland's record of each month's published change, keyed by (measure, month)."""
    return {
        (point.measure, point.reference_month): point.percent
        for point in points
        if point.kind == sources.ACTUAL
    }


def actual_mismatches(
    changes: Iterable[MonthlyChange], actuals: Mapping[tuple[str, date], float], measure: str
) -> list[date]:
    """Months where our first-published change differs from Cleveland's by more than rounding."""
    return [
        change.reference_month
        for change in changes
        if (measure, change.reference_month) in actuals
        and abs(change.change - actuals[(measure, change.reference_month)]) > ACTUAL_TOLERANCE_PP
    ]


# The unit each measure's actual and expected values are in.
PERCENT = "percent"
THOUSANDS = "thousands"


def to_actuals(
    changes: Iterable[MonthlyChange],
    event_type: str,
    measure: str,
    unit: str,
    events: Sequence[EventInstance],
) -> list[Actual]:
    """Each change as the ``Actual`` of the stored event that first published it.

    A change must come out on a stored release day: its own month's (a month carried into a later
    release, October 2025 payrolls, rides on that one's), or it is refused.
    """
    stored = {event.event_id for event in events}
    by_month = {event_month(event): event for event in events}
    actuals = []
    for change in changes:
        key = event_id(event_type, change.released)
        if key not in stored:
            month = change.reference_month
            if (own := by_month.get(month)) is not None:
                raise ValueError(
                    f"{measure} {month:%Y-%m}: released {change.released}, "
                    f"but the stored release is {release_date(own)}"
                )
            raise ValueError(
                f"{measure} {month:%Y-%m}: no release stored for it; "
                "run `fortuneteller load-releases` first"
            )
        actuals.append(Actual(key, measure, change.reference_month, change.change, unit))
    return actuals


def payroll_actuals(api_key: str, jobs: Sequence[EventInstance]) -> list[Actual]:
    """Each stored jobs report's first-published payroll change, checked against FRED's history."""
    vintages = sources.parse_vintages(
        sources.fetch_vintages(api_key, sources.NFP_SERIES_ID), sources.NFP_SERIES_ID
    )
    if missed := payroll_level_mismatches(vintages, jobs):
        months = ", ".join(f"{month:%Y-%m}" for month in missed)
        raise ValueError(
            f"{PAYROLLS}: the stored first release differs from FRED's revision history in {months}"
        )
    since = min(event_month(event) for event in jobs)
    changes = first_published_payroll_changes(vintages, since)
    return to_actuals(changes, NFP_EVENT_TYPE, PAYROLLS, THOUSANDS, jobs)


# CPI surprises smaller than this are noise for the hit rate, in percentage points.
NOTICEABLE_SURPRISE_PP = 0.1
# The direction a hotter-than-expected CPI should move each instrument; gold has no agreed one.
EXPECTED_SIGN = {"SPY / ES": -1, "UST10Y / ZN": 1, "DXY": 1, "GC / XAU": 0, "VIX": 1}
# Core against the trend gives the verdict; the other three are context (decided 2026-10-05).
VERDICT_COMBINATION = (sources.CORE, TREND_12M)
COMBINATIONS = (
    VERDICT_COMBINATION,
    (sources.CORE, NOWCAST_BASELINE),
    (sources.HEADLINE, TREND_12M),
    (sources.HEADLINE, NOWCAST_BASELINE),
)
# The direction a stronger-than-expected jobs report should move each instrument: rates and the
# dollar up; equities, VIX and gold have no agreed sign ("good news is bad news"). Rung 1 decision.
NFP_EXPECTED_SIGN = {"SPY / ES": 0, "UST10Y / ZN": 1, "DXY": 1, "GC / XAU": 0, "VIX": 0}
# Payroll surprises smaller than this are noise for the hit rate, in thousands of jobs.
NOTICEABLE_PAYROLLS_K = 50.0


@dataclass(frozen=True)
class SurpriseRule:
    """What step 4 measures for one event type. The first combination gives the verdict; the
    hit rate counts surprises of at least ``noticeable``, and the slope is per ``noticeable``,
    which the report names ``step``."""

    combinations: tuple[tuple[str, str], ...]
    expected_sign: Mapping[str, int]
    noticeable: float
    step: str


SURPRISE_RULES = {
    CPI_EVENT_TYPE: SurpriseRule(COMBINATIONS, EXPECTED_SIGN, NOTICEABLE_SURPRISE_PP, "0.1pp"),
    NFP_EVENT_TYPE: SurpriseRule(
        ((PAYROLLS, TREND_12M),), NFP_EXPECTED_SIGN, NOTICEABLE_PAYROLLS_K, "50k"
    ),
}


# The flows.


@dataclass(frozen=True)
class EventBatch:
    """A flow's events, checked, and the lines ``load-releases`` prints about them."""

    events: list[EventInstance]
    report: list[str]


class EventFlow(Protocol):
    event_type: str
    cli_name: str
    label: str
    surprise_rule: SurpriseRule | None

    def events(self, api_key: str) -> EventBatch: ...

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]: ...


def _months(months: Iterable[date]) -> str:
    return ", ".join(f"{month:%Y-%m}" for month in months)


def _release_batch(event_type: str, label: str, series_id: str, api_key: str) -> EventBatch:
    """A FRED first-release history as events: one per release day, the newest month kept."""
    payload = sources.fetch_first_releases(api_key, series_id=series_id)
    releases, valueless = sources.parse_first_releases(payload, series_id)
    if not releases:
        raise ValueError(f"FRED returned no {event_type} releases")
    kept, carried = one_release_per_day(releases)
    released = [release.released for release in kept]
    report = [f"loaded {len(kept)} {label} releases, {min(released)} … {max(released)}"]
    if valueless:
        report.append(f"  skipped {len(valueless)} printed without a value: {_months(valueless)}")
    if carried:
        report.append(
            f"  {len(carried)} first published with a later month: "
            f"{_months(release.reference_month for release in carried)}"
        )
    return EventBatch([to_event_instance(release, event_type) for release in kept], report)


class CpiFlow:
    """US CPI from FRED, 1972 on: core and headline month-over-month changes as first published,
    each checked against the Cleveland Fed's published figure."""

    event_type = CPI_EVENT_TYPE
    cli_name = "cpi"
    label = "CPI"
    surprise_rule: SurpriseRule | None = SURPRISE_RULES[CPI_EVENT_TYPE]

    def events(self, api_key: str) -> EventBatch:
        return _release_batch(self.event_type, self.label, sources.CPI_SERIES_ID, api_key)

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        changes = {
            measure: load_first_published_changes(api_key, series_id)
            for measure, series_id in MEASURE_SERIES.items()
        }
        published = published_actuals(sources.parse_nowcasts(sources.fetch_nowcasts()))
        for measure, measure_changes in changes.items():
            if missed := actual_mismatches(measure_changes, published, measure):
                raise ValueError(
                    f"{measure}: first-published change differs from the Cleveland Fed's by more "
                    f"than {ACTUAL_TOLERANCE_PP} pp in {_months(missed)}"
                )
        return [
            actual
            for measure, measure_changes in changes.items()
            for actual in to_actuals(measure_changes, self.event_type, measure, PERCENT, events)
        ]


class NfpFlow:
    """The US jobs report from FRED, 1955 on: the payroll change as first published, from FRED's
    revision history."""

    event_type = NFP_EVENT_TYPE
    cli_name = "nfp"
    label = "NFP"
    surprise_rule: SurpriseRule | None = SURPRISE_RULES[NFP_EVENT_TYPE]

    def events(self, api_key: str) -> EventBatch:
        return _release_batch(self.event_type, self.label, sources.NFP_SERIES_ID, api_key)

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        return payroll_actuals(api_key, events)


class FedFlow:
    """The Fed's rate decisions from its meeting calendars, 1994 on, checked against every change in
    its target rate. No surprise: there is no free record of what the market expected."""

    event_type = FOMC_EVENT_TYPE
    cli_name = "fomc"
    label = "Fed"
    surprise_rule: SurpriseRule | None = None

    def events(self, api_key: str) -> EventBatch:
        decisions = load_fomc_decisions(api_key)
        unscheduled = sum(not decision.scheduled for decision in decisions)
        first, last = decisions[0].day, decisions[-1].day
        report = [
            f"loaded {len(decisions)} Fed decisions, {first} … {last} ({unscheduled} unscheduled)"
        ]
        return EventBatch([fomc_event_instance(decision) for decision in decisions], report)

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        return []


EVENT_FLOWS: list[EventFlow] = [CpiFlow(), NfpFlow(), FedFlow()]


def load_releases(api_key: str, con: duckdb.DuckDBPyConnection | None = None) -> list[str]:
    """Run every flow, then store all their events: nothing is stored unless every flow succeeds."""
    batches = [flow.events(api_key) for flow in EVENT_FLOWS]
    report: list[str] = []
    for batch in batches:
        store_events(batch.events, con=con)
        report += batch.report
    return report


def load_surprises(api_key: str, con: duckdb.DuckDBPyConnection | None = None) -> list[Surprise]:
    """Rebuild ``surprises``: every flow with a surprise gives its stored events' actuals, every
    expectation source its expectations, and ``build_surprises`` checks and pairs them.

    Nothing is stored unless every flow's own checks pass (CPI's against the Cleveland Fed, NFP's
    against FRED's revision history) and every expectation fits its event.
    """
    events: list[EventInstance] = []
    actuals: list[Actual] = []
    for flow in EVENT_FLOWS:
        if flow.surprise_rule is None:
            continue
        if typed := stored_events(flow.event_type, con=con):
            events += typed
            actuals += flow.actuals(typed, api_key)
    if not events:
        raise ValueError("no releases stored; run `fortuneteller load-releases` first")
    expected = [
        expectation
        for source in EXPECTATION_SOURCES
        for expectation in source.expectations(events, actuals, api_key)
    ]
    rows = build_surprises(events, actuals, expected, SURPRISE_RULES)
    db.replace_rows("surprises", rows, "TRUE", con=con)
    return rows
