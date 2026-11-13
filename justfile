# FortuneTeller task runner — the canonical command surface.
# Requires `just` (https://just.systems) and `uv`. New here? Start at docs/README.md.
# `uv run fortuneteller --help` lists every command; the recipes below wrap the common ones.

# list available recipes
default:
    @just --list

# create the venv and install deps (incl. the dev group)
setup:
    uv sync

# run the test suite
test:
    uv run pytest

# lint
lint:
    uv run ruff check

# check formatting without changing files
fmt-check:
    uv run ruff format --check

# auto-format
fmt:
    uv run ruff format

# static type check
typecheck:
    uv run mypy src

# the full local gate (mirrors CI): lint + types + tests
check: lint fmt-check typecheck test

# create the DuckDB file with all tables
init:
    uv run fortuneteller init

# load the seed CSVs into the store
seed:
    uv run fortuneteller seed

# load every event's history from FRED, the Fed and TradingView (needs FT_FRED_API_KEY)
load-releases:
    uv run fortuneteller load-releases

# load daily closes from Yahoo and FRED and measure each release's move (after load-releases)
load-prices:
    uv run fortuneteller load-prices

# load each release's surprise against every expected value (after load-releases)
load-surprises:
    uv run fortuneteller load-surprises

# compare each instrument's moves on CPI days with ordinary days; any event: uv run fortuneteller raw-move --event NAME (after load-prices)
raw-move:
    uv run fortuneteller raw-move

# does each instrument's release-day move follow CPI's surprise? any event: uv run fortuneteller surprise --event NAME (after load-surprises)
surprise:
    uv run fortuneteller surprise
