"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``); ``load-releases`` loads the CPI release history from FRED
(MVP step 1 ``study``); ``load-prices`` loads the five instruments' daily closes and measures their
move around each release (MVP step 2).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from . import db, seed, study
from .config import settings

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


def _load_releases(_args: argparse.Namespace) -> int:
    api_key = settings.fred_api_key.get_secret_value() if settings.fred_api_key else ""
    if not api_key:
        print("load-releases: FT_FRED_API_KEY is not set (see docs/accounts.md)", file=sys.stderr)
        return 1
    try:
        payload = study.fetch_cpi_releases(api_key)
        releases, valueless = study.parse_cpi_releases(payload)
    except study.FredError as exc:
        print(f"load-releases: {exc}", file=sys.stderr)
        return 1
    if not releases:
        print("load-releases: FRED returned no CPI releases", file=sys.stderr)
        return 1
    con = db.get_connection()
    db.init_db(con=con)
    loaded = study.store_cpi_releases(releases, con=con)
    released = [release.released for release in releases]
    print(f"loaded {loaded} CPI releases, {min(released)} … {max(released)}")
    if valueless:
        months = ", ".join(month.strftime("%Y-%m") for month in valueless)
        print(f"skipped {len(valueless)} printed without a value: {months}")
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
            "load-prices: no CPI releases stored; run `fortuneteller load-releases` first",
            file=sys.stderr,
        )
        return 1
    try:
        study.load_daily_bars(con=con)
    except study.YahooError as exc:
        print(f"load-prices: {exc}", file=sys.stderr)
        return 1
    release_counts = study.store_observations(con=con)
    for instrument, counts in release_counts.items():
        print(describe_release_counts(instrument, counts))
    first = next(iter(release_counts.values()))
    releases = first.measured + first.skipped_before_history + first.skipped_no_close_nearby
    total = sum(counts.measured for counts in release_counts.values())
    print(f"{len(release_counts)} instruments × {releases} releases = {total} observations")
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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
