# A same-day source for earnings

> Step 34 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner ([Decisions](../decisions.md)). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** a live call on a Dow company's report needs its EPS and the consensus within
hours; Nasdaq's calendar, step 31's source, fills them days late (Walmart's of 2026-11-19 was
still empty on 2026-11-20). This step measures one free source, Yahoo's `earningsHistory`, before
anything is called from it: does it give the same kind as Nasdaq, and how soon?

At the end: a number for each question and a verdict, *usable* or not. No call, no trigger.

## The way to reach it

- **The source:** Yahoo's `quoteSummary` with `earningsHistory`: each of the last four quarters'
  end (`quarter`), EPS (`epsActual`), estimate (`epsEstimate`) and surprise, but no report day. It
  asks for a cookie from `fc.yahoo.com` and a crumb from `/v1/test/getcrumb` (the chart endpoint the
  prices use needs neither). Each ask is one request a member, its replies saved under
  `data/cache/earnings/yahoo/ASKED/TICKER.json`, ASKED the minute asked.
- **The same kind:** a Yahoo quarter is matched to the step 31 report whose saved Nasdaq page
  gives the same ticker and fiscal quarter (`fiscalQuarterEnding`, `Oct/2026` for a quarter ending
  2026-10-31). Yahoo's kind is recomputed as Nasdaq's surprise is, (EPS − estimate) / |estimate|
  in percent, at ±2%; Yahoo's own `surprisePercent` is a fraction and is only checked against it.
- **How soon:** for each member's report from 2026-11-23 to 2026-12-31 on Nasdaq's calendar
  (listed in the results before the first), Yahoo is asked every 30 minutes for six hours, by a
  loop run in a session, from 07:00 New York for a pre-market report or 16:00 for one after the
  close. The delay is measured afterwards: from the 8-K's minute (step 31's way) to the first ask
  holding that quarter's EPS; a report still empty at the end counts as *over six hours*.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before: one reply, Walmart's of 2026-11-20 08:40 Kyiv: its four quarters,
the newest below; on its three older ones Yahoo's estimate is unrounded ($0.65872) where Nasdaq's is
in cents ($0.65), a kind apart only near ±2%.*

- **Agreement:** at least 90% of matched reports get the same kind from both sources, on at least
  60 matched reports; under 60, *too few*. Ninety, so that a call made from Yahoo's kind would be
  Nasdaq's in nine of ten.
- **Speed:** the median delay at most 2 hours, so a pre-market report is called before its own
  close; none *over six hours*; on at least 3 reports, under 3 *too few*.
- **Usable** only if both hold; *too few* on either is not usable yet, and the step waits.
- **Seen already:** Walmart's report of 2026-11-19 on Yahoo, $0.65 against $0.636 (+2.2%,
  *above*); Nasdaq's forecast then was $0.64 (+1.6%, *as expected*). It is after step 31's seed,
  so it is not one of the 60.
- **Expected outcome:** agreement between 80% and 89%, the two estimates a cent apart on reports
  near ±2%, so *not usable* by agreement; speed within its bar.

## How you know it is right

- Three matched reports, the first three by ticker of the newest matched quarter, checked by hand
  against Yahoo's page and the Nasdaq page saved: the quarter, EPS and estimate within $0.01, and
  both kinds; a miss stops the step until explained.
- For every matched report, Yahoo's recomputed surprise equals 100 × its `surprisePercent` within
  0.1 points, so the scale is right.
- A report Yahoo does not have yet is *not yet*, never a kind; a test of the matching and the
  kind, on two saved replies.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | A one-off script `scripts/yahoo_earnings.py` saves the replies and prints the agreement table | The table, its counts and the three hand checks in `docs/steps/earnings-same-day-results.txt` |
| 2 | The delay asked on the members' reports to 2026-12-31 | Each report's delay in the same file |
| 3 | Results and the verdict | The Results section here, goldfish-reviewed |

## What this step does not do

- No live call, no trigger, no change to `follows` or the seed; a call is a later step, if usable.
- No paid source.

## Technical details

- `scripts/yahoo_earnings.py`, standard library only, as step 31's scripts, the cookie and crumb
  included.
- Docs: roadmap row 34, status, changelog, glossary (*same-day source*, *crumb*).
