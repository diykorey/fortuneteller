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
  sector news* (its own industry or commodity), *market or economy news* (a data release, a central
  bank, a crisis, that the company moved with more than the index; *added 2026-11-21 by the owner*,
  after the second reading stopped step 2, see below), *legal or regulatory*, *index change*, *nothing found*. Each with its source in
  `docs/steps/news-moves-sample.csv`; a *nothing found* row gives the searches made. *Filed later*
  needs the later 8-K to describe the same event the day's news reports.
- **A script,** `scripts/news_moves.py`, prints the matrix and the sample's days; run on a copy of
  the store (its path in the results file's header). No flow, no new table.

## The rule, fixed before measuring

*Written 2026-11-21. Seen before: no move and no count of this step; the 8-K items of step 36's
saved files, as step 36 read them for items 2.02. Amended the same day after the goldfish, before
any move was read: the chance line's rows named per test; 5.07's lift under 1.5; the direction
line as a count; the no-2.02 rows judged by the same bar; analyst action "the largest of the other
codes"; one member-day per filer; the definitions of the deviation (about the mean, dividing by
504), the sample's rows (*n* = N ÷ 40 rounded down) and the weekend; and the checks below: the
deviation within 0.01 point, five days with no 8-K checked on EDGAR, a failed check stopping step
1, the second reading stopping step 2, the test's summer, winter and Saturday cases. Seen by then: 820 tickers in `sp500.csv`, 624 saved filers, 115
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
- *Amended 2026-11-21, by the owner:* the first coding stopped step 2 (4 of 10 disagreed, 3 of
  them news about the whole economy, which had no code). With the new code all 40 are coded again
  by new readers, and the second reading taken again on the same rows, by the same bar; the first
  coding and its second reading stay in the results file.
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

- `scripts/news_moves.py`, two commands on the store at `FT_DB_PATH`: `matrix SEC_DIR` prints the
  matrix and the counts left out; `sample SEC_DIR` prints the sample's rows. It reads closes with the
  store's own helpers and the items from the saved submissions JSON (`filings.recent` and the
  `files` pages: `form`, `acceptanceDateTime`, `items`).
- The test, in `tests/test_news_moves.py`, as the seed scripts' tests: the window and the
  threshold on hand-made rows.

## Results

*Measured 2026-11-21 on a copy of the store ([evidence](news-moves-results.txt), [the
sample](news-moves-sample.csv)); every number from `scripts/news_moves.py matrix` and `sample`, the
sample's codes from the CSV.*

**In plain words:** on 1.7 million days of S&P 500 members since 2011, 1.63% were big moves. A
big move is 19.6 times as common on a day with a results filing (2.02) as on any day, though that
says they come together, not that the filing moved the shares; only a third of big moves (32.6%)
came with one, and 61.6% came with no 8-K at all. Of 40 of those unfiled big moves, read one by
one from free sources, 19 had no cause tied to the day; 12 were news of the company's industry or
commodity and 5 of the whole economy; 2 were the company's own news, filed late or never filed. Of
the filing kinds with 30 big moves or more, none leans up or down. So most big moves come with no
filing of the company's own, and for half of a sample of them the free sources name no cause.

| | Expected | Found |
| --- | --- | --- |
| Big moves | 1.0% to 2.0% of member-days | 27,646 of 1,695,627, 1.63% — right |
| 2.02 | lift 10 or more; on 35% to 60% of big moves | lift 19.56, goes; on 9,015 of 27,646 (32.6%) — **wrong** on the share |
| 1.01 | goes, lift 3 to 6 | lift 2.55 (370 big of 8,890), does not go — **wrong**; one possible reason, not measured: a company bought out may be missing more often (no closes, no filer), so a target's jump would be undercounted |
| 7.01 | goes; not on its days with no 2.02 | lift 6.66, goes; with no 2.02, 2.74 — right |
| 5.02 and 8.01 | lift 1.5 to 3, do not go | 5.02 lift 2.33, does not go — right; 8.01 lift 3.75, goes — **wrong**; with no 2.02 it is 1.74 |
| 5.07 | lift under 1.5 | 1.28 — right |
| Items with a direction | no more than the chance line plus two | none — right; the test runs on the 11 item rows with 30 big moves or more, a chance line of 0.11 (the script prints 0.21, all 21 rows; the verdict is the same). Items with fewer were not tested (5.01: 3 of 3 up) |
| No 8-K | 30% to 50% of big moves | 17,035 of 27,646, 61.6% — **wrong** |
| Sample: filed later and company news, unfiled | at least 20 of 40 | 2 (1 and 1) — **wrong** |
| Sample: analyst action | the largest of the other codes | 1; peer or sector news is 12 — **wrong** |
| Sample: nothing found | under 10 | 19 — **wrong** |

- **Beyond the expected lines:** other items go with big moves by the bar, on few days each:
  2.05 (exit or restructuring costs, lift 13.0, 3.54 with no 2.02), 3.02 (unregistered sales of
  shares, 3.75, 3.13 with no 2.02), 2.06 (impairments, 5.27), 1.04, 3.01 and 5.05 (under 90 days
  each). Nine of the 21 item rows pass, far over that test's chance line of 0.21; a pass says the item
  comes with big moves, not which way.
- **Left out:** 196 tickers with no filer in the saved files and 26 with no closes, of 820
  (`cut -d, -f2 data/seed/sp500.csv | sort -u`, less the header); 8,482 member-days of a second
  share class (the script's line *left out* labels all three counts *tickers*; this one counts
  member-days). The days lean towards survivors.
- **The checks:** five big moves and five days with no 8-K recomputed from the raw closes by a
  one-off script, its text in the evidence (the same moves to 5 decimals; the deviation as the
  step's script computes it, the same to 5 decimals), and checked on EDGAR's pages by hand (the
  same accessions and minutes; no 8-K in the windows said to have none). The test passes.
- **The sample's codes:** the first coding stopped step 2 (4 of 10 disagreed, 3 of them news about
  the whole economy, which had no code); with the owner's new code, the coding and the second
  reading were taken again: 1 of 10 disagreed (Newmont 2011-09-20, company news or gold), within 2.
  Several *nothing found* rows may have a cause behind a paywall: the free search seldom covers
  one day of one company.
- **What it means for the next kinds:** a filing kind is worth a step of its own when it has a
  surprise to sign it; 2.05 and 3.02 come with big moves without a results day. Of the sample's
  unfiled moves with a cause found, most (17 of 21) are an industry's or the economy's, which the project already measures by flow (oil, CPI, the
  Fed): a member's move against its sector, not the index, would be the next measure.
