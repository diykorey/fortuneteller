# Guesses against the base rate

> Step 55 of the [Roadmap](../roadmap.md), on [the guess ledger](guess-ledger.md). Terms are in
> the [Glossary](../glossary.md): *our guess*, *base rate*, *Subscription LLM*, *news guesser*,
> *grounded guesser*, *excess*. Asked for 2026-11-23 by the owner: guesses must come true "more
> often than the base rate, we should refine rules that would do it"; of three ways put to them
> (score only; give the guesser the record; the same with today's guesser kept beside it as the
> control), the owner chose the third.

## The goal

**In plain words:** a guess that the S&P 500 rises over seven months comes true most of the time
whatever the news says, so a count of guesses that came true says nothing about skill. From this
step each guess carries its *base rate*, the share of its market's past spans of the same length
that went its way, and the record is judged by how far the guesses beat it. Two guessers run each
evening on the same markets: the *news guesser*, today's, unchanged, and the *grounded guesser*,
which is also given the base rates and the forecasts that hold and must say why its guess should
beat its base rate. The grounded guesser's prompt is refined one numbered change at a time; the
news guesser, the control, shows what the same evenings gave without the record.

At the end, every row of `docs/predicts/our-guesses.csv` has its guesser, base rate and prompt
version; the stats page and `fortuneteller excess` show each guesser's *excess*; this spec's
Results say on 2027-01-31 whether the news guesser beats its base rates, and on 2027-04-30 whether
the grounded guesser's frozen prompt beats the news guesser.

## The way to reach it

- **The obstacle: a count of right guesses mixes skill with drift.** Markets drift: the S&P 500
  rose in most past years, so *up* guesses come true often by habit, and a guesser given base
  rates may simply guess *up* more. The *excess* answers that: right guesses minus the sum of their
  base rates, over the guesses graded. A guesser that only follows the drift scores near zero.
- **The obstacle: the same market moves decide many guesses at once.** Steps
  [41](expert-hypotheses.md) to [43](filing-severity.md) could test on past years; a guesser that
  knows those years cannot. So both guessers are tested only forward, side by side: on the same
  evenings the same market moves hit both, and the difference between them is mostly the
  prompt's. Run one after the other, a calm month against a falling one would decide it.
- **The obstacle: refining on the evenings that judge it.** A prompt changed until it wins has
  been fitted to those evenings. So refining runs to the gate, 2027-01-31, and its record there is
  reported, not a verdict; the prompt is then frozen, and only evenings after the freeze decide
  whether it beats the news guesser, read on 2027-04-30.
- **The base rate:** a guess ending *n* weekdays after its first day (counted when it is kept, the
  first day and the end date included, holidays not known, as the ledger's horizon counts) is set
  against every run in its market's stored closes before the evening from one close to the close
  *n* later, overlapping; the base rate is the share whose move went the guess's way (an
  unchanged close counts against it, as in the grade). Kept with the guess, never changed. A
  holiday inside the span makes the grade one close shorter than *n*; accepted.
- **The grounded guesser** is the news guesser's prompt plus: each market's base rate *up* over
  5, 21, 63 and 252 closes; the rows of `docs/predicts/forecasts.csv` still open; and one rule:
  the reasoning names the guess's base rate and why the news should beat it. Up to 50 guesses an
  evening, as the news guesser; its open guesses, repetition check and lessons
  (`docs/predicts/grounded-lessons.md`) are its own.
- **Refining, one change at a time:** the agent proposes each change from the grounded reviews
  and lessons, the owner approves it, and it becomes a numbered version on the first line of
  `src/fortuneteller/grounded_prompt.txt`, kept in each row. One version is live at a time. Its
  monthly lessons also get each tag's right guesses against its *expected*, the sum of the tag's
  base rates.

## The rule, fixed before measuring

Counted: guesses graded by the reading's day, each guesser apart, once per market and ISO week of
the end date, the S&P 500 and the Nasdaq as one market (the first stated kept, by stated date then
row order); the rest set aside so one bet is not counted many times.

- **Beats its base rate:** excess above zero, at least 60 counted guesses, and the one-sided
  chance of that many right or more, if each came true at exactly its base rate (the sum of
  independent yes-or-no draws), below 0.01. The bar is strict because markets move together.
  Read on 2027-01-31 for the news guesser, a verdict; for the grounded guesser, reported only.
- **A prompt version is kept** when, over at least 15 evenings since it began whose week-horizon
  guesses of both guessers are all graded, the grounded guesser's excess per counted guess is
  higher than the news guesser's on more than half (ties dropped); otherwise the previous version
  returns. Changes stop on 2027-01-31; the version live then is frozen.
- **Grounded beats news:** on the evenings from 2027-02-01 on which both have graded guesses, the
  frozen grounded guesser's excess per guess (all that evening's graded guesses, not deduplicated)
  higher than the news guesser's, ties dropped, on enough of at least 30 evenings for a one-sided
  binomial p below 0.05. Read on 2027-04-30.
- **Too few:** a reading short of 60 guesses or 30 evenings says *too few*, with its counts, and
  is read again three months later under the same bars.
- **Expected outcome, written first:** neither guesser beats its base rate (excess within ±0.05 a
  guess); the grounded guesser guesses with the drift more often and its share right rises, but
  its excess does not; grounded does not beat news.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The base rate on every row | Tests: closes up on 3 of 4 runs of *n* gives 0.75 for *up* and 0.25 for *down*; an unchanged run counts against both; *n* = 1 gives the share of up days; a close on or after the evening changes nothing. Stored guesses get theirs from the history before their evening |
| 2 | The grounded guesser | Tests (the model stubbed): `guess` asks both; the grounded prompt holds the base-rate table, the open forecasts and the rule's sentence, the news prompt none of them and equal to the one built before this step; each row names its guesser and version; a grounded guess repeating an open news guess is kept, one repeating an open grounded guess refused; a failed grounded call keeps the news guesses |
| 3 | `fortuneteller excess`, the stats page and the lessons | Tests: the once-per-market-and-week count with the twins as one; each guesser's excess and the chance; a version's evenings against the news guesser; the grounded lessons given each tag's right against expected |
| 4 | Readings on 2027-01-31 and 2027-04-30 | Each verdict against the rule above, numbers from `fortuneteller excess` |

## How you know it is right

- A hand check: the base rates of the first three stored grounded guesses counted from the
  closes in a spreadsheet, with *n* counted on a calendar, match.
- An *up* guess on every market, every Monday from 2010, over 5 and 21 weekdays, scored on the
  stored closes with base rates from before each Monday: excess within ±0.02 a guess. A
  `base_rate` off by one close would still pass this, so test 1's *n* = 1 case pins it.
- The news guesser is unchanged: `guess_prompt.txt`'s diff is empty and test 2 compares its built
  prompt with the one before this step.

## What this step does not do

The front page keeps the news guesser's guesses until the grounded one beats it by the rule. No
backtest on past years. No new markets or spans. No news read into event kinds (step 20, parked).

## Technical details

- `study.base_rate(closes, before, n, direction)`; `GUESS_FIELDS` adds `guesser`, `prompt` and
  `base_rate`; rows before this step are `news`, prompt `news-1`.
- `src/fortuneteller/grounded_prompt.txt`, version on its first line; its table from
  `study.base_rate` per market for 5, 21, 63 and 252 closes.
- `fortuneteller excess` prints each guesser's counted guesses, right, expected, excess and
  chance, and each version's evenings against the news guesser.
- Docs: this spec, the glossary, the ledger's columns in [the guess ledger](guess-ledger.md),
  status, the changelog.
