# Earnings beyond the Dow

> Step 36 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** [step 31](earnings.md) measured the Dow's 30 companies' reports and found a
miss followed by a fall against the S&P 500, holding on the day and the week. Does it hold on the
S&P 500's own ~500 companies, with about fifteen times the reports? A reader who brings "X missed"
about any large US company should be told what followed such misses.

At the end: `follows --event earnings500` prints the three kinds, measured exactly as step 31's
(each company's excess move against its own base of the 504 closes before), against the rule
below written first.

## The way to reach it

- **The companies: the S&P 500's members on the report's day, from 2011-01-03.** Rebuilt from
  Wikipedia: today's list (*List of S&P 500 companies*, revision 1384572480) taken back through
  step 35's dated changes (revision 1385951946), each change undone on its effective day. Written
  as `data/seed/sp500.csv` (`day`, `ticker`, `change`), as `dow.csv` is. Before 2011 the changes
  table is thin, so the step starts then. **Check:** the rebuilt count stays between 495 and 515 on
  every day; seen before, 502 to 510, a drift of a few from changes the table misses.
- **The reports, the kind, the minute, the left-outs: step 31's, unchanged.** Nasdaq's calendar
  pages (already saved, 2008 to 2026-11-18) kept for the members of that day; the kind at ±2%;
  the 8-K with Item 2.02 within a day, from the SEC's filing index of each member's filer number
  (its current ticker in the SEC's list; a member no longer listed has none and is *no 8-K*). Nasdaq
  gives no release time (*time-not-supplied* on all 2,092 of step 31's), so the 8-K is the minute.
- **The scripts, given the members:** `nasdaq_earnings.py seed` and `sec_8k_times.py fetch` take
  the members file and the seed to write (the Dow's by default, so step 31's run reads the same).
- **The flow:** `earnings500`, type code 36, event type `Earnings release`, the earnings' class
  with seed `data/seed/earnings_sp500.csv`. **Not loaded each evening and not on the page:** about
  650 companies' closes would add some ten minutes to the evening job; it is measured on a copy of
  the store, its closes loaded by `load-prices --companies` with that seed named.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price and no report count: the rebuilt membership's counts
above, and Nasdaq's missing release times.*

- `follows`' bars, as step 31's: under 10 events *too few*; an answer at p < 0.01 against the
  company's own base (its share of up among its moved spans for *up* and *down*); a link *holds*
  at 60% right of at least 30 graded walk-forward, 10 points over the base, p < 0.01; the placebo
  marks *the period*.
- **Expected outcome** (step 31's, with more reports): from the close before, a miss *down* on the
  day, the week and the month, the day and the week holding; an in-line report *down* on the day,
  holding; a beat *up* over the week and the month, not holding, its day *the period*. From the
  reaction close, a miss's day *down*, the rest *can't say*. Between 20,000 and 30,000 reports
  kept. Step 31's `follows --event earnings` unchanged.

## How you know it is right

- The membership check above, and five members on five days by hand against S&P's releases
  (the seed's rows 1, 1,000, 2,000, 3,000 and its last change).
- Every Dow report of step 31 from 2011 whose company was in the S&P 500 that day is in the new
  seed with the same kind and minute; the differences listed.
- Five reports' excess day moves by hand against `study.excess_spans`, as in step 35.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The membership, the scripts given members, the SEC indexes, the seed | `sp500.csv` and `earnings_sp500.csv` with seed tests; the check, the five members and the Dow comparison in `docs/steps/earnings-sp500-steps.txt`; step 31's seed rewritten byte for byte |
| 2 | The flow and `follows --event earnings500` | Tests as step 35's; `just check` passes |
| 3 | Results | `follows` both ways on a copy of the store, the five excess checks, the Results section, goldfish-reviewed; roadmap, status, changelog, schema updated |

## What this step does not do

- No page, no evening load, no trigger: a later step if it holds.
- No change to step 31's flow or the page's earnings.

## Technical details

- `scripts/sp500_additions.py members DIR` writes `sp500.csv` from the two saved revisions.
- `scripts/nasdaq_earnings.py seed DIR SEC_DIR [LAST] [--members FILE --out FILE --first DAY]`;
  `scripts/sec_8k_times.py fetch DIR [--members FILE]`.
- `flows.py`: `EARNINGS_500_FLOW`; `__main__.py`: `follows` as for the earnings;
  `load-prices --companies` gains `--seed FILE`.
