# Rung 2 — predict the next release

> Step 3 of the [Roadmap](../roadmap.md#next-steps-in-order)'s next steps, rung 2 of its feature
> ladder. It tests the [Legend](../legend.md)'s third claim and follows its step template. Terms
> are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when a CPI or jobs report lands, can we say which way the yield and the dollar
will close that day — and be right on releases we had not yet seen?

The [free consensus](free-consensus.md#results) found four links that pass against a free, live
expected value: the 10-year yield and the dollar on jobs reports, and on core CPI. But they were
found by looking at all of 2008–2026 at once. The Legend's third claim is that such a link holds
for the **next** release, not only for the history it was found in. Until that is measured, every
number so far is a description, not a predictor.

At the end: a `predict` command that (1) replays every release since 2008 as if it were the next
one, and grades the predictions that history would have allowed, and (2) given a new release's
actual, prints the prediction for that day's close.

## What a prediction is

At a release, the surprise is the actual minus Nasdaq's consensus. If it is noticeable (0.1pp for
CPI, 50k for payrolls) and the link is **open**, the prediction is the link's expected sign times
the surprise's sign: a hot CPI print says the yield closes up that day. Smaller surprises, and
closed links, get no prediction — silence, not a guess.

A link is open at a release if it passes the same test as everywhere else (rank correlation in the
expected direction, p < 0.01, right on at least 60% of noticeable surprises) **using only the
releases before it**. So each link earns the right to predict, and can lose it.

## The way to reach it

**Selection bias is the obstacle.** The four links were chosen because they pass on the whole
history; grading them on that same history would be circular. Two things handle it:

- **Walk-forward.** At each release, the gate sees only earlier releases; the prediction is then
  graded against that day's move, which the gate never saw.
- **Every candidate, not the winners.** All six links with an agreed direction are replayed — core
  CPI: S&P 500 down, yield up, dollar up, VIX up; jobs report: yield up, dollar up — and each opens
  or not on its own history. The four that passed in-sample get no head start.

The move is from the last close before the release to the first close after it, as everywhere
else. It contains the first reaction itself, so a prediction made at 08:30 is not a trade; it says
whether the link is stable enough to warn on.

## The rule, fixed before any prediction is graded

- **Claim 3 holds for a link** if, over the releases where it predicted, it was right at least 60%
  of the time **and** a one-sided binomial test against 50% gives p < 0.01, with at least 30
  predictions. Fewer than 30: too few to tell.
- **The baseline it must beat:** always predicting the expected sign's direction, regardless of the
  surprise, on the same releases. Reported beside each hit rate.
- With and without COVID (March 2020 – April 2021 graded or not), as everywhere.
- The expected signs, cut-offs, test and bars are the ones already fixed; nothing is tuned here.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`study.walk_forward`: per link, at each release, open or not on earlier releases; the prediction; graded~~ **done** | A planted link (moves follow 80% of surprises) opens and grades near 80%; a random one rarely opens and grades near 50%; changing every later release leaves a release's prediction unchanged |
| 2 | ~~`predict --event cpi\|nfp`: per link, predictions issued, right, hit rate, p, the baseline, the verdict, with and without COVID~~ **done** | The table printed on real data; no other command's output changes |
| 3 | `predict --event cpi\|nfp --actual X`: the next release's consensus from the calendars, the surprise, a line per open link | Prints the prediction, or silence with the reason (no consensus yet, small surprise, link closed) |
| 4 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says, per link, whether claim 3 holds, with and without COVID |

## How you know it is right

- **No look-ahead.** A test changes every surprise and move after a release and checks that
  release's gate and prediction do not change; mutation-checked by letting the gate see the
  release itself.
- **It can fail.** A planted link with no relation to its surprise must stay closed or grade near
  50%; one that follows 80% of surprises must open and grade near 80%.
- **The baseline.** A hit rate that does not beat "always the expected direction" says the link
  predicts the market's drift, not the surprise; the result says so.

## What this step does not do

No probabilities or move sizes: rung 3. No log of live predictions or their later grading: rung 4.
No fetching of the actual when it lands — it is typed in: rung 5. No delivery. No Fed: it has no
expected value. No new expected values, markets or events; no intraday prices.

## Technical details

`study.walk_forward(flow, instrument)` reads the consensus surprises and moves as
`study.surprise_pairs` does, oldest first, and reuses `track_pairs` for the gate. The gate runs
about 220 times per link, so it draws 2,000 permutations instead of 10,000 (p < 0.01 still
resolves; fixed seed). `stats.binomial_p` for the grade, plain Python. The CLI command in
`__main__.py`; the next release's consensus via `expectations.fetch_calendars`. No table.

## Results

*Filled in by step 4.*
