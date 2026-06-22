# Tech Stack & Reasoning

Technology decisions for building FortuneTeller, optimized for **fast iterative development** and
**readability**.

## TL;DR decisions

- **Language:** Python-first (a JVM/Go service only for high-throughput ingestion later, if ever).
- **Store:** DuckDB + Parquet (embedded, analytical) — not SQLite, not Postgres yet.
- **Persistence:** no ORM at M0 — Pydantic models + a thin SQL helper, schema in schema.sql.
- **Footprint:** ~8 runtime deps; scripts before services; no Docker / Kafka / web server until a
  milestone needs it.

## Why Python-first

- The hard part of this system is **statistics** (event-study abnormal returns, standardized
  surprise, Platt/isotonic/conformal calibration, partial pooling). That toolkit is Python-native:
  statsmodels, scikit-learn, MAPIE, numpy/scipy. In Python it's a few readable lines; in Java it's
  reimplementing math or wrestling bridges.
- The **latency budget is seconds-to-minutes** (a warning product, not HFT), so Python runtime
  speed is a non-issue.
- Fastest and most readable for the half you iterate on most (surprise, prediction, calibration,
  glue, LLM calls).
- A JVM (Kotlin) or Go service is reserved for the **streaming ingestion spine only if throughput
  demands it** — most builds never hit that, so it stays out of the MVP.

## Core stack

| Concern | Pick | Used from | Why |
| --- | --- | --- | --- |
| Language | Python 3.12+ | M0 | modern typing, lib-compatible |
| Env / deps / build | uv | M0 | one fast tool for venv+deps+lock+run |
| Lint + format | Ruff | M0 | single fast tool (replaces black+isort+flake8) |
| Type checking | mypy | M0 | keeps the Pydantic guarantees real |
| Tests | pytest (+cov) | M0 | the 'tests pass' exit criterion |
| Config | pydantic-settings | M0 | typed config from env/.env |
| Domain models | Pydantic v2 | M0 | validated Event / Observation / Prediction objects |
| DataFrames + Parquet I/O | Polars | M0 | fast + readable; reads/writes Parquet directly |
| Store | DuckDB | M0 | embedded columnar SQL; single file, zero server |
| Persistence layer | thin SQL helper (schema.sql) | M0 | typed access without ORM overhead |
| Seed data | committed CSV/Parquet in data/seed | M0 | clones-and-runs offline, no credentials at boot |
| Task runner | just | M0 | one entry point for setup/test/lint/typecheck/replay/seed |
| CI (day one) | GitHub Actions | M0 | ruff + mypy + pytest on every push |
| LLM classifier | Anthropic SDK + instructor | M1+ | prompts → validated Pydantic JSON |
| Modeling / calibration | statsmodels, scikit-learn, MAPIE, scipy | M2-M3 | event-study + probability/conformal calibration |

## Database: DuckDB (keep it)

- The core workload is **analytical** — event-study `GROUP BY`s, window functions, aggregations
  over the observations table. DuckDB does these natively and fast.
- **SQLite would be a downgrade**: it's row-oriented OLTP; it makes the analytical part slower to
  write and run. It only wins with many concurrent writers — which doesn't happen until a live
  service (M6).
- **Postgres now = infra tax**: a server to run, migrations to manage, a pool — friction with no
  payoff at prototype stage. Its moment is M6 (concurrent writes + live serving), and DuckDB →
  Postgres is a cheap migration if schema stays in plain SQL.
- DuckDB reads Parquet/CSV directly, runs in-process, and is a single file.

## ORM: none at M0 (Pydantic + thin SQL helper)

- Pydantic models are the typed domain objects; small functions like `insert(obs)` and
  `get_effect_size(event, instrument)` hold the SQL in one place (schema.sql) and return validated
  objects.
- This gives type safety + readability **without** SQLAlchemy's mapping layer, session management,
  or a duckdb-engine dependency — the fastest to write and read now.
- **When a real ORM would help:** lots of repetitive CRUD + a desire for managed migrations. Then
  the fast-dev pick is **SQLModel** (Pydantic + SQLAlchemy in one model class), paired with Postgres
  — because duckdb-engine is less battle-tested than Postgres's SQLAlchemy support.

## Deferred (don't install until the milestone needs it)

httpx / feed clients → M1; statsmodels / scikit-learn / MAPIE → M2-M3; APScheduler → M2;
datasketch / sentence-transformers (dedup, embeddings) → M4; FastAPI → M6; Postgres + SQLModel +
Redis → M6; Kafka / Bytewax (streaming) → M7; Docker → deploy time. Pulling any of these into M0 is
the main way 'lightweight' slips.

## Graduation triggers (stay lightweight until these fire)

| Move | Trigger | Milestone |
| --- | --- | --- |
| DuckDB → Postgres + SQLModel | concurrent writers or a live serving API | ~M6 |
| Scripts → FastAPI service | something external must call it | M6 |
| Polling → streaming bus (Kafka/Bytewax) | feed volume outgrows async polling | M7 (maybe never) |

## Guiding principle

Don't pay for Postgres / ORM / streaming machinery before the concurrency or migration need is
real. A thin typed layer over DuckDB is both the fastest to develop on now and a clean on-ramp to
the heavier stack later — and the schema-in-SQL + Pydantic shapes keep every later swap contained
rather than a rewrite.
