"""Expected values and surprises (docs/steps/event-flows.md).

An event flow gives each event's ``Actual`` per measure; every ``ExpectationSource`` gives its
``Expectation`` for some of them; ``build_surprises`` checks each expectation against its event and
actual, then stores ``actual − expected``. A new source is one class and one line in
``EXPECTATION_SOURCES``. Nothing here knows which event types exist.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from . import sources, stats
from .config import settings
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


def first_published_percent_changes(
    vintages: Mapping[date, Mapping[date, float]], since: date, power: int = 1
) -> list[MonthlyChange]:
    """Each period's change in percent as first published, from ``since`` on, oldest first.

    Census and BEA revise the period before in every release, so the change is against the previous
    period's level as it stood that same day. ``power`` 4 annualizes a quarter, as GDP is printed.
    """
    periods = sorted(vintages)
    changes: list[MonthlyChange] = []
    for previous, period in zip(periods, periods[1:]):
        levels, earlier = vintages[period], vintages[previous]
        if period < since or not levels:
            continue
        released = min(levels)
        known = [day for day in earlier if day <= released]
        if not known:
            continue
        ratio = levels[released] / earlier[max(known)]
        changes.append(MonthlyChange(period, released, (ratio**power - 1) * 100))
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
    """The period an event measures: its ``detail``, a month as ``YYYY-MM`` or a week's end as
    ``YYYY-MM-DD``."""
    detail = event.detail or ""
    return date.fromisoformat(detail if len(detail) == 10 else f"{detail}-01")


def own_actuals(events: Iterable[EventInstance], actuals: Iterable[Actual]) -> list[Actual]:
    """The actuals that are their event's own month: the ones a surprise can be built for."""
    months = {event.event_id: event_month(event) for event in events}
    return [actual for actual in actuals if months.get(actual.event_id) == actual.period]


TREND_12M = "trend_12m"
TREND_MONTHS = 12


class Trend12m:
    """The average of the previous 12 months' first-published values, for any measure but a
    year-on-year rate, within one event type from one country: UK CPI's core never enters US CPI's
    trend.

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
        actuals = [a for a in actuals if a.measure not in sources.TRADINGVIEW_ROWS]
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


# The published consensus (docs/steps/free-consensus.md).

# Each measure's row on Nasdaq's calendar and on TradingView's, the decimals its actual is published
# to, and the gap between the two calendars' consensus past which a release gets none.
CONSENSUS_ROWS = {
    sources.CORE: ("Core CPI", "Core Inflation Rate MoM", 1, 0.2),
    sources.HEADLINE: ("CPI", "Inflation Rate MoM", 1, 0.2),
    PAYROLLS: ("Nonfarm Payrolls", "Non Farm Payrolls", 0, 25.0),
    sources.RETAIL_SALES: ("Retail Sales", "Retail Sales MoM", 1, 0.3),
    sources.CORE_PCE: ("Core PCE Price Index", "Core PCE Price Index MoM", 1, 0.2),
    sources.GDP: ("GDP", "GDP Growth Rate QoQ Adv", 1, 0.5),
    sources.INITIAL_CLAIMS: ("Initial Jobless Claims", "Initial Jobless Claims", 0, 5.0),
}
# Nasdaq's calendar carries no consensus before 2008 (checked 2026-10-09): earlier days are not asked.
CONSENSUS_SINCE = date(2008, 1, 1)
# Release days whose Nasdaq row cannot be told, found 2026-10-09: no row's actual is our first
# print (core CPI, payrolls), or two are (headline CPI's month-on-month and year-on-year equal).
UNREADABLE_CONSENSUS = {
    (sources.CORE, date(2008, 10, 16)),
    (PAYROLLS, date(2020, 5, 8)),
    (sources.HEADLINE, date(2015, 11, 17)),
    (sources.HEADLINE, date(2020, 7, 14)),
    # Found 2026-10-12 (docs/steps/step-4-more-events.md): Nasdaq's retail sales actual is not the
    # first print (0.0 for +0.3, -0.1 for +1.0); GDP rebuilt from levels is 0.05 under BEA's print.
    (sources.RETAIL_SALES, date(2008, 2, 13)),
    (sources.RETAIL_SALES, date(2009, 2, 12)),
    (sources.GDP, date(2011, 4, 28)),
    (sources.GDP, date(2014, 7, 30)),
}


def published(value: float, decimals: int, row: float | None) -> bool:
    return row is not None and abs(round(value, decimals) - row) < 0.5 * 10**-decimals


def match_consensus(
    actuals: Iterable[Actual],
    released: Mapping[int, date],
    nasdaq: Iterable[sources.CalendarRow],
    tradingview: Iterable[sources.CalendarRow],
) -> tuple[dict[tuple[int, str], float], list[str], list[str]]:
    """Nasdaq's consensus for each actual, keyed by (event, measure), the releases left out, and
    those filled in from TradingView.

    A release's row is the one whose actual is our first print as published; none or two refuses
    everything, naming the day, except the days in ``UNREADABLE_CONSENSUS``. A release whose
    consensus differs from TradingView's by more than the measure's gap is left out. Where Nasdaq
    has no row with a consensus, TradingView's forecast is taken (docs/steps/consensus-fallback.md).
    ``released`` is each event's New York release day.
    """
    by_day: dict[tuple[str, date], list[sources.CalendarRow]] = {}
    for row in nasdaq:
        if row.consensus is not None:
            by_day.setdefault((row.name, row.day), []).append(row)
    checks = {(row.name, row.day): row.consensus for row in tradingview}
    consensus: dict[tuple[int, str], float] = {}
    left_out: list[str] = []
    filled_in: list[str] = []
    problems: list[str] = []
    for actual in actuals:
        if actual.measure not in CONSENSUS_ROWS:
            continue
        nasdaq_name, check_name, decimals, gap = CONSENSUS_ROWS[actual.measure]
        day = released[actual.event_id]
        candidates = by_day.get((nasdaq_name, day), [])
        where = f"{actual.measure} on {day}"
        check = checks.get((check_name, day))
        if not candidates:
            if check is not None and (actual.measure, day) not in UNREADABLE_CONSENSUS:
                consensus[(actual.event_id, actual.measure)] = check
                filled_in.append(f"{where}: TradingView {check:g}")
            continue
        rows = [r for r in candidates if published(actual.value, decimals, r.actual)]
        if len(rows) != 1 or rows[0].consensus is None:
            if (actual.measure, day) in UNREADABLE_CONSENSUS:
                left_out.append(f"{where}: no single Nasdaq row matches the first print")
            else:
                problems.append(f"{where}: {len(rows)} Nasdaq rows match the first print")
            continue
        value = rows[0].consensus
        if check is not None and abs(value - check) > gap + 1e-9:
            left_out.append(f"{where}: Nasdaq {value:g}, TradingView {check:g}")
            continue
        consensus[(actual.event_id, actual.measure)] = value
    if problems:
        raise ValueError("Nasdaq consensus refused: " + "; ".join(problems))
    return consensus, left_out, filled_in


def fetch_calendars(
    days: Iterable[date], cache_dir: Path
) -> tuple[list[sources.CalendarRow], list[sources.CalendarRow]]:
    """Nasdaq's and TradingView's rows for the consensus measures on ``days`` from
    ``CONSENSUS_SINCE``; Nasdaq answers slowly, so four of its days are asked at a time."""
    days = sorted({day for day in days if day >= CONSENSUS_SINCE})
    nasdaq_names = [names[0] for names in CONSENSUS_ROWS.values()]
    check_names = [names[1] for names in CONSENSUS_ROWS.values()]
    with ThreadPoolExecutor(4) as pool:
        replies = list(pool.map(lambda d: sources.fetch_nasdaq_day(d, cache_dir), days))
    nasdaq = [
        row
        for day, reply in zip(days, replies, strict=True)
        for row in sources.parse_nasdaq_day(reply, day, nasdaq_names)
    ]
    quarters = sorted({sources.quarter_start(day) for day in days})
    tradingview = [
        row
        for quarter in quarters
        for row in sources.parse_tradingview(
            sources.fetch_tradingview_quarter(quarter, cache_dir), check_names
        )
    ]
    return nasdaq, tradingview


@dataclass(frozen=True)
class NextConsensus:
    """The consensus for a measure's next scheduled release, on both calendars."""

    day: date
    nasdaq: float | None
    tradingview: float


def next_consensus(measure: str, today: date, cache_dir: Path) -> NextConsensus | None:
    """The first release from ``today`` on that TradingView lists with a forecast, and Nasdaq's
    consensus for it; ``None`` if TradingView lists none this quarter or next.

    Before the release there is no actual to pick Nasdaq's row by, so where two share a name (CPI's
    month-on-month and year-on-year) the one nearer TradingView's forecast is taken.
    """
    nasdaq_name, check_name, _decimals, _gap = CONSENSUS_ROWS[measure]
    this_quarter = sources.quarter_start(today)
    upcoming = [
        (row.day, row.consensus)
        for quarter in (this_quarter, sources.quarter_start(this_quarter + timedelta(days=95)))
        for row in sources.parse_tradingview(
            sources.fetch_tradingview_quarter(quarter, cache_dir), [check_name]
        )
        if row.day >= today and row.consensus is not None
    ]
    if not upcoming:
        return None
    day, forecast = min(upcoming)
    rows = sources.parse_nasdaq_day(sources.fetch_nasdaq_day(day, cache_dir), day, [nasdaq_name])
    values = [row.consensus for row in rows if row.consensus is not None]
    nearest = min(values, key=lambda v: abs(v - forecast), default=None)
    return NextConsensus(day, nearest, forecast)


def published_actual(measure: str, day: date, cache_dir: Path) -> float | None:
    """The actual TradingView's calendar shows for the measure's release on ``day``, if any yet.

    It matches FRED's first print on 804 of 806 stored releases since 2014 (rung 5's spec).
    """
    payload = sources.fetch_tradingview_quarter(sources.quarter_start(day), cache_dir)
    rows = sources.parse_tradingview(payload, [CONSENSUS_ROWS[measure][1]])
    return next((row.actual for row in rows if row.day == day and row.actual is not None), None)


# The Fed's decision on TradingView's calendar; a flow without a consensus row of its own.
FED_DECISION_ROW = "Fed Interest Rate Decision"


def other_releases(
    measures: Iterable[str], day: date, cache_dir: Path, lesser: Iterable[str] = ()
) -> list[str]:
    """The other flows' rows on TradingView's calendar for ``day``: any there shares the day. A
    ``lesser`` flow's measures share nobody's day.

    TradingView's, not Nasdaq's: Nasdaq names all three GDP estimates "GDP", and only the advance
    estimate is a flow's release (2014 to 2026-09, it gives the replay's shared days on all 355).
    """
    own = {CONSENSUS_ROWS[measure][1] for measure in measures if measure in CONSENSUS_ROWS}
    counted = {m: names for m, names in CONSENSUS_ROWS.items() if m not in set(lesser)}
    others = ({names[1] for names in counted.values()} - own) | {FED_DECISION_ROW}
    payload = sources.fetch_tradingview_quarter(sources.quarter_start(day), cache_dir)
    return sorted(
        {row.name for row in sources.parse_tradingview(payload, others) if row.day == day}
    )


NASDAQ_CONSENSUS = "nasdaq_consensus"


class NasdaqConsensus:
    """The consensus published on Nasdaq's calendar before each release in ``CONSENSUS_ROWS``,
    2008 on, checked against TradingView's, or TradingView's forecast where Nasdaq has none; known
    by the end of the day before the release (assumed)."""

    name = NASDAQ_CONSENSUS
    label = "Nasdaq's consensus"
    zone = NEW_YORK

    def __init__(self) -> None:
        self.left_out: list[str] = []
        self.filled_in: list[str] = []

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        wanted = [a for a in own_actuals(events, actuals) if a.measure in CONSENSUS_ROWS]
        if not wanted:
            return []
        released = {
            event.event_id: event.event_ts.replace(tzinfo=UTC).astimezone(self.zone).date()
            for event in events
        }
        nasdaq, tradingview = fetch_calendars(
            (released[a.event_id] for a in wanted), settings.cache_dir
        )
        consensus, self.left_out, self.filled_in = match_consensus(
            wanted, released, nasdaq, tradingview
        )
        return [
            Expectation(
                a.event_id,
                a.measure,
                self.name,
                consensus[(a.event_id, a.measure)],
                a.unit,
                end_of_day(released[a.event_id] - timedelta(days=1), self.zone),
            )
            for a in wanted
            if (a.event_id, a.measure) in consensus
        ]


TRADINGVIEW_FORECAST = "tradingview_forecast"


class TradingViewForecast:
    """TradingView's forecast for each release read from its calendar alone, in
    ``sources.TRADINGVIEW_ROWS`` (docs/steps/euro-inflation.md, ism-manufacturing.md); known by the
    end of the day before the release in its own zone (assumed)."""

    name = TRADINGVIEW_FORECAST
    label = "TradingView's forecast"

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        rows = sources.TRADINGVIEW_ROWS
        wanted = [a for a in own_actuals(events, actuals) if a.measure in rows]
        announced = {event.event_id: event.event_ts.replace(tzinfo=UTC) for event in events}

        def day(measure: str, when: datetime) -> date:
            return when.astimezone(rows[measure].zone).date()

        expected: list[Expectation] = []
        for country in dict.fromkeys(rows[a.measure].country for a in wanted):
            measures = {m for m, row in rows.items() if row.country == country}
            forecasts = {
                (r.measure, day(r.measure, r.announced)): r.forecast
                for r in sources.tradingview_releases(settings.cache_dir, measures)
                if r.forecast is not None
            }
            for a in wanted:
                released = day(a.measure, announced[a.event_id])
                forecast = forecasts.get((a.measure, released))
                if a.measure in measures and forecast is not None:
                    known_at = end_of_day(released - timedelta(days=1), rows[a.measure].zone)
                    expected.append(
                        Expectation(a.event_id, a.measure, self.name, forecast, a.unit, known_at)
                    )
        return expected


EXPECTATION_SOURCES: list[ExpectationSource] = [
    Trend12m(),
    ClevelandNowcast(),
    PayrollModel(),
    NasdaqConsensus(),
    TradingViewForecast(),
]


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
