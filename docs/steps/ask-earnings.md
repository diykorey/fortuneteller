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
| 2 | ~~On the published page, after the evening job~~ **done** 2026-11-20 | The 3 kinds appear with their 9 cells; a one-off script reads the published data and every flow's `follows` lines (the Fed's `--long` too) on the real store, and finds every cell's numbers and `period` equal, its output in the evidence; each bullet of the rule judged right or wrong in Results, with its numbers; a goldfish review of the Results |

## Results

*2026-11-20.* Every line quoted is in [the evidence](ask-earnings-steps.txt), step 2's part: the
published page's `data.json` (by `curl`) after the evening job of 2026-11-19 (PR #373, deployed 01:13 UTC),
`follows --event FLOW` for all 15 flows on the page and `follows --event fomc --long`, on a copy of
the real store taken after that job, the comparison of every cell with its line (`python3 -I
cmp32.py data.json FOLLOWS_DIR`, the script at the end of the evidence), and the page read in
Chrome.

**In plain words:** the published page answers what followed a Dow company's earnings above, in
line with or below the consensus, with `follows`' numbers, and marks every cell where shifting the
events in time gives the same answer. Three earnings answers held when replayed: a miss's day and
week and an in-line report's day, each a fall behind the S&P 500. A beat's day is grey, since it
reads as the period, not the event. The expected outcome held on every count.

- **Same numbers:** all 2,988 cells of the 15 flows equal `follows`' line for their kind, span and
  market, field by field, the placebo's `period` and the Fed's cycles on its quarter and year
  included; the 9 earnings cells among them, and each earnings kind's count equals `follows`'
  header (2,092 reports: 1,513 above, 337 as expected, 242 below; `follows --event earnings`).
  Right. One cell moved by one since [step 31's Results](earnings.md#results), within the one or
  two the rule allows: *above*'s day now counts 1,499 reports, 582 down (was 1,498 and 581), and
  is graded 1,356 times, 707 right (was 1,355), as `follows --event earnings` prints it.
- **The earnings add exactly three holds and one period mark:** *below*'s day (219 graded, 156
  right) and week (217, 145), *as expected*'s day (303, 183); *above*'s day marked *the period*,
  and it does not hold (1,356, 707), each as `cmp32.py` and `follows --event earnings` print it.
  Right.
- **Exactly three period marks across every flow:** the earnings' *above* day; the euro's day after
  a jobs report above the consensus (*down*, does not hold); natural gas's day after one as
  expected (*about the same*, *too few*). No other flow, the floods included, has one, and none of
  the three holds (`cmp32.py`, page to `follows`). The other way, the 16 `follows` outputs print
  `period` on exactly these three lines and no other (`grep`, in the evidence). Right.
- **Seven holds on the page:** step 22's three (the 10- and 5-year yields on the day of a jobs
  report above the consensus, 58 graded, 39 and 38 right; the 5-year breakeven on the day of a CPI
  release above it, 31, 23), step 29's gasoline after *oil up* (31, 20) and the earnings' three.
  Right.
- **The evening job:** `scoreboard` took 12 min 10 s on this step's code against 10 min 34 s on
  main's, 1 min 36 s longer, under the 3-minute bar (`time fortuneteller scoreboard`, step 1's
  evidence); `load-prices` loaded 67 of 67 companies in the evening job of 2026-11-19 (its log, by
  `journalctl`). That job was the one run by hand at 02:53 EET, after the scheduled 01:00 run
  failed on FRED's HTTP 500 (issue #371) before any price load. Right.
- **On screen:** *below* picked on the published page shows the day and the week held, coloured;
  *above*'s day is grey, answer and replay alike, its sentence ending with the placebo's words.
  Right.

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
