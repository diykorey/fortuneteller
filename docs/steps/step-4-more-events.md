# More events — retail sales, core PCE, GDP

> Step 4 of the [Roadmap](../roadmap.md#next-steps-in-order)'s next steps, chosen 2026-10-12. Three
> event flows, as in [Extending](../extending.md), each then run up rungs 2 and 3. Follows the step
> template in the [Legend](../legend.md); terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** do the yield and the dollar follow a surprise in US retail sales, core PCE
inflation or GDP the way they follow the jobs report, and can it be predicted?

[Rung 3](rung-3-confidence.md#results) stopped on too few calls: about 60–80 per link, too few to
tell a stated probability from a coin. More events mean more links, and more calls on each.

At the end: `retail`, `pce` and `gdp` flows that every command accepts, each with Nasdaq's
consensus as its expected value, and their rung 1–3 results beside CPI's and the jobs report's.

## The events

| Flow | Measure | FRED series | Since | Since 2008 |
| --- | --- | --- | --- | --- |
| `retail` | Retail and food services sales, month on month, advance estimate | `RSAFS` | 2001 | 225 |
| `pce` | Core PCE prices, month on month | `PCEPILFE` | 2000 | 225 |
| `gdp` | Real GDP, quarter on quarter annualized, advance estimate | `GDPC1` | 1992 | 75 |

- **Release days** are each series' first-release dates, as for CPI and payrolls; the weekday guard
  applies. Two core PCE months came out on one day twice; the newer is kept, as for CPI.
- **Actuals** come from the levels as they stood on the release day (FRED's revision history), as
  for payrolls: Census and BEA revise the previous month or quarter in the same release, and the
  printed change is against the revised level. GDP: ((level / previous level)⁴ − 1) × 100.
- **Event types:** the seed has one row, `Other macro data (GDP/PMI/PCE/retail/claims)`, and a flow
  is its (type, country). So three rows are added to `data/seed/event_types.csv` (tier 3, both
  polarities): `Retail sales`, `PCE inflation`, `GDP growth`. The old row keeps PMI and claims.

## The expected value

Nasdaq's consensus only, through the existing `NasdaqConsensus` and its checks; the 12-month trend
comes free as context. Nasdaq and TradingView name the rows:

| Measure | Nasdaq | TradingView | Decimals | Gap |
| --- | --- | --- | --- | --- |
| Retail sales | `Retail Sales` | `Retail Sales MoM` | 1 | 0.3pp |
| Core PCE | `Core PCE Price Index` | `Core PCE Price Index MoM` | 1 | 0.2pp |
| GDP | `GDP` | `GDP Growth Rate QoQ Adv` | 1 | 0.5pp |

The month-on-month and year-on-year rows share a name; the row whose actual equals our first print
is the release's, as for CPI. GDP days also carry `Core PCE Prices` (quarterly), a different name.
A rebuilt GDP rate may differ from BEA's print by 0.1; such days get no consensus and are named in
`UNREADABLE_CONSENSUS`, not matched more loosely.

## Shared days

A close-to-close move on a day with two releases carries both. Counted 2026-10-12 since 2008:
retail shares 19 days with CPI, 13 with the Fed and 2 with the jobs report; GDP 11 with the Fed and
4 with core PCE; core PCE 5 with the jobs report.

**A new flow's release on a day holding another flow's release is left out of its surprise and
prediction tables, and listed.** That costs retail about 15% of its releases, against the reason
for this step, and is accepted: a call graded on a CPI day is graded on CPI. CPI's and the jobs
report's tables keep their shared days, so nothing measured so far changes; the 19 CPI days shared
with retail go under "Known, not yet fixed".

## The rule, fixed before any surprise is measured

| Flow | S&P 500 | Yield | Dollar | Gold | VIX | Noticeable |
| --- | --- | --- | --- | --- | --- | --- |
| Retail sales | 0 | + | + | 0 | 0 | 0.3pp |
| Core PCE | − | + | + | 0 | + | 0.1pp |
| GDP | 0 | + | + | 0 | 0 | 0.5pp |

Growth news takes the jobs report's signs, inflation news CPI's. Each cut-off is about two thirds
of a typical consensus miss as known from outside this project, as payrolls' 50k is against their
71k; it is not measured here. The verdict is on (measure, `nasdaq_consensus`). Rungs 1–3 apply
unchanged: the same tests, bars, `MIN_CALLS`, groups and COVID scope.

**Expected outcome, written down first:** retail is the one real candidate, with about 190
releases left and enough noticeable surprises for both rungs. Core PCE's consensus is usually
within 0.1pp, so few calls. GDP's 60 or so releases cannot reach 20 + 30 calls: too few for rung 3,
likely for rung 2.

**Disclosed:** choosing the rows, a handful of actuals and consensus values were seen (retail
2015-04, 2026-07, 2026-08; GDP 2015-04, 2020-07; core PCE 2015-04, 2020-07), and the counts above.
No move was looked at.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Seed rows; three flows from FRED with actuals from the release day's levels; `load-releases`, `load-prices`, `raw-move --event retail\|pce\|gdp`~~ **done** | A test per flow builds an actual against a revised previous level; release counts as above; raw-move printed. CPI's, the jobs report's and the Fed's raw move change (fewer ordinary days): old against new reported |
| 2 | ~~Consensus rows, the three surprise rules, shared days left out; `load-surprises`, `surprise --event …`~~ **done** | Every release since 2008 has its Nasdaq row matched by our first print, or is named; CPI's and NFP's `surprise` and `predict` output byte-identical to `main`'s |
| 3 | Results here and in [`mvp-results.md`](../mvp-results.md): `raw-move`, `surprise` and `predict` per flow | Says per flow and market whether it moves, tracks, holds walk-forward, and whether its confidence is honest, with and without COVID |

**Step 1, checked 2026-10-12.** `load-releases` stores 303 retail sales releases (2001 on), 312
core PCE (2000 on; February 2019 and October 2025 came out with the month after) and 139 GDP advance
estimates (1992 on). Built from real levels, the actuals match the printed figures: retail sales
+0.2% and −0.6% for June and July 2026, GDP +1.5% for the second quarter. Raw move, on every
release day, shared or not:

| Market | Retail sales | Core PCE | GDP |
| --- | --- | --- | --- |
| S&P 500 | unclear: 1.11 | unclear: 1.15 | unclear: 1.24 |
| 10-year yield | **moves: 1.33** | doesn't: 1.10 | **moves: 1.60** |
| Dollar | **moves: 1.20** | unclear: 1.11 | **moves: 1.45** |
| Gold | doesn't: 0.99 | unclear: 1.12 | doesn't: 1.10 |
| VIX | doesn't: 1.08 | **moves: 1.25** | doesn't: 1.10 |

With 754 more event days left out of the ordinary days, CPI's, the jobs report's and the Fed's
ratios shift by up to 0.06 and their p values slightly; every verdict stays the same.

**Step 2, checked 2026-10-12.** `load-surprises` stores 214 retail sales, 216 core PCE and 70 GDP
consensus surprises, 2008 on. Of the releases since 2008 without one:

- **Named, no single row matches our first print:** retail sales 2008-02-13 and 2009-02-12
  (Nasdaq's actual is 0.0 and −0.1, the prints +0.3 and +1.0); GDP 2011-04-28 and 2014-07-30 (our
  rate from levels 1.75 and 3.95, BEA's printed 1.8 and 4.0). Now in `UNREADABLE_CONSENSUS`.
- **Named, TradingView's gap:** GDP 2017-10-27, Nasdaq 2.5 against TradingView 3.3.
- **No Nasdaq row that day:** retail sales 9 (2008-01-15, 2009-03-12, 2019-10-16, 2020-02-14,
  2020-09-16, 2020-12-16, 2022-07-15, 2022-09-15, 2022-10-14), core PCE 7, GDP 2.

Shared days left out: 37 retail sales releases, 14 core PCE and 19 GDP. CPI's and the jobs report's
`surprise` and `predict` output is byte-identical to before.

| Market | Retail sales (184) | Core PCE (207) | GDP (57) |
| --- | --- | --- | --- |
| S&P 500 | doesn't | unclear | doesn't |
| 10-year yield | **tracks: 0.26, right 67% (97)** | unclear | doesn't: 29% (21) |
| Dollar | doesn't: 0.14, 58% (97) | doesn't | unclear: 0.29, 71% (21) |
| VIX | doesn't | unclear | doesn't |

Against the consensus, in brackets how many releases; hit rate on noticeable surprises. Core PCE
had 19 noticeable surprises in 207. Against the trend, nothing tracks.

## How you know it is right

- **The actuals are checked.** Nasdaq's row must carry our first print to the published decimal;
  a wrong level, day or formula fails the load, naming the day.
- **Nothing measured changes.** Every report but `raw-move` byte-identical for CPI, NFP and Fed.
- **Shared days.** A test plants a release on another flow's day and checks it is left out and
  listed, for the new flow only.

## What this step does not do

No ECB or other country (step 4a), no second or third GDP estimate, no headline PCE or retail
control group, no new expected value or market, no change to CPI's or NFP's tables.

## Technical details

Flows in `flows.py` reuse `_release_batch` and the payroll path's vintages
(`sources.fetch_vintages`); measure names `retail_sales`, `core_pce`, `gdp`; labels `RET`, `PCE`,
`GDP`; type codes 4–6. Rows in `expectations.CONSENSUS_ROWS`. `SurpriseRule.alone` (true for the
three) drops shared days where `study` reads a flow's surprise pairs. Seed rows documented in
`docs/legacy/data/events.md` and `docs/schema.md`.
