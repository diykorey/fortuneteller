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
  *Amended 2026-11-24, by [step 57's R3](technical-fixes.md):* every market's spans are judged from
  its first close at or after Brent's reaction close, since every span from the close before, and
  Europe's and gold's from their own reaction close, hold the close that reads the kind. The run
  from the close before still prints, each row marked `(not judged)`. Gasoline's day after *oil
  up* (31 replayed, 20 right), the one answer that held, is gone with it: no OPEC cell holds.
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
| 2 | ~~`follows --event opec`~~ **done** 2026-11-17. `follows --event opec`; `opec` in `TRIGGER_KINDS` with its two kinds; `opec-imf.csv` and the check's script | Tests: an event's kind comes from the seed; an `opec` trigger is answered from the reaction close; Brent's day cell prints `(the kind)`. On a copy of the store the header reads `follows: 169 OPEC announcements 1983-07-19 … 2025-12-01: 96 oil up, 73 oil down`, and the seven other `follows` tables are byte for byte the ones before |
| 3 | ~~Results~~ **done** 2026-11-17, [below](#results). Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet of the expected outcome marked right or wrong with its numbers; the IMF check's two counts of answered cells; each kind's walk-forward records |

*Step 1, 2026-11-17, on a copy of the store:* 169 announcements stored, 1983-07-19 … 2025-12-01.
The live kind agrees with the surprise's sign on **72 of the 80** announcements since 2007-07-30
(90%; 8 disagree, none flat), above the 80% bar, so an `opec` trigger is answered. No other market
was read. Every one of the scoreboard's 26 existing entries is identical; the page gains the `opec`
entry, and raw-move's chance line its 25 cells (546 → 571).

*Step 2, 2026-11-17, on a copy of the store:* `follows --event opec` heads its table
`follows: 169 OPEC announcements 1983-07-19 … 2025-12-01: 96 oil up, 73 oil down`, and marks
Brent's two day cells `(the kind)`, from the close before only. The seven other flows' tables,
from the close before and from the reaction close, and the Fed's `--long`, 15 outputs, are byte
for byte those of `main` before. A live `opec` trigger takes its kind from Brent's reaction day:
waiting until that close is in, void if it differs from the kind filed; a stored announcement's
trigger keeps the seed's kind. `docs/steps/opec-imf.csv` holds the IMF's 101 meetings (its
*neutral* written *hold*); `scripts/opec_imf.py` finds 89 on a day of the list, as written above.
*Amended 2026-11-17, in step 2:* the page's *ask* leaves OPEC out for now: there Brent's day cell
would show without its mark. Adding it is its own change, after step 3.

## Results

Measured 2026-11-17 on a copy of the store taken that day, its last Brent close 2026-11-16 (read
from `daily_bars` in a one-off query). Every number in this section, unless it says otherwise, is
printed by `fortuneteller follows --event opec` (from the close before), `fortuneteller follows
--event opec --after-the-day` (from the reaction close) or `uv run python scripts/opec_imf.py` (the
IMF check); the three outputs are in [the evidence](opec-results.txt). 169 announcements, 96 *oil
up* and 73 *oil down*; 25 markets, three spans, two kinds: 150 cells a run. Brent's two day cells
are marked in the run from the close before; the run from the reaction close marks none.

**What answers, from the close before** (up / same / down; chance):

| Kind | Span | Market | Counts | Answer | Chance | Walk-forward |
| --- | --- | --- | --- | --- | --- | --- |
| oil up | day | XLE | 40 / 22 / 11 | up | 0.0002 | 47 graded, 25 right, *doesn't hold* |
| oil up | day | UGA | 30 / 14 / 4 | up | 0.0000 | 31 graded, 20 right, **holds** |
| oil up | day | T5YIE | 33 / 15 / 14 | up | 0.0068 | 23 graded, *too few* |
| oil up | week | BRN | 28 / 9 / 8 | up | 0.0024 | 29 graded, *too few* |
| oil up | week | XLE | 38 / 20 / 12 | up | 0.0020 | 17 graded, *too few* |
| oil up | week | UGA | 25 / 15 / 5 | up | 0.0008 | 27 graded, *too few* |
| oil up | month | BRN | 21 / 13 / 2 | up | 0.0001 | 13 graded, *too few* |
| oil up | month | XLE | 32 / 19 / 8 | up | 0.0033 | 8 graded, *too few* |
| oil up | month | UGA | 23 / 12 / 2 | up | 0.0002 | 13 graded, *too few* |
| oil down | day | XLE | 8 / 12 / 29 | down | 0.0001 | 16 graded, *too few* |
| oil down | day | UGA | 1 / 3 / 25 | down | 0.0000 | 19 graded, *too few* |
| oil down | week | BRN | 2 / 8 / 21 | down | 0.0000 | 19 graded, *too few* |
| oil down | week | XLE | 8 / 16 / 25 | down | 0.0003 | 9 graded, *too few* |
| oil down | week | UGA | 3 / 9 / 17 | down | 0.0004 | 17 graded, *too few* |
| oil down | week | T5YIE | 8 / 12 / 22 | down | 0.0056 | 7 graded, *too few* |

Brent's day, marked `(the kind)` and not counted: *up* after *oil up* (35 / 13 / 1, 36 graded, 28
right, holds), *down* after *oil down* (1 / 3 / 27, 20 graded, *too few*). The chance line: about
4.4 answers on all history.

**From the reaction close**, five cells answer, against about 4.5 by chance: *oil up*, the FTSE 100
over the day *about the same* (0.0083) and gasoline over the month *up* (0.0010); *oil down*, the
10-year and the 5-year yields over the day *down* (0.0097, 0.0009) and defence stocks (ITA) over
the month *down* (0.0063). None holds walk-forward; the DAX's day after *oil down*, 33 graded and
12 right, *doesn't hold*.

**Walk-forward records, each kind:** from the close before, *oil up* has two cells graded 30 or
more, gasoline's day (31, 20 right, holds) and energy stocks' day (47, 25 right, doesn't hold),
besides Brent's marked day; *oil down* has one, the dollar's week (42, 13 right, *doesn't hold*;
its answer *can't say*). From the reaction close, only the DAX's *oil down* day (33, 12 right).
Every other cell is *too few*. Gasoline's day clears step 17's bar: 20 of 31 is 65% right against
a base of 0.35 for *up*, 30 points over it, and the chance of 20 or more right of 31 at 0.35 is
0.0008, under 0.01 (the binomial, computed here; `follows` prints only *holds*).

**The IMF check.** 89 of the IMF's 101 meetings fall on a day of the list, 1987-12-14 … 2018-12-07:
20 *cut*, 53 *hold*, 16 *boost*; by the surprise, 50 *oil up* and 39 *oil down*. By the IMF's
decision **no cell answers** (0, Brent's day left out); by the surprise's sign **6 do**: energy
stocks' and gasoline's day and gasoline's and Brent's week after *oil up*, Brent's week after *oil
down*, and the S&P 500's month after *oil down* (*about the same*), against a chance line of about 3.7;
five of the six are oil, energy stocks or gasoline. Of a *cut*'s 75 cells, 39 *can't say* and 36
are *too few*; with 16 boosts, most *boost* cells are *too few* as well.

**In plain words:** counted from the close before the announcement, when OPEC's news pushes oil up,
energy stocks and gasoline rise with it that day and over the week and month; when it pushes oil
down, they fall that day and week. Only gasoline's day after *oil up* also holds when replayed in
order. Outside oil, energy stocks and gasoline, there are no more answers than chance plus two
allows. Counted from the reaction close, as a live trigger is answered, the move is already in:
energy stocks and gasoline answer nothing over the day or the week, and five scattered cells
answer, about what chance gives. On the IMF's 89 meetings, its *cut*, *hold* or *boost* answers no
cell, while the oil market's reading answers six, mostly oil itself; most of the decision's cells
have too few events to answer at all, so this says the reading carries more, not that the decision
carries nothing.

**Against the expected outcome:**

- The arithmetic (*oil up* 40 events on every market but bitcoin, 36; *oil down* only on the 15
  named): **right** on the day's counts, which the bullet was written from; every *oil down* cell
  elsewhere is *too few* walk-forward. Over the week and the month fewer events are kept, and
  several *oil up* markets fall under 40, among them corn 39, wheat and soybeans 37 over the week,
  and Brent 36 and the STOXX 50 31 over the month; those cells are *too few* walk-forward too.
- On the day, energy stocks and gasoline with the kind, nothing else: **wrong**. Both answer with
  the kind, *up* and *down*; but the breakeven (T5YIE) also answers *up* after *oil up*
  (33 / 15 / 14, 0.0068).
- Walk-forward, energy stocks' day holds for *oil up*, nothing else: **wrong**. Energy stocks'
  day, 47 graded, 25 right, *doesn't hold*; gasoline's day, 31 graded, 20 right, holds.
- From the reaction close, *can't say* everywhere: **wrong**, five cells answer (above). Brent's
  week and month *can't say*: **right**.
- Outside energy stocks and gasoline, no more than chance plus 2: **right** on both runs. From the
  close before 5 (T5YIE's day, Brent's week twice, Brent's month, T5YIE's week) against 4.4 + 2;
  from the reaction close 4 (gasoline's month left out) against 4.5 + 2.
- The live kind agrees on at least 80% since 2007-07-30: **right**, 72 of 80 (step 1's note,
  counted by a one-off script from the seed and Brent's stored closes).
- The IMF check, fewer cells by the IMF's decision than by the surprise's sign: **right**, 0
  against 6. Most of a *cut*'s cells *can't say*: **right**, 39 of 75; the other 36 are *too few*.
- Every existing output unchanged: **right** for what was compared: the scoreboard's 26 existing
  entries, identical (step 1's note), and the seven other flows' `follows` tables, 15 outputs,
  byte for byte (step 2's note, by `follows` on `main` before and after). Other flows' `raw-move`
  output was not compared on its own; the scoreboard page, which draws on it, gained the `opec`
  entry and raw-move's chance line its 25 cells (546 → 571), as step 1 says.

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
read at run time. Tests in `tests/test_seed_data.py`, `tests/test_study.py`, `tests/test_what_follows.py` and
`tests/test_triggers.py`; the IMF check is `scripts/opec_imf.py`. Docs: this spec,
`docs/schema.md` (the flow's code, event type and detail), the glossary (*OPEC+*, *oil supply
surprise*), `docs/legacy/data/README.md` (the seed file), status, changelog and roadmap row 24.
