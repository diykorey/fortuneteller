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
  to 510; a few changes the table misses); outside it, step 1 stops for the owner's call. *Amended
  2026-11-20 by the owner, after the five changes by hand found Okta's dated on S&P's release
  day:* the four changes Wikipedia dates on the day of S&P's release (Okta 2026, Phillips 66,
  Kinder Morgan and Alexion 2012) take the effective day from S&P's release instead.
- **The reports, the kind, the minute: step 31's.** Nasdaq's calendar pages (saved, 2008 to
  2026-11-18) kept for the members of that day; the kind at ±2%; the minute of the 8-K with Item
  2.02 within a day, from the SEC's filing index of the member's CIK (the SEC's filer number,
  looked up by ticker in the SEC's `company_tickers.json`). Nasdaq gives no release time in its
  saved pages (its `time` is *time-not-supplied* on all 2,092 of step 31's), so the 8-K is the
  minute. A member no longer listed has no CIK there: its reports are *no 8-K*, and the kept are
  survivors, as in step 35; the share left out so is printed.
- **The names, as step 35's:** each ticker's SEC company name and Yahoo name beside Wikipedia's,
  a mismatch read by hand and left out as *another company now*. *Amended 2026-11-20, before any
  report or price was read:* the SEC's name alone, since the SEC's list and Yahoo both name
  today's holder of a ticker; the tickers left out are passed to the seed as `--exclude`.
- **The scripts, given the members:** `nasdaq_earnings.py seed` and `sec_8k_times.py fetch` take
  the members file and the seed to write (the Dow's by default, so step 31's seed is rewritten
  byte for byte).
- **The flow:** `earnings500`, type code 36, event type `Earnings release (S&P 500)` (a flow's
  own, as each flow's must be), the earnings' class
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
| 2 | The flow, `follows --event earnings500`, `load-prices --companies --seed` | Tests: the seed loads one event per report; `--seed` loads that seed's companies and `company_tickers()` is unchanged; `follows` prints each kind's three spans; `just check` passes |
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

## Results

*Measured 2026-11-20 on a copy of the store ([evidence](earnings-sp500-results.txt), [step 1's
evidence](earnings-sp500-steps.txt)). The table's numbers are printed by `follows --event
earnings500`, the reaction close's by `follows --event earnings500 --after-the-day`.*

**In plain words:** across 24,298 reports by S&P 500 members since 2011, a **miss was followed by
the shares trailing the index on the day** 2,522 times and beating it 999 of the 3,521 that moved
(72%), where the companies' own days split about evenly. Replayed walk-forward that call was right
2,506 times of 3,798 (66%): it **holds**, as on the Dow (156 of 219). The Dow's two other holds do
not carry over: the miss's week was right 59.5% (2,246 of 3,777), just under the 60% bar, and an
in-line report's day 52% (1,916 of 3,664). A beat is followed by *up* on the day and the week, both
marked *the period*, and on the month, which does not hold. From the reaction close nothing is an
answer, the miss's day included.

| | Expected | Found |
| --- | --- | --- |
| Miss, day | *down*, holds | *down*, 999/300/2,522 of 3,821; **holds**, 2,506 of 3,798 — right |
| Miss, week | *down*, holds | *down*, 961/578/2,263; doesn't hold, 2,246 of 3,777 (59.5%) — **wrong** |
| Miss, month | *down* | *down*, marked *the period* — **wrong** |
| In line, day | *down*, holds | *down*, 1,444/367/2,003; doesn't hold, 1,916 of 3,664 — **wrong** |
| In line, week | *down* | *down*, 1,325/669/1,805 — right |
| In line, month | *down* | *down*, marked *the period* — **wrong** |
| Beat, day | *up*, marked *the period* | *up*, 8,788/1,515/6,105, marked *the period* — right |
| Beat, week | *up*, doesn't hold | *up*, marked *the period* — **wrong** |
| Beat, month | *up*, doesn't hold | *up*, 6,515/4,306/5,226; doesn't hold — right |
| From the reaction close | miss's day *down*, the rest *can't say* | every cell *can't say* (the beat's month *about the same*, marked *the period*) — **wrong** on the miss's day |
| Nothing else holds; answers beyond these ≤ chance line + 2 | | none beyond them (chance line 0.3) — right |
| Reports in the seed; shares | 20,000 to 30,000; within 5 points of 72/16/12 | 24,298; 68.3/15.8/15.9 — right |
| Kept by `follows` | at least 70% | 24,043 on the day (99%) — right |
| Every other flow's `follows` | unchanged | CEO, earnings, OPEC and additions: `cmp` identical — right |

- **Six cells of fourteen were expected wrongly.** The one that matters stands: a miss's day,
  on about 3,800 reports instead of 235.
- **Left out:** 240 holes on the day (fewer than 504 closes before) and 15 with no reaction close
  yet (reports of 2026-11-18, the copy's last close), in neither column as the
  [Glossary](../glossary.md)'s *Hole* says. Before the seed: 960 *no 8-K* (196 tickers with no
  SEC filer number today: bought, merged or delisted) and 178 *another company now*; the kept
  lean towards survivors.
- **The five by hand:** rows 1, 5,000, 10,000, 15,000 and the last kept (24,296; the last row,
  Palo Alto's of 2026-11-18, has no reaction close in the copy) equal `study.excess_spans` to 0.01
  point.
- **`follows` took 38 minutes** on the copy (34 from the reaction close), which is one reason it
  stays off the evening job.
- **By chance:** about 0.3 answers and 0.1 holds on all history; nine answers and one hold found.
