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
| `boj` | the same three for the Bank of Japan | [step 25](other-central-banks.md) |
| `war` | a violent act setting off an international crisis | [step 26](war.md) |
| `crypto` | a crypto hack of $100 million or more | [step 27](crypto.md) |
| `weather` | a US hurricane landfall | [step 28](weather.md) |

Spans are the day, the week and the month from the event's day, as `follows` prints by default.

## The way to reach it

- **Step 22's code, one list shorter.** `ask_data` skips these six flows by name today; the skip
  goes, and each kind gets its words in `ASK_DECISIONS`. Nothing else in the computation changes:
  `follows_cells` already computes all six.
- **Brent's day after OPEC is the kind, not an answer.** An OPEC+ decision's kind is the sign of
  Brent's own move, so Brent's day cell after it answers itself; `follows` prints it marked. On
  the page that cell carries `"kind_cell": true` (false for every other cell), is never coloured as
  an answer, and its sentence ends "This is how the kind is read, not an answer."
- **A flow that cannot be computed is named.** The Bank of Japan's kinds need its rates from
  TradingView's calendar. If that fetch fails, the BoJ is listed as left out with the error, and
  the other flows still show, as with the Fed without a FRED key.

## The rule, fixed before measuring

This step measures nothing new; it shows steps 24 to 28 exactly.

- **Same numbers:** for each of the six flows, every cell equals the line `follows --event FLOW`
  prints for that kind, span and market, field by field as [step 22's
  rule](ask-the-fortune-teller.md#the-rule-fixed-before-measuring) reads it; each kind's event
  count equals `follows`' header.
- **Expected outcome, written before the page is built on real data:** no cell of the six flows
  holds walk-forward (each step's Results: nothing holds), and the page's three holds, the 10-year
  and 5-year yields after a jobs report above the consensus and the breakeven after a CPI above
  it, stay the only ones. Exactly two cells are marked as the kind: Brent's day after each of
  OPEC's two kinds. A hold among the six, or a marked cell elsewhere, is a finding to explain before
  the step is done.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The six flows in `ask_data`, their words, the kind cell, the BoJ left out on a failed fetch | Tests below pass |
| 2 | On the published page, after the evening job | The 13 new kinds appear with their cells; the expected outcome is checked on the published data |

## How you know it is right

- **Same numbers, by a test:** on a store with the war flow's events and prices, every war cell in
  the data equals the `follows --event war` line, field by field.
- **The kind cell, by a test:** on a store with OPEC decisions, exactly Brent's day cells carry
  `kind_cell` true, and their sentences end with the words above.
- **No silent gap, by a test:** with the BoJ fetch raising, the BoJ is in `ask_left_out` with the
  error and the BoE is in `ask`.
- **No percentage, by a test:** no sentence of the new flows holds a "%" sign.
- **On screen:** step 2 opens the published page and picks each new kind.

## What this step does not do

- It adds no kind, market or span, changes no bar, and reads no news.
- It shows no reaction-close run (`--after-the-day`); the page shows spans from the event's day.

## Technical details

- **Step 1:** `__main__.py`: the skip in `ask_data` goes; `ASK_DECISIONS` gains `opec`, `boe`,
  `boj`, `war`, `crypto`, `weather`; `ask_cell` gains `kind_cell`, true for `opec` at
  (`study.KIND_SPAN`, `study.KIND_MARKET`); `ask_say` appends the sentence there; `ask_data`
  catches the BoJ fetch's error as a reason. `scoreboard.html` leaves a kind cell uncoloured.
  Tests in `tests/test_scoreboard.py` and the flows' own test files, given / when / then.
- **Step 2:** the evening job's next run writes the data; checked as step 22's step 5 was.
