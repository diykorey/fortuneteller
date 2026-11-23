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
| 2 | ~~The first refresh, 2026-11-23~~ **done** 2026-11-23 | Its pull request holds the new rows, the diff check, the hand check and the page's change; merged before the evening job |
| 3 | Each Monday after, to the gate (2027-01-31) | One pull request a week, as step 2; then reconsidered at the gate |

## What this step does not do

- No fetch in the evening job, no trigger, no live call: the calendar fills too late for one.
- No change to how `follows` reads the reports.

## Technical details

- `scripts/nasdaq_earnings.py`: `LAST` from the command line; `refetched(day, today)`, with
  `REFETCH_DAYS = 21`, takes the day so the test needs no clock. `scripts/sec_8k_times.py`:
  `_get(..., again=True)` for the current index.
- Docs: [step 31](earnings.md) gets a dated line naming this step; roadmap, status, changelog.

## Results

### Step 2: the first refresh, 2026-11-23

*2026-11-23, LAST 2026-11-20.* Every line quoted is in [the evidence](earnings-current-results.txt),
on step 31's caches and a copy of the real store of 2026-11-21 01:05.

**In plain words:** Nasdaq had filled Walmart's report of 2026-11-19 by Monday: EPS $0.65 against
$0.64 expected, a surprise of 1.56%, so *as expected*. It is the one new report, nothing older
changed, and every answer and verdict on the page stays as it was.

The counts are larger than the spec's because [step 39](exact-meet.md) added 119 exact
meets after the spec was written: the seed held 2,211 reports, not 2,092, and the in-line day
stood at 229 of 368, not 183 of 303.

- **The new rows** (`scripts/nasdaq_earnings.py seed data/cache/earnings/nasdaq
  data/cache/earnings/sec 2026-11-20`: `wrote 2212 reports`, above 1513, as expected 457, below
  242): one, `2026-11-19,11:58,WMT,0.65,0.64,1.56,as expected`. Expected exactly this one. Right.
- **History unchanged** (`git diff -U0 data/seed/earnings.csv`): one line added, none removed and
  none changed. 13 of the refetched pages (2026-11-02 to 2026-11-18) changed bytes, but no
  member's line in the seed changed with them. Right.
- **The seed test** (`uv run pytest -q tests/test_seed_data.py -k earnings`, 3 passed): Walmart a
  member on 2026-11-19 (`data/seed/dow.csv`, in since 2008), 1.56% *as expected* at ±2%, an 8-K
  with Item 2.02 accepted 2026-11-19 11:58:52 UTC. Right.
- **The hand check** (Yahoo's earnings history, finance.yahoo.com/quote/WMT/analysis,
  2026-11-23, quarter ending 10/31/2026): EPS 0.65 against Nasdaq's 0.65, estimate 0.64 against
  0.64, both within $0.02; the 8-K at 06:58 New York, before the open, so it reacts that day
  (the time from the 8-K, as in step 31). Pass. Yahoo prints the surprise as 2.16%, which would be *above* on its rounding of the
  estimate. The kind is Nasdaq's, so this is recorded, not a miss.
- **The ids** (the reload script in the evidence, on the copy): `ids: 2212 of 2212 stored equal
  the seed's`. Walmart was alone on its day, so no id shifted. Right.
- **The page's change** (`follows --event earnings`, before and after, on the copy): the header
  goes from 2,211 reports to 2,212, and one cell changes its counts. *as expected*'s day goes from
  451 to 452 reports (Walmart's day was up against the S&P 500), still *down*, and walk-forward
  goes from 368 graded with 229 right to 369 with 229 right (62.1%). It still holds and is still
  the cell nearest its bar. `--after-the-day` changes only its header. No answer or verdict
  changed. Right.

The expected outcome was **right**: exactly one new row, Walmart's of 2026-11-19, no line
removed, and no answer or verdict changed. Nasdaq had filled the report by 2026-11-23, four days after it.

