# What follows an OPEC+ decision

> Step 24 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the first of phase
> 5's kinds, taken 2026-11-17 by the owner. Terms are in the [Glossary](../glossary.md): *kind*,
> *span*, *base rate*, the four answers, *oil supply surprise*, *OPEC+*.

## The goal

**In plain words:** when OPEC (OPEC+ since 2016) announces what it will pump, and the news pushes
oil up or down, what did each market do over the next day, week and month?

At the end: `fortuneteller follows --event opec` prints [step 17's](what-follows.md) table for
OPEC's announcements, by kind, over the day, the week and the month (not the quarter and the
year, which only the Fed's decisions have), and a trigger file may name `opec`.

## The way to reach it

- **The days come from a list nobody here picks.** Känzig's oil supply news data (*American
  Economic Review* 2021; vintage `oilSupplyNewsShocks_2025M12.xlsx` at
  [github.com/dkaenzig/oilsupplynews](https://github.com/dkaenzig/oilsupplynews), read
  2026-11-17), sheet `Daily`: 169 OPEC announcements, 1983-07-19 to 2025-12-01, each the day
  OPEC's decision came out. Later announcements join with a later vintage, by a dated amendment.
- **The kind is the oil market's own reading.** Each row's *oil supply surprise* (the sheet's `PC`
  column: oil futures over the announcement's day, the first principal component across
  maturities) is positive or negative; none is zero. *Oil up* is a positive surprise, news of less
  oil than expected; *oil down* a negative one. A cut the market expected is not *oil up*. On the
  whole list: 96 *oil up*, 73 *oil down*. Only the sign is copied, not the values. A weekend
  announcement's surprise is the futures' move to the next trading day's close.
- **The day and the hour.** The source gives a date, no hour; 28 dates fall on a weekend. The hour
  is a rule: **08:00 New York**, as the summits' weekday rule: OPEC meets in Vienna and its word
  mostly comes in the European afternoon, before New York's close. Each market reacts at its own
  first close after that hour (`first_reaction_day`); a weekend day reacts on Monday whatever the
  hour, so the summits' 20:00 for a weekend changes nothing here. **Known misses, written now:** a
  word after a market's close is measured a day early on it: after 11:30 New York for Europe's
  indices, after 13:30 for gold and coffee, after 14:30 for Brent, its kind-defining day included.
- **Lesser, as the summits:** each OPEC day stays an ordinary day for every other flow, and the
  flow keeps only its lone reaction days in raw-move. So no other flow's base or table changes.
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES`; and
  `--after-the-day`, from the reaction close. Shared days are kept, as for the ECB; the results
  name the other flow.
- **Brent on the day is near the kind, not a finding.** The surprise is oil futures over that same
  day, so Brent's day cell mostly agrees with the kind; not always, since the surprise spans
  maturities and Brent is the front month. It prints, marked `(the kind)`, and is left out of the
  answers counted against chance and of the expected outcome. Its week and month, and every span
  from the reaction close, are judged.
- **A live trigger's kind** is the sign of Brent's move over its reaction day, close to close,
  read when that close is in; the trigger is answered from the reaction close. Step 1 counts how
  often that sign agrees with the surprise's on the 80 announcements since Brent's first close
  (2007-07-30); a Brent move of zero counts as disagreeing. Below 80%, an `opec` trigger is void:
  logged with no answer, its reason named.
- **One check, not a verdict:** the IMF's coding of 101 OPEC meetings, 1987-06-29 to 2019-07-01,
  as *cut*, *hold* or *boost* (Pescatori and Nazer, *OPEC and the Oil Market*, IMF working paper
  2022/183, table 7: 24 cuts, 19 boosts, 58 holds), 89 of them on a day of Känzig's list, matched
  by date. Only the dates and decisions are copied, into `docs/steps/opec-imf.csv`. A one-off
  script prints step 17's answers on those 89 days twice, by the IMF's decision and by the
  surprise's sign: does the decision say anything the surprise does not?

## The rule, fixed before anything is shown

- The source, the kind, the hour, step 17's bars and Brent's day left out, unchanged by what the
  run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: 30 graded needs 40 events of a kind on a market. *Oil up* has them
    on every market but bitcoin (36); *oil down* only on the S&P 500, the Nasdaq, both yields, the
    dollar, VIX, the DAX, the FTSE 100, energy stocks (49), gold, the euro, the STOXX 600, the
    breakeven, coffee and utilities. Elsewhere it is *too few* walk-forward.
  - On the day: energy stocks (XLE) and gasoline (UGA) with the kind: *up* after *oil up*, *down*
    after *oil down*. Nothing else.
  - Walk-forward: energy stocks on the day hold for *oil up*; nothing else holds.
  - From the reaction close: *can't say* on every market and span. Brent over the week and the
    month: *can't say*.
  - On all history, outside energy stocks and gasoline: no more answers than the chance line
    `follows` prints plus 2, for each run (from the close before, from the reaction close), Brent's
    day cells counted in neither.
  - Live kind agrees with the surprise's sign on at least 80% of the days since 2007-07-30.
  - The IMF check: on the same 89 days, fewer cells answer by the IMF's decision than by the
    surprise's sign; most of a *cut*'s cells *can't say*.
  - Every existing output unchanged byte for byte.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seed~~ **done** 2026-11-17. The seed `data/seed/opec.csv` (day, time, kind) from the vintage; the flow stored; the live kind's agreement counted | The seed test checks the header, 169 rows, days in order and unique, time `08:00`, kind *oil up* or *oil down*; a weekend row reacts on Monday; the agreement written here, in a commit before step 2's; every existing scoreboard entry identical on a copy of the store |
| 2 | `follows --event opec`; `opec` in `TRIGGER_KINDS` with its two kinds; `opec-imf.csv` and the check's script | Tests: an event's kind comes from the seed; an `opec` trigger is answered from the reaction close; Brent's day cell prints `(the kind)`. On a copy of the store the header reads `follows: 169 OPEC announcements 1983-07-19 … 2025-12-01: 96 oil up, 73 oil down`, and the seven other `follows` tables are byte for byte the ones before |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet of the expected outcome marked right or wrong with its numbers; the IMF check's two counts of answered cells; each kind's walk-forward records |

*Step 1, 2026-11-17, on a copy of the store:* 169 announcements stored, 1983-07-19 … 2025-12-01.
The live kind agrees with the surprise's sign on **72 of the 80** announcements since 2007-07-30
(90%; 8 disagree, none flat), above the 80% bar, so an `opec` trigger is answered. No other market
was read. Every one of the scoreboard's 26 existing entries is identical; the page gains the `opec`
entry, and raw-move's chance line its 25 cells (546 → 571).

## How you know it is right

- **The seed matches the source's dates and signs:** four days checked by hand against the news
  of the day: 2014-11-27, OPEC keeps output, *oil down*; 2016-11-30, the first OPEC+ cut deal,
  *oil up*; 2020-04-12 (a Sunday), the pandemic cut, *oil up*, reacting on 2020-04-13; 2022-10-05,
  a cut of two million barrels a day, *oil up*. A date shifted by the spreadsheet's day count, or
  a column or sign read wrong, fails at least one.
- **The flow changes nothing else:** every other flow's `raw-move` and `follows` output and every
  scoreboard entry, byte for byte on a copy of the store.
- **The kind is not read from the answer:** a test where every market moves against the kind
  still prints the kind from the seed.

## What this step does not do

It reads no OPEC communiqué and no hour from one, and no size of cut. Meetings that announce
nothing are not in the source and not added. The surprise's size is not used, only its sign.
Reading OPEC news into a trigger is the backlog's model; until then an `opec` trigger is filed by
hand.

## Technical details

One more `flows.DatedShockFlow`, `OPEC_FLOW`: event type `OPEC+ supply decision` (seed row 17,
tier 5), CLI name `opec`, seed `opec.csv` with header `day,time,kind`, detail column `kind`,
`lesser=True`, `scheduled=False`: the source does not say which meetings were set ahead, and the
extraordinary ones were not. `follows_cells` gives it kinds from each event's detail, order
`("oil up", "oil down")`. The vintage is read once by a one-off script into the seed; no source is
read at run time. Tests in `tests/test_seed_data.py` and `tests/test_study.py`. Docs: this spec,
`docs/schema.md` (the flow's code, event type and detail), the glossary (*OPEC+*, *oil supply
surprise*), `docs/legacy/data/README.md` (the seed file), status, changelog and roadmap row 24.
