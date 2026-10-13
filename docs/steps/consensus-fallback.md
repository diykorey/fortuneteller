# TradingView's forecast where Nasdaq has none

> A fix inside [rung 4](rung-4-keep-score.md), decided 2026-10-13. It changes where the
> [free consensus](free-consensus.md) comes from when Nasdaq's calendar has no row, nothing else.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** a release should not be lost because one calendar left it out.

On 2026-10-13, the day before the first live CPI release, Nasdaq's calendar had no CPI row for the
week, and `predict --actual` refuses without Nasdaq's consensus. TradingView listed it, with a
forecast. A release with no consensus gets no call and is missed for good: the log allows no
backfill.

At the end: where Nasdaq has no row, `predict --actual` and `load-surprises` take TradingView's
forecast, and say so.

## Measured first

On every stored release from 2008, TradingView's forecast beside the Nasdaq consensus we stored
(2026-10-13):

| Measure | Both listed | Same value | Same call | Direction flips |
| --- | --- | --- | --- | --- |
| Core CPI | 159 | 153 | 159 | 0 |
| Headline CPI | 159 | 147 | 154 | 0 |
| Payrolls | 162 | 107 | 162 | 0 |
| Retail sales | 156 | 125 | 153 | 0 |
| Core PCE | 143 | 136 | 140 | 0 |
| GDP | 49 | 40 | 44 | 0 |

"Same call" counts releases where the surprise falls on the same side of the flow's step under
both. Where it does not, it is under the step under one of them; no call ever turns around.
TradingView lists none of these before 2013, and from 2015 every one but two GDP releases (2019,
2025).

Releases Nasdaq has no row for at all, where TradingView has a forecast: retail sales 7
(2019-10-16 to 2022-10-14), core PCE 6 (2019-06-28 to 2022-07-29), GDP 1 (2020-01-30), CPI and
payrolls none. Six more have a TradingView forecast and no stored Nasdaq consensus for another
reason: four unreadable (in `UNREADABLE_CONSENSUS`), and core CPI 2014-11-20 and GDP 2017-10-27,
where the calendars differ past the gap.

## The rule, fixed before the replay is run again

- **Only where Nasdaq has no row.** TradingView's forecast fills in when Nasdaq's calendar has no
  row of the measure's name carrying a consensus on the release day. A release left out as
  unreadable, or because the two calendars differ past the gap, stays out: those were decided on a
  check, and a fallback would quietly undo it.
- **The same in the replay and live.** The stored surprise and the live call use one rule, so
  `score` grades a fallback call on the surprise it was made from. *Added in step 1, 2026-10-13,
  without changing which releases count:* unless Nasdaq adds its row before the release is loaded;
  then the stored surprise is Nasdaq's, as for any release. The 14 releases above join the
  replay; CPI's and the jobs report's do not change.
- **Unchecked, and named.** A fallback value has no second calendar to check it. `predict` prints
  "TradingView's forecast (Nasdaq has none)", and `load-surprises` lists the releases filled in,
  beside those left out.
- **Known the evening before**, as Nasdaq's: neither records when its forecast was final.
- **From the merge on.** A release missed before this is merged stays missed.
- **Every verdict re-measured and reported**, whatever it shows: each link's rung 2 record and
  verdict and rung 3 checks before and after, on the 14 releases added. Which releases count is
  not changed after seeing the effect.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The fallback in `expectations.match_consensus` and `next_consensus`; `predict` and `load-surprises` name it; schema doc updated~~ **done** | A planted release with a TradingView forecast and no Nasdaq row is called by `predict --actual`, stored by `load-surprises` and graded by `score`; an unreadable or gap-left-out release stays out |
| 2 | ~~Results: every link's verdict before and after~~ **done** | The before-and-after table here and in [`mvp-results.md`](../mvp-results.md) |

## Results

Measured 2026-10-13: `predict` and `surprise` for the three flows, on the stored history before
the fallback and after it. Of the 14 releases, 5 of retail sales' enter its tables (2020-09-16 and
2020-12-16 share a day with CPI and stay out), all 6 of core PCE's and GDP's one.

| Flow | Link | Before | After |
| --- | --- | --- | --- |
| Retail sales | yield, walk-forward | 50 of 78, p 0.008, **holds**; without COVID 43 of 67, p 0.014 | 51 of 79, p 0.006, **holds**; without COVID 44 of 68, p 0.0103, still just over 0.01 |
| Retail sales | yield, confidence | Brier 0.249 (p 0.48); without COVID 0.252, worse than a coin: **not honest** | 0.247 (p 0.44); without COVID 0.249 (p 0.48): **too close to tell** |
| Retail sales | yield, surprise | 0.26, right 67% (97), tracks | 0.26, right 67% (98), tracks |
| Retail sales | dollar | 3 calls, too few; surprise doesn't track | 4 calls, too few; doesn't track |
| Core PCE | every link | no calls; no surprise verdict changes | the same |
| GDP | every link | no calls; no surprise verdict changes | the same |

Every walk-forward verdict and every surprise verdict with an expected sign stands. One context row
moves: the S&P 500 on retail days (no expected sign) goes from doesn't to unclear (p 0.013 to 0.007).

**Retail sales' yield confidence moves from "not honest" to "too close to tell".** One more call
takes its Brier score without COVID from just over a coin's 0.25 to just under it; neither beats a
coin with p under 0.05. The probabilities are no more trustworthy than before: the change is the
width of one call, and it is reported as the rule fixed in advance requires.

## What this does not do

No change to the source name: the values stay under `nasdaq_consensus`, the fallback named in the
schema doc. No TradingView-first consensus, no third calendar, no consensus before 2008.
