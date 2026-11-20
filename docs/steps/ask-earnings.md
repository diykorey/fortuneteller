# Ask about earnings

> Step 32 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the page's *Ask the fortune teller* section ([step 22](ask-the-fortune-teller.md))
answers a Dow company's quarterly earnings report, above, in line with or below the analysts'
consensus, as [step 31](earnings.md) measured it: the company against the S&P 500 over the day,
the week and the month. Earnings are the news a reader meets most often, and three of their links
hold walk-forward. And every cell on the page says when the placebo reads its answer as *the
period*, as `follows` prints it: the page shows such a cell's answer today as if it were the
event's.

At the end: the section answers the three earnings kinds, every cell carries the placebo's mark,
and the evening job keeps both current.

## The way to reach it

- **Step 22's code, one skip shorter.** `ask_data` skips the earnings by name today; the skip goes
  and `ASK_DECISIONS` gains the three kinds' words: "a Dow company's earnings above the consensus"
  (`above`), "a Dow company's earnings in line with the consensus" (`as expected`), "a Dow
  company's earnings below the consensus" (`below`). The market is the CEO kind's, already named
  "the company against the S&P 500". 3 kinds × 3 spans × 1 market: 9 cells.
- **The members' closes, every evening.** `load-prices` without a flag also loads the companies of
  `--companies`, the tickers of `data/seed/ceo_scandals.csv` and `data/seed/earnings.csv`, each
  once (67 today), after the markets, so the evening job and the
  runner keep them current with no change to their scripts. A company Yahoo fails on is printed
  and left out, and `load-prices` still exits 0 for it, as one failed market does not stop the
  others; `--companies` alone keeps exiting 1 on a failure.
- **The placebo's mark on the page.** Each cell gains `"period"`, the value `follows` prints as
  `period` in its placebo column ([Placebo](../glossary.md)): true when the answer on all history
  is *up*, *down* or *about the same* and a placebo gives that same answer. Its sentence ends "With
  each event moved ten closes or a span away, the same answer comes: it reads as the period, not
  the event."; for the jobs report and jobless claims, released on a fixed weekday, "the period or
  the weekday", as [step 17, part 1b](what-follows-jobs.md) reads it. Like a kind cell ([step
  29](ask-phase-5.md)), its answer and replay are not coloured; a cell both a kind cell and marked
  ends with both sentences. A marked cell's hold is not counted among the page's holds.
- **The time it takes.** `follows --event earnings` took 11 min 16 s a run before PR #367 and
  59 s after, on a copy of the real store ([changelog](../changelog.md)); the page adds one run
  (spans from the event's day) to the evening's `scoreboard`, which the evening job (the laptop's,
  and the runner's in [step 21](loop-off-the-laptop.md)'s shadow) runs after `load-prices`.
- **The seed stays step 31's:** reports to 2026-11-17. Adding later reports is a step of its own.

## The rule, fixed before measuring

This step measures nothing new; it shows step 31's numbers and the placebo `follows` already
prints.

- **Same numbers:** every earnings cell equals the line `follows --event earnings` prints for its
  kind, span and market, field by field as [step 22's rule](ask-the-fortune-teller.md#the-rule-fixed-before-measuring)
  reads it; each kind's event count equals `follows`' header. Every cell of every flow carries
  `period` true exactly where `follows --event FLOW` prints `period` (the Fed's long spans as
  `follows --event fomc --long` prints them).
- **Expected outcome, written before the page is built on real data:**
  - The earnings add exactly three cells that hold, as in [step 31's
    Results](earnings.md#results) (whose expected outcome had foreseen one): *below*'s day and
    week, *as expected*'s day; and exactly one earnings cell marked *the period*, *above*'s day,
    which does not hold.
  - Across every flow, exactly three cells carry `period` true, as `follows --event FLOW` (and
    `--long` for the Fed) prints them on a copy of the real store of 2026-11-19 16:08: the
    earnings' *above* day; after a jobs report above the consensus, the euro's day (*down*, as in
    [step 17, part 1b's Results](what-follows-jobs.md#results)); after one as expected, natural
    gas's day (*about the same*). The Fed, the ECB, the BoE, the BoJ, CPI, retail sales, claims,
    the CEO flow, OPEC+, violent acts, hacks and landfalls print none; floods were not in that
    store, and [step 30's Results](floods.md#results) print none. None of the three holds.
  - So the page shows seven holds: step 22's three, step 29's gasoline after *oil up*, and the
    earnings' three.
  - A release or report since may move a count by one or two. Another hold or mark, or a missing
    one, fails this outcome and is written in Results with its numbers.
- **The evening job:** `scoreboard`, run once on main's code and once on this step's, each on its
  own copy of the same store, takes no more than 3 minutes longer on this step's (wall clock, by
  `time`); `load-prices` loads 67 of 67 companies.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The skip goes; the three kinds' words; `period` on every cell, its sentence and the page's script; `load-prices` loads the companies~~ **done** 2026-11-19 ([evidence](ask-earnings-steps.txt)): 3 kinds, 9 earnings cells, 7 holds and 3 period marks, as expected; `scoreboard` 1 min 36 s longer | The tests below pass; on a copy of the real store the data holds the 3 kinds and 9 earnings cells, nothing left out, and the period marks and holds as the expected outcome counts them; the two `scoreboard` times against the 3-minute bar, in `docs/steps/ask-earnings-steps.txt` |
| 2 | On the published page, after the evening job | The 3 kinds appear with their 9 cells; a one-off script reads the published data and every flow's `follows` lines (the Fed's `--long` too) on the real store, and finds every cell's numbers and `period` equal, its output in the evidence; each bullet of the rule judged right or wrong in Results, with its numbers; a goldfish review of the Results |

## How you know it is right

- **Same numbers, by a test:** on a store with reports of the three kinds and closes, every
  earnings cell in the data equals the `follows --event earnings` line for its kind, span and
  market, field by field, and each sentence opens with its own kind's words, so a swapped label
  fails.
- **The placebo's mark, by a test:** on a store where the placebo gives a cell's answer,
  that cell carries `period` true and its sentence ends with the words above; a cell the placebo
  does not mark carries false; the written page's script leaves a `period` cell uncoloured.
- **The companies, by a test:** `load-prices` with one company's fetch raising loads the others,
  prints the failure and exits 0; `load-prices --companies` with the same failure exits 1.
- **No percentage, by a test:** no earnings sentence holds a "%" sign.
- **On screen:** step 2 opens the published page, picks *below*, and sees the day and the week
  held, and *above*'s day uncoloured.

## What this step does not do

- No new report after 2026-11-17, no trigger for a report, no call made live, no new market.
- It shows no reaction-close run (`--after-the-day`), as the rest of the page shows none.

## Technical details

- `__main__.py`: the earnings skip in `ask_data` goes; `ASK_DECISIONS["earnings"]`; `ask_cell`
  gains `period` from `Follow.period`; `ask_say` appends the sentence; `_load_prices` calls
  `_load_companies`' fetch after the markets. `scoreboard.html` leaves a `period` cell
  uncoloured. Tests in `tests/test_scoreboard.py` and `tests/test_ceo_scandals.py`, given / when /
  then.
- Docs: [Schema](../schema.md) if the data file is described there, glossary (*the period* is
  already *Placebo*), roadmap, status, changelog.
