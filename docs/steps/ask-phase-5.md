# Ask about phase 5's kinds

> Step 29 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the page's *Ask the fortune teller* section ([step 22](ask-the-fortune-teller.md))
answers the kinds phase 5 measured, as it answers the jobs report: an OPEC+ decision, a Bank of
England or Bank of Japan decision, a violent act that set off an international crisis, a crypto
hack, a US hurricane landfall. Steps 24 to 28 measured them; today only `follows` prints them, so
a reader of the page cannot pick one.

At the end: the section answers every kind below, and the evening job keeps it current.

| Flow | Its kinds, as the page names them | Measured in |
| --- | --- | --- |
| `opec` | an OPEC+ decision that sent oil up; one that sent oil down | [step 24](opec.md) |
| `boe` | a Bank of England rate cut; the Bank of England holding its rate; a Bank of England rate hike | [step 25](other-central-banks.md) |
| `boj` | the same three for the Bank of Japan (no cut on record: listed with 0 events, every cell *too few*, as `follows` prints it) | [step 25](other-central-banks.md) |
| `war` | a violent act setting off an international crisis | [step 26](war.md) |
| `crypto` | a crypto hack of $100 million or more | [step 27](crypto.md) |
| `weather` | a US hurricane landfall | [step 28](weather.md) |

Eleven kinds. Spans are the day, the week and the month from the event's day, as `follows` prints
by default, on each of the 31 markets: 93 cells a kind, 1,023 in all (OPEC 186, each bank 279,
the three one-kind flows 93 each).

## The way to reach it

- **Step 22's code, one list shorter.** `ask_data` skips these six flows by name today; the skip
  goes, and each kind gets its words in `ASK_DECISIONS`. Nothing else in the computation changes:
  `follows_cells` already computes all six.
- **Brent's day after OPEC is the kind, not an answer.** An OPEC+ decision's kind is the sign of
  Brent's own move that day, so Brent's day cell after it answers itself; `follows` prints it
  marked. On the page that cell carries `"kind_cell": true` (false for every other cell); neither
  its answer nor its replay is coloured, even where it holds; its sentence keeps its counts and
  replay words and ends "This is how the kind is read, not an answer."
- **A flow that cannot be computed is named.** The Bank of Japan's kinds need its rates from
  TradingView's calendar, fetched (or read from its cache) when the page is built. The BoE's
  days were stored by `load-releases` and its kinds come from the seed `boe-changes.csv`, so it
  needs no fetch then. If the BoJ fetch fails, the BoJ is listed as left out with the error, and
  the other flows still show, as with the Fed without a FRED key.

## The rule, fixed before measuring

This step measures nothing new; it shows steps 24 to 28 exactly.

- **Same numbers:** for each of the six flows, every cell equals the line `follows --event FLOW`
  prints for that kind, span and market, field by field as [step 22's
  rule](ask-the-fortune-teller.md#the-rule-fixed-before-measuring) reads it; each kind's event
  count equals `follows`' header.
- **Expected outcome, written before the page is built on real data:** among the six flows,
  exactly one unmarked cell holds walk-forward: gasoline (UGA) on the day after *oil up*, 31
  graded, 20 right in [step 24's Results](opec.md#results); the BoE, the BoJ, violent acts, hacks
  and landfalls hold nothing (each step's Results). Exactly two cells are marked as the kind:
  Brent's day after *oil up* and after *oil down*; the first also holds (36 graded, 28 right) and
  is not counted as an answer. The page's three earlier holds stay. So the page shows four
  answers that hold. Releases since a step's Results may move a count by one or two; another
  hold, a missing one, or a marked cell elsewhere is written in this spec's Results with its
  numbers before the step is done.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The six flows in `ask_data`, their words, the kind cell, the BoJ left out on a failed fetch~~ **done** 2026-11-19; on a copy of the real store the data held the 11 kinds and 1,023 cells, nothing left out, before publishing | The four tests below pass |
| 2 | On the published page, after the evening job | The 11 new kinds appear with 1,023 cells; every cell equals `follows`' line on the real store (a one-off comparison, its output in the evidence); the expected outcome holds, or each difference is written in Results with its numbers |

## How you know it is right

- **Same numbers and the right words, by a test:** on a store with OPEC decisions of both kinds
  and prices, every OPEC cell in the data equals the `follows --event opec` line for the same kind,
  span and market, field by field, and each sentence opens with its own kind's words ("After an
  OPEC+ decision that sent oil up," for *oil up*), so a swapped label fails.
- **The kind cell, by a test:** on that store, exactly Brent's two day cells carry `kind_cell`
  true, their sentences end with the words above, and the written page's script leaves a cell
  with `kind_cell` uncoloured.
- **No silent gap, by a test:** with the BoJ fetch raising, the BoJ is in `ask_left_out` with the
  error and the BoE is in `ask`.
- **No percentage, by a test:** no sentence of the new flows holds a "%" sign.
- **On screen:** step 2 opens the published page, picks each new kind, and sees Brent's day after
  OPEC uncoloured.

## What this step does not do

- It adds no kind, market or span, changes no bar, and reads no news.
- It shows no reaction-close run (`--after-the-day`); the page shows spans from the event's day.

## Technical details

- **Names:** `ask_data` builds the page's *ask* data; `ask_cell` one cell; `ask_say` its sentence;
  `ASK_DECISIONS` maps each flow's kind to the words the picker and the sentences use.
  `study.KIND_SPAN` and `study.KIND_MARKET` are `day` and Brent (`BRN`), the cell `follows` marks.
- **Step 1:** `__main__.py`: the skip in `ask_data` goes; `ASK_DECISIONS` gains `opec`, `boe`,
  `boj`, `war`, `crypto`, `weather`; `ask_cell` gains `kind_cell`, true for `opec` at
  (`study.KIND_SPAN`, `study.KIND_MARKET`); `ask_say` appends the sentence there; `ask_data`
  catches the BoJ fetch's error as a reason. `scoreboard.html` leaves a kind cell uncoloured.
  Tests in `tests/test_scoreboard.py` and the flows' own test files, given / when / then.
- **Step 2:** the evening job's next run writes the data; checked as step 22's step 5 was.
