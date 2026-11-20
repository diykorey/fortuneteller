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

- **The source:** Yahoo's `quoteSummary` with `earningsHistory` (the last four quarters: EPS, the
  estimate, the surprise), which asks for a cookie from `fc.yahoo.com` and a crumb from
  `/v1/test/getcrumb` (the chart endpoint the prices use needs neither). One request a member; the reply saved under `data/cache/earnings/yahoo/DAY/TICKER.json`.
- **The same kind:** each member's quarters that step 31's seed also holds, matched by the
  report's day within a day; the kind by Yahoo's surprise at ±2%, beside the seed's.
- **How soon:** on each Dow member's report to 2026-12-31, Yahoo asked every 30 minutes from the
  8-K's minute for six hours; the delay is the first ask holding that quarter's EPS.

## The rule, fixed before measuring

- **Agreement:** at least 90% of the matched reports get the same kind from both sources, on at
  least 60 matched reports.
- **Speed:** the median delay at most 2 hours, on at least 3 reports, and none over 6.
- **Usable** only if both hold. One data point is seen already: Walmart's of 2026-11-19, $0.65
  against Yahoo's $0.636 (+2.2%, *above*) and Nasdaq's $0.64 (+1.6%, *as expected*), a
  disagreement, by 2026-11-20 08:40 Kyiv. It counts in the 60.
- **Expected outcome:** agreement about 85%, the two consensuses differing by a cent on reports
  near ±2%, so *not usable* by agreement; speed within the bar.

## How you know it is right

- Three matched reports checked by hand against Yahoo's page and Nasdaq's: EPS and estimate as
  saved, within $0.01.
- A report Yahoo does not have yet is *not yet*, never a kind.

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
- Docs: roadmap row 34, status, changelog, glossary (*same-day source*).
