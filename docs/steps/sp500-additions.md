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

- **The additions: Wikipedia's *Historical components of the S&P 500*,** its changes table at a
  fixed revision, each row an effective day, the company added and the one removed. Nobody here
  picks them; a row with no company added is skipped.
- **The announcement day,** since S&P announces days before a change takes effect: from the row's
  reference, the S&P press release's date in its address (`press.spglobal.com/YYYY-MM-DD-…` or
  `…/announcements/YYYYMMDD-…`), else the reference's `date=`; kept only if 0 to 40 days before
  the effective day. Five are checked by hand against S&P's release; one off by a day or more
  stops step 1.
- **The minute:** S&P announces after the close; the event is placed at 17:15 New York on that
  day and reacts on the next close. The five releases' times are read too; one before 16:00 is
  written in the evidence, two stop step 1.
- **The company's closes: Yahoo, under the ticker the row gives,** or the company's current one
  where it was renamed, written by hand beside it.
- **Left out, counted:** no announcement day; a company Yahoo has no closes for (bought or
  delisted since, so the kept ones are the survivors, written in the results); fewer than 504
  closes before (a new listing or a spin-off); a second addition of one company inside the first's
  span, as in step 20. Fewer than 100 kept stops step 1.
- **The flow:** `additions`, code 35, event type `Stock index inclusion` (a new row in
  `data/seed/event_types.csv`), a dated flow like the CEO one, the ticker in the detail, one kind
  (`added`), lesser. Seed `data/seed/sp500_additions.csv` (`day`, `time`, `ticker`,
  `effective`), written by `scripts/sp500_additions.py` from the saved revision. The companies'
  closes load each evening with the CEO flow's and the earnings' (`load-prices`).

## The rule, fixed before measuring

*Written 2026-11-20. Seen before: the table's row count (414, 392 with a company added) and that
256 have an announcement day 0 to 40 days before, 6 days the median; no price.*

- `follows`' bars, as every kind: an answer only at p < 0.01 against the company's own base; a
  link *holds* at 60% right of at least 30 graded walk-forward, 10 points over the base, p < 0.01;
  the placebo marks *the period*.
- **Expected outcome:** from the close before, the day *up*, holding walk-forward (the effect
  smaller than the 1990s' but there); the week *up*, not holding; the month *can't say*, the
  run-up given back after the effective day. From the reaction close, *can't say* on every span.
  Between 150 and 220 additions kept.

## How you know it is right

- Five additions by hand: the announcement day and time from S&P's release, the reaction close
  from Yahoo, and the excess day move against `follows`' own for that company, within 0.1 point.
- The kept count plus each left-out count equals the rows with a company added (392).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The script, the seed, the hand checks | `data/seed/sp500_additions.csv` with a seed test; the counts and the five checks in `docs/steps/sp500-additions-steps.txt` |
| 2 | The flow, `follows --event additions`, and its companies loaded nightly | `just check` passes; the closes loaded on a copy of the store |
| 3 | Results | `follows` and `raw-move` on a copy of the store, the Results section, goldfish-reviewed |

## What this step does not do

- No removals: most removed companies were bought or delisted, and have no closes.
- Not on the page's *Ask* yet: a later step, as step 32 was for earnings.
- No trigger and no live call: an addition is filed by hand as a step 18 trigger once it holds.

## Technical details

- `scripts/sp500_additions.py fetch DIR` saves the revision's wikitext; `seed DIR` writes the seed
  and prints the left-out counts.
- `flows.py`: `ADDITIONS_FLOW`, a `DatedShockFlow` as `CEO_FLOW`. `study.py`/`__main__.py`: the
  one kind passed to `follow_companies`, as the earnings' kinds are; `company_tickers()` reads
  the new seed.
- Docs: roadmap row 35, status, changelog, schema (`event_types`' new row), glossary (*index
  effect*, *effective day*).
