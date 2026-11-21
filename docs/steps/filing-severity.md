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
  2020-01-01 to 2025-12-31, carrying item 2.05, 3.02, 5.02, 7.01 or 8.01, on a member-day with no
  8-K carrying 2.02 in its window (results, measured as earnings since
  [step 36](earnings-sp500.md)). One per member-day: the first filed.
  **The sample:** the list sorted by day and ticker; every member-day whose filing carries 2.05 or
  3.02 is taken (step 40 counted 260 and 470 over 2011 to 2025, so under 400 from 2020), and the
  rest of the 400 drawn by `random.Random(43).sample` from the others in that order. The 400 are
  then sorted by day and ticker and given ids `F001` to `F400` in that order.
- **The text:** from EDGAR (saved, one request a second, the SEC's fair-access User-Agent as step
  40's `scripts/sec_8k_times.py` sends it), into `data/cache/eightk/`: the primary document from
  its first item heading (*Item 2.05*, *Item 8.01* and so on, past the cover page), up to 4,000
  characters, then the first exhibit 99 named in the filing's index (the press release, where
  7.01 and 8.01 filings put the news), up to 4,000 more; the company's names and tickers replaced
  by "the company" by step 42's `blind`.
- **The rubric** in `docs/steps/severity-brief.md`, written before any text is read: an integer
  from −5 to +5, how the news in the filing, by itself, moves the company's value for shareholders,
  against what the filing itself says was planned or guided before, or against no news where it
  says nothing of that. Anchors: −5 a going-concern doubt or a fraud found; −3 a
  large restructuring with job cuts and charges, or a chief executive leaving at once with no
  successor; 0 a routine filing (a director's term, a bylaw, a presentation's notice); +3 a large
  buyback or a contract won; +5 an agreed takeover at a premium.
- **The scorer:** the Subscription LLM, fresh sessions of 25 filings each given only the brief and
  their texts; rows `id,score,reason` to `docs/steps/severity-scores.csv`, committed and its SHA-256
  posted in the pull request before any test exists. The model name is recorded.
- **The second reading:** 50 filings, ids `F008`, `F016`, … `F400`, in two fresh sessions of 25;
  after scoring, each is shown the first reading's reasons for its 25 and marks any naming an
  event after that filing's date.
- **The test:** for each scored filing, the member's excess move (against the S&P 500, as
  `study.excess_spans`) over the day span from the close before its window's day, and over the
  week. **The side cut:** *bad* is a score of −2 or less, expected *down*; *good* +2 or more,
  expected *up*; the rest not counted. A filing is *right* when its excess move has the expected
  sign.
- **The placebo:** each filing's move taken 10 closes before and 10 after instead (not on another
  sampled filing's day), as `follows` shifts its events; a cell the shifted filings also answer is
  *the period*.
- `scripts/severity_check.py` prints, per cell (bad, good; day, week): the filings, right, the
  base, the chance (the binomial p), the placebo, and the walk-forward (right of graded, and
  whether it holds); and the same per item code, reported only.

## The rule, fixed before measuring

*Written 2026-11-21, amended the same day after the goldfish, before any text was fetched (the
exhibit, the 2.02 exclusion by member-day, the placebo, the base and the walk-forward defined, the
sample's check). Seen before: step 40's matrix (each item's share of big moves and its share
up) and step 42's results; no 8-K text, no score and no move of this step.*

- **A cell answers** when it has at least 10 filings and its right count beats the base at
  p < 0.01 (one-sided binomial), and the placebo does not answer it too. The base is the share,
  pooled over every sampled member (once each) and every span of it starting at one of the 504
  index closes before 2020-01-01 that it has (overlapping for the week), with the expected sign.
- **A cell holds** by the bar of every link: 60% right of at least 30 graded walk-forward, 10
  points over the base, p < 0.01, each filing in day order graded only once the cell answers on the
  filings before it (from 2020), and then right when it moved the expected way.
- **The chance line:** 0.01 times the 4 cells, 0.04; a count of answers at or under it plus two
  (2.04) is read as chance, so one or two answers alone show nothing; only a hold, or answers
  confirmed forward, would. The per-item rows are reported, not counted.
- **The second reading agrees** when the two readings are within 2 points on at least 80% of the
  50, and gives the same side (bad, good or neither) on at least 70%; short of either stops step 2
  for the owner's call; more than 5 reasons marked (above) stops it too.
- **Expected outcome:**
  - At least 380 filings scored (some texts not read).
  - Of the 400, 80 to 160 bad, 40 to 120 good, the rest neither.
  - Bad answers on the day; good does not (good news in an 8-K is often known before). One answer
    is within chance (above).
  - Bad does not hold on the day: fewer than 30 graded, or under 60% right of them.
  - Neither answers on the week.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- **The sample is right:** a test on the sample finds each filing in its member-day's window and a
  member on that day, carrying one of the five items, no 2.02 filing in the window, one per
  member-day, and the draw reproduced from `random.Random(43)`.
- **The text is blind:** a test on the cache finds none of the company's names or tickers in the
  texts the model sees; the count of texts under 500 characters (a stub) is printed.
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
| 1 | The texts and the brief | The brief committed before the first fetch; the sample and its texts by `scripts/eightk_text.py`, its test (the item filter, the window, the 2.02 exclusion, the text cut), the sample and blind tests passing; in `docs/steps/severity-results.txt` the counts left out: no primary document, no item heading read, no exhibit 99, a stub |
| 2 | The scores | `severity-scores.csv` committed and its hash posted; the second reading and the marks in the results file, within their bars |
| 3 | The tester | `severity_check.py` and its test; the two hand checks in the results file equal to the tester's; the local check (lint, format, types, tests) passes |
| 4 | Results | Every cell judged against the rule; goldfish-reviewed, each finding fixed or answered in the pull request; roadmap, status, changelog updated |
| 5 | Forward | Each member's 8-K of these items after the scores' commit, scored by the same brief and the row committed before its reaction close (the commit's time is the proof), graded at its span's end, to the 2027-01-31 gate, in `docs/steps/severity-forward.csv`; one scored late is logged and marked, not graded; recorded, no bar of its own |

## What this step does not do

- **No answer from the model:** a score is an input; a flow of scored filings would be its own
  step, after a cell holds.
- No API, no live call, no page; the Subscription LLM, by hand.

## Technical details

- `scripts/eightk_text.py`: the member-days by `news_moves.membership` (step 40: the seed's
  members on each day) and each 8-K's window day by `news_moves.window_day` (16:00 New York, as
  above); each 8-K's items, acceptance time and primary document from the saved submissions files
  (step 36's cache), the exhibit from the filing's index; `tenk_business.plain` (tags dropped) and
  `blind` (names replaced) for the text.
- `scripts/severity_check.py`: closes and excess moves by `study.excess_spans`; tests in
  `tests/test_severity.py`.

## Results

*Measured 2026-11-21; the evidence, every command and its output, in
[severity-results.txt](severity-results.txt).*

**In plain words:** the Subscription LLM read 400 S&P 500 members' 8-Ks of 2020 to 2025 and found
most of them neutral: 43 bad for shareholders, 22 good, 335 neither, far fewer either way than
expected. A second reading agreed on 47 of the 50 it reread. The score's sign did not say which
way the shares went: after the bad filings they trailed the index on 27 of 43 days, 63%, against
the half of any day before 2020, a chance of 0.06, short of the 0.01 an answer needs; after the
good ones they beat it on 12 of 22, no better than chance. Over the week, neither. Nothing holds.
A filing's own text, scored by a model, does not yet give step 40's filing kinds a direction;
the bad side leans the right way, on too few filings to tell.

| Expected (written before) | Found |
| --- | --- |
| At least 380 filings scored | 400 — right |
| 80 to 160 bad, 40 to 120 good | 43 bad, 22 good, 335 neither — **wrong**: the model scored most filings 0 or ±1 |
| Bad answers on the day | no: 27 of 43 against a base of 0.498, p 0.060 — **wrong** |
| Good does not answer | no: 12 of 22 against 0.502, p 0.42 — right |
| Bad does not hold on the day | it does not: no filing graded walk-forward (the cell never answers on the filings before) — right |
| Neither answers on the week | bad 24 of 43 (p 0.28), good 12 of 22 (p 0.41) — right |
| Second reading within 2 points on 80%, the same side on 70%; at most 5 marked | 100%, 94%; 0 marked — right |

- **The chance line:** 0 answers of 4 cells, under 0.04 plus two.
- **The items** (reported, not counted): the bad 7.01 filings (Reg FD notices, mostly with a
  press release) trailed on 13 of 16 days, p 0.010, at the line but not under it; the bad 2.05
  filings (restructurings), 23 of 36, p 0.063. Neither is a finding; each is too few.
- **The reach:** 200 of the 202 members have closes in the store, and every scored filing in a
  cell is counted. The model may know how a filing turned out (above); the counts say what the
  scores sort, not what they forecast. The forward log is free of that.
- **The checks:** the tester prints the scores' SHA-256 posted in pull request #397; the first bad
  (GM, 2020-02-18) and first good (MMM, 2020-08-13) filings' excess moves recomputed from
  `daily_bars` by a one-off script (its text and command in the evidence), equal to the tester's
  (−0.007149, +0.011788); the local check passes.
- **Step 5:** the forward log, to the 2027-01-31 gate, in `docs/steps/severity-forward.csv`.
