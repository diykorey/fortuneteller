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
  splits (`events=split`: the *split day*, the first day the shares trade split, and the ratio).
  Asked for every one of the 820 tickers in `data/seed/sp500.csv` ([step 36](earnings-sp500.md)),
  kept from 2011 when the ratio is above 1 (a *forward split*; a reverse split is a different
  story, of a falling price). A ticker Yahoo has nothing for is counted: the kept lean towards
  survivors, as step 36's. *Amended 2026-11-20, before any split was counted or price read:*
  a split's ratio has both terms 20 or under once reduced, since Yahoo writes a spin-off's price
  adjustment as a split (Agilent's Keysight in 2014, 1398:1000).
- **The announcement: the first 8-K naming the ratio.** The SEC's full-text search (EDGAR's, which
  covers filings from 2001) asked, per split, for the company's 8-Ks with "stock split" in the 120
  days before the split day. The event is the first whose text names the split's own ratio
  ("10-for-1", "3-for-2"), at its acceptance minute, UTC, as the 8-K is the earnings' minute in
  [step 31](earnings.md). An earlier 8-K that names no ratio, or another ratio, is passed over; a
  split with none is *no 8-K* and left out. A split put to shareholders more than 120 days ahead is
  *no 8-K* too: dated by the vote's 8-K it would be read late.
  *Amended 2026-11-20 by the owner, after step 1's hand check found Fiserv's 2018 split
  announced five days before its 8-K, and Alphabet's and Tesla's of 2022 dated by the shareholder
  vote:* the 8-Ks of the 365 days before the split day are searched, and the event is the earliest
  public mention naming the ratio: the filing's minute, or the date of the press release attached
  (an exhibit 99's opening date) when that is earlier, at 20:00 New York, a time unknown as
  [step 20](ceo-scandals.md)'s. One row a filer and split (Alphabet's two share classes, one).
  *Amended again 2026-11-20 by the owner ("automate option 2"):* that still dated Fiserv's 2018
  split by its late 8-K (the press release never filed) and Tesla's by the vote (its first 8-K
  named no ratio). The script flags the splits whose 8-K is a vote's (Item 5.07), or reports an
  earlier day than its filing with no press release dated; those 24 are dated by hand from the
  first public news of the split, a ratio named or not (a press release, an earnings release or
  a preliminary proxy), each source in the evidence, and kept in the script's `BY_HAND`.
- **Members on the announcement's day,** by `sp500.csv`.
- **The kind: alone or with a report.** Many splits are announced in the earnings release (Nvidia's
  of 2024-05-22). A split whose 8-K carries Item 2.02 is *with a report*, the rest *alone*: two
  kinds, since a report's own move would otherwise be read as the split's.
- **Closes are split-adjusted:** Yahoo's closes, as every company flow's ([Precision](../precision.md),
  step 20), so a week or a month span that crosses the split day reads no fall from the split.
  The checks below test one such span.
- **The flow:** `splits`, type code 37, event type `Stock split`, a flow of step 31's class
  (`EarningsFlow`: one event a seed row, its kind in the row) with seed
  `data/seed/stock_splits.csv` (`day`, `time`, `ticker`, `ratio`, `split_day`, `kind`,
  `accession`). As step 36's: its events load each evening with every flow's (and the page's
  raw-move card takes them), its companies' closes do not, and it is not on the page's *Ask*;
  measured on a copy of the store, its closes by `load-prices --companies --seed`.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price and no count: Nvidia's four splits on Yahoo, and its
2024 announcement in an 8-K with Item 2.02.*

- `follows`' bars, as [step 36](earnings-sp500.md)'s, on its three spans, the day, the week and the
  month, each company against its own base of the 504 closes before: under 10 events *too few*; an
  answer at p < 0.01 (for *up* and *down*, against the base's share of up among its spans that
  moved); a link *holds* at 60% right of at least 30 graded walk-forward, 10 points over the base,
  p < 0.01; an answer the placebo also gives is printed as *the period*, not counted.
- **Expected outcome:** in the seed between 100 and 300 forward splits, *with a report* 30% to 70%
  of them, *no 8-K* at most 40% of the splits asked; `follows` keeping at least 70% of the seed.
  Outside any of these, step 1 stops for the owner's call. *Alone*: *up* on the day from the close
  before, not holding; the week and the month *can't say*. *With a report*: *can't say* on every
  span (the report's surprise, not the split, moves it, and the kind does not know the surprise).
  From the reaction close, every cell *can't say*. Answers beyond these at most the chance line
  plus two. Every other flow's `follows`, both runs, byte for byte unchanged.

## How you know it is right

- Five splits by hand, the seed's rows 1, a quarter, a half, three quarters and the last, against
  the company's own release: the ratio, the split day and the announcement's day. Any of the three
  wrong on any of the five stops step 1 for the owner's call.
- Every kept 8-K names the ratio, by construction; the 8-Ks passed over are counted by why (no
  ratio, another ratio) and the first ten listed.
- Five announcements' excess day moves by hand against `study.excess_spans`, the same rows, within
  0.1 point; and one week span that crosses its split day, the stored closes showing no fall of
  the ratio's size.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scripts/stock_splits.py`: the splits, the 8-Ks, the seed | `stock_splits.csv` with a seed test (ratios above 1, members on the announcement's day, the announcement 1 to 120 days before the split day, the two kinds, one row an accession); the counts and the checks above in `docs/steps/stock-splits-steps.txt` |
| 2 | The flow | Tests: one event a split, two kinds; `follows` prints them; its tickers not in `company_tickers()`; not on the page's *Ask*; `just check` passes |
| 3 | Results | `follows --event splits` and `--after-the-day` on a copy of the store; every flow's `follows` both runs compared by `cmp`; the five excess checks and the week span; each expected cell judged right or wrong in the Results section, goldfish-reviewed; roadmap, status, changelog, schema and glossary (*Forward split*, *Split day*, *Alone*, *With a report*) updated |

## What this step does not do

- No reverse splits, no splits before 2011 or outside the S&P 500, no move on the split day.
- Not on the page's *Ask*, no evening load of its closes, no trigger.

## Technical details

- `scripts/stock_splits.py fetch DIR` (Yahoo's splits and the full-text search, saved under
  `DIR`) and `seed DIR`.
- `flows.py`: `SPLITS_FLOW`; `study.py`: the two kinds.

## Results

*Measured 2026-11-20 on a copy of the store ([evidence](stock-splits-results.txt), [step 1's
evidence](stock-splits-steps.txt)). The table's numbers are printed by `follows --event splits`,
the reaction close's by `follows --event splits --after-the-day`.*

**In plain words:** when an S&P 500 company announced a stock split on its own, not in an earnings
release, its shares beat the index the next day 48 times and trailed it 11 of the 59 that moved
(81%), where the same companies' own days split about evenly (52% up of those that moved). That is
an answer, *up*, and replayed walk-forward it was right 33 times of 51 (65%): it **holds**, which
the rule did not expect. The week from the close before leans the same way, 39 up against 9, an
answer that does not hold (21 of 44). The month is *can't say*. Splits announced in an earnings
release are *can't say* on every span, as are all spans from the reaction close.

| | Expected | Found |
| --- | --- | --- |
| Alone, day | *up*, doesn't hold | *up*, 48/15/11 of 74, chance below 0.0001, placebo `-`; **holds**, 33 of 51 — **wrong** |
| Alone, week | *can't say* | *up*, 39/26/9, chance 0.0002, placebo `-`; doesn't hold, 21 of 44 — **wrong** |
| Alone, month | *can't say* | *can't say*, 0.41 — right |
| With a report, every span | *can't say* | *can't say*: the day 18/0/12 of 30, 0.25; the week 0.34; the month 0.15 — right |
| From the reaction close | every cell *can't say* | every cell *can't say* — right |
| Answers beyond these ≤ chance line + 2 | | one, the alone week (chance line 0.2) — right |
| Splits in the seed | 100 to 300 | 105 — right |
| With a report | 30% to 70% | 31 of 105, 29.5% — **wrong**; the owner chose to go on |
| *No 8-K* | at most 40% of those asked | 19 of 159, 12% — right |
| Kept by `follows` | at least 70% | 104 of 105 on the day (one hole) — right |
| Every other flow's `follows` | unchanged, both runs | 15 flows both runs `cmp` identical; `earnings500` not re-run (38 minutes a run) — right, but for that one |

- **Why it may hold, and what to doubt.** 74 splits, 51 graded: a hold near its bar on a small
  kind. The kept are survivors (168 tickers Yahoo no longer lists; a company that split and then
  failed is missing), and companies split after their shares have risen, so the day may carry the
  run-up. 21 of the 74 *alone* are dated by hand (step 1), 4 of them at 20:00 for a time not
  given: a morning release so placed is read a day late, which can only blur the day.
- **The five by hand:** rows 1, 26, 52, 78 and 105 equal `study.excess_spans` to 0.01 point.
- **The span across a split day:** no week crosses one (the shortest lead, Tractor Supply's, is
  15 days); its month does, and its stored closes show no fall of the 5-for-1's 80% across
  2024-12-20: the closes are split-adjusted.
- **By chance:** about 0.2 answers and 0.0 holds on all history; two answers and one hold found.
