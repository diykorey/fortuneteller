# CLAUDE.md

## What this is

FortuneTeller — an event-driven market-impact prediction & warning system: ingest social / political
/ climate / macro events, predict which instruments move (direction + magnitude + horizon) with
**calibrated** confidence. A warning product, not HFT (latency budget is seconds-to-minutes). *Amended 2026-10-23:* an
entertainment tool with a realistic approach, not a financial one (`docs/legend.md`, the target):
the bars stay, the surface widens.

The repo holds M0 (the data spine), the MVP, ladder rungs 1–6 and roadmap steps 1–4b;
`docs/status.md` has the task in hand, and `uv run fortuneteller --help` what each command does.
**A call is made from the actual once it lands, never before it**, and a statement nobody scheduled
is never called before it happens.

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

The current set, each kept true or deleted:

- **`docs/legend.md`** — the target and the way; the template every step document follows.
- **`docs/roadmap.md`** — the MVP, the ladder and the numbered steps after it. **Build from this.**
- **`docs/status.md`**, **`docs/mvp-results.md`**, **`docs/steps/*.md`** — the task in hand, the
  findings in plain words, one spec per step.
- **`docs/schema.md`**, **`docs/precision.md`**, **`docs/extending.md`** — every column, every
  known shortcut and its trigger, how to add a flow or an expectation source.
- **`docs/glossary.md`** — every acronym and term. Add to it whenever you introduce one.

Everything under **`docs/legacy/`** is the pre-reset corpus: reference material, **not
instructions**. It documents a plan that was abandoned; where it and the roadmap disagree, the
roadmap wins. `docs/legacy/README.md` says what in there is still worth reading — including
`docs/legacy/data/`, which is still accurate about the seed CSVs the code loads.

## Scope discipline — the provable core

The core is measured: nine events × seven markets from free sources, three links that hold
walk-forward. Widening is planned in `docs/roadmap.md` steps 5–11 and goes one flow or one set of
markets per PR, each with a spec whose bars and expected outcome are written before anything is
measured and amended only with a date. Still deferred: unscheduled detection (rung 7, history
first) and paid data.

**Measure before predicting.** Every number comes from real data and is graded. A call carries its
record as counts and its band, never a probability, until one proves honest by rung 3's rule.
Emitting confident output from placeholder values is the specific failure the reset answered.

## Commands

Toolchain is `uv` (Python 3.12). `just` recipes wrap these; if `just` isn't installed, run the
`uv run` form directly.

```bash
uv sync                              # install deps + dev group (ruff, mypy, pytest)
just check                           # the full local gate = lint + typecheck + test (mirrors CI)
```

## Where things live

- **The plan:** `docs/roadmap.md` — the MVP, the ladder and the numbered steps after it. Work goes
  spec → one branch → one PR per step, `docs/status.md` updated in the same change. M0 shipped
  as tickets M0-01…09 (issues #2–#10, milestone closed); its ticket doc is now
  `docs/legacy/m0-tickets.md`. There is no ticket set for the MVP steps and none is needed yet.
- **The data spine:** Pydantic v2 models + a thin SQL helper over DuckDB — **no ORM**. Schema is plain
  SQL in `schema.sql` so the later Postgres migration stays cheap. **`docs/schema.md` describes every
  table, column and allowed column value; any change to `schema.sql`, or to what fills a column, updates it in the same
  change.** Reference tables are **config the
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
