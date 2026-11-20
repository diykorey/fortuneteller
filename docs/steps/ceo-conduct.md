# A CEO's conduct, no departure

> Step 38 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-20 by the owner; [step 20](ceo-scandals.md)'s part 1b. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** step 20 measured a CEO leaving over personal conduct: the company fell against
the S&P 500 on the day, 17 of 26. Most such news ends otherwise: the board reviews it and the CEO
stays (Nvidia's of 2026-11-08 is the case that raised it). A reader who brings "X's CEO is accused
of misconduct" should be told what followed such news when the CEO did not go.

At the end: `follows --event conduct` prints what followed against the rule below written first.

## The way to reach it

- **A list nobody picks: the SEC's full-text search.** Step 20 parked this kind until a free list
  nobody picks was found; a list from memory is picked by its moves. EDGAR's full-text search
  (8-Ks from 2001) for the company's own words about its CEO's conduct, three fixed queries:
  `"investigation" "personal conduct" "chief executive officer"`; `"special committee" "chief
  executive officer" "allegations"`; `"allegations" "against our chief executive officer"`. Hits
  kept when the filer was an S&P 500 member that day (`data/seed/sp500.csv`, [step 36](earnings-sp500.md)).
- **Read by the rule, by hand, as step 20's:** a hit is kept when the 8-K concerns the CEO's own
  personal conduct as step 20 codes it (a relationship, harassment or other personal misconduct; a
  misstated credential or expenses), and the CEO is still CEO 90 days after the first public
  word (no departure 8-K, Item 5.02, naming the CEO in that time, and not in step 20's seed). Fraud
  at the company, antitrust and product cases are left out, as there. Every hit's reading is
  listed with its reason in `docs/steps/ceo-conduct-coding.csv`.
- **The day is the first public word,** as step 20's: the earliest of the 8-K and the first report
  it or a cited source names, at its New York time, by step 20's time rule (the latest the word is
  known to be out; *unknown* reacts at the next close). The 8-K often follows the news.
- **The market, the base, the spans, the bars and the placebo: step 20's,** the company's excess
  move against the S&P 500 on its own base of the 504 closes before; the day, the week and the
  month, from the close before and from the reaction close. One kind, `conduct`.
- **The flow:** `conduct`, type code 38, event type `CEO conduct, no departure`, step 20's flow
  class with seed `data/seed/ceo_conduct.csv` (step 20's columns). Its companies' closes load with
  `load-prices --companies --seed`; not on the page's *Ask*.

## The rule, fixed before measuring

*Written 2026-11-20. Seen before, no price and no count kept: the three queries' hit totals (1,238,
194, and one that the search refused), and four hit names (Guess 2018, Best Buy 2012, Kroger 2025,
PDL 2007).*

- Step 20's bars: under 10 events *too few*; an answer at p < 0.01 against the company's own base;
  a link *holds* at 60% right of at least 30 graded walk-forward, 10 points over the base, p <
  0.01; an answer the placebo also gives is printed as *the period*, not counted.
- **Expected outcome:** between 10 and 40 kept. *Too few* or *can't say* on every span: a
  conduct with no departure is milder news than step 20's, whose day was *down* at 0.004 on 26.
  Nothing holds. If fewer than 10 are kept, the step ends there and says so.
- Every other flow's `follows`, both runs, byte for byte unchanged.

## How you know it is right

- Every kept row and every left-out hit in the coding file, with its reason; a second reading of
  ten hits picked by the file's row numbers (1, then every tenth) by a reviewer who sees only the
  rule, disagreeing on more than one stopping step 1 for the owner's call.
- Five kept rows' first public word checked against the cited source, and their excess day moves
  by hand against `study.excess_spans`, within 0.1 point.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The hits fetched (a script, saved), read by the rule, the seed | `ceo_conduct.csv` and the coding file with a seed test (members on the day, a source each, no row in step 20's seed); the second reading and the checks in `docs/steps/ceo-conduct-steps.txt` |
| 2 | The flow | Tests as step 37's; `just check` passes |
| 3 | Results | `follows` both runs on a copy of the store, every flow compared by `cmp`; each expected cell judged; goldfish-reviewed; roadmap, status, changelog, schema updated |

## What this step does not do

- No departures (step 20's), no fraud at the company, no news read live (step 20's part 2 is
  parked until the gate), no page, no trigger.
- A conduct the company never put in an 8-K is not in the list: the list is the companies' own
  words, and its reach is said in the Results.
