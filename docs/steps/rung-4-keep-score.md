# Rung 4 — keep score

> Rung 4 of the [Roadmap](../roadmap.md#after-the-mvp--the-feature-ladder)'s feature ladder. It
> keeps testing the [Legend](../legend.md)'s third claim, now on calls made live, and follows its
> step template. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when a release lands, write down every call before the market closes, and grade
it afterwards. No replay, however careful, can prove that it was not fitted after the fact; a log of
calls made before the outcome was known can.

[Rung 3](rung-3-confidence.md#results) and [step 4](step-4-more-events.md#results) left two calls
worth making (the dollar after a jobs report, the 10-year yield after retail sales) and no honest
probability, for want of calls. Live calls are the only calls that can be added from now on.

At the end: `predict --actual` writes each call to a committed log, and a `score` command grades the
logged calls once the day's closes are loaded, link by link, with rung 2's and rung 3's rules.

## What a logged call is

Every line `predict --actual` prints for a link becomes a row, as stated at the time and never
recomputed: the call with its probability and band, "too few calls so far", silent because the link
is closed, or no call because the surprise is under the step. Every flow with an expected value,
every link, including those whose confidence is not honest: logging only the two calls worth making
would bring back the selection rung 2 designed out.

`data/calls.csv`, one row per link per release:

| Column | Holds |
| --- | --- |
| `logged_at` | when the row was written, UTC |
| `flow`, `day` | the flow's CLI name and the release day, New York |
| `actual` | the typed-in actual |
| `instrument` | the link's market symbol |
| `outcome` | `call`, `too_few`, `silent` or `small` |
| `direction` | `up` or `down` for a call, else empty |
| `probability`, `band_low`, `band_high` | as stated, empty when there is none; the band in the market's unit as in `observations` (a fraction for prices, basis points for the yield) |

Rows are written only on the release day from 08:30 New York; a run at any other time is a what-if,
printed and not logged, so it cannot take the release's one entry. No consensus is stored: the repo
is public, and a row per release would grow into a copy of Nasdaq's calendar. The consensus is read
back from the calendar cache when grading.

## The way to reach it

**Trust is the obstacle.** The log is only worth more than the replay if it could not have been
edited after the close. The DuckDB file is local and ignored by git, so the log lives in the repo:

- **The witness is GitHub.** On each release day the log's new rows go up as a pull request opened
  before the earliest close they are graded on (15:00 New York for the yield and the dollar). The
  pull request's time is GitHub's, not ours. It is merged after grading. Alternatives considered: a
  long-lived `calls` branch pushed per release (less ceremony, no review), an issue comment per call
  (no file to grade from), a local log only (no witness).
- **No backfill.** A release with no rows is listed as missed by `score`. A missed release costs
  calls; a backfilled one would cost the log its point.
- **The actual is typed by hand** on release morning; fetching it is rung 5. A typo would be graded
  as a call on a different surprise, so `score` checks each row's actual against FRED's first print.

## Shared days

The next release is not yet in `event_instances`, so `study.shared_days` cannot see it. For a flow
whose surprise rule leaves shared days out (retail sales, core PCE, GDP), `predict --actual` reads
that day on TradingView's calendar and if another flow's row or the Fed's decision is there logs
every link as `silent` with the reason printed. Graded like the replay, a retail sales call on a CPI
day would be graded on CPI. TradingView's, not Nasdaq's: Nasdaq names all three GDP estimates `GDP`,
and only the advance estimate is a flow's release. From 2014 to September 2026 TradingView gives
the replay's shared days on all 355 of the three flows' release days, Nasdaq on 339.

## The rule, fixed before any live call is graded

- **A call counts** if it was logged after the release time and before its market's close that day
  (from [Precision](../precision.md): S&P 500 16:00, yield and dollar 15:00, gold 13:30, VIX 16:15,
  New York) and its actual matches FRED's first print to the published decimal. Otherwise it is
  **void**: listed, not graded.
- **Right or wrong** as in rung 2: the day's move closed strictly the called way. **In band** as in
  rung 3.
- **Per link:** rung 2's verdict (at least 60% right on at least 30 calls, binomial p < 0.01) and
  rung 3's confidence checks on the calls that carry a probability, with no change to either.
- **Against the replay:** each link's live record beside its replayed record, a measurement only.

**Expected outcome, written down first.** Since 2023 the replay made about 7 calls a year on each
jobs-report link, 5 on retail sales' yield and 2 to 3 on CPI's dollar. At that rate no link reaches
30 live calls before 2030. This rung delivers the log and its grading; its verdicts read "too few"
for years, and that is the expected result, not a failure.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`predict --actual` appends its rows to `data/calls.csv`; shared days logged `silent`; the unused `models.Prediction` removed~~ **done** | A test types an actual and finds a row per link with the printed numbers; a planted shared day logs every link `silent`; a second run on the same day refuses rather than adding rows |
| 2 | `score`: each row graded or void, missed releases listed, per-link record and rung 3's checks beside the replay's | Planted rows: one logged after the close is void, one with a mistyped actual is void and named, a release with no rows is missed, the rest graded |
| 3 | The first live releases logged and graded; Results here and in [`mvp-results.md`](../mvp-results.md) | At least one release's rows merged after a pull request opened before its close, and graded by `score` |

## What this step does not do

No fetching of the actual (rung 5), no alerts (rung 6), no new links, rules or markets. No
`predictions` table: the log is the record. No pooling of links into one verdict.

## Technical details

The log is written and read with `csv` from the standard library, at `settings.calls_path`
(`data/calls.csv`, like the other paths relative to the working directory: run from the main
checkout). `score` lives in `__main__.py`; grading reuses `study.grade` and
`study.grade_confidence` on `study.Prediction`s built from the rows and `observations`.
