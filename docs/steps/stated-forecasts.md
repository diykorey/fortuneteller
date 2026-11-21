# Stated forecasts

> Step 48 of the [Roadmap](../roadmap.md), for [step 23](be-seen.md)'s readers, on
> [Fortuneteller predicts](predicts.md). Terms are in the [Glossary](../glossary.md): *holds*,
> *walk-forward*, *cell*, *the answers that hold*. Asked for 2026-11-21 by the owner:
> "we should state something that we expect will happen today, tomorrow or soon … next year the
> cost of real estate will grow, tomorrow the stock market will fall", option A of the choice put
> to them the same day (the others: long-run patterns only; or daily calls with no tested
> record, not recommended).

## The goal

**In plain words:** the predictions page says what will happen, not only what would follow an
*if*. *Over the next year, US home prices will rise.* Each forecast has its tested record beside
it, is saved with its date, and is scored when its span ends, so the page can say how many came
true.

At the end, `docs/predicts/` shows stated forecasts of two kinds, and a file of every forecast
stated with its grade once its span has ended:

1. **From the long run:** a market over a span from tomorrow to a year, where its past direction,
   tested walk-forward, holds;
2. **After news that has landed:** an event of a kind whose week or month cell holds has
   happened, and its span has not ended, so what follows is stated outright.

## The way to reach it

- **The obstacle is honesty, not code.** A forecast before the news is what the reset answered
  (CLAUDE.md). Both kinds avoid it: the first calls no event, only the market's own past; the
  second is made from the actual once it has landed, as CLAUDE.md requires.
- **Overlapping spans would fake the record.** Every year-long span starting on each day of
  history shares most of its days with the next, so a count of them overstates how often the
  rule was tested. The test cuts the history, forward from its first close, into consecutive
  spans of one length that do not overlap (1, 5, 21 or 252 trading days); an unfinished last span
  is not counted. Cut from the first close, a span's edges do not move as days are added.
- **The long-run test:** walk-forward over those spans, oldest first. Before each span, the
  forecast is the direction more of the earlier spans took (none on a tie, none before five
  earlier spans). It is right if the span went that way. A span with no change is left out. The
  forecast stated now is the same rule over every finished span.
- **Holds, as rung 2 fixed it:** at least 30 forecasts, right on at least 60% of them, and a
  one-sided binomial p below 0.01 against a coin. The page states only a market and span that
  holds on the evening it is written.
- **Home prices** (S&P CoreLogic Case-Shiller national index, FRED `CSUSHPINSA`) come out about
  two months late and move with the seasons, so only the year is tested (12 monthly values), and
  the sentence names the months it covers: *in the 12 months after September 2026*.
- **After news:** a cell counts if it is among *the answers that hold* (so not a kind cell and not
  read as the period), its span is a week or a month, and its market is one of the markets the
  store measures by date (a company's own shares are not: they need a company). The flow's latest
  stored event with a kind is the one read. If it is of the cell's kind and its span, counted in
  weekdays from the event's first reaction day, ends on or after the evening the page is written,
  the forecast is stated: *by Mon, Nov 24, US gasoline prices will be higher than before the
  report*. It is measured from the close before the event, as the cell is, and the sentence says
  so: some of its days may already have passed.
- **Each forecast is kept once.** The evening job appends to `docs/predicts/forecasts.csv` a
  row per forecast: the day stated, the market, span, direction and kind (*long run* or *after
  news*), and the span's first and last day. A long-run forecast is added only when no row of the
  same market and span is still open, so the rows' spans do not overlap; while one is open, the
  page shows that row's forecast and its last day. An after-news forecast is added once per event,
  market and span. When the closes for a row's last day are stored, its grade is filled in: *came
  true* or *did not*, from the close before its first day to the close of its last. The page
  shows the tally: so many came true, so many did not, so many still open.

- **On the page** (*amended 2026-11-21, after step 1's results and before step 3 was built*):
  the after-news forecasts first, then one long run per market at its shortest span that holds,
  three stated forecasts at most, so the *if* cards keep at least two of the five places. Five
  pairs hold and four of them are two markets at two spans; a reader gains nothing from the S&P
  500's month and its year side by side. A stated card names its market and span (*The US stock
  market, over the next month*) and says what will be so: *higher on Mon, Dec 21, 2026 than on
  Fri, Nov 20, 2026*. Spans are counted in weekdays; a market holiday is not known, so a span's
  last day can fall one trading day later than its length.

## The rule, fixed before measuring

- **Bars:** a long-run forecast is shown only if it *holds* (above); an after-news forecast only if
  its cell is among *the answers that hold*.
- **Markets and spans tested:** the S&P 500, the Nasdaq Composite, gold, Brent oil, the dollar
  index, the 10-year Treasury yield and bitcoin over 1, 5, 21 and 252 trading days, and US home
  prices over 12 months: 29 pairs, measured on the store of 2026-11-21 and written in Results.
  The chance count is printed beside them: 29 × 0.01, about 0.3 by chance, so more than two that
  hold is more than chance.
- **History:** a pair needs 35 spans (30 forecasts after 5) to be able to hold. At a year that is
  35 years of closes, which gold, Brent and bitcoin do not have in the store: their year is *too
  few* by construction. `forecasts` prints each market's first close so this is visible.
- **Expected outcome:**
  - no 1-day forecast holds;
  - three to five pairs hold, all saying *up*: the S&P 500 and the Nasdaq at a year, home prices
    at a year, perhaps the S&P 500 or the Nasdaq at a month;
  - the 24 others do not hold or are *too few*;
  - after news, on the store of 2026-11-21: one or two forecasts open, from the CPI of
    2026-11-10 or the jobs report of 2026-11-20, if their kinds have a holding week or month cell.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `long_run(closes, span)` in `study.py`; `fortuneteller forecasts` prints the 29 pairs; Results written | Tests: 41 spans of a rising series give 36 forecasts, all right, *holds*, *up*; a seeded coin of 2,000 days does not hold at a day; spans run forward from the first close and leave an unfinished last span out; 25 monthly values give 2 year spans. Results list each pair's first close, right, of, p and verdict |
| 2 | After-news forecasts in `stated(data, today)`; `ask_entry` gives each flow's latest event and, on each cell of its kind, the span's last day | Tests: a holding week cell of the latest event's kind gives a forecast on its last day and none the day after; a day cell, a kind cell or a period cell gives none |
| 3 | The page states the forecasts first, then the *if* cards; `forecasts.csv` kept and graded | Tests: a long-run forecast is not added while its row is open and is added the day after it ends; a row is graded *came true* when its last close is above its first for *up*, and an open row is not graded; the rendered page shows *Over the next year, the US stock market will rise.* from a stub |
| 4 | Published | The page is live; the date and the first rows of `forecasts.csv` are written in Results |

## How you know it is right

- **Overlap caught:** spans are cut forward and do not overlap; a test of 2,000 closes over 252
  gives 7 spans, and the forecast count is the span count less five.
- **A coin stays a coin:** a seeded random walk of 2,000 days gives no 1-day forecast that holds.
- **Nothing peeks:** a test adds a span to a series and finds the record of every earlier span
  unchanged, with one forecast more.
- **The file cannot pile up:** a test writes the page on ten evenings in a row and finds one
  long-run row per market and span.
- **The edge of a span:** the after-news test sits on the last day and the day after it.

## What this step does not do

No forecast of an event before it happens. No quarter or year after news (only the Fed's
decisions have those cells). No percentage and no size of move. No new kind of
event. No market outside the list above. No 1-day forecast stated unless it holds.

## Technical details

- **Sources:** closes from `daily_bars` (`SPY / ES`, `COMP`, `GC / XAU`, `BRN`, `DXY`,
  `UST10Y / ZN`, `BTC`); home prices from FRED `CSUSHPINSA` through `sources.fetch_series`, read
  when `scoreboard` runs with `FT_FRED_API_KEY` set (the evening job had no key until this step; it
  now reads `FT_FRED_API_KEY` alone from the main checkout's `.env`, which also brings back the
  Fed's group on *Ask*), and left out with the reason when not.
- **Code:** `long_run` in `study.py`; `fortuneteller forecasts` prints the table; `scoreboard_data`
  gains `forecasts` (each pair's record and verdict) and `ask_entry` gains `latest`.
- **Words** follow [plain words](predicts.md): *Over the next year, the US stock market will rise.
  Tested on N past years, one at a time, this rule held R times and failed W.*
- **Docs:** this spec, the glossary (*stated forecast*, *long-run forecast*), status, the
  changelog, roadmap row 48 and a decisions entry for the page stating forecasts.

## Results

**Step 1, the long run, 2026-11-21.** `fortuneteller forecasts` on a copy of the store of
2026-11-21 (closes to 2026-11-20), home prices from FRED to September 2026:

| Market | First close | Tomorrow | Week | Month | Year |
| --- | --- | --- | --- | --- | --- |
| S&P 500 | 1970-01-02 | 7,560 of 14,280, no | 1,609 of 2,849, no | **402 of 666, holds** | **37 of 49, holds** |
| Nasdaq Composite | 1971-02-05 | 7,828 of 14,020, no | 1,619 of 2,802, no | **408 of 658, holds** | **35 of 50, holds** |
| Gold | 2000-08-30 | 3,450 of 6,526, no | 743 of 1,305, no | 167 of 300, no | 14 of 21, too few |
| Brent oil | 2007-07-30 | 2,454 of 4,745, no | 487 of 940, no | 114 of 221, no | 5 of 12, too few |
| Dollar index | 1971-01-04 | 6,742 of 13,653, no | 1,362 of 2,746, no | 318 of 651, no | 23 of 48, no |
| 10-year Treasury yield | 1970-01-02 | 6,751 of 13,382, no | 1,397 of 2,771, no | 323 of 646, no | 23 of 48, no |
| Bitcoin | 2014-09-17 | 1,643 of 3,155, no | 340 of 629, no | 81 of 141, no | 3 of 7, too few |
| US home prices | 1987-01 | | | | **29 of 34, holds** |

Each cell is right of forecasts made; *no* is *doesn't hold*. Five of the 29 pairs hold, all
saying *up* (0.3 expected by chance), as expected: the S&P 500 and the Nasdaq at a month and a
year, home prices at a year. No 1-day forecast holds. The S&P 500's tomorrow is right 7,560 of
14,280 times, p about 1e-12 against a coin, but short of the 60% bar: a day's direction is close
to a coin, so the page says nothing about tomorrow. The S&P 500 begins in 1970 in the store, not
1928, so its year has 49 forecasts.
