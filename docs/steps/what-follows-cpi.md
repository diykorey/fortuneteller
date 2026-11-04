# What follows a CPI release, over spans

> Step 17, part 1d, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1c](what-follows-retail.md); taken 2026-11-04 on the owner's "cpi by kind". Terms are in
> the [Glossary](../glossary.md).

## The goal

**In plain words:** when core inflation comes in hotter than expected, as expected, or cooler,
what did each market do over the next day, week and month? It is the mid-month headline ("core
prices rose 0.3%, more than the 0.2% expected"); the reader learns the kind, not the number.

CPI is the release the project began with ([MVP step 4](step-4-more-events.md)). Its surprise
moves the 10-year yield and the dollar on the day, and both are called live. As for the jobs
report, the day cells for *above* and *below* are a check against those links; the week, the
month and *as expected* are the question.

At the end: `fortuneteller follows --event cpi` prints part 1b's table for CPI.

## The way to reach it

- **The kind, from the headline as published.** The `surprises` row is core CPI month on month
  against Nasdaq's consensus, the rule's first measure and its `predicted_from`. The stored actual
  is the change computed from the index levels, unrounded (0.281 for August 2024). The Bureau of
  Labor Statistics publishes it rounded to 0.1 (0.3), and so does every headline. The consensus is
  given to 0.1 too.

  So the actual is rounded to one decimal before it is set against the consensus:
  - *above* if the rounded actual is 0.1 or more over the consensus;
  - *below* if it is 0.1 or more under;
  - *as expected* if the two are equal.

  On six releases checked against the published figures (2022-09, 2023-03, 2024-02, 2024-09,
  2024-12, 2025-01), the rounded actual equals the published one each time. On the store every
  consensus is on the 0.1 grid, so the three kinds cover every case. 26 of the 221 actuals lie
  within 0.005 of a rounding line (x.x5), where the computed change could round apart from the
  Bureau's own figure; the results give each answer's counts without them too, and an answer that turns to
  *can't say* without them is read as "maybe the rounding". A tie is rounded half up, as the
  Bureau does.
- **What the rounding changes.** On the store of 2026-11-04 there are 221 releases, 2008-02-20 …
  2026-10-14:
  - read from the headline: 61 above, 82 as expected, 78 below;
  - read unrounded at ±0.1: 25 above, 160 as expected, 36 below.

  78 releases change kind. August 2024 is one: the headline read "hotter than expected", and
  unrounded it is *as expected*. The reader hears the headline, and markets quote it. Unrounded, *above* could have at most 15 graded and could not hold. That is
  why this was looked at, and the reason is stated here. The headline is the kind either way.
- **Only this part reads the headline.** Part 1c's retail sales kinds were read unrounded and
  measured, and they stand; [Precision](../precision.md) records it, with its trigger. Step 4's
  links and the live calls keep the unrounded surprise.
- **Part 1's method and part 1b's release rule, unchanged.** CPI is released at 08:30 New York and
  reacts as the jobs report does.
- **Shared days.** CPI's rule has no `alone`, so there is nothing to set aside. 48 releases share
  their day with another release, 22 of them with retail sales. As in part 1c, the results give
  each answer's counts without the shared days. An answer that turns to *can't say* without them
  is read as "maybe the other release". If a hold's calls on lone days are right under 60%, the
  hold is read as "CPI or a same-day release".

## The rule, fixed before anything is shown

- Part 1's bars, the kinds above, and part 1b's release rule, none of them changed by what the run
  shows.
- **Expected outcome, written first.**
  - Arithmetic: over the month about a fifth of each kind is left out for overlap, as for retail
    sales, so *above* and *below* can reach 30 graded there.
  - On the day, on all history:
    - *above* answers the 10-year and 5-year yields *up* and the S&P 500 *down*, each checked on
      its own;
    - *below* answers at least two of their reverses;
    - so at least 5 answers on these six day cells, against about 0.2 by chance (4.3 for the
      table's 144 cells).
  - Walk-forward on the day: *above* holds on the 5-year yield; nothing else holds anywhere.
  - Over the week at most 2 answers in all, and over the month at most 2.
  - *As expected*: no answer except VIX *down* on the day, which would be the release.
  - Without the shared days, every answer on the yields keeps its direction; one that turns to
    *can't say* counts as not keeping it.
- Every existing output is unchanged byte for byte, including the other `follows` tables, step 4's
  tables and the live calls.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`follows --event cpi`, its kinds read from the headline~~ **done** 2026-11-04 (PR #248) | The tests below pass. On a copy of the store, the header reads `follows: 221 CPI releases 2008-02-20 … 2026-10-14: 61 above, 82 as expected, 78 below`, and 144 cells print |
| 2 | ~~Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row. Add each answer's counts without the shared days~~ **done** 2026-11-04, [below](#results) | Each kind's answers, release marks and walk-forward records are recorded against the expected outcome |

*Step 1, 2026-11-04 (PR #248):* on a copy of the store the header reads as written above and 144
cells print; the jobs report's and retail sales' tables are byte for byte the ones recorded.

## Results

Measured 2026-11-04 on a copy of the store: 221 releases, 61 above, 82 as expected, 78 below,
read from the headline.

**Nothing holds walk-forward, and little is graded.** The walk-forward calls a release only when
the earlier ones already answered, and they rarely did: no cell reaches 30 graded, the most is 19.

**On all history, 6 answers**, against about 4.3 by chance for the 144 cells, all after *below*.
None is marked by the placebo, and neither *above* nor *as expected* gives the same answer, so on
the release rule each is the kind. Every one turns to *can't say* without the 48 shared days, so
by the rule fixed first each is read as "maybe the other release":

| Kind | Span | Market | Up / same / down | Answer | Chance | Without the shared days | Without the 26 near the line |
| --- | --- | --- | --- | --- | --- | --- | --- |
| below | day | DXY | 17 / 23 / 38 | down | 0.0016 | *can't say*, 15 / 18 / 29 | down |
| below | day | GC / XAU | 41 / 23 / 14 | up | 0.0011 | *can't say*, 32 / 17 / 13 | up |
| below | day | UST5Y / ZF | 20 / 19 / 39 | down | 0.0057 | *can't say*, 16 / 15 / 31 | down |
| below | day | SXXP | 33 / 31 / 12 | up | 0.0059 | *can't say*, 27 / 22 / 12 | *can't say* |
| below | week | VIX | 14 / 29 / 35 | down | 0.0087 | *can't say*, 12 / 20 / 30 | down |
| below | week | BTC | 27 / 16 / 8 | up | 0.0080 | *can't say*, 24 / 11 / 7 | up |

Without the shared days each loses about a fifth of its releases, and its chance rises to between
0.011 and 0.037, just over the bar; the leanings stay the same way. The 48 are shared with retail
sales (22), the Fed (20) and the ECB (8).

After *above*, the yields lean up but do not answer: the 5-year 31 / 13 / 17 (chance 0.04), the
10-year 29 / 13 / 19 (0.09); the S&P 500 says nothing (25 / 16 / 20). Nothing answers over the
month. Left out for overlap over the month: 15 of 61 *above* and 23 of 78 *below* on the 10-year
yield.

**Against the expected outcome, written first:**

- Arithmetic: about a fifth left out over the month: **wrong**, a quarter to 30% (15 of 61, 23 of
  78); *above* and *below* can still reach 30 there (45 and 54 counted), but nothing answers.
- On the day, *above* answers the 10-year yield *up*: **wrong**; the 5-year *up*: **wrong**; the
  S&P 500 *down*: **wrong**. *Below* answers at least two of their reverses: **wrong**, one (the
  5-year). At least 5 answers on these six cells: **wrong**, 1.
- Walk-forward, *above* holds on the 5-year yield: **wrong**. Nothing else holds: **right**.
- Over the week at most 2 answers: **right** (2); over the month at most 2: **right** (none).
- *As expected* answers nothing but VIX: **right**, nothing at all (VIX 0.0499).
- Without the shared days the yields keep their direction: **wrong**, the 5-year turns to *can't
  say*.

**What it means.** Read from the headline the way a reader hears it, CPI by kind says little. A
cooler-than-expected core print leans the dollar and the 5-year yield down and gold up on the day,
the way a weaker economy would, but every one of those rests partly on the days CPI shares with
retail sales or the Fed. The hot print, the one in the news, gives no answer at all: the yields
lean up and stocks do nothing in particular. Step 4's link, the yield following the size of the
surprise, is a different question and stands. Nothing here can be told to a reader with a record.

## How you know it is right

- These CPI kinds come out as follows:
  - actual 0.281 against 0.2 is *above*;
  - 0.249 against 0.2 is *as expected*;
  - 0.151 against 0.2 is *as expected* (it rounds to 0.2), and 0.149 is *below* (it rounds to
    0.1);
  - a NULL surprise has no kind.
- An actual of 0.46 against 0.2 is *as expected* for retail sales at its 0.3 line (0.26
  unrounded), where rounding would make it *above*. This shows the headline rounding is CPI's
  alone.
- An actual of 0.25 against 0.2 is *above* for CPI (half up to 0.3), and 0.2499 *as expected*.
- With no key set, given three releases at 0.281, 0.2 and 0.0 against 0.2 and one market's closes,
  `follows --event cpi` exits 0. It prints `follows: 3 CPI releases <first> … <last>: 1 above,
  1 as expected, 1 below` and an *above* row.
- The other `follows` tests pass unchanged.

## What this part does not do

- No rerun of retail sales from its headline.
- No headline CPI: core is the rule's measure.
- No core PCE: it has the same unrounded actual and 0.1 line; it is its own part.
- No quarter or year (part 2), no trigger file (step 18). Nothing is stored.
- Releases are not independent; the chance says more than it should, as in part 1.

## Technical details

- **`flows.py`:** `SurpriseRule` gains `kind_decimals: int | None = None`, the decimals the
  headline is published to; its docstring says only `release_kinds` reads it, so step 4 and the
  live calls keep the unrounded surprise. `CPI_SURPRISE_RULE` sets it to 1.
- **`study.py`:** with `kind_decimals` set, `release_kinds` reads the row's `actual_mom` and
  `expected_mom`. The actual is rounded half up to `d` decimals (`Decimal.quantize` with
  `ROUND_HALF_UP`, on `repr` of the float), and the kind's surprise is `round(rounded - expected,
  6)`, compared with `noticeable` as now. The `surprise IS NOT NULL` filter stays, so a release with no
  surprise still has no kind. Without `kind_decimals`, nothing changes. The 1 is the decimals
  `expectations.CONSENSUS_ROWS` already records for core CPI.
- **`__main__.py`:** `FOLLOWS_NOUNS` gains `"cpi": "CPI releases"`.
- **Tests:** in `tests/test_what_follows.py`. `_store_reports` gains `values: Mapping[date,
  tuple[float, float]] | None = None`, a release's (actual, expected), 0.0 and 0.0 as now when
  absent, so the existing tests are unchanged. The CPI tests store a surprise of 0.0 beside their
  values, which shows the kind is read from the actual and the consensus, not the stored surprise.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17, `docs/precision.md`
  (the retail row, in the spec change), and `docs/status.md`.
