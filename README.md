# FortuneTeller

FortuneTeller forecasts how today's events ripple through markets and the world. From an event
happening now, it forecasts — across **short / mid / long horizons**:

- **The shake** — the event's own immediate impact.
- **The aftershakes** — the follow-on events and reactions it is likely to trigger.
- **The result of the aftershakes** — the downstream impact of those reactions, forecast on its own track.

Each forecast is *explained*, not just emitted — but every claim is anchored to a **measurable
backbone** (realized market moves), so confidence stays **calibrated** rather than asserted. A
forecasting/warning product, not HFT (the latency budget is seconds-to-minutes). *Amended
2026-10-23:* an entertainment tool with a realistic approach, not a financial one: a fortune teller
who shows their record ([Legend](docs/legend.md#the-target)).

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
- **[MVP results](docs/mvp-results.md)** — what the MVP found, in plain words, and the options for
  what comes next. The four step documents behind it are in [`docs/steps/`](docs/steps/);
  [status](docs/status.md) names the task being worked on now.
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

Bootstrapping, **measurable-spine first**. M0 (the data spine), the MVP, ladder rungs 1–6 and the
roadmap's steps 1–4b are complete. The repo holds ten events (US CPI, the jobs report, Fed
decisions, retail sales, core PCE, GDP, the ISM survey and weekly jobless claims; ECB decisions and
the euro area's flash inflation) and seven markets (the S&P 500, the 10-year yield, the dollar index, gold, VIX, the DAX
and the Euro Stoxx 50), 1972 to today, from free sources: each market's measured move around every
release, how it relates to each surprise, and a walk-forward replay of every link.

```bash
uv sync
uv run fortuneteller --help                 # every command and what it prints
uv run fortuneteller load-releases          # every event, from FRED, the Fed and TradingView (needs FT_FRED_API_KEY)
uv run fortuneteller load-prices            # daily closes from Yahoo and the move around each release
uv run fortuneteller load-surprises         # each surprise against its expected values
uv run fortuneteller raw-move --event cpi   # do release days move more than ordinary days?
uv run fortuneteller surprise --event nfp   # does the move follow the surprise?
uv run fortuneteller predict --event nfp    # the walk-forward replay, and a call for the next release
uv run fortuneteller score                  # the live calls, graded
uv run fortuneteller scoreboard             # the page: every call graded, every verdict and record
```

**What it predicts:** the direction of the 10-year yield and the dollar index on the three links
that hold walk-forward (the jobs report's dollar clearly, its yield barely over drift, retail
sales' yield), each printed with its record as counts and its band, never a probability: none has
proved honest yet. On release days the calls are made, graded and delivered as a desktop popup
unattended ([the release-day job](docs/steps/release-day-job.md), [the evening
score](docs/steps/evening-score.md)). Stocks, gold and VIX follow no surprise by direction; the
Fed, the ECB, euro-area inflation and ISM give no call. [MVP results](docs/mvp-results.md) has the
findings in plain words, the [roadmap](docs/roadmap.md) what comes next, and
[status](docs/status.md) the task in hand.

> **Data provenance:** the seed reference tables are partial (read-only Notion export limits) and
> the effect-size values in them are illustrative placeholders, not measurements — replacing them
> with measured numbers is what the MVP is for. Each table states its own completeness; see
> [docs/legacy/data/README.md](docs/legacy/data/README.md).
