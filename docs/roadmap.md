# Roadmap

> Why this plan has this shape — the target, the idea being tested, and the principles behind the
> ordering — is in the [Legend](legend.md). Unfamiliar acronym, ticker, or term? Every one is
> explained in the [Glossary](glossary.md).

## The goal

Given an event, say which instruments move, by how much, in which direction — with confidence that
means something. A warning product, not HFT: the latency budget is seconds to minutes.

## The MVP — "does the edge exist?"

The MVP answers one question with real data: **when CPI comes in different from what was expected,
do liquid instruments move in a measurable, repeatable way?**

It is not a predictor and not a product. It is a table of measured numbers with an honest `n` next
to each one. **"No edge" is a valid result** — finding that out in four steps is the whole point.

**Scope:** one event type (CPI) × five instruments — SPY, UST 10Y, DXY, Gold, VIX. Nothing else,
until this works.

**Done when:** for each of those five cells you can read a measured effect size (move per unit of
surprise), a hit rate, and `n` — and say honestly whether an edge is there.

### The four steps

Each step ends with something you can run that prints a real number. No step builds machinery for a
step that has not happened yet. The sample outputs below are illustrative shapes, not targets.

| # | Step | What it prints | Done when |
| --- | --- | --- | --- |
| 1 | **[Releases](step-1-releases.md)** — CPI release dates and actuals from FRED into `event_instances` | `loaded N CPI releases, <first> … <last>` | The table holds real releases |
| 2 | **Prices** — daily bars for the five instruments; the return around each release into `observations` | `5 instruments × N releases = M observations` | Real returns joined to real events |
| 3 | **Raw move** — do these instruments move abnormally on CPI days versus ordinary days? | Typical release-day move vs baseline, per instrument | You know whether the event matters at all |
| 4 | **Surprise** — add expected-vs-actual; relate the move to the surprise | Move per surprise unit, hit rate, `n`, per cell | **MVP complete** |

### Why this order

The previous attempt predicted from placeholder numbers first and measured afterwards. That built
machinery before touching real data, and produced output that looked like a product while meaning
nothing. Measuring first means the first thing that exists is a fact, and every feature after it
stands on real numbers. See the reset note in [CLAUDE.md](../CLAUDE.md).

### What the MVP deliberately does not have

No live data path, no scheduler, no delivery, no detection, no confidence calibration, no second
event type, no web anything. Each is on the ladder below and earns its turn.

### The open decision inside step 4

Surprise needs an expected value to subtract, and **free historical consensus is the scarcest data
in this project**. The choice is deliberately deferred to step 4, when steps 1–2 have made it cheap
to test:

- **Market consensus** — what forecasters actually predicted. The authentic definition, and the
  hardest to obtain free.
- **Computed baseline** — an expected value modelled from past prints. Always available from FRED
  alone, but it measures surprise-vs-trend rather than surprise-vs-market.

If consensus proves unobtainable, step 4 falls back to the computed baseline **and says so in its
output**. The claim shrinks; it does not get quietly overstated.

## After the MVP — the feature ladder

In order. Each rung is worth building only because the one below it worked.

| # | Feature | Why it waits |
| --- | --- | --- |
| 1 | **More events** — NFP, Fed decisions | Same code, more rows. Widen only once one event type is measured. |
| 2 | **Predict the next release** | A prediction is only worth emitting once it comes from measured numbers. |
| 3 | **Honest confidence** — hit rate → probability, magnitude bands, silence on low-`n` cells | "70%" must mean 70%. Needs enough measured history to calibrate against. |
| 4 | **Keep score** — log predictions, grade them against outcomes | You cannot grade predictions you are not yet making. |
| 5 | **Live path** — fetch the release when it lands, instead of by hand | Automating a manual step that must first be worth automating. |
| 6 | **Delivery** — the warning actually reaches a person | Never deliver uncalibrated warnings; needs rung 3. |
| 7 | **Unscheduled events** — detection, classification, entity linking, corroboration | The hardest part of the system, and worthless without a working predictor behind it. |

Beyond the ladder, and deliberately not planned in detail: breadth (more instruments, regime
conditioning), productization, and operations. They get planned when rung 7 is in sight.

## The rules this roadmap is built on

From the [reset note in CLAUDE.md](../CLAUDE.md), because they are what keeps steps small:

1. No new package until a second caller needs it.
2. No indirection for a single case.
3. A plan doc must be shorter than the code it specifies.

## Graduation triggers

Build the heavier thing only when its trigger actually fires. None has.

| Move | Trigger |
| --- | --- |
| DuckDB → Postgres | Concurrent writers, or a live serving API |
| Script → web service | Something external must call it |
| Polling → streaming bus | Feed volume outgrows simple polling |

## Status

Last completed task and the next one: **[status.md](status.md)**.

Historical planning documents, including the superseded M0–M7 milestone scheme, are kept in
[legacy/](legacy/README.md).
