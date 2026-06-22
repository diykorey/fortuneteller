# FortuneTeller

FortuneTeller forecasts how today's events ripple through markets and the world. From an event
happening now, it forecasts — across **short / mid / long horizons**:

- **The shake** — the event's own immediate impact.
- **The aftershakes** — the follow-on events and reactions it is likely to trigger.
- **The result of the aftershakes** — the downstream impact of those reactions, forecast on its own track.

Each forecast is *explained*, not just emitted — but every claim is anchored to a **measurable
backbone** (realized market moves), so confidence stays **calibrated** rather than asserted. A
forecasting/warning product, not HFT (the latency budget is seconds-to-minutes).

Design principles that run through everything:

- **Calibrated, not certain** — every forecast carries a probability and a magnitude range.
- **Anchored explanation** — the narrative explains the numbers; it may only claim what the
  measurable spine can (eventually) score. No unfalsifiable storytelling.
- **Surprise drives magnitude** — built around `actual − expected`, not headline tone.
- **Fast-but-noisy is confirmed before it fires** — speed tiers corroborated against reliable ones.
- **Knowledge base is config, pipeline is code** — the reference tables are data the pipeline reads.

## How it works

A **measurable spine** grounds everything: events flow through a deterministic pipeline that
predicts market impact and grades itself against realized returns.

```
ingest → classify (31 event types) → entity-link → corroborate → estimate surprise
→ predict (effect-size × regime, multi-horizon) → calibrate confidence → severity/dedup → warn → capture outcome
```

Captured outcomes feed a calibration loop that re-estimates the effect-size matrix, so the predictor
keeps learning. On top of that spine, a **causal-chain layer** forecasts the aftershakes (likely
follow-on events, constrained to the taxonomy) and their results, and explains the
shake → aftershake → result story — only ever asserting what the spine can score. Build-now detail
is in [mvp-architecture.md](docs/mvp-architecture.md); the eventual production shape is the
north-star [architecture sketch](docs/architecture.md).

## Documentation

Start at [`docs/`](docs/README.md). Highlights:

- **Architecture:** [MVP — build-now](docs/mvp-architecture.md) · [north-star sketch](docs/architecture.md)
- **Specs:** [Detection & Calibration](docs/detection-and-calibration.md) ·
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

Bootstrapping, **measurable-spine first**. The repo holds the design docs + seed data (mirrored from
Notion) and the **M0-01 project skeleton** (uv / DuckDB / Pydantic). The spine is built against a
narrow [provable core](docs/mvp-architecture.md) — scheduled-macro events × ~5 instruments,
calibrated against returns — before the causal-chain layer and broader coverage are added; see the
[roadmap](docs/roadmap.md) and [M0 tickets](docs/m0-tickets.md).

> **Data provenance:** narrative specs are reproduced in full. The standalone reference databases
> are partial (read-only Notion export limits) — each table states its completeness. See
> [docs/data/README.md](docs/data/README.md).
