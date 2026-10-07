"""The event study's measurements: what the events did to the five markets.

Fetching and parsing the outside sources lives in ``sources``; each event type's way in, from its
source to stored events and first-published actuals, in ``flows``; expected values and surprises
in ``expectations``. This module measures.

Step 2 (see ``docs/steps/step-2-prices.md``): store each instrument's daily closes; then measure
each instrument's move around every stored event into ``observations``.

Step 3 (see ``docs/steps/step-3-raw-move.md``): compare each instrument's moves on an event's days
with its moves on ordinary days, the days no stored event reacted on.

Step 4 (see ``docs/steps/step-4-surprise.md``): whether each instrument's release-day move follows
the event's surprise.
"""

from __future__ import annotations

import random
from bisect import bisect_left
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, time, timedelta
from statistics import median
from typing import NamedTuple

import duckdb

from . import db, sources, stats
from .models import DailyBar, EventInstance, Observation
from .flows import EVENT_FLOWS, EventFlow, SurpriseRule, stored_events
from .sources import NEW_YORK, DailyClosingPrice, YahooError


# Step 2 — each instrument's daily closes from Yahoo (docs/steps/step-2-prices.md).


class PriceSeries(NamedTuple):
    ticker: str
    unit: str
    close: time


# The five MVP instruments, keyed by the exact symbol in data/seed/instruments.csv, with the Yahoo
# ticker each is read from, the unit its move is measured in (pct for prices, bps for the yield)
# and the New York time of its daily close: the intraday price Yahoo's close matches, measured on
# 2026-09 data. Gold's is the COMEX settlement.
MVP_PRICE_SERIES = {
    "SPY / ES": PriceSeries("^GSPC", "pct", time(16, 0)),
    "UST10Y / ZN": PriceSeries("^TNX", "bps", time(15, 0)),
    "DXY": PriceSeries("DX-Y.NYB", "pct", time(15, 0)),
    "GC / XAU": PriceSeries("GC=F", "pct", time(13, 30)),
    "VIX": PriceSeries("^VIX", "pct", time(16, 15)),
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
    for instrument, (ticker, _unit, _close) in MVP_PRICE_SERIES.items():
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


def first_reaction_day(event: EventInstance, close: time) -> date:
    """The first day whose close can carry the event: the next day if it came at or after the close.

    Passed to ``closing_price_before_after``, this pairs the last close before the event with the
    first after it: a Fed decision at 14:00 reacts in gold, which closes at 13:30, the next day.
    """
    announced = event.event_ts.replace(tzinfo=UTC).astimezone(NEW_YORK)
    return announced.date() + timedelta(days=1 if announced.time() >= close else 0)


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
) -> tuple[list[Observation], dict[EventFlow, dict[str, ReleaseCounts]]]:
    """Measure every MVP instrument around every stored event, from ``daily_bars``.

    The counts are per event flow, then per instrument; a flow with no stored events is left out.
    """
    events = {flow: stored_events(flow, con=con) for flow in EVENT_FLOWS}
    observations: list[Observation] = []
    release_counts: dict[EventFlow, dict[str, ReleaseCounts]] = {
        flow: {} for flow, typed in events.items() if typed
    }
    for instrument, (_ticker, unit, close) in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        for flow, by_instrument in release_counts.items():
            counts = by_instrument[instrument] = ReleaseCounts()
            observations += _observe(events[flow], instrument, unit, close, closes, counts)
    return observations, release_counts


def _observe(
    events: Sequence[EventInstance],
    instrument: str,
    unit: str,
    close: time,
    closes: Sequence[DailyClosingPrice],
    counts: ReleaseCounts,
) -> list[Observation]:
    observations: list[Observation] = []
    for event in events:
        pair = closing_price_before_after(closes, first_reaction_day(event, close))
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
    return observations


def store_observations(
    con: duckdb.DuckDBPyConnection | None = None,
) -> dict[EventFlow, dict[str, ReleaseCounts]]:
    """Rebuild the observations: the table ends up holding exactly what this run measured."""
    connection = con if con is not None else db.get_connection()
    observations, release_counts = build_observations(con=connection)
    db.replace_rows("observations", observations, "TRUE", con=connection)
    return release_counts


# Step 3 — moves on an event's days against ordinary days (docs/steps/step-3-raw-move.md).


# Step 3's rule for "moves", fixed before the verdicts were run; see docs/steps/step-3-raw-move.md.
MOVE_RATIO_BAR = 1.10
MOVE_P_BAR = 0.01
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


def reaction_days(closes: Sequence[DailyClosingPrice], first_days: Iterable[date]) -> set[date]:
    """The days whose move is an event's reaction: the close step 2 pairs each event with.

    ``first_days`` are the events' ``first_reaction_day`` for this instrument.
    """
    days = set()
    for first_day in first_days:
        pair = closing_price_before_after(closes, first_day)
        if not isinstance(pair, str):
            days.add(pair[1].day)
    return days


@dataclass(frozen=True)
class MoveComparison:
    """One instrument's moves on an event's days against its moves on ordinary days."""

    event_days: int
    other_days: int
    median_event: float
    median_other: float
    ratio: float
    p: float
    verdict: str


def move_verdict(ratio: float, p: float) -> str:
    """``MOVES`` if the ratio is big enough and unlikely to be chance, ``UNCLEAR`` if only one."""
    big, significant = ratio >= MOVE_RATIO_BAR, p < MOVE_P_BAR
    if big and significant:
        return MOVES
    if big or significant:
        return UNCLEAR
    return DOESNT_MOVE


def compare_moves(
    event: Sequence[float],
    other: Sequence[float],
    permutations: int = stats.PERMUTATIONS,
    seed: int = stats.PERMUTATION_SEED,
) -> MoveComparison:
    """Median event-day move over median other-day move, and how often chance does as well.

    ``p`` is the share of random relabellings, drawing as many days as there are event days from
    all of them, whose ratio is at least the real one, counting the real labelling itself.
    """
    median_event, median_other = median(event), median(other)
    ratio = median_event / median_other
    pool = sorted([*event, *other])

    def draw(rng: random.Random) -> float:
        drawn = sorted(rng.sample(range(len(pool)), len(event)))
        return median([pool[i] for i in drawn]) / stats.median_not_drawn(pool, drawn)

    p = stats.permutation_p(ratio, draw, permutations, seed)
    verdict = move_verdict(ratio, p)
    return MoveComparison(len(event), len(other), median_event, median_other, ratio, p, verdict)


class EraRatio(NamedTuple):
    event_days: int
    ratio: float | None


@dataclass(frozen=True)
class RawMove:
    """Step 3's answer for one instrument: the verdict over all history, and each era's ratio."""

    unit: str
    overall: MoveComparison
    eras: dict[str, EraRatio]


def era_of(day: date) -> str:
    return next(label for label, last_year in ERAS if day.year <= last_year)


def measure_raw_moves(
    flow: EventFlow, con: duckdb.DuckDBPyConnection | None = None
) -> dict[str, RawMove]:
    """Each MVP instrument's moves on the event's days against its moves on ordinary days.

    An ordinary day is one that is no stored event's reaction day, of any type: a jobs-report or
    Fed day is not a fair "other day" for CPI.
    """
    events = stored_events(flow, con=con)
    every_event = [e for each in EVENT_FLOWS for e in stored_events(each, con=con)]
    results: dict[str, RawMove] = {}
    for instrument, (_ticker, unit, close) in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        days = reaction_days(closes, [first_reaction_day(event, close) for event in events])
        busy = reaction_days(closes, [first_reaction_day(event, close) for event in every_event])
        by_era: dict[str, tuple[list[float], list[float]]] = {label: ([], []) for label, _ in ERAS}
        for day, move in daily_moves(closes, unit).items():
            on_event, other = by_era[era_of(day)]
            if day in days:
                on_event.append(move)
            elif day not in busy:
                other.append(move)
        overall = compare_moves(
            [move for on_event, _ in by_era.values() for move in on_event],
            [move for _, other in by_era.values() for move in other],
        )
        eras = {
            label: EraRatio(
                len(on_event), median(on_event) / median(other) if on_event and other else None
            )
            for label, (on_event, other) in by_era.items()
        }
        results[instrument] = RawMove(unit, overall, eras)
    return results


# Step 4's rule for "tracks", fixed before any move was measured; see docs/steps/step-4-surprise.md.
TRACK_P_BAR = 0.01
HIT_RATE_BAR = 0.60
TRACKS = "tracks"
DOESNT_TRACK = "doesn't"


@dataclass(frozen=True)
class SurpriseTracking:
    """How one instrument's release-day moves follow one kind of CPI surprise.

    ``rank_corr`` is multiplied by the expected sign, so positive means "as expected" (absolute for
    gold). ``slope`` is the move per 0.1 pp of surprise, in the instrument's unit. ``verdict`` is
    ``None`` on a context row.
    """

    n: int
    rank_corr: float
    p: float
    hit_rate: float | None
    hit_n: int
    slope: float
    verdict: str | None


def track_verdict(p: float, hit_rate: float | None) -> str:
    """``TRACKS`` if the relation is unlikely to be chance and the direction usually right."""
    significant = p < TRACK_P_BAR
    usually_right = hit_rate is not None and hit_rate >= HIT_RATE_BAR
    if significant and usually_right:
        return TRACKS
    if significant or usually_right:
        return UNCLEAR
    return DOESNT_TRACK


def track_pairs(
    surprises: Sequence[float],
    moves: Sequence[float],
    expected_sign: int,
    judged: bool,
    step: float,
) -> SurpriseTracking:
    """Measure how ``moves`` follow ``surprises``, pair by pair; give a verdict if ``judged``.

    Surprises of at least ``step`` count for the hit rate; the slope is per ``step``.
    """
    rho = stats.spearman(surprises, moves)
    p = stats.spearman_permutation_p(surprises, moves, expected_sign)
    noticeable = [(s, m) for s, m in zip(surprises, moves, strict=True) if abs(s) >= step]
    hits = sum(expected_sign * s * m > 0 for s, m in noticeable)
    hit_rate = hits / len(noticeable) if expected_sign and noticeable else None
    return SurpriseTracking(
        n=len(surprises),
        rank_corr=abs(rho) if expected_sign == 0 else expected_sign * rho,
        p=p,
        hit_rate=hit_rate,
        hit_n=len(noticeable) if hit_rate is not None else 0,
        slope=stats.theil_sen(surprises, moves) * step,
        verdict=track_verdict(p, hit_rate) if judged else None,
    )


def surprise_pairs(
    combinations: Sequence[tuple[str, str]],
    con: duckdb.DuckDBPyConnection | None = None,
) -> dict[tuple[str, str], dict[str, tuple[list[float], list[float]]]]:
    """For each measure × baseline, then each instrument: its surprises and release-day moves."""
    connection = con if con is not None else db.get_connection()
    pairs: dict[tuple[str, str], dict[str, tuple[list[float], list[float]]]] = {}
    for measure, baseline in combinations:
        by_instrument: dict[str, tuple[list[float], list[float]]] = {}
        for instrument in MVP_PRICE_SERIES:
            rows = connection.execute(
                "SELECT s.surprise, o.ret_1d FROM surprises s "
                "JOIN observations o ON o.event_id = s.event_id "
                "WHERE s.measure = ? AND s.baseline = ? AND o.instrument = ? ORDER BY s.event_id",
                [measure, baseline, instrument],
            ).fetchall()
            by_instrument[instrument] = ([r[0] for r in rows], [r[1] for r in rows])
        pairs[(measure, baseline)] = by_instrument
    return pairs


def track_surprises(
    rule: SurpriseRule, con: duckdb.DuckDBPyConnection | None = None
) -> dict[tuple[str, str], dict[str, SurpriseTracking]]:
    """Step 4's answer for one event's rule: each instrument × measure × baseline, with the verdict
    on the rule's first combination (core against the trend for CPI, payrolls for NFP)."""
    verdict_combination = rule.combinations[0]
    return {
        combination: {
            instrument: track_pairs(
                surprises,
                moves,
                rule.expected_sign[instrument],
                combination == verdict_combination,
                rule.noticeable,
            )
            for instrument, (surprises, moves) in by_instrument.items()
        }
        for combination, by_instrument in surprise_pairs(rule.combinations, con=con).items()
    }
