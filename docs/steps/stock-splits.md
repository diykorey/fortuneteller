# Stock splits

> Step 37 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** "Nvidia announces a 10-for-1 split" makes the news. A split changes nothing a
company owns; does anything follow the announcement anyway? A reader who brings "X will split its
shares" should be told what followed such announcements by large US companies.

At the end: `follows --event splits` prints what followed each announcement against the S&P 500,
from the close before and from the reaction close, against the rule below written first.

## The way to reach it

- **The splits: Yahoo's.** The chart endpoint the closes already come from gives each ticker's
  splits (`events=split`: the day it takes effect and the ratio). Asked for the 598 companies of
  [step 36](earnings-sp500.md)'s seed and kept when the company was an S&P 500 member that day
  (`data/seed/sp500.csv`), from 2011, forward splits only (a ratio above 1: a reverse split is a
  different story, of a falling price).
- **The announcement: the first 8-K.** The SEC's full-text search (from 2001) asked, per split, for
  the company's 8-Ks with "stock split" in the 120 days before the split's day; the first one's
  acceptance minute is the event, as the 8-K is the earnings' minute in step 31. A split with no
  such 8-K is *no 8-K*, counted and left out.
- **The kind: alone or with a report.** Many splits are announced in the earnings release (Nvidia's
  of 2024-05-22). A split whose 8-K carries Item 2.02 is *with a report*, the rest *alone*: two
  kinds, since a report's own move would otherwise be read as the split's.
- **The flow:** `splits`, type code 37, event type `Stock split`, the earnings' class with seed
  `data/seed/stock_splits.csv` (`day`, `time`, `ticker`, `ratio`, `effective`, `kind`). Like step
  36's, not loaded each evening and not on the page; measured on a copy of the store, its closes
  by `load-prices --companies --seed`.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price and no count: Nvidia's four splits on Yahoo, and its
2024 announcement in an 8-K with Item 2.02.*

- `follows`' bars, as step 31's: under 10 events *too few*; an answer at p < 0.01 against the
  company's own base (for *up* and *down*, its share of up among its moved spans); a link *holds*
  at 60% right of at least 30 graded walk-forward, 10 points over the base, p < 0.01; an answer the
  placebo also gives is printed as *the period*, not counted.
- **Expected outcome:** between 100 and 300 forward splits kept. *Alone*: *up* on the day from the
  close before, not holding; the week and the month *can't say*. *With a report*: *can't say* on
  every span (the report's surprise, not the split, moves it, and the kind does not know the
  surprise). From the reaction close, every cell *can't say*. Answers beyond these at most the
  chance line plus two. Every other flow's `follows` unchanged.

## How you know it is right

- Five splits by hand (the seed's 1st, a quarter, half, three quarters and its last) against the
  company's own release: the ratio, the effective day, and the announcement's day; a wrong day or
  ratio on two of the five stops step 1 for the owner's call.
- Every 8-K kept names the split: its text read for "split" near a ratio, by the script, the
  others listed.
- Five announcements' excess day moves by hand against `study.excess_spans`, within 0.1 point.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scripts/stock_splits.py`: the splits, the 8-Ks, the seed | `stock_splits.csv` with a seed test (ratios above 1, members on the day, the kind from Item 2.02, an announcement 1 to 120 days before the effective day); the checks above in `docs/steps/stock-splits-steps.txt` |
| 2 | The flow | Tests: one event a split, two kinds; `follows` prints them; not in `company_tickers()` nor on the page; `just check` passes |
| 3 | Results | `follows --event splits` both ways on a copy of the store, every flow's `follows` compared both ways, the five excess checks; each expected cell judged in the Results section, goldfish-reviewed; roadmap, status, changelog, schema updated |

## What this step does not do

- No reverse splits, no splits before 2011 or outside the S&P 500, no move on the effective day.
- No page, no evening load, no trigger.

## Technical details

- `scripts/stock_splits.py fetch DIR` (Yahoo's splits and the full-text search, saved under
  `DIR`) and `seed DIR`.
- `flows.py`: `SPLITS_FLOW`; `study.py`: the two kinds.
