# Big moves and the news filed with them

> Step 40 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-21 by the owner ([why](../decisions.md#2026-11-21-big-moves-against-the-news-filed-with-them-by-the-owner)).
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** every step so far starts from a kind of news and asks what followed. This one
starts from the other end: the days an S&P 500 company's shares moved far more than usual against
the index, and what the company told the SEC that day. The matrix answers two questions: how often each
kind of filing comes with a big move, and how often a big move comes with no filing at all. The
second says which news the project cannot yet see; a sample of those days, read by hand, names it.

At the end: a matrix of 8-K items against big moves, up and down, each item with its share of big
moves set against the share on every day, judged against the rule below written first; and a
coded sample of big moves no 8-K explains.

## The way to reach it

- **The days:** every *member-day* from 2011-01-03 to the store's last close: a company in the
  S&P 500 that day by `data/seed/sp500.csv` ([step 36](earnings-sp500.md)), with its close and the
  close before in the store. Its *excess day move* is the company's close-to-close move less the
  S&P 500's, as `study.excess_spans` (the code every company flow measures with) gives it for one
  close. Closes load with `load-prices --companies --seed data/seed/earnings_sp500.csv`, which
  loads the companies in step 36's seed only: a member not in it, or with no closes, is counted and
  left out, so the days lean towards survivors, as step 36's. So is a member with no SEC filer
  number (CIK) in the saved files below: its days are not counted as *no 8-K*. Two share classes
  of one filer (GOOG and GOOGL) make one member-day, the first ticker by name.
- **A big move:** an excess day move whose size is at least 3 times the standard deviation of the
  company's excess day moves on the 504 closes before it (the day itself not among them; the
  deviation taken about their mean, dividing by 504; the base's span of the company flows,
  [step 31](earnings.md)); a member-day with fewer than 504 closes before is left out. *Big up* or *big down* by its sign.
- **The filings of a day:** the company's 8-Ks (not 8-K/A) accepted after 16:00:00 New York time
  on the close before (the previous trading close, so a weekend's filings fall to Monday) and at or
  before 16:00:00 on the day; the SEC gives the time in UTC, turned to New York's by its own
  daylight saving, by the acceptance time in the SEC's
  submissions files (each company's filing index, every filing listed with its items).
  Step 36 saved them for 624 companies in `data/cache/earnings/sec500`, every page of each
  present; a member missing there is fetched the same way, with `scripts/sec_8k_times.py`'s
  User-Agent. On a half-day session the 16:00 edge is kept, so a filing after a 13:00 close counts
  to that day; such days are few and are not set apart. An 8-K's *items* are the codes the SEC
  lists for it (2.02 results; 5.02 an officer or director leaving or joining; 1.01 a material
  agreement; 7.01 a disclosure under Regulation FD, often a slide deck or a press release; 8.01
  other events the company chooses to report; and so on); one 8-K can carry several, and a day counts each item once.
- **The matrix:** one row per item with at least 30 member-days, the others pooled as *other*,
  then *any 8-K* and *no 8-K*. For each row: its member-days, how many are big up and big down,
  its *big share* (big moves over its member-days), its *lift* (big share over the big share of
  all member-days), the up share of its big moves, and the same again on its days with no 2.02
  (its *no-2.02* row: its member-days without a 2.02, their big share over the all-days big share;
  results days carry other items, 7.01 and 9.01 most). Item 9.01 (exhibits attached) is printed
  but read as an attachment, not news.
- **The hand-read sample:** the big moves with no 8-K, in date order then ticker, numbered from 1;
  with *N* of them and *n* = N ÷ 40 rounded down, rows *n*, 2*n*, … 40*n*. Each is read from free sources (a web search on the company and the day; EDGAR for an
  8-K filed later) and coded once: *filed later* (an 8-K within the next four closes names it),
  *company news, unfiled* (a press release, guidance at a conference), *analyst action*, *peer or
  sector news*, *legal or regulatory*, *index change*, *nothing found*. Each with its source in
  `docs/steps/news-moves-sample.csv`; a *nothing found* row gives the searches made. *Filed later*
  needs the later 8-K to describe the same event the day's news reports.
- **A script,** `scripts/news_moves.py`, prints the matrix and the sample's days; run on a copy of
  the store (its path in the results file's header). No flow, no new table.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: no move and no count of this step; the 8-K items of step 36's
saved files, as step 36 read them for items 2.02. Amended the same day after the goldfish, before
any move was read: the chance line's rows named per test; 5.07's lift under 1.5; the direction
line as a count; the no-2.02 rows judged by the same bar; analyst action "the largest of the other
codes"; one member-day per filer. Seen by then: 820 tickers in `sp500.csv`, 624 saved filers, 115
of them with no filing before 2011, and 48,884 8-Ks from 2011 on the older pages, every one with
its items.*

- **An item goes with big moves** when it has at least 30 member-days, its lift is at least 3, and
  its big moves are more than the all-days share predicts at p < 0.01 (one-sided binomial). Its
  no-2.02 row is judged by the same bar.
- **An item has a direction** when the up share of its big moves differs from the up share of all
  big moves at p < 0.01 (two-sided binomial), on at least 30 big moves.
- **The chance line:** for each of the two tests, 0.01 times the item rows it is run on (9.01,
  *other*, *any 8-K* and *no 8-K* not among them, nor the no-2.02 rows). Passes at or under the
  line plus two are not read as more than chance.
- **Expected outcome:**
  - Big moves are 1.0% to 2.0% of member-days.
  - 2.02 goes with big moves at a lift of at least 10, and is on 35% to 60% of all big moves.
  - 1.01 (a merger agreement among them) goes with big moves, lift 3 to 6.
  - 7.01 goes with big moves, but not on its days with no 2.02 (lift under 3 there).
  - 5.02 and 8.01 do not: lift 1.5 to 3.
  - 5.07 (a shareholder vote) does not go with big moves: lift under 1.5.
  - Items with a direction: no more than the chance line plus two.
  - *No 8-K* holds 30% to 50% of big moves.
  - The sample: *filed later* and *company news, unfiled* together at least half; *analyst
    action* the largest of the other codes; *nothing found* under a quarter.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- A test: the window takes an 8-K at 16:01 the close before and at 16:00 the day, not at 16:00
  the close before or 16:01 the day, in summer time and in winter time from the SEC's UTC; a
  Saturday's 8-K falls to Monday; the threshold takes a move at 3 deviations and not under.
- Five big moves (the first, a quarter, a half, three quarters, the last) checked by hand: the
  excess move against `study.excess_spans` within 0.1 point; the deviation recomputed from the
  504 closes before, within 0.01 point; and the window's 8-Ks against EDGAR's filing pages, the
  same accessions and acceptance minutes. Five member-days with no 8-K checked the same way on
  EDGAR. Any check that fails stops step 1 until the script is fixed.
- A second reading of ten sample rows (1, then every fourth) by a reviewer who sees only the codes
  above, given the row's sources; disagreeing on more than two stops step 2 for the owner's call,
  with both readings recorded.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The script and the matrix | The test passes; the matrix and the five checks in `docs/steps/news-moves-results.txt`, on a copy of the store |
| 2 | The sample | 40 rows coded with sources in `news-moves-sample.csv`; the second reading in the results file |
| 3 | Results | Each expected line judged; goldfish-reviewed; roadmap, status, changelog updated |

## What this step does not do

- **No prediction:** an 8-K in the same window as the move is a match, not a forecast; an item's
  code says what kind of news it is, not whether it is good. What follows a kind is measured, as
  before, by a step of its own with a surprise; this one says which kinds are worth one.
- No paid news, no news site read in bulk, no news before the window, no flow, no page.
- A big move's cause is not proven by the match: a 2.02 day is a results day, whatever moved it.

## Technical details

- `scripts/news_moves.py`, two commands: `matrix STORE SEC_DIR` prints the matrix and the
  counts left out; `sample STORE SEC_DIR` prints the sample's rows. It reads closes with the
  store's own helpers and the items from the saved submissions JSON (`filings.recent` and the
  `files` pages: `form`, `acceptanceDateTime`, `items`).
- The test, in `tests/test_news_moves.py`, as the seed scripts' tests: the window and the
  threshold on hand-made rows.
