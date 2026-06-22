# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FortuneTeller — an event-driven market-impact prediction & warning system: ingest social / political
/ climate / macro events, predict which instruments move (direction + magnitude + horizon) with
**calibrated** confidence. A warning product, not HFT (latency budget is seconds-to-minutes).

The repo is **bootstrapping**: it currently holds the design docs (mirrored from a Notion workspace),
seed reference data, and the M0-01 project skeleton. Most runtime code is specified but not yet built
— follow the tickets.

## Two architectures — read this first

There are deliberately two architecture docs, and they disagree on purpose:

- **`docs/mvp-architecture.md` is the canonical "build now" picture** — Python-first, single process,
  embedded DuckDB, scripts-before-services. **Build from this.**
- **`docs/architecture.md` is the north-star** — the eventual Java/Kafka/Flink production spine. **Do
  NOT scaffold from it.** When the two conflict, MVP wins until a documented graduation trigger fires.

At the MVP stage the pipeline is a **deterministic chain of pure functions over local data**, not a
distributed system: the 10 stages in the north-star map to functions in one process; the "event bus"
is a list; the store is one DuckDB file + committed seed CSVs.

## Scope discipline — the provable core

The MVP calibrates exactly one slice before widening anything: **scheduled-macro events (CPI / NFP /
Fed) × ~5 liquid instruments** (SPY/ES, a rates benchmark, DXY, Gold, VIX), on recorded fixtures then
a free data stack (FRED + a free econ calendar + yfinance/Stooq). The full 31-event taxonomy, 55
instruments, 132 platforms, unscheduled detection, and paid/tick data are **post-proof** — every data
table says so. Do not implement against the full breadth until the core is proven.

## Commands

Toolchain is `uv` (Python 3.12). `just` recipes wrap these; if `just` isn't installed, run the
`uv run` form directly.

```bash
uv sync                              # install deps + dev group (ruff, mypy, pytest)
uv run fortuneteller --help          # CLI: init | seed | query-demo (handlers stubbed until M0-05/07)
uv run ruff check                    # lint (line length 100)
uv run ruff format                   # format
uv run mypy src                      # type check (strict)
uv run pytest                        # tests
uv run pytest tests/test_skeleton.py::test_version   # a single test
uv run pytest -k version             # tests matching a keyword
just check                           # the full local gate = lint + typecheck + test (mirrors CI)
```

CI (`.github/workflows/ci.yml`) runs ruff + mypy + pytest on every push, but **skips cleanly until
`pyproject.toml` exists** (it's guarded), then enforces automatically.

## Where things live

- **Roadmap & tickets:** `docs/roadmap.md` (M0–M7); `docs/m0-tickets.md` (M0-01…M0-09, the scaffold);
  `docs/m0-r-tickets.md` (M0-R-01…05, the replay harness). Tickets are written to be executed in
  isolation — file paths + binary acceptance criteria. GitHub mirrors these as milestones M0–M7 and
  M0 issues (#2–#10, label `M0`).
- **The data spine:** Pydantic v2 models + a thin SQL helper over DuckDB — **no ORM**. Schema is plain
  SQL in `schema.sql` so the later Postgres migration stays cheap. Reference tables are **config the
  pipeline reads**, committed as seed CSVs in `data/seed/` (and documented in `docs/data/`).
- **The fast-dev loop (replay harness):** the spine of iteration. A fixture (`fixtures/*.json`)
  carries a pre-detected event; `replay()` runs the deterministic core (stages 5–8: surprise →
  effect-size lookup → `Warning`) and golden files assert the output byte-for-byte. It is **offline
  and deterministic** — `as_of` comes from the fixture `t0`, never `now()`; no randomness. Iterate
  logic against fixtures instead of waiting for live data. Detection (stages 1–4) is out of scope
  until M4. Design: `docs/superpowers/specs/2026-06-22-replay-harness-fast-dev-loop-design.md`.

## Conventions & gotchas

- **Canonical keys are load-bearing.** `event_type` strings and instrument **symbols** must match
  `data/seed/event_types.csv` and `data/seed/instruments.csv` exactly (e.g. `CPI / inflation surprise`,
  `SPY / ES`). Naming drift silently breaks joins, fixtures, and the `query-demo` lookup.
- **Enum casing:** the M0-03 models / seed CSVs use lowercase enum values (`positive`, `both`, `up`,
  `conditional`, `equity_index`); `docs/calibration-dataset.md`'s DDL uses capitalized (`Positive`,
  `Up`). Reconcile to one casing when implementing M2.
- **Conditional direction is deferred to M1.** At M0-R, `conditional` cells emit
  `direction="conditional"` + a `surprise_sign`; turning that into a concrete up/down is M1's job.
- **Seed data is not ground truth.** Reference data is partial (Notion read-only export limits):
  `event_types`/`news_sources` are full, `instruments`/`countries` are representative subsets, and
  **`effect_size_seed` values are illustrative placeholders, not authoritative**; event tiers are
  inferred. Each table states its completeness; the full tables live in Notion.
- **Classifier:** start with the single unified prompt in
  `docs/event-polarity-and-classifier-prompts.md`; the three-way split there is a deferred option.
- Tests use the `# given` / `# when` / `# then` comment structure.
