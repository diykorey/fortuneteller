# A free consensus, as context

> Step 2 of the [Roadmap](../roadmap.md#next-steps-in-order)'s next steps, as chosen on 2026-10-09:
> free sources only, shown as context. Paid consensus and intraday prices are deferred, not dropped.
> Follows the step template in the [Legend](../legend.md); one expectation source, as in
> [Extending](../extending.md).

## The goal

**In plain words:** does the market follow the surprise better when "expected" is what forecasters
published before the release, rather than our trend, nowcast or model?

The [jobs-report forecast](nfp-forecast.md#results) found the yield's and the dollar's links pass
since 2014 against both the trend and a model. A published forecast is the expected value traders
actually saw. The only free history of it found is a community copy of Forex Factory's calendar.

At the end: an `ff_forecast` expectation source for core CPI, headline CPI and payrolls, its
surprises in `surprises`, and `surprise` reports judging it beside the trend on the same reports.

## The source

[`Tropstan/Forex_Factory_Calendar`](https://huggingface.co/datasets/Tropstan/Forex_Factory_Calendar)
on HuggingFace: one CSV of 83,427 calendar rows, January 2007 to April 2025, with `Actual`,
`Forecast` and `Previous`. It was scraped from Forex Factory and is marked for research and
educational use; the repository is public, so the file is downloaded at load time, pinned to
commit `501bd289` and checked against its SHA-256 (`f4e92bca…`), never committed.

Checked 2026-10-09 against the stored releases: 219 `Core CPI m/m`, 219 `CPI m/m` and 220
`Non-Farm Employment Change` rows, all with a forecast; every one falls on a stored release day,
and its `Actual` matches our first print (CPI to the published 0.1%, payrolls to the thousand),
except April 2020: −20,537k there, −20,500k here.

Nothing in the file says how Forex Factory builds its forecast column, so the baseline is named
after its source, not called "consensus".

## The way to reach it

- **Dates only.** Timestamps are Tehran time and some are midnight placeholders, so a row matches
  the release whose New York date equals the date as written.
- **Refuse, don't guess.** A row matching no stored release, a value that will not parse (`K`, `M`,
  `%`), or an `Actual` off our first print beyond rounding refuses the load, naming it. April 2020
  is the one named exception.
- **Known the evening before.** The file does not record when each forecast was final. Each counts
  as known at the end of the New York day before its release; this is an assumption the shared
  check cannot test.
- **The flow's actual.** Surprises use our first print, as every other source does. CPI forecasts
  are rounded to 0.1%, our actuals are not, which adds noise near the 0.1pp cut-off.

## The rule, fixed before any number is run

- `ff_forecast` joins CPI's and NFP's rules as context; every official verdict stays as it is.
- `compared` becomes a list of pairs, each judged on the reports both cover, with and without
  COVID: CPI (trend, ff_forecast) and (nowcast, ff_forecast); NFP (trend, payroll_model), as today,
  and (trend, ff_forecast).
- **Plausibility.** The forecast's mean absolute error against our first print, on the same reports
  as the trend and the model, is reported. If it is under half the model's, the forecast column
  likely holds post-release values; the step then reports that and draws no conclusion from it.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Fetch, verify and parse the file; match rows to stored releases with the refusals above | A row off any release, an unparseable value and a wrong actual are each refused in a test; the real file loads 658 rows |
| 2 | `ForexFactoryForecast` source; `compared` as pairs; both rules gain it | NFP's (trend, model) table byte-identical to `main`'s; CPI's official tables unchanged |
| 3 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says, per pair and with and without COVID, whether the yield and the dollar track better against the forecast |

## What this step does not do

No paid data, no intraday prices. No Kalshi: its markets start in 2022 (about 45 releases, too few
for p < 0.01), and its API does not answer from this network. No change to any official verdict.
No Fed: the file's `Federal Funds Rate` forecast is a level, not a surprise this project measures
yet.

## Technical details

Fetching in `sources.py` (download, hash check, CSV parse); matching and the source in
`expectations.py`; `SurpriseRule.compared` as pairs in `flows.py` and `study.side_by_side`. Baseline
`ff_forecast`, label "Forex Factory's forecast".

## Results

*Filled in by step 3.*
