"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``).
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

from . import db, seed
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fortuneteller", description="FortuneTeller CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create the DuckDB file with all tables")
    p_init.set_defaults(func=_init)

    p_seed = sub.add_parser("seed", help="load the seed CSVs into the store")
    p_seed.set_defaults(func=_seed)

    p_demo = sub.add_parser("query-demo", help="print a sample effect-size lookup row")
    p_demo.set_defaults(func=_query_demo)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
