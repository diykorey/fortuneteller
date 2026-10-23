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
| 1 | ~~The flash flow: events and actuals from TradingView, the forecast as an expectation source, the rule above; `live` skips it~~ **done**; `load-releases` stored 143 flashes, 2014-11-28 to 2026-10-02, and `load-surprises` 124 core and 143 headline surprises. US outputs changed, by the rule above (*amended 2026-10-22*): see below | A test's calendar quarter stores a flash at its Frankfurt time with its core and headline surprises; `raw-move` and `surprise --event hicp` print seven verdicts; `live` and every US output unchanged |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | Seven verdicts on both tests, US verdicts before and after, against the expected outcome |

## Results

Measured 2026-10-22 (`raw-move`, `surprise` and `predict --event hicp`): 143 flash estimates,
2014-11 to 2026-10.

| Market | Does it move? ratio, p | Does it follow the core surprise? rank corr, p, hit rate |
| --- | --- | --- |
| S&P 500 | 1.41, 0.0007, **moves** | 0.04, 0.74, doesn't |
| 10-year yield | 1.03, 0.43, doesn't | 0.18, 0.13, doesn't |
| Dollar index | 1.13, 0.15, unclear | 0.07, 0.29, 57%, doesn't |
| Gold | 1.14, 0.12, unclear | 0.14, 0.26, doesn't |
| VIX | 1.44, 0.0003, **moves** | 0.10, 0.42, doesn't |
| DAX | 0.98, 0.58, doesn't | 0.21, 0.04, 62%, unclear |
| Euro Stoxx 50 | 0.90, 0.83, doesn't | 0.10, 0.21, 57%, doesn't |

The surprise test runs on 70 releases: 124 have a core forecast, and 64 share their day with a US
release or an ECB decision and are left out. Walk-forward, no link opens, so `predict` makes no
flash calls.

**Europe's stocks do not move on their own inflation news; New York's do.** The S&P 500 and VIX move
about 40% more on a flash day than on an ordinary one, mostly since 2020 (S&P 500 1.41 since 2020
against 1.07 before). On the 79 flash days with no other stored release they still move more (1.40
and 1.25) but fall short of the bar (p 0.012 and 0.048). The likely cause is not the flash: it often
falls on the month's first working day, the day of the US manufacturing survey (ISM), which is not a
stored event; untested. (*Amended 2026-10-23*, [the ISM survey](ism-manufacturing.md#results): not
often, 25 of 142 flash days and 17 of the 79; with ISM stored, the 62 left move 1.25 and 1.25: ISM
explains part.)

**Nothing follows the surprise.** The DAX comes nearest, the right way (a hotter print, a lower
DAX, 62% of noticeable surprises), short of p < 0.01; headline gives the same picture for both
indices (0.22 and 0.21, p 0.03). The dollar index, down on a hotter print by the rule, does not
follow it at all (0.07, headline −0.02).

**Against what was written down first.** *Moves the dollar index only:* wrong; the dollar index is
unclear, and the S&P 500 and VIX move. *The dollar index and the yield follow the core surprise:*
wrong, neither does. *Europe's stocks unclear:* right for the DAX; the Euro Stoxx 50 doesn't.

**What it means.** Unlike US CPI, whose surprise the yield tracks, the euro area's flash moves no
market by its surprise, at least on a daily close and against a forecast nobody can check. With
the ECB's decisions priced in (part 2), euro-area news reaches markets weakly at best; what moves
Europe is the US (part 1).

**US outputs after step 1** (*added 2026-10-22*). Unchanged was wrong: a flash day is now another
flow's release day for the US consensus flows too, as the shared-days rule says, and no longer an
ordinary day. CPI, jobs-report and Fed surprises and calls are unchanged. Left out as shared:
retail sales 47 (was 46), core PCE 55 (was 15: the flash often lands on its day), GDP 31 (was 27).
Two verdicts changed: GDP's dollar index against the surprise, unclear to *doesn't*; GDP's VIX on
release days, *doesn't* to unclear (ratio 1.10, p 0.19). Retail sales' yield still holds
walk-forward.

## Technical details

`HicpFlow` beside `EcbFlow`, type code 8, cli `hicp`. The test flows' codes 9 and 10 move to 98 and
99, out of the way of the next flow. `sources.parse_euro_flash` reads both rows with their period;
`TradingViewForecast` is the expectation source for the two euro measures only, named
`tradingview_forecast` in `surprises.baseline`. `docs/schema.md` gets the new measures and source.

## What this does not do

No check of the flash actual: TradingView's is the only free record of the flash as printed (the
US flows check theirs against FRED). No country releases (Germany's, France's), no final HICP, no
Bund yield, no live euro calls.
