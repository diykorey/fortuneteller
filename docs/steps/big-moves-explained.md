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
  points for yields; each market's deviation is in its own unit, so the two never mix.
- **Start from the news, for the rest.** The closes cannot show a market we do not store. So
  once each weekday the Subscription LLM, with web search, is asked for the day's news reports of
  big price moves in any market, in any country, and returns each market named, the move as
  reported and the link. *Amended 2026-11-27, before December:* the scan's list gives each
  market's own name beside its plain one ("S&P 500 / the US stock market"), and a market the
  reply names exactly as we do gets our symbol though the reply left it blank; the first run
  named the S&P 500 on three days with no symbol, which would have made it a market to add.
- **The obstacle: after the fact a story is always found.** Of 40 big company moves read by hand
  in step 40, 19 had no reason found and 17 were the industry's or the economy's news. So the
  model must be allowed to say *nothing found*, must give a link for any reason it names, and its
  reasons are checked by hand on a sample before any count of them is reported.
- **Learning stays slow.** One case changes nothing. A reason is only a tally until a kind recurs,
  and then a step of its own, with bars written first.

Covered means an open row on that market, with a direction *up* or *down*, whose span holds
that close: a live call in `data/calls.csv` (its `instrument`, `direction` and release `day`,
spanning that day's reaction close; a row with no direction covers nothing), a stated forecast in
`docs/predicts/forecasts.csv`, or a guess in `docs/predicts/our-guesses.csv` (each from its first
close after it was made, [step 56](honest-page.md), to its end date). It points the right way if
its direction is the big move's; a big move covered by rows pointing both ways counts as *both*.

The model is given the market's name and symbol, the day, the move and the four kinds below, and
answers with a kind, the cause in a sentence and one link that names that cause for that move.
Several big moves on one day get one call each; the tally counts moves and, apart, days.
Each big move's reason falls in one of four kinds:

- *measured*: a release or decision of a flow `fortuneteller raw-move --event` takes (its help
  lists them), that day; the flow is named;
- *scheduled*: a dated event no flow measures (named), such as another country's release;
- *unscheduled*: news nobody scheduled, such as a war, a hack, a company's news;
- *nothing found*: no report tying the move to a cause that day.

## The rule, fixed before measuring

Written 2026-11-26, before building; *amended 2026-11-26, after the goldfish review, before
building.*

The month is the weekdays of December 2026 (23 days), read in Results in the first week of
January 2027.

Each expectation is marked right or wrong in Results; none stops the step.

- **Expected outcome:**
  - big moves are about 1 in 100 market-days, so 10 to 40 in the month across the tracked
    markets, many on the same few days;
  - at least half are covered, since 65 guesses run into December across 30 markets
    (`our-guesses.csv` on 2026-11-26); of the covered, 35% to 65% point the right way;
  - *measured* is the reason for at most a third; *unscheduled* and *nothing found* together for
    at least half, as in step 40;
  - the news scan names at least 3 markets we do not track on 3 or more days of the month.
- **Bar on the reasons:** 10 big moves, every one if fewer, checked by hand, picked by position
  in the file ordered by day and market: the first, the last and eight evenly between. A row passes
  if its link opens, is dated that day or the next, names this cause for this market's move (a
  market wrap that lists the move without its cause fails), and its kind fits the list above
  (*measured* only for a flow `raw-move` takes). If fewer than 8 pass, the month's reasons are
  reported as *unchecked* and no tally of them is read as a finding. Ten rows can show a model
  that makes reasons up; they cannot prove one that does not.
- **Bar on the scan:** 10 rows of `news-moves.csv`, every one if fewer, picked the same way: the
  link opens, is dated that day or the next, reports that move, and the symbol is right (blank
  only for a market we do not track); 8 of 10.
- **A market to add** is one the news names on 3 or more days of the month with free daily
  history of 10 years or more on Yahoo or FRED. Names are the model's common English name
  ("copper", "Turkish lira"); two names grouped as one market are listed so in Results. Adding it is a later step, the owner's choice.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | Big moves found and checked against our rows | Tests: a move of exactly 3 deviations is big and one just under is not; a market with fewer than 505 stored weekday closes is left out (*amended 2026-11-26, in the build:* 506, for 504 moves before the day's); a guess whose span holds the day covers it, one ending the day before does not; rows both ways count *both*; a call with no direction covers nothing. On the stored closes, 2024-08-05 is a big move for the Nikkei 225 (down about 12%) and VIX (up about 65%) |
| 3 | The reasons and the news scan | Tests, the model stubbed: a reply naming a reason without a link is stored as *nothing found*; a failed call leaves the row's kind and reason blank (*not asked*), asked again each evening up to 5 weekdays, then left blank and counted apart; the scan's prompt lists every tracked market's name and symbol, and a reply's symbol not in that list is stored blank |
| 4 | In the evening job | Test: the script's evening, with nothing to score, puts both files in the pages' pull request (`scoreboard-<day>`, merged on passing checks, [trigger-file](trigger-file.md)); a day missed while the evening waited on an open `calls-`, `score-` or `scoreboard-` pull request is filled by the next run, up to 5 weekdays back |
| 5 | December 2026 | Results: the counts of each bar, the two hand checks, and each market to add |

## How you know it is right

- **A threshold off by one day** would show in step 2's test at exactly 3 deviations and in the
  2024-08-05 replay (a move the deviation includes would shrink it).
- **A made-up reason** would show in the hand check: a link that does not open, or does not say
  the reason, fails it.
- **A link that does not give the cause** fails the hand check: a market wrap listing the move
  is not a reason.
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
  calling the Subscription LLM as `guess` does (its model named in `GUESS_MODEL` and stored on
  each row, with web search only), one call per big move and one scan a weekday. The evening's `score` runs it after `load-prices`.
- **Files** (*amended 2026-11-26, in the build:* documented here, as the ledgers are in their
  specs; [Schema](../schema.md) holds the store's tables). Reasons in our own words; no article
  text is stored.
  - `data/big-moves.csv`, one row per market and day: `day`; `market` (a symbol of
    `study.MVP_PRICE_SERIES`); `move` (a fraction for prices, basis points for yields, signed);
    `deviations` (the move over the deviation of the 504 before); `covered` (`yes`, `no`);
    `right` (`yes`, `no`, `both`, blank when not covered); `kind` (one of the four, blank when
    *not asked*); `flow` (a `raw-move` flow, for *measured* only); `reason`; `link`; `model`.
  - `data/news-moves.csv`, one row per market named: `day`; `market` (the model's English
    name, blank on a day the scan named none); `symbol` (ours, or blank); `move` (as reported);
    `link`; `model`. A day with no row was not scanned and is asked again.
- **Tests:** beside the guesser's (`tests/test_our_guesses.py` style, the model stubbed) and the
  evening script's (`tests/test_evening_prs.py`).
- **Docs:** this spec, the glossary, schema, status, the changelog, roadmap row 62, the decision.

## Results

Not yet measured.
