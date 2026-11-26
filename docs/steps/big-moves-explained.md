# Big moves, explained

> Step 62 of the [Roadmap](../roadmap.md). Asked for 2026-11-26 by the owner
> ([why](../decisions.md#2026-11-26-big-moves-explained-and-the-news-scanned-for-markets-we-miss-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *market big move*, *news scan*, *market to add*,
> *our guess*, *Subscription LLM*, *standard deviation*.

## The goal

**In plain words:** each evening the fortune teller looks at the markets that jumped or fell
hard that day. For each one it asks: did we see it coming, and if not, what happened? Once a
month it counts the reasons. Separately, it reads the day's news for big price moves in markets
it does not follow, to learn which markets are missing from its list.

At the end, two files are filled each weekday by the evening job:

- `data/big-moves.csv`: each *market big move* in the markets we track, whether an open call or
  guess covered it and whether it pointed the right way, and its reason as found in the news,
  sorted into one of four kinds;
- `data/news-moves.csv`: each big price move the day's news reports, with the market named, the
  tracked symbol it matches, or none.

A month of them (December 2026) answers how often we see a big move coming, why we miss the rest,
and which markets the news keeps naming that we do not track. Each kind of reason that keeps
coming back is a candidate for a later step, measured on history like any other; each market the
news keeps naming is a candidate to add. Neither file changes a call, a guess or a rule.

## The way to reach it

- **Start from the prices, for our markets.** A paper reports what its readers care about, and
  after the fact. The stored closes catch every big move in what we track, reported or not, at
  no cost: a weekday move at least 3 *standard deviations* of the 504 weekday moves before it
  (step 40's threshold, [news-moves](news-moves.md), on the market's own move instead of a
  company's excess over the index). Moves are `study.daily_moves`: a fraction for prices, basis
  points for yields.
- **Start from the news, for the rest.** The closes cannot show a market we do not store. So
  once each weekday the Subscription LLM, with web search, is asked for the day's news reports of
  big price moves in any market, in any country, and returns each market named, the move as
  reported and the link.
- **The obstacle: after the fact a story is always found.** Of 40 big company moves read by hand
  in step 40, 19 had no reason found and 17 were the industry's or the economy's news. So the
  model must be allowed to say *nothing found*, must give a link for any reason it names, and its
  reasons are checked by hand on a sample before any count of them is reported.
- **Learning stays slow.** One case changes nothing. A reason is only a tally until a kind recurs,
  and then a step of its own, with bars written first.

Covered means an open row on that market that day: a live call in `data/calls.csv`, a stated
forecast in `docs/predicts/forecasts.csv`, or a guess in `docs/predicts/our-guesses.csv`, whose
span holds that close (from its first close after it was made to its end date). It points the
right way if its direction is the big move's; a big move covered by rows pointing both ways counts
as *both*.

Each big move's reason falls in one of four kinds:

- *measured*: a release or decision of a flow `raw-move` takes, that day (the flow is named);
- *scheduled*: a dated event no flow measures (named), such as another country's release;
- *unscheduled*: news nobody scheduled, such as a war, a hack, a company's news;
- *nothing found*: no report tying the move to a cause that day.

## The rule, fixed before measuring

Written 2026-11-26, before building.

The month is the weekdays of December 2026 (23 days), read in Results in the first week of
January 2027.

- **Expected outcome:**
  - big moves are about 1 in 100 market-days, so 10 to 40 in the month across the tracked
    markets, many on the same few days;
  - at least half are covered, since the ledger keeps up to 50 guesses open across some 30
    markets; of the covered, about half point the right way;
  - *measured* is the reason for at most a third; *unscheduled* and *nothing found* together for
    at least half, as in step 40;
  - the news scan names at least 3 markets we do not track on 3 or more days of the month.
- **Bar on the reasons:** 10 big moves, every one if fewer, are checked by hand: the link opens,
  is dated that day or the next, and says what the row says. If fewer than 8 of 10 pass, the
  month's reasons are reported as *unchecked* and no tally of them is read as a finding.
- **Bar on the scan:** 10 rows of `news-moves.csv` checked the same way, with the same 8 of 10.
- **A market to add** is one the news names on 3 or more days of the month with free daily
  history of 10 years or more on Yahoo or FRED. Adding it is a later step, the owner's choice.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | Big moves found and checked against our rows | Tests: a move of exactly 3 deviations is big and one just under is not; a market with fewer than 505 stored weekday closes is left out; a guess whose span holds the day covers it, one ending the day before does not; rows both ways count *both*. On the stored closes, 2024-08-05 is a big move for the Nikkei 225 and VIX |
| 3 | The reasons and the news scan | Tests, the model stubbed: a reply naming a reason without a link is stored as *nothing found*; a failed call leaves the row's reason blank, asked again the next evening; a news row whose market matches a tracked name gets its symbol |
| 4 | In the evening job | Test: the script's evening, with nothing to score, puts both files in the pages' pull request; a day missed by a held evening is filled the next run |
| 5 | December 2026 | Results: the counts of each bar, the two hand checks, and each market to add |

## How you know it is right

- **A threshold off by one day** would show in step 2's test at exactly 3 deviations and in the
  2024-08-05 replay (a move the deviation includes would shrink it).
- **A made-up reason** would show in the hand check: a link that does not open, or does not say
  the reason, fails it.
- **Coverage read with hindsight** would show in step 2's test: a guess ending the day before does
  not cover the move.
- **A scan that only repeats our markets** would show as no untracked row, against the expected
  outcome's 3.

## What this step does not do

It does not change a call, a guess, a rule or the page; add a market or a kind; predict a big
move; or read the news in each country's own papers one by one (the scan asks for reports of big
moves in any market, wherever published). Weekend moves of bitcoin and ether are not read, as
every measurement reads weekdays ([step 59](crypto-weekends.md)).

## Technical details

- **Code:** a command `fortuneteller big-moves` in `__main__.py`, reading the stored weekday
  closes (`study.stored_closes`, `study.daily_moves`) for each day since its file's last row, and
  calling the model as `guess` does (`GUESS_MODEL`, with `WebSearch`), one call per big move and
  one scan a weekday. The evening's `score` runs it after `load-prices`.
- **Files:** `data/big-moves.csv` (day, market, move, deviations, covered, right, kind, flow,
  reason, link) and `data/news-moves.csv` (day, market as named, symbol, move as reported, link),
  documented in [Schema](../schema.md). Reasons in our own words; no article text is stored.
- **Tests:** beside the guesser's (`tests/test_our_guesses.py` style, the model stubbed) and the
  evening script's (`tests/test_evening_prs.py`).
- **Docs:** this spec, the glossary, schema, status, the changelog, roadmap row 62, the decision.

## Results

Not yet measured.
