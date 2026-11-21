# Good or bad, read from the filing: 8-K severity

> Step 43 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-21 by the owner, after step 42 ([why](../decisions.md#2026-11-21-scores-read-from-filings-tested-against-moves-by-the-owner)).
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** [step 40](news-moves.md) found that some kinds of filing come with big moves
(restructuring costs, share sales, officer changes, other company news) but that their item codes
do not say which way: as many go up as down. This step has the Subscription LLM read each
filing's own text and score how good or bad it is for shareholders, then tests whether the sign of
that score says which way the company's shares moved against the index.

At the end: a frozen file of scores, one row per filing, and for bad and good scores, on the day
and over the week, whether the shares moved the way the score says, judged against the rule below
written first.

## The way to reach it

- **The pattern:** step 42's ([exposure scores](exposure-scores.md)): free text, an anchored
  rubric, a score and a reason, blind to prices and names; a second reading; every score tested.
- **The filings:** 8-Ks of the S&P 500's members while members (step 40's member-days and its
  windows, from after 16:00 New York on the close before to 16:00 on the day), filed from
  2020-01-01 to 2025-12-31, carrying item 2.05, 3.02, 5.02, 7.01 or 8.01 and not 2.02 (results,
  measured as earnings since [step 36](earnings-sp500.md)). One per member-day: the first filed.
  **The sample:** 400 of them drawn by `random.Random(43)` from the list sorted by day and ticker,
  every 2.05 and 3.02 member-day first (they are few), the rest from the others.
- **The text:** the filing's primary document from EDGAR (saved, one request a second, step 36's
  User-Agent), into `data/cache/eightk/`, the first 8,000 characters after the cover page (from the
  first *Item*), with the company's names and tickers replaced by "the company", as step 42's
  `blind`, and under an id (`F001` …) that says nothing of the company or the day.
- **The rubric** in `docs/steps/severity-brief.md`, written before any text is read: an integer
  from −5 to +5, how the news in the filing, by itself, moves the company's value for shareholders
  from what a reader expected before it. Anchors: −5 a going-concern doubt or a fraud found; −3 a
  large restructuring with job cuts and charges, or a chief executive leaving at once with no
  successor; 0 a routine filing (a director's term, a bylaw, a presentation's notice); +3 a large
  buyback or a contract won; +5 an agreed takeover at a premium.
- **The scorer:** the Subscription LLM, fresh sessions of 25 filings each given only the brief and
  their texts; rows `id,score,reason` to `docs/steps/severity-scores.csv`, committed and its SHA-256
  posted in the pull request before any test exists. The model name is recorded.
- **The second reading:** 50 filings, rows 8, 16, … 400, in two fresh sessions of 25.
- **The test:** for each scored filing, the member's excess move (against the S&P 500, as
  `study.excess_spans`) over the day span from the close before its window's day, and over the
  week. **Bad** is a score of −2 or less, expected *down*; **good** +2 or more, expected *up*; the
  rest not counted. A filing is *right* when its excess move has the expected sign.
- `scripts/severity_check.py` prints, per cell (bad, good; day, week): the filings, right, the
  base, the chance, the walk-forward; and the same per item code, reported only.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: step 40's matrix (each item's share of big moves and its share
up) and step 42's results; no 8-K text, no score and no move of this step.*

- **A cell answers** when it has at least 10 filings and its right count beats the base at
  p < 0.01 (one-sided binomial). The base is the share of all the sampled members' day (or week)
  excess spans over the 504 closes before 2020 with the expected sign.
- **A cell holds** by the bar of every link: 60% right of at least 30 graded walk-forward, 10
  points over the base, p < 0.01, each filing in day order predicted by the answer the cell gives
  on the filings before it.
- **The chance line:** 0.01 times the 4 cells, 0.04; counts at or under it plus two are chance.
  The per-item rows are reported, not counted.
- **The second reading agrees** when the two readings are within 2 points on at least 80% of the
  50, and gives the same side (bad, good or neither) on at least 70%; short of either stops step 2
  for the owner's call. Each second session then marks the first reading's reasons naming an
  event after the filing's own text; more than 5 stops it too.
- **Expected outcome:**
  - At least 380 filings scored (some texts not read).
  - Bad answers on the day; good does not (good news in an 8-K is often known before).
  - Bad does not hold on the day (fewer than 30 graded at 60%).
  - Neither answers on the week.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- **The text is blind:** a test on the cache finds none of the company's names or tickers in the
  texts the model sees.
- **The scores are frozen:** the SHA-256 in the pull request equals the one the tester prints.
- **The tester is right:** a test on hand-made closes and scores (the side cut, the base, a right
  count); and two filings by hand from `daily_bars` (the first bad and the first good by day): the
  close before, the reaction close, the excess move, equal to the tester's.
- **The model's memory:** it may know how a filing's news turned out, and the filings are public
  and dated by what they say. No check here rules that out, so the test from 2020 says what the
  scores sort, not what they forecast; only the forward log, on filings after the scores' commit,
  is free of it.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The texts and the brief | The brief committed before the first fetch; the sample and its texts by `scripts/eightk_text.py`, its test, the blind test passing, the counts left out in `docs/steps/severity-results.txt` |
| 2 | The scores | `severity-scores.csv` committed and its hash posted; the second reading and the marks in the results file, within their bars |
| 3 | The tester | `severity_check.py` and its test; the two hand checks in the results file equal to the tester's; the gate passes |
| 4 | Results | Every cell judged against the rule; goldfish-reviewed, each finding fixed or answered in the pull request; roadmap, status, changelog updated |
| 5 | Forward | Each member's 8-K of these items after the scores' commit, scored by the same brief before its reaction close and graded, to the 2027-01-31 gate, in `docs/steps/severity-forward.csv`; recorded, no bar of its own |

## What this step does not do

- **No answer from the model:** a score is an input; a flow of scored filings would be its own
  step, after a cell holds.
- No API, no live call, no page; the Subscription LLM, by hand.

## Technical details

- `scripts/eightk_text.py`: the member-days and windows by `news_moves.member_days` and
  `window_day`; each 8-K's items and primary document from the saved submissions files (step 36's
  cache); `tenk_business.plain` and `blind` for the text.
- `scripts/severity_check.py`: closes and excess moves by `study.excess_spans`; tests in
  `tests/test_severity.py`.
