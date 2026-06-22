# MVP Architecture — what we build now

> **This is the canonical "build now" picture (M0–M3).** The Java / Spring / Kafka / Flink spine in
> [architecture.md](architecture.md) is the **north-star** — the eventual production shape, *not*
> what we scaffold first. When the two seem to disagree, **this document wins** until a
> [graduation trigger](#graduation-triggers) fires.

## The one decision

**Python-first, single process, DuckDB, fixture-driven.** No broker, no services, no containers, no
ORM, no web server — until a concrete trigger demands one. This is the fastest thing to build and
iterate on, and it maps 1:1 onto the north-star so nothing is wasted.

## Provable core (the scope discipline that keeps this fast)

The MVP calibrates exactly **one slice** end to end before widening anything:

- **Events:** scheduled macro only — **CPI, NFP, Fed decision** (optionally GDP/PMI later). These
  have published consensus → `surprise_sd` is computable, and they release often enough to reach
  n≥8 quickly. Clean to validate.
- **Instruments (~5):** **SPY / ES, a rates benchmark (UST 10Y or BUND/FGBL), DXY, Gold, VIX** —
  liquid, with free price data.
- **Everything else is post-proof reference, not build scope:** the other ~28 event types, the
  other ~50 instruments, the 132 platforms, and all unscheduled/detection work. The full tables in
  [`data/`](data/README.md) exist for *later* — do not implement against their breadth.
- **Done =** those core cells show calibrated `mag_per_sd` / `hit_rate` / `n_obs` and either beat
  the market-implied benchmark or honestly report that they don't.

Why this slice: it makes the data problem (below) trivial, and it's the only part that can actually
be *proven* with a few hundred observations. Breadth before proof is how a pet project stalls.

## The core idea

The pipeline is a **deterministic chain of pure functions over local data**, not a distributed
system. The north-star's 10 stages become functions in one process:

| North-star (architecture.md) | MVP reality |
| --- | --- |
| Kafka event bus / replay log | a Python list + the `fixtures/` directory |
| Stage = a streaming service | stage = a pure function in `src/fortuneteller/` |
| Postgres + Timescale + Redis | one DuckDB file + committed seed CSVs |
| Flink/Kafka Streams corroboration | (deferred to M4) plain functions over a window |
| Airflow/Dagster batch | a CLI subcommand, later APScheduler |
| Delivery service (push/email/WS) | `print` / file, then FastAPI only at M6 |

```
fixture / event  ->  surprise()  ->  predict()  ->  calibrate()  ->  warn()
                     (stage 5)       (stage 6)       (stage 7)       (stage 8)
                          \______ pure functions, one process ______/
                                   data: DuckDB + fixtures (local, committed)
```

The deterministic middle (stages 5–8) is the [replay harness](superpowers/specs/2026-06-22-replay-harness-fast-dev-loop-design.md):
`replay(fixture) -> list[Warning]`. Detection (stages 1–4) is added as ordinary functions/modules
at M4 — it does not exist in the MVP.

## Stack (M0–M3)

- **Language/runtime:** Python 3.12, one process. `uv` for env/deps/run.
- **Store:** DuckDB single file + Polars for CSV/Parquet IO. Schema in `schema.sql`. No ORM —
  Pydantic models + a thin SQL helper.
- **Data:** committed seed CSVs (`data/seed/`) + JSON `fixtures/`. Zero credentials to boot.
- **LLM classify (M1+):** one Anthropic API call behind `instructor` → validated Pydantic JSON.
  Use the **single unified** classifier prompt, not the three split prompts, until precision forces
  a split.
- **Modeling (M2–M3):** statsmodels / scikit-learn / MAPIE, in-process batch functions invoked by a
  CLI subcommand (then APScheduler).
- **Surface:** one CLI — `fortuneteller {init, seed, replay, predict, calibrate, backtest}`. Each
  subcommand is a thin wrapper over a pure function.
- **Quality gate:** ruff + mypy + pytest, run via the task runner and in CI from day one.

## Data acquisition — the real bottleneck (not the code)

What stalls a project like this is *getting data*, not writing the pipeline. The provable core is
chosen precisely so its data is cheap and free:

1. **Fixtures first.** A handful of recorded past releases (the replay harness) prove the mechanics
   with **zero live data and zero credentials**.
2. **Free backfill for the core only.** Consensus/actuals from **FRED** + a free econ calendar
   (Trading Economics free tier / Investing.com); daily and 1-minute bars from **yfinance / Stooq /
   Tiingo free tier**. ~5 instruments × a few years × scheduled releases ≈ a few hundred
   observations — enough for n≥8 on the core cells, with **no paid vendor**.
3. **Deferred until post-proof:** tick data and paid vendors (Polygon / Databento), on-chain /
   GDELT / X feeds. Daily / 1-minute bars are enough to prove the loop; intraday tick precision is
   justified only after breadth is.

This is a binding decision so M2 does not stall on a "which vendor?" debate.

## What we deliberately do NOT build yet

Kafka/Flink/Bytewax, Postgres/Timescale/Redis, Docker, a web service, live feed ingestion, the
three-way prompt split, the full 31×55 matrix, the 132-platform breadth. Each has a named trigger
below; none has fired.

## Graduation triggers

Build the heavier piece only when its trigger fires (from [tech-stack.md](tech-stack.md) /
[roadmap.md](roadmap.md)):

| Move | Trigger | Milestone |
| --- | --- | --- |
| DuckDB → Postgres + SQLModel | concurrent writers or a live serving API | ~M6 |
| Scripts → FastAPI service | something external must call it | M6 |
| Polling → streaming bus (Kafka/Bytewax) | feed volume outgrows async polling | M7 (maybe never) |
| Single process → the north-star spine | all of the above have fired | post-M6 |

## Why this is the fastest path

1. The hard work is statistics — Python-native, terse, readable; Java would mean reimplementing math.
2. Seconds-to-minutes latency budget → a single process is more than enough; streaming buys unused throughput.
3. The replay harness gives an instant, deterministic, offline feedback loop, so iteration cost ≈ a function call.
4. Schema-in-SQL + Pydantic shapes keep every later swap (Postgres, FastAPI, Kafka) contained, not a rewrite.
