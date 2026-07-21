# Business Overview — What FortuneTeller Is and Why It Exists

> The product story in one place: the problem, the idea, who it's for, and the principles that make
> it defensible. For the eventual technical shape see [MVP Architecture](mvp-architecture.md) and
> the [north-star sketch](architecture.md); for what is actually built today see
> [Implementation Status](implementation-status.md).

## The one-liner

**FortuneTeller turns an event happening now into a calibrated, explained warning about which
markets will move — direction, magnitude, and horizon — within a seconds-to-minutes budget.** It is
a forecasting / warning product, **not** high-frequency trading: the edge is *trustworthy foresight
and explanation*, not latency arbitrage.

## The problem

When a market-moving event breaks — a hot CPI print, a stablecoin depeg, a war headline, an OPEC
decision — three things are simultaneously true:

1. **The information exists** (on wires, econ calendars, on-chain, social) seconds after the event.
2. **The market reaction is patterned** — the same *kind* of event moves the same instruments in
   broadly the same way, scaled by how much it *surprised* consensus.
3. **Almost nobody can act on 1 + 2 fast, consistently, and honestly.** Newsrooms are slow and
   qualitative; trading desks are fast but proprietary and opaque; retail commentary is loud,
   uncalibrated, and unfalsifiable.

The gap is a product that reads the event, maps it to its likely market impact, and says so **with
a confidence you can trust** — fast enough to be a warning, calibrated enough to be believed.

## The idea

Treat market reaction to events as a **measurable, learnable function** and wrap it in a warning
product.

- **A measurable spine.** Every event flows through a deterministic pipeline —
  *ingest → classify → entity-link → corroborate → estimate surprise → predict → calibrate →
  warn → capture outcome* — and the predictor **grades itself against realized market returns**.
  Because outcomes are captured and fed back, the effect-size estimates keep improving. Nothing is
  asserted that the spine cannot (eventually) score.
- **Surprise, not headline tone, drives magnitude.** Markets price the *deviation from
  expectation*, so the system is built around `actual − consensus` (standardized to
  `surprise_sd`), not whether a number "sounds bad." See [Standardized Surprise](standardized-surprise.md).
- **A causal-chain layer on top.** Beyond the immediate move ("the shake"), the product forecasts
  the **aftershakes** (likely follow-on events, constrained to a fixed taxonomy) and their results —
  and explains the shake → aftershake → result story, only ever claiming what the measurable spine
  can score.

## What makes it defensible

These are the principles that separate a trustworthy warning product from noise. They run through
every design decision in this repo.

| Principle | What it means | Why it's the moat |
| --- | --- | --- |
| **Calibrated, not certain** | Every forecast carries a probability *and* a magnitude range; "70%" is measured to actually mean 70%. | A warning product lives or dies on trust. Calibrated confidence is the product. |
| **Anchored explanation** | The narrative explains the numbers; it may only claim what the measurable spine can score. No unfalsifiable storytelling. | Explanations that can't be graded are marketing. Grading them is the differentiator vs. punditry. |
| **Surprise drives magnitude** | Built on `actual − expected`, not tone. | Matches how markets actually price events; avoids the classic "good number, market fell" trap. |
| **Confirm fast-but-noisy before firing** | Speed-tier sources are corroborated against reliable ones before a warning goes out. | Kills the false-alarm problem that destroys alert products. |
| **Knowledge base is config, pipeline is code** | Reference tables (event types, instruments, effect sizes) are *data the pipeline reads*, not hard-coded logic. | The system improves by re-estimating data, not rewriting code — cheap to calibrate and widen. |

## Who it's for

A warning product, so the customer is anyone who needs **early, trustworthy, explained** notice of
market impact but is not themselves an HFT shop:

- **Active investors / traders** who want a calibrated heads-up ("hot CPI just printed — SPY likely
  down, DXY up, gold down, on a minutes-to-hours horizon") faster than the news cycle and more
  honest than social media.
- **Risk & treasury desks** wanting an early, explained flag on exposure to a breaking event.
- **Financial media / research** wanting a defensible, numbers-anchored first take.

The latency budget is **seconds-to-minutes**, which is precisely why this is buildable without
tick-data infrastructure or co-location — it competes on *foresight and calibration*, not speed.

## How the business stays honest and cheap: scope discipline

The single biggest risk for a system like this is **widening or productizing ahead of honesty** — a
broad system emitting uncalibrated confidence is worse than a narrow one that's trustworthy. So the
build order is deliberate:

- **Prove one slice first.** The "provable core" is **scheduled-macro events (CPI / NFP / Fed) × ~5
  liquid instruments** (SPY/ES, a rates benchmark, DXY, Gold, VIX), calibrated on recorded episodes
  and then a **free** data stack (FRED + a free econ calendar + yfinance/Stooq).
- **Everything else is post-proof.** The full 31-event taxonomy, ~55 instruments, 132 platforms,
  unscheduled detection, and paid/tick data are deferred until the core beats — or honestly fails to
  beat — a market-implied benchmark.
- **Stay lightweight until a trigger fires.** DuckDB → Postgres, scripts → a service, polling →
  streaming: each graduation waits for a concrete need (concurrent writers, an external caller, feed
  volume), not ambition. See the [Roadmap](roadmap.md).

This keeps burn low (free data, single process, embedded store) and credibility high (never ship an
uncalibrated warning) while the core is proven.

## Positioning: what it is *not*

- **Not HFT / execution.** No order routing, no latency arbitrage, no co-location. The budget is
  seconds-to-minutes and the output is a *warning*, not a trade.
- **Not investment advice.** Every warning ships with a disclaimer; the product informs, it does not
  direct.
- **Not a black box.** Confidence is calibrated and reported; explanations are anchored to a spine
  that scores itself. If a cell isn't calibrated, it doesn't reach a reader.
- **Not breadth-first.** It deliberately does *one* event slice well before widening.

## The arc, in one line

**Ship the slice → make it honest → make it broad → make it a product → operate it.** The
[Roadmap](roadmap.md) sequences that as M0 (scaffold) → M1 (thin vertical slice) → M2 (calibration)
→ M3 (confidence + backtest gate) → M4 (detection) → M5 (coverage) → M6 (productize) → M7 (operate).
Today the project is early on that arc — see [Implementation Status](implementation-status.md) for
exactly where.
