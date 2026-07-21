# FortuneTeller task runner — the canonical command surface.
# Requires `just` (https://just.systems) and `uv`. Recipes assume the M0 scaffold
# (pyproject.toml + src/fortuneteller) exists; see docs/m0-tickets.md.

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

# auto-format
fmt:
    uv run ruff format

# static type check
typecheck:
    uv run mypy src

# the full local gate (mirrors CI): lint + types + tests
check: lint typecheck test

# create the DuckDB file with all tables
init:
    uv run fortuneteller init

# load the seed CSVs into the store
seed:
    uv run fortuneteller seed

# replay an episode through the deterministic core (default: the war-shock episode)
replay episode="episodes/war-oil-shock-2026.json":
    uv run fortuneteller replay {{episode}} --json
