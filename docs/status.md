# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 1, sub-step 3 — `study.to_event_instance` maps each parsed release to an `EventInstance`:
`event_id` is the reference month as `YYYYMM`, `event_ts` the release day at 08:30 New York as naive
UTC (DuckDB would shift an aware one to the session zone), `quality` is `first_release`. All 649
live prints map to unique ids at 12:30 or 13:30 UTC.

## In progress

Nothing.

## Next

MVP step 1, sub-step 4 — **write the mapped releases with `insert_models(replace=True)`**; re-running
changes no row count. Round-trip `event_ts` under a non-UTC session time zone. Spec:
[step-1-releases.md](step-1-releases.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-25 | Step 1.3: map each CPI release to an `EventInstance` | this branch |
| 2026-09-25 | Step 1.2: fetch and parse the CPI initial-release history from FRED | PR #67 |
| 2026-09-11 | Step 1 prep: FRED key in settings, accounts doc, API verified, UST 10Y added | PR #66 |
| 2026-09-11 | Docs entry point, legend, step 1 spec | PR #65 |
| 2026-09-11 | Docs rebuilt around the lean MVP; pre-reset corpus archived to `legacy/` | PR #64 |
| 2026-08-05 | `main` reset to M0; pre-reset work parked in `origin/main_05082026` | — |
| before 2026-08 | M0 data spine: models, DuckDB schema, seed CSVs, `init \| seed \| query-demo` CLI | M0-01…09 |

## MVP progress

| Step | State |
| --- | --- |
| 1 Releases | Sub-step 3 of 5 done |
| 2 Prices | Not started |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
