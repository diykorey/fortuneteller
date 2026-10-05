# FortuneTeller task runner — the canonical command surface.
# Requires `just` (https://just.systems) and `uv`. Recipes assume the M0 scaffold
# (pyproject.toml + src/fortuneteller) exists; see docs/legacy/m0-tickets.md.

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

# load the CPI release history from FRED (needs FT_FRED_API_KEY)
load-releases:
    uv run fortuneteller load-releases

# load daily closes from Yahoo and measure each release's move (after load-releases)
load-prices:
    uv run fortuneteller load-prices

# compare each instrument's moves on CPI days with all other days (after load-prices)
raw-move:
    uv run fortuneteller raw-move
