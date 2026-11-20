# Earnings beyond the Dow

> Step 36 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** [step 31](earnings.md) measured the Dow's 30 companies' reports and found a
miss followed by a fall against the S&P 500, holding on the day and the week. Does it hold on the
S&P 500's own ~500 companies, with ten to fifteen times the reports? A reader who brings "X missed"
about any large US company should be told what followed such misses.

At the end: `follows --event earnings500` prints the three kinds, measured exactly as step 31's
(each company's excess move against its own base of the 504 closes before), against the rule
below written first.

## The way to reach it

- **The companies: the S&P 500's members on the report's day, from 2011-01-03.** Rebuilt from
  Wikipedia: today's list (*List of S&P 500 companies*, revision 1384572480 of 2026-11-08) taken
  back through step 35's dated changes (revision 1385951946), each change undone on its effective
  day; 820 tickers in all. Written as `data/seed/sp500.csv` (`day`, `ticker`, `change`), as
  `dow.csv` is. Before 2011 the table lists 1 to 13 changes a year against some 20 since, so the
  step starts then. **Check:** the rebuilt count stays between 495 and 515 on every day (seen: 503
  to 510; a few changes the table misses); outside it, step 1 stops for the owner's call.
- **The reports, the kind, the minute: step 31's.** Nasdaq's calendar pages (saved, 2008 to
  2026-11-18) kept for the members of that day; the kind at ±2%; the minute of the 8-K with Item
  2.02 within a day, from the SEC's filing index of the member's CIK (the SEC's filer number,
  looked up by ticker in the SEC's `company_tickers.json`). Nasdaq gives no release time in its
  saved pages (its `time` is *time-not-supplied* on all 2,092 of step 31's), so the 8-K is the
  minute. A member no longer listed has no CIK there: its reports are *no 8-K*, and the kept are
  survivors, as in step 35; the share left out so is printed.
- **The names, as step 35's:** each ticker's SEC company name and Yahoo name beside Wikipedia's,
  a mismatch read by hand and left out as *another company now*.
- **The scripts, given the members:** `nasdaq_earnings.py seed` and `sec_8k_times.py fetch` take
  the members file and the seed to write (the Dow's by default, so step 31's seed is rewritten
  byte for byte).
- **The flow:** `earnings500`, type code 36, event type `Earnings release`, the earnings' class
  (step 31's flow) with seed `data/seed/earnings_sp500.csv`, lesser as step 31's. Its events load
  each evening with every flow's (and the page's `raw-move` card takes its history, as every
  flow's), but **its companies' closes are not loaded each evening and it is not on the page's
  *Ask***: some 800 companies would add a quarter of an hour to the evening job. It is measured
  on a copy of the store, the closes loaded by `load-prices --companies --seed FILE`.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price and no report count: the rebuilt membership's counts
above, and Nasdaq's missing release times.*

- `follows`' bars, as step 31's: under 10 events *too few*; an answer at p < 0.01 against the
  company's own base (for *up* and *down*, its share of up among its moved spans); a link *holds*
  at 60% right of at least 30 graded walk-forward, 10 points over the base, p < 0.01; the placebo
  marks *the period*: an answer the placebo also gives is printed as *the period*, not counted.
- **Expected outcome** (step 31's, with more reports): from the close before, a miss *down* on the
  day, the week and the month, the day and the week holding; an in-line report *down* on the day,
  the week and the month, the day holding; a beat *up* over the week and the month, not holding,
  its day *up* but marked *the period*. From the reaction close, a miss's day *down*, the rest
  *can't say*. Nothing else holds; answers beyond these at most the chance line plus two. In the
  seed between 20,000 and 30,000 reports, the kinds' shares within 5 points of step 31's (72%
  above, 16% in line, 12% below); `follows` keeping at least 70% of them. Every other flow's
  `follows` unchanged.

## How you know it is right

- The membership check above; and five changes by hand against S&P's releases (the changes
  table's 1st, 100th, 200th, 300th and last after 2011-01-03): a company in or out on the wrong
  day stops step 1.
- Every Dow report of step 31 from 2011 whose company was in the S&P 500 that day is in the new
  seed, with the same kind and minute; each difference listed and explained; more than 2% of
  them differing stops step 1.
- The names above: every mismatch listed with its reading.
- Five reports' excess day moves by hand (the seed's rows 1, 5,000, 10,000, 15,000 and its last
  kept) against `study.excess_spans`, within 0.1 point.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The membership, the scripts given members, the SEC indexes, the names, the seed | `sp500.csv` and `earnings_sp500.csv` with seed tests (the count in 495 to 515 every day; each report's company a member on its day; kinds of the three); the checks above in `docs/steps/earnings-sp500-steps.txt`; step 31's seed rewritten byte for byte |
| 2 | The flow, `follows --event earnings500`, `load-prices --companies --seed` | Tests: the seed loads one event per report; `--seed` loads that seed's companies and `company_tickers()` is unchanged; `follows` prints nine cells; `just check` passes |
| 3 | Results | `follows --event earnings500` and `--after-the-day` on a copy of the store, every other flow's `follows` compared, the five excess checks; each expected cell judged right or wrong in the Results section, goldfish-reviewed; roadmap, status, changelog, schema updated |

## What this step does not do

- No page, no evening load, no trigger: a later step if it holds.
- No change to step 31's flow or the page's earnings.

## Technical details

- `scripts/sp500_additions.py members DIR` writes `sp500.csv` from the two saved revisions.
- `scripts/nasdaq_earnings.py seed DIR SEC_DIR [LAST] [--members FILE --out FILE --first DAY]`;
  `scripts/sec_8k_times.py fetch DIR [--members FILE]`.
- `scripts/sp500_additions.py names500 DIR SEC_DIR` prints the names side by side.
- `flows.py`: `EARNINGS_500_FLOW`; `__main__.py`: `follows` as for the earnings;
  `load-prices --companies` gains `--seed FILE`.
