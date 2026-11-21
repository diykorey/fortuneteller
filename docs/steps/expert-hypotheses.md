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

- **The pack the expert reads,** in `docs/steps/expert-pack/`, frozen before the expert runs: the
  records as they stood at 2019-12-31, and nothing after. Every flow's events to that day
  (`events.csv`, the store copy's `event_instances` to that day: time, type, detail, actual,
  consensus, surprise); `follows` for every flow, both runs (from
  the close before, and with `--after-the-day` from the reaction close), on a copy of the store
  whose events and closes end on 2019-12-31; `kinds.txt`, every flow with its kinds and every
  market in the store with its unit; and this spec's rule language and bars.
- **The expert:** the *Subscription LLM*, the hosted language model of the owner's subscription,
  run by hand in one fresh session, given only the pack and the brief in
  `docs/steps/expert-brief.md` (its role, the rule language, "use no knowledge of what happened
  after 2019"). Its model name and the session's text are saved in the results file. It writes 40
  rules, each with a line of reasoning, to `docs/steps/expert-hypotheses.csv`. Nothing in it is
  changed after its commit. Later, a model called through an API may run the same brief (not this
  step).
- **The rule language,** the CSV's columns, so the code reads a rule as written: `id`; `flow` and
  `kind` (a flow and kind of `kinds.txt`, such as `earnings500`, *below*); `condition` (`none`,
  `move` or `event`); for `move`: `on` (a market of `kinds.txt`, or `company`), `closes` (21 or
  63), `side` (`above` or `below`) and `threshold` (in the market's unit: percent for a price, or
  for the company's own shares, raw; basis points for a yield or breakeven, as `kinds.txt` gives
  each); for `event`: `other_flow` and
  `other_kind` (any flow and kind but the rule's own); `market` (a market of `kinds.txt`, or
  `company`); `span` (`day`, `week`, `month`, from the close before); `direction` (`up` or `down`);
  `reasoning`. A row with a value outside these is *untestable*, counted, not rewritten.
- **When a condition is read:** at the close before the event's reaction close, never later. A
  `move` is the market's change over the `closes` closes ending at that close. An `event` is met
  when another event of that kind has its reaction close within the 21 closes ending at it.
- **The test:** `scripts/expert_test.py` reads the rules from the commit that added them (named in
  its output) and, on the full store, keeps each rule's events from 2020-01-01 that meet its
  condition, after `follows`' own rule for overlapping events. It answers them as `follows` does,
  on the base `follows` uses for that market (a company's 504 closes before, as [step
  31](earnings.md); a market's span base, as [what follows](what-follows.md)), with `follows`' placebo,
  which shifts the kept events' days (*amended 2026-11-21, before the tester existed:* first
  written with the condition read again at each shifted close; `follows`' placebo keeps the kept
  events and shifts them, and the test uses it as it is). It answers the same rule
  without its condition on all the kind's events from 2020. It does so by handing `follows`' own
  functions (`study.follow_decisions`, `study.follow_companies`) the kinds of the kept events
  only, so the base, the placebo and the walk-forward are `follows`' own, from 2020.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: every `follows` cell of steps 1 to 40, measured on the full
history; no rule of the expert's, which does not exist yet. Amended the same day after the
goldfish, before the pack was built: the rule language as columns, the condition read at the
close before, the condition's test, the walk-forward's history, a forward log in place of calls,
the second reader's band, and the checks below.*

- **A rule passes** when, from 2020-01-01: at least 10 events meet it; the `follows` answer on them
  is its stated direction (p < 0.01); it is not *the period*; and, for a rule with a condition,
  the condition adds: the share of its counted events in the stated direction is above the same
  share for the rule without the condition, at p < 0.05 (one-sided binomial, that share the rate).
- **A rule holds** by the bar of every link: 60% right of at least 30 graded walk-forward, 10
  points over the base, p < 0.01, each event from 2020 predicted from the rule's events before it
  from 2020. *Amended 2026-11-21, after the rules were frozen and before the tester existed:*
  first written with the events before 2020 in the history; `follows`' walk-forward starts at a
  cell's first event, so the test runs it on the events from 2020 alone, which makes a hold harder.
- **The chance line:** 0.01 times the testable rules; passes at or under it plus two are read as
  chance.
- **Expected outcome:**
  - At least 30 of the 40 rules are testable as written.
  - Between 0 and 4 pass; at most 1 holds.
  - More than half the rules with a condition have under 10 events from 2020.
  - Of the rules that pass, at most half have a condition.
  - The second reader marks at most 5 rules as naming an event after 2019.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- **The pack ends at 2019-12-31:** a test on the pack's files finds no date after it.
- **The rules are frozen:** the CSV's SHA-256 is written in the pull request when it is committed,
  before the tester exists; the tester prints the hash of the rules it read, and the results file
  shows the two equal.
- **The tester is right:** a test on hand-made closes and events for each part of the language,
  with a condition whose move would differ if read at the reaction close; and, by hand from the
  store, the first testable rule of each condition (`none`, `move`, `event`) in the CSV's order:
  its events, the condition's moves, the answer's counts.
- **The expert saw no more:** a second reader, a fresh session of the same model given only the
  brief and the rules, marks any rule or reasoning naming an event after 2019; each is counted and
  its test stands, flagged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The pack and the brief | `expert-pack/` and `expert-brief.md` committed, the pack's test passing |
| 2 | The expert's rules | 40 rules with reasoning in `expert-hypotheses.csv`, committed; the second reader's marks in `docs/steps/expert-hypotheses-results.txt` |
| 3 | The tester and its test | `just check` passes; the three hand checks in the results file |
| 4 | Results | Every rule's answer from 2020, each expected line judged; goldfish-reviewed; roadmap, status, changelog updated |
| 5 | Forward | Each new event that meets a passing rule written to `docs/steps/expert-forward.csv` before its reaction close and graded at its span's end, to the 2027-01-31 gate; recorded, with no bar of its own (forward counts are few by then). A rule that reaches the hold bar is a link, and its calls follow the Legend's rule |

## What this step does not do

- **The model forecasts nothing:** it writes rules; the page shows nothing from this step until a
  rule holds, then with its counts, as every answer. Its reasoning may be shown beside a passing rule, labelled as
  reasoning, never as a record.
- **No hindsight claimed away:** the model was trained on years after 2019 and may know how they
  went; the test from 2020 guards against fitting our records, not against its memory. Only step
  5's forward log is free of both.
- No new kind or market, no paid data, no model call through an API, no second round of rules in
  this step: a new round is a new step with a new pack.

## Technical details

- The pack: `follows` output as text, one file per flow and run, with the lines of COIN (listed
  2021, no close before 2020; its closes kept in the copy only because `follows` needs every
  market's) taken out; `events.csv` from the copy.
- `scripts/expert_test.py` reuses `study.excess_spans`, `study.event_base` and `follows`' answer
  and placebo; the condition's moves come from `daily_bars`.
- Tests in `tests/test_expert_test.py`, as the seed scripts' tests.

## Results

*Measured 2026-11-21 ([evidence](expert-hypotheses-results.txt), [the rules](expert-hypotheses.csv));
every rule's numbers from `scripts/expert_test.py 9a2f138` on a copy of the full store.*

**In plain words:** the expert wrote 40 rules from the record to 2019, all of them testable. Tested
once on 2020 onward, 5 pass and 1 holds, but every one of the 5 restates an answer the record
already gave, and two of them only restate how the kind is defined. None of the 14 rules with a
condition passed: in no case did the condition raise the share of events going the stated way
(the smallest chance of it, 0.077). The expert's richer rules, a miss after a run-up falling
harder, a hot CPI biting more when yields were climbing, found no support from 2020; half of them
had under 10 events to judge. What holds is what `follows` already said: an S&P 500 member's miss
is followed by its shares trailing the index on the day.

| | Expected | Found |
| --- | --- | --- |
| Testable as written | at least 30 of 40 | 40 — right |
| Pass | 0 to 4 | 5 (rules 11, 23, 25, 26, 33) — **wrong**; 23 and 26 are Brent on the day after an OPEC+ announcement, whose kind is Brent's own reaction-day move (`follows` marks that cell *near the kind, not a finding*), so they pass by definition; without them, 3 |
| Hold | at most 1 | 1, rule 33 (a member's miss, the day *down*, 1,084 right of 1,690) — right; it restates step 36's hold |
| Conditioned rules under 10 events from 2020 | more than half | 7 of 14, half — **wrong** by one |
| Passes with a condition | at most half | 0 of 5 — right |
| Second reader's marks | at most 5 | 6 (rules 13 to 18) — **wrong**; none of the six had 10 events, so none was judged |
| Passes against the chance line (0.40) plus two | | 5, over it; all restatements |

- **The passes:** 11, a CPI above the consensus and 5-year breakevens *up* on the day (20 of 28);
  25, an OPEC+ *oil up* and gasoline *up* (18 of 28); 23 and 26, Brent, by definition; 33, the
  miss. Only 33 has enough graded walk-forward to hold; the others are graded forward (step 5).
- **The conditions:** the four with hundreds of events (35 to 38, earnings after a run-up or a
  fall) answered *down* or *up* as stated, but at about the share the same reports give without
  the condition (a miss after a run-up, 176 of 277 down, 64%, against 1,135 of 1,768, 64%); 36
  and 38 were also *the period*.
- **The checks:** the rules' SHA-256 in pull request #395 equals the tester's; rules 1 and 10
  recomputed from the store, the same counts; the test passes; `follows`, every flow both runs,
  byte for byte the same on main's code and this branch's after `follows_cells` was split for the
  tester.
- **What it means:** on this record, an expert's story about conditions does not beat the plain
  kind; the expert's value here was choosing which plain cells to watch. The forward log keeps the
  four passes that do not hold, to the gate. A second round, if any, is a new step with a new pack,
  and its brief should bar the kind's own defining market.
