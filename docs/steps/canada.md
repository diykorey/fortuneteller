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
  London, the next day, as for every event. (*Amended 2026-11-22, after step 1 read the calendar's
  hours:* 09:00 Toronto to 2012, 10:00 from 2013, 09:45 from 2024; every one before New York's
  and Toronto's close, so no reaction day changes. 2020-03-13's cut carries the calendar's 11:00;
  the Bank's pages give no hour and its notes point to the afternoon, so Europe's reaction to that
  one cut may be read a day early: a known miss.)
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
  link is added. Europe's and Tokyo's markets react as to any event at that hour: the Bank's hour and
  inflation's 08:30 Toronto are after Tokyo's close, so Tokyo reacts the next day; Europe closes at
  11:30 Toronto, after both, so it reacts the same day (*amended 2026-11-22, after step 1:* this
  read "after Europe's close"; the code places each event by its hour, so only the words were
  wrong).
- **Step 17's method, unchanged:** the spans, the base, the answers, the placebo, walk-forward and
  its bars, the chance line, both runs (from the close before, and `--after-the-day`).
- **Canada's jobs report is left out:** it is published at 08:30 on the same Friday as the US
  jobs report on most months, so its own days would be too few to tell apart.

## The rule, fixed before anything is shown

- The sources, the kinds, the hours and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - The headers: `follows: 152 BoC decisions 2008-03-04 … 2026-09-02: 22 cuts, 112 holds, 18
    hikes` (with any later decision `load-releases` reads added; *amended 2026-11-22, after step
    1, before step 2:* the calendar now lists the hike of 2026-10-28, so `follows: 153 BoC
    decisions 2008-03-04 … 2026-10-28: 22 cuts, 112 holds, 19 hikes`), and for inflation its counts on
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
| 1 | ~~The two markets and the Bank's history~~ **done** 2026-11-22. The two markets and the Bank's history: seed rows, series, `load-prices`, `boc-changes.csv` | `load-prices` stores both; tests: a 10:00 Toronto decision falls on the same day's TSX close and the next day's Canadian dollar close; the closes within 0.05% of the bars, written here; the disagreeing days listed here; on a copy of the store every existing `raw-move`, `follows` and scoreboard row identical, and each chance line before and after written here |
| 2 | The Bank: flow `boc`, `follows --event boc`, on *Ask*, `boc` a trigger kind (*cut*, *hold*, *hike*) | Tests: a quarter stores its decisions at their UTC time; a change day the calendar lacks is added; a decision's kind is the Bank's change, 2020-03-13 a cut and 2012-01-17 a hold; a `boc` trigger is answered; *Ask*'s `boc` cells equal `follows`', as step 29 checks. On a copy of the store the header as expected, or the difference amended with its date; every other flow's rows unchanged |
| 3 | Inflation: flow `cacpi`, `follows --event cacpi`, on *Ask*, a trigger kind (*above*, *as expected*, *below*) | Tests: a release's surprise is its actual minus its forecast, its kind *above* from 0.1, a day shared with a US release left out of its table; a `cacpi` trigger is answered; *Ask*'s cells equal `follows`'. The header and its counts written here; every other flow's rows unchanged |
| 4 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet marked right or wrong with its numbers |

*Step 1, 2026-11-22:* every number is in [the evidence](canada-steps.txt).

- **The Bank's history:** 42 changes of the target for the overnight rate, 2008-01-22 to
  2026-10-28, in `data/seed/boc-changes.csv`: from 2009-04-21 the Bank's daily series (Valet
  `V39079`), each change on the calendar's decision of its day or the business day before (Valet
  gives the effective day from 2022, and 2020-03-16 for the cut announced 2020-03-13); before it
  the calendar's rows, each of the nine rates of 2008 and 2009 as the calendar gives them, and the
  unscheduled cut of 2008-10-08 (to 2.50% from 3.00%, 07:00 Toronto). Every Valet change falls on
  a calendar decision. The calendar now also lists 2026-10-28, a hike to 2.50%, after the spec's
  reading: with the Bank's changes, 22 cuts, 112 holds and 19 hikes to it; to 2026-09-02, 153
  decisions with 22 cuts, 112 holds and 18 hikes, as written above.
- **The disagreeing days:** exactly the 16 expected: 2008-10-08, a cut the calendar lacks, and
  the 15 decisions with no rate from 2012-01-17 to 2013-10-23, holds by the Bank's history.
- **The hours:** `time` is the calendar's Toronto hour: 09:00 to 2012, 10:00 from 2013 to 2023,
  09:45 from 2024, not "10:00 (09:45 from 2023)" as written above; every one is before New York's
  and Toronto's close, so no reaction day of those markets changes. The calendar gives the
  emergency cuts 11:00 (2020-03-13) and 09:00 (2020-03-27); the Bank's pages give no hour. Its
  summary of deliberations has the decision taken after a morning meeting and announced "later
  that same day", and ING's note of that day says "this afternoon": with Europe's close at 12:30
  Toronto that week (America's clocks had changed, Europe's not), an afternoon hour would put
  Europe's reaction on the next day, the calendar's 11:00 on the same day. Left as the calendar
  gives it, a possible known miss for step 2. Also against the text above: the Bank's 09:00 to
  10:00 and inflation's 08:30 Toronto are *before* Europe's close (11:30 Toronto), so Europe's
  markets react the same day, not the next; the code places each by its hour, so only the words
  are wrong.
- **The closes**, against Yahoo's 5-minute bars of 2026-11-09 to 2026-11-20: the Canadian dollar's
  daily close is the 00:00 London bar's open within 0.017% on all ten days; Toronto's is its last
  bar's close, 15:55 to 16:00, within 0.046% (0.000% to 0.046%). Both within 0.05%.
- **On a copy of the store** (closes to 2026-11-19), with the two markets' closes loaded alone
  (`USDCAD` 6,028 from 2003-09-17, `TSX` 11,900 from 1979-06-29): every existing row of every
  flow's `raw-move` (37 events) and `follows` (18 flows, both runs, and the Fed's `--long`), and
  every scoreboard entry, is byte for byte the one before; each output gains the two markets' rows.
  Only the chance lines change, by the added cells: the scoreboard's raw-move chance 1,011 → 1,078
  cells (10.11 → 10.78), its surprise chance 372 → 396 (3.72 → 3.96), walk-forward unchanged at
  82; `follows`' lines, answers by chance on all history, before → after:

  | Flow | From the close before | From the reaction close |
  | --- | --- | --- |
  | Fed | 8.3 → 8.8 (`--long` 2.5 → 2.6) | 8.3 → 8.8 |
  | jobs report, retail sales, CPI, claims | 8.4 → 8.9 | 8.4 → 8.9 |
  | ECB | 8.1 → 8.7 | 8.2 → 8.7 |
  | BoE | 7.8 → 8.4 | 7.8 → 8.4 |
  | OPEC | 5.5 → 5.9 | 5.6 → 5.9 |
  | BoJ, crypto | 2.8 → 3.0 | 2.8 → 3.0 |
  | weather | 2.8 → 2.9 | 2.8 → 2.9 |
  | war, floods | 2.7 → 2.9 | 2.7 → 2.9 |
  | CEO scandals, additions, splits, earnings (Dow and S&P 500) | unchanged, 0.1 to 0.3 | unchanged |

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
