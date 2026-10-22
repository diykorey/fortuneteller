# Cross-country effects, part 3: euro-area inflation

> The third slice of the [Roadmap](../roadmap.md#next-steps-in-order)'s step 4a, chosen 2026-10-22,
> after [part 2](ecb-decisions.md) found ECB decisions priced in. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** does the euro area's inflation news move markets, and does the move follow the
surprise, as the 10-year yield follows US CPI's?

ECB decisions are expected, so they move little. What is not expected is the data the ECB decides
on: Eurostat's flash estimate of the month's inflation (**HICP**), out around the first working day
of the month at 11:00 Frankfurt. It is the first non-US event with a surprise.

At the end: flash releases loaded as an event flow with their surprise, run through rung 1 (does it
move?) and step 4 (does it follow the surprise?) for all seven markets.

## The events

- **Source:** TradingView's EU calendar, the rows `Core Inflation Rate YoY Flash` and
  `Inflation Rate YoY Flash`, fetched by quarter as for ECB decisions. Checked 2026-10-22: 142
  releases from 2014-11-28, every one with both actuals.
- **Time:** the calendar's own (11:00 Frankfurt), before Frankfurt's close and before New York
  opens, so every market reacts the same day.
- **Origin:** `Euro area`, event type `CPI / inflation surprise`, as US CPI's.
- **Measures:** year-on-year core and headline, with names of their own, so no US source
  (Nasdaq, the Cleveland Fed) ever reads them. The month-on-month flash starts in 2020 and never
  has a forecast.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** ratio ≥ 1.10 and p < 0.01 for every market.
- **The surprise: actual minus TradingView's forecast.** Nasdaq's calendar lists no euro-area flash
  (checked 2026-10-22 on three flash days), so there is no second calendar to check it against.
  Core gives the verdict, headline is context; noticeable from 0.1 pp, the print's own step. No
  12-month trend: an average of year-on-year rates is not an expectation.
- **Expected signs for a hotter print:** the DAX and the Euro Stoxx 50 down, as the S&P 500 is on
  US CPI; the **dollar index down**, since a hotter euro area means a stronger euro, over half of
  the index; the S&P 500, the 10-year yield, gold and VIX none.
- **Shared days left out** of the surprise tables, as for every consensus flow: a flash can fall on
  a jobs-report, core PCE or GDP day.
- **Ordinary days lose flash days** for every market, as they lost ECB days; each US verdict that
  changes is reported.
- **No live calls.** The flash lands 3½ hours before the release-day job's 08:30 New York run, so
  `live` skips it; `predict` grades its links walk-forward like the others.
- **Expected outcome, written down first:** the flash moves the dollar index only; the dollar index
  and the 10-year yield (by the Bund) follow the core surprise, Europe's stocks are unclear.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The flash flow: events and actuals from TradingView, the forecast as an expectation source, the rule above; `live` skips it | A test's calendar quarter stores a flash at its Frankfurt time with its core and headline surprises; `raw-move` and `surprise --event hicp` print seven verdicts; `live` and every US output unchanged |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Seven verdicts on both tests, US verdicts before and after, against the expected outcome |

## Technical details

`HicpFlow` beside `EcbFlow`, type code 8, cli `hicp`. The test flows' codes 9 and 10 move to 98 and
99, out of the way of the next flow. `sources.parse_euro_flash` reads both rows with their period;
`TradingViewForecast` is the expectation source for the two euro measures only, named
`tradingview_forecast` in `surprises.baseline`. `docs/schema.md` gets the new measures and source.

## What this does not do

No check of the flash actual: TradingView's is the only free record of the flash as printed (the
US flows check theirs against FRED). No country releases (Germany's, France's), no final HICP, no
Bund yield, no live euro calls.
