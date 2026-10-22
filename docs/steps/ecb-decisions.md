# Cross-country effects, part 2: ECB decisions

> The second slice of the [Roadmap](../roadmap.md#next-steps-in-order)'s step 4a, chosen 2026-10-22,
> after [part 1](cross-country.md) found Europe reacting to US news. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** does the European Central Bank's rate decision move markets, Europe's and New
York's, as the Fed's does?

Part 1 ran US events against European markets. This is the reverse direction and the project's
first event from outside the US: the ECB's Governing Council announcing its rates, eight times a
year (monthly until 2015).

At the end: ECB decisions loaded as an event flow and run through rung 1 (does it move?) for all
seven markets, beside the Fed's verdicts.

## The events

- **Source:** TradingView's calendar, `ECB Interest Rate Decision`, fetched a quarter at a time as
  for US releases. It lists every decision from 2013-04-04 (checked 2026-10-22: about 105); Nasdaq's
  goes back to 2008 but only one day per request, so it waits.
- **Time:** the announcement's own time from the calendar (13:45 Frankfurt until 2022, 14:15 since):
  before Frankfurt's 17:30 close and before New York opens, so every market reacts the same day.
- **Origin:** a new seed country, `Euro area`, the union whose central bank decides; event type
  `Central-bank decision`, as the Fed's.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** ratio ≥ 1.10 and p < 0.01 for every market.
- **No surprise test.** The calendar's forecast is the rate the market expected, and it equals the
  decision on almost every meeting; the count of meetings where it differs is printed, not judged.
  Like the Fed's, the ECB flow has no surprise rule, so `predict` makes no ECB calls.
- **Ordinary days lose ECB days.** As decided in [country-aware events](country-aware-events.md),
  part 2 settles the clean baseline: an ECB decision day is not an ordinary day for any market, as
  every stored event's is not. US verdicts move only by that; each changed one is reported.
- **Expected outcome, written down first:** the ECB moves the DAX, the Euro Stoxx 50 and the dollar
  index (the euro is over half of it); not the S&P 500, the 10-year yield, gold or VIX.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `Euro area` seed row; the ECB flow: decisions from TradingView with their time, `load-releases` stores them | A test's calendar quarter stores its decisions at their Frankfurt time; a quarter without one stores none; `raw-move --event ecb` prints seven verdicts |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Seven verdicts beside the Fed's, US verdicts before and after, against the expected outcome |

## What this does not do

No ECB surprise, press conference or speeches; no euro-area releases; no Bund yield; no decisions
before 2013.
