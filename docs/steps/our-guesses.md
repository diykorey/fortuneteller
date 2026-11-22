# Our guesses

> Step 49 of the [Roadmap](../roadmap.md), on [Fortuneteller predicts](predicts.md), beside
> [stated forecasts](stated-forecasts.md). Terms are in the [Glossary](../glossary.md):
> *stated forecast*, *Subscription LLM*, *our guess* (not a *guess*, a person's call). Asked for 2026-11-22 by the owner: "state without any
> if then … we guess based on past", then "we can forecast without past if we want and think it
> makes sense", option A of the choice put to them: guesses labelled apart from what was tested,
> with their own tally (the others: one list with one tally; or no guesses for now).

## The goal

**In plain words:** besides the forecasts tested on history, the page gives the fortune
teller's own guesses about the coming week or month, each with its reason in one line, such as
*Oil will fall over the next week: OPEC+ meets on Sunday and its members have been pumping above
their quotas.* Each guess is saved before its span starts, never changed, and scored when the
span ends; the page shows how many came true, apart from the tested forecasts' tally.

At the end the page states no *if*: up to three tested forecasts, then up to two guesses, five at
most; and `docs/predicts/our-guesses.csv` holds every guess with its grade. This amends the
[Legend](../legend.md) (*never a model's opinion*, *what has no past is never shown beside a
record*) and CLAUDE.md (*never before it*) with the owner's exception, dated 2026-11-22.

## The way to reach it

- **The obstacle is that a guess has no record.** The reset (CLAUDE.md) answered confident output
  from placeholder values. A guess is allowed here only because it says what it is: each card is
  headed *Our guess*, gives its reason, is kept before its span starts and is graded in public.
  The page never mixes the two tallies.
- **Who guesses:** the Subscription LLM, run by the evening job in a fresh session with web search
  and nothing else. It is given the evening's date, the markets it may guess on, and the spans; it
  reads that day's news itself. It returns at most two guesses as JSON: market, span, direction,
  reason. Its model name is kept in each row.
- **What is kept:** only the first two guesses of an answer, each naming by its exact code one
  of the markets the tested forecasts measure daily (`SPY / ES`, `COMP`, `GC / XAU`, `BRN`, `DXY`,
  `UST10Y / ZN`, `BTC`; home prices come out monthly and two months late, so a week or a month
  cannot be graded), a week or a month, *up* or *down*, and a reason of at most 30 words (split
  on spaces) with no `%`. A guess is kept only when no guess of the same market, or of its twin,
  and span is still open: the S&P 500 and the Nasdaq count as one, since they move together and
  two guesses on them would be one bet counted twice. Anything else is dropped and why printed;
  an answer with no JSON list keeps nothing.
- **When a span starts:** the weekday after the evening it is written; a week ends 5 weekdays
  later and a month 21, holidays not known. It is graded, as the tested forecasts are, from the
  close before its first day to the close of its last: *came true* if that move is in its
  direction, *did not* otherwise, an unchanged close included.
- **The page:** first the tested forecasts (one per market at its shortest holding span, three at
  most), then the open guesses, the one ending soonest first, five cards at most; two tallies
  under the headline. The *if* cards go: the owner asked for no *if* (2026-11-22), and step 47
  is amended with that date: its bar of one to five cards becomes none to five, and a page with
  none says *Nothing passed our tests today*.
- **A guess may come before news.** The owner allowed it (2026-11-22): a guess may anticipate an
  event (*OPEC+ meets on Sunday*), as no tested forecast may. That is what heading it *Our guess*
  and scoring it apart are for.

## The rule, fixed before measuring

- **No bar decides what is shown:** a guess is shown because it was made, labelled as a guess.
- **The test of the guesses, once 30 are graded:** better than a coin if one-sided binomial p
  is below 0.01, which at 30 is 22 right or more. Beside it, with no verdict, the count *always
  up* would have had right on the same rows, so a model that only says *up* in a rising market
  is seen for what it is.
- **Expected outcome:** no better than a coin at 30 graded: 10 to 20 right.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `fortuneteller guess`: runs the Subscription LLM, checks each guess and appends what passes to `our-guesses.csv`; `scripts/release-day.sh` runs it before each `scoreboard` | Tests (the model stubbed): a guess on a market not listed, a quarter, a `%` or a 31-word reason is dropped; a second guess of an open market and span, or of the Nasdaq while the S&P 500's is open, is not kept; a third guess is not read; a failed or malformed run keeps nothing and ends with 0. The script's two `scoreboard` lines are each preceded by `guess` |
| 2 | The page: tested forecasts, then guesses headed *Our guess*, two tallies, no *if* cards | A rendered test shows two tested forecasts and two guesses in that order, a passed one dropped, five at most, and no arrow of an *if* |
| 3 | Grading | A test grades a guess from the close before its first day, not its first day's close, and leaves an open one ungraded |
| 4 | Published | The first guesses are on the live page; their rows and the date are written in Results. The test at 30 graded is a later step of its own, not this one |

## How you know it is right

- **A guess cannot be rewritten:** a test runs `guess` twice on the same evening and finds the
  first row unchanged and no second row for the same market and span.
- **A guess cannot peek:** its first day is after the evening it is kept; a test checks it.
- **The tallies stay apart:** the guesses are kept in their own file and tallied from it only.
- **The right closes:** a test where the close before the first day and the first day's close
  give opposite grades finds the first.
- **A silent model is seen:** `guess` prints *0 kept* and why each was dropped in the evening
  log; the page's guess tally stops growing, which anyone can see.

## What this step does not do

No guess on a market outside the list, no span but a week or a month, no size of move, no
percentage. A guess never counts toward a tested forecast's record, nor the other way round.

## Technical details

- **The run:** `claude -p` with `--allowedTools WebSearch`, `--model claude-opus-5-5` (kept in
  each row), output as
  JSON, a time limit of 10 minutes; the prompt is `src/fortuneteller/guess_prompt.txt`.
- **The file:** `docs/predicts/our-guesses.csv`, columns `stated, market, span, direction, first, last,
  reason, model, grade`.
- **Docs:** this spec, step 47's and step 48's amendments, the glossary (*our guess*, *Subscription
  LLM* amended), the Legend's and CLAUDE.md's amendments, and a decisions entry (a guess with no record, labelled, is allowed), status, the changelog and
  roadmap row 49.
