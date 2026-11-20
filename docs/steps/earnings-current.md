# The earnings kept current

> Step 33 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20: not a new kind, the upkeep of [step 31](earnings.md)'s. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** step 31's reports stop at 2026-11-18, and the page's answer to "a Dow company
missed" ([step 32](ask-earnings.md)) stops with them. Each week, the reports since are added the
way step 31 added the first 2,092, so the page counts Walmart's report of 2026-11-19 and the ones
after it.

At the end: a refresh, run by hand in a session each Monday, adds the week's reports to
`data/seed/earnings.csv` in a pull request; the evening job loads the seed as it does today
(`load-releases` reads every flow's seed; `load-prices` loads each company's closes).

## The way to reach it

- **Step 31's scripts, given the last day.** `scripts/nasdaq_earnings.py fetch DIR LAST` and
  `seed DIR SEC_DIR LAST` take the last day, a weekday, the Friday before the run; with none,
  2026-11-18, step 31's.
- **A page fetched again while Nasdaq may still fill it.** Nasdaq fills a report's EPS late:
  Walmart's report of 2026-11-19 still had no EPS 32 hours after it (2026-11-20 08:30 Kyiv). So
  `fetch` fetches again each page dated 21 days or fewer before the day it runs; older pages stay
  as saved. Three weeks covers a lag of days with room; a report still empty after it stays out.
- **The filing indexes fetched again.** `scripts/sec_8k_times.py fetch DIR` fetches each
  member's current index again (the newest 8-Ks are in it); its older pages and the SEC's ticker
  list are kept as saved.
- **The members.** `data/seed/dow.csv` gets a dated row in the refresh's pull request when the
  Dow's members change (S&P Dow Jones Indices announces it); a new member's closes load with the
  others ([step 32](ask-earnings.md)).
- **The rest is step 31's:** the members of each day, the ±2% kind, the 8-K's minute, the reports
  left out. A report with no EPS yet is *no kind* this week and comes in a later one.

## The rule, fixed before the first refresh

- **History unchanged:** `git diff -U0 data/seed/earnings.csv` removes no line dated more than 22
  days before the run (the window's 21 days and one for the 8-K's UTC day). A line inside it
  that changes is listed in the pull request with Nasdaq's old and new figures.
- **Each new report** is checked as step 31's seed test checks it (a member on its day, a kind by
  ±2%, an 8-K minute), and the newest one by hand against Yahoo's earnings history: its EPS and
  its estimate within $0.02 each, and its time before the open or after the close. A miss stops
  the refresh until the row is explained, as in step 31.
- **The page's change:** `follows --event earnings` on a copy of the store, before and after; the
  pull request lists each cell whose answer or verdict changes. The in-line day, 183 of 303
  (60.4%), is the cell nearest its bar.
- **Expected outcome of the first refresh** (run 2026-11-23, LAST 2026-11-20): exactly one new
  row, Walmart's of 2026-11-19, if Nasdaq has filled it by then; no line removed; no answer or
  verdict changed by one report in 2,093. No row means Nasdaq's lag is over three days, which
  goes in the results.

## How you know it is right

- `nasdaq_earnings.py seed` with no last day writes the committed seed byte for byte from step
  31's cache, run before any refetch (done 2026-11-20: `wrote 2092 reports`, no diff).
- A report filled late that sorts first on a day shifts that day's ids (`n`, [step 31](earnings.md));
  checked on a copy of the store: after the reload, every stored report's id, detail and minute
  equal the seed's (2,093 of 2,093), and the observations are rebuilt whole each evening, so none
  keeps an old id's move.
- A test: a page 21 days before the run is fetched again, 22 is not; the last day is the one given.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two scripts take the last day and fetch again as above | The byte-for-byte check and the test pass |
| 2 | The first refresh, 2026-11-23 | Its pull request holds the new rows, the diff check, the hand check and the page's change; merged before the evening job |
| 3 | Each Monday after, to the gate (2027-01-31) | One pull request a week, as step 2; then reconsidered at the gate |

## What this step does not do

- No fetch in the evening job, no trigger, no live call: the calendar fills too late for one.
- No change to how `follows` reads the reports.

## Technical details

- `scripts/nasdaq_earnings.py`: `LAST` from the command line; `refetched(day, today)`, with
  `REFETCH_DAYS = 21`, takes the day so the test needs no clock. `scripts/sec_8k_times.py`:
  `_get(..., again=True)` for the current index.
- Docs: [step 31](earnings.md) gets a dated line naming this step; roadmap, status, changelog.
