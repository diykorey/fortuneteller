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
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md); the changed findings amended in their step documents~~ **done** 2026-11-02, [below](#results) | Every flow's verdicts before and after, against the expected outcome |

## Results

Measured 2026-11-02 on a copy of the main store, the code before and after step 1 on the same copy.
60 of the 192 cells changed verdict, one more than step 1 counted on 2026-10-30: retail sales'
S&P 500 sits on the bar (1.0998 against 1.10) and the days since tipped it. *Moves* went from 52
to 54. Surprise, walk-forward, the calls and the chance line are untouched.

| Flow | *Moves* | Became *moves* | Stopped being *moves* | Cells changed |
| --- | --- | --- | --- | --- |
| CPI | 5 → 5 | — | — | 2 |
| Jobs report | 10 → 10 | — | — | 0 |
| Fed | 11 → 9 | — | dollar (1.23 → 1.18), Nasdaq (1.38 → 1.07) | 2 |
| Retail sales | 3 → 2 | 5-year yield (p 0.06 → 0.001) | dollar (1.23 → 1.19), Nasdaq (1.24 → 1.01) | 4 |
| Core PCE | 3 → 1 | — | VIX (1.24 → 1.17), Nasdaq (1.37 → 1.07) | 5 |
| GDP | 4 → 3 | — | Nasdaq (1.32 → 1.06) | 2 |
| ECB | 2 → 3 | FTSE 100 (1.07 → 1.37) | — | 6 |
| Flash HICP | 3 → 1 | — | VIX (1.45 → 1.27), Nasdaq (1.53 → 1.32) | 6 |
| ISM | 7 → 12 | S&P 500, dollar, gold, Euro Stoxx 50, FTSE 100 | — | 7 |
| Claims *(seen)* | 1 → 6 | dollar, gold, DAX, euro, 5-year yield, FTSE 100 | Nasdaq (1.16 → 1.04) | 10 |
| Fed chair *(seen)* | 0 → 0 | — | — | 7 |
| ECB president *(seen)* | 3 → 2 | Euro Stoxx 50 (1.10 → 1.25) | VIX (1.24 → 1.10), Nasdaq (1.27 → 1.16) | 9 |

- **The Nasdaq was the tilt.** It *moved* on nine flows; now on two, the jobs report and ISM. The
  Fed, retail sales, core PCE and GDP lose it too: their days start in the 1990s or 2000s, while
  the Nasdaq's ordinary days ran from 1971.
- **ISM is the loudest of the later flows:** twelve of sixteen markets *move*, every one but VIX,
  bitcoin, the defence ETF and the euro.
- **The era split now mostly agrees.** The 2008–2019 era lost its 2008–12 ordinary days for the
  flows from 2013, so its ratios rose. Of the new *moves*, all reach 1.10 in both eras but ISM's
  S&P 500 and Nasdaq (1.04 and 1.06 since 2020), ISM's Brent (1.02 before 2020) and claims' gold
  (1.09 since 2020).
- **Precision's new trigger fires once:** the ECB president's Brent *moves* (1.28) with 219 of its
  332 days since 2020, where its ratio is 1.09. Claims' and ISM's days split evenly between the
  eras, so their disagreements are not that tilt.

**Against the expected outcome:**

- CPI and the jobs report unchanged: **half right.** The jobs report's cells are identical; CPI's
  S&P 500 and Nasdaq fall from *unclear* to *doesn't*, its *moves* unchanged.
- The Fed, retail sales, core PCE and GDP at most two cells each: **wrong** for retail sales (4)
  and core PCE (5); right for the Fed and GDP (2 each).
- The Nasdaq loses most of its *moves* in the five later flows: **right**, ISM's alone stays.
  Yields, the dollar, the euro and Europe's indices gain on ISM and the ECB: **partly**, ISM gains
  the dollar, the Euro Stoxx 50 and the FTSE 100 (and the S&P 500 and gold, not expected); the ECB
  only the FTSE 100.
- The flash HICP's New York *moves* fall to *unclear* or below: **wrong for the S&P 500**, which
  still *moves* (1.55, 1.42 and 1.40 by era); right for VIX and the Nasdaq.
- The claims and statements cells were seen on 2026-10-29 and are not counted as evidence.

**What it means.** No call changes. The lesser flows now look different: lone claims days move six
markets, the dollar, the euro, the 5-year yield and Europe's stocks among them, where the pooled
baseline said nothing. The ECB president's Brent stays a *moves* that the era split does not
support.

## Technical details

One line in `study.measure_raw_moves`: a day before the flow's first reaction day on that market
is skipped, for the flow's own days and for ordinary days alike. In `docs/precision.md`, the
*loud and quiet years* row goes, because its simpler fix is built. A new row takes its place: the
years inside the span are still not matched one by one, so a flow whose days bunch in its recent
years keeps a smaller tilt. Its more precise form is per-year weighting or a volatility model.

## What this does not do

No per-year weighting, no volatility model (GARCH), no change to the bars, the surprise test or the
calls.
