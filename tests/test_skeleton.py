"""Skeleton smoke tests for M0-01 (the real DB smoke tests are M0-08)."""

from pathlib import Path

import pytest

from fortuneteller import __version__
from fortuneteller.__main__ import build_parser, main


def test_version() -> None:
    # given the installed package
    # when reading its version
    # then it is set
    assert __version__


def test_subcommands_run(tmp_db: Path) -> None:
    # given the skeleton CLI pointed at a throwaway store, never data/fortuneteller.duckdb
    for cmd in ("init", "seed", "query-demo"):
        # when the subcommand runs
        rc = main([cmd])
        # then it exits 0
        assert rc == 0


def test_no_subcommand_errors() -> None:
    # given the parser
    parser = build_parser()
    # when parsing with no subcommand
    # then argparse exits (subcommand is required)
    with pytest.raises(SystemExit):
        parser.parse_args([])
