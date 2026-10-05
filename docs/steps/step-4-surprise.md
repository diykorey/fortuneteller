# MVP step 4 — Surprise

> Step 4 of the four in the [Roadmap](../roadmap.md); this document follows the step template in the
> [Legend](../legend.md). Unfamiliar acronym or term? See the [Glossary](../glossary.md). What this
> step simplifies, and the more precise way, is in [Precision](../precision.md).

## The goal

**In plain words:** when CPI comes in hotter than expected, do markets move the way, and by the
amount, the surprise says they should?

Step 3 showed that the 10-year yield, the dollar and VIX move more on CPI days than on other days.
That says CPI matters. It does not say the move is forecastable: a market can jump on every
release in a direction nobody could call. This step tests the Legend's second must-be-true claim:
**the size of the move tracks the size of the surprise.** If it does, there is something to
predict, and the MVP is complete. If it does not, the event matters but not in a way this signal
can forecast, and the project rethinks the signal before building anything on it.

Two commands. `uv run fortuneteller load-surprises` stores, for every release, how far core and
headline CPI landed from two expected values. `uv run fortuneteller surprise` prints, for each
instrument and expected value, whether the move follows the surprise, how often its direction was
right, and the move per 0.1 pp of surprise. The step ends with
[`mvp-results.md`](../mvp-results.md): what the MVP set out to prove, what it found, and what next.

## The way to reach it

Three obstacles.

**There is no free history of what the market expected.** Economists' consensus is sold, not
published. So step 4 uses two expected values and compares them. The **12-month trend** of
first-published core m/m covers every release from 1998, but measures surprise against the trend,
not against the market. The **Cleveland Fed nowcast** is a model forecast close to what the market
saw, but starts in 2013 (about 155 releases). The plan was to read agreement between the two as
the strong result. Sub-step 4 found that **for core the nowcast is almost exactly the trend**
(median gap 0.003 pp, correlation 0.997): its information is oil and gasoline prices, which move
headline, not core. So no free expectation of core independent of its trend exists, and the
verdict is plainly "surprise against the trend". See [Decisions](#decisions).

**The number the market saw is not the number FRED stores today.** FRED's first-release series
gives each month's index level as first published, so m/m as first published is this month's
first level over last month's. That holds except in February, when BLS revises its seasonal
adjustment and last month's level moves the same day: January 2023 core reads 0.57% that way, but
was published as 0.41%. So for each February release, last month's level is fetched as it stood on
the release day.

**One month was never published.** The 2025 government shutdown left October 2025 without a CPI.
October and November 2025 therefore get no change and no surprise (November has no October to
compare with), and the 12-month trend averages the months that exist. November 2025 is the one
known exception to the check against Cleveland's "actual", which estimates it (−0.09%).

**Testing many things invites a lucky pass.** The rule, the measure (core decides, headline is
context) and each instrument's expected direction are fixed below, before any run.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`cpi_surprises` table in `schema.sql` and `docs/schema.md`~~ **done** | `init` creates it; the doc explains every column and value |
| 2 | ~~First-published m/m, core and headline: fetch `CPILFESL`, apply the February fix~~ **done** | Tests pass; live: core from 1997, headline from 1972; January 2023 core reads 0.41% |
| 3 | ~~Cleveland Fed nowcast: fetch, parse, keep the last value before each release~~ **done** | Tests pass; live: our m/m equals Cleveland's "actual" within 0.01 pp for every release since 2013 |
| 4 | ~~`load-surprises`: the 12-month trend, both expected values, stored in `cpi_surprises`~~ **done** | Re-running changes no count; the August 2022 core surprise is positive against both |
| 5 | `track_surprises`: rank correlation, permutation `p`, hit rate, slope, verdict | The synthetic checks pass; two runs give the same result |
| 6 | `uv run fortuneteller surprise` prints the table | The live run prints every instrument × expected value; an empty store gives a one-line error |
| 7 | Results here, and [`mvp-results.md`](../mvp-results.md) | Both answer: does the move follow the surprise, for which instruments, and what next? |

## How you know it is right

- **Our "actual" is the published one.** Since 2013, first-published m/m must equal the Cleveland
  Fed's "actual" within 0.01 pp, core and headline, every release. A miss means every surprise is
  wrong.
- **A known release.** August 2022 core (released 2022-09-13, the S&P 500's −4.3% day) must show a
  positive surprise against both expected values.
- **Same release, same day.** A core row's release date must equal the headline release it is
  stored against. Core and headline come out in one BLS release.
- **A planted relationship is found.** Synthetic moves built as 3 × surprise plus noise give
  *tracks*; the same moves shuffled across releases do not.
- **Repeatable.** Two runs print identical output; the random seed is fixed.

## What this step does not do

No prediction or warning (ladder rung 2). No survey consensus. No `surprise_sd`. No intraday
window. No conditioning on regime. No event beyond CPI. `event_instances.consensus` and
`.surprise` stay empty: they mean a forecasters' consensus, and neither expected value here is one.

## Decisions

| Decision | Chosen | Turned down | Why |
| --- | --- | --- | --- |
| Where "expected" comes from | Both: 12-month trend (all history) and Cleveland Fed nowcast (2013 on), side by side | Nowcast only; trend only | Agreement between the two is the strongest result free data allows; trend alone can mistake trend for surprise |
| How the two are read (decided 2026-10-05, after sub-step 4 found the core nowcast ≈ the trend, before any move was measured) | **Core against the 12-month trend decides** (from 1998, 342 releases). Core against the nowcast, and headline against both, are context without a verdict | Both core baselines as verdicts; headline against the nowcast as the verdict | For core the two baselines are nearly the same test, so a second core verdict adds no evidence. Headline against the nowcast is the one place the nowcast carries market-like information, so it is shown, but core stays the measure markets trade. Survey consensus remains the upgrade ([Precision](../precision.md)) |
| Which CPI number | Core decides the verdict; headline is context | Headline only; both as verdicts | Markets have traded core since the 2000s (August 2022: headline +0.06 pp, core hot); one verdict measure keeps the test count down |
| The computed baseline | Average of the previous 12 first-published core m/m | Last month's m/m; a fitted forecasting model (AR) | Stable and needs no model. **A fitted model would forecast better** and is listed in [Precision](../precision.md) |
| What "tracks" means | Rank correlation in the expected direction, p < 0.01, **and** hit rate ≥ 60% on surprises ≥ 0.1 pp; *unclear* if one; *doesn't* if neither | Regression slope and its p; hit rate alone | Ranks resist crash days; the hit rate is what a warning needs; both together means real and usable |
| Expected direction of a hot surprise | UST 10Y up, DXY up, VIX up, S&P 500 down; gold two-sided | Learning directions from the data | Fixed in advance, so the test cannot fit itself; gold has no agreed sign, so it can reach at most *unclear* |
| Where surprises live | New `cpi_surprises` table | `event_instances` columns | Four surprises per release (2 measures × 2 expected values); `event_instances` holds one, and its `consensus` means a survey |

## Technical details

**Sources.** FRED, the same request as step 1 with `series_id=CPILFESL`. For each February
release, one more FRED request: last month's observation with `realtime_start` and `realtime_end`
both set to the release date (about 30 for core, 54 for headline; FRED allows 120 a minute). The
Cleveland Fed's chart data,
`https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json`: one
record per reference month, with series `CPI Inflation`, `Core CPI Inflation`, `Actual CPI
Inflation` and `Actual Core CPI Inflation`, each a daily path in m/m percent. Unofficial like
Yahoo's: no key, may change shape, checked by the 0.01 pp test above.

**`cpi_surprises`** — key (`event_id`, `measure`, `baseline`):

| Column | Type | Value |
| --- | --- | --- |
| `event_id` | BIGINT | The `event_instances` row: the release |
| `measure` | TEXT | `core` or `headline` |
| `baseline` | TEXT | `trend_12m` or `nowcast` |
| `actual_mom` | DOUBLE | m/m change as first published, percent |
| `expected_mom` | DOUBLE | What that baseline expected, percent |
| `surprise` | DOUBLE | `actual_mom − expected_mom`, percentage points |

A release gets a `trend_12m` row once 12 earlier first-published m/m values exist, and a `nowcast`
row when Cleveland has a value before its release date.

**The measurement**, for each instrument, on core against the 12-month trend (the verdict), then
the same numbers without a verdict for core against the nowcast and headline against both:

- Pairs: each release's core surprise with its `observations.ret_1d`.
- Rank correlation: Spearman, times the expected sign, so positive means "as expected"; gold uses
  the absolute value.
- `p`: shuffle surprises across releases 10,000 times, fixed seed; `p = (1 + shuffles at least as
  strong) / 10,001`. One-sided, gold two-sided.
- Hit rate: among releases with |surprise| ≥ 0.1 pp, the share whose move had the expected sign,
  with that `n`. Gold: `—`.
- Slope: Theil–Sen, in bp (UST) or % per 0.1 pp of surprise. Reported, not judged.

**Output:**

```
core against the 12-month trend
instrument   n    expected  rank corr  p       hit rate (n)  per 0.1pp  verdict
UST10Y / ZN  nnn  up        x.xx       0.xxxx  xx% (nnn)     x.x bp     …
...
context, no verdict: core against the nowcast; headline against the trend; headline against the nowcast
instrument   measure   baseline   n    rank corr  p       hit rate (n)
...
tracks = corr as expected, p < 0.01, hit rate >= 60%; unclear = one of the two; doesn't = neither
```

**Reading the result:** *tracks* means the move follows the surprise against the trend. The
context rows say whether that holds since 2013 (core against the nowcast) and where a market-like
expectation exists (headline against the nowcast); they can qualify the verdict in Results, not
replace it.

**Code.** Functions in `study.py`, handlers in `__main__.py`, tests in
`tests/test_study_surprise.py`. No new dependency: Spearman, Theil–Sen and the permutation are a
few lines each.

## Results

*Filled in by step 4.7, from the live run.*
