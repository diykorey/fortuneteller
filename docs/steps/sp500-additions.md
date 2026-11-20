# S&P 500 additions

> Step 35 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when S&P announces that a company joins the S&P 500, what does its share price
do against the index, over the day, the week and the month? The *index effect* is a known one,
said to have faded since the 1990s; a reader who sees "X to join the S&P 500" should be told what
followed past additions.

At the end: `follows --event additions` prints the record of one kind, *added*, measured as [step
20](ceo-scandals.md) measures a company against the S&P 500 (its excess move against its own base
of the 504 closes before), against the rule below written first.

## The way to reach it

- **The additions: Wikipedia's *Historical components of the S&P 500*,** its changes table at
  revision 1385951946 (2026-11-16), each row an effective day, the company added and the one
  removed. Nobody here picks them; a row with no company added is skipped.
- **The announcement day,** since S&P announces days before a change takes effect: from the row's
  references, the first that is S&P's own release (its address on `press.spglobal.com` or
  `spglobal.com/…/announcements/`, or its publisher S&P Global, S&P Dow Jones Indices or PR
  Newswire), the date in its address, else its `date=`. Kept only if 1 to 40 days before the
  effective day: S&P announces at least a session ahead, so a same-day date is an article about
  the effective day. A news article's date is never used, as it may be the day after. Where S&P
  first said a company would join without a day, and named the day in a later release (Tesla:
  2020-11-16, then 2020-12-11), the first is the announcement, written by hand in the script.
- **The minute:** S&P announces after the close; the event is placed at 17:15 New York and reacts
  on the next close. A release found to be earlier in the day is placed at its own minute.
- **Five checked by hand in step 1:** the seed's rows 1, 50, 100, 150 and its last, each against
  S&P's release, its day and time; one off by a day or more stops step 1 for the owner's call.
- **The company's closes: Yahoo, under the row's ticker** (`.` as `-`), loaded each evening with
  the CEO flow's and the earnings' companies (`load-prices`; a company that fails is printed and
  skipped, as now; about 190 more asks, a few minutes). A company whose Yahoo name is not the
  row's is *another company now* and left out: the script prints both names for each, and a
  mismatch is read by hand.
- **Left out, counted, each once:** no S&P release dated 1 to 40 days before; *another company
  now*; no closes on Yahoo (bought or delisted since, so the kept ones are survivors, written in
  the results); fewer than 504 closes before (a new listing or a spin-off); a second addition of
  one company inside the first's span of that length, the second left out, as in step 20. Fewer
  than 100 kept stops step 1 for the owner's call.
- **The flow:** `additions`, type code 35 (the first part of its events' ids), event type `Stock
  index inclusion` (a new row in `data/seed/event_types.csv`), one event per addition as the
  earnings' flow keeps one per report (several are announced on one day), the ticker and the kind
  `added` in the detail; lesser, as the CEO flow and the earnings are (`raw-move` judges its lone
  days). Seed `data/seed/sp500_additions.csv` (`day`, `time` in UTC, `ticker`, `kind`,
  `effective`), written by `scripts/sp500_additions.py` from the saved revision.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price: the revision's 414 rows, 392 with a company added;
194 with an S&P release 1 to 40 days ahead; Uber's (2023-12-01) and Palantir's (2024-09-06) days,
and Tesla's above.*

- `follows`' bars, as every kind ([what follows](what-follows.md)): under 10 events *too few*;
  an answer only at p < 0.01 against the company's own base; a link *holds* at 60% right of at
  least 30 graded walk-forward, 10 points over the base's share of that answer, p < 0.01; the
  placebo marks *the period* where events moved ten closes away give the same answer.
- **Expected outcome:** from the close before, the day *up*, holding walk-forward; the week *up*,
  not holding; the month *can't say*. From the reaction close, *can't say* on every span. Between
  120 and 180 additions kept. Every other flow's `follows` output unchanged.

## How you know it is right

- Step 1's five announcement days and times, as above.
- The kept count plus each left-out count equals the 392 rows with a company added.
- Step 3: the same five additions' excess day move from Yahoo's closes by hand (the company's
  move less the S&P 500's, close before to reaction close) against `follows`' within 0.1 point.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The script, the seed, the names, the five checks | `data/seed/sp500_additions.csv`; a seed test (every row's day 1 to 40 days before its effective day, kind `added`, tickers unique per day); the counts, the names and the five checks passing in `docs/steps/sp500-additions-steps.txt` |
| 2 | The flow, `follows --event additions`, the companies loaded each evening | Tests: the seed loads one event per row; `company_tickers()` includes the new seed's; `follows --event additions` prints three spans of one kind; every other flow's `follows` the same on a copy of the store; `just check` passes |
| 3 | Results | `follows`, `raw-move` and the five excess checks on a copy of the store, the Results section, goldfish-reviewed; roadmap row 35, status, changelog, schema, glossary updated |

## What this step does not do

- No removals: most removed companies were bought or delisted, and have no closes.
- Not on the page's *Ask* yet: a later step, as step 32 was for earnings.
- No trigger and no live call: an addition is filed by hand as a step 18 trigger once it holds.

## Technical details

- `scripts/sp500_additions.py fetch DIR` saves the revision's wikitext; `seed DIR` writes the seed
  and prints the left-out counts; `names DIR` prints each kept ticker's Yahoo name beside the row's.
- `flows.py`: `ADDITIONS_FLOW`, the earnings' flow class with this flow's names and seed.
  `__main__.py`: `follows` passes the one kind to `study.follow_companies`, as the earnings' kinds
  are; `company_tickers()` reads the new seed.
- Docs: roadmap row 35, status, changelog, schema (`event_types`' new row, the seed), glossary
  (*index effect*, *effective day*).
