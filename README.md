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
is being rebuilt from a measured base; see the [roadmap](docs/roadmap.md).

## Documentation

**[`docs/`](docs/README.md) is the single entry point** — it carries the map of how everything
connects. The documents form one chain, from *why* to *what exactly*:

- **[Legend](docs/legend.md)** — the target, the bet behind it, the way we intend to get there, and
  the template every step document follows.
- **[Roadmap](docs/roadmap.md)** — what gets built, in what order, and what "done" means.
- **[Step 1 — Releases](docs/step-1-releases.md)** — the step being worked on now.
- **[Glossary](docs/glossary.md)** — every acronym, ticker, and piece of jargon, explained.

The pre-2026-09-11 design corpus — architecture sketches, reference-table documentation, the old
milestone plans — is kept for reference in [`docs/legacy/`](docs/legacy/README.md).

## Repository layout

```
docs/            # legend + roadmap + step docs + glossary — start at docs/README.md
docs/legacy/     # the pre-2026-09-11 design corpus, kept for reference
data/seed/       # committed seed CSVs the embedded store loads
src/fortuneteller/  # the package: config, models, db helper, seed loader, CLI
tests/           # pytest suite (ruff + mypy --strict + pytest is the gate)
```

## Status

Bootstrapping, **measurable-spine first**. **M0 — the data spine — is complete, and so is step 1 of
the MVP.** Today the repo gives you typed Pydantic models, a DuckDB schema, the committed seed
tables, a CLI that loads and queries them, and the real CPI release history from FRED:

```bash
uv sync
uv run fortuneteller init        # create the DuckDB file
uv run fortuneteller seed        # load the seed CSVs
uv run fortuneteller query-demo  # a sample effect-size lookup
uv run fortuneteller load-releases  # CPI release history from FRED (needs FT_FRED_API_KEY)
```

There is **no prediction code yet** — no surprise computation, no direction resolution, no warnings.
An earlier attempt at that layer was reset on 2026-08-05 for being over-engineered for the stage; it
is preserved on the `main_05082026` branch.

Next is the MVP: a measured answer to **does the edge exist** — one event type (CPI) × five liquid
instruments, from real historical data, in four steps. Not a predictor, not a product: a table of
real numbers with an honest `n` beside each. Everything else waits behind it. See the
[roadmap](docs/roadmap.md).

> **Data provenance:** the seed reference tables are partial (read-only Notion export limits) and
> the effect-size values in them are illustrative placeholders, not measurements — replacing them
> with measured numbers is what the MVP is for. Each table states its own completeness; see
> [docs/legacy/data/README.md](docs/legacy/data/README.md).
