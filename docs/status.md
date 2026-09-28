# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 2, sub-step 4 — `study.store_observations` measures each of the five instruments around
each CPI release, from `daily_bars` and `event_instances`, into `observations`. Live run on
2026-09-28: 649 / 648 / 649 / 312 / 440 = **2,698 observations**, the same after a re-run; every
check in the spec passes (S&P 500 −4.32% on 2022-09-13; `^TNX` within 0.2 bp median of FRED's
`DGS10`; median S&P release-day move 0.55%).

## In progress

Nothing.

## Next

MVP step 2, sub-step 5 — **`uv run fortuneteller load-prices`**: fetch and store the closes, build
the observations, and print the counts per instrument and in total. Spec:
[step-2-prices.md](steps/step-2-prices.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-28 | Step 2.4: build `observations` — 2,698 release-day moves | this branch |
| 2026-09-28 | Step 2.3: store the five instruments' closes; bulk `insert_models` | PR #76 |
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
| 2 Prices | Sub-step 4 of 5 done |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
