# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

The US manufacturing survey (ISM), spec: ISM's index as an event flow with its surprise against
TradingView's forecast, and the flash-day check repeated without ISM days. *(PR #173.)*

## In progress

The US manufacturing survey (ISM), step 1 (this change): the flow, read from TradingView's
calendar through one flow shared with the euro-area flash. [Spec](steps/ism-manufacturing.md).

Also waiting: release-day job step 3, evening score step 2 and rung 6 step 2: the first release the morning job
logs, pops up and the evening grades, waiting for the next CPI or retail sales release.

## Next

The US manufacturing survey (ISM), step 2: results, and the flash-day check without ISM days.

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-10-23 | The US manufacturing survey (ISM), spec | PR #173 |
| 2026-10-22 | Cross-country effects, part 3, step 2: results — the flash moves New York, not Europe; nothing follows its surprise | PR #171 |
| 2026-10-22 | Cross-country effects, part 3, step 1: the flash HICP flow; two GDP verdicts changed by shared days | PR #170 |
| 2026-10-22 | Cross-country effects, part 3, spec: euro-area inflation, the flash HICP and its surprise | PR #169 |
| 2026-10-22 | Cross-country effects, part 2, step 2: results — the ECB moves the dollar, not Europe's stocks | PR #168 |
| 2026-10-22 | Cross-country effects, part 2, step 1: the ECB flow | PR #167 |
| 2026-10-22 | Cross-country effects, part 2, spec: ECB decisions | PR #166 |
| 2026-10-21 | Cross-country effects, part 1, step 2: results — Europe follows CPI's surprise more than New York | PR #165 |
| 2026-10-21 | Cross-country effects, part 1, step 1: the DAX and Euro Stoxx 50 loaded | PR #163 |
| 2026-10-21 | Cross-country effects, part 1, spec: US releases against Europe's stocks | PR #162 |
| 2026-10-21 | Rung 6 step 1: the desktop popup; failure reports fixed (broken since #151) | PR #161 |
| 2026-10-21 | Rung 6 spec: delivery as a desktop popup | PR #160 |
| 2026-10-20 | The record, not a probability, step 2: the call line without a percentage | PR #159 |
| 2026-10-20 | The record, not a probability: spec; an honest probability passes rung 3 one time in five at 80 calls | PR #158 |
| 2026-10-20 | The evening score installed: the timer on, one check run clean | PR #157 |
| 2026-10-20 | The evening score step 1: `release-day.sh score`, its timer, one lock for both jobs | PR #156 |
| 2026-10-19 | The evening score spec: the day loaded and scored unattended | PR #155 |
| 2026-10-19 | Rungs 4 and 5 results: the first live calls graded, verdicts "too few"; both rungs done | PR #154 |
| 2026-10-16 | The release-day job catches up a start missed while the laptop was off | PR #153 |
| 2026-10-15 | The release-day job installed: the timer on, one check run clean | PR #152 |
| 2026-10-15 | Release-day job step 2: the script and its systemd timer | PR #151 |
| 2026-10-15 | The first release logged with `--fetch`: retail sales, 0.8 against 0.3 | PR #150 |
| 2026-10-15 | Release-day job step 1: `fortuneteller live` | PR #149 |
| 2026-10-14 | Release-day job spec: the call logged and its pull request opened unattended | PR #148 |
| 2026-10-14 | Rung 5 step 1: TradingView's CPI actual at most 8 s after 08:30, equal to the typed one | PR #147 |
| 2026-10-14 | The first live call: CPI 2026-10-14, core 0.3 against 0.2 | PR #146 |
| 2026-10-13 | Rung 5 step 2: `predict --fetch` reads the actual from TradingView | PR #145 |
| 2026-10-13 | Rung 5 spec: the live path, `predict --fetch` from TradingView | PR #144 |
| 2026-10-13 | Consensus fallback step 2: results — every verdict stands; retail's yield confidence too close to tell | PR #143 |
| 2026-10-13 | Consensus fallback step 1: TradingView's forecast where Nasdaq has no row | PR #142 |
| 2026-10-13 | Consensus fallback spec: TradingView's forecast where Nasdaq has none | PR #141 |
| 2026-10-13 | Rung 4 spec: the calls' pull request opens right after logging, before gold's close | PR #140 |
| 2026-10-13 | Rung 4 step 2: `score` grades the logged calls beside the replay | PR #139 |
| 2026-10-13 | Rung 4 step 1: `predict --actual` logs every link's line to `data/calls.csv` | PR #138 |
| 2026-10-13 | Rung 4 spec: keep score | PR #137 |
| 2026-10-12 | Step 4 step 3: results — retail sales' yield holds; core PCE and GDP no calls; step 4 complete | PR #136 |
| 2026-10-12 | Step 4 step 2: consensus surprises for the three; retail sales' yield tracks | PR #135 |
| 2026-10-12 | Step 4 step 1: retail sales, core PCE and GDP flows; GDP and retail sales move the yield and the dollar | PR #134 |
| 2026-10-12 | Step 4 spec: more events — retail sales, core PCE, GDP | PR #133 |
| 2026-10-12 | Rung 3 step 4: results — the bands are honest, the probabilities not; rung 3 complete | PR #132 |
| 2026-10-12 | Rung 3 step 3: `predict --actual` gives each call's probability and band | PR #131 |
| 2026-10-12 | Rung 3 step 2: `predict` grades each link's stated confidence | PR #130 |
| 2026-10-12 | Rung 3 step 1: `confident_calls`, a probability and a band per call | PR #129 |
| 2026-10-12 | Rung 3 spec: honest confidence — a probability and a band per call, graded | PR #128 |
| 2026-10-12 | Rung 2 step 4: results — jobs-report links hold, the dollar clearly; CPI too few; rung 2 complete | PR #127 |
| 2026-10-12 | Rung 2 step 3: `predict --actual`, the next release's call | PR #126 |
| 2026-10-12 | Rung 2 step 2: `predict`, each link's walk-forward record and verdict | PR #125 |
| 2026-10-12 | Rung 2 step 1: the walk-forward replay | PR #124 |
| 2026-10-12 | Rung 2 spec: predict the next release, tested walk-forward | PR #123 |
| 2026-10-09 | Free consensus step 3: results — jobs-report links pass, stronger; CPI's dollar passes against the consensus | PR #122 |
| 2026-10-09 | Free consensus step 2: Nasdaq's consensus as a source, judged beside the trend | PR #121 |
| 2026-10-09 | Free consensus: spec revised to Nasdaq; step 1, the calendars fetched and matched | PR #120 |
| 2026-10-09 | Data sources survey: ~250 free sources from FinceptTerminal graded; Nasdaq, TradingView and Forex Factory consensus compared | PR #119 |
| 2026-10-09 | Jobs-report forecast step 4: results — both links pass since 2014, against the trend too | PR #117 |
| 2026-10-09 | Jobs-report forecast step 3: the model beside the trend on the same reports | PR #116 |
| 2026-10-08 | Jobs-report forecast step 2: least squares and the payroll model | PR #115 |
| 2026-10-07 | Country-aware events step 2: trends and reports per flow, each market's zone — part 1 complete | PR #114 |
| 2026-10-07 | Country-aware events spec and step 1: flow identity by type and country | PR #113 |
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
| NFP | moves: all five | unclear: UST 10Y, DXY, gold; doesn't: S&P 500, VIX. Since 2014: UST 10Y and DXY track, against the forecast and the trend alike |
| Fed | moves: S&P 500, DXY (borderline), gold, VIX; unclear: UST 10Y | none: no free expected value |
| Retail sales (step 4) | moves: UST 10Y, DXY | against the consensus: UST 10Y tracks; DXY doesn't |
| Core PCE (step 4) | moves: VIX | none track: too few noticeable surprises |
| GDP (step 4) | moves: UST 10Y, DXY | none track; DXY unclear |

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- CPI release dates for 1972–1989, and NFP release dates before 1994, have not been checked against
  BLS. Later dates are checked; see step 1's spec and rung 1's.
- In 1990–2007 the 10-year yield and the dollar move more the day after a Fed decision than on the
  day; either their close then came before the statement, or the reaction ran on. See
  [Precision](precision.md), "Close times".
- Since 2008, 19 CPI releases share their day with retail sales, and 7 jobs reports with retail
  sales or core PCE; CPI's and the jobs report's tables keep those days. See
  [step 4](steps/step-4-more-events.md#shared-days).
