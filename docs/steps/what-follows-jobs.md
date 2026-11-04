# What follows a jobs report, over spans

> Step 17, part 1b, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1](what-follows.md); chosen 2026-11-04 before part 2, whose quarter and year would answer
> few Fed cycles (about ten cuts and hikes cycles each since 1994). Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** when the jobs report comes in above what was expected, as expected, or below,
what did each market do over the next day, week and month? It is the headline a news reader
sees on the first Friday of a month ("the economy added more jobs than expected").

Part 1 found nothing for the Fed's decisions. The jobs report is the one release whose surprise
already holds on the day ([rung 2](rung-2-predict.md)); this part asks whether a reader can be
told so by its kind alone, and whether it lasts a week or a month.

At the end: `fortuneteller follows --event nfp` prints part 1's table for the jobs report.

## The way to reach it

- **The kind, from the consensus.** The payrolls surprise against Nasdaq's consensus, as stored
  by `load-surprises`: *above* when it is at least the rule's noticeable 50k, *below* when at most
  −50k, *as expected* between. On the store of 2026-11-04: 222 reports since 2008-03, 68 above,
  104 as expected, 50 below. A report with no consensus has no kind.
- **Everything else is part 1's,** unchanged: the spans, the non-overlap rule (a month span runs
  about as long as the gap to the next report, so about half of the month is left out), the
  base and its cut, the answer with direction apart from size, the placebo a span away, the
  walk-forward and its bars, the chance line. Only the kinds and their names differ.

## The rule, fixed before anything is shown

- Part 1's bars and the kinds above, unchanged by what the run shows.
- **Expected outcome, written first.**
  - On the day, *above* answers the 10-year and 5-year yields and the dollar index *up*, and
    EUR/USD *down*, on all history; *below* the reverse, fewer. Walk-forward, *above* holds on the
    5-year yield on the day at most; *below* (at most 40 graded) holds nothing.
  - Over a week, the day's answers fade to *can't say* except the 5-year yield after *above*;
    over a month, nothing answers beyond chance.
  - *As expected* answers nothing, on any span.
  - On all history, answers well above chance's count on the day, about chance's over the month.
- Every existing output, part 1's `follows` included, is unchanged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The kinds read from stored surprises; `follows --event nfp` | The tests below pass; the run on a copy of the store prints 144 cells and both chance lines; `follows` for the Fed prints what it printed before |
| 2 | Results here and in [MVP results](../mvp-results.md), the expected outcome checked, the roadmap row | Each kind's answers and walk-forward records recorded against the expected outcome |

## How you know it is right

- A surprise of +50k is *above*, +49.9k *as expected*, −50k *below*; a report with no consensus
  surprise is left out.
- The Fed's table is the same as before the change, cell by cell, on made-up decisions.
- `follows --event nfp` prints the header with the kinds' counts and a row; with no surprises
  stored it says to run `load-surprises` and exits 1.

## What this part does not do

No other release (each its own part, one at a time), no quarter or year (part 2), no page, no
trigger file (step 18). Nothing is stored.

## Technical details

- `study.py`: `follow_market(decisions, closes, unit, c, kinds)`, the kinds passed in;
  `release_kinds(flow, con)` from `surprises` (the rule's `predicted_from` baseline, its first
  combination's measure, its `noticeable`), `ABOVE`, `AS_EXPECTED`, `BELOW`;
  `follow_decisions(flow, kinds, order, con)` for any flow.
- `__main__.py`: `follows --event` choices `fomc` and `nfp`; FRED is read for the Fed only.
- Tests in `tests/test_what_follows.py`.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17, `docs/status.md`.
