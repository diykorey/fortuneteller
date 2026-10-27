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
  of 2026-10-26 on the calendars; 450 once stored, *amended 2026-10-27*, the jobs report's, the
  Fed's, the flash's and ISM's Thursdays counted too): a claims day with another release says
  nothing about claims.
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

*Added 2026-10-27:* not decided as step 1 landed. The job opens, never merges, as before, and the
user merges each Thursday's pull request until it is.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The claims flow: events and actuals from TradingView, Nasdaq's consensus with TradingView's forecast as fallback, the lesser-release rule, `live` on Thursdays, the seed type, the Nasdaq days fetched by hand~~ **done** 2026-10-26: on a copy of the store, `load-releases` stored 706 reports, 2013-03-07 to 2026-10-22 (the seven weeks published at once on 2025-11-20 are one event, the newest week, as the jobs report's months are); `load-surprises` 704 surprises against TradingView's forecast and 701 against Nasdaq's consensus, 330 of them TradingView's forecast where Nasdaq had no row, 3 left out for the calendars disagreeing, 2025-11-20 without any, its forecasts being the older weeks'; 702 Nasdaq days fetched by hand; TradingView's actual equals FRED's first print on all 26 weeks; the nine other flows' page entries identical with and without claims | A test's calendar quarter stores a Thursday release at 08:30 New York with its surprise, its period the week's end; `live` on a Thursday asks for claims and logs a row per link; TradingView's actual equals FRED's first print on the last 26 weeks; every other flow's stored rows, verdicts and `live` lines identical before and after |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** 2026-10-27 | Seven verdicts on both tests on lone days, the walk-forward records, the context check, against the expected outcome |
| 3 | The first Thursday unattended | The morning job logs claims' rows and opens their pull request with no one there; the evening grades them |

## Results

Measured 2026-10-27 (`raw-move`, `surprise` and `predict --event claims` on a copy of the store):
706 reports, 2013-03 to 2026-10, 450 of them alone on their day. The 256 on a day with another
stored release are left out of both tests by the rule above: 16 more than the spec counted, the
jobs report's, the Fed's, the flash's and ISM's Thursdays too.

| Market | Does it move? ratio, p | Does it follow the surprise? rank corr, p, hit rate |
| --- | --- | --- |
| S&P 500 | 0.92, 0.90, doesn't | 0.02, 0.61, doesn't |
| 10-year yield | 1.03, 0.34, doesn't | 0.14, 0.0018, 56%, unclear |
| Dollar index | 1.08, 0.13, doesn't | 0.10, 0.021, 56%, doesn't |
| Gold | 1.10, 0.064, unclear | 0.08, 0.11, doesn't |
| VIX | 1.00, 0.54, doesn't | 0.05, 0.26, doesn't |
| DAX | 0.97, 0.67, doesn't | 0.03, 0.55, doesn't |
| Euro Stoxx 50 | 1.00, 0.53, doesn't | 0.01, 0.83, doesn't |

The surprise test runs on the 448 lone days with a consensus, 307 of them noticeable (5k or more).
A 5k surprise moves the yield 0.1 bp the expected way and the dollar index 0.01%. Against
TradingView's forecast the picture is the same (the yield 0.13, p 0.002, 56% of 310).

**Nothing moves.** On a lone claims day every market moves as on an ordinary day: the S&P 500 8%
less, the yield 3% more, gold 10% more (p 0.06, unclear by the ratio alone). The eras disagree,
without a verdict: before 2020 every market but gold moved less on lone claims days than on
ordinary ones; since 2020 all but VIX move more, the dollar index 27% on its 223 days, the DAX 21%,
the Euro Stoxx 50 16%.

**The yield leans the right way, faintly.** More claims than expected, a lower yield: the rank
correlation is small (0.14) but on 448 days unlikely to be chance (p 0.002); the direction is right
on 56% of the 307 noticeable surprises, short of the 60% bar. The dollar leans the same way, short
of both bars. The median miss is 8k on a level near 220k: the report rarely tells the market
anything it did not expect.

**Walk-forward, no link opens.** No link reaches the surprise test's bars at any point of the
replay, so `predict` makes no prediction and every Thursday's rows are silent until one does.

**Other flows unchanged, by the rule.** The nine other flows' scoreboard entries are identical with
and without claims, cell for cell (step 1). As context, not a verdict: with claims days taken out of
ordinary days instead, CPI's and the jobs report's yield ratios stay 1.33 and 1.67 to the third
decimal; the largest move of any ratio is the Euro Stoxx 50's on jobs-report days, 1.41 to 1.40, and
CPI's S&P 500 would slip from 1.101 to 1.097, back under the ratio bar. Ordinary days would lose
450 of about 11,700.

**Against what was written down first.** *No market reaches the bar, the yield's ratio the largest:*
right that none does; the largest is gold's (1.10), the yield's third (1.03). *The yield follows the
surprise, short of* tracks *on the hit rate:* right. *The dollar unclear:* wrong, it falls short of
both bars (p 0.02). *The rest nothing:* right. *No link holds walk-forward at first:* right; none
opens. *No other flow's row or verdict changes:* right. *CPI's and the jobs report's yield ratios
move by under 0.02:* right, by under 0.001.

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
