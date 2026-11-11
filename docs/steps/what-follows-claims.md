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
  report's, retail sales' or ISM's). Each answer is also given without the shared days, and an
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
| 1 | `follows --event claims`; `claims` in `TRIGGER_KINDS` | Tests: `follows --event claims` prints a header with the three kinds; a claims trigger is read and answered, not refused. On a copy of the store of 2026-11-11 the header reads `follows: 703 jobless claims reports 2013-03-14 … 2026-11-05: 206 above, 216 as expected, 281 below`, and the other four tables are unchanged |
| 2 | Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row. Give each answer's counts without the shared days | Each kind's answers and walk-forward records are recorded against the expected outcome |
