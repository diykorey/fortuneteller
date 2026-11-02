# Germany's calendar

> Step 9 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-02 after the
> statements' preview. The first European surveys, and the first country inside the euro area.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** does Europe move on its own news? Germany's two business surveys and its
flash inflation each come out every month, before New York opens, with a forecast. Do markets
move on those days, and does the move follow the surprise?

So far Europe has reacted mostly to the US. Fed decisions and jobs reports move the DAX, while the
ECB moves the dollar and only London's stocks, and the euro-area flash moves the S&P 500 but not
Frankfurt. Germany is the euro area's largest economy, and its surveys are the ones the region's
markets are said to watch.

At the end: three German releases are loaded as event flows with their surprises, and run through
rung 1, step 4 and walk-forward for all sixteen markets.

## The events

- **Source:** TradingView's calendar for `DE`, fetched a quarter at a time and cached like `US`
  and `EU`. Checked 2026-11-02, with a forecast and an actual on each row:

  | Flow | Row | Releases | Time (Frankfurt) | Alone |
  | --- | --- | --- | --- | --- |
  | `zew` | `ZEW Economic Sentiment Index`: analysts' six-month outlook | 157, 2013-10 to 2026-10 | 11:00 (15 at 12:00) | 113 |
  | `ifo` | `Ifo Business Climate`: firms' current state and outlook | 104, 2018-02 to 2026-10 | 10:00 | 97 |
  | `decpi` | `Inflation Rate YoY Prel`: the national flash CPI | 144, 2014-11 to 2026-10 | 14:00 (8 at another time) | 85 |

  *Alone* counts the days with no other stored release that isn't a lesser one. ZEW shares 23
  days with US CPI and 21 with retail sales. The flash CPI shares 28 with core PCE and 21 with
  GDP. The three almost never share a day with each other (one ZEW–Ifo day).
- **Ifo's history starts in 2018** on TradingView, the only calendar this project reads it from.
- **The flash CPI comes late in its own day.** Six states publish their CPI from 10:00, with no
  forecast, so by 14:00 much of the national print may be known. The surprise is still taken
  against TradingView's forecast, whenever it was last updated; a close-to-close move holds the
  state prints and the national one alike.
- **Time:** the calendar's own, before Frankfurt's 17:30 close and New York's open, so every
  market reacts the same day.
- **Origin:** `Germany`, already in the seed. Two new seed event types: `Investor sentiment survey`
  (ZEW) and `Business climate survey` (Ifo). The flash CPI is a `CPI / inflation surprise`.

## The rule, fixed before any move is measured

- **Rung 1's test and step 4's, unchanged:** for *moves*, a ratio ≥ 1.10 at p < 0.01; for
  *tracks*, a rank correlation at p < 0.01 with the right sign on ≥ 60% of noticeable surprises.
- **Lesser, as claims.** A German day remains an ordinary day for every other flow, and is no
  other flow's shared day. Every existing table, verdict and call stays identical. Each German
  flow's tables keep only its lone days.
- **The surprise: actual minus TradingView's forecast.** It is noticeable from two thirds of the
  forecast's median miss, as for claims: ZEW 3.5 points (median miss 5.2), Ifo 0.5 points (0.8),
  the flash CPI 0.1 pp (the print's own step). No 12-month trend.
- **Expected signs.** For stronger surveys: the DAX and the Euro Stoxx 50 up (London and the
  STOXX 600 by analogy), and the dollar index down (a stronger euro, so the euro up); the US
  markets, the 10-year yield and gold none. Unlike ISM's, Europe's stocks get a sign: one country's
  growth news moves the ECB less than ISM's moves the Fed, so less of it is undone by a dearer
  rate. For a hotter flash CPI, the euro-area flash's signs: the dollar index, the DAX and the
  Euro Stoxx 50 down.
- **No live calls.** All three land before the release-day job's 08:30 New York run, so `live`
  skips them, as it skips the euro-area flash. `predict` grades their links walk-forward.
- **Chance, counted:** fifteen flows × sixteen markets = 240 *does it move?* cells, 2.4 *moves*
  by chance; the surprise and walk-forward grids grow by 48 cells each. *Amended 2026-11-02, in
  step 1:* walk-forward only by 18, a cell for each market with an expected sign, six a flow; the
  grids hold 176 and 66 cells.
- **Expected outcome, written down first:** none of the three moves a market at the bar, the euro
  and the DAX the nearest on ZEW days. Nothing tracks a surprise; the DAX comes closest on Ifo
  and the euro on the flash CPI. Ifo's 97 lone days give the fewest noticeable surprises, and no
  link opens.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The three flows, their TradingView rows and their seed types; `load-releases` and `load-surprises` store them; the scoreboard gains three rows~~ **done** 2026-11-02; on a copy of the store, 157 ZEW, 104 Ifo and 144 flash CPI releases and their surprises stored; the scoreboard built by the code before and after from that same copy, every existing entry identical, three flows added, in 12 min beside the other build. The page's *missed* would have listed the three: it now counts only the flows `live` calls, as ISM and the euro-area flash would have shown from their next release | A test's `DE` quarter stores a ZEW, an Ifo and a flash CPI release at their Frankfurt times, with their surprises; `raw-move` and `surprise --event zew` print sixteen verdicts; every existing output identical on a copy of the store; `live` unchanged; the scoreboard rebuilt within the evening job's twenty minutes |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Every verdict of the three, against the expected outcome |

## Technical details

Three entries in `sources.TRADINGVIEW_ROWS` with the country `DE` and the zone `FRANKFURT`, and
three `TradingViewFlow` lines with `lesser=True`, type codes 13–15. One sign table for the two
surveys beside `EURO_EXPECTED_SIGN`, and three `SurpriseRule`s with `predicted_from` TradingView's
forecast. Two seed rows
in `data/seed/event_types.csv`, documented in `docs/legacy/data/events.md` and `docs/schema.md`.

## What this does not do

It adds no Bund yield (no free daily series), no state CPIs, no Ifo before 2018, and no other
German release (factory orders, industrial production). France and Italy are not included.
