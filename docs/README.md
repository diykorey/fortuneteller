# FortuneTeller — Market-Event Prediction System

Home for the event → market prediction & warning system. All reference data, mappings, the
quantitative layer, and the calibration dataset are documented here.

> Mirrored from the project's Notion workspace. Narrative/spec pages are reproduced in full;
> the standalone reference databases are summarized as far as the export tooling allows — see
> [`data/README.md`](data/README.md) for provenance and known gaps.

## Design & spec documents

| Document | What it covers |
| --- | --- |
| **[MVP Architecture](mvp-architecture.md)** | **Build-now picture (M0–M3): Python-first, single process, DuckDB, provable-core scope. Start here.** |
| [System Architecture Sketch](architecture.md) | *North-star / eventual* — the full Java/Kafka production shape. Not the build-now plan |
| [Detection & Confidence Calibration](detection-and-calibration.md) | Part A: turning a noisy firehose into trustworthy events. Part B: making "70%" mean 70% |
| [Event Polarity & Classifier Prompts](event-polarity-and-classifier-prompts.md) | Polarity of each event type + the three LLM classifier prompts |
| [News-Source Stack & Coverage](news-source-stack.md) | Ranked source list, coverage by event, coverage by market group, gap analysis |
| [Event-Study Calibration Dataset](calibration-dataset.md) | Data model, methodology, Postgres DDL, calibration query, pitfalls |
| [Standardized Surprise](standardized-surprise.md) | What "surprise" means, actual−consensus → surprise_sd, the above/below/unknown sign, and its place as pipeline stage 5 |
| [News Source Coverage & Gaps](news-source-coverage-and-gaps.md) | Standalone coverage check across the taxonomy and platform list |

## Planning

| Document | What it covers |
| --- | --- |
| [Roadmap — Prototype to Complete Solution](roadmap.md) | Milestones M0–M7, critical path, graduation triggers |
| [Tech Stack & Reasoning](tech-stack.md) | Python-first, DuckDB, no-ORM decisions and their rationale |
| [M0 Tickets — Scaffold & Seed](m0-tickets.md) | LLM-ready tickets M0-01 … M0-10 with file paths and acceptance criteria |
| [M0-R Tickets — Replay Harness](m0-r-tickets.md) | LLM-ready tickets M0-R-01 … 05: the deterministic fixture-replay dev loop |
| [M1 Tickets — Thin Vertical Slice](m1-tickets.md) | LLM-ready tickets M1-01 … 07: CPI → resolved warning, end to end, + the free live path |

## Reference data

| Table | Status |
| --- | --- |
| [Market-Moving Events (Ranked)](data/events.md) | Full — 31 events with polarity and tier |
| [News Sources (Ranked)](data/news-sources.md) | Full — 25-source ranked stack + coverage matrices |
| [Instruments / Tickers](data/instruments.md) | Representative subset (12 of 55) |
| [Effect-Size Matrix (event × instrument)](data/effect-size-matrix.md) | Representative seed subset |
| [Top Countries by GDP — Coverage](data/countries.md) | Representative subset (10 of 50) |
| [Markets & Trading Platforms](data/platforms.md) | Representative subset (of 132) |

Seed data for the embedded store lives in [`/data/seed`](../data/seed).

## The system in one line

Ingest social / political / climate / macro events → predict which instruments move
(direction + magnitude + horizon) with **calibrated** confidence → warn readers within a
seconds-to-minutes budget. A warning product, not HFT.
