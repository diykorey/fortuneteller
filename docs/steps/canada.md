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
  (`day,time,rate`). A decision on a change's day is a *cut* or a *hike* by it; any other decision
  after the first is a *hold*; a change the calendar lacks is added as a decision at the file's
  time. From the calendar alone, read 2026-11-22: 21 cuts, 97 holds, 18 hikes. The two are expected
  to disagree on exactly the unscheduled cuts, 2008-10-08, 2020-03-13 and 2020-03-27; step 1 lists
  every day they disagree, and any other is written here with a dated amendment before step 2.
- **Canadian inflation: `Inflation Rate YoY`,** country `CA`, with TradingView's forecast: 225
  releases from 2008-01 to 2026-09, at 08:30 Toronto (07:00 in its early years). The surprise is the
  actual minus the forecast, noticeable from 0.1 percentage point, the print's own step (its median
  miss): 77 above, 51 as expected, 95 below. No 12-month trend. A flow of the `CPI / inflation
  surprise` type, country Canada.
- **Lesser, both,** as OPEC's and the BoJ's: each day stays an ordinary day for every other flow,
  so no other flow's base or row changes. Canada's inflation shares its 08:30 with US releases on
  some days; step 3 counts them, and its table keeps them, naming the other flow, as OPEC's does.
- **The markets.** Yahoo's `CAD=X` (dollars in Canadian dollars: *up* is the Canadian dollar
  weaker), closed as the other currencies, at 00:00 London of its own day; `^GSPTSE`, closed at
  16:00 Toronto. Each checked against intraday bars, as step 25 did: the daily closes of one recent
  week within 0.05% of the bar at the close time. **Unsigned,** as step 25's three are, so no live
  link is added.
- **Step 17's method, unchanged:** the spans, the base, the answers, the placebo, walk-forward and
  its bars, the chance line, both runs (from the close before, and `--after-the-day`).
- **Canada's jobs report is left out:** it is published at 08:30 on the same Friday as the US
  jobs report on most months, so its own days would be too few to tell apart.

## The rule, fixed before anything is shown

- The sources, the kinds, the hours and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: an answer needs 10 events of a kind, and a cell holds only with 30
    graded walk-forward, each after ten earlier ones. So the Bank's cuts (about 21) and hikes
    (about 18) may answer on all history but are *too few* walk-forward; only holds (about 97) and
    inflation's three kinds can hold.
  - Walk-forward: nothing holds, for either flow.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each flow and
    each run.
  - The Canadian dollar after a Bank of Canada cut or hike, on the day: *can't say*, as the euro,
    the pound and the yen after their own banks' moves.
  - The two new markets give each existing flow new cells and each chance line and grid more; every
    existing row of every output unchanged byte for byte on a copy of the store. The new markets'
    rows are recorded, not judged. Toronto's long run may hold as the S&P 500's does; the front page
    still shows one card on stocks.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two markets and the Bank's history: seed rows, series, `load-prices`, `boc-changes.csv` | `load-prices` stores both; tests: a 10:00 Toronto decision falls on the same day's TSX close and the next day's Canadian dollar close; the closes within 0.05% of the bars, written here; the disagreeing days listed here; on a copy of the store every existing `raw-move`, `follows` and scoreboard row identical, and each chance line before and after written here |
| 2 | The Bank: flow `boc`, `follows --event boc`, on *Ask*, `boc` a trigger kind | Tests: a quarter stores its decisions at their UTC time; a change day the calendar lacks is added; a decision's kind is the Bank's change. The header and its counts written here |
| 3 | Inflation: flow `cacpi`, `follows --event cacpi`, on *Ask*, a trigger kind | Tests: a release's surprise is its actual minus its forecast, and its kind *above* from 0.1. The header, the counts and the days shared with US releases written here |
| 4 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet marked right or wrong with its numbers |

## How you know it is right

- **Nothing measured before changes:** the byte-for-byte check of step 1, run again after steps 2
  and 3.
- **The hours:** a test for each flow places a real release on its reaction day.
- **The Bank's emergency cuts are kinds:** the test of step 2 finds 2020-03-13 a cut.

## What this step does not do

No Canadian jobs report, no Canadian bond (no free daily yield), no sign for the two markets, no
live call on Canada.

## Technical details

- **Docs:** this spec, [step 50](guess-ledger.md)'s list of markets amended, the glossary (*BoC*,
  *TSX*), `docs/schema.md` (the event type's country, the markets), a decisions entry (the three
  countries, their order), status, the changelog, roadmap row 52.
