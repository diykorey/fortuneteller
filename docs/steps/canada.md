# Canada: the Bank of Canada and Canadian inflation

> Step 52 of the [Roadmap](../roadmap.md), the first of three countries the owner asked for on
> 2026-11-22 ("lets cover canada china and Switzerland"); China and Switzerland follow as steps 53
> and 54. Built as [step 25](other-central-banks.md) built the Bank of England and the Bank of
> Japan, and [Germany's calendar](germany-calendar.md) its flash inflation. Terms are in the
> [Glossary](../glossary.md): *kind*, *span*, *lesser release*, *holds*, the four answers, *area*.

## The goal

**In plain words:** when the Bank of Canada cuts, holds or raises its rate, or Canada's inflation
comes in above or below forecasts, what did each market do over the next day, week and month,
the Canadian dollar and Toronto's stocks among them?

At the end: two markets more, the Canadian dollar (USD/CAD) and Toronto's S&P/TSX Composite;
`fortuneteller follows --event boc` and `--event cacpi` print [step 17's](what-follows.md) table;
both are on the page's *Ask the fortune teller*, as [step 29](ask-phase-5.md) put the other banks;
and the two markets are in the guesser's list and in their [areas](predicts.md) (currencies,
stocks).

## The way to reach it

- **The Bank of Canada's days and hour: TradingView's calendar,** country `CA`, title `Interest
  Rate`, a quarter at a time, as the BoJ's. Read 2026-11-22: 152 decisions from 2008-01-22 to
  2026-09-02, announced at 10:00 Toronto (09:45 from 2023), before New York's and Toronto's close:
  every New York market and Toronto react the same day; the currencies, whose close is 00:00
  London, the next day, as for every event.
- **The kind, from the Bank's own history,** as the BoE's: the Bank of Canada's published target
  for the overnight rate, every change from 2008-01-01, copied into `data/seed/boc-changes.csv`
  (`day,time,rate`, `time` the Toronto hour of the Bank's announcement; its daily series, Valet
  `V39079`, from 2009-04-21, checks the file). A decision on a change's day is a *cut* or a *hike*
  by it; any other decision after the first is a *hold*; the first, 2008-01-22, has no kind; a
  change the calendar lacks is added as a decision at the file's time. The event type is
  `Central-bank decision`, country `Canada` (in the seed).
  - From the calendar alone, read 2026-11-22: 21 cuts, 97 holds, 18 hikes, and 15 decisions from
    2012-01-17 to 2013-10-23 with no rate (the rate stood at 1% through them), so 136 of 151 with
    a kind. The calendar lists both emergency cuts of March 2020 (13th and 27th) but not the
    unscheduled cut of 2008-10-08.
  - The two *disagree* on a day the calendar lacks, or where the calendar's kind (its rate against
    the previous) is missing or differs from the Bank's. The expected list is exactly 2008-10-08
    (added, a cut) and the 15 days with no rate (holds); any other day is written here with a dated
    amendment before step 2.
  - With the Bank's history: 153 decisions, 152 with a kind: 22 cuts, 112 holds, 18 hikes to
    2026-09-02; a later decision is counted as `load-releases` reads it.
- **Canadian inflation: `Inflation Rate YoY`,** country `CA`, with TradingView's forecast: 225
  releases from 2008-01 to 2026-09, at 08:30 Toronto (07:00 from 2008 to 2012); either hour is
  before every close of its day but Tokyo's, so the reaction days are the same. The surprise is the
  actual minus the forecast, noticeable from 0.1 percentage point, the print's own step and its
  median absolute miss (read 2026-11-22): 77 above, 51 as expected, 95 below; 2009-11-18 and
  2012-12-21 have no forecast and no kind. No 12-month trend. A flow of the `CPI / inflation
  surprise` type, country Canada.
- **Lesser, both,** as OPEC's and the BoJ's: each day stays an ordinary day for every other flow,
  so no other flow's base or row changes. The Bank's table keeps every decision, a day shared with
  another flow included, as step 25's banks do. Inflation's keeps only its days alone, as
  [Germany's flash CPI](germany-calendar.md) does, so a US release on the same day cannot answer
  for it: read 2026-11-22, 187 of the 223 with a kind, the other 36 shared with US retail sales
  (17), the Fed (13), US CPI (8), PCE and GDP (1 each).
- **The markets.** Yahoo's `CAD=X` (dollars in Canadian dollars: *up* is the Canadian dollar
  weaker), closed as the other currencies, at 00:00 London of its own day; `^GSPTSE`, closed at
  16:00 Toronto. Each checked against intraday bars, as step 25 did: the daily closes of one recent
  week within 0.05% of the bar at the close time; a miss is written here with its cause, and a
  close time it shows wrong is fixed before step 2. Both are in the guesser's list and their
  areas, `USDCAD` currencies and `TSX` stocks. **Unsigned,** as step 25's three are, so no live
  link is added. Europe's and Tokyo's markets react as to any event at that hour: the Bank's 10:00
  and inflation's 08:30 Toronto are after Europe's close and Tokyo's, so they react the next day.
- **Step 17's method, unchanged:** the spans, the base, the answers, the placebo, walk-forward and
  its bars, the chance line, both runs (from the close before, and `--after-the-day`).
- **Canada's jobs report is left out:** it is published at 08:30 on the same Friday as the US
  jobs report on most months, so its own days would be too few to tell apart.

## The rule, fixed before anything is shown

- The sources, the kinds, the hours and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - The headers: `follows: 152 BoC decisions 2008-03-04 … 2026-09-02: 22 cuts, 112 holds, 18
    hikes` (with any later decision `load-releases` reads added), and for inflation its counts on
    its 187 days alone, written in step 3 before its table is read.
  - Arithmetic, not a finding: an answer needs 10 events of a kind, and a cell holds only with 30
    graded walk-forward, each after ten earlier ones. So the Bank's cuts (22) and hikes (18) may
    answer on all history but are *too few* walk-forward; only holds (112) and inflation's three
    kinds can hold.
  - Walk-forward: nothing holds, for either flow.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each flow and
    each run.
  - The Canadian dollar after a Bank of Canada cut or hike, on the day: *can't say*, in both runs,
    as the euro, the pound and the yen after their own banks' moves.
  - The Canadian dollar after inflation above or below, on the day: *can't say*, in both runs; the
    ECB's and Germany's prints did not move the euro beyond chance.
  - The two new markets give each existing flow new cells and each chance line and grid more; every
    existing row of every output unchanged byte for byte on a copy of the store. The new markets'
    rows are recorded, not judged, Toronto's long run among them; the front page shows one card on
    stocks whatever it gives.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two markets and the Bank's history: seed rows, series, `load-prices`, `boc-changes.csv` | `load-prices` stores both; tests: a 10:00 Toronto decision falls on the same day's TSX close and the next day's Canadian dollar close; the closes within 0.05% of the bars, written here; the disagreeing days listed here; on a copy of the store every existing `raw-move`, `follows` and scoreboard row identical, and each chance line before and after written here |
| 2 | The Bank: flow `boc`, `follows --event boc`, on *Ask*, `boc` a trigger kind (*cut*, *hold*, *hike*) | Tests: a quarter stores its decisions at their UTC time; a change day the calendar lacks is added; a decision's kind is the Bank's change, 2020-03-13 a cut and 2012-01-17 a hold; a `boc` trigger is answered; *Ask*'s `boc` cells equal `follows`', as step 29 checks. On a copy of the store the header as expected, or the difference amended with its date; every other flow's rows unchanged |
| 3 | Inflation: flow `cacpi`, `follows --event cacpi`, on *Ask*, a trigger kind (*above*, *as expected*, *below*) | Tests: a release's surprise is its actual minus its forecast, its kind *above* from 0.1, a day shared with a US release left out of its table; a `cacpi` trigger is answered; *Ask*'s cells equal `follows`'. The header and its counts written here; every other flow's rows unchanged |
| 4 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet marked right or wrong with its numbers |

## How you know it is right

- **Nothing measured before changes:** the byte-for-byte check of step 1, run again after steps 2
  and 3.
- **The hours:** a test for each flow places a real release on its reaction day.
- **The Bank's emergency cuts are kinds:** the test of step 2 finds 2020-03-13 a cut.
- **A US release cannot answer for Canada's inflation:** its table holds no day shared with one.

## What this step does not do

No Canadian jobs report, no Canadian bond (no free daily yield), no sign for the two markets, no
live call on Canada.

## Technical details

- **Docs:** this spec, [step 50](guess-ledger.md)'s list of markets amended, the glossary (*BoC*,
  *TSX*), `docs/schema.md` (the event type's country, the markets), a decisions entry (the three
  countries, their order), status, the changelog, roadmap row 52.
