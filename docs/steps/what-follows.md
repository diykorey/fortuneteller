# What follows a Fed decision, over spans

> Step 17, part 1, of the [Roadmap](../roadmap.md#next-steps-in-order), chosen by the owner
> 2026-11-04 with the target amended ([Legend](../legend.md#the-target)). Terms are in the
> [Glossary](../glossary.md): *span*, *base rate*, *kind*, the four answers.

## The goal

**In plain words:** after the Fed cuts, holds or hikes, what did each market do over the next day,
week and month, and was that different from what it does over any day, week or month? For
example: "Fed cut → 5-year yield, next month: down after 25 of 34 cuts" (an illustration, not a
measurement).

Today a direction comes only from a surprise, and the Fed's (its statement's sentiment, step 14)
calls nothing. A decision's *kind*, what was decided, is what a news reader knows the moment it
lands. This part answers for that kind, and is the base steps 18–20 stand on.

At the end: `fortuneteller follows` prints, for each kind, span and market, the counts, the base
rates, the answer on all history, a placebo's answer and the walk-forward record.

## The way to reach it

- **The kind, from the target rate** (FRED, as `target_rates` reads it): the rate three days after
  the decision's New York day (`TARGET_EFFECT_DAYS`) against the day before; equal is a *hold*,
  lower a *cut*, higher a *hike*; either missing, left out. On the store of 2026-11-04: 276
  decisions, 184 holds, 52 hikes, 40 cuts. Read when `follows` runs; nothing is stored. Every
  decision is kept, shared days included.
- **A span of *c* closes** (a day 1, a week 5, a month 21) keyed on a close runs from the close
  before it to the *c*-th close from it, signed, in the market's unit (`release_move`); it is
  skipped if any two consecutive closes in it are more than `MAX_CLOSE_GAP_DAYS` apart, as
  `weekly_moves`. A decision's span is the one keyed on the close `closing_price_before_after`
  pairs with its `first_reaction_day` on that market, so a market's zone decides its day as in
  `raw-move`. Closes are not calendar days: bitcoin's week is five days.
- **No two counted spans overlap.** Per market and span, walking the decisions oldest first, a
  decision is left out if its close before is earlier than the end close of the last decision
  *kept*, whatever its kind; sharing that close is allowed. `follows` prints how many each cell
  left out, for overlap and for holes.
- **Three outcomes, from the market's own spans.** The *base* is every span of that length keyed
  on or after the kind's first counted reaction close on that market. Its cut is the lower third
  of absolute moves (`quantiles(..., n=3, method="inclusive")[0]`), one per kind, span and market;
  a move under the cut, or zero, is *about the same*, the rest *up* or *down* by sign. The base
  rates printed are the shares measured, not a third by assumption.
- **The answer, direction apart from size.** A market that only moves more on decision days must
  not read as a direction. So *about the same* is tested on all *n* events against its base rate,
  and *up* and *down* only on the *m* events that moved, against the share of up among the base
  spans that moved. Each chance is that of *k* or more at that rate (`stats.binomial_tail`). The
  answer is the outcome with the smallest chance if it is under 0.01 (`FOLLOW_P_BAR`) and no
  other ties it; else *can't say*; under 10 events (`MIN_EVENT_DAYS`), *too few*. An outcome whose
  rate is 0 or 1 is not tested.
- **A placebo, for the period.** Holds sit in the bull years 2009–15 and 2020–21, cuts in 2001,
  2008 and 2020: a kind can stand in for its years. Each counted decision's key close is moved 10
  closes earlier, and separately 10 later, skipping any that lands on a Fed reaction close, and
  the same rule answers. If either placebo gives the same answer under 0.01, the cell is printed
  as *the period*, not the decision.
- **Walk-forward, with nothing from the future.** At each counted decision, with its close
  before *b*: the earlier decisions are this cell's counted ones whose end close is on or before
  *b*; the base is the spans ending on or before *b*; the cut, the rates and every earlier outcome
  come from those. With under 10 earlier decisions it is not answered. An *up*, *down* or *about
  the same* answer is graded on the decision's own outcome under that same cut, at the answered
  outcome's base rate then. A cell **holds** (`HOLDS`) with at least 30 graded (`MIN_PREDICTIONS`,
  else `TOO_FEW`), right on at least 60% of them (`HIT_RATE_BAR`) and 10 points above their mean
  base rate, and a chance under 0.01 of as many right, each answer at its own rate
  (`stats.poisson_binomial_tail`, exact); else `DOESNT_HOLD`. *Can't say* is counted, never
  graded.
- **Chance, said.** The cells answered (not *too few*) × 3 outcomes × 0.01 on all history, and the
  cells with 30 graded × 0.01 walk-forward, each printed as a number. The chance treats decisions
  as independent; within a cut cycle or a run of holds they are not, so a hold is weaker than its
  chance says. Part 2 tests by cycle.

## The rule, fixed before anything is shown

- The kinds, spans, cut, bars (0.01, 10 events, 30 graded, 60% and 10 points), placebo and
  markets above, unchanged by what the run shows.
- **Expected outcome, written first.**
  - Arithmetic, not a finding: cuts cannot hold on the month (about 34 counted, at most 24
    graded), and on the day and week only if every one of 30 is answered.
  - Hikes (at most 42 graded): none holds.
  - Holds: none holds as the decision. An answer for stocks or VIX after holds, if any, is
    marked *the period* by the placebo.
  - On all history, a few answers, near the chance count; cuts lean yields down and gold up over
    the month, and are marked *the period*.
  - Left out: only the month, about six decisions in 2001, 2008 and 2020, perhaps one in 1994;
    2001-09-17 on US markets on every span, for the hole after 2001-09-11.
- Every existing output — `raw-move`, `surprise`, `predict`, `score`, the scoreboard — is
  unchanged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Kinds, spans, the base and its cut, the answer, the placebo and the walk-forward in `study.py`; `follows` prints them | The tests below pass; the run on a copy of the store prints all 144 cells and both chance lines |
| 2 | Results: the run on the store, recorded here and in [MVP results](../mvp-results.md), the expected outcome checked, the roadmap row | Each kind's holds, answers, *the period* and *too few* recorded against the expected outcome |

## How you know it is right

- The target unchanged is a hold, lower a cut, higher a hike; a rate missing either side is left
  out.
- A span with a five-day gap inside it is skipped; a decision's span is the base span keyed on its
  reaction close.
- Of three decisions where the second overlaps the first and the third only the second, the third
  is counted; one starting on the last kept span's end close is counted.
- On closes whose event spans swing twice as wide as the base, as often up as down, the answer is
  never *up* or *down*.
- On closes alternating ±1% daily, with a 3% rise over each of 12 decisions' month spans, the
  answer is *up*.
- `span_answer` with 10 *up* of 10, a same rate of 0.25 and up half of the base spans that moved:
  *up*, chance 0.5^10 ≈ 0.001; 9 events, *too few*; a chance of exactly 0.01, *can't say*.
- Changing every close after a decision's close before leaves its walk-forward answer, cut and
  rate unchanged.
- Decisions all inside one rising year, on closes flat elsewhere: the placebo answers too, and the
  cell reads *the period*.
- `poisson_binomial_tail` with every rate equal is `binomial_tail`.
- `follows` with FRED patched prints the header and a row; without a key it exits 1.

## What this part does not do

No quarter or year (part 2), no ECB (the euro area, after the US), no other flow, no page, no
trigger file (step 18), no new market (step 19). No `live` call and no row in `data/calls.csv`;
FRED is read, nothing is stored.

## Technical details

- `study.py`: `SPANS = {"day": 1, "week": 5, "month": 21}`; `FOLLOW_P_BAR = 0.01`;
  `fed_kinds(events, rates: Mapping[date, float]) -> dict[int, str]` by event id, `"cut"`,
  `"hold"`, `"hike"`, from `release_date`; `span_moves(closes, unit, c) -> dict[date, Span]`, key
  close → (close before, end close, signed move); `span_answer(counts, same_rate, up_share) ->
  tuple[str, float]`; `answer_before(...)`, the walk-forward answer at one decision;
  `follow_market(decisions, closes, unit, c)`, each kind's `Follow` on one market and span: counts,
  base, answer, placebo, walk-forward grade (`HOLDS`, `DOESNT_HOLD`, `TOO_FEW` reused);
  `follow_decisions(flow, rates)` over every market and span.
- `stats.py`: `binomial_tail(k, n, rate)`, summing `_binomial_chance`;
  `poisson_binomial_tail(right, rates)`, by dynamic programming over the tries.
- `__main__.py`: `follows --event fomc` (the one choice, the default), the key by `_fred_key`;
  FRED failing prints `follows: …` and exits 1, as `load-tone`; no decisions or closes, as
  `raw-move`. Output, rows by kind (cut, hold, hike), span, then `MVP_PRICE_SERIES` order:

  ```
  follows: 276 Fed decisions 1994-02-04 … 2026-10-28: 40 cuts, 184 holds, 52 hikes
  kind  span   market        n  up same down  out  base up/same/down  answer  chance  placebo  walk-forward
  cut   month  UST5Y / ZF   34  25    4    5    6   0.34/0.33/0.33     down    0.0004  -        24: 15 right, too few
  ```
  then `by chance: about N answers on all history, M holds walk-forward`.
- Tests: `tests/test_what_follows.py`, `tmp_db`, given/when/then.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17, `docs/status.md`,
  the glossary's four answers (*too few* under ten events).
