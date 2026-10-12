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

At the end: every call from `predict` carries a probability and a 50% band for the move, or says
it has too few calls before it to state one; and the replay grades both.

## What a confident call is

At a release where rung 2's link makes a call:

- **Probability:** the link's record on its own earlier calls, smoothed toward a coin: (right + 1) /
  (calls + 2). With fewer than **20** earlier calls, the call stands but carries no probability or
  band: "too few calls so far". This is the minimum history rung 2's gate lacked.
- **Drift probability**, its baseline: of the earlier noticeable releases, the share whose move
  closed strictly the called way (a zero move counts against, as in rung 2's grading), smoothed
  the same way. Unlike rung 2's "always the expected direction", it follows the call: for a down
  call it is the share that closed down.
- **Band:** the middle is the Theil–Sen slope fitted on earlier noticeable releases times the
  surprise; the band is the middle plus the 25th to 75th percentile of those releases' misses
  (move minus slope × surprise). Computed in the market's unit as in `observations`, printed in
  percent for prices and basis points for the yield.

Everything comes from releases before the call, as in rung 2's walk-forward. Without COVID, as in
rung 2, drops March 2020 – April 2021 from grading only; the records behind each probability keep
them.

## The way to reach it

**Few calls are the obstacle.** The best link has about 60 calls that can carry a probability, so
no curve can be fitted and the probability is the record itself: one slowly moving number per link,
between roughly 60% and 80%. Two things follow, and the rule accepts both:

- **A difference must be told from noise.** "Better than drift" is a test, not a comparison of two
  scores.
- **Calibration can only catch large errors.** With 50 calls at 65%, anything from about 52% to 77%
  right passes. Passing says the stated number is not far off; it does not prove it.

## The rule, fixed before any call is graded

**A link's confidence is honest** if, over the calls that carry a probability (at least 30):

1. **Calibrated:** calls grouped by their probability (under 60%, 60–70%, 70% and over); in each
   group of at least 10, the share right is inside the 95% binomial interval around the group's
   mean probability.
2. **Better than a coin and than drift:** its Brier score is below 0.25 and below the drift
   probability's on the same calls, each with p < 0.05 in a paired sign-flip permutation test on
   the per-call differences (one-sided, `stats.permutation_p`). Below but not significant: "too
   close to tell", which is not honest.
3. **Bands mean 50%:** the share of moves inside their band is inside the 95% binomial interval
   around 50%.

Fewer than 30: too few to tell. The verdict is given with and without COVID; it is honest only if
both are. With up to four checks at 95%, an honest link fails one about one time in six; the rule
accepts that rather than loosen each check. The smoothing, the 20, the groups, the band and the
levels are fixed here; nothing is tuned on the result.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`study.confident_calls(pairs, expected_sign, step)`: pure, like `walk_forward`: each call with its probability, drift probability and band, or none before 20 earlier calls~~ **done** | On 400 planted releases (fixed seed) right on 80% of calls, the stated probability over the last 100 calls averages 0.75–0.85; planted moves land in their band on 40–60% of calls; changing any later release leaves a call's numbers unchanged |
| 2 | ~~`predict --event cpi\|nfp`: per link, a confidence table (calls, mean probability, share right per group, Brier, coin and drift p, band coverage, verdict), with and without COVID, under rung 2's tables; and the hit rate on surprises under and over twice the step, as a measurement only~~ **done** | The "it can fail" planted links below fail their checks; the table printed on real data; rung 2's tables unchanged |
| 3 | ~~`predict --actual X`: each call with its probability and band, e.g. `DXY up 67% (58 calls before), +0.34% to +1.05%`~~ **done**, with the link's confidence verdict beside it | Prints them, or "too few calls so far" |
| 4 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says, per link, whether its confidence is honest, and which check failed |

## How you know it is right

- **No look-ahead.** As in rung 2: a test changes a call's own move and every later release, and
  checks that call's probability, drift probability and band do not change; mutation-checked by
  letting each see the release itself.
- **It can fail.** Planted calls all up, right 55% of the time, on moves that close up 60% of the
  time whatever the surprise: the link must not beat drift. A band built from half the planted
  spread must cover well under 50%.
- **Expected outcome, written down first:** the dollar should pass 2 and 3; the yield is likely to
  fail 2 against drift; CPI's links are too few. (Unchanged from the first draft.)

**Disclosed:** the review of this spec computed the rule's outcomes on real data (before the
significance test in check 2 was added). The fixes it led to are made on design grounds and only
make the rule stricter; the calibration groups were not changed after the outcomes were seen.

## What this step does not do

No new events, markets or expected values. No logistic or isotonic fit, and no probability that
varies with the surprise's size: too few calls. No log of live calls: rung 4. No table.

## Technical details

`study.confident_calls` takes the pairs and the walk-forward's calls, as `walk_forward` does; a
wrapper reads them via `_flow_pairs`. `stats.theil_sen` for the slope; percentiles in plain Python.
The 95% binomial interval needs a tail at any rate, not only a coin's: a small function beside
`stats.binomial_p`. `predict` and `--actual` in `__main__.py`.

## Results

*Filled in by step 4.*
