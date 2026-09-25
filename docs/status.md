# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 1, sub-step 2 — `study.fetch_cpi_releases` fetches the CPI initial-release history from
FRED in one request; `study.parse_cpi_releases` turns it into dated records (reference month,
release date, value) and reports the months printed without a value. Live run on 2026-09-25: 650
rows, 649 parsed, `2025-10` skipped, published 1972-08-22 … 2026-09-11.

## In progress

Nothing.

## Next

MVP step 1, sub-step 3 — **map each parsed release to an `EventInstance`**: release timestamp at
08:30 America/New_York stored UTC, the actual, and an `event_id` from the reference month. Code goes
in `src/fortuneteller/study.py`. Spec: [step-1-releases.md](step-1-releases.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-25 | Step 1.2: fetch and parse the CPI initial-release history from FRED | `study.py` |
| 2026-09-11 | Step 1 prep: FRED key in settings, accounts doc, API verified, UST 10Y added | PR #66 |
| 2026-09-11 | Docs entry point, legend, step 1 spec | PR #65 |
| 2026-09-11 | Docs rebuilt around the lean MVP; pre-reset corpus archived to `legacy/` | PR #64 |
| 2026-08-05 | `main` reset to M0; pre-reset work parked in `origin/main_05082026` | — |
| before 2026-08 | M0 data spine: models, DuckDB schema, seed CSVs, `init \| seed \| query-demo` CLI | M0-01…09 |

## MVP progress

| Step | State |
| --- | --- |
| 1 Releases | Sub-step 2 of 5 done |
| 2 Prices | Not started |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
