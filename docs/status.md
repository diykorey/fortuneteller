# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

Review hygiene: the CLI smoke test no longer writes to `data/fortuneteller.duckdb`; an empty
`FT_FRED_API_KEY` is treated as unset; `event_ts` must be a naive datetime (the model enforces it); a
seed test assertion that could never fail now checks the line number; CI requires the lockfile and
checks formatting; `justfile`, `CLAUDE.md` and `schema.md` catch up with the code.

**Known and deferred from the same review:** paths and `.env` resolve from the working directory;
the CLI catches only `FredError`, so network timeouts and malformed responses show a traceback;
`daily_bars` rows from a replaced ticker are never deleted; `obs_id` depends on instrument order; the
unused `Prediction` model; release dates before 1997 have not been checked against the BLS archive
(one, 1992-12-13, falls on a Sunday).

## In progress

Nothing.

## Next

MVP step 2, sub-step 5 — **`uv run fortuneteller load-prices`**: fetch and store the closes, build
the observations, and print the counts per instrument and in total. Spec:
[step-2-prices.md](steps/step-2-prices.md).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-29 | Review hygiene: test isolation, empty key, naive `event_ts`, CI lockfile | this branch |
| 2026-09-29 | Review fixes: rebuild observations, loud failures, no provisional bars | PR #78 |
| 2026-09-28 | Step 2.4: build `observations` — 2,698 release-day moves | PR #77 |
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
