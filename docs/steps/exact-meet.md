# An exact meet

> Step 39 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5; the
> trigger written in [Precision](../precision.md) ("Steps 31 and 36 — earnings reports"). Terms
> are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when a company's earnings per share equal the analysts' forecast to the cent,
Nasdaq's calendar prints the surprise as `N/A`, not 0, and the earnings seeds left the report out.
That is a report *as expected* by the rule of [step 31](earnings.md): the surprise is 0, inside
±2%. The page's *as expected* cells ([Ask about earnings](ask-earnings.md), the Dow's) miss these reports: 87 of the Dow's since 2011 and 1,802 of
the S&P 500 members'. [Step 34](earnings-same-day.md)'s Yahoo script already reads an exact meet so.

At the end: both seeds carry the exact meets as *as expected*, and `follows --event earnings` and
`--event earnings500` print the cells with them, judged against the rule below written first.

## The way to reach it

- **The kind:** `nasdaq_earnings.kind` takes the EPS and the forecast too. A surprise of `N/A`
  with both figures given and equal is *as expected*; with the figures unequal or either missing,
  the report has no kind and is left out, as before (counted); Nasdaq also prints `N/A` for a
  forecast of $0, where no percent exists. A loss is written `($0.17)`. The seed's `surprise`
  column keeps Nasdaq's `N/A`. Nothing else changes: the bar, the 8-K's minute, the members. An
  event's id counts the reports of its day, so a new row renumbers its day's others; earnings
  have no live calls and nothing kept refers to those ids. The `raw-move` and scoreboard cells
  of the two flows change with the rows; they are not judged here.
- **The seeds rebuilt** from the saved pages (`data/cache/earnings/nasdaq`), with the commands
  that built them ([step 31](earnings.md), [step 36](earnings-sp500.md)); their other rows are
  unchanged byte for byte.
- **Measured as steps 31 and 36,** on a copy of the store: `load-releases`, `load-prices
  --companies` for the S&P 500 seed's companies, and `follows` both runs for `earnings` and
  `earnings500`.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before: the two counts above (step 36's Results) and the cells of steps
31 and 36; no exact meet's move. Amended the same day after the goldfish, before any price was
read, with the seeds already rebuilt (step 1): the 87 is the Dow's since 2011, its seed runs from
2008; the cells below the first bullet list were added.*

- Steps 31 and 36's bars, unchanged: under 10 *too few*; an answer at p < 0.01 against the
  company's own base; a link *holds* at 60% right of at least 30 graded walk-forward, 10 points
  over the base, p < 0.01; an answer the placebo also gives is *the period*.
- **Expected outcome:**
  - The seeds gain 87 (Dow) and 1,802 (S&P 500) *as expected* rows, give or take 5%, and lose
    none. The *above* and *below* rows are unchanged.
  - An exact meet is no beat: the market reads it as a small miss. So the *as expected* cells keep
    their answers. The Dow's: *down* on the day, the week and the month from the close before. The
    day's hold (60.4% of 303) stays at or over 60%. The S&P 500's *as expected* day keeps its
    answer and still does not hold.
  - The S&P 500's *as expected* week stays *down* and the month *down* marked *the period*; none
    holds. From the reaction close, every *as expected* cell of both flows stays *can't say*.
    The Dow's *as expected* week and month do not hold. Answers beyond these at most the chance
    line plus two.
  - `follows`' header counts *as expected* up by the rows added (from 2008 for the Dow).
  - The *above* and *below* cells are byte for byte unchanged. So is every other flow's `follows`.
  - A count outside its band is recorded, not a stop: the rows are what Nasdaq printed.

## How you know it is right

- A test: an equal gain and an equal loss (`($0.17)`) are *as expected*; a forecast of $0 and a
  missing EPS have no kind; numeric surprises are read as before.
- The seeds' diff adds rows only, each `N/A` with EPS equal to forecast. Five new S&P 500 rows
  (1, a quarter, a half, three quarters, the last) match Nasdaq's saved page and the 8-K.
- `follows`' header *as expected* count equals step 31's and 36's plus the rows added.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The kind and the seeds | The test passes; both seeds rebuilt, the diff adds rows only; counts and the five checks in `docs/steps/exact-meet-steps.txt` |
| 2 | Results | `follows` both runs, both flows, on a copy of the store, against the rule above; every other flow's `follows` both runs compared by `cmp`, main's code against the branch's on the same copy; goldfish-reviewed; Precision's exact-meet row removed; roadmap, status and changelog updated |

## What this step does not do

- No new kind, no change to the ±2% bar, no change to the page's code: the page reads the store
  each evening, so its *as expected* cells take the rows once merged.
