# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 2, sub-step 3 — `study.load_daily_bars` fetches, parses and stores all five instruments'
closes in `daily_bars` (`MVP_TICKERS` maps each symbol to its Yahoo ticker). Live run on 2026-09-28:
58,460 rows, the same after a re-run, in about 3 seconds including the download. `db.insert_models`
now writes through a temporary Parquet file instead of row by row (4 minutes → a fraction of a
second) and rejects a key repeated within one call.

## In progress

Nothing.

## Next

MVP step 2, sub-step 4 — **build `observations` from `daily_bars` and `event_instances`**: the close
before each release and the move to the first close after it. Spec:
[step-2-prices.md](steps/step-2-prices.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-28 | Step 2.3: store the five instruments' closes; bulk `insert_models` | this branch |
| 2026-09-28 | Step 2.2: fetch and parse Yahoo daily closes | PR #75 |
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
| 2 Prices | Sub-step 3 of 5 done |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
