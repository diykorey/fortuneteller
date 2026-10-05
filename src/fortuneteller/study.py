"""Event study over US CPI releases — MVP step 1 onward (see ``docs/steps/step-1-releases.md``).

Fetching and parsing the outside sources lives in ``sources``; this module turns their records
into rows and measures them.

Step 1: map each CPI release to an ``EventInstance`` and store them. Each record keeps both dates,
because the reference month (what was measured) and the release date (when the market saw it) are
about six weeks apart.

Step 2 (see ``docs/steps/step-2-prices.md``): store each instrument's daily closes; then measure
each instrument's move around each CPI release into ``observations``.

Step 3 (see ``docs/steps/step-3-raw-move.md``): compare each instrument's moves on CPI days with its
moves on all other days.
"""

from __future__ import annotations

import random
from bisect import bisect_left
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from statistics import median
from typing import NamedTuple
from zoneinfo import ZoneInfo

import duckdb

from . import db, sources
from .models import CpiSurprise, DailyBar, EventInstance, Observation
from .sources import CpiRelease, DailyClosingPrice, YahooError


# Step 1 — the CPI release history from FRED (docs/steps/step-1-releases.md).


# Exact keys from data/seed/event_types.csv and countries.csv — joins match on these strings.
CPI_EVENT_TYPE = "CPI / inflation surprise"
CPI_COUNTRY = "United States"
CPI_RELEASE_TIME = time(8, 30)
CPI_RELEASE_ZONE = ZoneInfo("America/New_York")
FIRST_RELEASE = "first_release"


def to_event_instance(release: CpiRelease) -> EventInstance:
    """Map one release to its ``event_instances`` row, keyed by reference month (``YYYYMM``).

    ``event_ts`` is naive UTC: DuckDB converts an aware datetime written to a ``TIMESTAMP`` column
    into the session time zone, so the offset is applied here and then dropped.
    """
    published = datetime.combine(release.released, CPI_RELEASE_TIME, tzinfo=CPI_RELEASE_ZONE)
    return EventInstance(
        # YYYYMM is unique only within CPI. event_id is the key of the whole table, so a second
        # event type keyed this way would collide and replace=True would silently overwrite CPI rows.
        # Before adding one, replace this with a key generic across event types, e.g. a
        # deterministic hash of (event_type, detail).
        event_id=release.reference_month.year * 100 + release.reference_month.month,
        event_type=CPI_EVENT_TYPE,
        event_ts=published.astimezone(UTC).replace(tzinfo=None),
        country=CPI_COUNTRY,
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


def store_cpi_releases(
    releases: Sequence[CpiRelease], con: duckdb.DuckDBPyConnection | None = None
) -> int:
    """Write the releases to ``event_instances``; re-running overwrites by ``event_id``."""
    events = [to_event_instance(release) for release in releases]
    return db.insert_models("event_instances", events, con=con, replace=True)


# Step 2 — each instrument's daily closes from Yahoo (docs/steps/step-2-prices.md).


class PriceSeries(NamedTuple):
    ticker: str
    unit: str


# The five MVP instruments, keyed by the exact symbol in data/seed/instruments.csv, with the Yahoo
# ticker each is read from and the unit its move is measured in: pct for prices, bps for the yield.
# Order matters: observations are numbered by position in this table.
MVP_PRICE_SERIES = {
    "SPY / ES": PriceSeries("^GSPC", "pct"),
    "UST10Y / ZN": PriceSeries("^TNX", "bps"),
    "DXY": PriceSeries("DX-Y.NYB", "pct"),
    "GC / XAU": PriceSeries("GC=F", "pct"),
    "VIX": PriceSeries("^VIX", "pct"),
}


def store_daily_bars(
    instrument: str,
    ticker: str,
    closes: Sequence[DailyClosingPrice],
    con: duckdb.DuckDBPyConnection | None = None,
) -> int:
    """Replace one instrument's closes in ``daily_bars`` with ``closes``.

    Every earlier row of the instrument goes, so closes from a previous ticker can never mix with
    the new ones.
    """
    source = f"yahoo:{ticker}"
    bars = [
        DailyBar(instrument=instrument, day=c.day, close=c.price, source=source) for c in closes
    ]
    return db.replace_rows("daily_bars", bars, "instrument = ?", [instrument], con=con)


def load_daily_bars(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, int]:
    """Fetch, parse and store every MVP instrument's daily closes; return the count per instrument.

    All five are fetched and parsed before any is stored, so a failure on one leaves ``daily_bars``
    as it was rather than half-refreshed.
    """
    fetched: dict[str, tuple[str, list[DailyClosingPrice]]] = {}
    for instrument, (ticker, _unit) in MVP_PRICE_SERIES.items():
        payload = sources.fetch_daily_bars(ticker)
        try:
            closes = sources.parse_daily_bars(payload)
        except YahooError as exc:
            raise YahooError(f"{ticker}: {exc}") from None
        if not closes:
            raise YahooError(f"Yahoo sent no usable closes for {ticker}")
        fetched[instrument] = (ticker, closes)
    return {
        instrument: store_daily_bars(instrument, ticker, closes, con=con)
        for instrument, (ticker, closes) in fetched.items()
    }


# Step 2 — each instrument's move around each release, into observations.


# A close more than this many calendar days from the release is not "the day before" or "the
# reaction": four admits Friday -> Tuesday after a Monday holiday and rejects a hole in the data.
MAX_CLOSE_GAP_DAYS = 4
BEFORE_HISTORY = "before_history"
NO_CLOSE_NEARBY = "no_close_nearby"
YAHOO = "yahoo"
DAILY_CLOSE = "daily_close"


@dataclass
class ReleaseCounts:
    """For one instrument: how many CPI releases were measured, and how many skipped and why."""

    measured: int = 0
    skipped_before_history: int = 0
    skipped_no_close_nearby: int = 0


def closing_price_before_after(
    closes: Sequence[DailyClosingPrice], release_date: date
) -> tuple[DailyClosingPrice, DailyClosingPrice] | str:
    """The last close before the release date and the first on or after it, or why there is none.

    ``closes`` must be in date order. Returns ``BEFORE_HISTORY`` when no close precedes the release,
    and ``NO_CLOSE_NEARBY`` when the reaction close is missing or either close is more than
    ``MAX_CLOSE_GAP_DAYS`` from the release.
    """
    i = bisect_left(closes, release_date, key=lambda close: close.day)
    if i == 0:
        return BEFORE_HISTORY
    if i == len(closes):
        return NO_CLOSE_NEARBY
    before, after = closes[i - 1], closes[i]
    if (release_date - before.day).days > MAX_CLOSE_GAP_DAYS:
        return NO_CLOSE_NEARBY
    if (after.day - release_date).days > MAX_CLOSE_GAP_DAYS:
        return NO_CLOSE_NEARBY
    return before, after


def release_move(before: DailyClosingPrice, after: DailyClosingPrice, unit: str) -> float:
    """The move from ``before`` to ``after``: relative for prices, in basis points for yields."""
    if unit == "bps":
        return (after.price - before.price) * 100
    if unit == "pct":
        return after.price / before.price - 1
    raise ValueError(f"unknown unit {unit!r}: expected 'pct' or 'bps'")


def stored_cpi_events(con: duckdb.DuckDBPyConnection | None = None) -> list[EventInstance]:
    """The stored CPI releases, oldest first."""
    return db.fetch_all(
        EventInstance,
        "SELECT * FROM event_instances WHERE event_type = ? ORDER BY event_id",
        [CPI_EVENT_TYPE],
        con=con,
    )


def release_date(event: EventInstance) -> date:
    """The New York calendar date the release came out; ``event_ts`` is naive UTC."""
    return event.event_ts.replace(tzinfo=UTC).astimezone(CPI_RELEASE_ZONE).date()


def stored_closes(
    instrument: str, con: duckdb.DuckDBPyConnection | None = None
) -> list[DailyClosingPrice]:
    """One instrument's closes from ``daily_bars`` in date order; none at all is an error."""
    bars = db.fetch_all(
        DailyBar,
        "SELECT * FROM daily_bars WHERE instrument = ? ORDER BY day",
        [instrument],
        con,
    )
    if not bars:
        raise ValueError(f"no daily_bars for {instrument}: load its prices first")
    return [DailyClosingPrice(bar.day, bar.close) for bar in bars]


def build_observations(
    con: duckdb.DuckDBPyConnection | None = None,
) -> tuple[list[Observation], dict[str, ReleaseCounts]]:
    """Measure every MVP instrument around every stored CPI release, from ``daily_bars``."""
    events = stored_cpi_events(con=con)
    observations: list[Observation] = []
    release_counts: dict[str, ReleaseCounts] = {}
    for position, (instrument, (_ticker, unit)) in enumerate(MVP_PRICE_SERIES.items()):
        closes = stored_closes(instrument, con=con)
        counts = release_counts[instrument] = ReleaseCounts()
        for event in events:
            pair = closing_price_before_after(closes, release_date(event))
            if pair == BEFORE_HISTORY:
                counts.skipped_before_history += 1
                continue
            if isinstance(pair, str):
                counts.skipped_no_close_nearby += 1
                continue
            before, after = pair
            counts.measured += 1
            observations.append(
                Observation(
                    # Unique only while event_id is: the same CPI-only caveat as event_id itself.
                    obs_id=event.event_id * 10 + position,
                    event_id=event.event_id,
                    instrument=instrument,
                    px_t0=before.price,
                    ret_unit=unit,
                    ret_5m=None,
                    ret_1h=None,
                    ret_1d=release_move(before, after, unit),
                    ret_1w=None,
                    abn_ret_1d=None,
                    car=None,
                    peak_move=None,
                    half_life_min=None,
                    realized_dir=None,
                    data_source=YAHOO,
                    quality=DAILY_CLOSE,
                )
            )
    return observations, release_counts


def store_observations(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, ReleaseCounts]:
    """Rebuild the CPI observations: the table ends up holding exactly what this run measured."""
    connection = con if con is not None else db.get_connection()
    observations, release_counts = build_observations(con=connection)
    db.replace_rows(
        "observations",
        observations,
        "event_id IN (SELECT event_id FROM event_instances WHERE event_type = ?)",
        [CPI_EVENT_TYPE],
        con=connection,
    )
    return release_counts


# Step 3 — moves on CPI days against all other days (docs/steps/step-3-raw-move.md).


# Step 3's rule for "moves", fixed before the verdicts were run; see docs/steps/step-3-raw-move.md.
MOVE_RATIO_BAR = 1.10
MOVE_P_BAR = 0.01
PERMUTATIONS = 10_000
PERMUTATION_SEED = 3
MOVES = "moves"
UNCLEAR = "unclear"
DOESNT_MOVE = "doesn't"
# Context only, no verdict: each era's last year. The last era runs to today.
ERAS = (("1970-1989", 1989), ("1990-2007", 2007), ("2008-2019", 2019), ("2020-now", 9999))


def daily_moves(closes: Sequence[DailyClosingPrice], unit: str) -> dict[date, float]:
    """Each day's absolute move from the previous close, keyed by the day.

    ``closes`` must be in date order. A pair more than ``MAX_CLOSE_GAP_DAYS`` apart is a hole in the
    data, not a day, and is skipped.
    """
    return {
        after.day: abs(release_move(before, after, unit))
        for before, after in zip(closes, closes[1:], strict=False)
        if (after.day - before.day).days <= MAX_CLOSE_GAP_DAYS
    }


def cpi_days(closes: Sequence[DailyClosingPrice], release_dates: Iterable[date]) -> set[date]:
    """The days whose move is a CPI release's reaction: the close step 2 pairs each release with."""
    days = set()
    for release_date in release_dates:
        pair = closing_price_before_after(closes, release_date)
        if not isinstance(pair, str):
            days.add(pair[1].day)
    return days


@dataclass(frozen=True)
class MoveComparison:
    """One instrument's moves on CPI days against its moves on all other days."""

    cpi_days: int
    median_cpi: float
    median_other: float
    ratio: float
    p: float
    verdict: str


def median_not_drawn(pool: Sequence[float], drawn: Sequence[int]) -> float:
    """The median of ``pool`` without the positions in ``drawn``, both sorted, without copying it."""

    def kth_not_drawn(k: int) -> float:
        position = k
        for i in drawn:
            if i > position:
                break
            position += 1
        return pool[position]

    rest = len(pool) - len(drawn)
    return (kth_not_drawn((rest - 1) // 2) + kth_not_drawn(rest // 2)) / 2


def move_verdict(ratio: float, p: float) -> str:
    """``MOVES`` if the ratio is big enough and unlikely to be chance, ``UNCLEAR`` if only one."""
    big, significant = ratio >= MOVE_RATIO_BAR, p < MOVE_P_BAR
    if big and significant:
        return MOVES
    if big or significant:
        return UNCLEAR
    return DOESNT_MOVE


def compare_moves(
    cpi: Sequence[float],
    other: Sequence[float],
    permutations: int = PERMUTATIONS,
    seed: int = PERMUTATION_SEED,
) -> MoveComparison:
    """Median CPI-day move over median other-day move, and how often chance does as well.

    ``p`` is the share of random relabellings, drawing as many days as there are CPI days from all
    of them, whose ratio is at least the real one, counting the real labelling itself.
    """
    median_cpi, median_other = median(cpi), median(other)
    ratio = median_cpi / median_other
    pool = sorted([*cpi, *other])
    rng = random.Random(seed)
    as_large = 0
    for _ in range(permutations):
        drawn = sorted(rng.sample(range(len(pool)), len(cpi)))
        if median([pool[i] for i in drawn]) / median_not_drawn(pool, drawn) >= ratio:
            as_large += 1
    p = (as_large + 1) / (permutations + 1)
    return MoveComparison(len(cpi), median_cpi, median_other, ratio, p, move_verdict(ratio, p))


class EraRatio(NamedTuple):
    cpi_days: int
    ratio: float | None


@dataclass(frozen=True)
class RawMove:
    """Step 3's answer for one instrument: the verdict over all history, and each era's ratio."""

    unit: str
    overall: MoveComparison
    eras: dict[str, EraRatio]


def era_of(day: date) -> str:
    return next(label for label, last_year in ERAS if day.year <= last_year)


def measure_raw_moves(con: duckdb.DuckDBPyConnection | None = None) -> dict[str, RawMove]:
    """Each MVP instrument's moves on CPI days against its moves on all other days."""
    release_dates = [release_date(event) for event in stored_cpi_events(con=con)]
    results: dict[str, RawMove] = {}
    for instrument, (_ticker, unit) in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        days = cpi_days(closes, release_dates)
        by_era: dict[str, tuple[list[float], list[float]]] = {label: ([], []) for label, _ in ERAS}
        for day, move in daily_moves(closes, unit).items():
            cpi, other = by_era[era_of(day)]
            (cpi if day in days else other).append(move)
        overall = compare_moves(
            [move for cpi, _ in by_era.values() for move in cpi],
            [move for _, other in by_era.values() for move in other],
        )
        eras = {
            label: EraRatio(len(cpi), median(cpi) / median(other) if cpi and other else None)
            for label, (cpi, other) in by_era.items()
        }
        results[instrument] = RawMove(unit, overall, eras)
    return results


# Step 4 — the CPI surprise (docs/steps/step-4-surprise.md).


# Core decides step 4's verdicts; headline is context. Each is read from its own FRED series.
MEASURE_SERIES = {sources.CORE: sources.CORE_CPI_SERIES_ID, sources.HEADLINE: sources.CPI_SERIES_ID}


@dataclass(frozen=True)
class MonthlyChange:
    """One month's CPI change as first published, in percent (``0.4`` means +0.4%)."""

    reference_month: date
    released: date
    percent: float


def previous_month(month: date) -> date:
    return date(month.year - 1, 12, 1) if month.month == 1 else date(month.year, month.month - 1, 1)


def first_published_changes(
    releases: Sequence[CpiRelease], revised_previous: Mapping[date, float]
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


def load_first_published_changes(api_key: str, series_id: str) -> list[MonthlyChange]:
    """Fetch a CPI series' first releases and each January's revised December, then the changes."""
    releases, _valueless = sources.parse_cpi_releases(
        sources.fetch_cpi_releases(api_key, series_id=series_id)
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


def nowcast_expectations(
    points: Iterable[sources.NowcastPoint], release_dates: Mapping[date, date]
) -> dict[tuple[str, date], float]:
    """The last nowcast made before each month's release day, keyed by (measure, month).

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
    return {key: percent for key, (_day, percent) in latest.items()}


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
        and abs(change.percent - actuals[(measure, change.reference_month)]) > ACTUAL_TOLERANCE_PP
    ]


# The two expected values, as stored in cpi_surprises.baseline.
TREND_12M = "trend_12m"
NOWCAST_BASELINE = "nowcast"
TREND_MONTHS = 12


def trend_expectations(changes: Sequence[MonthlyChange]) -> dict[date, float]:
    """Each month's 12-month trend: the average first-published change over the 12 months before it.

    Every one of those was published before the month's own release, so the trend uses only what
    was known then. A month gets a trend once a full year of history lies behind it; a month never
    published inside the year (October 2025) is skipped, and the rest are averaged.
    """
    percents = {change.reference_month: change.percent for change in changes}
    first = min(percents, default=date.max)
    trend: dict[date, float] = {}
    for month in percents:
        window = [month]
        for _ in range(TREND_MONTHS):
            window.append(previous_month(window[-1]))
        if window[-1] < first:
            continue
        known = [percents[m] for m in window[1:] if m in percents]
        trend[month] = sum(known) / len(known)
    return trend


def build_surprises(
    events: Iterable[EventInstance],
    changes: Mapping[str, Sequence[MonthlyChange]],
    points: Iterable[sources.NowcastPoint],
) -> list[CpiSurprise]:
    """One ``cpi_surprises`` row per stored release, measure and expected value.

    Each change is matched to its stored release by month, and must have come out the same day:
    core and headline are one BLS release.
    """
    stored = {date.fromisoformat(f"{event.detail}-01"): event for event in events}
    nowcast_points = list(points)
    rows: list[CpiSurprise] = []
    for measure, measure_changes in changes.items():
        released = {change.reference_month: change.released for change in measure_changes}
        nowcasts = nowcast_expectations(nowcast_points, released)
        expected_by = {
            TREND_12M: trend_expectations(measure_changes),
            NOWCAST_BASELINE: {m: v for (kind, m), v in nowcasts.items() if kind == measure},
        }
        for change in measure_changes:
            month = change.reference_month
            event = stored.get(month)
            if event is None:
                raise ValueError(
                    f"{measure} {month:%Y-%m}: no CPI release stored for it; "
                    "run `fortuneteller load-releases` first"
                )
            if release_date(event) != change.released:
                raise ValueError(
                    f"{measure} {month:%Y-%m}: released {change.released}, "
                    f"but the stored release is {release_date(event)}"
                )
            for baseline, expected in expected_by.items():
                if month in expected:
                    rows.append(
                        CpiSurprise(
                            event_id=event.event_id,
                            measure=measure,
                            baseline=baseline,
                            actual_mom=change.percent,
                            expected_mom=expected[month],
                            surprise=change.percent - expected[month],
                        )
                    )
    return rows


def load_surprises(api_key: str, con: duckdb.DuckDBPyConnection | None = None) -> list[CpiSurprise]:
    """Fetch both CPI measures and the nowcast, then rebuild ``cpi_surprises`` from them.

    Nothing is stored unless every first-published change matches the Cleveland Fed's published
    one within ``ACTUAL_TOLERANCE_PP``: a wrong actual would make every surprise wrong.
    """
    events = stored_cpi_events(con=con)
    if not events:
        raise ValueError("no CPI releases stored; run `fortuneteller load-releases` first")
    changes = {
        measure: load_first_published_changes(api_key, series_id)
        for measure, series_id in MEASURE_SERIES.items()
    }
    points = sources.parse_nowcasts(sources.fetch_nowcasts())
    actuals = published_actuals(points)
    for measure, measure_changes in changes.items():
        if missed := actual_mismatches(measure_changes, actuals, measure):
            months = ", ".join(f"{month:%Y-%m}" for month in missed)
            raise ValueError(
                f"{measure}: first-published change differs from the Cleveland Fed's by more than "
                f"{ACTUAL_TOLERANCE_PP} pp in {months}"
            )
    rows = build_surprises(events, changes, points)
    db.replace_rows("cpi_surprises", rows, "TRUE", con=con)
    return rows
