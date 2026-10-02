# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 2, sub-step 5 — `uv run fortuneteller load-prices` fetches and stores the five instruments'
daily closes, rebuilds the observations, and prints the counts. **Step 2 is complete.** Live run on
2026-09-29, twice, output identical to the spec's: `5 instruments × 649 releases = 2698
observations` (649 / 648 / 649 / 312 / 440), about 4 seconds per run. *(PR #80.)*
A failed or malformed Yahoo or FRED reply, or a network timeout, now ends either command with a
one-line error instead of a traceback, and `load-prices` stores nothing unless all five
instruments were read.

## In progress

MVP step 3 — **Raw move**: the spec, [step-3-raw-move.md](steps/step-3-raw-move.md) — do these
instruments move more on CPI days than on ordinary days? Its Decisions section records each choice
and why; the more precise alternatives are in [precision.md](precision.md).

## Next

MVP step 3, sub-step 1 — `daily_moves` and `cpi_days`: every day's absolute move, and which days
are CPI days; CPI-day moves must equal `observations.ret_1d`.

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-09-29 | Step 2.5: `load-prices` CLI — step 2 complete | PR #80 |
| 2026-09-29 | Review hygiene: test isolation, empty key, naive `event_ts`, CI lockfile | PR #79 |
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
| 2 Prices | Done |
| 3 Raw move | Not started |
| 4 Surprise | Not started |

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- `daily_bars` rows from a replaced ticker are never deleted, so an old and a new series could mix.
- `obs_id` depends on the order of `MVP_PRICE_SERIES` and leaves room for ten instruments.
- The `Prediction` model has no table and no caller.
- CPI release dates before 1997 have not been checked against the BLS archive. One, 1992-12-13,
  falls on a Sunday; the other 648 fall on weekdays. Check before step 3 relies on them.
