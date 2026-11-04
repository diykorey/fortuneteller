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

Roadmap step 17 (see ``docs/steps/what-follows.md``): what each market did over a day, a week and
a month after each kind of Fed decision, against its own spans of that length.
"""

from __future__ import annotations

import csv
import io
import json
import math
import random
import re
import subprocess
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from statistics import median, quantiles
from typing import NamedTuple
from zoneinfo import ZoneInfo

import duckdb

from . import db, expectations, sources, stats
from .models import DailyBar, EventInstance, Observation
from .flows import (
    EVENT_FLOWS,
    RELEASE_TIME,
    TARGET_EFFECT_DAYS,
    DatedShockFlow,
    EventFlow,
    called_live,
    event_date,
    release_date,
    stored_events,
)
from .sources import (
    FRANKFURT,
    LONDON,
    NEW_YORK,
    UTC_ZONE,
    ZURICH,
    DailyClosingPrice,
    YahooError,
)


# Step 2 — each instrument's daily closes from Yahoo (docs/steps/step-2-prices.md).


class PriceSeries(NamedTuple):
    ticker: str
    unit: str
    close: time
    zone: ZoneInfo


# Every market measured: the five MVP instruments, Europe's two stock indices
# (docs/steps/cross-country.md) and the nine more outcomes (docs/steps/more-outcomes.md), keyed by
# the exact symbol in data/seed/instruments.csv, with the Yahoo ticker each is read from, the unit
# its move is measured in (pct for prices, bps for a yield) and the local time and zone of its
# daily close: the intraday price Yahoo's close matches, measured on 2026-09 and 2026-10 data.
# Gold's and Brent's are their settlements; a stock index's the closing auction after its last
# 5-minute bar; EUR/USD's the price at 00:00 London of the bar's own day, which is how Yahoo
# stamps a currency pair, so the next London day's bar is the first to follow a US release.
MVP_PRICE_SERIES = {
    "SPY / ES": PriceSeries("^GSPC", "pct", time(16, 0), NEW_YORK),
    "UST10Y / ZN": PriceSeries("^TNX", "bps", time(15, 0), NEW_YORK),
    "DXY": PriceSeries("DX-Y.NYB", "pct", time(15, 0), NEW_YORK),
    "GC / XAU": PriceSeries("GC=F", "pct", time(13, 30), NEW_YORK),
    "VIX": PriceSeries("^VIX", "pct", time(16, 15), NEW_YORK),
    "DAX": PriceSeries("^GDAXI", "pct", time(17, 30), FRANKFURT),
    "SX5E": PriceSeries("^STOXX50E", "pct", time(17, 30), FRANKFURT),
    "BRN": PriceSeries("BZ=F", "pct", time(14, 30), NEW_YORK),
    "EURUSD": PriceSeries("EURUSD=X", "pct", time(0, 0), LONDON),
    "COMP": PriceSeries("^IXIC", "pct", time(16, 0), NEW_YORK),
    "UST5Y / ZF": PriceSeries("^FVX", "bps", time(15, 0), NEW_YORK),
    "UKX": PriceSeries("^FTSE", "pct", time(16, 30), LONDON),
    "SXXP": PriceSeries("^STOXX", "pct", time(17, 30), ZURICH),
    "BTC": PriceSeries("BTC-USD", "pct", time(23, 59), UTC_ZONE),
    "ITA": PriceSeries("ITA", "pct", time(16, 0), NEW_YORK),
    "XLE": PriceSeries("XLE", "pct", time(16, 0), NEW_YORK),
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

    All are fetched and parsed before any is stored, so a failure on one leaves ``daily_bars``
    as it was rather than half-refreshed.
    """
    fetched: dict[str, tuple[str, list[DailyClosingPrice]]] = {}
    for instrument, (ticker, *_rest) in MVP_PRICE_SERIES.items():
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


def first_reaction_day(event: EventInstance, series: PriceSeries) -> date:
    """The first day whose close can carry the event: the next day if it came at or after the close,
    both read in the market's own time zone.

    Passed to ``closing_price_before_after``, this pairs the last close before the event with the
    first after it: a Fed decision at 14:00 reacts in gold, which closes at 13:30, the next day.
    """
    announced = event.event_ts.replace(tzinfo=UTC).astimezone(series.zone)
    return announced.date() + timedelta(days=1 if announced.time() >= series.close else 0)


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
    for instrument, series in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        for flow, by_instrument in release_counts.items():
            counts = by_instrument[instrument] = ReleaseCounts()
            observations += _observe(events[flow], instrument, series, closes, counts)
    return observations, release_counts


def _observe(
    events: Sequence[EventInstance],
    instrument: str,
    series: PriceSeries,
    closes: Sequence[DailyClosingPrice],
    counts: ReleaseCounts,
) -> list[Observation]:
    observations: list[Observation] = []
    for event in events:
        pair = closing_price_before_after(closes, first_reaction_day(event, series))
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
                ret_unit=series.unit,
                ret_5m=None,
                ret_1h=None,
                ret_1d=release_move(before, after, series.unit),
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
# Fewer event days than this give no verdict (docs/steps/elections.md); chosen, not derived.
MIN_EVENT_DAYS = 10
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


# A week's move: from the close before a day to the fifth close from it (docs/steps/elections.md).
WEEK_CLOSES = 5


def weekly_moves(closes: Sequence[DailyClosingPrice], unit: str) -> dict[date, float]:
    """Each day's absolute five-day move, from the previous close to the fifth close from the day,
    keyed by the day; a window with a hole in the data is skipped, as in ``daily_moves``."""
    moves = {}
    for i in range(1, len(closes) - WEEK_CLOSES + 1):
        window = closes[i - 1 : i + WEEK_CLOSES]
        if all(
            (after.day - before.day).days <= MAX_CLOSE_GAP_DAYS
            for before, after in zip(window, window[1:], strict=False)
        ):
            moves[closes[i].day] = abs(release_move(window[0], window[-1], unit))
    return moves


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
    Under ``MIN_EVENT_DAYS`` event days there is no verdict, only ``TOO_FEW``, with no ratio and
    no ``p`` (docs/steps/elections.md).
    """
    if len(event) < MIN_EVENT_DAYS:
        middle = median(event) if event else math.nan
        return MoveComparison(
            len(event), len(other), middle, median(other), math.nan, math.nan, TOO_FEW
        )
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
    flow: EventFlow, con: duckdb.DuckDBPyConnection | None = None, week: bool = False
) -> dict[str, RawMove]:
    """Each MVP instrument's moves on the event's days against its moves on ordinary days.

    An ordinary day is one that is no stored event's reaction day, of any type: a jobs-report or
    Fed day is not a fair "other day" for CPI. A lesser flow's days stay ordinary, and its own
    event days are the ones it has alone. Ordinary days start at the flow's first reaction day on
    each market, so a flow is not judged against years it has no days in
    (docs/steps/own-years-baseline.md). A dated shock (an election, a tariff action) is alone if
    its reaction day is no other flow's, and its days end at its ``ordinary_until``
    (docs/steps/presidential-posts.md); ``week`` compares five-day moves (docs/steps/elections.md).
    """
    dated = isinstance(flow, DatedShockFlow)
    until = flow.ordinary_until if isinstance(flow, DatedShockFlow) else None
    events = stored_events(flow, con=con)
    if flow.lesser and not dated:
        shared = shared_days(flow, con=con)
        events = [e for e in events if e.event_id not in shared]
    every_event = [
        e for each in EVENT_FLOWS if not each.lesser for e in stored_events(each, con=con)
    ]
    results: dict[str, RawMove] = {}
    for instrument, series in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        days = reaction_days(closes, [first_reaction_day(event, series) for event in events])
        busy = reaction_days(closes, [first_reaction_day(event, series) for event in every_event])
        if dated:
            days -= busy
        first = min(days, default=None)
        by_era: dict[str, tuple[list[float], list[float]]] = {label: ([], []) for label, _ in ERAS}
        moves = weekly_moves(closes, series.unit) if week else daily_moves(closes, series.unit)
        for day, move in moves.items():
            if (first is not None and day < first) or (until is not None and day > until):
                continue
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
        results[instrument] = RawMove(series.unit, overall, eras)
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
    flow: EventFlow,
    combinations: Sequence[tuple[str, str]],
    con: duckdb.DuckDBPyConnection | None = None,
) -> dict[tuple[str, str], dict[str, tuple[list[float], list[float]]]]:
    """For each measure × baseline, then each instrument: one flow's surprises and release-day
    moves, its event type in its country only."""
    connection = con if con is not None else db.get_connection()
    pairs: dict[tuple[str, str], dict[str, tuple[list[float], list[float]]]] = {}
    for measure, baseline in combinations:
        by_instrument: dict[str, tuple[list[float], list[float]]] = {}
        for instrument in MVP_PRICE_SERIES:
            rows = _flow_pairs(flow, measure, baseline, instrument, connection)
            by_instrument[instrument] = ([r[2] for r in rows], [r[3] for r in rows])
        pairs[(measure, baseline)] = by_instrument
    return pairs


def shared_days(flow: EventFlow, con: duckdb.DuckDBPyConnection | None = None) -> dict[int, date]:
    """The flow's stored releases on a day that also holds another flow's, by event id; a lesser
    flow's releases share nobody's day."""
    others = {
        release_date(event)
        for each in EVENT_FLOWS
        if (each.event_type, each.country) != (flow.event_type, flow.country) and not each.lesser
        for event in stored_events(each, con=con)
    }
    return {
        event.event_id: day
        for event in stored_events(flow, con=con)
        if (day := release_date(event)) in others
    }


def _flow_pairs(
    flow: EventFlow, measure: str, baseline: str, instrument: str, con: duckdb.DuckDBPyConnection
) -> list[tuple[int, str, float, float]]:
    """One flow's (event id, month, surprise, release-day move) rows, oldest first; without its
    shared days if its rule says so."""
    rows = con.execute(
        "SELECT s.event_id, e.detail, s.surprise, o.ret_1d FROM surprises s "
        "JOIN observations o ON o.event_id = s.event_id "
        "JOIN event_instances e ON e.event_id = s.event_id "
        "WHERE e.event_type = ? AND e.country = ? "
        "AND s.measure = ? AND s.baseline = ? AND o.instrument = ? ORDER BY s.event_id",
        [flow.event_type, flow.country, measure, baseline, instrument],
    ).fetchall()
    rule = flow.surprise_rule
    shared = shared_days(flow, con=con) if rule is not None and rule.alone else {}
    return [(r[0], _month(r[0], r[1]), r[2], r[3]) for r in rows if r[0] not in shared]


def _month(event_id: int, detail: str | None) -> str:
    """The month a release reports on: its detail when that begins with one, as for every flow but
    the Fed's, whose detail says "scheduled meeting"; else the month of its day."""
    if detail is not None and re.match(r"\d{4}-\d{2}", detail):
        return detail
    return f"{event_date(event_id):%Y-%m}"


def side_by_side(
    flow: EventFlow,
    baselines: tuple[str, ...],
    leave_out: tuple[date, date] | None = None,
    con: duckdb.DuckDBPyConnection | None = None,
) -> dict[str, dict[str, SurpriseTracking]]:
    """``baselines`` of the rule's verdict measure, each judged on exactly the reports they all
    cover, per instrument; months from ``leave_out[0]`` to ``leave_out[1]`` are dropped. Empty when
    they share no report."""
    connection = con if con is not None else db.get_connection()
    rule = flow.surprise_rule
    if rule is None:
        raise ValueError(f"{flow.event_type} in {flow.country} has no surprise rule")
    measure = rule.combinations[0][0]
    results: dict[str, dict[str, SurpriseTracking]] = {b: {} for b in baselines}
    for instrument in MVP_PRICE_SERIES:
        rows = {b: _flow_pairs(flow, measure, b, instrument, connection) for b in baselines}
        shared = set.intersection(*({r[0] for r in found} for found in rows.values()))
        if leave_out is not None:
            first, last = (f"{month:%Y-%m}" for month in leave_out)
            shared -= {r[0] for r in rows[baselines[0]] if first <= r[1] <= last}
        if not shared:
            continue
        for baseline, found in rows.items():
            kept = [r for r in found if r[0] in shared]
            results[baseline][instrument] = track_pairs(
                [r[2] for r in kept],
                [r[3] for r in kept],
                rule.expected_sign[instrument],
                True,
                rule.noticeable,
            )
    return results if all(results.values()) else {}


def track_surprises(
    flow: EventFlow, con: duckdb.DuckDBPyConnection | None = None
) -> dict[tuple[str, str], dict[str, SurpriseTracking]]:
    """Step 4's answer for one flow's rule: each instrument × measure × baseline, with the verdict
    on the rule's first combination (core against the trend for CPI, payrolls for NFP)."""
    rule = flow.surprise_rule
    if rule is None:
        raise ValueError(f"{flow.event_type} in {flow.country} has no surprise rule")
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
        for combination, by_instrument in surprise_pairs(flow, rule.combinations, con=con).items()
        if combination == verdict_combination
        or any(surprises for surprises, _moves in by_instrument.values())
    }


# Rung 2 — predict the next release (docs/steps/rung-2-predict.md).

# The gate runs at every release, so it draws fewer permutations than a one-off test; p < 0.01
# still resolves.
GATE_PERMUTATIONS = 2_000


@dataclass(frozen=True)
class Prediction:
    """A link's call at one release: the day's close moves in ``direction`` (+1 up, -1 down)."""

    event_id: int
    month: str
    surprise: float
    direction: int
    move: float

    @property
    def right(self) -> bool:
        return self.direction * self.move > 0


def is_open(
    surprises: Sequence[float], moves: Sequence[float], expected_sign: int, step: float
) -> bool:
    """Whether a link passes the surprise test (``TRACKS``) on these releases.

    The hit rate is checked first: when it misses the bar the permutation test cannot change the
    answer, and it is the expensive part.
    """
    noticeable = [(s, m) for s, m in zip(surprises, moves, strict=True) if abs(s) >= step]
    if not noticeable or len(set(surprises)) < 2 or len(set(moves)) < 2:
        return False
    hits = sum(expected_sign * s * m > 0 for s, m in noticeable)
    if hits / len(noticeable) < HIT_RATE_BAR:
        return False
    p = stats.spearman_permutation_p(surprises, moves, expected_sign, GATE_PERMUTATIONS)
    return p < TRACK_P_BAR


def walk_forward(
    pairs: Sequence[tuple[int, str, float, float]], expected_sign: int, step: float
) -> list[Prediction]:
    """Replay a link's releases, oldest first, as (event id, month, surprise, move).

    At each release with a noticeable surprise the link predicts only if it is open on the releases
    before it; the prediction is the expected sign times the surprise's sign.
    """
    predictions: list[Prediction] = []
    for i, (event_id, month, surprise, move) in enumerate(pairs):
        if abs(surprise) < step:
            continue
        earlier = pairs[:i]
        if is_open([e[2] for e in earlier], [e[3] for e in earlier], expected_sign, step):
            direction = expected_sign if surprise > 0 else -expected_sign
            predictions.append(Prediction(event_id, month, surprise, direction, move))
    return predictions


# Claim 3 holds for a link if it was right this often, on at least this many predictions, and a
# coin could not have done it (binomial p under the step 4 bar).
MIN_PREDICTIONS = 30
HOLDS = "holds"
DOESNT_HOLD = "doesn't hold"
TOO_FEW = "too few"


@dataclass(frozen=True)
class LinkGrade:
    """A link's walk-forward record; ``always_right`` is how often its expected direction alone,
    whatever the surprise, would have been right on the same releases."""

    predictions: int
    right: int
    p: float
    always_right: int
    first: str | None
    verdict: str


def grade(predictions: Sequence[Prediction], expected_sign: int) -> LinkGrade:
    n = len(predictions)
    right = sum(p.right for p in predictions)
    p = stats.binomial_p(right, n)
    if n < MIN_PREDICTIONS:
        verdict = TOO_FEW
    elif right / n >= HIT_RATE_BAR and p < TRACK_P_BAR:
        verdict = HOLDS
    else:
        verdict = DOESNT_HOLD
    return LinkGrade(
        predictions=n,
        right=right,
        p=p,
        always_right=sum(expected_sign * call.move > 0 for call in predictions),
        first=predictions[0].month if predictions else None,
        verdict=verdict,
    )


# The release ``predict --actual`` asks about: after every stored one, whose ids are positive.
NEXT_RELEASE = -1


def confident_links(
    flow: EventFlow,
    baseline: str,
    con: duckdb.DuckDBPyConnection | None = None,
    next_surprise: float | None = None,
) -> dict[str, list[ConfidentCall]]:
    """Each instrument with an expected direction, replayed walk-forward against ``baseline``'s
    surprises of the flow's verdict measure, each call with its probability and band.

    With ``next_surprise``, a release after every stored one is replayed too; its call, if the link
    makes one, is the last and has ``event_id`` ``NEXT_RELEASE``."""
    connection = con if con is not None else db.get_connection()
    rule = flow.surprise_rule
    if rule is None:
        raise ValueError(f"{flow.event_type} in {flow.country} has no surprise rule")
    measure = rule.combinations[0][0]
    linked = {}
    for instrument, sign in rule.expected_sign.items():
        if sign:
            pairs = _flow_pairs(flow, measure, baseline, instrument, connection)
            if next_surprise is not None:
                pairs.append((NEXT_RELEASE, "next", next_surprise, 0.0))
            linked[instrument] = confident_calls(pairs, sign, rule.noticeable)
    return linked


# Rung 3: a call states a probability and a move band only once its link has made this many calls.
MIN_CALLS = 20


@dataclass(frozen=True)
class ConfidentCall:
    """A walk-forward call with what was known before it: ``probability`` is the link's smoothed
    record on its earlier calls, ``drift`` how often earlier noticeable releases closed the called
    way, and ``band`` the 25th to 75th percentile of the expected move, in the market's unit. All
    three are ``None`` before ``MIN_CALLS`` earlier calls; the band also when the earlier noticeable
    surprises are all equal, as no slope can be fitted."""

    call: Prediction
    probability: float | None
    drift: float | None
    band: tuple[float, float] | None


def confident_calls(
    pairs: Sequence[tuple[int, str, float, float]], expected_sign: int, step: float
) -> list[ConfidentCall]:
    """``walk_forward``'s calls on ``pairs``, each with its probability, drift probability and band,
    from the releases and calls before it."""
    calls = walk_forward(pairs, expected_sign, step)
    position = {pair[0]: i for i, pair in enumerate(pairs)}
    confident = []
    for n, call in enumerate(calls):
        if n < MIN_CALLS:
            confident.append(ConfidentCall(call, None, None, None))
            continue
        right = sum(c.right for c in calls[:n])
        earlier = [p for p in pairs[: position[call.event_id]] if abs(p[2]) >= step]
        surprises = [p[2] for p in earlier]
        moves = [p[3] for p in earlier]
        with_call = sum(call.direction * m > 0 for m in moves)
        band = None
        if len(set(surprises)) > 1:
            slope = stats.theil_sen(surprises, moves)
            low, _, high = quantiles(
                [m - slope * s for s, m in zip(surprises, moves, strict=True)],
                n=4,
                method="inclusive",
            )
            middle = slope * call.surprise
            band = (middle + low, middle + high)
        confident.append(
            ConfidentCall(call, (right + 1) / (n + 2), (with_call + 1) / (len(moves) + 2), band)
        )
    return confident


# Rung 3's rule (docs/steps/rung-3-confidence.md): a link's stated confidence is honest if, on at
# least MIN_STATED calls with a probability, each calibration group of at least MIN_GROUP calls is
# right as often as it says, its Brier score beats a coin's and the drift's with p under
# BRIER_P_BAR, and half of its moves land in their band.
MIN_STATED = 30
MIN_GROUP = 10
BRIER_P_BAR = 0.05
COIN_BRIER = 0.25
CALIBRATION_GROUPS = (("under 60%", 0.0, 0.6), ("60–70%", 0.6, 0.7), ("70% and over", 0.7, 1.01))
HONEST = "honest"
NOT_HONEST = "not honest"
TOO_CLOSE = "too close to tell"


@dataclass(frozen=True)
class CalibrationGroup:
    """Calls whose probability falls in one group: how many were right, what they stated on
    average, and the range of rights a binomial at that average allows (95%)."""

    label: str
    calls: int
    right: int
    stated: float
    allowed: tuple[int, int]

    @property
    def passes(self) -> bool:
        return self.calls < MIN_GROUP or self.allowed[0] <= self.right <= self.allowed[1]


@dataclass(frozen=True)
class ConfidenceGrade:
    """A link's calls with a probability, graded: ``missed`` names the checks it failed outright,
    ``unproven`` those it passed without p under ``BRIER_P_BAR``."""

    calls: int
    right: int
    stated: float
    brier: float
    coin_p: float
    drift_brier: float
    drift_p: float
    banded: int
    inside: int
    band_allowed: tuple[int, int]
    groups: tuple[CalibrationGroup, ...]
    by_size: tuple[tuple[int, int], tuple[int, int]]
    verdict: str
    missed: tuple[str, ...]
    unproven: tuple[str, ...]


def grade_confidence(calls: Sequence[ConfidentCall], step: float) -> ConfidenceGrade:
    stated = [
        (c.call, c.probability, c.drift, c.band)
        for c in calls
        if c.probability is not None and c.drift is not None
    ]
    n = len(stated)
    link = [(p - call.right) ** 2 for call, p, _, _ in stated]
    against_drift = [(d - call.right) ** 2 for call, _, d, _ in stated]
    brier = sum(link) / n if n else 0.0
    drift_brier = sum(against_drift) / n if n else 0.0
    coin_p = stats.sign_flip_p([COIN_BRIER - b for b in link])
    drift_p = stats.sign_flip_p([d - b for d, b in zip(against_drift, link, strict=True)])
    banded = [(call, band) for call, _, _, band in stated if band is not None]
    inside = sum(low <= call.move <= high for call, (low, high) in banded)
    band_allowed = stats.binomial_range(len(banded), 0.5)
    groups = []
    for label, low, high in CALIBRATION_GROUPS:
        members = [(call, p) for call, p, _, _ in stated if low <= p < high]
        mean = sum(p for _, p in members) / len(members) if members else 0.0
        groups.append(
            CalibrationGroup(
                label,
                len(members),
                sum(call.right for call, _ in members),
                mean,
                stats.binomial_range(len(members), mean),
            )
        )
    small = [call for call, _, _, _ in stated if abs(call.surprise) < 2 * step]
    large = [call for call, _, _, _ in stated if abs(call.surprise) >= 2 * step]
    missed = tuple(
        name
        for name, fails in (
            ("calibration", not all(g.passes for g in groups)),
            ("coin", brier >= COIN_BRIER),
            ("drift", brier >= drift_brier),
            ("band", not banded or not band_allowed[0] <= inside <= band_allowed[1]),
        )
        if fails
    )
    unproven = tuple(
        name
        for name, p in (("coin", coin_p), ("drift", drift_p))
        if p >= BRIER_P_BAR and name not in missed
    )
    if n < MIN_STATED:
        verdict = TOO_FEW
    elif missed:
        verdict = NOT_HONEST
    elif unproven:
        verdict = TOO_CLOSE
    else:
        verdict = HONEST
    return ConfidenceGrade(
        calls=n,
        right=sum(call.right for call, _, _, _ in stated),
        stated=sum(p for _, p, _, _ in stated) / n if n else 0.0,
        brier=brier,
        coin_p=coin_p,
        drift_brier=drift_brier,
        drift_p=drift_p,
        banded=len(banded),
        inside=inside,
        band_allowed=band_allowed,
        groups=tuple(groups),
        by_size=(
            (sum(call.right for call in small), len(small)),
            (sum(call.right for call in large), len(large)),
        ),
        verdict=verdict,
        missed=missed if n >= MIN_STATED else (),
        unproven=unproven if n >= MIN_STATED else (),
    )


def overall_confidence(grades: Sequence[ConfidenceGrade]) -> str:
    """One verdict from a link's grades with and without COVID: honest only if every one is."""
    verdicts = {g.verdict for g in grades}
    for verdict in (NOT_HONEST, TOO_FEW, TOO_CLOSE):
        if verdict in verdicts:
            return verdict
    return HONEST


# Rung 4: what `predict --actual` said for each link, one row per link per release.
CALLED, TOO_FEW_CALLS, SILENT, SMALL = "call", "too_few", "silent", "small"
LOG_COLUMNS = (
    "logged_at",
    "flow",
    "day",
    "actual",
    "instrument",
    "outcome",
    "direction",
    "probability",
    "band_low",
    "band_high",
)


@dataclass(frozen=True)
class LoggedCall:
    """A link's line at a live release, as stated then: ``direction`` +1 or -1 for a call (with or
    without a probability), ``None`` otherwise; ``band`` in the market's unit as in
    ``observations`` (a fraction for prices, basis points for the yield)."""

    logged_at: datetime
    flow: str
    day: date
    actual: float
    instrument: str
    outcome: str
    direction: int | None = None
    probability: float | None = None
    band: tuple[float, float] | None = None


def _blank(value: float | None) -> str:
    return "" if value is None else repr(value)


def append_calls(path: Path, calls: Sequence[LoggedCall]) -> None:
    """Adds ``calls`` to the log at ``path``, writing its header if the log is new."""
    before = path.read_text() if path.exists() else ""
    lines = io.StringIO()
    writer = csv.writer(lines, lineterminator="\n")
    if not before:
        writer.writerow(LOG_COLUMNS)
    elif not before.endswith("\n"):
        lines.write("\n")
    for c in calls:
        writer.writerow(
            [
                c.logged_at.astimezone(UTC).isoformat(timespec="seconds"),
                c.flow,
                c.day.isoformat(),
                repr(c.actual),
                c.instrument,
                c.outcome,
                "" if c.direction is None else ("up" if c.direction > 0 else "down"),
                _blank(c.probability),
                _blank(c.band[0] if c.band else None),
                _blank(c.band[1] if c.band else None),
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as log:
        log.write(lines.getvalue())


def _logged(r: dict[str, str]) -> LoggedCall:
    logged_at = datetime.fromisoformat(r["logged_at"])
    if logged_at.tzinfo is None:
        raise ValueError(f"logged_at {r['logged_at']!r} has no zone")
    if r["outcome"] not in (CALLED, TOO_FEW_CALLS, SILENT, SMALL):
        raise ValueError(f"unknown outcome {r['outcome']!r}")
    if r["direction"] not in ("", "up", "down"):
        raise ValueError(f"unknown direction {r['direction']!r}")
    if bool(r["band_low"]) != bool(r["band_high"]):
        raise ValueError("half a band")
    return LoggedCall(
        logged_at,
        r["flow"],
        date.fromisoformat(r["day"]),
        float(r["actual"]),
        r["instrument"],
        r["outcome"],
        {"up": 1, "down": -1}.get(r["direction"]),
        float(r["probability"]) if r["probability"] else None,
        (float(r["band_low"]), float(r["band_high"])) if r["band_low"] else None,
    )


def read_calls(path: Path) -> list[LoggedCall]:
    """Every row of the log at ``path``, in order; none if there is no log yet."""
    if not path.exists():
        return []
    calls = []
    with path.open(newline="") as log:
        reader = csv.DictReader(log)
        if reader.fieldnames is not None and tuple(reader.fieldnames) != LOG_COLUMNS:
            raise ValueError(f"{path} line 1 is not the log's header: {reader.fieldnames}")
        for r in reader:
            try:
                calls.append(_logged(r))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path} line {reader.line_num} cannot be read: {exc!r}") from None
    return calls


@dataclass(frozen=True)
class LiveScore:
    """One flow's logged calls: each link's graded calls, and the rows left ungraded, with why.
    A void row is never graded; a pending one is once its release, surprise and move are loaded."""

    calls: dict[str, list[ConfidentCall]]
    void: list[str]
    pending: list[str]


def score_calls(
    flow: EventFlow, rows: Sequence[LoggedCall], con: duckdb.DuckDBPyConnection | None = None
) -> LiveScore:
    """The flow's logged calls (rows with a direction) graded on the day's close, as the replay
    grades its own. A row counts if logged from the release until its market's close that day, with
    the first print typed in; its drift, which the log does not hold, is reckoned as the replay's
    from the releases before it."""
    connection = con if con is not None else db.get_connection()
    rule = flow.surprise_rule
    if rule is None:
        raise ValueError(f"{flow.event_type} in {flow.country} has no surprise rule")
    measure = rule.combinations[0][0]
    decimals = expectations.CONSENSUS_ROWS[measure][2]
    baseline = expectations.NASDAQ_CONSENSUS
    events = {release_date(event): event for event in stored_events(flow, con=connection)}
    pairs = {
        instrument: _flow_pairs(flow, measure, baseline, instrument, connection)
        for instrument, sign in rule.expected_sign.items()
        if sign
    }
    calls: dict[str, list[ConfidentCall]] = {instrument: [] for instrument in pairs}
    void: list[str] = []
    pending: list[str] = []
    made = [r for r in rows if r.flow == flow.cli_name and r.direction is not None]
    for day in sorted({r.day for r in made}):
        where = f"{flow.cli_name} {day}"
        released = datetime.combine(day, RELEASE_TIME, tzinfo=NEW_YORK)
        in_time = []
        for r in (r for r in made if r.day == day):
            series = MVP_PRICE_SERIES[r.instrument]
            close = datetime.combine(day, series.close, tzinfo=series.zone)
            if released <= r.logged_at < close:
                in_time.append(r)
            else:
                void.append(
                    f"{where} {r.instrument}: logged {r.logged_at.astimezone(NEW_YORK):%H:%M} "
                    f"New York, not from the release at {released:%H:%M} until its close at "
                    f"{close:%H:%M}"
                )
        event = events.get(day)
        if not in_time:
            continue
        if event is None:
            pending.append(f"{where}: the release is not loaded")
            continue
        stored = {
            name: (actual, surprise)
            for name, actual, surprise in connection.execute(
                "SELECT baseline, actual_mom, surprise FROM surprises "
                "WHERE event_id = ? AND measure = ?",
                [event.event_id, measure],
            ).fetchall()
        }
        if not stored:
            pending.append(f"{where}: its first print is not loaded")
            continue
        first = next(iter(stored.values()))[0]
        typo = [r for r in in_time if not expectations.published(first, decimals, r.actual)]
        if typo:
            void.append(
                f"{where}: actual {typo[0].actual:g} is not FRED's first print {first:.{decimals}f}"
            )
            in_time = [r for r in in_time if r not in typo]
        if not in_time:
            continue
        if baseline not in stored:
            pending.append(f"{where}: its consensus surprise is not loaded")
            continue
        surprise = stored[baseline][1]
        moves = dict(
            connection.execute(
                "SELECT instrument, ret_1d FROM observations WHERE event_id = ?",
                [event.event_id],
            ).fetchall()
        )
        for r in in_time:
            move = moves.get(r.instrument)
            if move is None or r.direction is None:
                pending.append(f"{where} {r.instrument}: its move is not loaded")
                continue
            earlier = [
                p
                for p in pairs[r.instrument]
                if p[0] < event.event_id and abs(p[2]) >= rule.noticeable
            ]
            drift = (sum(r.direction * p[3] > 0 for p in earlier) + 1) / (len(earlier) + 2)
            call = Prediction(event.event_id, event.detail or "", surprise, r.direction, move)
            calls[r.instrument].append(
                ConfidentCall(
                    call, r.probability, drift if r.probability is not None else None, r.band
                )
            )
    return LiveScore(calls, void, pending)


def missed_releases(
    rows: Sequence[LoggedCall], con: duckdb.DuckDBPyConnection | None = None
) -> list[str]:
    """Each stored release of a flow `live` calls, from its rule's ``logged_since``, that has no row
    in the log, oldest first."""
    logged = {(r.flow, r.day) for r in rows}
    missed = [
        (day, flow.cli_name)
        for flow in EVENT_FLOWS
        if called_live(flow) and (rule := flow.surprise_rule) is not None
        for event in stored_events(flow, con=con)
        if (day := release_date(event)) >= rule.logged_since and (flow.cli_name, day) not in logged
    ]
    return [f"{name} {day}" for day, name in sorted(missed)]


# Step 12: a person's guess, graded beside the machine's call (docs/steps/beat-the-fortune-teller.md).
GUESS_COLUMNS = ("flow", "instrument", "direction")
GITHUB_REPO = "diykorey/fortuneteller"
GUESS_FILE = re.compile(r"(\d{4}-\d{2}-\d{2})-([a-z0-9-]{1,20})\.csv")
RIGHT, WRONG, WAITING, VOID = "right", "wrong", "waiting", "void"


@dataclass(frozen=True)
class Guess:
    """One row of a guess file: ``direction`` +1 or -1; ``sha`` the commit that added the file."""

    day: date
    who: str
    flow: str
    instrument: str
    direction: int
    path: str
    sha: str


@dataclass(frozen=True)
class GradedGuess:
    """A guess and its state, with why when it is void or waiting."""

    guess: Guess
    state: str
    reason: str | None = None


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    ).stdout


def guess_files(directory: Path) -> list[tuple[str, str, bytes | None]]:
    """Every file ever added to ``directory`` along ``HEAD``'s first parents, as (path, the oldest
    commit that added it, its bytes there, ``None`` if they cannot be read); none when the directory
    does not exist. A file deleted, renamed or edited later is read as it was added."""
    if not directory.is_dir():
        return []
    log = _git(
        directory,
        "log",
        "--first-parent",
        "--diff-merges=first-parent",
        "--no-renames",
        "--diff-filter=A",
        "--relative",
        "--name-only",
        "--format=%x00%H",
        "HEAD",
        "--",
        ".",
    ).decode("utf-8", errors="replace")
    added: dict[str, str] = {}
    for block in log.split("\0")[1:]:
        sha, *paths = [line for line in block.splitlines() if line]
        for path in paths:
            added[path] = sha
    files: list[tuple[str, str, bytes | None]] = []
    for path, sha in sorted(added.items()):
        if path == ".gitkeep":
            continue
        try:
            files.append((path, sha, _git(directory, "show", f"{sha}:./{path}")))
        except subprocess.CalledProcessError:
            files.append((path, sha, None))
    return files


def read_guesses(
    files: Sequence[tuple[str, str, bytes | None]],
) -> tuple[list[Guess], list[str]]:
    """The guesses in ``files``, and a note for each file that cannot be read; its guesses are
    void, and no file can stop the others."""
    guesses: list[Guess] = []
    bad: list[str] = []
    for path, sha, content in files:
        name = GUESS_FILE.fullmatch(path)
        try:
            if name is None:
                raise ValueError("its name is not <day>-<handle>.csv, lowercase, in data/guesses/")
            if content is None:
                raise ValueError("it cannot be read from its commit")
            reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
            if tuple(reader.fieldnames or ()) != GUESS_COLUMNS:
                raise ValueError(f"its header is not {','.join(GUESS_COLUMNS)}")
            day = date.fromisoformat(name[1])
            rows = []
            for r in reader:
                if None in r or None in r.values():
                    raise ValueError(f"line {reader.line_num}: not three columns")
                if r["direction"] not in ("up", "down"):
                    raise ValueError(f"line {reader.line_num}: direction {r['direction']!r}")
                rows.append(
                    Guess(
                        day,
                        name[2],
                        r["flow"],
                        r["instrument"],
                        1 if r["direction"] == "up" else -1,
                        path,
                        sha,
                    )
                )
        except (ValueError, csv.Error) as exc:
            bad.append(f"{path}: void, {exc}")
            continue
        guesses.extend(rows)
    return guesses, bad


def merged_at(directory: Path, sha: str) -> datetime | None:
    """When GitHub merged the pull request whose merge commit is ``sha``; ``None`` when GitHub
    answers and none matches. A failure to ask is an error, so an outage cannot void a guess."""
    reply = subprocess.run(
        ["gh", "api", f"repos/{GITHUB_REPO}/commits/{sha}/pulls"],
        cwd=directory,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for pull in json.loads(reply):
        if pull.get("merge_commit_sha") == sha and pull.get("merged_at"):
            return datetime.fromisoformat(pull["merged_at"])
    return None


def score_guesses(
    guesses: Sequence[Guess],
    merged: Callable[[str], datetime | None],
    con: duckdb.DuckDBPyConnection | None = None,
) -> list[GradedGuess]:
    """Each guess right or wrong on its market's move that day, as rung 2 grades a call; void with
    why when a rule fails; waiting while its release or move is not loaded."""
    connection = con if con is not None else db.get_connection()
    by_name = {flow.cli_name: flow for flow in EVENT_FLOWS}
    times: dict[str, datetime | None] = {}
    seen: set[tuple[str, str, str]] = set()
    releases: dict[str, dict[date, EventInstance]] = {}
    graded = []
    for g in guesses:
        flow = by_name.get(g.flow)
        rule = flow.surprise_rule if flow is not None else None
        released = datetime.combine(g.day, RELEASE_TIME, tzinfo=NEW_YORK)
        if g.sha not in times:
            times[g.sha] = merged(g.sha)
        at = times[g.sha]
        reason = None
        if flow is None or rule is None or not called_live(flow):
            reason = f"{g.flow} is not a flow `live` calls"
        elif not rule.expected_sign.get(g.instrument):
            reason = f"{g.instrument} is not one of {g.flow}'s links"
        elif at is None:
            reason = "not merged through a pull request"
        elif at >= released:
            reason = (
                f"merged {at.astimezone(NEW_YORK):%Y-%m-%d %H:%M} New York, not before "
                f"{released:%H:%M} on {g.day}"
            )
        elif (g.path, g.flow, g.instrument) in seen:
            reason = f"repeats {g.flow} {g.instrument} in its file"
        seen.add((g.path, g.flow, g.instrument))
        if reason is not None or flow is None:
            graded.append(GradedGuess(g, VOID, reason))
            continue
        if flow.cli_name not in releases:
            releases[flow.cli_name] = {
                release_date(e): e for e in stored_events(flow, con=connection)
            }
        events = releases[flow.cli_name]
        event = events.get(g.day)
        if event is None:
            if any(day > g.day for day in events):
                graded.append(GradedGuess(g, VOID, f"{g.flow} had no release on {g.day}"))
            else:
                graded.append(GradedGuess(g, WAITING, "the release is not loaded"))
            continue
        move = connection.execute(
            "SELECT ret_1d FROM observations WHERE event_id = ? AND instrument = ?",
            [event.event_id, g.instrument],
        ).fetchone()
        if move is None or move[0] is None:
            graded.append(GradedGuess(g, WAITING, "its move is not loaded"))
            continue
        graded.append(GradedGuess(g, RIGHT if g.direction * move[0] > 0 else WRONG))
    return graded


# Step 17 — what follows a Fed decision, over spans (docs/steps/what-follows.md).


SPANS = {"day": 1, "week": 5, "month": 21}
FOLLOW_P_BAR = 0.01
CUT, HOLD, HIKE = "cut", "hold", "hike"
KINDS = (CUT, HOLD, HIKE)
UP, SAME, DOWN = "up", "about the same", "down"
OUTCOMES = (UP, SAME, DOWN)
CANT_SAY = "can't say"
# A placebo decision sits this many closes before, and after, the real one, and never less than
# the span, so the two spans share no move (docs/steps/what-follows.md, amended 2026-11-04).
PLACEBO_SHIFT = 10
# A walk-forward record holds only this far above the mean base rate of its answers.
ABOVE_BASE = 0.10


def fed_kinds(events: Iterable[EventInstance], rates: Mapping[date, float]) -> dict[int, str]:
    """Each decision's kind by event id, from the target rate ``TARGET_EFFECT_DAYS`` after its New
    York day against the day before; a decision with either rate missing has none."""
    kinds = {}
    for event in events:
        day = release_date(event)
        before = rates.get(day - timedelta(days=1))
        after = rates.get(day + timedelta(days=TARGET_EFFECT_DAYS))
        if before is not None and after is not None:
            kinds[event.event_id] = HOLD if after == before else CUT if after < before else HIKE
    return kinds


class Span(NamedTuple):
    start: date
    end: date
    move: float


def span_moves(closes: Sequence[DailyClosingPrice], unit: str, c: int) -> dict[date, Span]:
    """Every span of ``c`` closes keyed on its first close: from the close before it to the
    ``c``-th close from it, signed; a span with a hole in the data is skipped, as in
    ``weekly_moves``."""
    spans = {}
    for i in range(1, len(closes) - c + 1):
        window = closes[i - 1 : i + c]
        if all(
            (after.day - before.day).days <= MAX_CLOSE_GAP_DAYS
            for before, after in zip(window, window[1:], strict=False)
        ):
            spans[closes[i].day] = Span(
                window[0].day, window[-1].day, release_move(window[0], window[-1], unit)
            )
    return spans


def outcome(move: float, cut: float) -> str:
    if move == 0 or abs(move) < cut:
        return SAME
    return UP if move > 0 else DOWN


@dataclass(frozen=True)
class Base:
    """A market's spans of one length: the cut under which a move is about the same, and each
    outcome's share."""

    cut: float
    rates: dict[str, float]

    @property
    def up_share(self) -> float:
        moved = self.rates[UP] + self.rates[DOWN]
        return self.rates[UP] / moved if moved else math.nan


def base_of(moves: Sequence[float]) -> Base | None:
    """The cut at the lower third of absolute moves and each outcome's share; none under two."""
    if len(moves) < 2:
        return None
    cut = quantiles([abs(move) for move in moves], n=3, method="inclusive")[0]
    counts = {o: 0 for o in OUTCOMES}
    for move in moves:
        counts[outcome(move, cut)] += 1
    return Base(cut, {o: counts[o] / len(moves) for o in OUTCOMES})


def span_answer(counts: Mapping[str, int], same_rate: float, up_share: float) -> tuple[str, float]:
    """The outcome after a kind of event, with its chance: *about the same* against its rate on all
    events, *up* and *down* only on the events that moved, against the base's share of up among
    its spans that moved, so a market that only moves more reads as no direction."""
    n = sum(counts[o] for o in OUTCOMES)
    if n < MIN_EVENT_DAYS:
        return TOO_FEW, math.nan
    chances = {}
    if 0 < same_rate < 1:
        chances[SAME] = stats.binomial_tail(counts[SAME], n, same_rate)
    moved = counts[UP] + counts[DOWN]
    if moved and 0 < up_share < 1:
        chances[UP] = stats.binomial_tail(counts[UP], moved, up_share)
        chances[DOWN] = stats.binomial_tail(counts[DOWN], moved, 1 - up_share)
    if not chances:
        return CANT_SAY, math.nan
    best = min(chances.values())
    winners = [o for o, chance in chances.items() if chance == best]
    if best < FOLLOW_P_BAR and len(winners) == 1:
        return winners[0], best
    return CANT_SAY, best


def _answer(spans: Iterable[Span], base: Base) -> tuple[str, float, dict[str, int]]:
    counts = {o: 0 for o in OUTCOMES}
    for span in spans:
        counts[outcome(span.move, base.cut)] += 1
    answer, chance = span_answer(counts, base.rates[SAME], base.up_share)
    return answer, chance, counts


@dataclass(frozen=True)
class Follow:
    """One kind's record on one market over one span length."""

    counts: dict[str, int]
    overlapped: int
    holes: int
    base: Base | None
    answer: str
    chance: float
    period: bool
    graded: int
    right: int
    walk_chance: float
    verdict: str


def follow_market(
    decisions: Sequence[tuple[date, str]], closes: Sequence[DailyClosingPrice], unit: str, c: int
) -> dict[str, Follow]:
    """Each kind's record on one market over spans of ``c`` closes.

    ``decisions`` are (first reaction day on this market, kind), oldest first. A decision is left
    out if its span starts before the end of the last one kept, whatever its kind, or has a hole.
    """
    spans = span_moves(closes, unit, c)
    index = {close.day: i for i, close in enumerate(closes)}
    keys: dict[str, list[date]] = {kind: [] for kind in KINDS}
    overlapped = dict.fromkeys(KINDS, 0)
    holes = dict.fromkeys(KINDS, 0)
    reacted: set[date] = set()
    last_end: date | None = None
    for day, kind in decisions:
        pair = closing_price_before_after(closes, day)
        if pair == BEFORE_HISTORY or day > closes[-1].day:
            continue
        if isinstance(pair, str):
            holes[kind] += 1
            continue
        key = pair[1].day
        reacted.add(key)
        if key not in spans:
            if index[key] + c <= len(closes):
                holes[kind] += 1
            continue
        if last_end is not None and spans[key].start < last_end:
            overlapped[kind] += 1
            continue
        keys[kind].append(key)
        last_end = spans[key].end
    by_end = sorted(spans.items(), key=lambda item: item[1].end)
    return {
        kind: _follow(
            keys[kind], spans, by_end, closes, index, reacted, overlapped[kind], holes[kind], c
        )
        for kind in KINDS
    }


def answer_before(
    keys: Sequence[date],
    j: int,
    spans: Mapping[date, Span],
    by_end: Sequence[tuple[date, Span]],
    ends: Sequence[date] | None = None,
) -> tuple[str, Base] | None:
    """The walk-forward answer at the ``j``-th decision, and the base it used: from the decisions
    and the base spans that ended on or before its close before, never anything later; none under
    ``MIN_EVENT_DAYS`` earlier decisions."""
    before = spans[keys[j]].start
    earlier = [spans[k] for k in keys[:j] if spans[k].end <= before]
    if len(earlier) < MIN_EVENT_DAYS:
        return None
    upto = bisect_right(ends if ends is not None else [span.end for _, span in by_end], before)
    base = base_of([span.move for k, span in by_end[:upto] if k >= keys[0]])
    if base is None:
        return None
    return _answer(earlier, base)[0], base


def _follow(
    keys: Sequence[date],
    spans: Mapping[date, Span],
    by_end: Sequence[tuple[date, Span]],
    closes: Sequence[DailyClosingPrice],
    index: Mapping[date, int],
    reacted: set[date],
    overlapped: int,
    holes: int,
    c: int,
) -> Follow:
    empty = {o: 0 for o in OUTCOMES}
    if not keys:
        return Follow(
            empty, overlapped, holes, None, TOO_FEW, math.nan, False, 0, 0, math.nan, TOO_FEW
        )
    start = keys[0]
    base = base_of([span.move for key, span in spans.items() if key >= start])
    if base is None:
        return Follow(
            empty, overlapped, holes, None, TOO_FEW, math.nan, False, 0, 0, math.nan, TOO_FEW
        )
    answer, chance, counts = _answer((spans[key] for key in keys), base)
    period = False
    if answer in OUTCOMES:
        reach = max(PLACEBO_SHIFT, c)
        for shift in (-reach, reach):
            moved = []
            for key in keys:
                i = index[key] + shift
                if 0 <= i < len(closes) and (day := closes[i].day) in spans and day not in reacted:
                    moved.append(spans[day])
            if _answer(moved, base)[0] == answer:
                period = True
    rates: list[float] = []
    right = 0
    ends = [span.end for _, span in by_end]
    for j, key in enumerate(keys):
        then = answer_before(keys, j, spans, by_end, ends)
        if then is not None and then[0] in OUTCOMES:
            said, base_then = then
            rates.append(base_then.rates[said])
            right += outcome(spans[key].move, base_then.cut) == said
    graded = len(rates)
    walk_chance = stats.poisson_binomial_tail(right, rates) if rates else math.nan
    if graded < MIN_PREDICTIONS:
        verdict = TOO_FEW
    elif (
        right / graded >= HIT_RATE_BAR
        and right / graded >= sum(rates) / graded + ABOVE_BASE
        and walk_chance < FOLLOW_P_BAR
    ):
        verdict = HOLDS
    else:
        verdict = DOESNT_HOLD
    return Follow(
        counts, overlapped, holes, base, answer, chance, period, graded, right, walk_chance, verdict
    )


def follow_decisions(
    flow: EventFlow, rates: Mapping[date, float], con: duckdb.DuckDBPyConnection | None = None
) -> tuple[list[EventInstance], dict[int, str], list[tuple[str, str, str, Follow]]]:
    """Every stored decision of ``flow``, its kinds, and a record per kind, span and market, in that
    order."""
    events = stored_events(flow, con=con)
    kinds = fed_kinds(events, rates)
    cells = []
    by_market = {}
    for instrument, series in MVP_PRICE_SERIES.items():
        closes = stored_closes(instrument, con=con)
        decisions = [
            (first_reaction_day(e, series), kinds[e.event_id])
            for e in events
            if e.event_id in kinds
        ]
        by_market[instrument] = {
            span: follow_market(decisions, closes, series.unit, c) for span, c in SPANS.items()
        }
    for kind in KINDS:
        for span in SPANS:
            for instrument in MVP_PRICE_SERIES:
                cells.append((kind, span, instrument, by_market[instrument][span][kind]))
    return events, kinds, cells
