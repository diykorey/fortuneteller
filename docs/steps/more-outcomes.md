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
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** 2026-10-27 | Nine markets' verdicts on both tests for every flow, the signed links' walk-forward records, the chance line, against the expected outcome |

## Results

Measured 2026-10-27 on a copy of the store with the nine loaded, data to 2026-10-26: the page's
numbers (`fortuneteller scoreboard`, `raw-move`, `surprise` and `predict` per flow). Each cell is the
median move on the release's days over ordinary days, and its verdict.

**Does it move?** (ratio; *m* moves, *u* unclear, blank doesn't)

| Release | Brent | EUR/USD | Nasdaq | 5-year | FTSE 100 | STOXX 600 | Bitcoin | Defence | Energy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPI | 0.93 | 1.27 *m* | 1.11 *u* | 1.29 *m* | 1.09 | 1.00 | 1.05 | 0.91 | 1.04 |
| Jobs report | 1.10 *u* | 1.17 *u* | 1.18 *m* | 1.90 *m* | 1.27 *m* | 1.39 *m* | 0.86 | 1.01 | 1.00 |
| Fed decision | 1.18 *u* | 1.55 *m* | 1.38 *m* | 1.39 *m* | 1.31 *m* | 1.50 *m* | 0.98 | 1.17 *u* | 1.05 |
| Retail sales | 0.95 | 1.15 *u* | 1.24 *m* | 1.23 *u* | 1.00 | 1.02 | 0.88 | 1.07 | 1.03 |
| Core PCE | 0.83 | 0.98 | 1.37 *m* | 0.94 | 1.11 *u* | 1.19 *m* | 0.98 | 1.04 | 0.99 |
| GDP | 1.00 | 1.19 *u* | 1.19 *u* | 1.71 *m* | 1.16 *u* | 0.97 | 0.57 | 0.90 | 1.04 |
| ECB decision | 1.01 | 1.42 *m* | 1.25 *u* | 0.90 | 1.08 | 1.15 *u* | 0.79 | 0.93 | 0.73 |
| Euro-area flash | 0.93 | 1.05 | 1.53 *m* | 1.03 | 1.02 | 1.02 | 0.95 | 1.05 | 0.92 |
| ISM | 1.42 *m* | 0.97 | 1.52 *m* | 1.29 *m* | 1.12 *u* | 1.35 *m* | 1.22 *u* | 1.11 *u* | 1.28 *m* |
| Jobless claims | 0.96 | 0.95 | 1.16 *m* | 0.98 | 0.89 | 1.04 | 1.12 *u* | 1.02 | 0.83 |

23 of the nine's 90 cells say *moves*; at p < 0.01 chance alone would give about one. The page's
chance line counts all 160: 1.6.

**Does it follow the surprise?** (rank corr, hit rate of noticeable surprises; the verdict's
surprise per flow, the Fed and the ECB having none)

| Release | EUR/USD | Nasdaq | 5-year | FTSE 100 | STOXX 600 |
| --- | --- | --- | --- | --- | --- |
| CPI (core, trend) | 0.10, 56%, doesn't | 0.16, 56%, unclear | 0.21, 64%, **tracks** | 0.11, 52%, doesn't | 0.17, 52%, unclear |
| Jobs report (trend) | 0.17, 59%, unclear | 0.03, doesn't | 0.27, 59%, unclear | 0.05, doesn't | 0.14, doesn't |
| Retail sales | 0.10, 55%, doesn't | 0.11, doesn't | 0.31, 70%, **tracks** | 0.09, doesn't | 0.14, doesn't |
| Core PCE | 0.11, 47%, doesn't | −0.11, 60%, unclear | 0.04, 60%, unclear | −0.04, 53%, doesn't | −0.13, 53%, doesn't |
| GDP | 0.10, 38%, doesn't | 0.07, doesn't | 0.04, 38%, doesn't | 0.13, doesn't | 0.14, doesn't |
| Euro-area flash | −0.01, 50%, doesn't | 0.07, doesn't | 0.23, doesn't | 0.02, 57%, doesn't | 0.18, 61%, unclear |
| ISM | 0.28, 65%, **tracks** | 0.19, doesn't | 0.41, 71%, **tracks** | 0.04, doesn't | 0.06, doesn't |
| Jobless claims | 0.06, 56%, doesn't | 0.00, doesn't | 0.14, 54%, unclear | 0.02, doesn't | 0.01, doesn't |

Brent, bitcoin, the defence and the energy ETF, which have no sign, follow no surprise: none of their
32 cells reaches p < 0.01 (the nearest the defence ETF on the jobs report, 0.15, p 0.02).

**Walk-forward.** Four links hold at once: the jobs report's euro (56 of 81 right, 69%, p 0.0004,
since 2014-06, beside the dollar index's 55 of 81) and 5-year yield (71 of 101, 70%, p 0.0000,
since 2010-09, beside the 10-year's 65 of 100); retail sales' 5-year yield (49 of 74, 66%, p 0.0035,
since 2009-10, beside the 10-year's 49 of 72); ISM's 5-year yield (34 of 50, 68%, p 0.008, since
2014-08, where the 10-year's 31 of 49 does not hold). Too few: CPI's 5-year (6 of 8) and euro
(2 of 3), ISM's euro (6 of 12). The Nasdaq's, the FTSE 100's and the STOXX 600's links never open.
The first three are called live from their next release, 6 and 17 November; ISM lands at 10:00,
after the morning job.

**The 5-year yield is the most responsive market of the sixteen.** It moves on jobs-report days 90%
more than on ordinary ones (the 10-year 67%), on GDP days 71% (60%), on Fed days 39% (23%); it
tracks CPI, retail sales and ISM as the 10-year does, with the higher correlation each time; and it
holds walk-forward wherever the 10-year does and once where it does not. The front end of the curve
reads growth news harder than the long end.

**The euro is the dollar's mirror, sometimes a sharper one.** It moves on CPI days (1.27, the dollar
1.20), Fed days (1.55, 1.24) and ECB days (1.42, 1.41), but on jobs-report days only *unclear* (1.17
on 273 days since 2003, the dollar 1.27 on 669). It tracks ISM beside the dollar and holds on the
jobs report beside it, a point better.

**The Nasdaq moves on more events than the S&P 500**: seven of ten, against the S&P 500's two,
including retail sales, core PCE, the euro-area flash and lone claims days (1.16, p 0.009), the only
market claims move. It follows CPI's surprise as the S&P 500 does, *unclear*, and no link opens.

**London and the STOXX 600 behave as Frankfurt does**: Fed and jobs-report days move them, the STOXX
600 ISM and core PCE days too; CPI days do not; the ECB's own decisions move neither (1.08, 1.15
*unclear*). The STOXX 600 follows CPI's surprise as the DAX does, *unclear* at 52%.

**Brent moves on ISM days alone** (1.42), the energy ETF with it (1.28); on no other release does
either reach the bar. **Bitcoin moves on no release**, and less than on ordinary days on most: GDP
days 0.57, ECB days 0.79, jobs-report days 0.86. **The defence ETF moves on none**, the Fed nearest
(1.17, p 0.05).

**Against what was written down first.** *The 5-year moves and tracks wherever the 10-year does,
with larger ratios:* right, but for CPI and ISM, where its ratio is smaller, and it holds once more
than the 10-year. *The euro mirrors the dollar index, a little weaker:* mirrors, yes; weaker, no:
it moves more on CPI and Fed days and holds on the jobs report. *The Nasdaq as the S&P 500:* right
on jobs-report and Fed days and on following no surprise; it moves on five events more. *The FTSE
100 and the STOXX 600 as the DAX and the Euro Stoxx 50:* right. *The defence and energy ETFs as the
S&P 500 on release days:* wrong; neither moves on jobs-report or Fed days. *Oil and bitcoin reach
the bar on no release:* right for bitcoin, wrong for Brent on ISM days. *No new link holds except the
5-year's where the 10-year's does:* wrong by two: the 5-year holds on ISM too, and the euro on the
jobs report.

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
