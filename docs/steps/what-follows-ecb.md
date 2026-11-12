# What follows an ECB decision, over spans

> Step 17, part 1f, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1e](what-follows-claims.md); taken 2026-11-11, the roadmap's "the ECB's with the euro
> area, the first country after the US". Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when the European Central Bank cuts, holds or raises its rate, what did each
market do over the next day, week and month? It is [part 1](what-follows.md), the Fed's decisions,
for the ECB.

At the end: `fortuneteller follows --event ecb` prints part 1's table for the ECB, and a trigger file
may name `ecb`.

**Only a hold can hold.** On the calendar cache of 2026-11-11 the ECB made 115 decisions from
2013-04-04 to 2026-09-10: 87 holds, 15 cuts and 12 hikes by the rule below, the first decision having none. The walk-forward
needs ten earlier decisions of a kind before it answers, so a cut has at most 5 graded and a hike
2. Only a hold, with at most 77, can reach 30. Cuts and hikes are still shown on all history.

## The way to reach it

- **The rate.** The ECB has three rates. From 2015-12-03 the calendar lists the deposit facility
  rate, the one the ECB steered by in the negative-rate years. It moved alone on 2015-12-03 and
  2019-09-12, and on 2024-09-12 it fell by 0.25 while the refinancing rate fell by 0.6, when the
  corridor between them narrowed. Before that date only the main
  refinancing rate is listed. So a decision's rate is the deposit rate where the calendar has it
  (titled `Deposit Facility Rate`, or `Deposit Facilty Rate` until 2017), and the refinancing rate
  (`ECB Interest Rate Decision`) before.
- **The kind, from consecutive actuals.** A decision is a *cut* if its rate is below the previous
  decision's, a *hike* if above, and a *hold* if equal. The first decision has no kind. The
  calendar's own `previous` column agrees on every decision in the cache of 2026-11-11.
- **The decisions are the stored ones.** The kinds come from the calendar replies that
  `load-releases` already fetches for `ecb`. The rows `event_instances` holds do not change.
- **Part 1's method, unchanged:** the spans, the non-overlap rule, the base and its cut, the answer
  with direction apart from size, the placebo a span away, the walk-forward and its bars, and the
  chance lines. A decision is stored at the calendar's time, 13:45 to 14:45 Frankfurt until 2022-06 and 14:15
  since 2022-07-21, before Europe's close and New York's, so every market reacts the same day.
- **Shared days are kept**, as for retail sales, CPI and claims. Every decision falls on a Thursday,
  and claims are a *lesser* flow, so a claims morning does not make an ECB day shared. The results
  give the shared days by the other flow.
- **Triggers.** `TRIGGER_KINDS` gains `ecb` with the Fed's kinds, `cut`, `hold` and `hike`.

## The rule, fixed before anything is shown

- Part 1's bars and the kinds above, none of them changed by what the run shows.
- **Expected outcome, written first.**
  - Arithmetic, not a finding: a cut has at most 5 graded and a hike at most 2, so neither can hold.
  - Walk-forward: nothing holds, hold days included. The Fed's holds held nothing either; the
    nearest was VIX falling on the day, 51%.
  - On all history: no more answers than the chance line `follows` prints, plus 2.
  - After a hike, EUR/USD *up* on the day, read as the kind; nothing else on the day for a hike or
    a cut.
  - On a hold: VIX *down* on the day, as after the Fed's holds; nothing else.
- Every existing output is unchanged byte for byte, including the five `follows` tables and the
  ECB's `event_instances` rows.

*Written 2026-11-11 16:09, before `follows --event ecb` first ran on the store at about 16:20;
nothing above was changed after it.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The ECB's rates from the calendar; `follows --event ecb`; `ecb` in `TRIGGER_KINDS`~~ **done** 2026-11-11 (PR #287) | Tests: a decision's kind comes from the deposit rate where listed and the refinancing rate before; `follows --event ecb` prints a header with the three kinds; an ECB trigger is answered, not refused. On a copy of the store the header gives the counts by kind, and the other five tables are unchanged |
| 2 | ~~Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row~~ **done** 2026-11-11, [below](#results) | Each kind's answers and walk-forward records are recorded against the expected outcome |

*Step 1, 2026-11-11 (PR #287):* on a copy of the store the header reads `follows: 115 ECB decisions
2013-05-02 … 2026-10-29: 15 cuts, 88 holds, 12 hikes`; the calendar's current quarter adds the
hold of 2026-10-29. 225 cells print. The other five tables and the answer to the trigger filed so
far are byte for byte the ones before. `follows` and `triggers` now share one function for a
central bank's kinds, `_decision_kinds`.

## Results

Measured 2026-11-11 on a copy of the store: 115 decisions with a kind, 2013-05-02 … 2026-10-29,
15 cuts, 88 holds and 12 hikes. 30 of them fell on a day with another stored release: 21 holds, 5
hikes and 4 cuts, most often with US GDP (10), retail sales (9) or CPI (8).

**Nothing answers.** On all history no cell of the 225 gives *up*, *down* or *about the same*,
against about 6.8 by chance; so nothing holds walk-forward either. The smallest chance is 0.015,
the 10-year yield over the week after a cut, 9 / 5 / 1 of 15. On the day of a hold, VIX falls on
35 of 88 against a base of 36%, and EUR/USD on 42 of 88 against 34%; neither is an answer (chance
0.18 and 0.20). After a hike EUR/USD rose on 5 of 12 days and fell on 7.

**Against the expected outcome:**

- Cuts and hikes too few to hold: **right**, every walk-forward cell for them is *too few*.
- Nothing holds: **right**.
- Answers no more than the chance line plus 2: **right**, none against 6.8.
- EUR/USD *up* on the day after a hike: **wrong**, 5 up and 7 down.
- VIX *down* on the day of a hold: **wrong**, *can't say*.
- Every existing output unchanged: **right**.

**What it says.** An ECB decision, read as cut, hold or hike, tells nothing about what these markets
did next, on the day, the week or the month: fewer answers than chance alone would give. The kind is
known before the day: the calendar's forecast equals the decision at almost every meeting, which is
why the flow has no surprise rule ([ECB decisions](ecb-decisions.md)). An ECB trigger will be
answered *can't say* on every market. No new call.
