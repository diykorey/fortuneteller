# What follows a Bank of England or a Bank of Japan decision

> Step 25 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the second of phase
> 5's kinds, taken 2026-11-17. Terms are in the [Glossary](../glossary.md): *kind*, *span*, *base
> rate*, the four answers, *lesser release*, *Bank Rate*, *BoJ*.

## The goal

**In plain words:** when the Bank of England or the Bank of Japan cuts, holds or raises its rate,
what did each market do over the next day, week and month, the pound and the yen among them?

At the end: three markets more, the pound (GBP/USD), the yen (USD/JPY) and Tokyo's Nikkei 225;
`fortuneteller follows --event boe` and `--event boj` print [step 17's](what-follows.md) table for
each bank, as [the ECB's](what-follows-ecb.md) does, over the day, the week and the month; and a
trigger file may name `boe` or `boj`.

## The way to reach it

- **The days and the hour: TradingView's calendar**, as for the ECB, title `Interest Rate`, a
  quarter at a time, country `GB` or `JP`, each at the time the calendar gives. Read 2026-11-17
  (every quarter fetched once into a scratch cache; step 2 and step 3 fetch them again through
  `load-releases`): the BoE's from 2008-01-10, 186 decisions to 2026-11-05; the BoJ's from
  2016-04-29, 86 to 2026-10-30. The quarters before list none. The BoE announces at 12:00 London
  (07:00 in 2020's spring and summer); the BoJ when its meeting ends, around midday Tokyo, which
  the calendar gives as 00:00 to 04:30 UTC.
  - A BoJ decision is after every market's close the day before and before every close that day,
    the Nikkei's included, except the euro's, the pound's and the yen's, whose close is 00:00
    London and so the next day's, as for every event.
  - A BoE decision at 12:00 London is after Tokyo's close, so the Nikkei reacts the next day, as
    the three currencies do; every other market the same day. A wrong hour within these windows
    changes no reaction day.
- **The kind, from the rate against the previous decision's**, as the ECB's: *cut*, *hold*,
  *hike*; the first decision has none. The BoJ's rate is the calendar's; its `previous` column
  agrees with the decision before on every one read. Read 2026-11-17: the BoJ's 85 decisions with
  a kind, 79 holds and 6 hikes (2024-03-19 the first), no cut.
- **The BoE's rate is the Bank's own.** The calendar lists no decision on 2020-03-11 or 2020-03-19,
  the two emergency cuts (0.75% to 0.25%, then to 0.1%), and gives 2020-03-26 as a cut from 0.75%
  to 0.1%. So the BoE's kinds come from the Bank of England's published history of Bank Rate
  changes (its *Official Bank Rate history*), copied by hand for every change from 2008-01-01 into
  `data/seed/boe-changes.csv`, columns `day,time,rate`, `time` the London hour of the Bank's
  announcement from its news release.
  - A decision on a change's day is a *cut* or a *hike* by that change; any other decision after
    the first is a *hold*; the first, 2008-01-10, has no kind, as the ECB's first has none.
  - A change whose day the calendar lacks is added as a decision, at the file's time.
  - The two *disagree* on a day when the calendar's kind (its rate against the previous) differs
    from the Bank's, or when one has a decision the other lacks. Step 1 lists each such day. The
    expected list is exactly 2020-03-11 and 2020-03-19 (added, cuts) and 2020-03-26 (a hold, not a
    cut); any other day is written here with a dated amendment before step 2.
  - From the calendar alone, read 2026-11-17: 16 cuts, 152 holds, 17 hikes. With the Bank's
    history: 188 decisions, 187 with a kind, 17 cuts, 153 holds, 17 hikes.
- **The markets.** Yahoo's `GBPUSD=X` (*up* is the pound stronger), `JPY=X` (dollars in yen: *up*
  is the yen weaker) and `^N225`. Their closes: the pound's and the yen's as the euro's, the price
  at 00:00 London of its own day; the Nikkei's at 15:30 Tokyo (15:00 before 2024-11-05, when Tokyo
  lengthened its session). Checked as [more outcomes](more-outcomes.md) did, against intraday
  bars: each daily close of one recent week within 0.05% of the bar at its close time, and the
  Nikkei's of one week of October 2024 against hourly bars at 15:00.
  - **Known misses, written now:** an event from 15:00 to 15:30 Tokyo before 2024-11-05 is read on
    the Nikkei a day early: the two BoE decisions at 07:00 London (06:00 UTC, 15:00 Tokyo),
    2020-05-07 and 2020-08-06, and any other stored event step 1 lists.
  - **Their signs** in every flow's rule, which raw-move's *tracks* test reads: the pound as the
    euro, the opposite of the dollar index; the yen as the dollar index; the Nikkei as the S&P
    500. `called_live` is unchanged, so no new link is called live by this step; one that holds
    walk-forward is reported, and calling it is a decision of its own.
    *Amended 2026-11-17, in step 1:* a market with a sign is a live link: the morning job logs a
    row for it on every release, and calls it once it holds. So the three are **unsigned**, as
    coffee is, and no new link can be called; signing them is a decision of its own. The signs'
    check under How you know is dropped with them.
  - The two banks' bonds are not added: no free source gives a daily gilt or Japanese government
    bond yield (FRED's are monthly).
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES` (the markets
  `follows` reads), and both runs: from the close before and, with `--after-the-day`, from the
  reaction close ([OPEC's spec](opec.md) names the two runs).
- **Lesser, as OPEC's:** each decision day stays an ordinary day for every other flow, so no other
  flow's base or row changes. (The ECB's flow, built before lesser flows, is not lesser; it is
  left so.) A bank's own table keeps every decision, a day shared with another flow included, as
  OPEC's does; the results name the other flow.

## The rule, fixed before anything is shown

- The sources, the kind, the hour and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: an answer needs 10 events of a kind, and a cell holds only with 30
    graded walk-forward, each after ten earlier ones. So the BoJ's hikes (6) are *too few*
    everywhere; the BoE's cuts and hikes (17 each) are *too few* walk-forward, and over the month
    step 17's no-overlap rule may leave fewer than 10, *too few* on all history too; only holds
    (BoE 153, BoJ 79) can hold.
  - The headers: `follows: 187 BoE decisions 2008-02-07 … 2026-11-05: 17 cuts, 153 holds, 17
    hikes` and `follows: 85 BoJ decisions 2016-06-16 … 2026-10-30: 0 cuts, 79 holds, 6 hikes`.
  - Walk-forward: nothing holds, for either bank.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each bank
    and each run. The ECB's run gave none.
  - The pound after a BoE hike and after a cut, on the day: *can't say*, in both runs; the
    decisions are priced in, as the ECB's were for the euro.
  - Every existing row of every output unchanged byte for byte: each other flow's `follows` and
    `raw-move` rows and the scoreboard's existing cells. Only lines that count every cell change,
    by the added cells alone: each chance line and the scoreboard's grids, each written before and
    after. The three markets' new rows are recorded, not judged.

*Written 2026-11-17 before any `follows` or `raw-move` ran on the two banks or the three markets;
the counts above are from the calendar and are arithmetic.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The three markets~~ **done** 2026-11-17. The three markets: seed rows, series, signs, `load-prices`; `boe-changes.csv` from the Bank's history | `load-prices` stores the three; tests: an 08:30 New York release falls on the next day's close for the pound, the yen and the Nikkei, a 02:30 UTC one on the same day's Nikkei close and a 12:00 London one on the next day's; the closes within 0.05% of the bars, written here; the known misses listed; on a copy of the store every existing row of `raw-move`, `follows` and the scoreboard identical, and each chance line and grid before and after written here; the seed test checks `boe-changes.csv`'s header, order and rates; the disagreeing days listed here |
| 2 | ~~The BoE~~ **done** 2026-11-17. The BoE: flow `boe`, `follows --event boe`, `boe` in `TRIGGER_KINDS` | Tests: a calendar quarter stores its decisions at their UTC time; a change day the calendar lacks is added at the file's time; a decision's kind is the Bank's change, and 2020-03-26 a hold; a `boe` trigger is answered. On a copy of the store the header is the expected one, or the difference written with a dated amendment; every other flow's `follows` and `raw-move` rows unchanged |
| 3 | ~~The BoJ~~ **done** 2026-11-18. The BoJ: flow `boj`, `follows --event boj`, `boj` in `TRIGGER_KINDS` | Tests: a quarter stores its decisions at their UTC time; a decision's kind is its rate against the previous; a `boj` trigger is answered. The header as expected, or amended; the others unchanged |
| 4 | ~~Results~~ **done** 2026-11-18. Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every judged bullet of the expected outcome marked right or wrong with its numbers; each bank's walk-forward records; the new markets' rows in the other flows summarised |

*Step 1, 2026-11-17:*

- **The Bank's history** (its *Official Bank Rate history*, read that day): 34 changes from
  2008-02-07 to 2026-11-05, in `data/seed/boe-changes.csv`. Against the calendar's 186 decisions
  the two disagree on exactly the three days expected: 2020-03-11 and 2020-03-19, cuts the
  calendar lacks, and 2020-03-26, a hold the calendar gives as a cut. *Amended 2026-11-17:* the
  Bank's pages give no hour for either emergency cut. 2020-03-11 is written 07:00, as the news of
  that morning reported it; 2020-03-19 is written 12:00 by rule: any hour from 06:30 to 15:30
  London gives every market the same reaction day.
- **The closes**, against Yahoo's 5-minute bars of 2026-11-09 to 2026-11-16: the pound's daily
  close is the 00:00 London bar's open within 0.02% on all six days; the yen's within 0.02% on
  five, and 0.058% on Monday 2026-11-09; the Nikkei's is 0.02% to 0.07% from its last bar, 15:25
  to 15:30, the closing auction after it, as the DAX's is, against 0.1% to 1.6% from the next
  bar. So the 0.05% bar is met by the pound, missed by the yen on one Monday and by the Nikkei on
  three days, each by under 0.02 points; the closes are at the times named. *Amended
  2026-11-17:* the October 2024 hourly check could not run: Yahoo serves hourly bars for the last
  730 days only. The Nikkei's 15:00 close before 2024-11-05 rests on the exchange's change of
  hours, not on bars.
- **The known misses:** one stored event lies from 15:00 to 15:30 Tokyo before 2024-11-05, a
  presidential post at 06:08 UTC on 2019-12-13; with the two BoE decisions to come, three.
- **On a copy of the store**, with the three markets' closes loaded alone (the pound from
  2003-12-01, the yen from 1996-10-30, the Nikkei from 1970-01-05, each to 2026-11-16): every
  existing row of every flow's `raw-move` (25 flows) and `follows` (seven flows, both runs, and the
  Fed's `--long`) and every scoreboard entry is byte for byte the one before; each output gains
  the three markets' rows. Only the chance lines change, by the added cells: the scoreboard's
  raw-move chance 546 → 614 cells, its surprise chance 300 → 336, and each `follows` line, e.g.
  the Fed's from about 6.8 answers to 7.6. OPEC was not stored on that copy and was not compared.

*Step 2, 2026-11-17:* on a copy of the store, with step 1's closes and the BoE's decisions alone
loaded (`load-releases`' report: `loaded 188 BoE decisions, 2008-01-10 … 2026-11-05`, `2 from the
Bank's changes the calendar lacks: 2020-03-11, 2020-03-19`), `follows --event boe` prints the
expected header, `follows: 187 BoE decisions 2008-02-07 … 2026-11-05: 17 cuts, 153 holds, 17
hikes`. Every other flow's `follows` (both runs, and the Fed's `--long`) and `raw-move` output is
byte for byte the one before. `raw-move --event boe` is new: 143 lone BoE days on the S&P 500, the
lesser flow's days shared with no other flow. The scoreboard gains the BoE's raw-move entry (26 →
27 events), and its raw-move chance moves by the added cells alone, 614 → 642; every other entry
is the same. The BoE is in `follows` and triggers, not in the page's *ask*, as OPEC is.

*Step 3, 2026-11-18:* on the same copy of the store, with the BoJ's decisions added
(`loaded 86 BoJ decisions, 2016-04-29 … 2026-10-30`), `follows --event boj` prints the expected
header, `follows: 85 BoJ decisions 2016-06-16 … 2026-10-30: 0 cuts, 79 holds, 6 hikes`. Every
other flow's `follows` and `raw-move` output, the BoE's included, is byte for byte the one before;
`raw-move --event boj` is new (47 lone BoJ days on the S&P 500). The scoreboard gains the BoJ's
raw-move entry (27 → 28 events), its raw-move chance 642 → 670 cells; every other entry is the
same. Like the BoE, the BoJ is in `follows` and triggers, not in the page's *ask*.

## Results

*2026-11-18.* Every line quoted is in [the evidence](other-central-banks-results.txt): a copy of
the store of 2026-11-17, closes to 2026-11-16, with step 1's three markets and the two banks'
decisions loaded, each command's whole output.

**In plain words:** what followed a Bank of England or a Bank of Japan decision cannot be told
from an ordinary day. Out of hundreds of cells, a handful show a lean, fewer than chance alone
would give, and none holds walk-forward. The pound after a BoE cut or hike is *can't say*: the
market had it priced in.

- **The headers, as expected:** `follows: 187 BoE decisions 2008-02-07 … 2026-11-05: 17 cuts,
  153 holds, 17 hikes` and `follows: 85 BoJ decisions 2016-06-16 … 2026-10-30: 0 cuts, 79
  holds, 6 hikes` (`follows --event boe`, `--event boj`).
- **Walk-forward: nothing holds**, for either bank, in either run. As expected.
- **On all history, against the chance line plus 2** (`follows`, each run):

  | Bank | Run | Answers | By chance |
  | --- | --- | --- | --- |
  | BoE | from the close before | 1 | 7.2 |
  | BoE | from the reaction close | 2 | 7.2 |
  | BoJ | from the close before | 0 | 2.5 |
  | BoJ | from the reaction close | 2 | 2.5 |

  Each within its bar, as expected. The answers: after a BoE hike, Europe's shares (SXXP) *down*
  on the day, 11 of 17, chance 0.0093, *too few* walk-forward; from the reaction close, after a
  BoE hold, the VIX *down* on the day (74 of 153, chance 0.0004; walk-forward 47 of 94 right,
  doesn't hold) and the DAX *about the same* over the week (chance 0.0056; 25 of 57, doesn't
  hold); after a BoJ hold, the VIX *up* on the day (30 of 79, chance 0.0049) and homebuilders
  (ITB) *up* over the month (36 of 71, chance 0.0048), both *too few* walk-forward.
- **The pound on the day after a BoE decision: *can't say*** after a cut (17: 6 up, 9 down,
  chance 0.30; from the reaction close 5 up, 8 down, chance 0.28) and after a hike (17: 3 up, 8 down, chance 0.11; from the reaction close
  3 up, 11 down, chance 0.026), in both runs. As expected.
- **The arithmetic held:** the BoJ's 6 hikes are *too few* everywhere; the BoE's cuts and hikes
  answer on all history where 10 or more are graded and are *too few* walk-forward.
- **Every existing row unchanged**, steps 1 to 3 above: only the chance lines and the
  scoreboard's raw-move chance moved, by the added cells (546 → 614 → 642 → 670).
- **Days shared with another flow** (by the bank's day), kept in each bank's own table: the BoE's
  188 with jobless claims on 121, the ECB on 28, the ECB president on 16, the BoJ on 10, CPI on 8
  and 15 other flows on 1 to 6 each; the BoJ's 86 with jobless claims on 24, the euro-area flash
  HICP, the ECB president and the German flash CPI on 11 each, core PCE and the BoE on 10, and 15
  others on 1 to 8.

The expected outcome was **right** on every count.

## How you know it is right

- **The kinds match the news:** seven BoE days checked by hand against the Bank's announcements:
  2009-03-05 cut to 0.5%, 2016-08-04 cut to 0.25%, 2020-03-11 cut to 0.25%, 2020-03-19 cut to
  0.1%, 2020-03-26 hold, 2022-12-15 hike to 3.5%, 2025-12-18 cut to 3.75%; and three BoJ days,
  2016-09-21 hold (the yield-curve policy began, not a rate move), 2024-03-19 hike (the end of
  negative rates), 2024-07-31 hike to 0.25%.
- ~~**The signs:** a test where the dollar index rises and the yen weakens, `JPY=X` up, reads both
  as the same direction, and the pound, `GBPUSD=X` down, as the opposite.~~ *Amended 2026-11-17:*
  the three are unsigned (above); a test finds each sign 0 in every flow's rule.
- **The new markets change nothing else:** every existing row byte for byte, on a copy of the
  store, before and after step 1.
- **The Nikkei's close:** a test with a decision at 02:30 UTC finds the Nikkei's close that day, and
  one at 06:00 UTC on 2020-05-07 the same day, the known miss; one at 06:00 UTC after 2024-11-05
  the same day too, rightly, 15:00 being before 15:30.

## What this step does not do

No surprise against a forecast: the calendar's forecast equals almost every decision. No votes,
minutes, press conferences or the BoJ's bond-buying and yield-curve decisions, only the rate. No
gilt or JGB yields. A BoJ decision before 2016-04-29, such as the cut to −0.1% of 2016-01-29, is not
in the source and not added. No new link called live.

## Technical details

- **Markets:** three `PriceSeries` in `study.MVP_PRICE_SERIES` (`GBPUSD`, `USDJPY`, `NKY`), seed
  rows in `data/seed/instruments.csv`, a `TOKYO` zone in `sources.py`, their signs in `flows.py`.
- **Flows:** two in `flows.py` on the ECB's pattern, `event_id` type codes 28 (`boe`, `United
  Kingdom`) and 29 (`boj`, `Japan`) (`docs/schema.md`), event type `Central-bank decision`,
  `lesser`; country `GB` and `JP` in `fetch_tradingview_quarter`. The kinds: the BoE's from
  `data/seed/boe-changes.csv`, the BoJ's from the calendar as `study.ecb_kinds` reads the ECB's,
  both through `_decision_kinds` in `__main__.py`, which `follows` and `triggers` share.
  `FOLLOWS_NOUNS` gains `BoE decisions` and `BoJ decisions`; `TRIGGER_KINDS` gains both with the
  Fed's `cut`, `hold`, `hike`.
- **Tests** in `tests/test_event_flows.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`
  and `tests/test_seed_data.py`.
- **Docs:** this spec; `docs/schema.md` (codes 28 and 29, the instruments); the glossary (*BoE*,
  *Bank Rate*, *BoJ*; *GBP/USD*, *USD/JPY*, and the Nikkei 225 now in the universe);
  `docs/legacy/data/README.md` (the seed); status, changelog, roadmap row 25.
