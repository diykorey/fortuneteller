# Hypotheses from an expert reader

> Step 41 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-21 by the owner ([why](../decisions.md#2026-11-21-a-model-proposes-the-records-decide-by-the-owner)).
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** `follows` answers one kind against one market: "a CEO leaves over conduct, the
shares fall on the day". Readers ask richer things: does it fall more when the shares were already
falling, does oil's rise after an OPEC+ cut reach the airlines a month on, does a miss weigh more
in a week of hot inflation. An economist and statistician reading every record could propose such
rules. This step has a language model play that expert: it reads the records up to 2019 and writes
a fixed set of testable rules; the code then tests each, once, on 2020 onward, by the bars every
answer meets. The model proposes; only the arithmetic answers.

At the end: a frozen file of the expert's rules, each tested on 2020 onward against the rule below
written first; the rules that pass logged as calls and graded forward as events land.

## The way to reach it

- **The pack the expert reads:** the records as they stood at 2019-12-31, and nothing after:
  every flow's events to that day (`data/seed/`, cut at the day), and `follows`, both runs, for
  every flow on a copy of the store whose events and closes end on 2019-12-31. Also this spec's
  rule language below and its bars. The pack is written to `docs/steps/expert-pack/` and frozen
  before the expert runs.
- **The expert:** a hosted language model through the owner's subscription, run by hand in one
  session, given only the pack and the brief in `docs/steps/expert-brief.md` (its role, the rule
  language, "use no knowledge of what happened after 2019"). It writes 40 rules, each with a line
  of reasoning, to `docs/steps/expert-hypotheses.csv`, committed before any test is run. Nothing
  is changed after. Later, a model called through an API may run the same brief (not this step).
- **The rule language,** so the code can test a rule as written. A rule is: a **kind** (one of
  `follows`' flows and its kinds, such as `earnings500` *below*); an optional **condition** from
  a menu: (a) a market's move over the 21 or 63 closes before the event, above or below a
  threshold in percent, the market being any in the store, or the event's own company; (b) an
  event of another kind within the 21 closes before; a **market** (any in the store, or the
  company); a **span** (day, week, month, from the close before); and a **direction** (*up* or
  *down*, against the market's base as `follows` measures it). A rule outside the language is
  counted *untestable*, not rewritten.
- **The test:** `scripts/expert_test.py` reads the rules and, on the full store, keeps each rule's
  events from 2020-01-01 that meet its condition, and answers them as `follows` does (the market's
  own base of the 504 closes before; a company against the S&P 500; the placebo). The same rule
  without its condition is answered too, on the same events' period.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: every `follows` cell of steps 1 to 40, measured on the full
history; no rule of the expert's, which does not exist yet.*

- **A rule passes** when, from 2020-01-01: at least 10 events meet it; its answer is its stated
  direction at p < 0.01, one-sided; the placebo does not give the same answer (not *the period*);
  and, for a rule with a condition, the same rule without it does not give the same answer at
  p < 0.01, or gives it at a smaller share of events in the direction (the condition adds
  something).
- **A rule holds** by the bar of every link: 60% right of at least 30 graded walk-forward from
  2020, 10 points over the base, p < 0.01.
- **The chance line:** 0.01 times the testable rules; passes at or under it plus two are read as
  chance.
- **Expected outcome:**
  - At least 30 of the 40 rules are testable as written.
  - Between 0 and 4 pass; at most 1 holds. Most rules with a condition have under 10 events
    from 2020.
  - Of those that pass, at most half are rules with a condition: an expert's rule restates more
    often than it adds.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- **The pack ends at 2019-12-31:** no event, close or cell in it after that day, checked by a test
  on the pack's files.
- **The rules are frozen:** the CSV's commit comes before the test script's first run, seen in
  the git log.
- **The tester is right:** a test on hand-made closes and events for each part of the language;
  and three rules recomputed by hand from the store (their events, the condition's move, the
  answer's counts).
- **The expert saw no more:** a second reader given only the brief and the rules marks any rule
  or reasoning naming an event after 2019; each such rule is counted and reported, and its test
  stands, flagged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The pack and the brief | `expert-pack/` and `expert-brief.md` committed, the pack's test passing |
| 2 | The expert's rules | 40 rules with reasoning in `expert-hypotheses.csv`, committed; the second reader's marks in `docs/steps/expert-hypotheses-results.txt` |
| 3 | The tester and its test | `just check` passes; the three hand checks in the results file |
| 4 | Results | Every rule's answer from 2020, each expected line judged; goldfish-reviewed; roadmap, status, changelog updated |
| 5 | Forward | Each passing rule a call in `data/calls.csv` on each new event that meets it, graded by `score`, to the 2027-01-31 gate |

## What this step does not do

- **The model forecasts nothing:** it writes rules; the page shows only rules that pass, with
  their counts, as every answer. Its reasoning may be shown beside a passing rule, labelled as
  reasoning, never as a record.
- **No hindsight claimed away:** the model was trained on years after 2019 and may know how they
  went; the test from 2020 guards against fitting our records, not against its memory. Only step
  5's forward grading is free of both.
- No new kind or market, no paid data, no model call through an API, no second round of rules in
  this step: a new round is a new step with a new pack.

## Technical details

- The pack: `follows` output as text, one file per flow and run; the seeds cut by date with the
  same columns.
- `scripts/expert_test.py` reuses `study.excess_spans`, `study.event_base` and `follows`' answer
  and placebo; the condition's moves come from `daily_bars`.
- Tests in `tests/test_expert_test.py`, as the seed scripts' tests.
