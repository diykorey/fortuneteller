"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``); ``load-releases`` loads the CPI and jobs-report release
histories from FRED (MVP step 1 ``study``) and the Fed's decisions (rung 1); ``load-prices`` loads
the five instruments' daily closes and measures their move around each release (MVP step 2);
``raw-move`` compares each instrument's moves on an event's days with ordinary days, which no
stored event touched (MVP step 3); ``load-surprises`` stores each release's CPI and payroll surprise
and ``surprise`` measures how the moves follow it (MVP step 4, rung 1).
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, date, datetime

import duckdb

from . import db, expectations, flows, seed, sources, study
from .config import settings
from .models import Surprise

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
    except (sources.FredError, sources.FedError, ValueError) as exc:
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


def _load_prices(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    if db.count_rows("event_instances", con=con) == 0:
        print(
            "load-prices: no releases stored; run `fortuneteller load-releases` first",
            file=sys.stderr,
        )
        return 1
    try:
        study.load_daily_bars(con=con)
        release_counts = study.store_observations(con=con)
    except (sources.YahooError, ValueError) as exc:
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
    return 0


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
    lines += [
        "",
        f"{study.TRACKS} = corr as expected, p < {study.TRACK_P_BAR}, hit rate >= "
        f"{study.HIT_RATE_BAR:.0%}; {study.UNCLEAR} = one of the two; "
        f"{study.DOESNT_TRACK} = neither",
    ]
    return [line.rstrip() for line in lines]


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
    stored = con.execute(
        "SELECT count(*) FROM surprises s JOIN event_instances e ON e.event_id = s.event_id "
        "WHERE e.event_type = ? AND e.country = ? AND s.measure = ? AND s.baseline = ?",
        [flow.event_type, flow.country, measure, baseline],
    ).fetchone()
    for missing, command in (
        (not flows.stored_events(flow, con=con), "load-releases"),
        (db.count_rows("observations", con=con) == 0, "load-prices"),
        (stored is None or stored[0] == 0, "load-surprises"),
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
    sign = "+" if signed else ""
    return f"{value:{sign}.1f} bp" if unit == "bps" else f"{value * 100:{sign}.2f}%"


def describe_raw_moves(results: dict[str, study.RawMove], label: str) -> list[str]:
    """The report: a verdict line per instrument, an era line per instrument, and the rule.

    ``label`` names the event in the headers: a three-letter name keeps the columns aligned.
    """
    lines = [f"instrument   {label} days  median {label}  median other  ratio  p       verdict"]
    for instrument, raw in results.items():
        c = raw.overall
        lines.append(
            f"{instrument:<12} {c.event_days:>8}  {_move_size(c.median_event, raw.unit):>10}  "
            f"{_move_size(c.median_other, raw.unit):>12}  {c.ratio:>5.2f}  {c.p:.4f}  {c.verdict}"
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
    lines += [
        "",
        f"{study.MOVES} = ratio >= {study.MOVE_RATIO_BAR:.2f} and p < {study.MOVE_P_BAR}; "
        f"{study.UNCLEAR} = one of the two; {study.DOESNT_MOVE} = neither; "
        f"other = days with no {_any_of(flow.label for flow in flows.EVENT_FLOWS)} reaction",
    ]
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
        results = study.measure_raw_moves(flow, con=con)
    except ValueError as exc:
        print(f"raw-move: {exc}", file=sys.stderr)
        return 1
    for line in describe_raw_moves(results, label=flow.label):
        print(line)
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
    baseline = expectations.NASDAQ_CONSENSUS
    stored = con.execute(
        "SELECT count(*) FROM surprises s JOIN event_instances e ON e.event_id = s.event_id "
        "WHERE e.event_type = ? AND e.country = ? AND s.baseline = ?",
        [flow.event_type, flow.country, baseline],
    ).fetchone()
    if stored is None or stored[0] == 0 or db.count_rows("observations", con=con) == 0:
        print(
            f"predict: no {baseline} surprises or moves for {args.event} yet; run "
            "`fortuneteller load-prices` and `fortuneteller load-surprises` first",
            file=sys.stderr,
        )
        return 1
    if args.actual is not None:
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
    print(
        f"{study.HOLDS} = right on at least {study.HIT_RATE_BAR:.0%} of at least "
        f"{study.MIN_PREDICTIONS} predictions, binomial p < {study.TRACK_P_BAR} against 50%; "
        f"{study.TOO_FEW} = under {study.MIN_PREDICTIONS} predictions"
    )
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
    actual: float,
    con: duckdb.DuckDBPyConnection,
) -> int:
    """The prediction for the next release, from its typed-in actual and the calendars."""
    measure = rule.combinations[0][0]
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
    if upcoming.nasdaq is None:
        print(
            f"predict: Nasdaq has no consensus yet for {measure} on {upcoming.day}", file=sys.stderr
        )
        return 1
    if abs(upcoming.nasdaq - upcoming.tradingview) > gap + 1e-9:
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
                [m for m, _ in rule.combinations], upcoming.day, settings.cache_dir
            )
            if rule.alone
            else []
        )
    except sources.CalendarError as exc:
        print(f"predict: {exc}", file=sys.stderr)
        return 1
    surprise = round(actual - upcoming.nasdaq, 9)
    print(
        f"{measure} on {upcoming.day}: actual {actual:g}, {_source_label(expectations.NASDAQ_CONSENSUS)} "
        f"{upcoming.nasdaq:g}, surprise {surprise:+g}"
    )
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
    replayed = {
        instrument: [c for c in made if c.call.event_id != study.NEXT_RELEASE]
        for instrument, made in confident.items()
    }
    graded = _graded_confidence(replayed, rule)
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
        unit = study.MVP_PRICE_SERIES[instrument].unit
        band = (
            f"{_move_size(latest.band[0], unit, signed=True)} to "
            f"{_move_size(latest.band[1], unit, signed=True)}"
            if latest.band
            else "no band"
        )
        overall = study.overall_confidence([grades[instrument] for _, grades in graded])
        print(
            f"{instrument:<12} {call:<6} closes {call} today: {latest.probability:.0%} "
            f"({len(made) - 1} calls before), {band}; its confidence: {overall}"
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
        "probability = the link's record on its calls so far; band = where half its moves land; "
        f"confidence graded by `fortuneteller predict --event {flow.cli_name}`"
    )
    return _log_calls(calls, live, released)


def _now() -> datetime:
    return datetime.now(UTC)


def _log_calls(calls: Sequence[study.LoggedCall], live: bool, released: datetime) -> int:
    """Logs the calls only on the release's day, from its release time: any other run is a what-if
    and must not take the release's one entry in the log."""
    if not live:
        print(f"not logged: a release is logged on its day from {released:%H:%M} New York")
        return 0
    study.append_calls(settings.calls_path, calls)
    print(f"logged {len(calls)} rows to {settings.calls_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    # Each flow's short name on the command line, read when the parser is built.
    event_names = [flow.cli_name for flow in flows.EVENT_FLOWS]
    parser = argparse.ArgumentParser(prog="fortuneteller", description="FortuneTeller CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create the DuckDB file with all tables")
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
        "load-prices", help="load daily closes from Yahoo and measure each release's move"
    )
    p_prices.set_defaults(func=_load_prices)

    p_surprises = sub.add_parser(
        "load-surprises", help="load each event's surprise against every expected value"
    )
    p_surprises.set_defaults(func=_load_surprises)

    p_surprise = sub.add_parser(
        "surprise", help="does each instrument's release-day move follow the event's surprise?"
    )
    p_surprise.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    p_surprise.set_defaults(func=_surprise)

    p_raw = sub.add_parser(
        "raw-move", help="compare each instrument's moves on an event's days with ordinary days"
    )
    p_raw.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    p_raw.set_defaults(func=_raw_move)

    p_predict = sub.add_parser(
        "predict", help="replay every release, predicting each from the ones before it"
    )
    p_predict.add_argument(
        "--event", choices=event_names, default="cpi", help="the event (default: cpi)"
    )
    p_predict.add_argument(
        "--actual",
        type=float,
        help="the next release's actual (percent for CPI, thousands for payrolls): predict its "
        "day and log each link's line to data/calls.csv",
    )
    p_predict.set_defaults(func=_predict)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
