# FortuneTeller

A market-event prediction & warning system. It ingests social / political / climate / macro
events, predicts which instruments move (**direction + magnitude + horizon**) with **calibrated**
confidence, and warns readers within a seconds-to-minutes budget. A warning product, not HFT.

Four design principles run through everything:

- **Calibrated, not certain** — every warning carries a probability and a magnitude range.
- **Surprise drives magnitude** — built around `actual − expected`, not headline tone.
- **Fast-but-noisy is confirmed before it fires** — speed tiers corroborated against reliable ones.
- **Knowledge base is config, pipeline is code** — the reference tables are data the services read.

## How it works (10-stage pipeline)

```
ingest → classify (31 event types) → entity-link → corroborate → estimate surprise
→ predict (effect-size × regime) → calibrate confidence → severity/dedup → warn → capture outcome
```

Captured outcomes feed a calibration loop that re-estimates the effect-size matrix, so the
predictor keeps learning. Full detail in the [architecture sketch](docs/architecture.md).

## Documentation

Start at [`docs/`](docs/README.md). Highlights:

- **Specs:** [Architecture](docs/architecture.md) ·
  [Detection & Calibration](docs/detection-and-calibration.md) ·
  [Event Polarity & Classifier Prompts](docs/event-polarity-and-classifier-prompts.md) ·
  [News-Source Stack](docs/news-source-stack.md) ·
  [Calibration Dataset](docs/calibration-dataset.md)
- **Planning:** [Roadmap (M0–M7)](docs/roadmap.md) · [Tech Stack & Reasoning](docs/tech-stack.md) ·
  [M0 Tickets](docs/m0-tickets.md)
- **Reference data:** [events, instruments, news sources, effect-size, …](docs/data/README.md)

## Repository layout

```
docs/            # specs, roadmap, tech stack, tickets (mirrored from Notion)
docs/data/       # reference tables as markdown (provenance noted)
data/seed/       # committed seed CSVs the embedded store loads
```

## Status

Pre-M0. This repository currently holds the design docs and seed data mirrored from the project's
Notion workspace; the runtime code (the M0 scaffold — uv / DuckDB / Pydantic) is described in
[docs/m0-tickets.md](docs/m0-tickets.md) but not yet implemented.

> **Data provenance:** narrative specs are reproduced in full. The standalone reference databases
> are partial (read-only Notion export limits) — each table states its completeness. See
> [docs/data/README.md](docs/data/README.md).
