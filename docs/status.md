# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

MVP step 4, sub-step 4 — `uv run fortuneteller load-surprises` stores 1,287 surprises in
`cpi_surprises`: core 342 against the 12-month trend (1998-01 … 2026-08) and 155 against the nowcast
(2013-08 …); headline 635 and 155. It refuses to store anything if a month differs from Cleveland's
published actual by more than 0.01 pp. August 2022 core: +0.087 pp against the nowcast, +0.095
against the trend. About 47 s. **Finding:** for core, the Cleveland nowcast is almost exactly the
12-month trend (median gap 0.003 pp, correlation 0.997), so the two baselines are not independent
for core; for headline they are (0.46). Recorded in [precision.md](precision.md). **Decided:** core
against the trend gives the verdict; the other three combinations are context (spec, Decisions). *(PR #95.)*

## In progress

Nothing.

## Next

MVP step 4, sub-step 5 —
`track_surprises`: rank correlation, permutation `p`, hit rate, slope, verdict; the statistics move
to `stats.py` (part C of the `study.py` review).

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-10-05 | Step 4.4: `load-surprises` — 1,287 surprises stored | PR #95 |
| 2026-10-05 | Step 4.3: Cleveland Fed nowcast; expected value before each release | PR #94 |
| 2026-10-05 | Step 4.2: first-published m/m, core and headline, with the January fix | PR #92 |
| 2026-10-05 | `sources.py`: FRED and Yahoo requests and parsing moved out of `study.py` | PR #91 |
| 2026-10-05 | Step 4.1: `cpi_surprises` table and its schema doc | PR #90 |
| 2026-10-05 | `study.py` regrouped by step; no behaviour change | PR #89 |
| 2026-10-05 | `daily_bars` rebuilt per instrument; gold cross-checked, not replaced | PR #88 |
| 2026-10-05 | Step 4 spec: does the move follow the CPI surprise? | PR #87 |
| 2026-10-05 | Step 3.4: Results — step 3 complete; CPI moves UST 10Y, DXY, VIX | PR #86 |
| 2026-10-02 | Step 3.3: `raw-move` CLI — verdicts, eras, rule | PR #85 |
| 2026-10-02 | Step 3.2: `compare_moves` — ratio, permutation `p`, verdict | PR #84 |
| 2026-10-02 | Step 3.1: `daily_moves` and `cpi_days`; CPI-day moves match step 2 | PR #83 |
| 2026-10-02 | Step 3 spec: raw move on CPI days; precision doc | PR #82 |
| 2026-10-02 | Release dates checked against BLS; Nov 1992 corrected; weekend guard | PR #81 |
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
| 3 Raw move | Done — moves: UST 10Y, DXY, VIX; doesn't: S&P 500, gold |
| 4 Surprise | In progress — spec, 4.1–4.4 done |

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- `obs_id` depends on the order of `MVP_PRICE_SERIES` and leaves room for ten instruments.
- The `Prediction` model has no table and no caller.
- CPI release dates for 1972–1989 have not been checked against BLS (its reports for those years
  were not reachable). Later dates are checked; see step 1's spec.
