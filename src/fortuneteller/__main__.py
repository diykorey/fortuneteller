"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``); ``load-releases`` loads the CPI release history from FRED
(MVP step 1 ``study``); ``load-prices`` loads the five instruments' daily closes and measures their
move around each release (MVP step 2); ``raw-move`` compares each instrument's moves on CPI days
with all other days (MVP step 3); ``load-surprises`` stores each release's CPI surprise and
``surprise`` measures how the moves follow it (MVP step 4).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from datetime import date

from . import db, seed, sources, study
from .config import settings
from .models import Surprise

Handler = Callable[[argparse.Namespace], int]
# The events a command can be pointed at, by their short name on the command line.
EVENTS = {"cpi": study.CPI_EVENT_TYPE, "nfp": study.NFP_EVENT_TYPE}


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


def _months(releases: Sequence[sources.FirstRelease] | Sequence[date]) -> str:
    months = [r if isinstance(r, date) else r.reference_month for r in releases]
    return ", ".join(month.strftime("%Y-%m") for month in months)


def _load_releases(_args: argparse.Namespace) -> int:
    api_key = _fred_key("load-releases")
    if not api_key:
        return 1
    parsed = {}
    try:
        for event_type, series_id in study.RELEASE_SERIES.items():
            payload = sources.fetch_first_releases(api_key, series_id=series_id)
            parsed[event_type] = sources.parse_first_releases(payload, series_id)
    except sources.FredError as exc:
        print(f"load-releases: {exc}", file=sys.stderr)
        return 1
    for event_type, (releases, _valueless) in parsed.items():
        if not releases:
            print(f"load-releases: FRED returned no {event_type} releases", file=sys.stderr)
            return 1
    con = db.get_connection()
    db.init_db(con=con)
    for event_type, (releases, valueless) in parsed.items():
        kept, carried = study.one_release_per_day(releases)
        loaded = study.store_releases(event_type, kept, con=con)
        label = event_type.split(" /")[0]
        released = [release.released for release in kept]
        print(f"loaded {loaded} {label} releases, {min(released)} … {max(released)}")
        if valueless:
            print(f"  skipped {len(valueless)} printed without a value: {_months(valueless)}")
        if carried:
            print(f"  {len(carried)} first published with a later month: {_months(carried)}")
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
    for event_type, by_instrument in release_counts.items():
        print(event_type)
        for instrument, counts in by_instrument.items():
            print(describe_release_counts(instrument, counts))
        first = next(iter(by_instrument.values()))
        releases = first.measured + first.skipped_before_history + first.skipped_no_close_nearby
        total = sum(counts.measured for counts in by_instrument.values())
        print(f"{len(by_instrument)} instruments × {releases} releases = {total} observations")
    return 0


def describe_surprises(rows: Sequence[Surprise]) -> list[str]:
    """One report line per measure and expected value: how many surprises, over which months."""
    lines = []
    for measure in study.MEASURE_SERIES:
        for baseline in (study.TREND_12M, study.NOWCAST_BASELINE):
            ids = sorted(
                r.event_id for r in rows if r.measure == measure and r.baseline == baseline
            )
            if ids:
                first, last = (study.event_date(i) for i in (ids[0], ids[-1]))
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
        rows = study.load_surprises(api_key, con=con)
    except (sources.FredError, sources.ClevelandError, ValueError) as exc:
        print(f"load-surprises: {exc}", file=sys.stderr)
        return 1
    for line in describe_surprises(rows):
        print(line)
    return 0


def _direction(sign: int) -> str:
    return {1: "up", -1: "down"}.get(sign, "either")


def _hit_rate(tracking: study.SurpriseTracking) -> str:
    if tracking.hit_rate is None:
        return "—"
    return f"{tracking.hit_rate:.0%} ({tracking.hit_n})"


def describe_surprise_tracking(
    results: dict[tuple[str, str], dict[str, study.SurpriseTracking]],
) -> list[str]:
    """The report: the verdict table (core against the trend), the context table, and the rule."""
    lines = [
        "core against the 12-month trend",
        "instrument   n    expected  rank corr  p       hit rate (n)  per 0.1pp  verdict",
    ]
    for instrument, t in results.get(study.VERDICT_COMBINATION, {}).items():
        unit = study.MVP_PRICE_SERIES[instrument].unit
        lines.append(
            f"{instrument:<12} {t.n:<4} {_direction(study.EXPECTED_SIGN[instrument]):<9} "
            f"{t.rank_corr:<10.2f} {t.p:<7.4f} {_hit_rate(t):<13} "
            f"{_move_size(t.slope, unit):<10} {t.verdict}"
        )
    lines += [
        "",
        "context, no verdict",
        "instrument   measure   baseline   n    rank corr  p       hit rate (n)",
    ]
    for (measure, baseline), by_instrument in results.items():
        if (measure, baseline) == study.VERDICT_COMBINATION:
            continue
        for instrument, t in by_instrument.items():
            lines.append(
                f"{instrument:<12} {measure:<9} {baseline:<10} {t.n:<4} "
                f"{t.rank_corr:<10.2f} {t.p:<7.4f} {_hit_rate(t)}"
            )
    lines += [
        "",
        f"{study.TRACKS} = corr as expected, p < {study.TRACK_P_BAR}, hit rate >= "
        f"{study.HIT_RATE_BAR:.0%}; {study.UNCLEAR} = one of the two; "
        f"{study.DOESNT_TRACK} = neither",
    ]
    return [line.rstrip() for line in lines]


def _surprise(_args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    for table, command in (
        ("event_instances", "load-releases"),
        ("observations", "load-prices"),
        ("surprises", "load-surprises"),
    ):
        if db.count_rows(table, con=con) == 0:
            print(
                f"surprise: no {table} stored; run `fortuneteller {command}` first", file=sys.stderr
            )
            return 1
    for line in describe_surprise_tracking(study.track_surprises(con=con)):
        print(line)
    return 0


def _move_size(value: float, unit: str) -> str:
    return f"{value:.1f} bp" if unit == "bps" else f"{value * 100:.2f}%"


def describe_raw_moves(results: dict[str, study.RawMove], label: str = "CPI") -> list[str]:
    """The report: a verdict line per instrument, an era line per instrument, and the rule.

    ``label`` names the event in the headers: a three-letter name keeps the columns aligned.
    """
    lines = [f"instrument   {label} days  median {label}  median other  ratio  p       verdict"]
    for instrument, raw in results.items():
        c = raw.overall
        lines.append(
            f"{instrument:<12} {c.event_days:>8}  {_move_size(c.median_cpi, raw.unit):>10}  "
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
        f"{study.UNCLEAR} = one of the two; {study.DOESNT_MOVE} = neither",
    ]
    return [line.rstrip() for line in lines]


def _raw_move(args: argparse.Namespace) -> int:
    event_type = EVENTS[args.event]
    con = db.get_connection()
    db.init_db(con=con)
    if not study.stored_events(event_type, con=con):
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
        results = study.measure_raw_moves(con=con, event_type=event_type)
    except ValueError as exc:
        print(f"raw-move: {exc}", file=sys.stderr)
        return 1
    for line in describe_raw_moves(results, label=args.event.upper()):
        print(line)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fortuneteller", description="FortuneTeller CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create the DuckDB file with all tables")
    p_init.set_defaults(func=_init)

    p_seed = sub.add_parser("seed", help="load the seed CSVs into the store")
    p_seed.set_defaults(func=_seed)

    p_demo = sub.add_parser("query-demo", help="print a sample effect-size lookup row")
    p_demo.set_defaults(func=_query_demo)

    p_releases = sub.add_parser("load-releases", help="load the CPI release history from FRED")
    p_releases.set_defaults(func=_load_releases)

    p_prices = sub.add_parser(
        "load-prices", help="load daily closes from Yahoo and measure each release's move"
    )
    p_prices.set_defaults(func=_load_prices)

    p_surprises = sub.add_parser(
        "load-surprises", help="load each CPI release's surprise against both expected values"
    )
    p_surprises.set_defaults(func=_load_surprises)

    p_surprise = sub.add_parser(
        "surprise", help="does each instrument's release-day move follow the CPI surprise?"
    )
    p_surprise.set_defaults(func=_surprise)

    p_raw = sub.add_parser(
        "raw-move", help="compare each instrument's moves on an event's days with all other days"
    )
    p_raw.add_argument("--event", choices=EVENTS, default="cpi", help="the event (default: cpi)")
    p_raw.set_defaults(func=_raw_move)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
