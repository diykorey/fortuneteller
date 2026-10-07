# A free forecast of each jobs report

> The first of the next steps in the [Roadmap](../roadmap.md#next-steps-in-order); it follows the
> step template in the [Legend](../legend.md). Built on [event flows](event-flows.md) as one
> expectation source. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** would the jobs-report result change if "expected" were a real forecast instead
of a 12-month trend?

[Rung 1](rung-1-more-events.md#results) found that the 10-year yield and the dollar follow the
payroll surprise beyond doubt (p 0.0001), but go the expected way only 58% and 56% of the time,
under the 60% bar. The surprise is measured against the trend, which ignores everything the market
knew the week before: ADP's private-payroll report two days earlier, and the weekly jobless claims.
Economists' consensus uses both, but is paid. This step builds the closest free stand-in.

At the end: a `payroll_model` expectation source, its surprises next to the trend's in
`surprises`, and an answer, under a rule fixed here, to whether the yield's and the dollar's links
clear the bar against it.

## The way to reach it

**Only what was published before each report.** The forecast for a report uses ADP's change and
the claims as first printed, and a fit on earlier reports only, refitted before every report. Its
`known_at` is when its newest input came out, so the shared check in `build_surprises` refuses any
look-ahead.

**Two ADP series, with a gap.** FRED has ADP's first prints for its old method (`NPPTTL`, March 2011
to June 2022) and its new one (`ADPMNUSNERSA`, October 2022 on). ADP paused from June to August
2022, so three or four reports have no forecast. Both give the month's change in thousands, taken
as payrolls are: the month's first level minus the previous month's level as revised that day.

**COVID would swamp a least-squares fit.** April 2020's −20.5M print would dominate every later fit.
So March 2020 – April 2021 are left out of the fitting; their reports are still forecast and judged,
and every result is shown with and without them, as in rung 1.

## The model

Before each report, an ordinary least-squares fit on every earlier report that has all three inputs:

| Input | Series | Known |
| --- | --- | --- |
| ADP's change for the month, first print | `NPPTTL` to 2022-05, `ADPMNUSNERSA` from 2022-09 | two days before the report |
| The change in 4-week-average initial claims between the survey weeks (the week including the 12th) of the month and the month before, first prints | `IC4WSA` | the Thursday after each survey week |
| The 12-month trend of first-published payroll changes | `Trend12m` | at the previous report |

A forecast needs at least 36 earlier reports to fit on, so the first ones come in 2014: about 150
reports in all.

## The rule, fixed before any number is run

- The model's combination, payrolls against `payroll_model`, gets the same test as every other: rank
  correlation with the expected sign (yield and dollar up), p < 0.01 and hit rate ≥ 60% on
  surprises of at least 50k.
- It is judged on the reports it covers, and the trend is judged on **exactly the same reports**
  beside it, so the two are compared like for like.
- The trend keeps NFP's official verdict (681 reports, 1956 on). The model's verdict is reported as
  the answer to this step's question; making it official would be a separate decision.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Inputs: ADP's first-published monthly changes (both series) and the survey-week claims changes, from FRED~~ **done** | August 2022's gap is empty; a sample of ADP first prints matches ADP's releases |
| 2 | `stats.least_squares` and the `PayrollModel` source, refitted before each report | No forecast uses a report or input published at or after it (the shared check passes); a planted relationship is recovered |
| 3 | `payroll_model` in `EXPECTATION_SOURCES` and in NFP's rule as context; `surprise --event nfp` prints model and trend on the same reports | The comparison table printed; CPI's output unchanged |
| 4 | Results here and in [`mvp-results.md`](../mvp-results.md) | Says whether the yield's and the dollar's links clear the bar against the forecast, with and without COVID |

## How you know it is right

- **No look-ahead.** Every forecast's `known_at` is before its report, enforced by
  `build_surprises`, and a test plants an input dated after a report and expects a refusal.
- **The fit works.** On made-up data built from known coefficients, the refitted model recovers
  them.
- **The forecast is better than the trend.** Its mean absolute error against the first print should
  be clearly smaller than the trend's; if it is not, the model adds nothing and the result says so.
- **Nothing else changes.** CPI's reports and NFP's trend rows are byte-identical to `main`'s.

## What this step does not do

No paid data, no consensus, no intraday prices. No other event's forecast. No change to NFP's
official verdict. No tuning: the inputs, the 36-report minimum and the COVID window are fixed here.

**Inputs, checked 2026-10-07** (`expectations.load_model_inputs`). ADP: 185 months with a first
print in time, March 2011 to September 2026, none for June–August 2022. A first print comes 20–45
days after its month starts; anything FRED first shows later (history republished in 2011, 2022
and 2023) is not one, so a month counts only if first published within 50 days of its start.
Four first prints match ADP's own releases: April 2020 −20,236k, May 2022 +128k, September 2022
+208k (the relaunch), September 2025 −32k. Claims: a monthly change for 207 months from July 2009.

## Technical details

Fetching in `sources.py` (FRED first releases and vintages, as for payrolls). The source in
`expectations.py`; `least_squares` in `stats.py`, plain Python (normal equations, three inputs and
an intercept), no new dependency. Measure `payrolls`, unit thousands, baseline `payroll_model`.

## Results

*Filled in by step 4.*
