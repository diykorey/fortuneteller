# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 1, sub-step 5 — `uv run fortuneteller load-releases` fetches, parses and stores the CPI
release history. **Step 1 is complete.** Live run on 2026-09-25, twice: `loaded 649 CPI releases,
1972-08-22 … 2026-09-11`, `2025-10` skipped for having no value, 649 rows after both runs. *(PR #70.)*

## In progress

Nothing.

## Next

MVP step 2 — **Prices**: daily bars for the five MVP instruments; the return around each release
into `observations`. Spec: to be written, following the step template in [legend.md](legend.md).

## Done

| Date | What | Where |
| --- | --- | --- |
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
| 2 Prices | Not started |
| 3 Raw move | Not started |
| 4 Surprise | Not started |
