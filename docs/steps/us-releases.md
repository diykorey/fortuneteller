# The US releases with forecasts

> Step 64 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-27 by the owner
> from a review of possible sources, after [the 2-year yield](two-year-yield.md)
> ([Decisions](../decisions.md)). Built as [jobless claims](jobless-claims.md) were built: lesser
> flows from TradingView's calendar, each against its forecast. Terms are in the
> [Glossary](../glossary.md): *lesser release*, *days alone*, *noticeable*, *kind*, *holds*, the
> four answers, *PPI*, *JOLTS*, *Michigan sentiment*, *housing starts*, *durable goods orders*.

## The goal

**In plain words:** five more US reports come with a forecast. They cover prices factories charge,
job openings, how confident shoppers feel, new homes started, and orders for long-lasting goods.
When one comes in above or below its forecast, what do markets do, and does any of it repeat
well enough to call?

At the end: five flows, `ppi`, `housing`, `durable`, `jolts` and `umich`, each with `raw-move`,
`surprise`, `predict` and `follows --event <flow>`, a trigger kind (*above*, *as expected*,
*below*) and a place on the page's *Ask the fortune teller*, as claims has. A link on one that
holds walk-forward is called by the morning job if it lands at 08:30.

## The way to reach it

- **TradingView's US calendar,** the quarters `load-releases` already fetches for ISM and claims,
  one row per flow. Read 2026-11-28 from the cached quarters to 2026-09-30, releases with an
  actual and a forecast:

  | Flow | Row | Event type | Releases, first forecast | Hour (New York) | Printed step | Median miss | Noticeable from | Signs |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | `ppi` | `PPI MoM` | `CPI / inflation surprise` | 160, 2013-03-14 | 08:30 | 0.1 pp | 0.2 pp | 0.1 pp | CPI's |
  | `housing` | `Housing Starts` | `Real-estate / housing data` | 153, 2013-03-19 | 08:30 | 0.001 m | 0.111 m | 0.074 m | the jobs report's |
  | `durable` | `Durable Goods Orders MoM` | `Other macro data (GDP/PMI/PCE/retail/claims)` | 163, 2013-03-26 | 08:30 | 0.1 pp | 1.2 pp | 0.8 pp | the jobs report's |
  | `jolts` | `JOLTs Job Openings` | `Other macro data (GDP/PMI/PCE/retail/claims)` | 143, 2014-07-08 | 10:00 | 0.001 m | 0.21 m | 0.14 m | the jobs report's |
  | `umich` | `Michigan Consumer Sentiment Prel` | `Other macro data (GDP/PMI/PCE/retail/claims)` | 140, 2015-02-13 | 10:00 | 0.1 points | 2.3 points | 1.5 points | the jobs report's |

  *Noticeable from* is two thirds of the median miss against TradingView's forecast, rounded to
  the report's printed step, as for claims and [the German surveys](germany-calendar.md). The
  actual is rounded to that step before its kind is read. *m* is millions of jobs or homes, at an
  annual rate for homes; *pp* is percentage points. The threshold is read from every release's
  miss, as claims' and the surveys' were: it sets which surprises count, not any verdict, and no
  market's move was looked at. Each flow's events carry its own row as their measure, so two
  flows under one event type stay apart, as ISM's and claims' do. Loaded from 2013-01-01, as ISM;
  a release with no forecast has no kind and is in no surprise or `follows` table.
- **First prints.** In the cached quarters the actual is the figure first published, not a
  revision: it differs from the next release's *previous* (TradingView's revised figure) on 154 of
  157 housing starts, 149 of 162 durable goods and 145 of 147 job openings; producer prices are
  revised less often (47 of 160). Claims found TradingView's open quarter carrying revised
  figures ([jobless claims](jobless-claims.md)); a quarter is cached only once it is over.
- **Which row, of several.** The headline PPI, not core: it has more forecasts (160 against 157)
  and starts four months earlier. Michigan's preliminary reading, not the final one: the
  preliminary is the news, and the final shares its day with core PCE on 75 of its 140 releases, so it would rarely be
  alone. Housing
  starts, not building permits, which are released at the same minute and have fewer forecasts
  (112). Each row stands for its whole release, as industrial production does for China's.
- **Signs, from a reason written first.** Producer prices are inflation news, so they take CPI's
  signs (`EXPECTED_SIGN`): hotter means the yields, the dollar, VIX and the breakeven up, the
  S&P 500, the DAX, the Euro Stoxx 50 and homebuilders down. The other four are growth news, so
  they take the jobs report's (`NFP_EXPECTED_SIGN`), as ISM does: stronger means the yields and
  the dollar up, stocks unsigned. The markets added since take theirs from these, as for every flow
  ([more outcomes](more-outcomes.md)). No sign comes from a result.
- **The hours.** The code places each release by its hour, so each market reacts at its first
  close after it. 08:30 and 10:00 New York are before New York's closes and Frankfurt's 17:30, so
  those react the same day, as for ISM; Tokyo's close has passed, so it reacts the next day.
  Releases from 2013 to 2015 in summer are stamped an hour late (09:30 or 11:00), still before
  those closes, so the reaction day is the same. JOLTS and Michigan land after the morning job
  (08:30 to 09:00 New York), so a link on them cannot be called live, as ISM's cannot.
- **Lesser, all five,** as claims: each day stays an ordinary day for every flow outside the five,
  so no such flow's base or row changes. Each table keeps only its days alone: no release that day
  of a flow that is not lesser, and none of another of the five built so far. So each new flow
  takes the days it shares out of the earlier ones' tables too. Counted by hand 2026-11-28
  against CPI, the jobs report, retail sales, GDP's advance print, core PCE, ISM and the Fed, a
  day matched by its New York date, the expected headers after each step (releases alone: above /
  as expected / below) are:

  | After step | `ppi` | `housing` | `durable` | `jolts` | `umich` |
  | --- | --- | --- | --- | --- | --- |
  | 1 | 125: 60 / 18 / 47 | | | | |
  | 2 | 119: 55 / 18 / 46 | 124: 35 / 53 / 36 | | | |
  | 3 | 118: 55 / 18 / 45 | 123: 34 / 53 / 36 | 125: 48 / 44 / 33 | | |
  | 4 | 118: 55 / 18 / 45 | 119: 32 / 51 / 36 | 125: 48 / 44 / 33 | 123: 44 / 49 / 30 | |
  | 5 | 103: 46 / 17 / 40 | 110: 29 / 47 / 34 | 125: 48 / 44 / 33 | 119: 43 / 47 / 29 | 60: 17 / 21 / 22 |

  The code's count may differ by the flows the hand count left out (the ECB, the BoE, euro-area
  inflation and the other flows that are not lesser) and by the cached quarters ending at
  2026-09-30. Each step runs the new flow's header before its table and writes any difference
  here with a dated amendment, naming the days that make it. Only then is the table read.
- **The bars, unchanged:** rung 1's `raw-move` (*moves*: a median move ratio ≥ 1.10 to ordinary
  days and p < 0.01); step 4's `surprise` (*tracks*: rank correlation p < 0.01 and the expected
  way on ≥ 60% of noticeable surprises); `predict`'s walk-forward (*holds*: right on ≥ 60% of ≥ 30
  predictions, p < 0.01); and [step 17's](what-follows.md) `follows` over every market and its
  spans (the day, the week, the month), from the close before and from the reaction close
  (`--after-the-day`). An answer needs 10 events of a kind and chance < 0.01; a cell *holds* with
  ≥ 30 graded walk-forward, each after ten earlier, right on ≥ 60% and 10 points above their mean
  base rate.

## The rule, fixed before anything is shown

- The sources, the rows, the thresholds, the signs, the hours and every bar above, unchanged by
  what a run shows.
- **Expected outcome, written first:**
  - The headers above, or the difference amended with its date before the table is read.
  - Arithmetic, not a finding: a cell needs 40 events of its kind to hold (30 graded, each after
    ten). After step 5 only `ppi` *above* and *below*, `housing` *as expected*, `durable` *above*
    and *as expected*, and `jolts` *above* and *as expected* have 40; no `umich` cell can hold.
  - `raw-move`: *moves* in the 2-year and the 5-year on PPI's and JOLTS' days, as producer prices
    and job openings are read for the Fed's next move and the short yields carry it; on housing
    starts', durable goods' and Michigan's days, no more than 2 markets *move* (38 markets at
    p < 0.01 give 0.4 by chance).
  - `surprise`: on each flow, at most 2 markets *track* (0.4 by chance).
  - `predict`, walk-forward: nothing *holds*, so no live call is added.
  - `follows`, on all history: no more answers than the chance line it prints plus 2, for each
    flow and each run (ten checks).
- **Every existing row unchanged.** On a copy of the store, every other flow's `raw-move`,
  `surprise`, `predict` and `follows` output (both runs), and the scoreboard's `data.json`, are
  compared before and after each flow is added, with the lines and entries naming the new flow
  and the chance lines dropped. The diff must be empty for every flow outside the five; the five
  built before change only by the days the new one shares, their headers as in the table.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Producer prices: `ppi`, a TradingView row, a surprise rule, the flow, its trigger kind and *Ask* | Tests: the surprise is the actual less the forecast, *above* from 0.1; a day shared with CPI is left out of its table; a 09:30 stamp reacts on that day's New York close; a `ppi` trigger of kind *above* gets `follows`' answers for *above*; *Ask*'s `ppi` cells are as many as `follows --event ppi`'s lines, each with the same counts. The header equal to the one above, or amended; the comparison's diff empty; the scoreboard's rebuild time here, under the evening job's `TimeoutStartSec` of 60 minutes ([the evening score](evening-score.md)) |
| 2 | Housing starts: `housing` | As step 1, *above* from 0.074 m; a day shared with `ppi` left out of both tables, and `ppi`'s header after step 2 as above; the diff empty outside the five |
| 3 | Durable goods: `durable` | As step 2, *above* from 0.8 pp |
| 4 | Job openings: `jolts` | As step 2, *above* from 0.14 m; a 10:00 release reacts on that day's New York close |
| 5 | Michigan sentiment: `umich` | As step 2, *above* from 1.5 points |
| 6 | Results here, in [MVP results](../mvp-results.md) and the roadmap row | Each verdict against the expected outcome, with every number its bar needs and the command that prints it |

## How you know it is right

- **The rows:** a test serves each row through the patched calendar, and the flow's events carry
  its event type, its hour and TradingView's forecast. A row with no actual is not stored.
- **The kinds:** a release exactly at its threshold is *above* or *below*; one a step under is
  *as expected*; the actual is rounded to its step first.
- **Alone:** a release on a CPI day, and one on another of the five's day, is in no table of its
  flow; every other flow's tables are unchanged (the empty diff).
- **By hand:** for each flow, three releases (its first, one in 2020 and its last). The actual is
  read against the agency's own first release for that month (the BLS for producer prices and job
  openings, the Census Bureau for housing starts and durable goods, the University of Michigan),
  not TradingView's page; the forecast and the kind are written down beside it.
- **First prints:** the share of releases whose actual differs from the next release's
  *previous*, per flow, written in its step; a flow where they always agree is checked against
  the agency's release, as claims were against FRED.

## What this step does not do

No new market. No core PPI, building permits, Michigan's final reading or inflation expectations,
new or existing home sales, or the regional Fed surveys. Nothing before TradingView's first
forecast, and no second consensus to check its forecasts against. No change to the bars, the
signs of other flows or the front page's areas.

## Technical details

- **`sources.py`:** five `TradingViewRow`s, country `US`, zone New York, from 2013-01-01 (JOLTS
  and Michigan from their first forecast's year).
- **`flows.py`:** five `SurpriseRule`s with `predicted_from=TRADINGVIEW_FORECAST` and
  `alone=True`, `ppi` with CPI's signs and the others with the jobs report's; five
  `TradingViewFlow`s with `lesser=True`, added to the flows list.
- **`__main__.py`:** each flow's plain name. **`data/seed/event_types.csv`:** no new row.
- **Docs, each step:** this spec's note, `docs/schema.md` (the event types filled), the glossary,
  status, the changelog. **Results:** here, `docs/mvp-results.md`, the roadmap row.
