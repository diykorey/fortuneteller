# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

Jobs-report forecast, step 1 — the inputs (`expectations.load_model_inputs`): ADP's first-published
monthly change from both FRED series (185 months, 2011 on, none for June–August 2022; four checked
against ADP's releases) and the change in 4-week-average jobless claims between survey weeks (207
months, 2009 on). *(PR #112.)*

## In progress

**Country-aware events**: [country-aware-events.md](steps/country-aware-events.md). Spec under
review. The jobs-report forecast is paused after its step 1 until this is done.

## Next

Country-aware events, step 1 — flow identity: `country` and `zone` on `EventFlow`, stored events
read by (event type, country), duplicate flows refused, release dates in the flow's zone.

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-10-07 | Jobs-report forecast spec and step 1: ADP and claims inputs | PR #112 |
| 2026-10-06 | Event flows step 4: the recipe; a made-up flow and source plug in — refactor complete | PR #111 |
| 2026-10-06 | Event flows step 3: the CLI and measurement driven by the flows | PR #110 |
| 2026-10-06 | Event flows step 2: CPI, NFP and Fed as flows behind `EVENT_FLOWS` | PR #109 |
| 2026-10-06 | Event flows spec and step 1: expectation sources, validated surprises | PR #108 |
| 2026-10-06 | Rung 1.8: Results; rung 1 section in `mvp-results.md` — rung 1 complete | PR #107 |
| 2026-10-06 | Rung 1.7: NFP surprise; yield and dollar follow it but miss the hit-rate bar | PR #106 |
| 2026-10-06 | Rung 1.6: clean baseline; CPI and NFP verdicts hold, Fed's dollar just moves | PR #105 |
| 2026-10-06 | Rung 1.5: reaction close by event time; gold moves on Fed days (1.79) | PR #104 |
| 2026-10-05 | Rung 1.4: Fed decisions since 1994; S&P 500 and VIX move; gold's close precedes them | PR #103 |
| 2026-10-05 | Rung 1.3: every event's moves; `raw-move --event` — NFP moves all five | PR #102 |
| 2026-10-05 | Rung 1.2: NFP releases; dates checked against BLS since 1994 | PR #101 |
| 2026-10-05 | Rung 1.1: generic event keys; `surprises` | PR #100 |
| 2026-10-05 | Rung 1 spec: more events — NFP and Fed decisions | PR #99 |
| 2026-10-05 | Step 4.7: Results and `mvp-results.md` — step 4 and the MVP complete | PR #98 |
| 2026-10-05 | Step 4.6: `surprise` CLI — verdict and context tables | PR #97 |
| 2026-10-05 | Step 4.5: `track_surprises`; shared statistics in `stats.py` | PR #96 |
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
| 4 Surprise | Done — tracks: UST 10Y; unclear: DXY; doesn't: VIX, S&P 500, gold |

## Rung 1 progress

| Event | Step 3 (moves?) | Step 4 (follows the surprise?) |
| --- | --- | --- |
| CPI (clean baseline) | moves: UST 10Y, DXY, VIX; doesn't: S&P 500, gold | as the MVP |
| NFP | moves: all five | unclear: UST 10Y, DXY, gold; doesn't: S&P 500, VIX |
| Fed | moves: S&P 500, DXY (borderline), gold, VIX; unclear: UST 10Y | none: no free expected value |

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- The `Prediction` model has no table and no caller.
- CPI release dates for 1972–1989, and NFP release dates before 1994, have not been checked against
  BLS. Later dates are checked; see step 1's spec and rung 1's.
- In 1990–2007 the 10-year yield and the dollar move more the day after a Fed decision than on the
  day; either their close then came before the statement, or the reaction ran on. See
  [Precision](precision.md), "Close times".
