# Switzerland: the Swiss National Bank and Swiss inflation

> Step 54 of the [Roadmap](../roadmap.md), the last of the three countries the owner asked for on
> 2026-11-22 ("lets cover canada china and Switzerland"), after [Canada](canada.md) (step 52) and
> [China](china.md) (step 53). Built as Canada was: a central bank whose kind comes from its own
> history, and an inflation print against its forecast. Terms are in the
> [Glossary](../glossary.md): *kind*, *span*, *lesser release*, *alone*, *holds*, the four
> answers, *area*.

## The goal

**In plain words:** when the Swiss National Bank cuts, holds or raises its rate, or Swiss
inflation comes in above or below forecasts, what did each market do over the next day, week and
month, the franc and Zurich's stocks among them?

At the end: two markets more, the franc (USD/CHF) and Zurich's SMI; `fortuneteller follows
--event snb` and `--event chcpi` print [step 17's](what-follows.md) table; both are on the page's
*Ask the fortune teller*; and the two markets are in the guesser's list and in their
[areas](predicts.md) (currencies, stocks).

## The way to reach it

- **The SNB's days and hour: TradingView's calendar,** country `CH`, title `SNB Interest Rate
  Decision`, a quarter at a time, as the BoC's. Read 2026-11-23: 75 decisions from 2008-03-13 to
  2026-09-24, at 09:30 Zurich (14:00 for the March and September assessments of 2008 to
  2010); every one is before Europe's, Zurich's and New York's close, so those react the
  same day, Tokyo and the currencies (closed at 00:00 London) the next. One row, 2013-03-14, is
  stamped 00:00 Zurich (a date only): Tokyo's reaction to it is read a day early, a known miss.
- **The kind, from the SNB's own history,** as the BoC's: the midpoint of its target range for
  three-month Swiss franc LIBOR to 2019-06, its policy rate since, every change from 2008-01-01 in
  `data/seed/snb-changes.csv` (`day,time,rate`, `time` the Zurich hour of the SNB's press release),
  checked against the SNB's monthly series of official rates (`snboffzisa`, read 2026-11-23). A
  decision on a change's day is a *cut* or a *hike* by it; any other decision after the first is a
  *hold*; the first has no kind; a change the calendar lacks is added as an unscheduled decision.
  The 2019-06-13 switch from the range (midpoint −0.75%) to the policy rate (−0.75%) is a hold.
  - The calendar's own rates cannot give the kind: it has none for 2008 to 2009-03, and it
    lists 2015-03-19 at −0.75% from 0.125%, a cut, where the SNB held. The cuts came in its six
    unscheduled moves.
  - The six the calendar lacks, each a cut: 2008-10-08, 2008-11-06, 2008-11-20, 2011-08-03,
    2014-12-18 and 2015-01-15 (the end of the minimum exchange rate). The monthly series
    changes in each of those months (in 2008-11 by 1.5 points, the two cuts together) and in no
    other month of 2008 to 2015 but those of the scheduled cuts of 2008-12-11 and 2009-03-12. Any other disagreement is written here
    with a dated amendment before step 2. The minimum exchange rate of 2011-09-06 changed no rate
    and is not a decision.
  - With the SNB's history: 81 decisions, 80 with a kind: 14 cuts, 61 holds, 5 hikes. The event
    type is `Central-bank decision`, country `Switzerland`, a new row in `countries.csv`.
- **Swiss inflation: `Inflation Rate YoY`,** country `CH`, with TradingView's forecast: 227
  releases from 2008-01-04 to 2026-11-03, 223 with a forecast, at 08:30 or 09:15 Zurich (07:45 on
  12), each before Europe's close and on a weekday. The surprise is the actual, rounded to 0.1,
  minus the forecast, noticeable from 0.1 percentage point, the print's own step and its median
  absolute miss (0.1, read 2026-11-23): 64 above, 67 as expected, 92 below. A flow of the `CPI /
  inflation surprise` type, country Switzerland.
- **Lesser, both,** as Canada's. The SNB's table keeps every decision, as step 25's banks do.
  Inflation's keeps only its days alone: read by hand 2026-11-23, 152 of the 223, the others
  shared with the US jobs report (37), the ISM survey (26), PCE, the euro area's flash inflation
  (5 each), the ECB (4), US CPI (2) and GDP (1).
- **The markets.** Yahoo's `CHF=X` (dollars in francs: *up* is the franc weaker), 6,027 closes
  from 2003-09-17, closed at 00:00 London as the other currencies; `^SSMI`, 9,049 closes from
  1990-11-09, closed at 17:30 Zurich. Each checked as Canada's: the daily closes of the two weeks
  before step 1 within 0.05% of Yahoo's 5-minute bars, the franc's 00:00 London bar's open and the
  SMI's last bar's close, or the exchange's published close if the bars miss the closing
  auction; a miss is written here with its cause, and a close time it shows wrong is fixed before
  step 2. **Unsigned**, so no live link is added.
- **Step 17's method, unchanged:** the spans, the base, the answers, the placebo, walk-forward and
  its bars, the chance line, both runs (from the close before, and `--after-the-day`).

## The rule, fixed before anything is shown

- The sources, the kinds, the hours and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - The headers: `follows: 80 SNB decisions 2008-06-19 … 2026-09-24: 14 cuts, 61 holds, 5
    hikes` (any later decision `load-releases` reads added), and `follows: 152 Swiss CPI releases
    …: 47 above, 45 as expected, 60 below`; a difference is amended with its date before the
    table is read.
  - Arithmetic, not a finding: an answer needs 10 events of a kind, and a cell holds only with 30
    graded walk-forward, each after ten earlier ones. So the SNB's hikes (5) are *too few* even on
    all history, its cuts (14) are *too few* walk-forward, and only holds and inflation's three
    kinds can hold.
  - Walk-forward: nothing holds, for either flow.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each flow and
    each run (four checks).
  - The franc after an SNB cut, on the day: *can't say*, in both runs.
  - The franc after inflation above or below, on the day: *can't say*, in both runs.
  - The SMI after each kind of each flow, on the day: *can't say*, in both runs.
  - The two new markets give each existing flow new cells and each chance line more; every
    existing row of every output unchanged byte for byte on a copy of the store. The new markets'
    rows are recorded, not judged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two markets and the SNB's history: seed rows, series, `load-prices`, `snb-changes.csv` | `load-prices` stores both; tests: a 09:30 Zurich decision falls on the same day's SMI close and the next day's franc close; the closes within 0.05%, written here; each change's day and hour from the SNB's press release, checked against the monthly series; on a copy of the store every existing `raw-move`, `follows` and scoreboard row identical, each chance line before and after written here |
| 2 | The SNB: flow `snb`, `follows --event snb`, on *Ask*, a trigger kind (*cut*, *hold*, *hike*) | Tests: a quarter stores its decisions at their UTC time; an unscheduled change is added; 2015-01-15 a cut and 2015-03-19 a hold; an `snb` trigger is answered; *Ask*'s cells equal `follows`'. The header as expected, or amended; every other flow's rows unchanged |
| 3 | Inflation: flow `chcpi`, `follows --event chcpi`, on *Ask*, a trigger kind (*above*, *as expected*, *below*) | Tests: the surprise is the actual less the forecast, *above* from 0.1; a day shared with a US release left out of its table; a `chcpi` trigger is answered; *Ask*'s cells equal `follows`'. The header as expected, or amended; every other flow's rows unchanged |
| 4 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet marked right or wrong with its numbers |

## How you know it is right

- **Nothing measured before changes:** the byte-for-byte check of step 1, run again after steps 2
  and 3.
- **The kind is the SNB's:** a test reads the calendar's 2015-03-19 (−0.75% from 0.125%) as a hold
  and 2015-01-15, which the calendar lacks, as a cut.
- **The headers:** each against the hand count above; a gap is a bug in the code or in the hand
  count, found and written here before the table is read.

## What this step does not do

The SNB's currency interventions and the minimum exchange rate against the euro (2011 to 2015):
they are not rate decisions. Swiss GDP, the procure.ch PMI, the KOF indicator and unemployment.
The euro against the franc: the franc is read against the dollar, as every currency here. No sign
for the two markets, no live call on Switzerland.

## Technical details

- **Code:** a decision flow for the SNB beside `BOC_FLOW` in `flows.py`, zone Zurich, reading
  `snb-changes.csv` as the BoC's reads its file; `CH_CPI_FLOW` beside `CA_CPI_FLOW`; the two series
  in `study.py`'s price table.
- **Data:** `data/seed/instruments.csv` (`USDCHF`, `SMI`), `data/seed/countries.csv`
  (`Switzerland`), `data/seed/snb-changes.csv`.
- **Docs:** this spec, step 50's list of markets, the glossary, `docs/schema.md` (the codes, the
  country, the markets), status, the changelog, roadmap row 54.

## Results

Not yet measured.
