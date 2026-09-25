# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FortuneTeller — an event-driven market-impact prediction & warning system: ingest social / political
/ climate / macro events, predict which instruments move (direction + magnitude + horizon) with
**calibrated** confidence. A warning product, not HFT (latency budget is seconds-to-minutes).

The repo is **bootstrapping**. What exists today is M0 — the data spine — plus MVP step 1: the
design docs (mirrored from a Notion workspace), the seed reference data, a working
`init | seed | query-demo` CLI over DuckDB (M0-01…09; ruff + mypy --strict + pytest green), and
`load-releases`, which loads the real CPI release history from FRED into `event_instances`
(`src/fortuneteller/study.py`). **No prediction code exists**: no surprise computation, no direction
resolution, no warnings.

## The 2026-08-05 reset — read before planning any work

`main` was deliberately reset to `15ed679` on **2026-08-05**, discarding a built M0-R replay harness
and M1 offline prediction core. **Reason: it was over-engineered for the stage.** The discarded work
is preserved in the `origin/main_05082026` branch (41 commits) — read it for reference, but do not
restore it without asking.

GitHub issues #24–30 and #55–62, and the M1/M2 milestones, describe that pre-reset line of work.
**The board is stale** — it claims work that is not on this branch — and stays that way until a new
plan lands.

Three rules follow from the reset. They are checkable, so check them:

1. **No new package until a second caller needs it.** A change may not add an `__init__.py`; until
   two call sites exist, it is a function in a file that already exists.
2. **No indirection for a single case.** No mapping CSV, registry, or resolver layer until there are
   two concrete cases to resolve between.
3. **A plan doc must be shorter than the code it specifies.** If a step needs 600 lines of ticket,
   the step is too big — split it.

## Where we are

**`docs/status.md`** holds the last completed task, the one in progress, and the next one. Answer
"where are we / what's next" from it. When starting a task, move it to *In progress* and add the
task expected after it as the new *Next*; when finishing one, record it in the same change.

## The documents

Only two are current, both rewritten on 2026-09-11:

- **`docs/roadmap.md`** — the MVP and the feature ladder after it. **Build from this.**
- **`docs/glossary.md`** — every acronym and term. Add to it whenever you introduce one.

Everything under **`docs/legacy/`** is the pre-reset corpus: reference material, **not
instructions**. It documents a plan that was abandoned; where it and the roadmap disagree, the
roadmap wins. `docs/legacy/README.md` says what in there is still worth reading — including
`docs/legacy/data/`, which is still accurate about the seed CSVs the code loads.

## Scope discipline — the provable core

The MVP measures exactly one slice before widening anything: **CPI × 5 liquid instruments** (SPY,
UST 10Y, DXY, Gold, VIX) over real history, from free sources (FRED + yfinance/Stooq). The full
31-event taxonomy, 55 instruments, 132 platforms, unscheduled detection, and paid/tick data are
**post-proof**. Do not implement against the full breadth until the core is measured.

**Measure before predicting.** The MVP produces measured numbers, not warnings — emitting confident
output derived from placeholder seed values is the specific failure the reset was a response to.

## Commands

Toolchain is `uv` (Python 3.12). `just` recipes wrap these; if `just` isn't installed, run the
`uv run` form directly.

```bash
uv sync                              # install deps + dev group (ruff, mypy, pytest)
uv run fortuneteller --help          # CLI: init | seed | query-demo | load-releases
uv run ruff check                    # lint (line length 100)
uv run ruff format                   # format
uv run mypy src                      # type check (strict)
uv run pytest                        # tests
uv run pytest tests/test_skeleton.py::test_version   # a single test
uv run pytest -k version             # tests matching a keyword
just check                           # the full local gate = lint + typecheck + test (mirrors CI)
```

CI (`.github/workflows/ci.yml`) runs ruff + mypy + pytest on every push and pull request,
unconditionally — the old docs-only guard was dropped in M0-09.

## Where things live

- **The plan:** `docs/roadmap.md` — the MVP (four steps) and the feature ladder after it. M0 shipped
  as tickets M0-01…09 (issues #2–#10, milestone closed); its ticket doc is now
  `docs/legacy/m0-tickets.md`. There is no ticket set for the MVP steps and none is needed yet.
- **The data spine:** Pydantic v2 models + a thin SQL helper over DuckDB — **no ORM**. Schema is plain
  SQL in `schema.sql` so the later Postgres migration stays cheap. Reference tables are **config the
  pipeline reads**, committed as seed CSVs in `data/seed/` (documented in `docs/legacy/data/`).

## Conventions & gotchas

- **Canonical keys are load-bearing.** `event_type` strings and instrument **symbols** must match
  `data/seed/event_types.csv` and `data/seed/instruments.csv` exactly (e.g. `CPI / inflation surprise`,
  `SPY / ES`). Naming drift silently breaks joins and the `query-demo` lookup.
- **Enum casing:** the M0-03 models / seed CSVs use lowercase enum values (`positive`, `both`, `up`,
  `conditional`, `equity_index`); the DDL in `docs/legacy/calibration-dataset.md` uses capitalized
  (`Positive`, `Up`). Reconcile to one casing if that spec's SQL is ever adopted.
- **`conditional` cells are unresolved by design.** Many `effect_size_seed` rows carry
  `direction=conditional` — the move depends on the surprise sign and the regime. Turning those into
  a concrete up/down is future work; nothing in the repo does it today.
- **Seed data is not ground truth.** Reference data is partial (Notion read-only export limits):
  `event_types`/`news_sources` are full, `instruments`/`countries` are representative subsets, and
  **`effect_size_seed` values are illustrative placeholders, not authoritative**; event tiers are
  inferred. Each table states its completeness; the full tables live in Notion.
- **Classifier:** far future (feature-ladder rung 7). When it arrives, start with the single unified
  prompt in `docs/legacy/event-polarity-and-classifier-prompts.md`, not the three-way split.
- Tests use the `# given` / `# when` / `# then` comment structure.
