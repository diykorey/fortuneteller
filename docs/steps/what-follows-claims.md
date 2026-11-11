# What follows a jobless claims report, over spans

> Step 17, part 1e, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1d](what-follows-cpi.md); taken 2026-11-11, the next of "other US flows one at a time".
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when weekly jobless claims come in above what was expected, as expected, or
below, what did each market do over the next day, week and month? It is the Thursday headline
("more people filed for unemployment than expected"); the reader learns the kind, not the number.

Claims' surprise moves nothing on the day ([jobless claims](jobless-claims.md#results)): the
10-year yield follows it at 56%, *unclear*. The question is whether the kind says more than the
number did, over the day, the week and the month.

At the end: `fortuneteller follows --event claims` prints part 1b's table for claims, and a trigger
file may name `claims`.

**Why claims.** It is the only flow left whose every kind can reach 30 graded calls. On the store
of 2026-11-11, `release_kinds` gives claims 703 releases, 206 above, 216 as expected and 281 below.
The other US flows with a surprise rule fall short: PCE has 6 above and 15 below, GDP 14 and 15,
and ISM 39 below, at most 29 graded once ten come before.

## The way to reach it

- **The kind, from the consensus.** This is part 1b's `release_kinds`, unchanged. It reads initial
  claims, FRED's first print, against Nasdaq's consensus. A release is *above* at +5k or more (the
  rule's `noticeable`), *below* at −5k or less, and *as expected* in between. The actual and the
  consensus are whole thousands, so nothing is rounded. The releases run 2013-03-14 … 2026-11-05.
- **Part 1's method, unchanged:** the spans, the non-overlap rule, the base and its cut, the answer
  with direction apart from size, the placebo a span away, the walk-forward and its bars, and the
  chance lines. Claims come out at 08:30 New York and react the same day on every market but
  EUR/USD, which reacts the next day.
- **Weekly releases and the overlap rule.** A week span ends on the close before the next release's
  reaction close, and sharing that close is allowed. So the week keeps nearly every release; a
  holiday that moves a release by a day is the exception. The month keeps about one release in
  five.
- **Shared days are kept**, as for retail sales and for the same reasons. Claims' rule has `alone`,
  and 256 of 706 reports fell on a day with another stored release (most often the Fed's, the jobs
  report's, retail sales' or ISM's; *amended 2026-11-11:* counted in the results, mostly the ECB's,
  then US CPI's, PCE's and retail sales'). Each answer is also given without the shared days, and an
  answer that turns to *can't say* without them is read as "maybe the other release".
- **Triggers.** `TRIGGER_KINDS` gains `claims` with the surprise kinds, so a claims trigger is
  answered with these figures, as the other flows' triggers are.

## The rule, fixed before anything is shown

- Part 1's bars, the kinds above and part 1b's release rule, none of them changed by what the run
  shows.
- **Expected outcome, written first.**
  - Arithmetic, not a finding: on the day, at most 196, 206 and 271 are graded walk-forward; over
    the week nearly as many; over the month about a fifth of each kind is counted, so at most
    about 30 to 45 graded.
  - On the day, on all history: at most one answer on each yield, *down* after *above* and *up*
    after *below*; no answer on a stock index, VIX or gold.
  - Answers in all no more than the chance line `follows` prints, plus 3.
  - Walk-forward: nothing holds on any span, kind or market.
  - *As expected*: no answer.
  - Without the shared days, at most half the answers keep their direction.
- Every existing output is unchanged byte for byte, including the four `follows` tables and the
  answers to the triggers filed so far.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`follows --event claims`; `claims` in `TRIGGER_KINDS`~~ **done** 2026-11-11 (PR #284) | Tests: `follows --event claims` prints a header with the three kinds; a claims trigger is read and answered, not refused. On a copy of the store of 2026-11-11 the header reads `follows: 703 jobless claims reports 2013-03-14 … 2026-11-05: 206 above, 216 as expected, 281 below`, and the other four tables are unchanged |
| 2 | ~~Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row. Give each answer's counts without the shared days~~ **done** 2026-11-11, [below](#results) | Each kind's answers and walk-forward records are recorded against the expected outcome |

*Step 1, 2026-11-11 (PR #284):* on a copy of the store the header reads as written above and 225
cells print; the Fed's, the jobs report's, retail sales' and CPI's tables are byte for byte the
ones before.

## Results

Measured 2026-11-11 on a copy of the store: 703 reports, 206 above, 216 as expected, 281 below;
254 of them on a day with another stored release (73 above, 75 as expected, 106 below): an ECB
decision on 109, US CPI on 39, PCE on 38, retail sales on 36, GDP on 29, ISM on 22, the euro area's
flash on 17, the jobs report and the Fed on 5 each (a day can hold two).

**Nothing holds walk-forward.** The nearest are on the day: the 10-year yield down after *above*,
right on 20 of 37 graded (54%), and the 5-year yield up after *below*, 22 of 51 (43%).

**On all history, 8 answers**, against about 6.8 by chance for the 225 cells. None is marked by the
placebo. The yields' day answers go opposite ways for opposite kinds, so they are read as the kind:

| Kind | Span | Market | Up / same / down | Answer | Chance | Without the shared days |
| --- | --- | --- | --- | --- | --- | --- |
| above | day | UST10Y / ZN | 51 / 70 / 85 | down | 0.0017 | *can't say*, 34 / 47 / 52 |
| above | day | UST5Y / ZF | 51 / 78 / 77 | down | 0.0036 | *can't say*, 35 / 52 / 46 |
| as expected | day | XLU | 92 / 74 / 50 | up | 0.0094 | *can't say*, 55 / 53 / 33 |
| below | day | UST10Y / ZN | 116 / 84 / 81 | up | 0.0097 | *can't say*, 67 / 55 / 53 |
| below | day | UST5Y / ZF | 122 / 85 / 74 | up | 0.0025 | *can't say*, 73 / 56 / 46 |
| below | week | UST10Y / ZN | 108 / 62 / 69 | up | 0.0098 | *can't say*, 72 / 42 / 45 |
| below | week | UST5Y / ZF | 109 / 67 / 63 | up | 0.0056 | up, 72 / 49 / 38 |
| below | week | UGA | 77 / 98 / 65 | about the same | 0.0090 | about the same, 53 / 69 / 37 |

Without the shared days two new answers appear, VIX *about the same* on the day after *above* and
the dollar index *up* on the day after *below*; neither holds walk-forward. Nothing answers over the
month.

**Against the expected outcome:**

- The arithmetic: the day, **right**. The week, **wrong**: it leaves out 34 to 41 of each kind,
  about one in six, not "nearly none". A market holiday inside the Thursday-to-Wednesday window
  leaves the span a close short, so its fifth close lands on the next release's reaction close:
  the S&P 500 has 127 weekday holidays in the range against 114 week spans left out, while only 25
  releases moved off a Thursday. The month counts 41 above, 43 as expected and 57 below, about one in five: **right**.
- At most one day answer on each yield, *down* after *above* and *up* after *below*: the directions
  **right**, the count **wrong**, two on each, one per kind.
- No answer on a stock index, VIX or gold: **right**.
- Answers no more than the chance line plus 3, 9.8: **right**, 8.
- Nothing holds: **right**.
- *As expected* answers nothing: **wrong**, utilities rise on the day, and turn to *can't say*
  without the shared days.
- Without the shared days, at most half keep their direction: **right**, 2 of 8.

**What it says.** Jobless claims by kind repeat what the number said: the yields lean the expected
way on the day, and the lean is mostly the days claims share with another release, an ECB
decision most often, then US CPI, PCE or retail sales. A claims trigger will be answered *can't say* almost everywhere. No new call.
