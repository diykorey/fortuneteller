# Jobless claims

> Step 6 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-23 with the
> [plan update](../legend.md#the-target): the one event that beats the sample wall. Terms are in
> the [Glossary](../glossary.md).

## The goal

**In plain words:** does the weekly claims report move markets, does the move follow its surprise,
and can the morning job call it every Thursday?

Every event so far comes out once a month or less: a link gets twelve calls a year, and rung 3's
honesty bar needs thirty with a probability. Initial jobless claims come out every Thursday at
08:30 New York, the release-day job's hour, with a forecast on both calendars. Measured 2026-10-26
on the cached calendars: TradingView lists 708 releases from 2013-03-07, 702 with a forecast, 594
on a Thursday at 08:30 (23 on a Wednesday before a holiday, 89 stamped 09:30); Nasdaq lists the
same row with a consensus on every cached Thursday since 2008. The forecast misses the print by
8k at the median; 70% of misses are 5k or more.

At the end: claims loaded as an event flow with its surprise, run through rung 1 and step 4 for
all seven markets, and logged live by the morning job each Thursday like the monthly releases.

## The events

- **Source:** TradingView's US calendar, the row `Initial Jobless Claims`, in thousands, from the
  quarters already cached; the actual as TradingView prints it, the week's end as its period.
- **Nasdaq's consensus** as the baseline, TradingView's forecast where Nasdaq has none, as for
  every 08:30 US release ([consensus fallback](consensus-fallback.md)): claims come out at the hour
  `live` already runs, which is what kept ISM on TradingView alone. Nasdaq is a day per request:
  about 500 Thursdays are not cached yet and are fetched once, by hand, before the first evening run.
- **The first print checked** against FRED's `ICSA` as published on each release day, on the last
  26 weeks, the way rung 5 checked TradingView's CPI against BLS.
- **Time:** the calendar's own; 08:30 New York, before every close.
- **Origin:** `United States`, a new seed event type `Jobless claims`.
- **Measure:** `initial_claims`, the level in thousands.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** ratio ≥ 1.10 and p < 0.01 for every market.
- **The surprise: actual minus Nasdaq's consensus**, noticeable from 5k, about two thirds of the
  median miss as [more events](step-4-more-events.md) set its thresholds. No 12-month trend.
- **Expected signs for more claims** (weaker hiring, so the jobs report's signs reversed): the yield
  and the dollar index down; the S&P 500, gold, VIX, the DAX and the Euro Stoxx 50 none.
- **A lesser release.** Claims land on a fifth of all trading days (702 of 3,428 since 2013) and
  on 240 of them another stored release lands too (109 of the ECB's 115 decisions, 39 CPIs, 38 core
  PCEs, 36 retail sales, 28 GDPs). So, unlike every flow before it: a claims day is **no other
  flow's shared day and no other flow's busy day**; the others' tables, ordinary days and live
  calls do not change at all. Claims' **own tables, both tests, keep only its lone days** (462 as
  of 2026-10-26): a claims day with another release says nothing about claims.
- **Live every Thursday.** `live` treats claims as it treats CPI: the actual from TradingView,
  the consensus checked against TradingView's forecast (5k apart at most), a row per link, logged
  once, graded by the evening score. A Thursday that also holds another 08:30 release is silent by
  the rule above. `missed` counts claims from the first Thursday after the flow lands, not from
  2026-10-13.
- **Expected outcome, written down first:** no market reaches the bar on lone claims days, the
  yield's ratio the largest; the yield follows the surprise, short of *tracks* on the hit rate; the
  dollar unclear; the rest nothing; no link holds walk-forward at first, so the first Thursdays log
  silent rows; no other flow's row or verdict changes. As context, not a verdict: CPI's and the
  jobs report's yield ratios with claims days taken out of ordinary days move by under 0.02.

## Open, to decide before step 1

**Who merges the silent Thursdays.** Each release day the morning job opens a pull request with
the day's rows, and the evening job loads nothing while one is open. Claims add about fifty a
year, most holding two silent rows until a link opens. Either the user merges one a week, or the
job merges a pull request whose rows are all silent itself: a dated amendment to the release-day
job's *it opens, never merges*, since a silent row claims nothing. Proposed: the job merges them.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The claims flow: events and actuals from TradingView, Nasdaq's consensus with TradingView's forecast as fallback, the lesser-release rule, `live` on Thursdays, the seed type, the Nasdaq days fetched by hand | A test's calendar quarter stores a Thursday release at 08:30 New York with its surprise, its period the week's end; `live` on a Thursday asks for claims and logs a row per link; TradingView's actual equals FRED's first print on the last 26 weeks; every other flow's stored rows, verdicts and `live` lines identical before and after |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Seven verdicts on both tests on lone days, the walk-forward records, the context check, against the expected outcome |
| 3 | The first Thursday unattended | The morning job logs claims' rows and opens their pull request with no one there; the evening grades them |

## Technical details

A `TradingViewFlow` instance, type code 10, cli `claims`, label `CLM`, unit thousands, with the
period kept to the day for a weekly row (`detail` the week's end, `YYYY-MM-DD`). `initial_claims`
goes into both `TRADINGVIEW_ROWS` (the events, the forecast) and `CONSENSUS_ROWS` (Nasdaq's
consensus, `live`, the actual's check), decimals 0, gap 5. One flag on the flow, `lesser`, read in
three places: `shared_days` and `other_releases` skip a lesser flow's days for the others, and
`measure_raw_moves` keeps a lesser flow out of the busy set and its own event days to its lone
days. The log's start day moves from one constant to the flow. `docs/schema.md` gets the measure
and the type.

## What this does not do

No continuing claims, no four-week average, no claims before 2013, no weekly flow for anything
else yet.
