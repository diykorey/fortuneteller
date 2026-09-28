# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 2, sub-step 2 — `study.fetch_daily_bars` fetches one ticker's whole daily history from
Yahoo; `study.parse_daily_bars` turns it into closes by trading date, read in the exchange's time
zone, with empty and weekend bars dropped. Live run on 2026-09-28, on US Pacific time: 58,459 closes
across the five tickers, and the known 2022-09-13 closes come out right.

## In progress

Nothing.

## Next

MVP step 2, sub-step 3 — **store the closes of all five tickers in `daily_bars`**; re-running
changes no row count. Spec: [step-2-prices.md](steps/step-2-prices.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-28 | Step 2.2: fetch and parse Yahoo daily closes | this branch |
| 2026-09-28 | Step 2.1: `daily_bars` table and its schema doc | PR #74 |
| 2026-09-25 | Scenarios doc: ten shock → aftershock episodes, numbers verified | PR #72 |
| 2026-09-25 | Step 2 spec: prices from Yahoo, `daily_bars`, observations | PR #73 |
| 2026-09-25 | Schema doc: every table, column and enum value explained | PR #71 |
| 2026-09-25 | Step 1.5: `load-releases` CLI — step 1 complete | PR #70 |
| 2026-09-25 | Step 1.4: store the CPI events idempotently | PR #69 |
| 2026-09-25 | Step 1.3: map each CPI release to an `EventInstance` | PR #68 |
| 2026-09-25 | Step 1.2: fetch and parse the CPI initial-release history from FRED | PR #67 |
| 2026-09-11 | Step 1 prep: FRED key in settings, accounts doc, API verified, UST 10Y added | PR #66 |
| 2026-09-11 | Docs entry point, legend, step 1 spec | PR #65 |
| 2026-09-11 | Docs rebuilt around the lean MVP; pre-reset corpus archived to `legacy/` | PR #64 |
| 2026-08-05 | `main` reset to M0; pre-reset work parked in `origin/main_05082026` | — |
| before 2026-08 | M0 data spine: models, DuckDB schema, seed CSVs, `init \| seed \| query-demo` CLI | M0-01…09 |

## MVP progress

| Step | State |
| --- | --- |
| 1 Releases | Done |
| 2 Prices | Sub-step 2 of 5 done |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
