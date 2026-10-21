# Cross-country effects, part 1: US releases and Europe's stocks

> The first slice of the [Roadmap](../roadmap.md#next-steps-in-order)'s step 4a, chosen 2026-10-21.
> Builds on [country-aware events](country-aware-events.md), which gave each market's close its own
> time zone. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** does a US release move Europe's stock markets too, and does the move follow the
surprise as it does, or does not, at home?

Every market measured so far trades in New York. A US surprise is one number, but its power may
differ abroad. Europe is the first place to look: its markets close at 17:30 Frankfurt time, three
hours after an 08:30 New York release, so their same-day close holds the reaction; Tokyo closes
before it.

At the end: two European markets beside the five, run through rung 1 (does it move?) and step 4
(does it follow the surprise?) for every US flow, with their verdicts beside the S&P 500's.

## The markets

| Symbol | Market | Yahoo | Close | Daily since |
| --- | --- | --- | --- | --- |
| `DAX` | DAX, Germany | `^GDAXI` | 17:30 Europe/Berlin | 1987 |
| `SX5E` | Euro Stoxx 50, the euro area | `^STOXX50E` | 17:30 Europe/Berlin | 2007 |

Both are seed rows in `data/seed/instruments.csv` (`equity_index`, `europe`), keyed as everywhere
else. The close is checked as the five's were: Yahoo's close against the intraday price at that
time. The German 10-year yield, Europe's counterpart to the 10-year Treasury, has no free daily
series (FRED's is monthly; Stooq now refuses scripts), so it waits; EUR/USD would mostly repeat the
dollar index.

## The rule, fixed before any move is measured

- **Same tests, same bars.** Rung 1's raw move (ratio ≥ 1.10 and p < 0.01) and step 4's surprise
  verdict, unchanged, per flow and its verdict's surprise.
- **Signs: the S&P 500's.** A stock index abroad takes the US one's expected sign in each flow:
  down on hotter inflation (CPI, core PCE), none on growth news (jobs report, retail sales, GDP),
  so growth news gets "does it move?" only. Fixed here, from the S&P 500's, not from any result.
- **How strongly, beside the S&P 500:** each market's Theil–Sen slope per step of surprise on the
  same releases, in percent; a measurement, not a verdict.
- **Ordinary days unchanged:** no event abroad is stored yet, so the clean baseline stays as
  [country-aware events](country-aware-events.md) left it.
- **Calls follow on their own.** `predict` calls a link only when it passes walk-forward; a European
  link that does is logged and graded like the others, its close at 17:30 Berlin.
- **Expected outcome, written down first:** both move on CPI and jobs-report days, as the S&P 500
  does; neither follows the CPI surprise, as the S&P 500 does not.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`DAX` and `SX5E`: seed rows, Yahoo series with their close and zone, signs in each flow's rule~~ **done**; Yahoo's close falls after the last 5-minute bar, 17:25, on 2026-10-15 to 20; `load-prices` stored 1,954 and 1,176 rows, every US count unchanged | `load-prices` stores both; a test's 08:30 New York release falls on the same day's Frankfurt close, through both clock changes; every US output unchanged |
| 2 | Results: `raw-move` and `surprise` per flow, here and in [`mvp-results.md`](../mvp-results.md) | Both markets' verdicts and slopes beside the S&P 500's, against the expected outcome |

## What this does not do

No events abroad (the ECB, euro-area releases), no Bund yield, no Asian markets, no standard units
or `effect_size_matrix`: later slices of step 4a.
