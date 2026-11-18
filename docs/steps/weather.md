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
- **The kind: a hurricane's first landfall on the US coast**, one kind, *landfall*: a row marked
  `L` with status `HU` (a hurricane, 64 knots or more) whose place is on the US mainland or the
  Florida Keys, taken only once per storm, at its first. The place rule, written now: latitude
  24.4°N or more, longitude 66.9°W or west, below 47.5°N; south of 32°N only west of 80.0°W (not
  the Bahamas); west of 96.5°W only from 25.95°N (not Mexico); north of 43.6°N only west of 70°W
  (not Canada). Since 1970: **79 storms**, 1970-08-03 (Celia) to 2024-10-10 (Milton), no two on
  one day, 26 major (96 knots or more), 18 on a weekend.
- **The hour is the record's own**, in UTC: a landfall after a market's close reacts on its next
  close. 26 of the 79 come between 20:00 and 04:00 UTC. **Known misses, written now:** a storm's
  first US landfall is not always its worst: Katrina is read on 2005-08-25 in Florida, not
  2005-08-29 in Louisiana; Andrew on 1992-08-24 in Florida, not 08-26 in Louisiana. A storm that
  came ashore as less than a hurricane (Sandy, 2012) is not taken. Markets moved on the forecast
  for days before; the landfall is the day it happened, not the day it was known.
- **One market added: Allstate** (`ALL`, Yahoo, from 1993-06-03, 16:00 New York; *ALL*), the
  largest US home insurer listed for that long, **unsigned**, as step 25's three. The fuel and the
  crops are stored already: gasoline (UGA), natural gas (UNG), Brent, energy stocks (XLE), corn,
  wheat, soybeans. Landfalls after each market's first close: the S&P 500 79, energy stocks 48,
  Allstate 56, Brent, gasoline's and natural gas's funds 31 to 32, corn 28, wheat and soybeans 27.
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
  Allstate (56), energy stocks (48) and the markets stored before 1993 may have them on the day;
  the fuel funds, Brent and the crops (27 to 32) are *too few* walk-forward on every span. The
  week's and the month's counts are recorded, not predicted.
  - The header: `follows: 79 hurricane landfalls 1970-08-03 … 2024-10-10: 79 landfalls`.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Gasoline, natural gas, Brent, energy stocks, the three crops and Allstate on the day, the week
  and the month: *can't say*, in both runs. A storm is forecast days ahead; whatever it does to
  refineries, fields and claims is priced before it lands.
  - Every other flow's `follows` and `raw-move` output unchanged byte for byte but Allstate's rows
  (step 1), which are recorded, not judged; each other `follows` chance line and the scoreboard's
  chance rise by the added cells alone, written before and after.
- **Outside the rule, recorded:** `raw-move --event weather`. Nothing is expected.

*Written 2026-11-18, before Allstate's closes were loaded and before `follows` or `raw-move` ran on
these landfalls; the counts above are from the record and the markets' first closes.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Allstate: seed row, series, `load-prices`; the seed `data/seed/hurricanes.csv` (`day,time,kind,storm,knots`) from the record by `scripts/hurdat_landfalls.py` | `load-prices` stores it; each close of 2026-11-09 to 2026-11-13 within 0.05% of Yahoo's last hourly bar before 16:00 New York (`interval=60m`); the seed test checks the header, 79 rows, order, kind `landfall`, each at 64 knots or more, and the rows named below. On a copy of the store, before and after: every other flow's output identical but for Allstate's rows and the chance lines, each chance line and the scoreboard's written here |
| 2 | Flow `weather`; `follows --event weather`; `weather` in `TRIGGER_KINDS` | Tests: a landfall at 22:00 UTC reacts on the next day's close in New York; a `weather` trigger for a day not stored is answered from a landfall at the trigger's time. On a copy of the store the header is the expected one, and every other flow's output byte for byte the one of step 1's store |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet marked right or wrong with its numbers and command; each cell with 30 or more graded walk-forward and its record; the days shared with another flow, by the landfall's UTC day |

## How you know it is right

- **The rows match the record and the news:** five named now, each checked against its NHC
  Tropical Cyclone Report: 1992-08-24 08:40 Andrew (145 knots), 2005-09-24 07:40 Rita, 2008-09-13
  07:00 Ike, 2017-08-26 03:00 Harvey, 2022-09-28 02:00 Ian (at the Dry Tortugas, the Keys).
- **No foreign landfall:** none of the 79 is in the Bahamas, Cuba, Mexico or Canada, by the place
  rule; the seed test checks every row's place against it.
- **The hour:** a landfall at 03:00 UTC reacts on that day's New York close; one at 22:00 UTC on
  the next.
- **Nothing else changes:** every other flow's output on a copy of the store.

## What this step does not do

Only US hurricane landfalls: not floods or droughts, which have no single start day in a free
record (the US Drought Monitor is weekly and its onset is a judgement); not tropical storms below
hurricane strength, nor storms that only brushed the coast; not Pacific storms. No other insurer.
Not on the page's [*ask*](ask-the-fortune-teller.md). No live link.

## Technical details

- **Market:** `ALL` (`ALL`, 16:00 New York) in `study.MVP_PRICE_SERIES`, a seed row in
  `data/seed/instruments.csv`, sign 0 in every flow's rule.
- **Seed:** `data/seed/hurricanes.csv`, columns `day`, `time` (the record's UTC minute), `kind`
  (`landfall`), `storm` (the record's name) and `knots`, written by `scripts/hurdat_landfalls.py`
  from the downloaded record, which is not committed. Documented in `docs/legacy/data/README.md`.
- **Flow:** a `DatedShockFlow` in `flows.py`: event type `Natural disaster` (already seeded),
  country `United States`, zone UTC, type code 32, `weather`, detail the storm; `lesser`,
  unscheduled. One kind in `study.ONE_KIND`. `FOLLOWS_NOUNS` gains `hurricane landfalls`;
  `TRIGGER_KINDS` gains `weather` with `landfall`; a live trigger's landfall is made at the
  trigger's merge time.
- **Tests** in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`,
  `tests/test_study_raw_move.py`.
- **Docs:** this spec; `docs/schema.md` (code 32, the detail, `event_ts`, the instrument); the
  glossary (*HURDAT2*, *landfall*, *ALL*); roadmap row 28 amended to landfalls; status, changelog.
