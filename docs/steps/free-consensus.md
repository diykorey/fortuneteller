# A free consensus, as context

> Step 2 of the [Roadmap](../roadmap.md#next-steps-in-order)'s next steps, as chosen on 2026-10-09:
> free sources only, shown as context. Paid consensus and intraday prices are deferred, not dropped.
> Follows the step template in the [Legend](../legend.md); one expectation source, as in
> [Extending](../extending.md).

## The goal

**In plain words:** does the market follow the surprise better when "expected" is the consensus
published before the release, rather than our trend, nowcast or model?

The [jobs-report forecast](nfp-forecast.md#results) found the yield's and the dollar's links pass
since 2014 against both the trend and a model. The consensus is the expected value traders
actually saw.

At the end: a `nasdaq_consensus` expectation source for core CPI, headline CPI and payrolls, its
surprises in `surprises`, and `surprise` reports judging it beside the trend on the same reports.

## The source

**Nasdaq's economic calendar**, `api.nasdaq.com/api/calendar/economicevents?date=`: each day's
releases with actual, consensus and previous; no key, no stated terms. Chosen on 2026-10-09 from
the three free sources compared in [Data sources](../data-sources.md#which-free-consensus-is-best):
all three are equally accurate, and Nasdaq covers the most that is still updated, about 222
releases of each measure from early 2008 to today. **TradingView's calendar** (2013 on) checks it.

Two quirks, both handled: a request for day D returns day D − 1's releases, so a release is read
with D + 1; and the month-on-month and year-on-year rows share one name (`Core CPI`, `CPI`).

## The way to reach it

- **A local cache.** Nasdaq takes about 4 seconds a request and one request covers one day, so each
  release day's reply is kept under `data/cache/nasdaq/` (ignored by git, never committed) and
  fetched only once; past days do not change.
- **The right row.** Among the rows named `Core CPI`, `CPI` or `Nonfarm Payrolls` that carry a
  consensus on a release day, the one whose actual equals our first print, to the published
  rounding (0.1% for CPI, 1k for payrolls), is the release's. None or two such rows refuses the
  load, naming the day, except four named on 2026-10-09, which get no consensus: core CPI
  2008-10-16 (actual 0.4 there, 0.14 here) and payrolls 2020-05-08 (−20,537k there, −20,500k
  here) match none; headline CPI 2015-11-17 and 2020-07-14 match two, month-on-month and
  year-on-year being equal.
- **Checked against TradingView.** Where both have a forecast and they differ by more than 0.2pp
  or 25k, the release gets no consensus surprise and is named. On 2026-10-09 the largest gaps were
  0.3pp (core CPI, November 2014) and 12k; everything else was within 0.2pp and 12k.
- **Known the evening before.** Neither calendar records when a consensus was final. Each counts
  as known at the end of the New York day before its release; this is an assumption the shared
  check cannot test.
- **The flow's actual.** Surprises use our first print, as every other source does. Consensus is
  rounded to 0.1% for CPI, our actuals are not, which adds noise near the 0.1pp cut-off.

## The rule, fixed before any surprise is measured

- `nasdaq_consensus` joins CPI's and NFP's rules as context; every official verdict stays as it is.
- `compared` becomes a list of pairs, each judged on the reports both cover, with and without
  COVID: CPI (trend, nasdaq_consensus) and (nowcast, nasdaq_consensus); NFP (trend, payroll_model),
  as today, and (trend, nasdaq_consensus).
- **Plausibility.** If the consensus's mean miss against our first print were under half the
  payroll model's, it would likely hold post-release values. Measured in choosing the source: 71k
  against the model's 77k, so it passes.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Fetch with the cache, pick each release's row, check against TradingView, with the refusals above~~ **done** | No row, two rows, an unparseable value and a TradingView gap are each handled in a test; real data gives about 222 consensus values per measure |
| 2 | ~~`NasdaqConsensus` source; `compared` as pairs; both rules gain it~~ **done** | NFP's (trend, model) table byte-identical to `main`'s; CPI's official tables unchanged |
| 3 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says, per pair and with and without COVID, whether the yield and the dollar track better against the consensus |

**Step 1, checked 2026-10-09** (`expectations.fetch_calendars`, `match_consensus`; not yet a
source). On the stored releases: 220 core CPI, 219 headline CPI and 222 payroll consensus values,
February 2008 to October 2026. Five releases get none, exactly those named above: the four whose
row cannot be told, and core CPI 2014-11-20, 0.3pp off TradingView's. Nasdaq has no consensus
before 2008, so earlier days are not asked; TradingView answers `no_data` before 2013.

**Step 2, checked 2026-10-09.** `load-surprises` stores 661 consensus surprises (core 220,
headline 219, payrolls 222) and names the five releases left out. Against `main`: every official
verdict table, and NFP's trend-and-model tables, byte-identical; the context tables only widen
their baseline column; `event_instances`, `observations` and `daily_bars` identical row for row.

## What this step does not do

No paid data, no intraday prices. No Forex Factory copy: it adds only 2007, stops in April 2025 and
was scraped against its site's terms. No Kalshi: about 45 releases, too few for p < 0.01, and its
API does not answer from this network. No Fed: a consensus for a rate decision is a level, not a
surprise this project measures yet. No change to any official verdict.

## Technical details

Fetching in `sources.py` (the Nasdaq day request with its cache, the TradingView quarter request);
row choice, the check and the source in `expectations.py`; `SurpriseRule.compared` as pairs in
`flows.py` and `study.side_by_side`. Baseline `nasdaq_consensus`, label "Nasdaq's consensus".

## Results

*Filled in by step 3.*
