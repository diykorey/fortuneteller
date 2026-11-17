# What follows an OPEC+ decision

> Step 24 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the first of phase
> 5's kinds, taken 2026-11-17 by the owner. Terms are in the [Glossary](../glossary.md): *kind*,
> *span*, *base rate*, the four answers, *oil supply surprise*, *OPEC+*.

## The goal

**In plain words:** when OPEC (OPEC+ since 2016) announces what it will pump, and the news pushes
oil up or down, what did each market do over the next day, week and month?

At the end: `fortuneteller follows --event opec` prints [step 17's](what-follows.md) table for
OPEC's announcements, by kind, and a trigger file may name `opec`.

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
  whole list: 96 *oil up*, 73 *oil down*. Only the sign is copied, not the values.
- **The day and the hour.** The source gives a date, no hour; 28 dates fall on a weekend. The hour
  is a rule: **08:00 New York**, as the summits' weekday rule: OPEC meets in Vienna and its word
  mostly comes in the European afternoon, before New York's close. Every market reacts on that day
  if it trades, else on its next close (`first_reaction_day`). A word after Europe's close is
  measured a day early in Europe's four indices and the euro: a known miss, written now.
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES`; and
  `--after-the-day`, from the reaction close. Shared days are kept, as for the ECB; the results
  name the other flow.
- **Brent on the day is the kind, not a finding.** The surprise is oil futures over that same day,
  so Brent's day cell agrees with the kind by construction. It prints, and is left out of the
  answers counted against chance and of the expected outcome. Its week and month, and every span
  from the reaction close, are judged.
- **A live trigger's kind** is the sign of Brent's move over its reaction day, close to close,
  read when that close is in; the trigger is answered from the reaction close. Step 1 counts how
  often that sign agrees with the surprise's on the announcements since Brent's first close
  (2007-07-30). Below 80%, an `opec` trigger is void, and says so.
- **One check, not a verdict:** the IMF's coding of 101 OPEC meetings, 1987-06-29 to 2019-07-01,
  as *cut*, *hold* or *boost* (Pescatori and Nazer, *OPEC and the Oil Market*, IMF working paper
  2022/183, table 7), 89 of them in Känzig's list. A one-off script prints step 17's answers by
  that decision on those days: does the decision say anything the surprise does not?

## The rule, fixed before anything is shown

- The source, the kind, the hour, step 17's bars and Brent's day left out, unchanged by what the
  run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: since energy stocks' first close (1998-12-22), 73 *oil up* and 49
    *oil down*; both kinds can reach 30 graded walk-forward on most markets.
  - On the day: energy stocks (XLE) and gasoline (UGA) with the kind: *up* after *oil up*, *down*
    after *oil down*. Nothing else.
  - Walk-forward: energy stocks on the day hold for *oil up*; nothing else holds.
  - From the reaction close: *can't say* on every market and span. Brent over the week and the
    month: *can't say*.
  - On all history, outside energy stocks and gasoline: no more answers than the chance line plus 2.
  - Live kind agrees with the surprise's sign on at least 80% of the days since 2007-07-30.
  - The IMF check: a *cut* says less than *oil up*; most of its cells *can't say*.
  - Every existing output unchanged byte for byte.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed `data/seed/opec.csv` (day, time, kind) from the vintage; the flow stored; the live kind's agreement counted | The seed test checks the header, 169 rows, days in order and unique, time `08:00`, kind *oil up* or *oil down*; a weekend row reacts on Monday; the agreement written here before any other market is read; every existing scoreboard entry identical on a copy of the store |
| 2 | `follows --event opec`; `opec` in `TRIGGER_KINDS` with its two kinds; the IMF check | Tests: an event's kind comes from the seed; an `opec` trigger is answered from the reaction close; Brent's day cell is marked as the kind. On a copy of the store the header gives the counts by kind, and the other tables are unchanged |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Each kind's answers and walk-forward records recorded |

## What this step does not do

It reads no OPEC communiqué and no hour from one, and no size of cut. Meetings that announce
nothing are not in the source and not added. The surprise's size is not used, only its sign.
Reading OPEC news into a trigger is the backlog's model; until then an `opec` trigger is filed by
hand.

## Technical details

One more `flows.DatedShockFlow`, `OPEC_FLOW`: event type `OPEC+ supply decision` (seed row 17,
tier 5), CLI name `opec`, seed `opec.csv` with header `day,time,kind`, detail column `kind`,
`scheduled=False`. `follows_cells` gives it kinds from each event's detail, order
`("oil up", "oil down")`. The vintage is read once by a one-off script into the seed; no source is
read at run time. Tests in `tests/test_seed_data.py` and `tests/test_study.py`. Docs: this spec,
`docs/schema.md` (the flow's code, event type and detail), the glossary (*OPEC+*, *oil supply
surprise*), `docs/legacy/data/README.md` (the seed file), status, changelog and roadmap row 24.
