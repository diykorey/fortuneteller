# Big moves and the news filed with them

> Step 40 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-21 by the owner ([why](../decisions.md#2026-11-21-big-moves-against-the-news-filed-with-them-by-the-owner)).
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** every step so far starts from a kind of news and asks what followed. This one
starts from the other end: the days an S&P 500 company's shares moved far more than usual against
the index, and what the company told the SEC that day. Two counts make the matrix: how often each
kind of filing comes with a big move, and how often a big move comes with no filing at all. The
second says which news the project cannot yet see; a sample of those days, read by hand, names it.

At the end: a matrix of 8-K items against big moves, up and down, each item with its share of big
moves set against the share on every day, judged against the rule below written first; and a
coded sample of big moves no 8-K explains.

## The way to reach it

- **The days:** every *member-day* from 2011-01-03 to the store's last close: a company in the
  S&P 500 that day by `data/seed/sp500.csv` ([step 36](earnings-sp500.md)), with its close and the
  close before in the store. Its *excess day move* is the company's close-to-close move less the
  S&P 500's, as `study.excess_spans` gives it for one close. Its closes load with `load-prices
  --companies --seed data/seed/earnings_sp500.csv`; a member with no closes is counted and left
  out, so the days lean towards survivors, as step 36's.
- **A big move:** an excess day move at least 3 times the standard deviation of the company's
  excess day moves over the 504 closes before (the base's span, as `study.event_base` takes it); a
  member-day with fewer than 504 closes before is left out. *Big up* or *big down* by its sign.
- **The filings of a day:** the company's 8-Ks (not 8-K/A) accepted after 16:00 New York time on
  the close before and up to 16:00 on the day's close, by the acceptance time in the SEC's
  submissions files, already saved for step 36 (`data/cache/earnings/sec500`; fetched for a
  member missing there, with the User-Agent of step 36). An 8-K's *items* are the codes the SEC
  lists for it (2.02 results, 5.02 an officer leaving or joining, 1.01 a material agreement, and
  so on); one 8-K can carry several, and a day counts each item once.
- **The matrix:** one row per item with at least 30 member-days, the others pooled as *other*,
  then *any 8-K* and *no 8-K*. For each row: its member-days, how many are big up and big down,
  its *big share* (big moves over its member-days), its *lift* (big share over the big share of
  all member-days), the up share of its big moves, and its lift again on its days with no 2.02
  (results days carry other items, 7.01 and 9.01 most). Item 9.01 (exhibits attached) is printed
  but read as an attachment, not news.
- **The hand-read sample:** the big moves with no 8-K, in date order, every *n*-th, *n* chosen to
  give 40. Each is read from free sources (a web search on the company and the day; EDGAR for an
  8-K filed later) and coded once: *filed later* (an 8-K within the next four closes names it),
  *company news, unfiled* (a press release, guidance at a conference), *analyst action*, *peer or
  sector news*, *legal or regulatory*, *index change*, *nothing found*. Each with its source in
  `docs/steps/news-moves-sample.csv`.
- **A script,** `scripts/news_moves.py`, prints the matrix and the sample's days; run on a copy of
  the store. No flow, no new table.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: no move and no count of this step; the 8-K items of step 36's
saved files, as step 36 read them for items 2.02.*

- **An item goes with big moves** when it has at least 30 member-days, its lift is at least 3, and
  its big moves are more than the all-days share predicts at p < 0.01 (one-sided binomial).
- **An item has a direction** when the up share of its big moves differs from the up share of all
  big moves at p < 0.01 (two-sided binomial), on at least 30 big moves.
- **The chance line:** at p < 0.01, the number of rows times 0.01; findings at or under it plus two
  are not read as more than chance.
- **Expected outcome:**
  - Big moves are 1.0% to 2.0% of member-days.
  - 2.02 goes with big moves at a lift of at least 10, and is on 35% to 60% of all big moves.
  - 1.01 (a merger agreement among them) goes with big moves, lift 3 to 6.
  - 7.01 goes with big moves, but not on its days with no 2.02 (lift under 3 there).
  - 5.02 and 8.01 do not: lift 1.5 to 3.
  - 5.07 (a shareholder vote) does not go with big moves.
  - No item has a direction, the chance line plus two at most.
  - *No 8-K* holds 30% to 50% of big moves.
  - The sample: *filed later* and *company news, unfiled* together at least half; *analyst
    action* the next largest; *nothing found* under a quarter.
  - A count outside its band is recorded, not a stop.

## How you know it is right

- A test: the window takes an 8-K at 16:01 the close before and at 16:00 the day, not at 16:00
  the close before or 16:01 the day; the threshold takes a move at 3 deviations and not under.
- Five big moves (the first, a quarter, a half, three quarters, the last) checked by hand: the
  excess move against `study.excess_spans` within 0.1 point, and the window's 8-Ks against
  EDGAR's acceptance times.
- A second reading of ten sample rows (1, then every fourth) by a reviewer who sees only the codes
  above; disagreeing on more than two is recorded with both readings.

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
