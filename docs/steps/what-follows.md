# What follows a Fed decision, over spans

> Step 17, part 1, of the [Roadmap](../roadmap.md#next-steps-in-order), chosen by the owner
> 2026-11-04 with the target amended ([Legend](../legend.md#the-target)). Terms are in the
> [Glossary](../glossary.md): *span*, *base rate*, *kind*, the four answers.

## The goal

**In plain words:** after the Fed cuts, holds or hikes, what did each market do over the next day,
week and month, and was that different from what it does over any day, week or month? For
example: "Fed cut → 5-year yield, next month: down after 27 of 40 cuts; all months: down 3,100 of
7,900" (an illustration, not a measurement).

Today a direction comes only from a surprise, and the Fed's surprise (its statement's sentiment,
step 14) calls nothing. A decision's *kind*, what was decided, is the one thing a news reader
knows the moment it lands. This part answers for that kind, and is the base steps 18–20 stand on.

At the end: `fortuneteller follows --event fomc` prints, for each kind, span and market, the
counts, the base rate, the answer on all history and its walk-forward record.

## The way to reach it

- **The kind, from the target rate.** The Fed's target rate (FRED, as `target_rates` reads it)
  three days after a decision against the day before: equal is a *hold*, lower a *cut*, higher a
  *hike*, as `is_hold` reads it today. On the store of 2026-11-04: 276 decisions, 184 holds, 52
  hikes, 40 cuts. Read when `follows` runs; nothing new is stored.
- **The spans:** a day, a week (5 closes) and a month (21 closes). An event's move runs from the
  last close before its first reaction day (`closing_price_before_after`) to the 1st, 5th or 21st
  close from that day, signed, in the market's unit (`release_move`). A window with a hole in the
  data (`MAX_CLOSE_GAP_DAYS`) is skipped.
- **Spans do not overlap.** A decision whose span would start before the previous decision's span
  ends, of any kind, is left out of that span, so no two counted spans share a close. Only the
  month loses any (unscheduled decisions in 2001, 2008 and 2020). The quarter and the year, where
  this would leave too little, are part 2.
- **Three outcomes, from the market's own spans.** The *base* is every span of that length that
  starts on a trading day from the kind's first reaction day on that market, events or not.
  *About the same* is a move smaller than the base's lower third of absolute moves; *up* and
  *down* are the rest by sign. So about a third of base spans are *about the same* by
  construction, and the base rate of each outcome is its share of base spans.
- **The answer.** For a kind, span and market with *n* counted events, each outcome's count *k*
  is tested against its base rate: the chance of *k* or more in *n* draws at that rate
  (`stats._binomial_chance`, summed). The answer is the outcome with the smallest chance if it is
  under 0.01; otherwise *can't say*; under 10 events (`MIN_EVENT_DAYS`) *too few*.
- **Walk-forward.** At each event, oldest first, the answer from the events before it, with the
  base and its thirds from spans ended before it; an *up*, *down* or *about the same* answer is
  graded on the event's own outcome. A kind, span and market **holds** with at least 30 graded
  answers (`MIN_PREDICTIONS`) and a chance under 0.01 of as many right, each answer at its own
  outcome's base rate (the sum of independent draws, computed exactly). *Can't say* is counted,
  never graded.
- **Chance, said.** 3 kinds × 3 spans × 16 markets is 144 cells with three outcomes tested each:
  at 0.01, about 4 answers on all history by chance alone. `follows` prints that line.

## The rule, fixed before anything is shown

- The kinds, spans, thirds, bars (0.01, 10 events, 30 graded answers) and markets above, unchanged
  by what the run shows.
- **Expected outcome, written first.** Cuts and hikes are too few to hold: with 40 and 52
  decisions, a walk-forward answer opens no earlier than the tenth, leaving at most 30 and 42 to
  grade, and fewer once the first answers are *can't say*. On all history, cuts lean yields down
  and gold up over the month (cuts cluster in 2001, 2008 and 2020); a few answers there, near
  chance's four. Holds (184) are the only kind that can hold; expected: none does, because a hold
  is priced in.
- Every existing output — `raw-move`, `surprise`, `predict`, `score`, the scoreboard — is
  unchanged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The kind, the spans, the base and its thirds, the answer and the walk-forward in `study.py`; `follows --event fomc` prints them | The tests below pass; the run on a copy of the store prints all 144 cells and the chance line |
| 2 | Results: the run on the store, recorded here and in [MVP results](../mvp-results.md), the expected outcome checked, the roadmap row | Each kind's holds, answers and *too few* recorded against the expected outcome |

## How you know it is right

- A decision with the target unchanged is a hold, lower a cut, higher a hike; one FRED has no rate
  for yet is left out.
- A month span starting before the previous decision's ends is left out of the month only.
- On made-up closes rising every day, every span's answer is *up*; on closes repeating a fixed
  cycle, the base thirds are the cycle's.
- A walk-forward answer never uses an event, or a base span, ending on or after the event it
  answers (checked by changing a later close and getting the same answer).
- Ten events at a rate of one half, all *up*: chance 0.001, answered; nine: *too few*.

## What this part does not do

No quarter or year (part 2), no ECB (the euro area, after the US), no other flow, no page, no
trigger file (step 18), no new market (step 19). Nothing is stored and nothing is called live.

## Technical details

- `study.py`: `SPANS = {"day": 1, "week": 5, "month": 21}`; `fed_kinds(events, rates)`;
  `span_moves(closes, unit, closes_n)` (signed, every start day); `span_answer(counts, base)`;
  `follow_forward(...)`. `weekly_moves` stays as it is.
- `stats.py`: the chance of at least *k* in *n* at a rate, and of at least *r* right with each try
  at its own rate.
- `__main__.py`: `follows --event fomc` (only `fomc` in this part), reading FRED with
  `FT_FRED_API_KEY`.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17, `docs/status.md`.
