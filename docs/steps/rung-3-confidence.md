# Rung 3 — honest confidence

> Rung 3 of the [Roadmap](../roadmap.md#after-the-mvp--the-feature-ladder)'s feature ladder. It
> keeps testing the [Legend](../legend.md)'s third claim, now for a stated confidence, and follows
> its step template. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when `predict` says the dollar closes up, how sure should we be, and how far
will it move? And when it says 70%, is it right about 70% of the time?

[Rung 2](rung-2-predict.md#results) left one link worth trusting (the dollar on a jobs-report
surprise, right 68% of the time against 47% for "always up") and one that mostly rides the drift
(the yield: 65% against 61%). Both print the same bare "up". The Legend's promise is confidence that
means something: a number per call, and a range for the move, each checked against what happened.

At the end: every call from `predict` carries a probability and a 50% band for the move, or stays
silent because too few calls came before it; and the replay grades both.

## What a confident call is

At a release where rung 2's link makes a call:

- **Probability:** the link's record on its own earlier calls, smoothed toward a coin: (right + 1) /
  (calls + 2). Fewer than **20** earlier calls: no probability and no call, "too few calls so far".
  This is the gate's minimum history that rung 2 lacked.
- **Drift probability**, its baseline: how often the market moved the called way on the earlier
  noticeable releases, smoothed the same way. It is what a call would be worth if it were only
  riding the drift.
- **Band:** the middle is the Theil–Sen slope fitted on earlier noticeable releases times the
  surprise; the band is the middle plus the 25th to 75th percentile of those releases' misses
  (move minus slope × surprise). In the market's own unit, as in `observations`.

Everything comes from releases before the call, as in rung 2's walk-forward.

## The rule, fixed before any call is graded

**A link's confidence is honest** if, over the calls that carry a probability (at least 30):

1. **Calibrated:** calls grouped by their probability (under 60%, 60–70%, 70% and over); in each
   group of at least 10, the share right is inside the 95% binomial interval around the group's
   mean probability.
2. **Better than a coin and than drift:** its Brier score is below 0.25 and below the drift
   probability's Brier on the same calls.
3. **Bands mean 50%:** the share of moves inside their band is inside the 95% binomial interval
   around 50%.

Fewer than 30: too few to tell. With and without COVID, as everywhere. The smoothing, the 20, the
groups and the 25th–75th band are fixed here; nothing is tuned on the result.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `study.confident_calls`: per link, each walk-forward call with its probability, drift probability and band, or silent with too few earlier calls | A planted link right on 80% of calls states about 80% once past 20 calls; planted moves land in their band about half the time; changing any later release leaves a call's numbers unchanged |
| 2 | `predict --event cpi\|nfp`: a confidence table per link (calls, mean probability, share right, Brier, coin, drift Brier, band coverage, verdict) with and without COVID, under rung 2's tables | The table printed on real data; rung 2's tables unchanged |
| 3 | `predict --actual X`: each call with its probability and band, e.g. `DXY up 67% (58 calls before), +0.12 to +0.41` | Prints them, or silence with the reason |
| 4 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says, per link, whether its confidence is honest, with and without COVID |

## How you know it is right

- **No look-ahead.** As in rung 2: a test changes a call's own move and every later release, and
  checks that call's probability, drift probability and band do not change; mutation-checked by
  letting each see the release itself.
- **It can fail.** A planted link that is right 55% of the time but states its record must not beat
  drift where the planted drift is 60%; a band built from too narrow a spread must miss the 50%.
- **Expected outcome, written down first:** the dollar should pass 2 and 3; the yield is likely to
  fail 2 against drift; CPI's links are too few. A result that differs is reported as it is.

## What this step does not do

No new events, markets or expected values. No logistic or isotonic fit: about 80 calls on the best
link are too few to fit a curve, so the probability is the record. No probability that varies with
the surprise's size; the replay reports the hit rate for surprises under and over twice the step,
as a measurement only. No log of live calls: rung 4. No table.

## Technical details

`study.confident_calls(flow, baseline, instrument)` reuses `walk_forward`'s calls and `_flow_pairs`'
history; `stats.theil_sen` for the slope; percentiles in plain Python. The 95% binomial interval
needs a tail at any rate, not only a coin's: a small function beside `stats.binomial_p`. `predict` and `--actual` in `__main__.py`.

## Results

*Filled in by step 4.*
