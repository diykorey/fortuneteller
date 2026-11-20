# The earnings kept current

> Step 33 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** [step 31](earnings.md)'s reports stop at 2026-11-17, and the page's answer to
"a Dow company beat" ([step 32](ask-earnings.md)) stops with them. Each week, the reports since
are added the way step 31 added the first 2,092, so the page counts this week's Nvidia or
Walmart too, and a post can quote them.

At the end: a weekly refresh, run by hand in a session, adds the week's reports to
`data/seed/earnings.csv` in a pull request; the evening job loads them as it loads the seed today.

## The way to reach it

- **Step 31's scripts, given the last day.** `scripts/nasdaq_earnings.py fetch DIR LAST` and
  `seed DIR SEC_DIR LAST` take the last day, which was fixed at 2026-11-18; without it, they keep
  2026-11-18, so step 31's run reads the same.
- **A page fetched again while Nasdaq may still fill it.** Nasdaq's calendar fills a report's EPS
  a day or more after it: Walmart's report of 2026-11-19 had none at 00:30 New York the next
  day. So `fetch` fetches again every page within 21 days before the day it runs, saved or not;
  older pages stay as saved.
- **The filing indexes fetched again.** `scripts/sec_8k_times.py fetch DIR` fetches each
  member's current filing index again (the newest 8-Ks are in it), keeping its older pages.
- **The rest is step 31's:** the members of each day, the ±2% kind, the 8-K's minute, the reports
  left out. A report with no EPS yet is *no kind* this week and comes in the next.

## The rule, fixed before the first refresh

- **Unchanged history:** every row of the seed dated before the refetched window is unchanged,
  byte for byte. A row inside the window that changes is listed in the pull request, with Nasdaq's
  old and new figures.
- **Each new report** is a member on its day with a kind by ±2% and an 8-K minute within a day, as
  step 31's seed test checks; one of each refresh's new reports is checked by hand against Yahoo's
  earnings history (within $0.02 passes) and its release time (before the open or after the
  close), written in the pull request.
- **Expected outcome of the first refresh** (to 2026-11-20): the reports of 2026-11-18 to
  2026-11-20 that Nasdaq has filled, Walmart's of 2026-11-19 among them (a few rows), and
  no row dated before 2026-11-02 (21 days before the run) changed.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two scripts take the last day and fetch again as above | `nasdaq_earnings.py seed` with no last day writes today's seed byte for byte from step 31's cache; a test of the window's arithmetic passes |
| 2 | The first refresh, to 2026-11-20, on Monday 2026-11-23 | Its pull request holds the new rows, the history check's output and the hand check; merged before the evening job, which loads it |
| 3 | Each Monday after: the week's refresh, one pull request | A row in the [changelog](../changelog.md) each week |

## What this step does not do

- No fetch in the evening job, no trigger, no live call: the calendar fills too late for one.
- No new company or market; no change to how `follows` reads the reports.

## Technical details

- `scripts/nasdaq_earnings.py`: `LAST` from the command line; `fetch` refetches pages within
  `REFETCH_DAYS = 21` of today. `scripts/sec_8k_times.py`: `_get` fetches the current index again.
- Docs: [step 31](earnings.md) gets a dated line naming this step; roadmap, status, changelog.
