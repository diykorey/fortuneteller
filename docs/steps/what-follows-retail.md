# What follows a retail sales release, over spans

> Step 17, part 1c, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1b](what-follows-jobs.md); taken 2026-11-04 on the owner's "another release by kind: CPI or
> retail sales, using the same method". Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when retail sales come in above what was expected, as expected, or below,
what did each market do over the next day, week and month? It is the mid-month headline ("shoppers
spent more than expected"); the reader learns the kind, not the number.

Retail sales' surprise holds on the day on two markets, the 10-year and the 5-year yields
([step 4](step-4-more-events.md), [more outcomes](more-outcomes.md)). As for the jobs report, the
day cells for *above* and *below* are a check against those links; the week, the month and *as
expected* are the question.

At the end: `fortuneteller follows --event retail` prints part 1b's table for retail sales.

**Why retail sales before CPI.** CPI has 25 releases above the consensus and 36 below, on the
store of 2026-11-04. The walk-forward needs ten earlier ones before it answers, so *above* would
have at most 15 graded, and *below* 26. Neither could reach 30, and only *as expected* could
hold. Retail sales has 51 above, 109 as expected and 62 below, so every kind can reach 30 on the
day.

## The way to reach it

- **The kind, from the consensus.** This is part 1b's `release_kinds`, unchanged. It reads the
  `surprises` row on the rule's first measure, headline retail sales month on month, against
  Nasdaq's consensus:
  - *above* at +0.3pp or more (the rule's `noticeable`);
  - *below* at −0.3pp or less;
  - *as expected* in between.

  On the store of 2026-11-04 that gives 222 releases, 2008-03-13 … 2026-10-15: 51 above, 109 as
  expected and 62 below. The actual is the first print; revisions are not read.
- **Part 1's method, unchanged.** The release rule from part 1b is unchanged too. Retail sales is
  released at 08:30 New York, like the jobs report. It reacts the same day on every market except
  EUR/USD, which reacts the next day. Over the month, a span runs about to the next release, as it
  did for the jobs report.
- **Shared days are kept.** Step 4's rule for retail sales has `alone`: a release on a day that
  holds another flow's release is left out of step 4's tables. That covers 48 of 222 releases,
  most of them on a CPI day or an ECB day.

  `follows` keeps them, as part 1b kept the jobs report's 31. Two reasons:
  - a news reader hears of the release on that day either way;
  - leaving them out would cut *above* to 39, and with ten needed before the walk-forward answers,
    at most 29 would be graded, short of 30.

  As a reading aid, the results give each answer's counts without the shared days, the way part
  1b gave them without 2020–21. Fixed before measuring: where an answer turns to *can't say*
  without the shared days, it is read as "maybe the other release".

## The rule, fixed before anything is shown

- Part 1's bars, the kinds above, and part 1b's release rule, none of them changed by what the run
  shows.
- **Expected outcome, written first.**
  - Arithmetic, not a finding:
    - over the month, about half of each kind is left out for overlap, so neither *above* (about
      25 counted) nor *below* (about 31) can hold there;
    - on the day, *above* has at most 41 graded.
  - On the day, on all history:
    - *above* answers both yields *up*;
    - *below* answers at least one yield *down*;
    - the dollar index and EUR/USD answer for neither kind (retail sales' dollar never held);
    - at least 3 answers on the two yields, against about 4.3 by chance across the table's 144
      cells.
  - Walk-forward on the day: *above* holds on the 5-year yield; nothing else holds anywhere.
  - Over the week, at most one answer per kind. Over the month, at most 2 answers in all.
  - *As expected*: VIX *down* on the day, read as the release, as on a jobs report; nothing else.
  - Without the shared days, every answer on the yields keeps its direction.
- Every existing output is unchanged byte for byte, including the Fed's and the jobs report's
  `follows` tables.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `follows --event retail` | The tests below pass. On a copy of the store, the header reads `follows: 222 retail sales releases 2008-03-13 … 2026-10-15: 51 above, 109 as expected, 62 below`, and 144 cells print |
| 2 | Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row. Add each answer's counts without the shared days, as a reading aid | Each kind's answers, release marks and walk-forward records are recorded against the expected outcome |

## How you know it is right

- With no key set, given three releases at +0.4, 0 and −0.4 and one market's closes,
  `follows --event retail` exits 0 and prints the header for them and an *above* row.
- With a surprise of +0.3 the kind is *above*; with +0.29 it is *as expected*. This catches a
  noticeable threshold taken from the wrong rule.
- The Fed's and the jobs report's `follows` tests pass unchanged.

## What this part does not do

- No CPI: its own part, whose only kind that could hold is *as expected*.
- No quarter or year (part 2), no trigger file (step 18).
- Nothing is stored.
- No change to step 4's shared-day rule.
- Releases are not independent; the chance says more than it should, as in part 1.

## Technical details

- **`__main__.py`:** `FOLLOWS_NOUNS` gains `"retail": "retail sales releases"`. `--event`'s
  choices follow from it.
- **`study.py`:** no change. `release_kinds` already reads the flow's own rule.
- **Tests:** in `tests/test_what_follows.py`.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17, and
  `docs/status.md`.
