"""Command-line entry point for FortuneTeller.

Subcommands are wired here; their implementations land in later M0 tickets
(``init`` -> M0-05 ``db.init_db``; ``seed`` / ``query-demo`` -> M0-07 ``seed``).
For the M0-01 skeleton the handlers are placeholders.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

Handler = Callable[[argparse.Namespace], int]


def _init(_args: argparse.Namespace) -> int:
    print("init: not implemented yet (wired in M0-05 — db.init_db)")
    return 0


def _seed(_args: argparse.Namespace) -> int:
    print("seed: not implemented yet (wired in M0-07 — seed.load_all)")
    return 0


def _query_demo(_args: argparse.Namespace) -> int:
    print("query-demo: not implemented yet (wired in M0-07 — seed.query_demo)")
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
