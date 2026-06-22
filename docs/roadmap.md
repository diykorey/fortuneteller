# Roadmap — Prototype to Complete Solution

Milestones sequenced so each one ships something working and de-risks the next. The arc in one
line: ship the slice → make it honest → make it broad → make it a product → operate it.

> **Provable core first (scope discipline).** M1–M3 calibrate exactly one slice: **scheduled-macro
> events (CPI / NFP / Fed) × ~5 liquid instruments (SPY/ES, UST 10Y or Bund, DXY, Gold, VIX)**, on
> recorded fixtures then **free** data (FRED + a free econ calendar + yfinance/Stooq). The full
> 31×55 matrix, 132 platforms, unscheduled detection, and paid/tick data are **post-proof** — widen
> only after the core beats (or honestly fails to beat) the benchmark. See
> [mvp-architecture.md](mvp-architecture.md).

## M0 — Scaffold & seed (S)

**Goal:** a repo you can clone and run, with the data spine in place.

**Build:** lightweight layout (uv, Ruff, pytest); Pydantic models for Event/Observation/Prediction
from the data dictionary; DuckDB + Parquet store; load the Notion reference tables (events,
instruments, effect-size seeds, news sources) into local tables.

**Done when:** `uv run` boots, the seed effect-size matrix and instruments are queryable in DuckDB,
tests pass.

> Implementation tickets for this milestone: [M0 Tickets — Scaffold & Seed](m0-tickets.md).

## M1 — Prototype: the thin vertical slice (S-M)

**Goal:** one event type produces one warning, end to end.

**Build:** replay a **recorded CPI fixture** through the slice — compute surprise and surprise_sd →
look up the seed effect-size for the **~5 core instruments** → emit a warning to console/file. Then
wire a free live path (FRED + a free econ calendar) behind the same function. No detection, no real
calibration yet (uses seed priors).

**Done when:** replaying the CPI fixture produces the asserted warning, **deterministically**. A
*real* CPI release reproducing it is an optional live-validation, not the dev gate. This is the
demoable prototype.

## M2 — Historical dataset + event-study calibration (M)

**Goal:** replace seed guesses with measured numbers for scheduled events.

**Build:** backfill scheduled-macro events (CPI/NFP/Fed/PMI/GDP) into the calibration dataset;
compute abnormal returns, CAR, half-life; run the calibration SQL to overwrite seed
magnitudes/hit-rates; close the feedback loop (outcome capture → recalibrate). Data comes from the
**free stack** (FRED + a free econ calendar + yfinance/Stooq); paid/tick vendors stay deferred — see
[mvp-architecture.md](mvp-architecture.md).

**Done when:** the effect-size matrix shows calibrated mag_per_sd, hit_rate, n_obs for
scheduled-macro cells, and the loop re-runs on a schedule (APScheduler).

## M3 — Confidence calibration + backtest gate (M)

**Goal:** make "70%" actually mean 70%, and don't ship cells that aren't ready.

**Build:** directional probability calibration (Platt/isotonic, per regime bucket); conformal
magnitude bands (MAPIE); benchmark each prediction vs options-implied move + prediction-market
odds; a backtest harness (Brier, ECE, reliability diagram, coverage, skill score) and the gate that
blocks reader warnings for uncalibrated/low-n cells.

**Done when:** every warning carries a calibrated probability + magnitude band, and only cells
passing the gate are reader-visible.

## M4 — Unscheduled detection + corroboration (L)

**Goal:** go beyond scheduled events to the noisy, high-impact world.

**Build:** ingest wires/Benzinga/GDELT/on-chain/X (async pollers); MinHash dedup + clustering; LLM
classification with the polarity prompts; entity-linking to instruments/countries via the
gazetteer; the log-odds corroboration model + WATCH→CONFIRMED→RETRACTED state machine.

**Done when:** an unscheduled event (a hack, a tariff headline) is detected, deduped, classified,
entity-linked, corroborated, and routed to prediction — with a detection confidence.

## M5 — Coverage expansion + regime conditioning (M, partly parallel)

**Goal:** fill the matrix and add nuance.

**Build:** widen to more event types and instruments incl. the sector/single-name layer; regime
buckets (VIX/rate-regime) as calibration dimensions; partial-pooling for sparse cells; keep
rare/systemic events flagged as scenario priors.

**Done when:** the matrix is broadly populated, regime-conditioned, with low-n cells honestly
flagged.

## M6 — Productize (L)

**Goal:** turn the engine into something readers receive.

**Build:** the alerting layer (severity = magnitude × confidence, dedup, anti-alert-fatigue
thresholds, black-swan trigger); delivery channels (email/web/WebSocket) with disclaimers +
licensing guard; wrap the logic in a FastAPI service; graduate DuckDB → Postgres/TimescaleDB +
Redis if/when concurrency demands it.

**Done when:** real users get well-formed, rate-limited, compliant warnings through a real channel.

## M7 — Harden, scale & operate (ongoing)

**Goal:** reliable, observable, self-maintaining.

**Build:** observability (latency, classifier accuracy, alert precision/recall, calibration drift);
auto-recalibration on drift; CI/CD; streaming bus (Kafka/Bytewax) only if throughput demands;
compliance/audit trail; data-ops for feeds.

**Done when:** it runs unattended, recalibrates itself, and alerts you before it degrades.

---

## Critical path & parallelism

- Strictly sequential: M0 → M1 → M2 → M3 (each needs the prior).
- Parallel: M4 can start alongside M3 once M2 exists. M5 is continuous from M3 onward.
- Gated: M6 needs M3 (don't productize uncalibrated warnings). M7 is ongoing from M6.

## Graduation triggers (stay lightweight until these fire)

| Move | Trigger | Milestone |
| --- | --- | --- |
| DuckDB → Postgres/Timescale | concurrent writers or a live serving API | ~M6 |
| Scripts → FastAPI service | something external must call it | M6 |
| Polling → streaming bus (Kafka/Bytewax) | feed volume outgrows async polling | M7 (maybe never) |

## The one principle to hold

Never widen (M4/M5) or productize (M6) ahead of honesty (M3). A broad system that emits
uncalibrated confidence is worse than a narrow one that's trustworthy — which is the whole point of
a warning product.
