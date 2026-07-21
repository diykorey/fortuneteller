"""Command-line entry point for FortuneTeller.

Subcommands: ``init`` creates the store (M0-05 ``db.init_db``); ``seed`` / ``query-demo`` load and
read the seed data (M0-07 ``seed``); ``replay`` runs an episode through the deterministic core and
prints the resolved warnings (M0-R-03).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from . import db, seed
from .config import settings
from .replay import engine as replay_engine

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


def _replay(args: argparse.Namespace) -> int:
    con = db.get_connection()
    db.init_db(con=con)
    # replay is meaningless without the reference data, and the load is idempotent, so refresh the
    # store from the committed CSVs on every run — this keeps it in step with the seed even if the
    # schema or seed grew since the store was last written.
    seed.load_all(con=con)

    try:
        episode = replay_engine.load_episode(Path(args.episode))
        replay_engine.validate_keys(episode, con=con)
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1

    warnings = replay_engine.replay(episode, con=con)
    if args.json:
        sys.stdout.write(replay_engine.warnings_to_json(warnings))
    else:
        print(replay_engine.warnings_to_table(warnings))

    if episode.expect:
        by_symbol = {w.instrument: w.direction for w in warnings}
        mismatches = [
            (symbol, expected, by_symbol.get(symbol))
            for symbol, expected in episode.expect.items()
            if by_symbol.get(symbol) != expected
        ]
        if mismatches:
            for symbol, expected, actual in mismatches:
                print(
                    f"expect mismatch: {symbol} expected {expected} got {actual}", file=sys.stderr
                )
            return 1
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

    p_replay = sub.add_parser("replay", help="run an episode through the deterministic core")
    p_replay.add_argument("episode", help="path to an episodes/<id>.json file")
    p_replay.add_argument(
        "--json", action="store_true", help="emit structured JSON instead of a table"
    )
    p_replay.set_defaults(func=_replay)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
