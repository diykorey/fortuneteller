# What follows a hurricane landfall

> Step 28 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the fifth of phase 5,
> *weather and climate*. Terms are in the [Glossary](../glossary.md): *kind*, *span*, *base rate*,
> the four answers, *HURDAT2*, *landfall*, *lesser release*.

## The goal

**In plain words:** when a hurricane came ashore on the US coast, what did gasoline, natural gas,
oil, energy stocks, the crops, an insurer's shares and every other market do over the next day,
week and month?

At the end, `fortuneteller follows --event weather` prints [step 17's](what-follows.md) table for
these landfalls, as [war's](war.md) does, and a trigger file may name `weather`, so the next
hurricane in the news can be answered from its past.

## The way to reach it

- **The days come from a record nobody here picks.** The National Hurricane Center's Atlantic
  best track, HURDAT2 (`hurdat2-1851-2025-092326.txt` from
  [nhc.noaa.gov/data/hurdat](https://www.nhc.noaa.gov/data/hurdat/), free, read 2026-11-18): every
  Atlantic storm since 1851, six-hourly, with each landfall as its own row, marked `L`, at its
  minute in UTC, its place and its wind. It ends with the 2025 season; 2026's storms join with a
  dated amendment when the NHC adds them.
- **The kind: a storm's first US landfall as a hurricane**, one kind, *landfall*: the earliest
  row of a storm marked `L` (a landfall) with status `HU` (a hurricane, 64 knots or more; the
  record's other statuses, tropical storm `TS` and below, are not taken) whose place is on the US
  mainland or the Florida Keys. A storm that first came ashore weaker and later as a hurricane is
  taken at the hurricane's landfall. The place rule, written now: latitude 24.4°N or more,
  longitude 66.9°W or west (not Nova Scotia), below 47.5°N; south of 32°N only west of 80.0°W (not
  the Bahamas); west of 96.5°W only from 25.95°N (not Mexico). Puerto Rico is not the mainland and
  is not taken. Since 1970: **79 storms**, 1970-08-03 (Celia) to 2024-10-10 (Milton), no two on
  one day, 26 major (96 knots or more), 18 on a weekend.
- **The hour is the record's own**, in UTC: a landfall after a market's close reacts on its next
  close. 8 of the 79 come between 16:00 and 20:00 UTC, the hours that tell UTC from New York's
  time on New York's close (Michael, 2018-10-10 17:30 UTC, 13:30 New York, reacts that day); 18
  fall on a weekend by the UTC day and react on Monday. **Known misses, written now:** a storm's
  first US landfall is not always its worst: Katrina is read on 2005-08-25 in Florida, not
  2005-08-29 in Louisiana; Andrew on 1992-08-24 in Florida, not 08-26 in Louisiana. A storm that
  came ashore as less than a hurricane (Sandy, 2012) is not taken. Markets moved on the forecast
  for days before; the landfall is the day it happened, not the day it was known.
- **One market added: Allstate** (`ALL`, Yahoo, from 1993-06-03, 16:00 New York; *ALL*), the
  largest US home insurer listed for that long, **unsigned** (sign 0 in every flow's rule: no live
  link, as [step 25's](other-central-banks.md) pound, yen and Nikkei). The fuel and the
  crops are stored already: gasoline (UGA), natural gas (UNG), Brent, energy stocks (XLE), corn,
  wheat, soybeans. Landfalls after each market's first close ([Schema](../schema.md),
  *How much data*): the S&P 500, the 10-year and 5-year yields and the Nikkei 79; the dollar index
  and the Nasdaq 78; the FTSE 100 72; the DAX 62; VIX 58; Allstate 56; the yen 52; energy stocks
  and utilities 48; gold and coffee 45; the breakeven 44; the euro, the STOXX 600 and the pound 42;
  the Euro Stoxx 50, defence stocks, Brent, homebuilders and natural gas 32; gasoline 31; corn 28;
  wheat and soybeans 27; bitcoin 25; ether 20; Coinbase 10.
- **Lesser, as war's:** each day stays an ordinary day for every other flow; `raw-move --event
  weather` keeps the flow's own lone days. `follows` keeps every landfall; the results name days
  shared with another flow (`scripts/shared_days.py`), by the landfall's UTC day.
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES` (31 with Allstate),
  and both runs, `follows` from the close before and `follows --after-the-day` from the reaction
  close.

## The rule, fixed before anything is shown

- The source, the place rule, the first landfall, the hour, the market and step 17's bars,
  unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: 30 graded walk-forward needs 40 events ([OPEC's](opec.md) rule).
  On the day, the 19 markets with 42 or more above have 40 counted; the 12 with 32 or fewer,
  among them the fuel funds, Brent and the crops, are *too few* walk-forward on every span. The
  week's and the month's counts, after overlap, are recorded, not predicted.
  - The header: `follows: 79 hurricane landfalls 1970-08-03 … 2024-10-10: 79 landfalls`.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Gasoline, natural gas, Brent, energy stocks, the three crops and Allstate on the day, the week
  and the month: *can't say*, in both runs. A storm is forecast days ahead; whatever it does to
  refineries, fields and claims is priced before it lands.
  - Every other flow's `follows` and `raw-move` output unchanged byte for byte but Allstate's rows
  (step 1), which are recorded, not judged; each other `follows` chance line and the scoreboard's
  three chance counts (raw-move, surprise, walk-forward) rise by Allstate's cells alone, written
  before and after.
- **Outside the rule, recorded:** `raw-move --event weather`. Nothing is expected.

*Written 2026-11-18, before Allstate's closes were loaded and before `follows` or `raw-move` ran on
these landfalls; the counts above are from the record and the markets' first closes.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Allstate: seed row, series, `load-prices`; the seed `data/seed/hurricanes.csv` (`day,time,kind,storm,knots`) from the record by `scripts/hurdat_landfalls.py` | `load-prices` stores it; each close of 2026-11-09 to 2026-11-13 within 0.05% of Yahoo's last hourly bar before 16:00 New York (`interval=60m`), a miss recorded, not the bar changed; the seed test checks the header, 79 rows, order, kind `landfall`, each at 64 knots or more, each `lat`/`lon` inside the place rule, and the rows named below. On a copy of the store, before and after: every other flow's `raw-move` and `follows` output (both runs, the Fed's `--long`) identical once Allstate's rows and the chance lines are taken out, and the scoreboard's data once Allstate and its chance are taken out; each chance line written here |
| 2 | Flow `weather`; `follows --event weather`; `weather` in `TRIGGER_KINDS` | Tests: Michael's landfall, 2018-10-10 17:30 UTC, reacts that day in New York and the next day in Tokyo; Harvey's, Saturday 2017-08-26 03:00 UTC, on Monday; a `weather` trigger for a day not stored is answered from a landfall at 04:00 UTC that day, as war's. On a copy of the store the header is the expected one, and every other flow's output byte for byte the one of step 1's store |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet marked right or wrong with its numbers and command; each cell with 30 or more graded walk-forward and its record; the days shared with another flow, by the landfall's UTC day |

## How you know it is right

- **The rows match the record and the news:** five named now, each checked by hand against its
  NHC Tropical Cyclone Report (the Hurricane Center's report on each storm) for the day, the hour
  within 30 minutes and the US state: 1992-08-24 08:40 Andrew (145 knots, Florida), 2005-09-24
  07:40 Rita (100, Louisiana), 2008-09-13 07:00 Ike (95, Texas), 2017-08-26 03:00 Harvey (115,
  Texas), 2022-09-28 02:00 Ian (110, the Dry Tortugas, Florida's Keys).
- **No foreign landfall, by hand:** the record's hurricane landfalls the rule must leave out,
  named now: Matthew 2016-10-07 and Nicole 2022-11-09 on Grand Bahama, Dorian 2019-09-01 on Abaco,
  Maria 2017-09-20 on Puerto Rico, Katia 2017-09-09 and Grace 2021-08-21 in Mexico; none is in the
  seed. Matthew, Nicole and Dorian are in it at their later US landfalls.
- **The hour is UTC:** Michael's test above; read in New York's time, it would react a day late.
- **Nothing else changes:** every other flow's output on a copy of the store.

## What this step does not do

Only US hurricane landfalls: not floods or droughts, which have no single start day in a free
record (the US Drought Monitor is weekly and its onset is a judgement); not tropical storms below
hurricane strength, nor storms that only brushed the coast; not Pacific storms. No other insurer.
Not on the page's [*ask*](ask-the-fortune-teller.md). No live link. Days are shared by the
landfall's UTC day, as war's: a landfall after a close that shares only its reaction close with
another flow is not named.

## Technical details

- **Market:** `ALL` (`ALL`, 16:00 New York) in `study.MVP_PRICE_SERIES`, a seed row in
  `data/seed/instruments.csv`, sign 0 in every flow's rule.
- **Seed:** `data/seed/hurricanes.csv`, columns `day`, `time` (the record's UTC minute), `kind`
  (`landfall`), `storm` (the record's name), `knots`, `lat` and `lon` (degrees, west negative), written by `scripts/hurdat_landfalls.py`
  from the downloaded record, which is not committed. Documented in `docs/legacy/data/README.md`.
- **Flow:** a `DatedShockFlow` in `flows.py`: event type `Natural disaster` (already seeded),
  country `United States`, zone UTC, type code 32, `weather`, detail the storm; `lesser`,
  unscheduled. One kind in `study.ONE_KIND`. `FOLLOWS_NOUNS` gains `hurricane landfalls`;
  `TRIGGER_KINDS` gains `weather` with `landfall`; a live trigger's landfall is made at 04:00 UTC
  on its day, as war's (`study.SHOCK_HOUR`): one after that day's close is read a day early, a
  known miss.
- **Tests** in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`,
  `tests/test_study_raw_move.py`.
- **Docs:** this spec; `docs/schema.md` (code 32, the detail, `event_ts`, the instrument); the
  glossary (*HURDAT2*, *landfall*, *ALL*); roadmap row 28 amended to landfalls; status, changelog.
