# More outcomes

> Step 7 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-27 with the
> [plan update](../legend.md#the-target): the surface widens, the bars stay. Builds on
> [cross-country effects, part 1](cross-country.md), which gave each market its own close and zone.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** which other markets move on the days of the ten releases, and do the ones with
a sign written down follow a surprise?

Seven markets have been measured against every event. The fortune teller's audience asks about
more: oil, the euro, the Nasdaq, London, bitcoin. Each is one Yahoo series with a daily history
and a close; every verdict table gains a row for each, under the same two tests and the same bars.
Probed 2026-10-27 on Yahoo's chart API, daily bars:

| Symbol | Market | Yahoo | Zone | Close, expected | Daily since |
| --- | --- | --- | --- | --- | --- |
| `BRN` | Brent crude, front month | `BZ=F` | New York | 14:30, the ICE settlement | 2007-07 |
| `EURUSD` | The euro against the dollar | `EURUSD=X` | London | ~~23:59, the day's last price~~ *measured 2026-10-27:* 00:00 of the bar's own day, the price Yahoo keeps as the close, so the next London day's bar is the first after a US release | 2003-12 |
| `COMP` | Nasdaq Composite | `^IXIC` | New York | 16:00 | 1971-02 |
| `UST5Y / ZF` | US Treasury 5-year yield, in bps | `^FVX` | New York | 15:00, as the 10-year's | 1970-01 |
| `UKX` | FTSE 100, London | `^FTSE` | London | 16:30 | 1984-01 |
| `SXXP` | STOXX Europe 600 | `^STOXX` | Zurich | 17:30 | 2004-04 |
| `BTC` | Bitcoin, in dollars | `BTC-USD` | UTC | 23:59, the day's last price | 2014-09 |
| `ITA` | US aerospace and defence ETF | `ITA` | New York | 16:00 | 2006-05 |
| `XLE` | US energy sector ETF | `XLE` | New York | 16:00 | 1998-12 |

The close is expected, not known: step 1 checks each as step 2 and cross-country did, Yahoo's
close against the intraday price at that time. `BRN` and `BTC` are seed rows already; the seven
others go into `data/seed/instruments.csv`. Bitcoin trades every day, and the parser drops weekend
bars, so its Monday move spans the weekend as every market's does. Brent is the seed's oil, the
global benchmark and the natural outcome of step 10's shocks; WTI (`CL=F`) would add 2000 to 2007
and is not taken.

## The rule, fixed before any move is measured

- **Same tests, same bars.** Rung 1's raw move (ratio ≥ 1.10 and p < 0.01) and step 4's surprise
  verdict (rank corr p < 0.01 and hit rate ≥ 60%), per flow, unchanged; walk-forward (*holds*:
  right on ≥ 60% of ≥ 30 predictions, p < 0.01) for every signed link.
- **Signs by analogy, written down here.** In every flow's rule the euro takes the dollar index's
  sign reversed, the 5-year yield the 10-year's, the Nasdaq the S&P 500's, the FTSE 100 and the
  STOXX 600 the DAX's. Oil, bitcoin, the defence and the energy ETF get none: "does it move?" only,
  their surprise rows a correlation with no verdict beyond *unclear*, as gold's. No sign comes from
  a result.
- **Ordinary days unchanged.** No new event is stored; the clean baseline is the same set of days
  for every market, each with its own closes.
- **Every existing cell unchanged.** A market is a column of its own: the seven measured so far,
  their verdicts, records and live calls, are identical before and after.
- **Calls follow on their own.** A signed link that holds walk-forward is called by `predict` and
  the morning job, logged and graded like the others, its close in its own zone.
- **Chance, counted.** Ten flows × sixteen markets = 160 *does it move?* cells, 1.6 *moves* by
  chance at p < 0.01 (70 cells and 0.7 once claims land); the surprise grid 128 cells, 1.3; the
  page's chance line says so.
- **Expected outcome, written down first:** the 5-year yield moves and tracks wherever the 10-year
  does, with larger ratios; the euro mirrors the dollar index, sign reversed, a little weaker; the
  Nasdaq as the S&P 500 (moves on jobs-report and Fed days, follows no surprise); the FTSE 100 and
  the STOXX 600 as the DAX and the Euro Stoxx 50 (Fed days and the jobs report, CPI's surprise short
  of *tracks*); the defence and energy ETFs as the S&P 500 on release days; oil and bitcoin reach
  the bar on no release. No new link holds walk-forward except where the 10-year's does (the jobs
  report, retail sales), and there the 5-year's record is near the 10-year's.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The nine markets: seed rows, Yahoo series with their close and zone checked against intraday bars, signs in every flow's rule, `load-prices` stores them, the page's grids sixteen columns wide~~ **done** 2026-10-27: closes checked against 5-minute bars of 2026-10-19 to 26 (Brent's 14:30 settlement and the 5-year's last bar exact; the stock indices' after their last bar, as the DAX's; bitcoin's the 23:55 UTC bar; EUR/USD's the price at 00:00 London of its own day, the table above amended); on a copy of the store `load-prices` stored 70,792 closes for the nine, 144,077 for the sixteen, and 45,773 observations; the ten events' cells for the seven markets, the calls, the missed line and the rules identical before and after, `score` and `predict` adding rows only; the grids 16 columns wide, 160, 128 and 48 cells; the scoreboard rebuilt in 502 s alone (10 min 16 s beside the test suite). Four new links hold walk-forward at once, for step 2: the jobs report's euro (56 of 81, p 0.0004) and 5-year yield (71 of 101, p 0.0000), retail sales' 5-year yield (49 of 74, p 0.0035) and ISM's (34 of 50, p 0.008; not called live, ISM lands at 10:00); the first three are called from their next release | `load-prices` stores nine more series; a test's 08:30 New York release falls on the same day's close in London, Zurich and UTC, and a 14:00 Fed decision on the next day's FTSE close; every existing output identical on a copy of the store; the scoreboard rebuilt in under ten minutes |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Nine markets' verdicts on both tests for every flow, the signed links' walk-forward records, the chance line, against the expected outcome |

## Technical details

Nine `PriceSeries` rows in `MVP_PRICE_SERIES` (ticker, unit, close, zone; `bps` for the 5-year
yield, `pct` for the rest), with `Europe/London`, `Europe/Zurich` and `UTC` beside New York and
Frankfurt; seven seed rows; nine keys in each flow's expected signs. `load-prices` is one request
per ticker, nine more a night for the evening job; the scoreboard's permutations grow with the
cells (about 3 minutes for 63 today). `docs/schema.md` gets the seed count and the series, the
glossary the seven new symbols.

## What this does not do

No new event, no intraday window, no Bund yield (no free daily series), no Nasdaq-100 or WTI beside
the composite and Brent, no sign for oil, bitcoin or the ETFs, no `ret_1w` horizon (step 10's), no
`effect_size_matrix`.
