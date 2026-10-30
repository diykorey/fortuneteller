# Ordinary days from each flow's own years

> Step 8a of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-29 before the
> statements' preview, when [scheduled statements](scheduled-statements.md#results) fired
> precision's *loud and quiet years* trigger. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** compare a flow's days with ordinary days from the same years, so a market
that is louder now than in its past doesn't seem to "move" on every recent event.

Rung 1's raw move compares a flow's days with every ordinary day of the market's history. The ECB
president's days start in 2013, while the Nasdaq's ordinary days start in 1971. So the Nasdaq
*moves* on those days at 1.27 overall, but only 0.71 and 1.17 within each era. Five flows start
in 2013 or 2014: the ECB's decisions, the flash HICP, ISM, claims and the statements. Every one of
them is judged against decades in which it had no days.

## The rule, fixed before any move is measured

- **Ordinary days from the flow's own years.** For each flow and market, an ordinary day must fall
  on or after that flow's first reaction day on that market. The rest is unchanged: no stored
  non-lesser event's reaction day, the same ratio and permutation test, and the same bars (ratio ≥
  1.10, p < 0.01).
- **Only the raw move changes.** The surprise test, walk-forward, the calls, their grades and the
  chance line (192 cells) do not use ordinary days, and stay identical.
- **The era table stays** as context.
- **Already seen** (2026-10-29, exploratory, ordinary days from 2013 on): the Fed chair's, the
  ECB president's and claims' cells. Their changes are not counted as evidence for this rule.
- **Expected outcome, written down first:**
  - CPI's and the jobs report's verdicts are unchanged, because their days span every market's
    history.
  - The Fed, retail sales, core PCE and GDP change in at most two cells each.
  - In the five flows from 2013 or 2014, the Nasdaq loses most of its *moves*. In exchange, the
    yields, the dollar, the euro and Europe's indices gain some on ISM and the ECB's decisions.
  - The flash HICP's *moves* in New York (the S&P 500, VIX, the Nasdaq) fall to *unclear* or below.
- **Earlier findings** that change are amended where they stand, with this date, and never
  rewritten.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`measure_raw_moves` takes ordinary days from the flow's first reaction day on each market~~ **done**; on a copy of the store, 59 cells changed verdict in eleven flows (the jobs report's in none), *moves* 52 → 54; surprise, walk-forward, calls and the chance line identical; the scoreboard in 502 s | A test's market, quiet in old years and loud since, no longer *moves* on events that all fall in the quiet years; all twelve flows re-measured on a copy of the store; every changed verdict listed; the surprise, walk-forward and calls entries identical |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md); the changed findings amended in their step documents | Every flow's verdicts before and after, against the expected outcome |

## Technical details

One line in `study.measure_raw_moves`: a day before the flow's first reaction day on that market
is skipped, for the flow's own days and for ordinary days alike. In `docs/precision.md`, the
*loud and quiet years* row goes, because its simpler fix is built. A new row takes its place: the
years inside the span are still not matched one by one, so a flow whose days bunch in its recent
years keeps a smaller tilt. Its more precise form is per-year weighting or a volatility model.

## What this does not do

No per-year weighting, no volatility model (GARCH), no change to the bars, the surprise test or the
calls.
