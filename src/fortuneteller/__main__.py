"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``); ``load-releases`` loads the CPI and jobs-report release
histories from FRED (MVP step 1 ``study``) and the Fed's decisions (rung 1); ``load-prices`` loads
every market's daily closes, from Yahoo and FRED, and measures their move around each release (MVP step 2);
``raw-move`` compares each instrument's moves on an event's days with ordinary days, which no
stored event touched (MVP step 3); ``load-surprises`` stores each release's CPI and payroll surprise
and ``surprise`` measures how the moves follow it (MVP step 4, rung 1); ``scoreboard`` writes what
they print, and the graded calls, as the page's data (roadmap step 5).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import math
import statistics
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from importlib.resources import files
from typing import NamedTuple

import duckdb

from . import stats, db, expectations, flows, seed, sources, study
from .config import settings
from .models import EventInstance, Surprise

Handler = Callable[[argparse.Namespace], int]


def _init(_args: argparse.Namespace) -> int:
    db.init_db()
    print(f"init: created {settings.db_path}")
    return 0


def _seed(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    counts = seed.load_all(con=con)
    for table, count in counts.items():
        print(f"{table}: {count}")
    return 0


def _query_demo(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    row = seed.query_demo(con=con)
    if row is None:
        print("query-demo: no effect-size rows (run `fortuneteller seed` first)")
        return 1
    print(
        f"{row.event_type} x {row.instrument}: direction={row.direction} "
        f"magnitude={row.typical_magnitude} confidence={row.direction_confidence}"
    )
    return 0


def _fred_key(command: str) -> str:
    api_key = settings.fred_api_key.get_secret_value() if settings.fred_api_key else ""
    if not api_key:
        print(f"{command}: FT_FRED_API_KEY is not set (see docs/accounts.md)", file=sys.stderr)
    return api_key


def _load_releases(_args: argparse.Namespace) -> int:
    api_key = _fred_key("load-releases")
    if not api_key:
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    try:
        report = flows.load_releases(api_key, con=con)
    except (sources.FredError, sources.FedError, sources.CalendarError, ValueError) as exc:
        print(f"load-releases: {exc}", file=sys.stderr)
        return 1
    for line in report:
        print(line)
    return 0


def describe_release_counts(instrument: str, counts: study.ReleaseCounts) -> str:
    """One report line: how many releases were measured for ``instrument``, and why others were not."""
    parts = [f"{instrument:<12} {counts.measured} observations"]
    if counts.skipped_before_history:
        parts.append(f"{counts.skipped_before_history} skipped (before its history)")
    if counts.skipped_no_close_nearby:
        gap = study.MAX_CLOSE_GAP_DAYS
        parts.append(f"{counts.skipped_no_close_nearby} skipped (no close within {gap} days)")
    return ", ".join(parts)


def _load_prices(args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    if args.companies:
        return _load_companies(con, args.seed)
    if db.count_rows("event_instances", con=con) == 0:
        print(
            "load-prices: no releases stored; run `fortuneteller load-releases` first",
            file=sys.stderr,
        )
        return 1
    api_key = _fred_key("load-prices")
    if not api_key:
        return 1
    try:
        study.load_daily_bars(api_key, con=con)
        release_counts = study.store_observations(con=con)
    except (sources.YahooError, sources.FredError, ValueError) as exc:
        print(f"load-prices: {exc}", file=sys.stderr)
        return 1
    for flow, by_instrument in release_counts.items():
        print(flow.event_type)
        for instrument, counts in by_instrument.items():
            print(describe_release_counts(instrument, counts))
        first = next(iter(by_instrument.values()))
        releases = first.measured + first.skipped_before_history + first.skipped_no_close_nearby
        total = sum(counts.measured for counts in by_instrument.values())
        print(f"{len(by_instrument)} instruments × {releases} releases = {total} observations")
    # The companies too, so the evening keeps them current (docs/steps/ask-earnings.md); one Yahoo
    # fails on is reported and left out, as the page shows it, and does not fail the load.
    tickers = company_tickers()
    loaded, failed = study.load_company_bars(tickers, con=con)
    for note in failed:
        print(f"load-prices: {note}", file=sys.stderr)
    print(f"{len(loaded)} of {len(tickers)} companies loaded")
    return 0


def company_tickers() -> list[str]:
    """The CEO flow's, the earnings' and the S&P 500 additions' companies, each once, in their
    seeds' order."""
    tickers: list[str] = []
    company_flows = (flows.CEO_FLOW, flows.EARNINGS_FLOW, flows.ADDITIONS_FLOW)
    for seed_file in (flow.seed_file for flow in company_flows):
        with (settings.seed_dir / seed_file).open(newline="") as file:
            tickers += [row["ticker"] for row in csv.DictReader(file)]
    return list(dict.fromkeys(tickers))


def _load_companies(con: duckdb.DuckDBPyConnection, seed: Path | None = None) -> int:
    """The companies' closes alone, the evening's or, with ``seed``, that seed's (step 36,
    docs/steps/earnings-sp500.md); a company Yahoo fails on is reported, the rest load, and the
    exit is 1."""
    if seed is None:
        tickers = company_tickers()
    else:
        with seed.open(newline="") as file:
            tickers = list(dict.fromkeys(row["ticker"] for row in csv.DictReader(file)))
    counts, failed = study.load_company_bars(tickers, con=con)
    for ticker, n in counts.items():
        print(f"{ticker}: {n} closes")
    for note in failed:
        print(f"load-prices: {note}", file=sys.stderr)
    print(f"{len(counts)} of {len(tickers)} companies loaded")
    return 1 if failed else 0


def describe_surprises(rows: Sequence[Surprise]) -> list[str]:
    """One report line per measure and expected value, in the order the rows came: how many
    surprises, over which release days."""
    lines = []
    for measure, baseline in dict.fromkeys((r.measure, r.baseline) for r in rows):
        ids = sorted(r.event_id for r in rows if r.measure == measure and r.baseline == baseline)
        first, last = (flows.event_date(i) for i in (ids[0], ids[-1]))
        lines.append(
            f"{measure:<9} {baseline:<10} {len(ids):>3} surprises, released {first} … {last}"
        )
    return lines


# One-sided p < 0.01 on a rank correlation of n pairs needs about this times 1/sqrt(n - 1).
Z_ONE_SIDED_01 = 2.326


def describe_tone(
    load: flows.ToneLoad,
    con: duckdb.DuckDBPyConnection,
    signed: Sequence[str] = flows.TONE_SIGNED,
    word: str = "tone",
    checks: Sequence[tuple[str, bool]] = (),
) -> list[str]:
    """``load-tone``'s report, written before any move is read: the statements scored, each signed
    link's count of holds with a non-zero surprise and a move (shared days left out) with the
    smallest correlation it could detect, the noticeable surprise, and the holds with the highest
    and the lowest tone, with their phrases; ``load-sentiment``'s too, with its checks against
    the paper."""
    toned = sum(tone is not None for tone, _ in load.tones.values())
    holds = {i: s for i, s in load.surprises.items() if i in load.holds}
    shared = study.shared_days(flows.FED_FLOW, con=con)
    lone = {i: s for i, s in holds.items() if i not in shared}
    lines = [
        f"statements: {len(load.tones)} since {flows.TONE_FROM}, {toned} with a {word}, "
        f"{len(load.holds)} holds",
        f"surprises: {len(load.surprises)} on every decision, {len(holds)} on holds, "
        f"{len(lone)} of them alone on their day",
        "signed links, holds with a non-zero surprise and a move:",
    ]
    moving = [i for i, s in lone.items() if s != 0]
    for instrument in signed:
        n = 0
        if moving:
            marks = ", ".join("?" * len(moving))
            (n,) = con.execute(
                "SELECT count(*) FROM observations WHERE instrument = ? AND ret_1d IS NOT NULL "
                f"AND event_id IN ({marks})",
                [instrument, *moving],
            ).fetchone() or (0,)
        smallest = f"{Z_ONE_SIDED_01 / math.sqrt(n - 1):.2f}" if n > 1 else "-"
        verdict = "" if n >= flows.TONE_MIN_PAIRS else ", too few"
        lines.append(f"  {instrument:<12} {n:>4}, smallest detectable {smallest}{verdict}")
    sizes = sorted(abs(s) for s in lone.values() if s != 0)
    lines.append(f"noticeable: {statistics.median(sizes):.4f}" if sizes else "noticeable: none")
    lines += [f"check, {'pass' if passed else 'fail'}: {name}" for name, passed in checks]
    by_tone = sorted(
        (tone, flows.event_date(i), phrases)
        for i, (tone, phrases) in load.tones.items()
        if i in load.holds and tone is not None
    )
    for label, chosen in (("lowest", by_tone[:5]), ("highest", by_tone[::-1][:5])):
        lines.append(f"holds with the {label} {word}:")
        for tone, day, phrases in chosen:
            lines.append(f"  {day} {tone:.2f}: {'; '.join(phrases)}")
    return lines


def _load_tone(_args: argparse.Namespace) -> int:
    api_key = _fred_key("load-tone")
    if not api_key:
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    try:
        load = flows.load_tone(api_key, settings.cache_dir, con=con)
    except (sources.FredError, sources.FedError, ValueError) as exc:
        print(f"load-tone: {exc}", file=sys.stderr)
        return 1
    for line in describe_tone(load, con):
        print(line)
    return 0


def _load_sentiment(_args: argparse.Namespace) -> int:
    api_key = _fred_key("load-sentiment")
    if not api_key:
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    try:
        load = flows.load_sentiment(api_key, settings.cache_dir, con=con)
    except (sources.FredError, sources.FedError, ValueError) as exc:
        print(f"load-sentiment: {exc}", file=sys.stderr)
        return 1
    checks = flows.sentiment_checks(load)
    for line in describe_tone(load, con, flows.SENTIMENT_SIGNED, "sentiment", checks):
        print(line)
    if not all(passed for _, passed in checks):
        print("not stored: a check against the paper failed")
        return 1
    print(f"stored: {flows.store_sentiment(load, con=con)} surprises")
    return 0


def _load_surprises(_args: argparse.Namespace) -> int:
    api_key = _fred_key("load-surprises")
    if not api_key:
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    try:
        rows = flows.load_surprises(api_key, con=con)
    except (sources.FredError, sources.ClevelandError, sources.CalendarError, ValueError) as exc:
        print(f"load-surprises: {exc}", file=sys.stderr)
        return 1
    for line in describe_surprises(rows):
        print(line)
    for source in expectations.EXPECTATION_SOURCES:
        if isinstance(source, expectations.NasdaqConsensus):
            for note in source.left_out:
                print(f"  no consensus: {note}")
            for note in source.filled_in:
                print(f"  Nasdaq has none, TradingView's forecast taken: {note}")
    return 0


def _direction(sign: int) -> str:
    return {1: "up", -1: "down"}.get(sign, "either")


def _hit_rate(tracking: study.SurpriseTracking) -> str:
    if tracking.hit_rate is None:
        return "—"
    return f"{tracking.hit_rate:.0%} ({tracking.hit_n})"


def describe_surprise_tracking(
    results: dict[tuple[str, str], dict[str, study.SurpriseTracking]],
    rule: flows.SurpriseRule,
) -> list[str]:
    """The report: the verdict table, the context table if the rule has one, and the rule."""
    verdict_combination = rule.combinations[0]
    lines = [
        f"{verdict_combination[0]} against {_source_label(verdict_combination[1])}",
        f"instrument   n    expected  rank corr  p       hit rate (n)  per {rule.step:<5}  verdict",
    ]
    for instrument, t in results.get(verdict_combination, {}).items():
        unit = study.MVP_PRICE_SERIES[instrument].unit
        lines.append(
            f"{instrument:<12} {t.n:<4} {_direction(rule.expected_sign[instrument]):<9} "
            f"{t.rank_corr:<10.2f} {t.p:<7.4f} {_hit_rate(t):<13} "
            f"{_move_size(t.slope, unit):<10} {t.verdict}"
        )
    width = max(10, *(len(baseline) for _measure, baseline in rule.combinations))
    named = max(9, *(len(measure) for measure, _baseline in rule.combinations))
    if len(rule.combinations) > 1:
        lines += [
            "",
            "context, no verdict",
            f"instrument   {'measure':<{named}} {'baseline':<{width}} n    rank corr  p       "
            "hit rate (n)",
        ]
    for (measure, baseline), by_instrument in results.items():
        if (measure, baseline) == verdict_combination:
            continue
        for instrument, t in by_instrument.items():
            lines.append(
                f"{instrument:<12} {measure:<{named}} {baseline:<{width}} {t.n:<4} "
                f"{t.rank_corr:<10.2f} {t.p:<7.4f} {_hit_rate(t)}"
            )
    lines += ["", _track_rule()]
    return [line.rstrip() for line in lines]


def _move_rule() -> str:
    return (
        f"{study.MOVES} = ratio >= {study.MOVE_RATIO_BAR:.2f} and p < {study.MOVE_P_BAR}; "
        f"{study.UNCLEAR} = one of the two; {study.DOESNT_MOVE} = neither; "
        f"other = days with no {_any_of(f.label for f in flows.EVENT_FLOWS if not f.lesser)} reaction"
    )


def _track_rule() -> str:
    return (
        f"{study.TRACKS} = corr as expected, p < {study.TRACK_P_BAR}, hit rate >= "
        f"{study.HIT_RATE_BAR:.0%}; {study.UNCLEAR} = one of the two; "
        f"{study.DOESNT_TRACK} = neither"
    )


def _hold_rule() -> str:
    return (
        f"{study.HOLDS} = right on at least {study.HIT_RATE_BAR:.0%} of at least "
        f"{study.MIN_PREDICTIONS} predictions, binomial p < {study.TRACK_P_BAR} against 50%; "
        f"{study.TOO_FEW} = under {study.MIN_PREDICTIONS} predictions"
    )


def _surprises_stored(
    flow: flows.EventFlow, measure: str, baseline: str, con: duckdb.DuckDBPyConnection
) -> bool:
    """Whether any of the flow's releases has its surprise of ``measure`` against ``baseline``."""
    stored = con.execute(
        "SELECT count(*) FROM surprises s JOIN event_instances e ON e.event_id = s.event_id "
        "WHERE e.event_type = ? AND e.country = ? AND s.measure = ? AND s.baseline = ?",
        [flow.event_type, flow.country, measure, baseline],
    ).fetchone()
    return stored is not None and stored[0] > 0


def _surprise_command(flow: flows.EventFlow) -> str:
    """The command that stores a flow's surprises: the Fed's sentiment is loaded on its own."""
    return "load-sentiment" if flow is flows.FED_FLOW else "load-surprises"


def _surprise(args: argparse.Namespace) -> int:
    flow = flows.flow_named(args.event)
    rule = flow.surprise_rule
    if rule is None:
        print(
            f"surprise: {flow.event_type} has no surprise: no free record of what the market "
            "expected",
            file=sys.stderr,
        )
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    measure, baseline = rule.combinations[0]
    for missing, command in (
        (not flows.stored_events(flow, con=con), "load-releases"),
        (db.count_rows("observations", con=con) == 0, "load-prices"),
        (not _surprises_stored(flow, measure, baseline, con), _surprise_command(flow)),
    ):
        if missing:
            print(
                f"surprise: nothing for {args.event} yet; run `fortuneteller {command}` first",
                file=sys.stderr,
            )
            return 1
    results = study.track_surprises(flow, con=con)
    for line in describe_surprise_tracking(results, rule):
        print(line)
    covid = expectations.COVID_MONTHS
    for pair in rule.compared:
        for leave_out, scope in ((None, "all"), (covid, f"without {_months_between(*covid)}")):
            side_by_side = study.side_by_side(flow, pair, leave_out, con=con)
            if not side_by_side:
                continue
            for line in describe_side_by_side(side_by_side, rule, scope):
                print(line)
    for line in describe_shared_days(flow, con):
        print(line)
    return 0


def describe_shared_days(flow: flows.EventFlow, con: duckdb.DuckDBPyConnection) -> list[str]:
    """The releases a rule leaves out for sharing their day with another flow's release."""
    rule = flow.surprise_rule
    days = sorted(study.shared_days(flow, con=con).values()) if rule and rule.alone else []
    if not days:
        return []
    return [
        "",
        f"left out: {len(days)} {flow.label} releases on a day with another event's release",
        *textwrap.wrap(", ".join(f"{day}" for day in days), 100),
    ]


def _months_between(first: date, last: date) -> str:
    return f"{first:%Y-%m} … {last:%Y-%m}"


def describe_side_by_side(
    results: dict[str, dict[str, study.SurpriseTracking]], rule: flows.SurpriseRule, scope: str
) -> list[str]:
    """The compared baselines judged on the same reports; the official verdict stays above."""
    measure = rule.combinations[0][0]
    width = max(14, *(len(baseline) for baseline in results))
    lines = [
        "",
        f"{measure} against {' and '.join(_source_label(b) for b in results)}, "
        f"on the same reports ({scope}); not the official verdict",
        f"instrument   {'baseline':<{width}} n    rank corr  p       hit rate (n)  "
        f"per {rule.step:<5}  verdict",
    ]
    for instrument in study.MVP_PRICE_SERIES:
        unit = study.MVP_PRICE_SERIES[instrument].unit
        for baseline, by_instrument in results.items():
            t = by_instrument[instrument]
            lines.append(
                f"{instrument:<12} {baseline:<{width}} {t.n:<4} {t.rank_corr:<10.2f} {t.p:<7.4f} "
                f"{_hit_rate(t):<13} {_move_size(t.slope, unit):<10} {t.verdict}"
            )
    return [line.rstrip() for line in lines]


def _source_label(name: str) -> str:
    return next(s.label for s in expectations.EXPECTATION_SOURCES if s.name == name)


def _any_of(labels: Iterable[str]) -> str:
    *rest, last = labels
    return f"{', '.join(rest)} or {last}" if rest else last


def _move_size(value: float, unit: str, signed: bool = False) -> str:
    if math.isnan(value):
        return "—"
    sign = "+" if signed else ""
    return f"{value:{sign}.1f} bp" if unit == "bps" else f"{value * 100:{sign}.2f}%"


def _ratio_p(c: study.MoveComparison) -> str:
    if c.verdict == study.TOO_FEW:
        return f"{'—':>5}  {'—':<6}"
    return f"{c.ratio:>5.2f}  {c.p:.4f}"


def describe_raw_moves(results: dict[str, study.RawMove], label: str) -> list[str]:
    """The report: a verdict line per instrument, an era line per instrument, and the rule.

    ``label`` names the event in the headers: a three-letter name keeps the columns aligned.
    """
    lines = [f"instrument   {label} days  median {label}  median other  ratio  p       verdict"]
    for instrument, raw in results.items():
        c = raw.overall
        lines.append(
            f"{instrument:<12} {c.event_days:>8}  {_move_size(c.median_event, raw.unit):>10}  "
            f"{_move_size(c.median_other, raw.unit):>12}  {_ratio_p(c)}  {c.verdict}"
        )
    eras = next(iter(results.values())).eras
    lines += [
        "",
        f"by era: ratio ({label} days)",
        " ".join(["instrument  ", *(f"{e:<12}" for e in eras)]),
    ]
    for instrument, raw in results.items():
        cells = [
            "—" if era.ratio is None else f"{era.ratio:.2f} ({era.event_days})"
            for era in raw.eras.values()
        ]
        lines.append(" ".join([f"{instrument:<12}", *(f"{cell:<12}" for cell in cells)]).rstrip())
    lines += ["", _move_rule()]
    return [line.rstrip() for line in lines]


def _raw_move(args: argparse.Namespace) -> int:
    flow = flows.flow_named(args.event)
    event_type = flow.event_type
    con = db.get_connection()
    db.init_db(con=con)
    if not flows.stored_events(flow, con=con):
        print(
            f"raw-move: no {event_type} releases stored; run `fortuneteller load-releases` first",
            file=sys.stderr,
        )
        return 1
    if db.count_rows("daily_bars", con=con) == 0:
        print(
            "raw-move: no daily_bars stored; run `fortuneteller load-prices` first", file=sys.stderr
        )
        return 1
    try:
        results = study.measure_raw_moves(flow, con=con, week=args.week)
    except ValueError as exc:
        print(f"raw-move: {exc}", file=sys.stderr)
        return 1
    if args.week:
        print(
            f"over a week: the move from the close before each day to the {study.WEEK_CLOSES}th close"
        )
    for line in describe_raw_moves(results, label=flow.label):
        print(line)
    return 0


def describe_follows(
    events: Sequence[EventInstance],
    kinds: Mapping[int, str],
    cells: Sequence[tuple[str, str, str, study.Follow]],
    order: Sequence[str] = study.KINDS,
    noun: str = "Fed decisions",
    after: bool = False,
    long: bool = False,
    marked: tuple[str, str] | None = None,
) -> list[str]:
    """``follows``' table: a row per kind, span and market, then what chance alone would give;
    with ``long``, each cell's answer counting each cycle once. A ``marked`` span and market is
    near the kind itself: each kind's cell there prints ``(the kind)`` and is left out of the
    chance line (docs/steps/opec.md)."""
    counted = [kinds[e.event_id] for e in events if e.event_id in kinds]
    first, last = (flows.release_date(e) for e in (events[0], events[-1]))
    plural = (
        "s"
        if tuple(order)
        in (
            study.KINDS,
            (study.SCANDAL,),
            (study.VIOLENT_ACT,),
            (study.HACK,),
            (study.LANDFALL,),
            (study.FLOOD,),
        )
        else ""
    )
    width = max(5, *(len(kind) for kind in order))
    span_width = max(6, *(len(span) + 1 for _, span, _, _ in cells))
    lines = [
        f"follows: {len(events)} {noun} {first} … {last}: "
        + ", ".join(f"{counted.count(kind)} {kind}{plural}" for kind in order)
        + (", spans from the reaction close" if after else ""),
        f"{'kind':<{width}} {'span':<{span_width}} market        n  up same down  out/hole  base up/same/down  "
        "answer          chance  placebo  "
        + ("cycles             " if long else "")
        + "walk-forward",
    ]
    for kind, span, market, f in cells:
        n = sum(f.counts.values())
        base = "/".join(f"{f.base.rates[o]:.2f}" for o in study.OUTCOMES) if f.base else "—"
        chance = f"{f.chance:.4f}" if not math.isnan(f.chance) else "—"
        placebo = "period" if f.period else "-"
        walk = f"{f.graded}: {f.right} right, {f.verdict}"
        if long and f.by_cycle is not None:
            walk = f"{f'{f.by_cycle[0]}: {f.by_cycle[1]}':<18} {walk}"
        if (span, market) == marked:
            walk += "  (the kind)"
        lines.append(
            f"{kind:<{width}} {span:<{span_width}} {market:<12} {n:>3} {f.counts[study.UP]:>3} "
            f"{f.counts[study.SAME]:>4} {f.counts[study.DOWN]:>4} {f'{f.overlapped}/{f.holes}':>8}  "
            f"{base:<18} {f.answer:<15} {chance:<7} {placebo:<8} {walk}"
        )
    judged = [f for _, span, market, f in cells if (span, market) != marked]
    answered = sum(f.answer != study.TOO_FEW for f in judged)
    walked = sum(f.graded >= study.MIN_PREDICTIONS for f in judged)
    lines.append(
        f"by chance: about {answered * len(study.OUTCOMES) * study.FOLLOW_P_BAR:.1f} answers on "
        f"all history, {walked * study.FOLLOW_P_BAR:.1f} holds walk-forward"
    )
    return [line.rstrip() for line in lines]


# What ``follows`` calls each flow's events in its header.
FOLLOWS_NOUNS = {
    "fomc": "Fed decisions",
    "nfp": "jobs reports",
    "retail": "retail sales releases",
    "cpi": "CPI releases",
    "claims": "jobless claims reports",
    "ecb": "ECB decisions",
    "ceo": "CEO scandals",
    "opec": "OPEC announcements",
    "boe": "BoE decisions",
    "boj": "BoJ decisions",
    "war": "violent acts",
    "crypto": "crypto hacks",
    "weather": "hurricane landfalls",
    "flood": "floods",
    "earnings": "earnings reports",
    "additions": "S&P 500 additions",
    "earnings500": "S&P 500 earnings reports",
    "splits": "stock splits",
}


def _decision_kinds(
    flow: flows.EventFlow, events: list[EventInstance], command: str
) -> dict[int, str] | None:
    """A central bank's decisions' kinds: the Fed's from FRED's target rate, ``None`` without a
    key; the ECB's from the calendar's rates; the BoE's from the Bank's changes."""
    if flow is flows.ECB_FLOW:
        return study.ecb_kinds(events, flows.load_ecb_rates(settings.cache_dir))
    if flow is flows.BOE_FLOW:
        return study.boe_kinds(events, _boe_rates())
    if flow is flows.BOJ_FLOW:
        return study.ecb_kinds(events, _boj_rates())
    api_key = _fred_key(command)
    if not api_key:
        return None
    return study.fed_kinds(events, dict(flows.target_rates(api_key)))


def _boj_rates() -> dict[date, float]:
    rates = flows.load_boj_rates(settings.cache_dir)
    return {at.astimezone(flows.BOJ_FLOW.zone).date(): rate for at, rate in rates.items()}


def _boe_rates() -> dict[date, float]:
    return {day: rate for day, (_, rate) in flows.boe_changes(settings.seed_dir).items()}


class FollowsUnavailable(Exception):
    """Why a flow's ``follows`` cells cannot be computed, worded as ``follows`` prints it."""


class FollowCells(NamedTuple):
    """A flow's ``follows`` cells: its events with a kind, the kinds, their order, a record per kind,
    span and market, and what its events are called."""

    events: list[EventInstance]
    kinds: dict[int, str]
    order: Sequence[str]
    cells: list[tuple[str, str, str, study.Follow]]
    noun: str


def follows_kinds(
    flow: flows.EventFlow, con: duckdb.DuckDBPyConnection
) -> tuple[list[EventInstance], dict[int, str], Sequence[str]]:
    """A flow's stored events, each one's kind by event id, and the kinds' order, as ``follows``
    reads them; raises ``FollowsUnavailable`` with the reason it cannot."""
    events = flows.stored_events(flow, con=con)
    if flow is flows.CEO_FLOW:
        return events, dict.fromkeys((e.event_id for e in events), study.SCANDAL), (study.SCANDAL,)
    if flow in (
        flows.EARNINGS_FLOW,
        flows.EARNINGS_500_FLOW,
        flows.ADDITIONS_FLOW,
        flows.SPLITS_FLOW,
    ):
        order = {
            flows.ADDITIONS_FLOW.cli_name: (study.ADDED,),
            flows.SPLITS_FLOW.cli_name: study.SPLIT_KINDS,
        }.get(flow.cli_name, study.SURPRISE_KINDS)
        return events, study.earnings_kinds(events), order
    if flow is flows.OPEC_FLOW:
        return events, study.detail_kinds(events), study.OPEC_KINDS
    if flow.cli_name in study.ONE_KIND:
        return events, study.one_kind(flow, events), (study.ONE_KIND[flow.cli_name],)
    if flow is flows.BOE_FLOW:
        return events, study.boe_kinds(events, _boe_rates()), study.KINDS
    if flow is flows.BOJ_FLOW:
        try:
            boj_rates = _boj_rates()
        except sources.CalendarError as exc:
            raise FollowsUnavailable(
                f"the BoJ's rates could not be read from TradingView: {exc}"
            ) from None
        return events, study.ecb_kinds(events, boj_rates), study.KINDS
    if flow is flows.ECB_FLOW:
        return (
            events,
            study.ecb_kinds(events, flows.load_ecb_rates(settings.cache_dir)),
            study.KINDS,
        )
    if flow is flows.FED_FLOW:
        api_key = settings.fred_api_key.get_secret_value() if settings.fred_api_key else ""
        if not api_key:
            raise FollowsUnavailable("FT_FRED_API_KEY is not set (see docs/accounts.md)")
        return events, study.fed_kinds(events, dict(flows.target_rates(api_key))), study.KINDS
    kinds = study.release_kinds(flow, con=con)
    if not kinds:
        raise FollowsUnavailable(
            f"no surprises for {flow.cli_name} yet; run `fortuneteller load-surprises` first"
        )
    return events, kinds, study.SURPRISE_KINDS


def follows_of(
    flow: flows.EventFlow,
    events: list[EventInstance],
    kinds: dict[int, str],
    order: Sequence[str],
    con: duckdb.DuckDBPyConnection,
    after: bool = False,
    long: bool = False,
) -> tuple[list[EventInstance], list[tuple[str, str, str, study.Follow]]]:
    """The flow's events with a kind and a record per kind, span and market, on ``kinds``' events."""
    if flow is flows.CEO_FLOW:
        return events, study.follow_ceo(events, con=con, after=after)
    if flow in (
        flows.EARNINGS_FLOW,
        flows.EARNINGS_500_FLOW,
        flows.ADDITIONS_FLOW,
        flows.SPLITS_FLOW,
    ):
        return events, study.follow_companies(events, kinds, order, con=con, after=after)
    return study.follow_decisions(flow, kinds, order, con=con, after=after, long=long)


def follows_cells(
    name: str, con: duckdb.DuckDBPyConnection, after: bool = False, long: bool = False
) -> FollowCells:
    """What ``follows`` prints for the flow ``name``, computed once for the command and the
    scoreboard's *ask* (docs/steps/ask-the-fortune-teller.md); raises ``FollowsUnavailable`` with
    the reason it cannot be."""
    if long and name != "fomc":
        raise FollowsUnavailable(
            "the quarter and the year are measured on the Fed's decisions only"
        )
    flow = flows.flow_named(name)
    noun = FOLLOWS_NOUNS[name]
    if not flows.stored_events(flow, con=con):
        raise FollowsUnavailable(f"no {noun} stored; run `fortuneteller load-releases` first")
    if db.count_rows("daily_bars", con=con) == 0:
        raise FollowsUnavailable("no daily_bars stored; run `fortuneteller load-prices` first")
    try:
        stored, kinds, order = follows_kinds(flow, con)
        events, cells = follows_of(flow, stored, kinds, order, con, after, long)
    except (sources.FredError, sources.CalendarError, ValueError) as exc:
        raise FollowsUnavailable(str(exc)) from exc
    if not events:
        raise FollowsUnavailable(f"no {noun} with a kind yet")
    return FollowCells(events, kinds, order, cells, noun)


def _follows(args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    try:
        f = follows_cells(args.event, con, args.after_the_day, args.long)
    except FollowsUnavailable as exc:
        print(f"follows: {exc}", file=sys.stderr)
        return 1
    marked = (
        (study.KIND_SPAN, study.KIND_MARKET)
        if args.event == flows.OPEC_FLOW.cli_name and not args.after_the_day
        else None
    )
    for line in describe_follows(
        f.events, f.kinds, f.cells, f.order, f.noun, args.after_the_day, args.long, marked
    ):
        print(line)
    return 0


def _trigger_companies(
    triggers: Sequence[study.Trigger],
    events: Sequence[EventInstance],
    con: duckdb.DuckDBPyConnection,
) -> dict[str, list[sources.DailyClosingPrice]]:
    """For `ceo` triggers alone: each named company's closes fetched from Yahoo and stored, and the
    stored scandals' companies' closes, fetched only when none are stored, by ticker; a company
    Yahoo fails on is reported."""
    named = sorted({t.ticker for t in triggers if t.flow == flows.CEO_FLOW.cli_name and t.ticker})
    if not named:
        return {}

    def load() -> dict[str, list[sources.DailyClosingPrice]]:
        companies = {}
        for ticker in {*named, *(e.detail or "" for e in events)}:
            try:
                companies[ticker] = study.stored_closes(ticker, con=con)
            except ValueError:
                continue
        return companies

    unloaded = {e.detail or "" for e in events} - set(load())
    for note in study.load_company_bars(sorted({*named, *unloaded}), con=con)[1]:
        print(f"triggers: {note}")
    return load()


def _triggers(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    try:
        triggers, bad = study.read_triggers(study.guess_files(settings.triggers_dir))
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"triggers: the files cannot be read: {exc}", file=sys.stderr)
        return 1
    for note in bad:
        print(note)
    if not triggers:
        print("triggers: none filed")
        return 0
    names = {t.flow for t in triggers if t.flow in study.TRIGGER_KINDS}
    events: dict[str, list[EventInstance]] = {}
    kinds: dict[str, dict[int, str]] = {}
    try:
        for name in sorted(names):
            flow = flows.flow_named(name)
            events[name] = flows.stored_events(flow, con=con)
            if flow in (flows.FED_FLOW, flows.ECB_FLOW, flows.BOE_FLOW, flows.BOJ_FLOW):
                decided = _decision_kinds(flow, events[name], "triggers")
                if decided is None:
                    return 1
                kinds[name] = decided
            elif flow is flows.CEO_FLOW:
                kinds[name] = {}
            elif flow is flows.OPEC_FLOW:
                kinds[name] = study.detail_kinds(events[name])
            elif name in study.ONE_KIND:
                kinds[name] = study.one_kind(flow, events[name])
            else:
                kinds[name] = study.release_kinds(flow, con=con)
        closes = {m: study.stored_closes(m, con=con) for m in study.MVP_PRICE_SERIES}
        companies = _trigger_companies(triggers, events.get(flows.CEO_FLOW.cli_name, []), con)
        times: dict[str, datetime | None] = {}

        def merged(sha: str) -> datetime | None:
            if sha not in times:
                times[sha] = study.merged_at(settings.triggers_dir, sha)
            return times[sha]

        log = study.read_trigger_log(settings.trigger_log_path)
        rows, lines = study.answer_triggers(triggers, merged, events, kinds, closes, log, companies)
    except (
        sources.FredError,
        sources.CalendarError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"triggers: {exc}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    study.write_trigger_log(settings.trigger_log_path, rows)
    return 0


def _read_article(args: argparse.Namespace) -> int:
    """A pasted text read into a kind (docs/steps/article-to-trigger.md): a trigger row the owner
    could file, with the answers a trigger on its day would get; the second kind, not answered;
    or not a measured kind. It files nothing."""
    try:
        text = Path(args.file).read_text()
    except OSError as exc:
        print(f"read-article: {exc}", file=sys.stderr)
        return 1
    reading = study.read_article(text)
    if reading is None:
        print("not a measured kind")
        return 0
    if reading.kind == study.CONDUCT_NO_DEPARTURE:
        print(
            "a CEO's conduct, no departure: not measured yet"
            + (f" ({reading.ticker})" if reading.ticker else "")
        )
        return 0
    con = db.get_connection()
    db.init_db(con=con)
    closes = {m: study.stored_closes(m, con=con) for m in study.MVP_PRICE_SERIES}
    days = [c.day for c in closes[study.EXCESS_OVER]]
    day = study.article_day(reading, days) or reading.day
    print(f"trigger: ceo,{day or ''},scandal,{reading.ticker}")
    if reading.day is None:
        print("  no date in the text: fill the day")
        return 0
    if reading.at is None:
        print("  time not given: check it")
    if not reading.ticker:
        print("  no ticker in the text: fill it to get the answer")
        return 0
    assert day is not None
    trigger = study.Trigger(
        "article", 1, "", flows.CEO_FLOW.cli_name, day, "scandal", reading.ticker
    )
    events = {trigger.flow: flows.stored_events(flows.CEO_FLOW, con=con)}
    companies = _trigger_companies([trigger], events[trigger.flow], con)
    at = datetime.combine(day, datetime.min.time(), tzinfo=sources.NEW_YORK)
    lines = study.answer_triggers(
        [trigger], lambda _: at, events, {trigger.flow: {}}, closes, [], companies
    )[1]
    head = lines[0].split(": ", 1)
    if ", merged " not in lines[0]:
        print(f"  {head[-1]}")
    for line in lines[1:]:
        print(line)
    return 0


# Step 23 (docs/steps/be-seen.md): the page the weekly post links to, and the code of its Umami
# share link, public by design.
SCOREBOARD_URL = "https://diykorey.github.io/fortuneteller/scoreboard/"
UMAMI_SHARE = "7PW46kYjf9EyzI0H"
DISCLAIMER = "An entertainment tool, not advice."
# The releases the morning job calls, as a post names them.
POST_NAMES = {
    "cpi": "CPI",
    "nfp": "the jobs report",
    "retail": "retail sales",
    "claims": "jobless claims",
    "pce": "core PCE",
    "gdp": "GDP",
    "ism": "the ISM survey",
}


def _post_name(flow: str) -> str:
    return POST_NAMES.get(flow, flows.flow_named(flow).event_type)


def weekly_post_lines(
    rows: Sequence[study.LoggedCall],
    grades: Mapping[int, str],
    start: datetime,
    end: datetime,
    names: Mapping[str, str],
    page: Mapping[str, object] | None = None,
) -> list[str]:
    """The week's post: its releases, each call logged in it and its grade, the record of graded
    calls so far, the page's first answer that holds and its Dow reports ahead (step 44), the link
    and the disclaimer. ``grades`` holds ``_grade``'s word for each row
    with a direction, by its place in ``rows``; a call is a row whose outcome is ``call``."""
    week = [r for r in rows if start <= r.logged_at < end]
    last = (end - timedelta(days=1)).date()
    lines = [f"The fortune teller, {start:%Y-%m-%d} to {last:%Y-%m-%d}", ""]
    releases = sorted({(r.day, _post_name(r.flow)) for r in week})
    if releases:
        lines.append("Releases: " + "; ".join(f"{label} {day}" for day, label in releases) + ".")
    else:
        lines.append("No release this week.")
    calls = [(i, r) for i, r in enumerate(rows) if r.outcome == "call"]
    said = [(i, r) for i, r in calls if start <= r.logged_at < end]
    for i, r in said:
        lines.append(
            f"{_post_name(r.flow)} {r.day}: {names.get(r.instrument, r.instrument)} "
            f"{_direction(r.direction or 0)}, {grades.get(i, 'pending')}."
        )
    if not said:
        lines.append("No call this week.")
    right = sum(grades.get(i) == "right" for i, _ in calls)
    wrong = sum(grades.get(i) == "wrong" for i, _ in calls)
    lines += ["", f"The record so far: {right} right, {wrong} wrong."]
    lines += _post_page_lines(page or {}, end.date())
    lines += [SCOREBOARD_URL, DISCLAIMER]
    return lines


POST_REPORTS = 5


def _post_page_lines(page: Mapping[str, object], since: date) -> list[str]:
    """The page's first answer that holds, and the S&P 500 earnings kinds' lines with the five
    largest companies reporting from ``since``, as the page has them."""
    lines: list[str] = []
    holds = page.get("holds") or []
    assert isinstance(holds, list)
    if holds:
        lines += ["", "An answer that holds: " + str(holds[0]["say"])]
    ahead = page.get("earnings_ahead") or {}
    assert isinstance(ahead, dict)
    reports = [
        {**r, "day": d["day"]}
        for d in ahead.get("days", [])
        if date.fromisoformat(d["day"]) >= since
        for r in d["reports"]
    ]
    if reports:
        largest = sorted(reports, key=lambda r: -r["cap"])[:POST_REPORTS]
        lines += ["", f"S&P 500 companies reporting ({len(reports)}), the largest:"]
        lines += [f"{r['name']} ({r['symbol']}), {r['day']}, {r['time']}." for r in largest]
        lines += ["What followed past S&P 500 reports, on the day against the index:"]
        lines += ahead["lines"]
    return lines


LONG_RUN_MARKETS = ("SPY / ES", "COMP", "GC / XAU", "BRN", "DXY", "UST10Y / ZN", "BTC")
HOME = "US home prices"


def home_prices(fred_key: str) -> list[sources.DailyClosingPrice]:
    """The Case-Shiller national index by month from FRED; none without a key."""
    if not fred_key:
        return []
    payload = sources.fetch_series(fred_key, study.HOME_SERIES)
    return [sources.DailyClosingPrice(d, v) for d, v in sources.parse_series(payload)]


def long_runs(
    con: duckdb.DuckDBPyConnection, home: Sequence[sources.DailyClosingPrice] = ()
) -> list[dict[str, object]]:
    """Step 48's pairs: each market's long run over each span, and home prices' when ``home``
    holds their months."""
    runs: list[tuple[str, str, study.LongRun]] = []
    for market in LONG_RUN_MARKETS:
        try:
            closes = study.stored_closes(market, con)
        except ValueError:
            continue
        runs += [(market, s, study.long_run(closes, n)) for s, n in study.LONG_RUN_SPANS.items()]
    if home:
        runs += [(HOME, s, study.long_run(home, n)) for s, n in study.HOME_SPANS.items()]
    return [
        {
            "market": m,
            "span": s,
            "first": r.first.isoformat(),
            "spans": r.spans,
            "up": r.up,
            "down": r.down,
            "right": r.right,
            "called": r.called,
            "p": r.p,
            "verdict": r.verdict,
            "now": r.now,
            "latest": home[-1].day.isoformat() if m == HOME else None,
        }
        for m, s, r in runs
    ]


def _forecasts(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    rows = long_runs(con, home_prices(_fred_key("forecasts")))
    for r in rows:
        print(
            f"{r['market']:<14} {r['span']:<9} from {r['first']}  spans {r['spans']:>5}"
            f"  up {r['up']:>5}"
            f"  down {r['down']:>5}  right {r['right']:>5} of {r['called']:>5}"
            f"  p {r['p']:.2g}  {r['verdict']:<12} now {r['now']}"
        )
    holding = sum(r["verdict"] == "holds" for r in rows)
    print(f"{len(rows)} pairs, {holding} hold; by chance at p 0.01: {len(rows) * 0.01:.1f}")
    return 0


def _weekly_post(_args: argparse.Namespace) -> int:
    try:
        rows = study.read_calls(settings.calls_path)
    except ValueError as exc:
        print(f"weekly-post: {exc}", file=sys.stderr)
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    scores = {
        flow.cli_name: study.score_calls(flow, rows, con=con)
        for flow in flows.EVENT_FLOWS
        if flow.surprise_rule is not None and any(r.flow == flow.cli_name for r in rows)
    }
    grades = {
        i: _grade(r, scores[r.flow])[0]
        for i, r in enumerate(rows)
        if r.direction is not None and r.flow in scores
    }
    start, end = study.last_full_week(_now())
    page = None
    try:
        page = json.loads((settings.scoreboard_dir / "data.json").read_text())
    except (OSError, ValueError) as exc:
        print(f"weekly-post: the page's data: {exc}", file=sys.stderr)
    for line in weekly_post_lines(rows, grades, start, end, market_names(), page):
        print(line)
    print()

    def ask(a: datetime, b: datetime) -> int:
        return sources.fetch_umami_visitors(UMAMI_SHARE, a, b - timedelta(milliseconds=1))

    try:
        visitors, crosses = study.week_visitors(start, end, ask)
    except sources.UmamiError as exc:
        print(f"weekly-post: {exc}", file=sys.stderr)
        return 1
    print(f"visitors: {visitors}" + (" (the larger of the week's two months)" if crosses else ""))
    return 0


def describe_grades(
    grades: dict[str, study.LinkGrade], expected_sign: dict[str, int], scope: str
) -> list[str]:
    """One walk-forward table: a row per link, its record and its verdict."""
    lines = [
        f"walk-forward ({scope})",
        "instrument   expected  from     predicted  right  hit rate  p       always expected  verdict",
    ]
    for instrument, g in grades.items():
        hit = f"{g.right / g.predictions:.0%}" if g.predictions else "—"
        always = f"{g.always_right / g.predictions:.0%}" if g.predictions else "—"
        p = f"{g.p:.4f}" if g.predictions else "—"
        lines.append(
            f"{instrument:<12} {_direction(expected_sign[instrument]):<9} {g.first or '—':<8} "
            f"{g.predictions:<10} {g.right:<6} {hit:<9} {p:<7} {always:<16} {g.verdict}"
        )
    return [line.rstrip() for line in lines]


def describe_confidence(
    grades: dict[str, study.ConfidenceGrade], scope: str, step: str
) -> list[str]:
    """Rung 3's tables: each link's stated confidence graded, its calibration groups, and its hit
    rate by surprise size."""
    lines = [
        f"confidence ({scope})",
        "instrument   calls  stated  right  Brier   coin p  drift Brier  drift p  in band (allowed)  "
        "verdict",
    ]
    for instrument, g in grades.items():
        if not g.calls:
            lines.append(
                f"{instrument:<12} {0:<6} {'—':<7} {'—':<6} {'—':<7} {'—':<7} "
                f"{'—':<12} {'—':<8} {'—':<18} {g.verdict}"
            )
            continue
        reasons = [", ".join(g.missed)] if g.missed else []
        if g.unproven:
            reasons.append(f"{', '.join(g.unproven)} unproven")
        verdict = f"{g.verdict} ({'; '.join(reasons)})" if reasons else g.verdict
        low, high = g.band_allowed
        band = f"{g.inside}/{g.banded} ({low}–{high})"
        lines.append(
            f"{instrument:<12} {g.calls:<6} {g.stated:<7.0%} {g.right / g.calls:<6.0%} "
            f"{g.brier:<7.4f} {g.coin_p:<7.4f} {g.drift_brier:<12.4f} {g.drift_p:<8.4f} "
            f"{band:<18} {verdict}"
        )
    lines += [
        "",
        f"calibration ({scope})",
        "instrument   group          calls  stated  right  allowed",
    ]
    for instrument, g in grades.items():
        for group in g.groups:
            if group.calls:
                low, high = group.allowed
                mark = "" if group.passes else "  outside"
                if group.calls < study.MIN_GROUP:
                    mark = "  too few to check"
                lines.append(
                    f"{instrument:<12} {group.label:<14} {group.calls:<6} {group.stated:<7.0%} "
                    f"{group.right:<6} {low}–{high}{mark}"
                )
    lines += [
        "",
        f"hit rate by surprise size, calls with a probability ({scope})",
        f"instrument   {'under 2×' + step:<15} 2×{step} and over",
    ]
    for instrument, g in grades.items():
        cells = [f"{right}/{calls}" if calls else "—" for right, calls in g.by_size]
        lines.append(f"{instrument:<12} {cells[0]:<15} {cells[1]}")
    return [line.rstrip() for line in lines]


def _graded_confidence(
    confident: dict[str, list[study.ConfidentCall]], rule: flows.SurpriseRule
) -> list[tuple[str, dict[str, study.ConfidenceGrade]]]:
    """Each link's stated confidence graded on all its calls, then without COVID's months."""
    first, last = (f"{month:%Y-%m}" for month in expectations.COVID_MONTHS)
    return [
        (
            scope,
            {
                instrument: study.grade_confidence(
                    [c for c in calls if not (leave_out and first <= c.call.month <= last)],
                    rule.noticeable,
                )
                for instrument, calls in confident.items()
            },
        )
        for leave_out, scope in ((False, "all"), (True, f"without {first} … {last}"))
    ]


def _predict(args: argparse.Namespace) -> int:
    flow = flows.flow_named(args.event)
    rule = flow.surprise_rule
    if rule is None:
        print(f"predict: {flow.event_type} has no expected value to predict from", file=sys.stderr)
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    baseline = rule.predicted_from
    if (
        not _surprises_stored(flow, rule.combinations[0][0], baseline, con)
        or db.count_rows("observations", con=con) == 0
    ):
        print(
            f"predict: no {baseline} surprises or moves for {args.event} yet; run "
            f"`fortuneteller load-prices` and `fortuneteller {_surprise_command(flow)}` first",
            file=sys.stderr,
        )
        return 1
    if args.actual is not None or args.fetch:
        return _predict_release(flow, rule, args.actual, con)
    confident = study.confident_links(flow, baseline, con=con)
    predictions = {instrument: [c.call for c in calls] for instrument, calls in confident.items()}
    first, last = (f"{month:%Y-%m}" for month in expectations.COVID_MONTHS)
    print(
        f"{rule.combinations[0][0]} against {_source_label(baseline)}: each release predicted "
        "only from the ones before it"
    )
    for leave_out, scope in ((False, "all"), (True, f"without {first} … {last}")):
        grades = {
            instrument: study.grade(
                [p for p in made if not (leave_out and first <= p.month <= last)],
                rule.expected_sign[instrument],
            )
            for instrument, made in predictions.items()
        }
        print()
        for line in describe_grades(grades, dict(rule.expected_sign), scope):
            print(line)
    print()
    print(_hold_rule())
    graded = _graded_confidence(confident, rule)
    for scope, confidence in graded:
        print()
        for line in describe_confidence(confidence, scope, rule.step):
            print(line)
    print()
    print("confidence verdict (honest only if honest with and without COVID)")
    for instrument in confident:
        overall = study.overall_confidence([grades[instrument] for _, grades in graded])
        print(f"{instrument:<12} {overall}")
    print()
    print(
        f"{study.HONEST} = on at least {study.MIN_STATED} calls with a probability (from call "
        f"{study.MIN_CALLS + 1} on):\n"
        f"  each group of at least {study.MIN_GROUP} calls right as often as it states;\n"
        f"  Brier below a coin's and the drift's, each with sign-flip p < {study.BRIER_P_BAR};\n"
        "  the moves inside their band as often as a coin would put them there.\n"
        f"{study.TOO_CLOSE} = Brier below, but p not under {study.BRIER_P_BAR}"
    )
    for line in describe_shared_days(flow, con):
        print(line)
    return 0


def _predict_release(
    flow: flows.EventFlow,
    rule: flows.SurpriseRule,
    typed: float | None,
    con: duckdb.DuckDBPyConnection,
) -> int:
    """The prediction for the next release, from its actual, typed in or else fetched, and the
    calendars."""
    measure = rule.combinations[0][0]
    if measure not in expectations.CONSENSUS_ROWS:
        print(f"predict: {flow.cli_name} has no live path, only the replay", file=sys.stderr)
        return 1
    _nasdaq_name, _check_name, _decimals, gap = expectations.CONSENSUS_ROWS[measure]
    now = _now()
    today = now.astimezone(sources.NEW_YORK).date()
    try:
        upcoming = expectations.next_consensus(measure, today, settings.cache_dir)
    except sources.CalendarError as exc:
        print(f"predict: {exc}", file=sys.stderr)
        return 1
    if upcoming is None:
        print(f"predict: no {measure} release with a consensus from {today} on", file=sys.stderr)
        return 1
    if upcoming.nasdaq is not None and abs(upcoming.nasdaq - upcoming.tradingview) > gap + 1e-9:
        print(
            f"predict: the calendars disagree for {measure} on {upcoming.day}: Nasdaq "
            f"{upcoming.nasdaq:g}, TradingView {upcoming.tradingview:g}; no prediction",
            file=sys.stderr,
        )
        return 1
    released = datetime.combine(upcoming.day, flows.RELEASE_TIME, tzinfo=sources.NEW_YORK)
    live = upcoming.day == today and now >= released
    try:
        logged_before = study.read_calls(settings.calls_path)
    except ValueError as exc:
        print(f"predict: {exc}", file=sys.stderr)
        return 1
    if live and any(c.flow == flow.cli_name and c.day == upcoming.day for c in logged_before):
        print(
            f"predict: {flow.cli_name} on {upcoming.day} is already in {settings.calls_path}; "
            "a release is logged once",
            file=sys.stderr,
        )
        return 1
    try:
        shared = (
            expectations.other_releases(
                [m for m, _ in rule.combinations],
                upcoming.day,
                settings.cache_dir,
                lesser=_lesser_measures(),
            )
            if rule.alone
            else []
        )
    except sources.CalendarError as exc:
        print(f"predict: {exc}", file=sys.stderr)
        return 1
    if typed is not None:
        actual = typed
    else:
        fetched = _fetch_actual(measure, upcoming.day, live, released)
        if fetched is None:
            return 1
        actual = fetched
    if upcoming.nasdaq is None:
        expected, label = upcoming.tradingview, "TradingView's forecast (Nasdaq has none)"
    else:
        expected, label = upcoming.nasdaq, _source_label(expectations.NASDAQ_CONSENSUS)
    surprise = round(actual - expected, 9)
    print(
        f"{measure} on {upcoming.day}: actual {actual:g}, {label} {expected:g}, "
        f"surprise {surprise:+g}"
    )
    if (line := _trigger_line(flow, rule, upcoming, actual)) is not None:
        print(line)
    links = [instrument for instrument, sign in rule.expected_sign.items() if sign]

    def logged(
        instrument: str,
        outcome: str,
        direction: int | None = None,
        probability: float | None = None,
        band: tuple[float, float] | None = None,
    ) -> study.LoggedCall:
        return study.LoggedCall(
            now,
            flow.cli_name,
            upcoming.day,
            actual,
            instrument,
            outcome,
            direction,
            probability,
            band,
        )

    if shared or abs(surprise) < rule.noticeable:
        if shared:
            print(f"no prediction: {upcoming.day} also holds {', '.join(shared)}")
        else:
            print(f"no prediction: the surprise is under {rule.step}")
        outcome = study.SILENT if shared else study.SMALL
        return _log_calls([logged(instrument, outcome) for instrument in links], live, released)
    calls = []
    confident = study.confident_links(
        flow, expectations.NASDAQ_CONSENSUS, con, next_surprise=surprise
    )
    for instrument, made in confident.items():
        if not made or made[-1].call.event_id != study.NEXT_RELEASE:
            print(
                f"{instrument:<12} {'—':<6} silent: the link does not pass on the releases so far"
            )
            calls.append(logged(instrument, study.SILENT))
            continue
        latest = made[-1]
        call = _direction(latest.call.direction)
        if latest.probability is None:
            print(f"{instrument:<12} {call:<6} closes {call} today; too few calls so far")
            calls.append(logged(instrument, study.TOO_FEW_CALLS, direction=latest.call.direction))
            continue
        band = _band(latest.band, study.MVP_PRICE_SERIES[instrument].unit) or "no band"
        right = sum(c.call.right for c in made[:-1])
        print(
            f"{instrument:<12} {call:<6} closes {call} today: right on {right} of {len(made) - 1} "
            f"calls before, {band}"
        )
        calls.append(
            logged(
                instrument,
                study.CALLED,
                direction=latest.call.direction,
                probability=latest.probability,
                band=latest.band,
            )
        )
    print(
        "record = the link's calls so far, walk-forward; band = where half its moves land; "
        f"both graded by `fortuneteller predict --event {flow.cli_name}`"
    )
    return _log_calls(calls, live, released)


def _lesser_measures() -> list[str]:
    """The measures of the lesser flows, whose releases share nobody's day."""
    return [
        measure
        for flow in flows.EVENT_FLOWS
        if flow.lesser and flow.surprise_rule is not None
        for measure, _baseline in flow.surprise_rule.combinations
    ]


def _live(_args: argparse.Namespace) -> int:
    """Each flow released today, fetched and logged as by ``predict --fetch``: 0 on a day without
    a release, 1 if any release today, or the check for one, fails (the release-day job's spec)."""
    now = _now().astimezone(sources.NEW_YORK)
    if now.time() < flows.RELEASE_TIME:
        print(f"live: before {flows.RELEASE_TIME:%H:%M} New York; the timer runs it then")
        return 0
    today = now.date()
    try:
        logged = {c.flow for c in study.read_calls(settings.calls_path) if c.day == today}
    except ValueError as exc:
        print(f"live: {exc}", file=sys.stderr)
        return 1
    released, failed = [], False
    for flow in flows.EVENT_FLOWS:
        if not flows.called_live(flow) or flow.surprise_rule is None:
            continue
        measure = flow.surprise_rule.combinations[0][0]
        try:
            upcoming = expectations.next_consensus(measure, today, settings.cache_dir)
        except sources.CalendarError as exc:
            print(f"live: {flow.cli_name}: {exc}", file=sys.stderr)
            failed = True
            continue
        if upcoming is None or upcoming.day != today:
            continue
        released.append(flow.cli_name)
        if flow.cli_name in logged:
            print(f"live: {flow.cli_name} is already in {settings.calls_path}")
            continue
        print(f"live: {flow.cli_name} is released today")
        args = argparse.Namespace(event=flow.cli_name, actual=None, fetch=True)
        failed = _predict(args) != 0 or failed
    if not released and not failed:
        print(f"live: no release today ({today})")
    try:
        for line in _previews(now):
            print(line)
    except (sources.CalendarError, OSError, ValueError, KeyError) as exc:
        print(f"live: the statements' preview: {exc!r}", file=sys.stderr)
        failed = True
    rows = [c for c in study.read_calls(settings.calls_path) if c.day == today]
    if rows:
        spoke = sum(c.outcome != study.SILENT for c in rows)
        print(
            f"live: {len(rows)} row{'s' if len(rows) != 1 else ''} logged today, "
            f"{f'{spoke} not silent' if spoke else 'all silent'}"
        )
    return 1 if failed else 0


def _previews(now: datetime) -> list[str]:
    """A line for each statement still ahead today, with the markets that moved on its flow's lone
    days, read from the scoreboard's data; the record only, never a direction (scheduled
    statements, step 3)."""
    statements = [
        (flow, given)
        for flow in flows.EVENT_FLOWS
        if isinstance(flow, flows.StatementFlow)
        and (given := flow.ahead(settings.cache_dir, now)) is not None
    ]
    if not statements:
        return []
    data = json.loads((settings.scoreboard_dir / "data.json").read_text())
    measured = {event["name"]: event["raw_move"] for event in data["events"]}
    lines = []
    for flow, (at, title) in statements:
        cells = measured[flow.cli_name]
        days = max(cell["days"] for cell in cells.values())
        movers = [
            f"{market} {cell['ratio']:.2f}"
            for market, cell in cells.items()
            if cell["verdict"] == study.MOVES
        ]
        record = (
            f"moved more than on ordinary days: {', '.join(movers)}"
            if movers
            else "no market moved more than on ordinary days"
        )
        lines.append(
            f"preview: {title} at {at.astimezone(sources.NEW_YORK):%H:%M} New York; "
            f"on the {flow.office}'s {days} days alone before, {record}"
        )
    return lines


def _now() -> datetime:
    return datetime.now(UTC)


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


# How often, and for how long from the release time, --fetch reads the calendar (rung 5's spec).
FETCH_EVERY_S = 15
FETCH_FOR = timedelta(minutes=30)


def _trigger_line(
    flow: flows.EventFlow,
    rule: flows.SurpriseRule,
    upcoming: expectations.NextConsensus,
    actual: float,
) -> str | None:
    """The row a trigger for this release is filed with, its kind read as ``release_kinds`` will
    read it from the store, or why it has none; nothing for a flow no trigger may name."""
    if study.TRIGGER_KINDS.get(flow.cli_name) != study.SURPRISE_KINDS:
        return None
    nasdaq = rule.predicted_from == expectations.NASDAQ_CONSENSUS
    expected = upcoming.nasdaq if nasdaq else upcoming.tradingview
    if expected is None:
        label = _source_label(rule.predicted_from)
        return f"trigger: none, {label} has none to read the kind against"
    kind = study.surprise_kind(rule, actual, expected)
    return f"trigger: {flow.cli_name},{upcoming.day},{kind}"


def _fetch_actual(measure: str, day: date, live: bool, released: datetime) -> float | None:
    """The release's actual from TradingView's calendar, read until it appears or ``FETCH_FOR``
    after the release time has passed; ``None``, with the reason printed, if it does not."""
    if not live:
        print(
            f"predict: --fetch reads {measure} on {day} from its release at "
            f"{released:%H:%M} New York that day",
            file=sys.stderr,
        )
        return None
    until = released + FETCH_FOR
    while True:
        try:
            actual = expectations.published_actual(measure, day, settings.cache_dir)
        except sources.CalendarError as exc:
            print(f"predict: {exc}; reading again", file=sys.stderr)
            actual = None
        now = _now().astimezone(sources.NEW_YORK)
        if actual is not None:
            print(f"actual {actual:g} from TradingView at {now:%H:%M:%S} New York")
            return actual
        if now >= until:
            print(
                f"predict: TradingView shows no actual for {measure} on {day} by "
                f"{until:%H:%M} New York; type it with --actual",
                file=sys.stderr,
            )
            return None
        _sleep(FETCH_EVERY_S)


def _log_calls(calls: Sequence[study.LoggedCall], live: bool, released: datetime) -> int:
    """Logs the calls only on the release's day, from its release time: any other run is a what-if
    and must not take the release's one entry in the log."""
    if not live:
        print(f"not logged: a release is logged on its day from {released:%H:%M} New York")
        return 0
    study.append_calls(settings.calls_path, calls)
    print(f"logged {len(calls)} rows to {settings.calls_path}")
    return 0


def _score(_args: argparse.Namespace) -> int:
    try:
        rows = study.read_calls(settings.calls_path)
    except ValueError as exc:
        print(f"score: {exc}", file=sys.stderr)
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    print(
        f"{len(rows)} rows in {settings.calls_path}, each call graded on its market's close that "
        "day beside the replay of every stored release"
    )
    baseline = expectations.NASDAQ_CONSENSUS
    for flow in flows.EVENT_FLOWS:
        rule = flow.surprise_rule
        if rule is None or not any(r.flow == flow.cli_name for r in rows):
            continue
        live = study.score_calls(flow, rows, con=con)
        replay = study.confident_links(flow, baseline, con=con)
        signs = dict(rule.expected_sign)
        print()
        print(f"{flow.cli_name}: {rule.combinations[0][0]} against {_source_label(baseline)}")
        for scope, linked in (("live", live.calls), ("replay", replay)):
            print()
            grades = {
                instrument: study.grade([c.call for c in calls], signs[instrument])
                for instrument, calls in linked.items()
            }
            for line in describe_grades(grades, signs, scope):
                print(line)
        print()
        confidence = {
            instrument: study.grade_confidence(calls, rule.noticeable)
            for instrument, calls in live.calls.items()
        }
        for line in describe_confidence(confidence, "live", rule.step):
            print(line)
        for label, notes in (
            ("void", live.void),
            ("pending", live.pending),
            ("waiting", live.waiting),
        ):
            if notes:
                print()
                print(f"{label}: {len(notes)}")
                for note in notes:
                    print(f"  {note}")
    try:
        graded, bad = _read_guesses(con)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"score: the guesses cannot be read: {exc}", file=sys.stderr)
        return 1
    for line in describe_guesses(graded, bad, rows, con):
        print(line)
    missed = study.missed_releases(rows, con=con)
    print()
    later = [
        f"{flow.cli_name} since {rule.logged_since}"
        for flow in flows.EVENT_FLOWS
        if (rule := flow.surprise_rule) is not None and rule.logged_since != flows.LOG_SINCE
    ]
    print(
        f"missed: {len(missed)} releases since {flows.LOG_SINCE} with no rows"
        + (f" ({', '.join(later)})" if later else "")
    )
    for note in missed:
        print(f"  {note}")
    return 0


def _band(band: tuple[float, float] | None, unit: str) -> str | None:
    if band is None:
        return None
    low, high = (_move_size(edge, unit, signed=True) for edge in band)
    return f"{low} to {high}"


def _record(replay: Sequence[study.ConfidentCall], before: date) -> dict[str, int]:
    """A link's record as counts on the replay's calls before ``before``: what the popup said."""
    earlier = [c for c in replay if flows.event_date(c.call.event_id) < before]
    return {"right": sum(c.call.right for c in earlier), "calls": len(earlier)}


def _read_guesses(
    con: duckdb.DuckDBPyConnection,
) -> tuple[list[study.GradedGuess], list[str]]:
    """Every guess file on ``main``'s history, graded or voided, and a note for each bad file; a
    failure of git or GitHub raises, so an outage cannot void every guess."""
    guesses, bad = study.read_guesses(study.guess_files(settings.guesses_dir))
    graded = study.score_guesses(
        guesses, lambda sha: study.merged_at(settings.guesses_dir, sha), con=con
    )
    return graded, bad


def guess_rows(
    graded: Sequence[study.GradedGuess],
    rows: Sequence[study.LoggedCall],
    con: duckdb.DuckDBPyConnection,
) -> list[dict[str, str | None]]:
    """Each guess with its state and the machine's row beside it: right or wrong, void or waiting
    as ``score`` grades the row, "no call" for a row without a direction, "not logged" for none."""
    lives: dict[str, study.LiveScore] = {}
    out: list[dict[str, str | None]] = []
    for g in graded:
        guess = g.guess
        row = next(
            (
                r
                for r in rows
                if (r.flow, r.day, r.instrument) == (guess.flow, guess.day, guess.instrument)
            ),
            None,
        )
        if row is None:
            machine = "not logged"
        elif row.direction is None:
            machine = "no call"
        else:
            if row.flow not in lives:
                lives[row.flow] = study.score_calls(flows.flow_named(row.flow), rows, con=con)
            grade = _grade(row, lives[row.flow])[0]
            machine = study.WAITING if grade == "pending" else grade
        out.append(
            {
                "day": guess.day.isoformat(),
                "who": guess.who,
                "event": guess.flow,
                "market": guess.instrument,
                "direction": "up" if guess.direction > 0 else "down",
                "state": g.state,
                "reason": g.reason,
                "machine": machine,
            }
        )
    return out


def handle_counts(graded: Sequence[study.GradedGuess]) -> list[dict[str, object]]:
    """Each handle's record as counts: right out of graded, never a share."""
    counts = []
    for who in sorted({g.guess.who for g in graded}):
        mine = [g for g in graded if g.guess.who == who and g.state in (study.RIGHT, study.WRONG)]
        right = sum(g.state == study.RIGHT for g in mine)
        counts.append({"who": who, "right": right, "graded": len(mine)})
    return counts


def describe_guesses(
    graded: Sequence[study.GradedGuess],
    bad: Sequence[str],
    rows: Sequence[study.LoggedCall],
    con: duckdb.DuckDBPyConnection,
) -> list[str]:
    """``score``'s guesses block: each guess and the machine's row beside it, then each handle's
    count; nothing when there are no guesses. No line starts with ``pending:``, which the evening
    job waits on."""
    if not graded and not bad:
        return []
    lines = ["", f"guesses: {len(graded) + len(bad)}"]
    for g in guess_rows(graded, rows, con):
        state = g["state"] if g["reason"] is None else f"{g['state']}, {g['reason']}"
        lines.append(
            f"  {g['day']} {g['who']} {g['event']} {g['market']} {g['direction']}: {state}; "
            f"machine: {g['machine']}"
        )
    lines += [f"  {note}" for note in bad]
    lines += [f"  {h['who']}: {h['right']} of {h['graded']} right" for h in handle_counts(graded)]
    return lines


def _grade(row: study.LoggedCall, live: study.LiveScore) -> tuple[str, str | None]:
    """A logged row with a direction: right or wrong on its close, else void or pending with
    ``score``'s note on it."""
    for c in live.calls.get(row.instrument, []):
        if flows.event_date(c.call.event_id) == row.day:
            return ("right" if c.call.right else "wrong"), None
    where = f"{row.flow} {row.day}"
    for grade, notes in (
        ("void", live.void),
        ("pending", live.pending),
        ("pending", live.waiting),
    ):
        prefixes = (f"{where}:", f"{where} {row.instrument}:")
        note = next((n for n in notes if n.startswith(prefixes)), None)
        if note is not None:
            return grade, note
    return "pending", None


def scoreboard_data(
    rows: Sequence[study.LoggedCall],
    con: duckdb.DuckDBPyConnection,
    today: date,
    graded: Sequence[study.GradedGuess] = (),
    bad: Sequence[str] = (),
    ahead: list[dict[str, object]] | None = None,
    watch: list[dict[str, object]] | None = None,
    earnings_days: Callable[[date], list[dict[str, str]]] | None = None,
) -> dict[str, object]:
    """The page's numbers: what ``raw-move``, ``surprise`` and ``predict`` print for every flow
    with releases stored, the calls and the guesses as ``score`` grades them, and the chance count
    by each grid."""
    events: list[dict[str, object]] = []
    replays: dict[str, dict[str, list[study.ConfidentCall]]] = {}
    cells = {"raw_move": 0, "surprise": 0, "walk_forward": 0}
    for flow in flows.EVENT_FLOWS:
        stored = flows.stored_events(flow, con=con)
        if not stored:
            continue
        raw = study.measure_raw_moves(flow, con=con)
        cells["raw_move"] += sum(r.overall.verdict != study.TOO_FEW for r in raw.values())
        entry: dict[str, object] = {
            "name": flow.cli_name,
            "label": flow.label,
            "event_type": flow.event_type,
            "country": flow.country,
            "releases": len(stored),
            "first": flows.release_date(stored[0]).isoformat(),
            "last": flows.release_date(stored[-1]).isoformat(),
            "raw_move": {
                instrument: (
                    {"days": r.overall.event_days, "verdict": r.overall.verdict}
                    if r.overall.verdict == study.TOO_FEW
                    else {
                        "days": r.overall.event_days,
                        "median_event": _move_size(r.overall.median_event, r.unit),
                        "median_other": _move_size(r.overall.median_other, r.unit),
                        "ratio": round(r.overall.ratio, 2),
                        "p": round(r.overall.p, 4),
                        "verdict": r.overall.verdict,
                    }
                )
                for instrument, r in raw.items()
            },
            "surprise": None,
            "walk_forward": None,
        }
        rule = flow.surprise_rule
        if rule is not None:
            measure, baseline = rule.combinations[0]
            if _surprises_stored(flow, measure, baseline, con):
                tracking = study.track_surprises(flow, con=con)[(measure, baseline)]
                cells["surprise"] += len(tracking)
                entry["surprise"] = {
                    "measure": measure,
                    "against": _source_label(baseline),
                    "left_out": len(study.shared_days(flow, con=con)) if rule.alone else 0,
                    "links": {
                        instrument: {
                            "expected": _direction(rule.expected_sign[instrument]),
                            "n": t.n,
                            "rank_corr": round(t.rank_corr, 2),
                            "p": round(t.p, 4),
                            "hit_rate": None if t.hit_rate is None else round(t.hit_rate, 2),
                            "hit_n": t.hit_n,
                            "verdict": t.verdict,
                        }
                        for instrument, t in tracking.items()
                    },
                }
            if _surprises_stored(flow, measure, rule.predicted_from, con):
                replay = study.confident_links(flow, rule.predicted_from, con=con)
                replays[flow.cli_name] = replay
                cells["walk_forward"] += len(replay)
                grades = {
                    instrument: study.grade([c.call for c in calls], rule.expected_sign[instrument])
                    for instrument, calls in replay.items()
                }
                entry["walk_forward"] = {
                    "measure": measure,
                    "against": _source_label(rule.predicted_from),
                    "links": {
                        instrument: {
                            "expected": _direction(rule.expected_sign[instrument]),
                            "first": g.first,
                            "predictions": g.predictions,
                            "right": g.right,
                            "p": round(g.p, 4),
                            "always_right": g.always_right,
                            "verdict": g.verdict,
                        }
                        for instrument, g in grades.items()
                    },
                }
        events.append(entry)
    scores = {
        flow.cli_name: study.score_calls(flow, rows, con=con)
        for flow in flows.EVENT_FLOWS
        if flow.surprise_rule is not None and any(r.flow == flow.cli_name for r in rows)
    }
    calls: list[dict[str, object]] = []
    for r in rows:
        flow = flows.flow_named(r.flow)
        call: dict[str, object] = {
            "day": r.day.isoformat(),
            "event": flow.cli_name,
            "label": flow.label,
            "actual": r.actual,
            "market": r.instrument,
            "outcome": r.outcome,
            "direction": None if r.direction is None else _direction(r.direction),
            "record": None,
            "band": _band(r.band, study.MVP_PRICE_SERIES[r.instrument].unit),
            "grade": None,
            "note": None,
        }
        if r.direction is not None:
            call["record"] = _record(replays.get(r.flow, {}).get(r.instrument, []), r.day)
            call["grade"], call["note"] = _grade(r, scores[r.flow])
        calls.append(call)
    missed = [note.split() for note in study.missed_releases(rows, con=con)]
    (last_close,) = con.execute("SELECT max(day) FROM daily_bars").fetchone() or (None,)
    bars = {
        "raw_move": study.MOVE_P_BAR,
        "surprise": study.TRACK_P_BAR,
        "walk_forward": study.TRACK_P_BAR,
    }
    asked = ask_data(con)
    earnings: dict[str, object] | None = None
    if earnings_days is not None:
        try:
            earnings = earnings_ahead(today, asked["ask"], earnings_days)
        except sources.CalendarError as exc:
            print(f"scoreboard: the earnings calendar: {exc}", file=sys.stderr)
    return {
        "written": today.isoformat(),
        "data_until": None if last_close is None else last_close.isoformat(),
        "markets": list(study.MVP_PRICE_SERIES),
        "rules": {
            "raw_move": _move_rule(),
            "surprise": _track_rule(),
            "walk_forward": _hold_rule(),
        },
        "chance": {
            grid: {"cells": n, "p": bars[grid], "by_chance": round(n * bars[grid], 2)}
            for grid, n in cells.items()
        },
        "events": events,
        "calls": calls,
        "missed": [{"event": name, "day": day} for name, day in missed],
        "guesses": guess_rows(graded, rows, con),
        "bad_guesses": list(bad),
        "handles": handle_counts(graded),
        "ahead": ahead,
        "watch": watch,
        "market_names": market_names(),
        **asked,
        "holds": answers_that_hold(asked["ask"]),
        "earnings_ahead": earnings,
    }


# Step 22, ask the fortune teller (docs/steps/ask-the-fortune-teller.md): each kind of event, in
# the words the page gives it.
ASK_DECISIONS = {
    "fomc": {
        study.CUT: "a Fed rate cut",
        study.HOLD: "the Fed holding its rate",
        study.HIKE: "a Fed rate hike",
    },
    "ecb": {
        study.CUT: "an ECB rate cut",
        study.HOLD: "the ECB holding its rate",
        study.HIKE: "an ECB rate hike",
    },
    "ceo": {study.SCANDAL: "a CEO's conduct in question"},
    "opec": {
        study.OIL_UP: "an OPEC+ decision that sent oil up",
        study.OIL_DOWN: "an OPEC+ decision that sent oil down",
    },
    "boe": {
        study.CUT: "a Bank of England rate cut",
        study.HOLD: "the Bank of England holding its rate",
        study.HIKE: "a Bank of England rate hike",
    },
    "boj": {
        study.CUT: "a Bank of Japan rate cut",
        study.HOLD: "the Bank of Japan holding its rate",
        study.HIKE: "a Bank of Japan rate hike",
    },
    "war": {study.VIOLENT_ACT: "a violent act setting off an international crisis"},
    "crypto": {study.HACK: "a crypto hack of $100 million or more"},
    "weather": {study.LANDFALL: "a US hurricane landfall"},
    "flood": {study.FLOOD: "a billion-dollar US flood"},
    "earnings500": {
        study.ABOVE: "an S&P 500 company's earnings above the consensus",
        study.AS_EXPECTED: "an S&P 500 company's earnings in line with the consensus",
        study.BELOW: "an S&P 500 company's earnings below the consensus",
    },
    "additions": {study.ADDED: "a company announced as joining the S&P 500"},
    "splits": {
        "alone": "a stock split announced alone",
        "with a report": "a stock split announced with an earnings report",
    },
    "earnings": {
        study.ABOVE: "a Dow company's earnings above the consensus",
        study.AS_EXPECTED: "a Dow company's earnings in line with the consensus",
        study.BELOW: "a Dow company's earnings below the consensus",
    },
}
# Brent's day after an OPEC+ decision is how its kind is read (docs/steps/ask-phase-5.md).
KIND_CELL_WORDS = "This is how the kind is read, not an answer."
# A cell the placebo marks (docs/steps/ask-earnings.md).
PERIOD_WORDS = (
    "With each event moved ten closes or a span away, the same answer comes: it reads as the "
    "period, not the event."
)
# A release on a fixed weekday lands on that weekday again when moved (what-follows-jobs.md).
WEEKDAY_PERIOD_WORDS = (
    "With each event moved ten closes or a span away, the same answer comes: it reads as the "
    "period or the weekday, not the event."
)
WEEKDAY_FLOWS = ("nfp", "claims")


def is_kind_cell(name: str, span: str, market: str) -> bool:
    return (name, span, market) == ("opec", study.KIND_SPAN, study.KIND_MARKET)


ASK_RELEASES = {
    "nfp": "a jobs report",
    "retail": "a retail sales release",
    "cpi": "a CPI release",
    "claims": "a jobless claims report",
}
ASK_SURPRISE = {
    study.ABOVE: "above the consensus",
    study.AS_EXPECTED: "as expected",
    study.BELOW: "below the consensus",
}
ASK_SPANS = {
    "day": "on the day",
    "week": "over the next week",
    "month": "over the next month",
    "quarter": "over the next quarter",
    "year": "over the next year",
}


def market_names() -> dict[str, str]:
    """Each market's name from data/seed/instruments.csv, the CEO kind's in words; a market not
    there keeps its symbol."""
    with (settings.seed_dir / "instruments.csv").open(newline="") as f:
        names = {row["symbol"]: row["name"] for row in csv.DictReader(f)}
    names[study.EXCESS_MARKET] = "the company against the S&P 500"
    return names


def ask_kind(name: str, kind: str) -> str:
    """A kind of event as the page names it: "a jobs report above the consensus"."""
    if name in ASK_DECISIONS:
        return ASK_DECISIONS[name][kind]
    return f"{ASK_RELEASES[name]} {ASK_SURPRISE[kind]}"


def _counts(up: int, same: int, down: int) -> str:
    return f"up {up}, about the same {same}, down {down}, of {up + same + down}"


def ask_say(
    name: str, kind: str, span: str, market: str, f: study.Follow, market_name: str | None = None
) -> str:
    """One cell in plain words: the events' counts, the base's counts, the answer and its replay;
    counts only, never a percentage."""
    counts = [f.counts[o] for o in study.OUTCOMES]
    shown = market if market_name is None else market_name
    words = [f"After {ask_kind(name, kind)}, {shown} {ASK_SPANS[span]}: {_counts(*counts)}."]
    if f.base is not None and f.base.n:
        base = [round(f.base.rates[o] * f.base.n) for o in study.OUTCOMES]
        every = "On every day" if span == "day" else f"Over every {span}"
        words.append(f"{every} of its history: {_counts(*base)}.")
    elif f.base is not None:
        words.append(
            "Its base is each company's own past two years, averaged, so it has no single count."
        )
    n = sum(counts)
    if f.answer == study.TOO_FEW:
        words.append(f"Too few events to answer: {n}, against the {study.MIN_EVENT_DAYS} it needs.")
    else:
        words.append(f"Answer: {f.answer}.")
    if f.graded == 0:
        words.append("Not replayed.")
    elif f.verdict == study.HOLDS:
        words.append(f"Replayed, it held: right {f.right} of {f.graded}.")
    elif f.verdict == study.DOESNT_HOLD:
        words.append(f"Replayed, it did not hold: right {f.right} of {f.graded}.")
    else:
        words.append(f"Too few replayed to judge: right {f.right} of {f.graded}.")
    if f.by_cycle is not None:
        words.append(
            f"Counting each rate cycle once: {f.by_cycle[1]}, from {f.by_cycle[0]} cycles."
        )
    if is_kind_cell(name, span, market):
        words.append(KIND_CELL_WORDS)
    if f.period:
        words.append(WEEKDAY_PERIOD_WORDS if name in WEEKDAY_FLOWS else PERIOD_WORDS)
    return " ".join(words)


def ask_cell(
    name: str, kind: str, span: str, market: str, f: study.Follow, names: Mapping[str, str]
) -> dict[str, object]:
    """One cell's numbers, as ``follows`` prints them, and its sentence."""
    base = f.base
    return {
        "kind": kind,
        "span": span,
        "market": market,
        "market_name": names.get(market, market),
        "up": f.counts[study.UP],
        "same": f.counts[study.SAME],
        "down": f.counts[study.DOWN],
        "base_up": None if base is None else round(base.rates[study.UP], 4),
        "base_same": None if base is None else round(base.rates[study.SAME], 4),
        "base_down": None if base is None else round(base.rates[study.DOWN], 4),
        "base_n": None if base is None else base.n,
        "answer": f.answer,
        "graded": f.graded,
        "right": f.right,
        "verdict": f.verdict,
        "cycles": None if f.by_cycle is None else list(f.by_cycle),
        "kind_cell": is_kind_cell(name, span, market),
        "period": f.period,
        "say": ask_say(name, kind, span, market, f, names.get(market, market)),
    }


# Step 45 (docs/steps/sp500-on-the-page.md): the S&P 500's kinds need its members' closes, which
# only a copy of the store holds, and `follows` on them takes most of an hour; their *ask* is
# measured once there and frozen here, shown with the day it was measured.
SP500_FLOWS = ("earnings500", "additions", "splits")
SP500_ASK = settings.seed_dir / "ask_sp500.json"


def ask_data(con: duckdb.DuckDBPyConnection) -> dict[str, list[dict[str, object]]]:
    """The page's *ask*: for each flow ``follows`` measures, its kinds and every cell, the Fed's
    with the quarter and the year; and each flow that cannot be computed, with the reason."""
    ask: list[dict[str, object]] = []
    left_out: list[dict[str, object]] = []
    names = market_names()
    for name, noun in FOLLOWS_NOUNS.items():
        if name in SP500_FLOWS:
            continue  # measured on a copy of the store, frozen in SP500_ASK (step 45)
        try:
            ask.append(ask_entry(name, noun, con, names))
        except FollowsUnavailable as exc:
            left_out.append({"name": name, "noun": noun, "reason": str(exc)})
    if SP500_ASK.exists():
        frozen = json.loads(SP500_ASK.read_text())
        ask += [{**entry, "measured": frozen["measured"]} for entry in frozen["ask"]]
    return {"ask": ask, "ask_left_out": left_out}


def ask_entry(
    name: str, noun: str, con: duckdb.DuckDBPyConnection, names: Mapping[str, str]
) -> dict[str, object]:
    """One flow's *ask*: its kinds with their counts, its first and last day, and every cell."""
    f = follows_cells(name, con)
    cells = list(f.cells)
    if name == "fomc":
        cells += follows_cells(name, con, long=True).cells
    counted = [f.kinds[e.event_id] for e in f.events if e.event_id in f.kinds]
    latest = f.events[-1]
    asked = [ask_cell(name, *cell, names) for cell in cells]
    for c in asked:
        series = study.MVP_PRICE_SERIES.get(str(c["market"]))
        if c["kind"] == f.kinds.get(latest.event_id) and series and c["span"] in study.SPANS:
            first = study.first_reaction_day(latest, series)
            c["open_until"] = _weekdays_after(first, study.SPANS[str(c["span"])] - 1).isoformat()
    return {
        "name": name,
        "noun": noun,
        "kinds": [
            {"kind": k, "label": ask_kind(name, k), "events": counted.count(k)} for k in f.order
        ],
        "first": flows.release_date(f.events[0]).isoformat(),
        "last": flows.release_date(f.events[-1]).isoformat(),
        "latest": {
            "day": flows.release_date(latest).isoformat(),
            "kind": f.kinds.get(latest.event_id),
        },
        "cells": asked,
    }


def _weekdays_after(day: date, count: int) -> date:
    """The weekday ``count`` weekdays after ``day``; holidays are not known here."""
    while count:
        day += timedelta(days=1)
        count -= day.weekday() < 5
    return day


# The week ahead (docs/steps/week-ahead.md): the releases `live` calls in the next seven days.
AHEAD_DAYS = 7


def week_ahead(
    con: duckdb.DuckDBPyConnection, today: date, cache_dir: Path
) -> list[dict[str, object]]:
    """Each release `live` calls from the day after ``today`` to ``AHEAD_DAYS`` after it, oldest
    first: its consensus, the thresholds either side, and what each signed link would call for a
    noticeable surprise, with its replay record; every link silent on a shared day."""
    ahead = []
    for flow in flows.EVENT_FLOWS:
        rule = flow.surprise_rule
        if rule is None or not flows.called_live(flow):
            continue
        measure = rule.combinations[0][0]
        upcoming = expectations.next_consensus(measure, today + timedelta(days=1), cache_dir)
        if upcoming is None or upcoming.day > today + timedelta(days=AHEAD_DAYS):
            continue
        consensus = upcoming.tradingview if upcoming.nasdaq is None else upcoming.nasdaq
        shared = (
            expectations.other_releases(
                [m for m, _ in rule.combinations],
                upcoming.day,
                cache_dir,
                lesser=_lesser_measures(),
            )
            if rule.alone
            else []
        )
        replay = study.confident_links(
            flow, rule.predicted_from, con, next_surprise=rule.noticeable
        )
        links: dict[str, dict[str, object]] = {}
        for instrument, made in replay.items():
            sign = rule.expected_sign[instrument]
            calls = made[:-1] if made and made[-1].call.event_id == study.NEXT_RELEASE else made
            g = study.grade([c.call for c in calls], sign)
            calling = not shared and len(calls) < len(made)
            links[instrument] = {
                "above": _direction(made[-1].call.direction) if calling else None,
                "below": _direction(-made[-1].call.direction) if calling else None,
                "right": g.right,
                "predictions": g.predictions,
                "always_right": g.always_right,
                "verdict": g.verdict,
            }
        ahead.append(
            {
                "day": upcoming.day.isoformat(),
                "time": f"{flows.RELEASE_TIME:%H:%M}",
                "event": flow.cli_name,
                "label": flow.label,
                "measure": measure,
                "consensus": consensus,
                "consensus_from": "TradingView" if upcoming.nasdaq is None else "Nasdaq",
                "below": round(consensus - rule.noticeable, 9),
                "above": round(consensus + rule.noticeable, 9),
                "step": rule.step,
                "shared": shared,
                "links": links,
            }
        )
    return sorted(ahead, key=lambda release: str(release["day"]))


# Step 44, a page a stranger reads (docs/steps/readers.md): the answers that hold first, and the
# Dow's reports of the next seven weekdays with what followed each kind.
EARNINGS_WORDS = {
    "above": "If it beats",
    "as expected": "If it is in line",
    "below": "If it misses",
}
EARNINGS_TIMES = {"time-pre-market": "before the open", "time-after-hours": "after the close"}


def _answered(cell: Mapping[str, object]) -> bool:
    return cell["verdict"] == "holds" and not cell["kind_cell"] and not cell["period"]


def answers_that_hold(ask: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    """Every cell that holds, less the kind cells and those read as the period, in *Ask*'s order
    of flows, kinds and cells; each its sentence and the kind it opens."""
    held = []
    for flow in ask:
        kinds = flow["kinds"]
        cells = flow["cells"]
        assert isinstance(kinds, list) and isinstance(cells, list)
        order = [k["kind"] for k in kinds]
        for c in sorted(filter(_answered, cells), key=lambda c: order.index(c["kind"])):
            held.append({"flow": str(flow["name"]), "kind": c["kind"], "say": c["say"]})
    return held


def earnings_line(kind: str, cell: Mapping[str, object] | None) -> str:
    """One kind's line for a report ahead: a direction only from a cell that holds."""
    word = EARNINGS_WORDS[kind]
    if cell is None:
        return f"{word}: not measured."
    if _answered(cell):
        return f"{word}: {cell['answer']}, right {cell['right']} of {cell['graded']} replayed."
    if cell["verdict"] == "holds" and cell["period"]:
        return f"{word}: it reads as the period, not the report."
    if cell["verdict"] == "too few":
        return f"{word}: too few to say."
    return f"{word}: did not hold."


def sp500_members(day: date) -> set[str]:
    """The S&P 500's members on ``day`` by data/seed/sp500.csv's dated changes."""
    members: set[str] = set()
    with (settings.seed_dir / "sp500.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            if date.fromisoformat(row["day"]) <= day:
                (members.add if row["change"] == "in" else members.discard)(row["ticker"])
    return members


def _dollars(text: str) -> float:
    try:
        return float(text.replace("$", "").replace(",", ""))
    except ValueError:
        return 0.0


def earnings_ahead(
    today: date,
    ask: Sequence[Mapping[str, object]],
    fetch: Callable[[date], list[dict[str, str]]],
) -> dict[str, object]:
    """The S&P 500 earnings kinds' lines, from *Ask*'s day cells against the index, and each
    member's report Nasdaq lists in the ``AHEAD_DAYS`` weekdays after ``today``, by day."""
    group = next((f for f in ask if f["name"] == "earnings500"), None)
    cells: dict[object, Mapping[str, object]] = {}
    if group is not None:
        listed = group["cells"]
        assert isinstance(listed, list)
        cells = {
            c["kind"]: c
            for c in listed
            if c["span"] == "day" and c["market"] == study.EXCESS_MARKET
        }
    days: list[dict[str, object]] = []
    day, counted = today, 0
    while counted < AHEAD_DAYS:
        day += timedelta(days=1)
        if day.weekday() >= 5:
            continue
        counted += 1
        members = sp500_members(day)
        reports = [
            {
                "symbol": r["symbol"],
                "name": r["name"],
                "time": EARNINGS_TIMES.get(r["time"], "time not given"),
                "cap": _dollars(r.get("marketCap", "")),
            }
            for r in fetch(day)
            if r["symbol"].replace("/", "-").replace(".", "-") in members
        ]
        if reports:
            days.append({"day": day.isoformat(), "reports": reports})
    return {"lines": [earnings_line(k, cells.get(k)) for k in EARNINGS_WORDS], "days": days}


# Step 47, the predictions page (docs/steps/predicts.md), in words a reader without financial
# training follows (amended 2026-11-21): no code, no term unexplained, counts and never a
# probability. Since 2026-11-22 it states forecasts only (step 48), no if-then cards.
PLAIN_MARKETS = {
    "SPY / ES": "the US stock market",
    "COMP": "US tech stocks",
    "GC / XAU": "the price of gold",
    "BRN": "the price of oil",
    "UGA": "US gasoline prices",
    "UNG": "US natural gas prices",
    "DXY": "the US dollar",
    "EURUSD": "the euro against the dollar",
    "GBPUSD": "the British pound against the dollar",
    "USDJPY": "the dollar against the Japanese yen",
    "USDCAD": "the dollar against the Canadian dollar",
    "UST10Y / ZN": "the interest the US government pays to borrow money for 10 years",
    "UST5Y / ZF": "the interest the US government pays to borrow money for 5 years",
    "T5YIE": "the inflation investors expect over the next 5 years",
    "VIX": "the stock market's fear gauge",
    "XLE": "US energy company stocks",
    "XLU": "US power and water company stocks",
    "ITB": "US homebuilder stocks",
    "ITA": "US defence company stocks",
    "TSX": "the Canadian stock market",
    "BTC": "the price of bitcoin",
    "ETH": "the price of ether",
}
PLAIN_KINDS = {
    ("nfp", "above"): "The US jobs report shows more new jobs than economists expected",
    ("nfp", "below"): "The US jobs report shows fewer new jobs than economists expected",
    ("cpi", "above"): "US prices rise faster than economists expected",
    ("cpi", "below"): "US prices rise slower than economists expected",
    ("opec", "oil up"): "The big oil-producing countries (OPEC+) make a decision that lifts oil",
    ("opec", "oil down"): "The big oil-producing countries (OPEC+) make a decision that drops oil",
    ("earnings", "above"): "One of the 30 Dow companies earns more than experts expected",
    ("earnings", "as expected"): "One of the 30 Dow companies earns what experts expected",
    ("earnings", "below"): "One of the 30 Dow companies earns less than experts expected",
    ("earnings500", "above"): "A big US company earns more than experts expected",
    ("earnings500", "as expected"): "A big US company earns what experts expected",
    ("earnings500", "below"): "A big US company earns less than experts expected",
    ("splits", "alone"): "A big US company announces a stock split",
    ("additions", "added"): "A company is announced as joining the 500 biggest US companies",
}


def _plain_record(right: int, graded: int, cases: str) -> str:
    """The replay's record in words, as counts: "In 58 past jobs reports, this held 39 times and
    failed 19 times." """
    return f"{cases}, this held {right:,} times and failed {graded - right:,} times."


# Step 48, stated forecasts (docs/steps/stated-forecasts.md): what will happen, from a market's
# own long run where it holds, and after news that has landed where its cell holds; each kept once
# in forecasts.csv and graded when its span ends.
STATED_MAX = 3
# The front page shows one card per area (the owner, 2026-11-22, docs/steps/predicts.md).
AREAS = {
    **dict.fromkeys(
        ("SPY / ES", "COMP", "VIX", "DAX", "SX5E", "UKX", "SXXP", "NKY", "ITA", "XLE", "XLU"),
        "stocks",
    ),
    **dict.fromkeys(("ITB", "COIN", "ALL", "TSX"), "stocks"),
    **dict.fromkeys(("UST10Y / ZN", "UST5Y / ZF", "T5YIE"), "interest rates and inflation"),
    **dict.fromkeys(("DXY", "EURUSD", "GBPUSD", "USDJPY", "USDCAD"), "currencies"),
    **dict.fromkeys(("BRN", "UGA", "UNG"), "energy"),
    "GC / XAU": "gold",
    **dict.fromkeys(("CORN", "WEAT", "SOYB", "KC"), "food"),
    **dict.fromkeys(("BTC", "ETH"), "crypto"),
    "US home prices": "homes",
}


def one_per_area[T](
    items: Sequence[T], market: Callable[[T], str], taken: Iterable[str]
) -> list[T]:
    """The first item of each area not in ``taken``, in order; a market with no area is its own."""
    seen, out = set(taken), []
    for item in items:
        area = AREAS.get(market(item), market(item))
        if area not in seen:
            seen.add(area)
            out.append(item)
    return out


FORECAST_FIELDS = (
    "stated",
    "kind",
    "market",
    "span",
    "direction",
    "first",
    "last",
    "event",
    "grade",
)
LONG_RUN_WORDS = {"tomorrow": "tomorrow", "week": "week", "month": "month", "year": "year"}


def _plain_day(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%a, %b %-d, %Y")


def _plain_month(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%B %Y")


def _months_after(day: date, months: int) -> date:
    total = day.year * 12 + day.month - 1 + months
    return date(total // 12, total % 12 + 1, 1)


def stated(
    data: Mapping[str, object], today: date, kept: Sequence[Mapping[str, str]] = ()
) -> list[dict[str, object]]:
    """The forecasts the page states on ``today``'s evening, after-news ones first, then one long
    run per market at its shortest span that holds; ``STATED_MAX`` at most. Each carries the row
    ``forecasts.csv`` would keep for it under ``row``; a long run still open in ``kept`` is shown
    as it was kept."""
    names = data.get("market_names") or {}
    assert isinstance(names, dict)
    out: list[dict[str, object]] = []
    ask = data.get("ask") or []
    assert isinstance(ask, list)
    for f in ask:
        latest = f.get("latest") or {}
        for c in filter(_answered, f["cells"]):
            until = c.get("open_until")
            if until is None or c["span"] == "day" or until < today.isoformat():
                continue
            what = PLAIN_MARKETS.get(c["market"], c["market_name"])
            label = PLAIN_KINDS.get((f["name"], c["kind"]), c["kind"])
            out.append(
                {
                    "stated": True,
                    "market": c["market"],
                    "day": None,
                    "until": until,
                    "when": f"News of {_plain_day(latest['day'])}",
                    "event": label[0].upper() + label[1:],
                    "outcome": f"{what} higher on {_plain_day(until)} than before the news"
                    if c["answer"] == "up"
                    else f"{what} lower on {_plain_day(until)} than before the news",
                    "direction": c["answer"],
                    "record": _plain_record(
                        c["right"], c["graded"], f"In {c['graded']:,} past cases"
                    ),
                    "right": c["right"],
                    "called": c["graded"],
                    "unit": "past cases",
                    "note": "Some of these days may already have passed; it is counted from the"
                    " close before the news.",
                    "link": f"#ask/{f['name']}/{c['kind']}",
                    "row": {
                        "kind": "after news",
                        "market": c["market"],
                        "span": c["span"],
                        "direction": c["answer"],
                        "first": latest["day"],
                        "last": until,
                        "event": f"{f['name']} {latest['day']}",
                    },
                }
            )
    runs = data.get("forecasts") or []
    assert isinstance(runs, list)
    seen: set[str] = set()
    for r in runs:
        if r["verdict"] != "holds" or r["now"] is None or r["market"] in seen:
            continue
        seen.add(r["market"])
        held = [
            k
            for k in kept
            if (k["kind"], k["market"], k["span"]) == ("long run", r["market"], r["span"])
            and k["last"] >= today.isoformat()
        ]
        direction = held[-1]["direction"] if held else str(r["now"])
        rising = direction == "up"
        if r["market"] == HOME:
            home_latest = date.fromisoformat(str(r["latest"]))
            first, last = _months_after(home_latest, 1), _months_after(home_latest, 12)
            if held:
                last = date.fromisoformat(held[-1]["last"])
                first, home_latest = date.fromisoformat(held[-1]["first"]), _months_after(last, -12)
            title = (
                f"US home prices, in the 12 months after {_plain_month(home_latest.isoformat())}"
            )
            outcome = (
                f"{'higher' if rising else 'lower'} in {_plain_month(last.isoformat())}"
                f" than in {_plain_month(home_latest.isoformat())}"
            )
            when = f"Checked when {_plain_month(last.isoformat())}'s figure is out"
        else:
            length = study.LONG_RUN_SPANS[r["span"]]
            first, last = _weekdays_after(today, 1), _weekdays_after(today, length)
            if held:
                first, last = (
                    date.fromisoformat(held[-1]["first"]),
                    date.fromisoformat(held[-1]["last"]),
                )
            base = first - timedelta(days=1)
            while base.weekday() >= 5:
                base -= timedelta(days=1)
            what = PLAIN_MARKETS.get(r["market"], names.get(r["market"], r["market"]))
            title = f"{what[0].upper()}{what[1:]}, over the next {LONG_RUN_WORDS[r['span']]}"
            outcome = (
                f"{'higher' if rising else 'lower'} on {_plain_day(last.isoformat())}"
                f" than on {_plain_day(base.isoformat())}"
            )
            when = f"Checked after the close on {_plain_day(last.isoformat())}"
        stated_on = held[-1]["stated"] if held else today.isoformat()
        when = f"Stated {_plain_day(stated_on)} · {when[0].lower()}{when[1:]}"
        unit = "years" if r["span"] == "year" else f"{r['span']}s"
        out.append(
            {
                "stated": True,
                "market": r["market"],
                "day": None,
                "until": last.isoformat(),
                "when": when,
                "event": title,
                "outcome": outcome,
                "direction": direction,
                "record": _plain_record(
                    r["right"], r["called"], f"Tested on {r['called']:,} past {unit}, one at a time"
                ),
                "right": r["right"],
                "called": r["called"],
                "unit": f"past {unit}",
                "note": f"It goes the way most past {unit} went. It says nothing about how far.",
                "link": "",
                "row": {
                    "kind": "long run",
                    "market": r["market"],
                    "span": r["span"],
                    "direction": direction,
                    "first": first.isoformat(),
                    "last": last.isoformat(),
                    "event": "",
                },
            }
        )
    return one_per_area(out, lambda t: str(t["market"]), ())[:STATED_MAX]


def keep_forecasts(
    rows: list[dict[str, str]], told: Sequence[Mapping[str, object]], today: date
) -> list[dict[str, str]]:
    """``rows`` with each forecast in ``told`` added once: a long run only when its span starts
    after every kept row of its market and span has ended, an after-news one once per event,
    market and span."""
    kept = list(rows)
    for t in told:
        new = t["row"]
        assert isinstance(new, dict)
        same = [
            r
            for r in kept
            if (r["kind"], r["market"], r["span"]) == (new["kind"], new["market"], new["span"])
        ]
        if new["kind"] == "long run" and any(r["last"] >= new["first"] for r in same):
            continue
        if new["kind"] == "after news" and any(r["event"] == new["event"] for r in same):
            continue
        kept.append(
            {"stated": today.isoformat(), **{k: str(v) for k, v in new.items()}, "grade": ""}
        )
    return kept


def grade_forecasts(
    rows: list[dict[str, str]], closes: Callable[[str], Sequence[sources.DailyClosingPrice]]
) -> list[dict[str, str]]:
    """Each ungraded row whose last day has a close: *came true* if the close of its last day is
    beyond the last close before its first day in its direction, else *did not*."""
    graded = []
    for r in rows:
        if not r["grade"]:
            series = closes(r["market"])
            first, last = date.fromisoformat(r["first"]), date.fromisoformat(r["last"])
            before = [c for c in series if c.day < first]
            upto = [c for c in series if c.day <= last]
            if before and series and series[-1].day >= last:
                move = upto[-1].price - before[-1].price
                right = move > 0 if r["direction"] == "up" else move < 0
                r = {**r, "grade": "came true" if right else "did not"}
        graded.append(r)
    return graded


def forecast_tally(rows: Sequence[Mapping[str, str]]) -> dict[str, int]:
    grades = [r["grade"] for r in rows]
    return {
        "came_true": grades.count("came true"),
        "did_not": grades.count("did not"),
        "open": grades.count(""),
    }


def week_watch(today: date, cache_dir: Path) -> list[dict[str, object]]:
    """Each scheduled event `live` does not call, from the day after ``today`` to ``AHEAD_DAYS``
    after it, oldest first, at its New York time (docs/steps/watch-ahead.md)."""
    start, end = today + timedelta(days=1), today + timedelta(days=AHEAD_DAYS)
    watch = []
    for flow in flows.EVENT_FLOWS:
        if flows.called_live(flow) or not isinstance(
            flow, flows.FedFlow | flows.EcbFlow | flows.StatementFlow | flows.TradingViewFlow
        ):
            continue
        for at, title in flow.scheduled(cache_dir, start, end):
            local = at.astimezone(sources.NEW_YORK)
            if not start <= local.date() <= end:
                continue
            watch.append(
                {
                    "day": local.date().isoformat(),
                    "time": f"{local:%H:%M}",
                    "event": flow.cli_name,
                    "label": flow.label,
                    "title": title,
                    "lesser": flow.lesser,
                }
            )
    return sorted(watch, key=lambda event: (str(event["day"]), str(event["time"])))


SCOREBOARD_DATA_MARK = "__SCOREBOARD_DATA__"
PREDICTS_DATA_MARK = "__PREDICTS_DATA__"


# Steps 49 and 50, our guesses and the guess ledger (docs/steps/our-guesses.md,
# docs/steps/guess-ledger.md): the Subscription LLM's guesses from the day's news, up to 50 an
# evening, each checked, kept before its span, graded by the closes, reviewed by the model against
# its own reasoning, and the reviews turned monthly into numbered lessons.
GUESS_MODEL = "claude-opus-5-5"
GUESS_MAX = 50
GUESS_TWINS = {"SPY / ES": "stocks", "COMP": "stocks"}
GUESS_TAGS = (
    "momentum",
    "reversal",
    "interest rates",
    "inflation",
    "jobs",
    "earnings",
    "oil supply",
    "geopolitics",
    "policy",
    "sentiment",
    "season",
    "other",
)
GUESS_CONFIDENCE = ("low", "medium", "high")
HORIZONS = (("week", 5), ("month", 21), ("quarter", 63), ("year", 261))
GUESS_APART = 5
GUESS_FIELDS = (
    "stated",
    "market",
    "horizon",
    "direction",
    "first",
    "last",
    "statement",
    "reasoning",
    "tag",
    "confidence",
    "source",
    "model",
    "lessons",
    "grade",
    "move",
    "review",
)
LESSONS_HEAD = re.compile(r"^## Version (\d+), (\d{4}-\d{2}-\d{2})$", re.M)


def _weekdays_between(start: date, end: date) -> int:
    count, day = 0, start
    while day < end:
        day += timedelta(days=1)
        count += day.weekday() < 5
    return count


def horizon(today: date, last: date) -> str | None:
    """The horizon of a guess made on ``today``'s evening ending on ``last``; none past a year."""
    ahead = _weekdays_between(today, last)
    return next((name for name, most in HORIZONS if ahead <= most), None)


def _run_model(prompt: str, web: bool) -> str:
    """One fresh Subscription LLM session; its answer's text."""
    command = ["claude", "-p", prompt, "--model", GUESS_MODEL, "--output-format", "json"]
    if web:
        command += ["--allowedTools", "WebSearch"]
    done = subprocess.run(command, capture_output=True, text=True, timeout=1800, check=True)
    return str(json.loads(done.stdout)["result"])


def _json_list(answer: str) -> list[object] | None:
    """The first JSON list in ``answer``, at any ``[``; none if there is none."""
    decoder = json.JSONDecoder()
    for at in (i for i, ch in enumerate(answer) if ch == "["):
        try:
            found, _ = decoder.raw_decode(answer, at)
        except json.JSONDecodeError:
            continue
        if isinstance(found, list):
            return found
    return None


def _prompt(name: str, **fields: str) -> str:
    return files("fortuneteller").joinpath(name).read_text().format(**fields)


def market_list() -> str:
    names = market_names()
    return "\n".join(
        f"{m}: {PLAIN_MARKETS.get(m, names.get(m, m))}" for m in study.MVP_PRICE_SERIES
    )


def _open(rows: Sequence[Mapping[str, str]]) -> list[Mapping[str, str]]:
    return [r for r in rows if not r.get("grade")]


def ask_for_guesses(today: date, rows: Sequence[Mapping[str, str]], lessons: str) -> str:
    """The model's new guesses for ``today``'s evening, shown the open ones and the lessons."""
    shown = "\n".join(
        f"{r['market']} {r.get('horizon', '')} {r['direction']} to {r['last']}: "
        f"{r.get('statement') or r.get('reason', '')}"
        for r in _open(rows)
    )
    return _run_model(
        _prompt(
            "guess_prompt.txt",
            today=today.isoformat(),
            markets=market_list(),
            tags=", ".join(GUESS_TAGS),
            most=str(GUESS_MAX),
            open=shown or "(none)",
            lessons=lessons or "(none yet)",
        ),
        web=True,
    )


def _why_not(g: Mapping[str, object], kept: Sequence[Mapping[str, str]], today: date) -> str | None:
    market, direction = g.get("market"), g.get("direction")
    statement, reasoning = str(g.get("statement", "")).strip(), str(g.get("reasoning", "")).strip()
    source = str(g.get("source", "")).strip()
    try:
        last = date.fromisoformat(str(g.get("end", "")))
    except ValueError:
        return "no end date"
    reach = horizon(today, last)
    if market not in study.MVP_PRICE_SERIES:
        return "a market not listed"
    if direction not in ("up", "down"):
        return "a direction not up or down"
    if last.weekday() >= 5 or _weekdays_between(today, last) < 2 or reach is None:
        return "an end date not a weekday from the second after tonight to a year"
    if not statement or len(statement.split()) > 40:
        return "a statement missing or over 40 words"
    if not 15 <= len(reasoning.split()) <= 150:
        return "reasoning not 15 to 150 words"
    if "%" in statement or "%" in reasoning:
        return "a percent sign"
    if g.get("tag") not in GUESS_TAGS:
        return "a tag not listed"
    if g.get("confidence") not in GUESS_CONFIDENCE:
        return "a confidence not low, medium or high"
    if not source.startswith("https://") or " " in source:
        return "no https link to its news"
    group = GUESS_TWINS.get(str(market), str(market))
    for r in _open(kept):
        near = abs(
            _weekdays_between(
                min(last, date.fromisoformat(r["last"])), max(last, date.fromisoformat(r["last"]))
            )
        )
        if GUESS_TWINS.get(r["market"], r["market"]) == group and near < GUESS_APART:
            return f"repeats an open guess on {r['market']} ending {r['last']}"
    return None


def keep_guesses(
    answer: str, rows: list[dict[str, str]], today: date, lessons_version: str = "0"
) -> tuple[list[dict[str, str]], list[str]]:
    """``rows`` with each acceptable guess in ``answer`` added, and why each other was dropped."""
    guesses = _json_list(answer)
    if guesses is None:
        return rows, ["the answer held no JSON list"]
    kept, dropped = list(rows), []
    first = _weekdays_after(today, 1)
    for g in guesses[:GUESS_MAX]:
        if not isinstance(g, dict):
            dropped.append(f"not a guess: {g!r}")
            continue
        why = _why_not(g, kept, today)
        if why:
            dropped.append(f"{g.get('market')} to {g.get('end')}: {why}")
            continue
        last = date.fromisoformat(str(g["end"]))
        kept.append(
            {
                "stated": today.isoformat(),
                "market": str(g["market"]),
                "horizon": str(horizon(today, last)),
                "direction": str(g["direction"]),
                "first": first.isoformat(),
                "last": last.isoformat(),
                "statement": str(g["statement"]).strip(),
                "reasoning": str(g["reasoning"]).strip(),
                "tag": str(g["tag"]),
                "confidence": str(g["confidence"]),
                "source": str(g["source"]).strip(),
                "model": GUESS_MODEL,
                "lessons": lessons_version,
                "grade": "",
                "move": "",
                "review": "",
            }
        )
    return kept, dropped


def grade_guesses(
    rows: list[dict[str, str]], closes: Callable[[str], Sequence[sources.DailyClosingPrice]]
) -> list[dict[str, str]]:
    """``grade_forecasts`` on the ledger, keeping each newly graded row's move."""
    graded = []
    for r in rows:
        if r.get("grade"):
            graded.append(r)
            continue
        new = grade_forecasts([r], closes)[0]
        if new["grade"]:
            series = closes(r["market"])
            first, last = date.fromisoformat(r["first"]), date.fromisoformat(r["last"])
            before = [c for c in series if c.day < first][-1].price
            after = [c for c in series if c.day <= last][-1].price
            new = {**new, "move": f"{before:g} to {after:g}"}
        graded.append(new)
    return graded


def review_guesses(rows: list[dict[str, str]], ask: Callable[[str], str]) -> list[dict[str, str]]:
    """Each graded row with no review given the model's review of its own reasoning; the grade is
    never changed."""
    due = [
        i
        for i, r in enumerate(rows)
        if r.get("grade") and not r.get("review") and r.get("reasoning")
    ]
    if not due:
        return rows
    listed = "\n".join(
        json.dumps(
            {
                "id": i,
                "market": rows[i]["market"],
                "statement": rows[i]["statement"],
                "reasoning": rows[i]["reasoning"],
                "grade": rows[i]["grade"],
                "move": rows[i]["move"],
                "from": rows[i]["first"],
                "to": rows[i]["last"],
            }
        )
        for i in due
    )
    reviews = _json_list(ask(_prompt("review_prompt.txt", guesses=listed))) or []
    out = list(rows)
    for item in reviews:
        if isinstance(item, dict) and item.get("id") in due:
            text = " ".join(str(item.get("review", "")).split()[:80])
            out[int(item["id"])] = {**out[int(item["id"])], "review": text}
    return out


def lessons_version(text: str) -> tuple[int, str | None]:
    """The latest version's number and date in ``lessons.md``; 0 and none before the first."""
    found = LESSONS_HEAD.findall(text)
    return (int(found[0][0]), found[0][1]) if found else (0, None)


def update_lessons(
    text: str, rows: Sequence[Mapping[str, str]], today: date, ask: Callable[[str], str]
) -> str:
    """On the first evening of a month without a version, version N + 1 from the reviews since N,
    newest version first; else ``text`` as it was."""
    number, dated = lessons_version(text)
    if dated is not None and dated[:7] == today.isoformat()[:7]:
        return text
    since = dated or "0000-00-00"
    reviews = [r for r in rows if r.get("review") and r["last"] >= since]
    if not reviews:
        return text
    listed = "\n".join(
        f"- {r['market']} {r['direction']} to {r['last']} ({r['tag']}, {r['confidence']}): "
        f"{r['grade']}. {r['review']}"
        for r in reviews
    )
    body = ask(_prompt("lessons_prompt.txt", lessons=text or "(none yet)", reviews=listed))
    body = " ".join(body.split()[:400])
    head = f"## Version {number + 1}, {today.isoformat()}"
    title = "# Lessons\n\nWhat the fortune teller's guesser reads each evening, newest first.\n"
    rest = text.split("\n", 3)[3] if text.startswith("# Lessons") else ""
    return f"{title}\n{head}\n\n{body}\n\n{rest}".rstrip() + "\n"


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _write_rows(path: Path, fields: Sequence[str], rows: Sequence[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{f: r.get(f, "") for f in fields} for r in rows])


def _ledger_row(r: Mapping[str, str]) -> dict[str, str]:
    """A step 49 row read as the ledger's: its span as a horizon, its reason as its statement."""
    if "horizon" in r:
        return dict(r)
    return {
        **r,
        "horizon": r.get("span", ""),
        "statement": r.get("reason", ""),
        "reasoning": "",
        "tag": "",
        "confidence": "",
        "lessons": "0",
        "move": "",
        "review": "",
    }


def _guess(_args: argparse.Namespace) -> int:
    today = _now().astimezone(sources.NEW_YORK).date()
    folder = settings.scoreboard_dir.parent / "predicts"
    path, lessons_path = folder / "our-guesses.csv", folder / "lessons.md"
    rows = [_ledger_row(r) for r in _read_rows(path)]
    con = db.get_connection()
    db.init_db(con=con)

    def closes(market: str) -> Sequence[sources.DailyClosingPrice]:
        try:
            return study.stored_closes(market, con)
        except ValueError:
            return []

    rows = grade_guesses(rows, closes)
    lessons = lessons_path.read_text() if lessons_path.exists() else ""
    try:
        rows = review_guesses(rows, lambda prompt: _run_model(prompt, web=False))
        updated = update_lessons(lessons, rows, today, lambda prompt: _run_model(prompt, web=False))
        if updated != lessons:
            lessons_path.write_text(updated)
            lessons = updated
        answer = ask_for_guesses(today, rows, lessons)
        kept, dropped = keep_guesses(answer, rows, today, str(lessons_version(lessons)[0]))
        if dropped == ["the answer held no JSON list"]:
            print(f"guess: no JSON list, asking once more: {answer[:200]!r}", file=sys.stderr)
            kept, dropped = keep_guesses(
                ask_for_guesses(today, rows, lessons), rows, today, str(lessons_version(lessons)[0])
            )
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        print(f"guess: the model failed: {exc}", file=sys.stderr)
        _write_rows(path, GUESS_FIELDS, rows)
        return 0
    for why in dropped:
        print(f"guess: dropped {why}", file=sys.stderr)
    _write_rows(path, GUESS_FIELDS, kept)
    print(f"guess: {len(kept) - len(rows)} kept, {len(dropped)} dropped")
    return 0


FRONT_FIELDS = ("stated", "market", "direction", "last", "statement", "why", "source")
FRONT_LOCKED = ("stated", "market", "direction", "last", "source")


def front_rows(
    picks: Sequence[Mapping[str, str]], approved: Sequence[Mapping[str, str]]
) -> list[dict[str, str]]:
    """The front page's proposal (docs/steps/front-staging.md): the picked guesses with the
    ledger's words, or the owner's for a guess already approved."""
    kept = {tuple(r.get(f, "") for f in FRONT_LOCKED): r for r in approved}
    out = []
    for g in picks:
        row = {f: g.get(f, "") for f in FRONT_LOCKED}
        row["statement"] = g.get("statement", "")
        row["why"] = g.get("reasoning") or g.get("reason") or g.get("statement", "")
        old = kept.get(tuple(row[f] for f in FRONT_LOCKED))
        out.append({f: (old or row).get(f, "") for f in FRONT_FIELDS})
    return out


def unlocked(
    front: Sequence[Mapping[str, str]], ledger: Sequence[Mapping[str, str]]
) -> list[Mapping[str, str]]:
    """The rows of ``front.csv`` whose locked fields match no ledger row."""
    known = {tuple(r.get(f, "") for f in FRONT_LOCKED) for r in ledger}
    return [r for r in front if tuple(r.get(f, "") for f in FRONT_LOCKED) not in known]


def front_guesses(
    rows: Sequence[Mapping[str, str]],
    promoted: set[str],
    today: date,
    most: int,
    taken: Iterable[str] = (),
) -> list[Mapping[str, str]]:
    """The open guesses the front page shows: a promoted tag first, then high confidence, then
    the soonest end date; one per area, none in an area of ``taken``."""
    rank = {"high": 0, "medium": 1, "low": 2}
    live = [r for r in _open(rows) if r["last"] >= today.isoformat()]
    live.sort(
        key=lambda r: (
            r.get("tag") not in promoted,
            rank.get(r.get("confidence", ""), 3),
            r["last"],
        )
    )
    return one_per_area(live, lambda r: r["market"], taken)[:most]


def guess_record(rows: Sequence[Mapping[str, str]], key: str) -> list[dict[str, object]]:
    """The record by ``key`` (tag, confidence, horizon, market or lessons): each guess, and each
    evening's guesses of the value as one try once all of them are graded, right if more than
    half came true (a tie is not); rung 2's verdict on the evenings."""
    groups: dict[str, dict[str, list[bool]]] = {}
    pending = {(r.get(key) or "(none)", r["stated"]) for r in rows if not r.get("grade")}
    for r in rows:
        value = r.get(key) or "(none)"
        if r.get("grade") not in ("came true", "did not") or (value, r["stated"]) in pending:
            continue
        groups.setdefault(value, {}).setdefault(r["stated"], []).append(r["grade"] == "came true")
    out = []
    for value, evenings in sorted(groups.items()):
        each = [g for day in evenings.values() for g in day]
        tries = [sum(day) * 2 > len(day) for day in evenings.values()]
        right, n = sum(tries), len(tries)
        p = stats.binomial_p(right, n)
        verdict = (
            "too few" if n < 30 else "holds" if right >= 0.6 * n and p < 0.01 else "doesn't hold"
        )
        out.append(
            {
                key: value,
                "guesses": len(each),
                "came_true": sum(each),
                "evenings": n,
                "evenings_right": right,
                "p": p,
                "verdict": verdict,
            }
        )
    return out


FRONT_MOST = 5
STATS_KEYS = (
    ("tag", "Kind of reasoning"),
    ("confidence", "Confidence"),
    ("horizon", "Horizon"),
    ("lessons", "Lessons version"),
)


def write_stats(path: Path, rows: Sequence[Mapping[str, str]], promoted: set[str]) -> None:
    """The stats page: the tally, the record by kind, and every guess with its grade and review."""
    from html import escape

    def table(key: str, title: str) -> str:
        lines = [
            f"<tr><td>{escape(str(r[key]))}{' (promoted)' if key == 'tag' and r[key] in promoted else ''}</td>"
            f"<td>{r['came_true']} of {r['guesses']}</td><td>{r['evenings_right']} of {r['evenings']}</td>"
            f"<td>{r['verdict']}</td></tr>"
            for r in guess_record(rows, key)
        ]
        head = (
            f"<h2>{title}</h2><div class='wide'><table><tr><th></th><th>Guesses that came true</th>"
            "<th>Evenings mostly right</th><th>Verdict</th></tr>"
        )
        return head + "".join(lines) + "</table></div>" if lines else ""

    def item(r: Mapping[str, str]) -> str:
        grade = r.get("grade") or "open"
        parts = [
            f"<li class='{escape(grade.replace(' ', '-'))}'><div class='meta'>{escape(r['stated'])}"
            f" to {escape(r['last'])} · {escape(PLAIN_MARKETS.get(r['market'], r['market']))}"
            f" {escape(r['direction'])}"
            f" · {escape(r.get('tag') or '')} · {escape(r.get('confidence') or '')} confidence"
            f" · <b>{escape(grade)}</b>{(' (' + escape(r['move']) + ')') if r.get('move') else ''}</div>",
            f"<p class='statement'>{escape(r.get('statement') or '')}</p>",
        ]
        if r.get("reasoning"):
            parts.append(f"<p><b>Reasoning:</b> {escape(r['reasoning'])}</p>")
        if r.get("review"):
            parts.append(f"<p><b>Looking back:</b> {escape(r['review'])}</p>")
        if r.get("source"):
            parts.append(
                f"<p><a href='{escape(r['source'])}' rel='noopener nofollow'>The news</a></p>"
            )
        return "".join(parts) + "</li>"

    t = forecast_tally(rows)
    newest = sorted(rows, key=lambda r: (r["stated"], r["last"]), reverse=True)
    body = (
        "<h1>Our guesses: the record</h1>"
        f"<p class='lede'>Every guess the fortune teller has made, with its reasoning, its grade once its"
        f" end date passed, and its own look back. {t['came_true']} came true, {t['did_not']} did not,"
        f" {t['open']} still open. Guesses made on one evening move together, so a kind of reasoning is"
        " judged by its evenings: an evening counts once, right if most of its guesses came true. A kind"
        " is promoted when it has 30 evenings, at least 60 in 100 mostly right, and a chance of under"
        " 1 in 100 that a coin would do as well. For fun, not financial advice.</p>"
        "<p><a href='../'>Back to Fortuneteller predicts</a>"
        + (
            " · <a href='../lessons.md'>The lessons</a>"
            if (path.parent.parent / "lessons.md").exists()
            else ""
        )
        + "</p>"
        + "".join(table(k, title) for k, title in STATS_KEYS)
        + "<h2>Every guess, newest first</h2><ol class='all'>"
        + "".join(item(r) for r in newest)
        + "</ol>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    page = files("fortuneteller").joinpath("stats.html").read_text()
    path.write_text(page.replace("__STATS_BODY__", body))


def stated_forecasts(
    con: duckdb.DuckDBPyConnection, data: Mapping[str, object], today: date, kept_path: Path
) -> dict[str, object]:
    """Step 48 on the evening's page: the long runs measured, the kept forecasts graded, the new
    ones kept, and what the page states with the tally."""
    try:
        home = home_prices(_fred_key("scoreboard"))
    except sources.FredError as exc:
        print(f"scoreboard: home prices: {exc}", file=sys.stderr)
        home = []
    runs = long_runs(con, home)
    rows = _read_rows(kept_path)

    def closes(market: str) -> Sequence[sources.DailyClosingPrice]:
        return home if market == HOME else study.stored_closes(market, con)

    rows = grade_forecasts(rows, closes)
    told = stated({**data, "forecasts": runs}, today, rows)
    rows = keep_forecasts(rows, told, today)
    _write_rows(kept_path, FORECAST_FIELDS, rows)
    guesses = [_ledger_row(r) for r in _read_rows(kept_path.parent / "our-guesses.csv")]
    promoted = {str(t["tag"]) for t in guess_record(guesses, "tag") if t["verdict"] == "holds"}
    write_stats(kept_path.parent / "stats" / "index.html", guesses, promoted)
    taken = {AREAS.get(str(t["market"]), str(t["market"])) for t in told}
    picks = front_guesses(guesses, promoted, today, FRONT_MOST - len(told), taken)
    approved = _read_rows(kept_path.parent / "front.csv")
    _write_rows(kept_path.parent / "front-next.csv", FRONT_FIELDS, front_rows(picks, approved))
    return {
        "guess_tally": forecast_tally([g for g in guesses if g.get("grade") != "void"]),
        "stated": [{k: v for k, v in t.items() if k != "row"} for t in told],
        "tally": forecast_tally(rows),
        "kept_since": rows[0]["stated"] if rows else None,
    }


def _scoreboard(_args: argparse.Namespace) -> int:
    try:
        rows = study.read_calls(settings.calls_path)
    except ValueError as exc:
        print(f"scoreboard: {exc}", file=sys.stderr)
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    if db.count_rows("event_instances", con=con) == 0 or db.count_rows("daily_bars", con=con) == 0:
        print(
            "scoreboard: no releases or prices stored; run `fortuneteller load-releases`, "
            "`load-prices` and `load-surprises` first",
            file=sys.stderr,
        )
        return 1
    today = _now().astimezone(sources.NEW_YORK).date()
    try:
        graded, bad = _read_guesses(con)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"scoreboard: the guesses cannot be read: {exc}", file=sys.stderr)
        return 1
    ahead = None
    try:
        ahead = week_ahead(con, today, settings.cache_dir)
    except sources.CalendarError as exc:
        print(f"scoreboard: the week ahead: {exc}", file=sys.stderr)
    watch = None
    try:
        watch = week_watch(today, settings.cache_dir)
    except sources.CalendarError as exc:
        print(f"scoreboard: also on the calendar: {exc}", file=sys.stderr)
    try:
        data = scoreboard_data(
            rows, con, today, graded, bad, ahead, watch, lambda d: sources.fetch_earnings_day(d)
        )
    except ValueError as exc:
        print(f"scoreboard: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    page = files("fortuneteller").joinpath("scoreboard.html").read_text()
    out = settings.scoreboard_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.json").write_text(text)
    # Inside <script>, a "<" in the data could end the element; JSON reads < as the same "<".
    embedded = text.replace("<", "\\u003c")
    (out / "index.html").write_text(page.replace(SCOREBOARD_DATA_MARK, embedded))
    predicts = out.parent / "predicts"
    predicts.mkdir(parents=True, exist_ok=True)
    told = {
        "written": data.get("written"),
        **stated_forecasts(con, data, today, predicts / "forecasts.csv"),
    }
    shown = json.dumps(told, ensure_ascii=False).replace("<", "\\u003c")
    template = files("fortuneteller").joinpath("predicts.html").read_text()
    (predicts / "index.html").write_text(template.replace(PREDICTS_DATA_MARK, shown))
    events = data["events"]
    assert isinstance(events, list)
    print(
        f"scoreboard: {len(events)} events, {len(rows)} call rows, data to {data['data_until']}; "
        f"written to {out}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    # Each flow's short name on the command line, read when the parser is built.
    event_names = [flow.cli_name for flow in flows.EVENT_FLOWS]
    parser = argparse.ArgumentParser(prog="fortuneteller", description="FortuneTeller CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create the DuckDB file with all tables")
    sub.add_parser(
        "guess", help="step 49: the evening's guesses from the news, kept in guesses.csv"
    ).set_defaults(func=_guess)
    sub.add_parser(
        "forecasts", help="step 48: each market's long run, walk-forward over spans"
    ).set_defaults(func=_forecasts)
    p_init.set_defaults(func=_init)

    p_seed = sub.add_parser("seed", help="load the seed CSVs into the store")
    p_seed.set_defaults(func=_seed)

    p_demo = sub.add_parser("query-demo", help="print a sample effect-size lookup row")
    p_demo.set_defaults(func=_query_demo)

    p_releases = sub.add_parser(
        "load-releases", help="load every event type's history (CPI, NFP, Fed)"
    )
    p_releases.set_defaults(func=_load_releases)

    p_prices = sub.add_parser(
        "load-prices", help="load daily closes from Yahoo and FRED and measure each release's move"
    )
    p_prices.add_argument(
        "--companies",
        action="store_true",
        help="load only the companies of the CEO scandals (step 20), each under its ticker",
    )
    p_prices.add_argument(
        "--seed",
        type=Path,
        help="with --companies: the companies of this seed instead (a ticker column)",
    )
    p_prices.set_defaults(func=_load_prices)

    p_surprises = sub.add_parser(
        "load-surprises", help="load each event's surprise against every expected value"
    )
    p_surprises.set_defaults(func=_load_surprises)

    p_tone = sub.add_parser(
        "load-tone", help="score each Fed statement's tone against the previous statement's"
    )
    p_tone.set_defaults(func=_load_tone)
    p_sentiment = sub.add_parser(
        "load-sentiment",
        help="score each Fed statement with the FOMC-built dictionary against the previous one",
    )
    p_sentiment.set_defaults(func=_load_sentiment)

    p_surprise = sub.add_parser(
        "surprise", help="does each instrument's release-day move follow the event's surprise?"
    )
    p_surprise.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    p_surprise.set_defaults(func=_surprise)

    p_follows = sub.add_parser(
        "follows",
        help="what each market did over a day, a week and a month after each kind of event",
    )
    p_follows.add_argument(
        "--event", choices=list(FOLLOWS_NOUNS), default="fomc", help="the events (default: fomc)"
    )
    p_follows.add_argument(
        "--after-the-day",
        action="store_true",
        help="spans from the close of the reaction day, the ones a trigger can be graded on",
    )
    p_follows.add_argument(
        "--long",
        action="store_true",
        help="over a quarter and a year, each answer also counting each cycle once (Fed only)",
    )
    p_follows.set_defaults(func=_follows)

    p_triggers = sub.add_parser(
        "triggers",
        help="answer each trigger in data/triggers/ from the reaction close, and log and grade it",
    )
    p_triggers.set_defaults(func=_triggers)

    p_post = sub.add_parser(
        "weekly-post",
        help="draft the week's post: its calls and grades, the record, and the page's visitors",
    )
    p_post.set_defaults(func=_weekly_post)

    p_article = sub.add_parser(
        "read-article",
        help="read a pasted text into a trigger row it reports, if a measured kind; files nothing",
    )
    p_article.add_argument("file", help="the text, as a file")
    p_article.set_defaults(func=_read_article)

    p_raw = sub.add_parser(
        "raw-move", help="compare each instrument's moves on an event's days with ordinary days"
    )
    p_raw.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    p_raw.add_argument(
        "--week",
        action="store_true",
        help="compare five-day moves, from the close before each day to the fifth close from it",
    )
    p_raw.set_defaults(func=_raw_move)

    p_predict = sub.add_parser(
        "predict", help="replay every release, predicting each from the ones before it"
    )
    p_predict.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    given = p_predict.add_mutually_exclusive_group()
    given.add_argument(
        "--actual",
        type=float,
        help="the next release's actual (percent for CPI, thousands for payrolls): predict its "
        "day and log each link's line to data/calls.csv",
    )
    given.add_argument(
        "--fetch",
        action="store_true",
        help="as --actual, with the actual read from TradingView's calendar once it appears",
    )
    p_predict.set_defaults(func=_predict)

    p_live = sub.add_parser(
        "live", help="predict --fetch for each event released today; the release-day job's command"
    )
    p_live.set_defaults(func=_live)

    p_score = sub.add_parser(
        "score", help="grade the calls logged in data/calls.csv, beside the replay"
    )
    p_score.set_defaults(func=_score)

    p_scoreboard = sub.add_parser(
        "scoreboard",
        help="write the scoreboard page and its data: every call graded, every verdict and record",
    )
    p_scoreboard.set_defaults(func=_scoreboard)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
