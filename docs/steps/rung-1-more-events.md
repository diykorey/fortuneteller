# Rung 1 — More events

> Rung 1 of the feature ladder in the [Roadmap](../roadmap.md); this document follows the step
> template in the [Legend](../legend.md). It runs the MVP's measurements
> ([step 3](step-3-raw-move.md), [step 4](step-4-surprise.md)) on two more events. Terms are in
> the [Glossary](../glossary.md); simplifications in [Precision](../precision.md).

## The goal

**In plain words:** does what we measured for CPI also hold for the monthly jobs report and for
Fed rate decisions? And was step 3's CPI answer distorted by those days?

The [MVP](../mvp-results.md) found that CPI moves the 10-year yield, the dollar and VIX, and that
the 10-year yield's move follows the CPI surprise, weakly. That is one event. This rung asks
whether the method finds anything for two others, and gives step 3 the cleaner baseline it
deferred: "ordinary days" without jobs-report and Fed days, which are not ordinary.

At the end: `event_instances` holds NFP releases and FOMC decisions next to CPI, `raw-move` gives
a step 3 verdict for each event, CPI's step 3 verdict is re-measured against the clean baseline,
and `surprise` gives NFP a step 4 verdict. The Fed gets no step 4: see the obstacles.

## The way to reach it

**The keys were built for one event.** `event_id` is CPI's reference month (`YYYYMM`), unique only
within CPI, and `obs_id` depends on the order of the instrument table. A second event type would
collide silently. So keys come first: an event is its type code and its date, and an observation
is its event and instrument.

**NFP revises the previous months in every release.** CPI's last month changes once a year (the
January fix); payrolls' changes every month, so "the change first published" needs the previous
month as it stood on each release day. FRED returns exactly that in one request: its
new-and-revised view (`output_type=3`) has one column per release day, holding the new month and
the months revised that day. August 2022 read this way gives +315k, the figure BLS printed.

**The Fed's decisions are not a FRED series.** Their dates come from the Fed's meeting calendars:
one page per year for 1994–2020, one current page from 2021. They start in February 1994, the
first decision announced on the day; before that, markets inferred decisions. A change in the
target rate (FRED `DFEDTAR`, then `DFEDTARU`) must fall on a listed decision day, which catches a
missed meeting, including the unscheduled ones (2001, 2008, 2020).

**There is no free history of what the market expected from the Fed.** Fed funds futures, the
standard source, are paid. So the Fed gets step 3 only; its surprise is in
[Precision](../precision.md).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Generic keys: `event_id` = type code × 10⁸ + release date (CPI 2022-09-13 → `120220913`); `observations` keyed by (`event_id`, `instrument`); `cpi_surprises` becomes `surprises`~~ **done** | Fact tables reloaded under the new keys; `raw-move` and `surprise` print the CPI numbers unchanged |
| 2 | NFP releases into `event_instances` (`NFP / labor data`, 08:30 New York) | Weekend guard; dates checked against BLS's Employment Situation archive from 1994; 2026-10 count recorded |
| 3 | `raw-move` takes an event (`cpi`, `nfp`, `fomc`) | NFP's step 3 verdict printed |
| 4 | FOMC decisions into `event_instances` (`Central-bank decision`, `United States`, 14:00 New York; unscheduled ones `scheduled = false`) | Every target-rate change since 1994 falls on a listed decision; FOMC's step 3 verdict printed |
| 5 | Clean baseline: "ordinary days" exclude every stored event's reaction day | CPI's step 3 re-run; old and new verdicts recorded side by side |
| 6 | NFP surprise: first-published monthly payroll change against its 12-month trend, into `surprises`; `surprise` takes an event | August 2022 reads +315k; NFP's step 4 verdict printed |
| 7 | Results here, and a rung 1 section in [`mvp-results.md`](../mvp-results.md) | Says, per event, whether it moves the five markets and (NFP) whether the move follows the surprise |

## How you know it is right

- **CPI unchanged by the new keys.** After step 1, `raw-move` and `surprise` print CPI's numbers
  exactly as before; only the ids differ.
- **NFP's actual is the published one.** August 2022 first published: +315k. A sample of first
  prints checked against BLS's releases, as CPI's were.
- **No missed Fed decision.** Every target-rate change since February 1994 lands on a decision day
  in the calendar; a change with no decision means a missing meeting.
- **Same rules as the MVP.** Step 3's (ratio ≥ 1.10, p < 0.01) and step 4's (p < 0.01, hit rate
  ≥ 60%) bars are unchanged, so results compare across events.

## What this rung does not do

No Fed surprise. No consensus forecasts, no intraday prices (option 2 in
[`mvp-results.md`](../mvp-results.md)). No other event types or central banks. No prediction
(rung 2).

## Decisions

| Decision | Chosen | Turned down | Why |
| --- | --- | --- | --- |
| Fed surprise | Out of scope: step 3 only | A proxy from the day's own move | The only free proxy is the market's reaction itself, which would measure the move against itself |
| Event key | Type code × 10⁸ + release date: `1` CPI, `2` NFP, `3` US central-bank decision | A hash of type and detail | Readable, sortable, unique per type and day |
| Order | Keys, NFP, FOMC, clean baseline, NFP surprise | FOMC first | NFP reuses the most CPI code |
| Ordinary days | Days with no stored event's reaction, for every event | A separate baseline per event | One rule; each event's baseline excludes the others |
| NFP surprise measure | Monthly payroll change, thousands, against its 12-month trend | Unemployment rate | The payroll number is the headline the market trades first |
| NFP expected direction of a strong print | UST 10Y up, DXY up; S&P 500, VIX, gold two-sided | A sign for every instrument | "Good news is bad news" makes equities' sign regime-dependent; only rates and the dollar have an agreed one |
| NFP hit-rate cut-off | \|surprise\| ≥ 50k | 0.1 pp, as CPI | Payroll surprises are in thousands; 50k is about half a typical one |

## Technical details

**Reloading.** Step 1 changes keys in three fact tables, and `init` does not alter existing
tables. So an existing database is deleted and rebuilt: `init`, then `load-releases`,
`load-prices` and `load-surprises` (about a minute; plus `seed` for the reference tables). Every
table is refilled from its source, so nothing is lost.

**NFP source.** FRED `PAYEMS`, `output_type=3`, full real-time range, one request: one column per
release day (`PAYEMS_YYYYMMDD`). For each release day, the first-published change is the newest
month minus the previous month in that same column (or, if not revised that day, its latest earlier
value). The release date is the column's date.

**Fed source.** `https://www.federalreserve.gov/monetarypolicy/fomchistorical<year>.htm` for
1994–2020 and `…/fomccalendars.htm` from 2021. Each decision's date is the meeting's last day.
Cross-check: FRED `DFEDTAR` (to 2008-12-15), `DFEDTARU` (from 2008-12-16).

**Code.** As before: fetching and parsing in `sources.py`, measurement in `study.py`, statistics
in `stats.py`, commands in `__main__.py`. Event-specific values (series ID, release time, expected
signs, cut-off) sit in one dictionary per event type in `study.py`; that is three concrete cases,
which rule 2 allows.

## Results

*Filled in by sub-step 7.*
