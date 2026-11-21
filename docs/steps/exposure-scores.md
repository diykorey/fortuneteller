# Who a macro event hits: exposure scores

> Step 42 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-21 by the owner ([why](../decisions.md#2026-11-21-scores-read-from-filings-tested-against-moves-by-the-owner)).
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** [step 40](news-moves.md) found that most big moves of S&P 500 members come
with no filing of the company's own, and that those with a cause found were mostly news of their
industry or of the whole economy. `follows` can say what an OPEC+ cut does to Brent or a hot CPI
to the 10-year yield, but not which companies such news hits. This step has the Subscription LLM
read each member's own description of its business and score how it stands to gain or lose from
three things the record measures (oil, interest rates, consumer spending), then tests whether the
scores sort the members' moves on those events.

At the end: a frozen file of scores, one row per member and rubric, and for each rubric and each
kind of event it names, whether the high scorers beat the low scorers in the stated direction,
judged against the rule below written first.

## The way to reach it

- **Where the pattern comes from:** Andrej Karpathy's [US job market
  visualizer](https://karpathy.ai/jobs/) ([code](https://github.com/karpathy/jobs)) scrapes the
  BLS's 342 occupation pages, has a model score each against a rubric with anchored bands (0 to 10,
  "how much will AI reshape this occupation", each band named by examples) into a JSON line with a
  rationale, and draws the scores as a treemap. It says of itself "rough LLM estimates, not
  rigorous predictions": one score each, no second reading, nothing tested against what happened.
  This step takes the pattern (free text, an anchored rubric, a score and a reason) and adds what
  it lacks: the model blind to prices and to anything after the text, a second reading, and every
  score tested against the moves by the project's bars. No code or data of it is used.
- **The members:** the S&P 500's on 2020-01-02 by `data/seed/sp500.csv` ([step 36](earnings-sp500.md)),
  one per filer (of two share classes, the first ticker by name, as step 40), with closes in the
  store and a 10-K on EDGAR filed in 2019; others counted, left
  out.
- **The text:** each member's last 10-K filed before 2020-01-01, its *Item 1. Business*, the first
  12,000 characters, with the company's name and tickers replaced by "the company". Fetched from
  EDGAR by `scripts/tenk_business.py` (saved, one request a second, step 36's User-Agent), into
  `data/cache/tenk/`. The model is told the year is 2019; it still knows the companies, which is
  said in the Results' reach.
- **The rubrics,** each signed from −5 to +5, written in `docs/steps/exposure-brief.md` with its
  anchors before any text is read:
  - **Oil:** how a 20% rise in crude, by itself, moves the company's profits. +5 an oil producer;
    −5 an airline; 0 a software company.
  - **Rates:** how a one-point rise in US interest rates moves them. +5 a bank living on its
    lending margin; −5 a homebuilder or a utility; 0 a company with no debt and no lending.
  - **Consumer:** how a 5% rise in US consumer spending moves them. +5 a retailer of discretionary
    goods; 0 a defence contractor; −5 none expected (a dollar store at most −1).
- **The scorer:** the Subscription LLM ([step 41](expert-hypotheses.md); a hosted model through
  the owner's subscription, allowed as an input by the [decision of
  2026-11-21](../decisions.md#2026-11-21-a-model-proposes-the-records-decide-by-the-owner)), in fresh sessions of 25 members each, given only the brief
  and those members' texts; each text under an id that says nothing of the company (`M001` …, the key kept in the cache); it writes `id,rubric,score,reason` rows to
  `docs/steps/exposure-scores.csv`. The file is committed, and its SHA-256 posted in the pull
  request, before any test exists. Its model name is recorded.
- **The second reading:** 50 members, rows *n*, 2*n*, … 50*n* of the file by ticker order (*n* the
  members ÷ 50, rounded down), scored again by a fresh session given the same brief and texts.
- **The events and the test,** from 2020-01-01: per rubric, the kinds it names, each with the sign
  the rubric implies: oil, `opec` *oil up* (+) and *oil down* (−); rates, `cpi` *above* (+) and
  *below* (−), `fomc` *hike* (+) and *cut* (−); consumer, `retail` *above* (+) and *below* (−).
  For each event, the **spread** is the mean excess day move (against the S&P 500, as
  `study.excess_spans` gives it, from the close before) of the members scoring +3 or more less
  that of those scoring −3 or less (for consumer, +3 or more against 0 or less). An event is
  *right* when the spread has the kind's sign. Also the week, from the close before. Each flow's
  events are taken whole, as `follows` takes them: an event sharing its day with another flow's is
  counted in both.
- **The sector baseline:** the same test with each member's score replaced by the mean score of the
  *other* members of its SIC major group (the first two digits of the `sic` in its SEC
  submissions file, step 36's cache); a member alone in its group is left out of both the
  baseline and its comparison, counted. It says whether a company's own
  score sorts better than its industry's.
- `scripts/exposure_check.py` prints, per rubric, kind and span: the events, right, the base, the
  chance, the placebo, the walk-forward, and the same for the sector baseline.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: step 40's matrix (8-K items against big moves) and sample; step
41's results; no score, no 10-K text and no spread of this step. Amended the same day after the
goldfish, before any text was fetched: the walk-forward, the base's spans, the sector baseline
left one out, the chance lines, the second reader's bar, the forward log, and the checks below.
Amended the same day: before any text was fetched, the texts given under ids that say nothing
of the company; before any score was read, the second reading run as two sessions of 25, as the
scoring was.*

- **A cell answers** when it has at least 10 events, and its right count beats the base at
  p < 0.01 (one-sided binomial). The base is the share of the 504 spans starting at each of the
  504 closes before 2020 (a day or a week each, overlapping for the week), with the members and
  scores fixed as above, whose spread had the kind's sign. A cell `follows`' placebo (the events
  shifted, as [what follows](what-follows.md) shifts them) also answers is *the period*.
- **A cell holds** by the bar of every link: 60% right of at least 30 graded walk-forward, 10
  points over the base, p < 0.01, each event from 2020 predicted by the answer the cell gives on
  the events from 2020 before it (graded only once that answer is the kind's sign).
- **The score adds** over its sector when the cell is right on more events than the sector
  baseline's same cell, by a sign test on the events where they differ, p < 0.05.
- **The chance lines:** for answers, 0.01 times the 16 cells (8 kinds, 2 spans), 0.16; for
  *adds*, 0.05 times 16, 0.8. Counts at or under a line plus two are read as chance. The sector
  baseline's cells are reported, not counted.
- **The second reading agrees** when, per rubric, the two readings' scores are within 2 points on
  at least 80% of the 50; one rubric short of it stops step 2 for the owner's call (to amend the
  rubric, or end the step). More than 5 reasons the second reader marks as naming an event after
  2019 also stop it.
- **Expected outcome:**
  - At least 450 members scored.
  - Oil answers on both OPEC kinds on the day, and holds on neither (under 30 events).
  - Rates answers on CPI *above* on the day; FOMC *hike* and *cut* are *too few* or *can't say*
    (as `follows` prints them: under 10 events, or not an answer).
  - Consumer answers on no kind.
  - The score adds over its sector in at most 2 cells, within chance: most of a company's
    exposure is its industry's.
  - Answers beyond these at most the chance line plus two.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- **The text is blind:** a test on the cache finds each text's filing date before 2020-01-01 and
  none of the company's names or tickers in it.
- **The scores are frozen:** the SHA-256 in the pull request equals the one the tester prints.
- **The tester is right:** a test on hand-made closes and scores (a spread's sign, the group cut,
  the base, the leave-one-out mean); and two events by hand from the store (the first OPEC *oil
  up* and the first CPI *above* from 2020): the members in each group, their excess moves, the
  spread, equal to the tester's.
- **The model's memory:** it knows 2020 to 2026 and may score what happened, not what the text
  says, in words no reader can catch. No check here can rule it out, so the test from 2020 is
  read as what the scores sort, not as a forecast; only the forward log (step 5), on events after
  the scores were frozen, is free of it.
- **The model saw no more:** the second reader also marks any reason naming an event after 2019,
  within the bar above.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The texts and the brief | The brief committed before the first fetch; `tenk_business.py` and its test; texts for the members in the cache, the blind test passing, the counts left out in `docs/steps/exposure-scores-results.txt` |
| 2 | The scores | `exposure-scores.csv` committed and its hash posted; the second reading's agreement per rubric and the marked reasons in the results file, within their bars |
| 3 | The tester | `exposure_check.py` and its test; the two hand checks in the results file, equal to the tester's; `just check` passes |
| 4 | Results | Every cell judged against the rule; goldfish-reviewed, each finding fixed or answered in the pull request; roadmap, status, changelog updated |
| 5 | Forward | Each new OPEC+, CPI, Fed and retail event after the scores' commit, its spread per rubric written to `docs/steps/exposure-forward.csv` and graded, to the 2027-01-31 gate; recorded, no bar of its own |

## What this step does not do

- **No answer from the model:** a score is an input; only a cell that answers reaches the page,
  with its counts, as every answer.
- No new flow, no live call, no page: the treemap (members sized by value, coloured by what
  followed an event) waits for a cell that answers. No API: the Subscription LLM, by hand.
- 8-K filings scored for good or bad news are step 43, by the same pattern, after this one.

## Technical details

- `scripts/tenk_business.py`: the 10-K's primary document from each member's submissions JSON
  (step 36's cache), its text from *Item 1* to *Item 1A* or *Item 2*, names replaced.
- `scripts/exposure_check.py`: closes and excess moves by `study.excess_spans`; events and kinds by
  `follows_kinds` (step 41); tests in `tests/test_exposure.py`.

## Results

*Measured 2026-11-21; the evidence, every command and its output, in
[exposure-scores-results.txt](exposure-scores-results.txt).*

**In plain words:** the Subscription LLM scored 426 S&P 500 members from their 2019 business
sections, and a second reading agreed on all 50 it reread. Tested on events from 2020, two of 16
cells answer, both on the 18 OPEC+ days when Brent fell: the oil scorers (producers and oilfield
services) trailed the low scorers (airlines, cruise lines, FedEx), 15 of 18 on the day and over
the week. Two answers of 16 cells is within the chance line plus two, so by the rule they are read
as chance. They are also near the kind: the OPEC kind *is* Brent's own move that day, so they say
oil-exposed shares follow oil, not what OPEC+ news does. The industries alone sort the day as well
(the sector baseline answers, 15 of 18); over the week it is 15 of 18 too, short of an answer. On
the days Brent rose, 17 of 28, not an answer. Rates sorted nothing: on a hot CPI, banks beat
utilities and homebuilders on 15 of 28 days, no more often than on any day before 2020 (0.486).
Consumer spending sorted nothing on retail sales. Nothing holds walk-forward, and in no cell did a
company's own score beat its industry's. The scores, read from text, find no more than the
industry does.

| Expected (written before) | Found |
| --- | --- |
| At least 450 members scored | 426 of the 513 members of 2020-01-02, 425 with closes — **wrong**; left out: 60 not in the SEC's current listing, 4 second share classes, 9 with no 10-K filed in 2019, 14 with no Item 1 read |
| Oil answers on both OPEC kinds on the day | *oil down* answers, 15 of 18 against a base of 0.522, p 0.0064; *oil up* does not, 17 of 28 against 0.478, p 0.12 — **wrong** in half |
| Oil holds on neither | neither holds: on the day, 1 event graded walk-forward (0 right); on the week, none — right |
| Rates answers on CPI *above* on the day | no: 15 of 28 against 0.486, p 0.37 — **wrong** |
| FOMC *hike* and *cut* *too few* or *can't say* | *hike* 12 events, no answer (p 0.57); *cut* 8, under 10 — right |
| Consumer answers on no kind | none — right |
| The score adds over its sector in at most 2 cells | 0 (the smallest p 0.23) — right |
| Answers beyond these at most the chance line plus two (2.16) | 1: oil *oil down* on the week, 15 of 18 against 0.540, p 0.0096 — right. All answers, 2, are within the line plus two too: read as chance |
| Second reading within 2 points on 80% per rubric; at most 5 reasons marked | 100% on each (50 of 50); 0 marked — right |

- **The period:** neither answer is one the placebo also gives (the tester's *period* column).
- **The kind:** both answers are on *oil down*, whose kind is Brent's close on the reaction day
  below the close before ([step 24](opec.md)); that oil producers lag on a day oil fell
  is near what the kind says, as step 41's rules 23 and 26 were. No answer is a finding about
  OPEC+.
- **The sector:** 11 members alone in their SIC group are left out of it. It answers the same day
  cell (15 of 18 against 0.534, p 0.0084), and not the week (15 of 18 against 0.558, p 0.014); the
  sign test has no event in either where the two differ.
- **The columns:** *walk* is right of graded walk-forward; *period* `-` is no placebo answer.
- **The reach:** the members are 2020's, read from what they wrote in 2019, and the model knows
  2020 to 2026; no check here rules that out (above), so these counts say what the scores sort, not
  what they forecast. Only the forward log, on events after the scores' commit, is free of it.
- **The checks:** the tester prints the scores' SHA-256 posted in pull request #396; the first
  OPEC *oil up* (2020-04-13) and CPI *above* (2020-07-14) from 2020 recomputed from `daily_bars`
  by a one-off script (its text and command in the evidence), the same spreads the tester prints
  (+0.067771, −0.018410); the gate (`just check`'s steps) passes, 732 tests.
- **Step 5:** the forward log of every rubric's kinds after the scores' commit, to the 2027-01-31
  gate, in `docs/steps/exposure-forward.csv`.
