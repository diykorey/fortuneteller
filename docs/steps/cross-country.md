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
| 2 | ~~Results: `raw-move` and `surprise` per flow, here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | Both markets' verdicts and slopes beside the S&P 500's, against the expected outcome |

## Results

Measured 2026-10-21 (`raw-move` and `surprise` per flow). Every US row is identical to the code
before step 1 on the same database.

**Does it move?** (ratio of median moves, release days against ordinary days; verdict)

| Flow | S&P 500 | DAX | Euro Stoxx 50 |
| --- | --- | --- | --- |
| CPI | 1.10, doesn't | 0.95, doesn't | 0.98, doesn't |
| Jobs report | 1.20, moves | 1.10, unclear (p 0.06) | 1.40, moves |
| Fed decision | 1.31, moves | 1.38, moves | 1.63, moves |
| Retail sales | 1.11, unclear | 0.94, doesn't | 1.01, doesn't |
| Core PCE | 1.15, unclear | 1.09, doesn't | 1.14, unclear |
| GDP | 1.24, unclear | 0.95, doesn't | 0.94, doesn't |

**Does it follow the surprise?** On CPI (core against the trend, the verdict's surprise), both
are *unclear*, as the S&P 500 is, but follow it more closely: rank correlation 0.18 (DAX, p 0.0009)
and 0.18 (Euro Stoxx 50, p 0.002) against the S&P 500's 0.13; hit rate 59% and 56% against 54%. Against
Nasdaq's consensus the gap is wider: 0.17 (p 0.004) and 0.14 against the S&P 500's 0.02. Per 0.1 pp
of surprise, −0.19% and −0.17% against −0.12%. On core PCE neither follows it (the S&P 500 neither);
growth news has no expected sign, and neither index tracks it.

**Against what was written down first.** *Both move on CPI and jobs-report days:* wrong on CPI,
where neither moves, but neither does the S&P 500 on this measure; half right on jobs reports (the
Euro Stoxx 50 moves, the DAX is unclear). *Neither follows the CPI surprise:* right by verdict, but
both follow it more than the S&P 500 does, the opposite of a weaker echo.

**What it means.** A US surprise reaches Europe: Fed decisions move it more than New York (the
next day, as they come after its close), and CPI's surprise shows in the DAX at least as clearly
as in the S&P 500, with a larger move per point. Since 2020, Europe's CPI days have been calmer
than its ordinary days (ratios 0.72–0.74), unlike New York's. Walk-forward, the DAX's CPI link
opens from 2014-07 and is right on 5 of 13 calls ("too few"): live CPI releases will log a DAX
call, graded like the others.

## What this does not do

No events abroad (the ECB, euro-area releases), no Bund yield, no Asian markets, no standard units
or `effect_size_matrix`: later slices of step 4a.
