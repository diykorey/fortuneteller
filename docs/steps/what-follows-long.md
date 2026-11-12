# What follows a Fed decision, over a quarter and a year

> Step 17, part 2, of the [Roadmap](../roadmap.md#next-steps-in-order), set aside 2026-11-10 and
> taken 2026-11-12 after [part 1f](what-follows-ecb.md). Terms are in the
> [Glossary](../glossary.md): *span*, *base rate*, *kind*, *cycle*, the four answers.

## The goal

**In plain words:** when the Fed cuts, holds or hikes, what did each market do over the next quarter
and the next year? It is [part 1](what-follows.md) over the two spans the legend names last. The
catch: one cut cycle is several cuts in a row, so counting each cut as an event counts one story
many times. Part 2 counts each cycle once, as well as each decision, and an answer stands only if
both give it.

At the end: `fortuneteller follows --long` prints part 1's table for the Fed over a quarter and a
year, with a column for the answer counting each cycle once.

## The way to reach it

- **Part 1's method, unchanged:** the kinds from FRED's target rate, the non-overlap rule, the
  holes (`MAX_CLOSE_GAP_DAYS`), the base and its cut, the answer, the walk-forward and its bars,
  the chance lines. Only the spans are new: a quarter of 63 closes and a year of 252
  (`LONG_SPANS`). The placebo moves each key close by the span's length, 63 or 252, as part 1's
  rule already does for any span longer than 10.
- **A cycle**, from the decisions in date order, before any market is read:
  - a *cut cycle* runs from a cut to the last cut before the next hike; holds between cuts do not
    end it. A *hike cycle* is the same with the kinds swapped;
  - a *run of holds* is consecutive holds, ended by any cut or hike.
  On the store of 2026-11-12: 6 cut cycles, 7 hike cycles (1997 and 2026 a single hike each) and
  35 runs of holds.
- **The answer counting each cycle once.** For each cell, the first kept decision of each cycle
  among its kept decisions is answered again by part 1's rule (`span_answer`, the same base and
  cut). The cell's answer stands only if this one is the same. Otherwise the cell prints *one cycle*,
  or *too few cycles* with fewer than 10. The walk-forward is part 1's, on every kept decision. A
  cell *holds* only if its answer also stands counting each cycle once.
- **`follows --long`** prints the quarter and the year for `fomc` only. With any other event it
  refuses with "the quarter and the year are measured on the Fed's decisions only" and exits 1.
  `SPANS` is unchanged, so `follows` without the flag, `--after-the-day`, `triggers`, the trigger
  log and the scoreboard print what they print today.

## The rule, fixed before anything is shown

- Part 1's bars, the spans and the cycles above, none of them changed by what the run shows.
- **Expected outcome, written first.** The counts are from kept decisions only, read before any
  move was measured:
  - Arithmetic, not a finding: nothing can hold. Cuts and hikes have at most 6 cycles on any
    market, under 10, so their answers are at best *too few cycles*. Holds keep at most 71 on the
    quarter but come from at most 25 runs. On the year they keep at most 19, so at most 9 are
    graded.
  - The DAX, the Euro STOXX 50, the FTSE 100 and the STOXX 600 keep at most one decision a year:
    Yahoo's European histories have a gap of more than four days nearly every year (Christmas), so
    almost every 252-close span holds a hole. Their year cells are *too few*. Part 1's gap rule is
    not changed here.
  - On all history: no more answers than the chance line plus 2. Stocks *up* a year after a hold,
    marked *the period* by the placebo, since a year either side lands in the same bull run. Gold
    *up* a quarter after a cut, *too few cycles*. Nothing else.
- Every existing output is unchanged byte for byte, including the six `follows` tables, the
  trigger log and the scoreboard.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`fed_cycles`, `LONG_SPANS` and the cycle column in `study.py`; `follows --long`~~ **done** 2026-11-12 (PR #294) | Tests: the cycles of a cut, hold, cut, hike, hike, hold, hold sequence are one cut cycle, one hike cycle and two runs of holds; an answer from three cuts of one cycle, ten times over, prints *too few cycles*; an answer the cycles repeat stands; `follows --long --event nfp` exits 1. On a copy of the store the run prints 150 cells, and the other outputs are unchanged |
| 2 | ~~The results, here and in [MVP results](../mvp-results.md); the expected outcome checked; roadmap row 17~~ **done** 2026-11-12, [below](#results) | Each kind's answers, cycle column and walk-forward recorded against the expected outcome |

*Step 1, 2026-11-12 (PR #294):* on a copy of the store `follows --long` prints the 150 cells and
the chance line in about 25 seconds. The twelve `follows` tables, each flow with and without
`--after-the-day`, are byte for byte `main`'s. The span column widens to fit *quarter* only under
`--long`.

## Results

Measured 2026-11-12 on a copy of the store, the target rate from FRED that day: 276 decisions,
1994-02-04 … 2026-10-28, 40 cuts, 184 holds and 52 hikes.

**Nothing holds, and no answer stands counting each cycle once.** No cell reaches 30 graded
walk-forward; the most is 5, gold over a quarter after a hold. On all history one cell of 150
answers, against about 2.0 by chance: over a quarter after a hike, the S&P 500 moved *about the
same* 13 times in 21, against a base of 33% (chance 0.0068). Those 21 hikes come from 6 cycles, so
it is *too few cycles*. Every other answered cell is *can't say*: 67 of them.

The holds come closest to counting: 71 kept on the quarter from 25 runs, 19 on the year from 13.
Stocks rose a year after 10 of 19 holds and fell after 2. But the year rises as often anyway (a
base of 56% up and 11% down), so that is *can't say* (chance 0.46).

**Against the expected outcome:**

- Nothing can hold: **right**, every cell *too few* walk-forward.
- The European indices' year *too few*: **right**. The DAX and the Euro STOXX 50 keep one hold each,
  the FTSE 100 and the STOXX 600 none, 116 to 178 holes a cell.
- No more answers than chance plus 2: **right**, one against 2.0.
- Stocks *up* a year after a hold, *the period*: **wrong**, *can't say*.
- Gold *up* a quarter after a cut, *too few cycles*: **wrong** as an answer. Only 9 cuts are kept,
  under 10, so *too few*. It is 4 cycles, as expected.
- Nothing else: **wrong**, the S&P 500 *about the same* a quarter after a hike, *too few cycles*.
- Every existing output unchanged: **right**.

**What it says.** Over a quarter or a year, a Fed decision read as cut, hold or hike tells nothing
about what these markets did: the year rises in most years whatever the Fed did, and its cuts and
hikes come in too few cycles to count. A trigger on a quarter or a year would be answered
*can't say* everywhere. No new call.

## What this part does not do

No other flow: the ECB and the surprise flows over a quarter and a year wait, one at a time, for
this part's result. No trigger on a quarter or a year, which would take a year to grade. No change
to the gap rule, the placebo or any bar.

## Technical details

- `study.py`: `LONG_SPANS = {"quarter": 63, "year": 252}`; `fed_cycles(kinds in date order) ->
  list[int]`, a cycle number per decision; `follow_decisions(..., spans=SPANS)` and
  `follow_market` take the spans and the cycles. `Follow` gains `by_cycle`, the answer counting
  each cycle once, or `None` without `--long`.
- `__main__.py`: `follows --long`. The table adds a `cycles` column after `placebo`: the answer
  counting each cycle once, its count of cycles, and *one cycle* or *too few cycles* where it
  differs.
- Tests in `tests/test_what_follows.py`, `tmp_db`, given/when/then.
- **Docs:** this spec, the glossary (*cycle*), `docs/status.md`, the roadmap's row 17.
