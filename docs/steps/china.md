# China: inflation, the factory survey, output and trade

> Step 53 of the [Roadmap](../roadmap.md), the second of three countries the owner asked for on
> 2026-11-22 ("lets cover canada china and Switzerland"), after [Canada](canada.md) (step 52) and
> before Switzerland (step 54). Built as Canada's inflation was built. Terms are in the
> [Glossary](../glossary.md): *kind*, *span*, *lesser release*, *release moment*, *holds*, the four
> answers, *area*, *NBS*, *PPI*, *USDCNY*, *SHCOMP*.

## The goal

**In plain words:** when China's inflation, its factory survey, its factory output or its exports
come in above or below forecasts, what did each market do over the next day, week and month, the
yuan and Shanghai's stocks among them?

At the end: two markets more, the yuan (`USDCNY`) and the Shanghai Composite (`SHCOMP`); four
flows, `cncpi`, `cnpmi`, `cnip` and `cntrade`, each with `fortuneteller follows --event <flow>`, a
trigger kind (*above*, *as expected*, *below*) and a place on the page's *Ask the fortune teller*,
as Canada's inflation has; the two markets in the guesser's list of markets ([step
50](guess-ledger.md)) and in their [areas](predicts.md) (currencies, stocks).

## The way to reach it

- **One flow per release moment.** China publishes several reports at the same minute; a table
  cannot tell them apart, so each moment is one flow, its kind read from one report named here.
  All from TradingView's calendar, country `CN`, a quarter at a time, with its forecast. Read
  2026-11-23, releases with an actual and a forecast:

  | Flow | Event type (country China) | The kind's report | Released with it | Releases, first forecast | Median miss | Noticeable from | Kinds (above / as expected / below) |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | `cncpi` | `CPI / inflation surprise` | `Inflation Rate YoY` | PPI, on 218 of 226 | 192, 2010-12 | 0.1 pp | 0.1 pp | 64 / 38 / 90 |
  | `cnpmi` | `Manufacturing survey` | `NBS Manufacturing PMI` | the services PMI, on 143 of 227 | 193, 2009-05 | 0.3 points | 0.2 points | 63 / 57 / 73 |
  | `cnip` | `Other macro data (GDP/PMI/PCE/retail/claims)` | `Industrial Production YoY` | retail sales on 199 and fixed investment on 195 of 207; GDP in each quarter's first month | 174, 2010-12 | 0.4 pp | 0.3 pp | 60 / 62 / 52 |
  | `cntrade` | `Trade data` (a new seed row) | `Exports YoY` | imports and the balance, on all | 185, 2010-12 | 3.5 pp | 2.3 pp | 67 / 64 / 54 |

  *Noticeable from* is two thirds of the median miss against TradingView's forecast, rounded to
  the report's 0.1 step, as for claims and [the German surveys](germany-calendar.md); for
  inflation that is the print's own step, as for Canada's. The actual is rounded to 0.1 before its
  kind is read. Industrial production stands for its moment as the first line of the NBS's
  release; retail sales has as many forecasts (174), and GDP, quarterly, has 64.
- **The hours.** Inflation at 09:30 Beijing (01:30 UTC); the survey at 09:00, and at 09:30 on 58
  releases since 2015; output at 10:00, and 13:30 on 31 releases of 2011 to 2013; trade from 09:00
  to 11:00. Each is before the close of Shanghai (15:00), Tokyo, Europe and New York on its day,
  so those react that day; the currencies, closed at 00:00 London, the next day, as for every
  event (*amended 2026-11-23, step 1:* the yuan, read at noon New York, the same day; see the
  markets below). Ten releases fall at or after 15:00 Beijing (inflation 1, the survey 1, output 5, trade
  3); the code places each by its hour, so Shanghai's reaction is the next day's close. Trade's
  four releases at 00:00 UTC (2011-06-10, 2012-04-10, 2013-01-10, 2013-07-10) carry a date only
  and are placed at 08:00 Beijing: if they came out after 15:00, Shanghai's reaction day is one
  early, a known miss on 4 of 185.
- **Weekends.** China publishes on Saturdays and Sundays: inflation 33 of 192, the survey 57 of
  193, output 12 of 174, trade 32 of 185. Every market reacts at its next close, as the code
  already places an event by its hour. *Alone* is read on the first weekday on or after the
  Beijing date, not the date itself: the survey comes out on the month's last day and, on a
  weekend, reacts on a Monday that is often the first of the month, the US survey's day (40 of
  the survey's releases).
- **Lesser, all four,** as Canada's inflation: each day stays an ordinary day for every other
  flow, so no other flow's base or row changes. Each table keeps only its days alone: no day of a
  flow that is not lesser, and no day of another of the four (inflation shares 21 days with
  output, 5 with trade). Read by hand 2026-11-23 against the US flows and the ECB, the expected
  headers are:
  - `follows: 116 Chinese CPI releases …: 39 above, 22 as expected, 55 below`
  - `follows: 82 Chinese PMI releases …: 27 above, 23 as expected, 32 below`
  - `follows: 110 Chinese output releases …: 44 above, 33 as expected, 33 below`
  - `follows: 127 Chinese trade releases …: 41 above, 44 as expected, 42 below`

  The code's own count may differ by the flows the hand count left out (the BoE, the BoJ, OPEC);
  any difference is written here with a dated amendment before that flow's table is read.
  (*Amended 2026-11-23, in step 2, before its table was read:* until `cnip` and `cntrade` exist,
  inflation's days shared with them stay in, so step 2's header is `follows: 148 Chinese CPI
  releases …: 53 above, 29 as expected, 66 below`; with their days taken out by hand, the 148 are
  the 116 above, 39, 22 and 55, exactly. Each header is checked again after step 4.)
  (*Amended 2026-11-23, in step 3, before either table was read:* the survey's hand count of 82
  left out the euro area's flash inflation, a flow that is not lesser and comes out on the month's
  last or first day, as the survey does; it shares 23 of the survey's days, and with them taken
  out the header is `follows: 59 Chinese PMI releases …: 18 above, 19 as expected, 22 below`.
  Without it the same count gives the 82, 27, 23 and 32 above, exactly. Output's 110 stands. Until
  `cntrade` exists, inflation's header is `follows: 132 Chinese CPI releases …: 47 above, 26 as
  expected, 59 below`. Taking out trade's days changes neither the survey's count nor output's.)
- **The markets.** Yahoo's `CNY=X` (dollars in yuan: *up* is the yuan weaker), 6,364 closes from
  2001, closed as the other currencies at 00:00 London; `000001.SS`, 7,120 closes from 1997,
  closed at 15:00 Shanghai. Each checked as Canada's: the daily closes of the two weeks before step
  1 against Yahoo's 5-minute bars, the yuan's against the 00:00 London bar's open, Shanghai's
  against its last bar's close; each within 0.05%, or the close time fixed before step 2. The yuan
  was held to the dollar from 2008-07 to 2010-06 (one survey forecast falls in it) and moves
  within a daily band since, so its moves are small. **Unsigned**, so no live link is added.
  (*Amended 2026-11-23, in step 1, before any China flow existed:* the yuan is FRED's `DEXCHUS`,
  the Federal Reserve's noon buying rate in New York, read at 12:00 New York, and kept from
  2010-06-21, the end of the second peg. Yahoo's `CNY=X` has no 00:00 London bar on 9 of the ten
  days and stamps each day with `DEXCHUS` of the business day before, so at 00:00 London it would
  date an event between noon New York and midnight London a day early. Held, the yuan does not
  move: from 1994 to 2005 and 2008 to 2010 its median move is zero, which broke `raw-move`. So a
  China release at 09:30 Beijing reacts in the yuan the same day, not the next; and Shanghai's
  closes are checked against the exchange's published close, since the 5-minute bars end at 14:57,
  before the closing auction.)
- **Step 17's method, unchanged:** the spans, the base, the answers, the placebo, walk-forward and
  its bars, the chance line, both runs (from the close before, and from the reaction close,
  `--after-the-day`).

## The rule, fixed before anything is shown

- The sources, the reports, the thresholds, the hours and step 17's bars, unchanged by what the
  run shows.
- **Expected outcome, written first:**
  - The four headers above, or the difference amended with its date before the table is read.
  - Arithmetic, not a finding: an answer needs 10 events of a kind, and a cell holds only with 30
    graded walk-forward, each after ten earlier ones.
  - Walk-forward: nothing holds, for any of the four flows.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each flow
    and each run (eight checks).
  - Shanghai's stocks after each kind of each flow, on the day: *can't say*, in both runs.
  - The yuan after each kind of each flow, on the day: *can't say*, in both runs.
  - Brent after `cnip` and `cnpmi` above or below, on the day: *can't say*, in both runs.
  - The two new markets give each existing flow new cells and each chance line more; every
    existing row of every output unchanged byte for byte on a copy of the store. The new markets'
    rows are recorded, not judged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The two markets~~ **done** 2026-11-23. The two markets: seed rows, series, `load-prices`, the guesser's list and the areas | `load-prices` stores both; tests: a 09:30 Beijing release falls on the same day's Shanghai and Tokyo close and the next day's yuan close (*amended 2026-11-23:* the same day's, the yuan at noon New York), a Saturday's on Monday's Shanghai close; `USDCNY` is in the currencies area and `SHCOMP` in stocks; the closes' largest difference from the bars written here, each within 0.05%; on a copy of the store every existing `raw-move`, `follows` and scoreboard row identical, each chance line before and after written here |
| 2 | ~~Inflation~~ **done** 2026-11-23. Inflation: `cncpi` | Tests: the surprise is the actual less the forecast, *above* from 0.1; a day shared with a US release, and a day shared with `cnip`, left out of its table; a Saturday release dated, for *alone*, on its Monday; a `cncpi` trigger is answered; *Ask*'s cells equal `follows`'. The header equal to the one above, or amended; every other flow's rows unchanged |
| 3 | The survey and output: `cnpmi`, `cnip` | As step 2, each with its threshold; a survey on a Sunday before a US survey's Monday left out; an output release at 15:30 Beijing reacts at Shanghai's next close |
| 4 | Trade: `cntrade`, and `Trade data` in `event_types.csv` (tier 3, *both*) and `docs/schema.md` | As step 2; the seed row loads and the flow's events carry it |
| 5 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet marked right or wrong with its numbers |

*Step 1, 2026-11-23:* every number is in [the evidence](china-steps.txt).

- **The yuan, from FRED** (amended above): `DEXCHUS`, 4,102 closes from 2010-06-21 to
  2026-11-13, read at 12:00 New York. Yahoo's `CNY=X` stamps each day with `DEXCHUS` of the
  business day before, equal on all four days FRED has published of the two weeks; its 5-minute
  bars have a 00:00 London bar on one day of ten, 0.150% from the daily value. FRED publishes
  `DEXCHUS` a week at a time, so the yuan's latest closes lag by up to a week; with no sign, no
  live call waits on them.
- **Shanghai:** `000001.SS`, 7,118 closes from 1997-07-02. Its daily close equals the exchange's
  published close (Eastmoney) to the cent on all ten days of 2026-11-09 to 2026-11-20; against
  the last 5-minute bar, 14:55, it differs by 0.004% to 0.125%, the closing auction from 14:57 to
  15:00 being in no bar.
- **Tests:** a 09:30 Beijing release reacts in Shanghai, Tokyo, New York and the yuan the same
  day, a Fed decision at 14:00 New York in the yuan the next; a Saturday's release is paired
  with Friday's and Monday's Shanghai closes; `USDCNY` is a currency and `SHCOMP` a stock market;
  a close from the peg is not stored.
- **On a copy of the store** (of 2026-11-21, closes to 2026-11-19, the Canadian dollar and
  Toronto loaded first with main's code), with the two markets' closes loaded alone: every
  existing row of every flow's `raw-move` (39 events) and `follows` (20 flows, both runs, and the
  Fed's `--long`), 80 outputs, and every scoreboard entry, is byte for byte the one before; each
  output gains the two markets' rows. The copy holds no BoC or Canadian CPI events, so their
  `follows` print nothing on either side. Only the chance lines change: the scoreboard's raw-move
  chance 1,078 → 1,142 cells (10.78 → 11.42), its surprise chance 396 → 420 (3.96 → 4.20),
  walk-forward unchanged at 82; `follows`' answers by chance on all history, before → after:

  | Flow | From the close before | From the reaction close |
  | --- | --- | --- |
  | Fed | 8.8 → 9.4 (`--long` 2.6 → 2.7) | 8.8 → 9.4 |
  | jobs report, retail sales, CPI, claims | 8.9 → 9.5 | 8.9 → 9.5 |
  | ECB | 8.6 → 9.0 | 8.6 → 9.1 |
  | BoE | 8.4 → 8.8 | 8.4 → 8.8 |
  | OPEC | 5.9 → 6.2 | 5.9 → 6.3 |
  | BoJ, crypto | 3.0 → 3.1 | 3.0 → 3.1 |
  | weather, war, floods | 2.9 → 3.1 | 2.9 → 3.1 |
  | CEO scandals, additions, splits, earnings (Dow and S&P 500) | unchanged, 0.1 to 0.3 | unchanged |

*Step 2, 2026-11-23:* on a copy of step 1's store, with China's CPI alone loaded (`loaded 226
Chinese CPI releases, 2008-01-24 … 2026-11-09`, 192 with TradingView's forecast, the first
2010-12-11), `follows --event cncpi` prints the header amended above, `follows: 148 Chinese CPI
releases 2010-12-11 … 2026-11-09: 53 above, 29 as expected, 66 below`: 44 releases with a kind
share a weekday with a flow that is not lesser, read on the Beijing date or, at a weekend, the
Monday after. Every other flow's `follows` (both runs, and the Fed's `--long`) and `raw-move`
output, 80 in all, is byte for byte the one before, chance lines too. The scoreboard gains
inflation's entry (38 events): its raw-move chance 1,142 → 1,177 cells and its surprise chance
420 → 455; walk-forward stays at 82 cells. Every other entry, and every other flow's *Ask* entry,
is the same. On *Ask*, inflation's 315 cells equal `follows --event cncpi`'s 315 lines.

| Run | Answers | Chance line | Walk-forward |
| --- | --- | --- | --- |
| From the close before | 2: *above*, day, the Canadian dollar about the same; *as expected*, day, wheat down | about 9.4 answers, 0.0 holds | 315 of 315 *too few* (at most 17 graded) |
| `--after-the-day` | 6: *above*, week, Brent about the same; *as expected*, day, the 10-year and 5-year yields up, the yuan up (13 / 14 / 2 of 29), and week, the pound down; *below*, week, the Euro Stoxx 50 about the same | about 9.4 answers, 0.0 holds | 315 of 315 *too few* (at most 15 graded) |

The yuan and Shanghai's stocks on the day, up / same / down of n:

| Kind | Run | USDCNY | SHCOMP |
| --- | --- | --- | --- |
| above | close before | 23 / 10 / 20 of 53, *can't say* | 22 / 12 / 19 of 53, *can't say* |
| as expected | close before | *can't say* | *can't say* |
| below | close before | 22 / 23 / 21 of 66, *can't say* | 22 / 26 / 16 of 64, *can't say* |
| above | after the day | 24 / 15 / 14 of 53, *can't say* | 17 / 22 / 14 of 53, *can't say* |
| as expected | after the day | 13 / 14 / 2 of 29, *up* | *can't say* |
| below | after the day | 20 / 18 / 28 of 66, *can't say* | 23 / 23 / 19 of 65, *can't say* |

`raw-move --event cncpi` reads 177 days: the yuan's ratio 1.14 (p 0.18, *unclear*, 153 days),
Shanghai's 1.00. Both runs' tables are in [the evidence](china-steps.txt), for step 5 to judge.

## How you know it is right

- **Nothing measured before changes:** the byte-for-byte check of step 1, run again after steps 2
  to 4.
- **The kind is the named report's:** a test per flow reads a real release where the named
  report and its companion disagree (CPI above, PPI below) and finds the named report's kind.
- **The day is Beijing's, then the weekday:** a test places a 09:30 Beijing release, which is the
  evening before in New York, on New York's next close, and a Sunday survey on Monday.
- **The headers:** each flow's count of lone releases against the hand count above; a gap larger
  than the BoE's, the BoJ's and OPEC's days on those dates is a bug, not an amendment.

## What this step does not do

Money and credit (M2, new loans, total financing): irregular hours, often after Shanghai's close.
Foreign-exchange reserves: forecasts only from 2016, mostly on weekends. The loan prime rate: no
forecast, few changes. The private (Caixin, now RatingDog) surveys: no actuals on the calendar.
Unemployment, house prices and industrial profits: no forecast. China's holidays beyond weekends
(the Spring Festival, the October week) are not handled: a release before one is placed at the
next close whatever the gap. No sign for the two markets, no live call on China.

## Technical details

- **Code:** four `TradingViewFlow`s beside `CA_CPI_FLOW` in `flows.py`, zone Shanghai; their
  titles in `sources.py`; `shared_days` in `study.py` reads the four China flows as sharing each
  other's days, and a lesser flow's weekend date as its next weekday; the two series in
  `study.py`'s price table.
- **Data:** `data/seed/instruments.csv` (`USDCNY`, `SHCOMP`), `data/seed/event_types.csv`
  (`Trade data`).
- **Docs:** this spec, step 50's list of markets, the glossary (done with this spec),
  `docs/schema.md` (the event type, the country, the markets), status, the changelog, roadmap row
  53.

## Results

Not yet measured.
