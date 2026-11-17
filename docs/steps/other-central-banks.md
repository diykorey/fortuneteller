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
  quarter at a time, country `GB` or `JP`, each at the time the calendar gives. Read 2026-11-17:
  the BoE's from 2008-01-10, 186 decisions to 2026-11-05; the BoJ's from 2016-04-29, 86 to
  2026-10-30. Earlier quarters list none. The BoE announces at 12:00 London (07:00 in 2020's
  spring and summer); the BoJ when its meeting ends, around midday Tokyo, which the calendar gives
  as 00:00 to 04:30 UTC. Either is after every market's close the day before and before every
  close that day, except the euro's and the pound's and the yen's, whose close is 00:00 London
  and so the next day's, as for every event. So a wrong hour within those windows changes no
  reaction day.
- **The kind, from the rate against the previous decision's**, as the ECB's: *cut*, *hold*,
  *hike*; the first decision has none. The BoJ's rate is the calendar's; its `previous` column
  agrees with the decision before on every one read. Kinds read 2026-11-17: the BoJ 79 holds and
  6 hikes (2024-03-19 the first), no cut.
- **The BoE's rate is the Bank's own.** The calendar lists no decision on 2020-03-11 or 2020-03-19,
  the two emergency cuts (0.75% to 0.25% to 0.1%), and gives 2020-03-26 as the cut. So the kind
  of each BoE decision comes from the Bank of England's published history of Bank Rate changes
  (its *Official Bank Rate history*, read by hand into `data/seed/boe-changes.csv`: day, rate): a
  decision on a day of a change is a *cut* or a *hike* by that change, any other a *hold*; a
  change day the calendar lacks is added, at the hour of the Bank's own announcement. Step 1
  lists every day where the two disagree. From the calendar alone, read 2026-11-17: 16 cuts, 152
  holds, 17 hikes; the Bank's history is expected to give 17 cuts and one more hold.
- **The markets.** Yahoo's `GBPUSD=X`, `JPY=X` (dollars in yen: *up* is the yen weaker) and
  `^N225`, closes checked against intraday bars as [more outcomes](more-outcomes.md) did: the
  pound's and the yen's as the euro's (the price at 00:00 London of its own day), the Nikkei's at
  15:30 Tokyo (15:00 before 2024-11-05, when Tokyo lengthened its session). **Known misses,
  written now:** an event from 15:00 to 15:30 Tokyo before 2024-11-05 is read on the Nikkei a day
  early; two BoE decisions at 07:00 London, 2020-05-07 and 2020-08-06, are among them, and step 1
  lists every stored one. Their signs in every flow's rule: the pound as the euro, against the dollar
  index; the yen as the dollar index; the Nikkei as the S&P 500. The two banks' bonds are not
  added: no free source gives a daily gilt or Japanese government bond yield (FRED's are monthly).
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES`, and
  `--after-the-day`. Shared days are kept, as for the ECB; the results name the other flow.
- **Lesser, as OPEC's:** each decision day stays an ordinary day for every other flow, so no other
  flow's base or table changes; the ECB's flow, older, is not.

## The rule, fixed before anything is shown

- The sources, the kind, the hour and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: an answer needs 10 events of a kind and 30 graded walk-forward,
    with ten earlier ones first. So the BoJ's hikes (6) answer *too few* everywhere; the BoE's
    cuts and hikes answer on all history but are *too few* walk-forward; only holds can hold.
  - Walk-forward: nothing holds, for either bank.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each bank
    and each run (from the close before, from the reaction close). The ECB's run gave none.
  - The pound after a BoE hike and a cut: *can't say* on the day; the decisions are priced in,
    as the ECB's were for the euro.
  - The three markets in the other flows' tables and in raw-move: recorded, not judged.
  - Every existing row of every output unchanged byte for byte: the other flows' `follows` and
    `raw-move` rows and the scoreboard's entries, the new markets' rows added.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The three markets: seed rows, series, signs, `load-prices`; `boe-changes.csv` from the Bank's history | `load-prices` stores the three; a test's 08:30 New York release falls on the next day's close for the pound, the yen and the Nikkei, and a 02:30 UTC one on the same day's Nikkei close; closes checked against intraday bars of one week, written here; every existing row of `raw-move`, `follows` and the scoreboard identical on a copy of the store; the seed test checks `boe-changes.csv`'s header and order; the days where the calendar and the Bank disagree listed here |
| 2 | The BoE: flow `boe`, `follows --event boe`, `boe` in `TRIGGER_KINDS` | Tests: a calendar quarter stores its decisions at their London time; a change day the calendar lacks is added; a decision's kind is the Bank's change; a `boe` trigger is answered. On a copy of the store the header gives the counts by kind, and every other table is unchanged |
| 3 | The BoJ: flow `boj`, `follows --event boj`, `boj` in `TRIGGER_KINDS` | Tests: a quarter stores its decisions at their Tokyo day; a decision's kind is its rate against the previous; a `boj` trigger is answered. The header gives the counts, the others unchanged |
| 4 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet of the expected outcome marked right or wrong with its numbers; each bank's walk-forward records |

## How you know it is right

- **The kinds match the news:** five BoE days checked by hand against the Bank's announcements,
  2009-03-05 cut to 0.5%, 2016-08-04 cut to 0.25%, 2020-03-11 cut to 0.25%, 2022-12-15 hike to
  3.5%, 2025-12-18 cut to 3.75%; and three BoJ days, 2016-09-21 hold (the yield-curve policy
  began, not a rate move), 2024-03-19 hike (the end of negative rates), 2024-07-31 hike to 0.25%.
- **The new markets change nothing else:** every existing row byte for byte, on a copy of the
  store, before and after step 1.
- **A BoJ day reacts the same day in Tokyo:** a test with a decision at 02:30 UTC finds the
  Nikkei's close that day, and the pound's and the yen's the next.

## What this step does not do

No surprise against a forecast: the calendar's forecast equals almost every decision. No votes,
minutes, press conferences or the BoJ's bond-buying and yield-curve decisions, only the rate. No
gilt or JGB yields. A BoJ decision before 2016-04-29, such as the cut to −0.1% of 2016-01-29, is not
in the source and not added.

## Technical details

- **Markets:** three `PriceSeries` in `study.MVP_PRICE_SERIES` (`GBPUSD`, `USDJPY`, `NKY`), seed
  rows in `data/seed/instruments.csv`, a `TOKYO` zone in `sources.py`, their signs in `flows.py`.
- **Flows:** two in `flows.py` on the ECB's pattern, codes 28 (`boe`, `United Kingdom`) and 29
  (`boj`, `Japan`), event type `Central-bank decision`; country `GB` and `JP` in
  `fetch_tradingview_quarter`. The BoE's kinds read `data/seed/boe-changes.csv`; the BoJ's from the
  calendar, as `ecb_kinds`. `FOLLOWS_NOUNS`, `TRIGGER_KINDS` with `KINDS`.
- **Tests** in `tests/test_event_flows.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`
  and `tests/test_seed_data.py`.
- **Docs:** this spec; `docs/schema.md` (codes 28 and 29, the instruments); the glossary (*Bank
  Rate*, *BoJ*); `docs/legacy/data/README.md` (the seed); status, changelog, roadmap row 25.
