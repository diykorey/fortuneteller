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
| 2 | ~~NFP releases into `event_instances` (`NFP / labor data`, 08:30 New York)~~ **done** | Weekend guard; dates checked against BLS's Employment Situation archive from 1994; 2026-10 count recorded |
| 3 | ~~`raw-move` takes an event (`cpi`, `nfp`, `fomc`)~~ **done** | NFP's step 3 verdict printed |
| 4 | ~~FOMC decisions into `event_instances` (`Central-bank decision`, `United States`, 14:00 New York; unscheduled ones `scheduled = false`)~~ **done** | Every target-rate change since 1994 falls on a listed decision; FOMC's step 3 verdict printed |
| 5 | ~~Reaction close by event time: an event after an instrument's daily close reacts at its next close; each Fed decision at its announced time~~ **done** | Gold's Fed-day move measured after the decision; CPI and NFP output unchanged |
| 6 | ~~Clean baseline: "ordinary days" exclude every stored event's reaction day~~ **done** | CPI's step 3 re-run; old and new verdicts recorded side by side |
| 7 | ~~NFP surprise: first-published monthly payroll change against its 12-month trend, into `surprises`; `surprise` takes an event~~ **done** | August 2022 reads +315k; NFP's step 4 verdict printed |
| 8 | ~~Results here, and a rung 1 section in [`mvp-results.md`](../mvp-results.md)~~ **done** | Says, per event, whether it moves the five markets and (NFP) whether the move follows the surprise |

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
| Order | Keys, NFP, FOMC, close timing, clean baseline, NFP surprise | FOMC first | NFP reuses the most CPI code; close timing changes the reaction days the clean baseline removes |
| Ordinary days | Days with no stored event's reaction, for every event | A separate baseline per event | One rule; each event's baseline excludes the others |
| NFP surprise measure | Monthly payroll change, thousands, against its 12-month trend | Unemployment rate | The payroll number is the headline the market trades first |
| NFP expected direction of a strong print | UST 10Y up, DXY up; S&P 500, VIX, gold two-sided | A sign for every instrument | "Good news is bad news" makes equities' sign regime-dependent; only rates and the dollar have an agreed one |
| NFP hit-rate cut-off | \|surprise\| ≥ 50k | 0.1 pp, as CPI | Payroll surprises are in thousands; 50k is about half a typical one |

## Technical details

**Reloading.** Step 1 changes keys in three fact tables, and `init` does not alter existing
tables. So an existing database is deleted and rebuilt: `init`, then `load-releases`,
`load-prices` and `load-surprises` (about a minute; plus `seed` for the reference tables). Every
table is refilled from its source, so nothing is lost.

**NFP release dates, checked 2026-10-05.** All 392 release dates from January 1994 match BLS's
Employment Situation archive. Two looked wrong at first, June 1997 and December 1999, but BLS's
own release texts ("embargoed until 8:30 A.M., Thursday, July 3, 1997"; "Friday, January 7,
2000") confirm FRED; the archive list's labels for those two are wrong. Dates before 1994 are not
checked. October 2025 was first published with November on 2025-12-16, after the shutdown; that
release day is stored once, as November (`study.one_release_per_day`).

**NFP source.** FRED `PAYEMS`, `output_type=3`, full real-time range, one request: one column per
release day (`PAYEMS_YYYYMMDD`). For each release day, the first-published change is the newest
month minus the previous month in that same column (or, if not revised that day, its latest earlier
value). The release date is the column's date.

**Fed source.** `https://www.federalreserve.gov/monetarypolicy/fomchistorical<year>.htm` for
1994–2020 and `…/fomccalendars.htm` from 2021 (`sources.parse_fomc_history`,
`parse_fomc_calendar`). The rule:

- A meeting or conference call with a statement is a decision on the statement's date: the day the
  market heard it (the call of 2008-01-21 was announced on the 22nd).
- A scheduled meeting with no statement is a decision on its last day, but only before May 1999:
  until then the Fed announced only changes, and the market watched for one. Later meetings without
  a statement are not decisions (2003-09-15 was a briefing).
- Cancelled meetings, notation votes and calls without a statement are not decisions.
- A meeting is unscheduled (`scheduled = false`) if it is a call or marked unscheduled.

Cross-check: FRED `DFEDTAR` (to 2008-12-15), `DFEDTARU` (from 2008-12-16). Every change in the
target must fall on a decision day or up to 3 days after it (since 2017 a new target takes effect
the next day); `load-releases` refuses to store the decisions otherwise, naming the day.

**Fed decisions, loaded 2026-10-05.** 275 decisions, 1994-02-04 … 2026-09-16, 14 unscheduled.
Every target change, 92 of them, falls on a decision. 2001-09-17 has no move: markets were shut
11–14 September, so no close lies within 4 days before it. The cross-check catches only a missing
decision that changed the rate; a year with no change (2021) is covered only by the calendar page,
so if the Fed moves 2021 to its year pages, `FED_HISTORY_YEARS` must grow with it.

**Gold closes before the Fed decides.** `GC=F`'s daily close is the COMEX settlement, 13:30 New
York; decisions come at 14:00. So gold's "Fed-day" move ends before the decision: its ratio is 0.79
on the day and 1.80 on the next. Gold's Fed verdict from sub-step 4 (*doesn't*, ratio 0.78) is
therefore not a finding; sub-step 5 fixes the pairing. The dollar's next-day ratio (1.46, against
1.15 on the day) suggests its Yahoo close time is worth checking in the same sub-step; the others
close after 14:00.

**Close timing, 2026-10-06.** Each instrument's close is the intraday time its Yahoo close
matches (September 2026 data): S&P 500 16:00, yield and dollar 15:00, gold 13:30, VIX 16:15. Each
Fed decision carries the time its statement came out:

- 1994–2004: Gürkaynak, Sack & Swanson's appendix (2005).
- Mid-2006–2015: the minutes ("to be released at").
- Since 2016: the statements themselves.
- 2008-03-11: the 2008-03-10 call ("8:30 a.m. … tomorrow").

The statements came at 14:15 until 2013-01-30 and at 14:00 from 2013-03-20, with 25 exceptions in
`study.FOMC_ANNOUNCED_AT`. Those include the 12:30 statements on the 2011–2012 press-conference
days, and 1998-10-15 at 15:15, after the yield's and the dollar's close.

Gold's Fed ratio is now 1.79 (*moves*, p 0.0001), up from 0.78. CPI, NFP and `surprise` are
unchanged: `main`'s code gives the same output on the same database.

Two cells remain open. In 1990–2007 the yield's and the dollar's next-day ratios beat their Fed-day
ratios; see [Precision](../precision.md).

Five of the 14 unscheduled decisions are liquidity or implementation statements, not rate moves:
2007-08-10, 2007-08-17, 2008-03-11, 2010-05-09 and 2019-10-11.

**Clean baseline, 2026-10-06.** A day is ordinary only if no stored event, of any type, reacted on
it at that instrument's close (`study.measure_raw_moves`). A day that is two events' reaction day
counts as an event day for both: 20 CPI days are also Fed days, none is also a jobs-report day.
Old (all other days) and new (ordinary days), on the same data:

| Event | Instrument | Old ratio, p | New ratio, p | Verdict |
| --- | --- | --- | --- | --- |
| CPI | S&P 500 | 1.07, 0.0999 | 1.09, 0.0624 | doesn't → doesn't |
| CPI | UST 10Y | 1.25, 0.0007 | 1.33, 0.0002 | moves → moves |
| CPI | DXY | 1.16, 0.0037 | 1.18, 0.0010 | moves → moves |
| CPI | Gold | 1.02, 0.4151 | 1.04, 0.2722 | doesn't → doesn't |
| CPI | VIX | 1.19, 0.0020 | 1.22, 0.0006 | moves → moves |
| NFP | all five | 1.18–1.61 | 1.19–1.67 | moves → moves |
| Fed | S&P 500 | 1.28, 0.0010 | 1.30, 0.0010 | moves → moves |
| Fed | UST 10Y | 1.16, 0.1110 | 1.23, 0.0316 | unclear → unclear |
| Fed | DXY | 1.20, 0.0178 | 1.22, 0.0096 | unclear → **moves**, just under the bar |
| Fed | Gold | 1.79, 0.0001 | 1.81, 0.0001 | moves → moves |
| Fed | VIX | 1.22, 0.0034 | 1.25, 0.0020 | moves → moves |

As [Precision](../precision.md) predicted, removing noisy days only raises the ratios. The one flip,
the Fed's dollar, sits at p 0.0096 against a 0.01 bar: a borderline result, not a strong one.

**NFP surprise, 2026-10-06.** The changes are built from FRED `PAYEMS`, `output_type=3`
(`sources.parse_vintages`, `study.first_published_payroll_changes`). Each month's change is its
first level minus the previous month's level as it stood that day. Checks:

- **All 856 stored jobs reports** match FRED's revision history on release day and first level.
  `load-surprises` refuses to store anything otherwise (`study.payroll_level_mismatches`).
- **Five first prints agree with BLS's own release texts:** August 2022 +315k, April 2020 −20.5M,
  September 2008 −159k, November 2025 +64k, June 1997 +217k.
- **CPI's `surprise` output is unchanged**, compared with `main` on the same database.

844 payroll surprises, 1956-06-08 … 2026-10-02: every report but the first twelve.

The trend now counts only months published *before* the release day. October 2025 came out with
November on 2025-12-16, so it is not in November's trend. CPI's trends are unchanged by this.

October 2025 has no surprise of its own: its release day is stored as November. Five of the 14
unscheduled Fed decisions are not rate moves either, and the results say so.

NFP's step 4 verdict, payrolls against the trend:

| Instrument | Expected | Rank corr | p | Hit rate (n) | Per 50k | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| UST 10Y | up | 0.26 | 0.0001 | 58% (466) | 0.6 bp | unclear |
| DXY | up | 0.16 | 0.0001 | 56% (457) | 0.02% | unclear |
| Gold | either | 0.16 | 0.0036 | — | −0.04% | unclear |
| S&P 500 | either | 0.01 | 0.71 | — | 0.00% | doesn't |
| VIX | either | 0.05 | 0.28 | — | −0.07% | doesn't |

The yield and the dollar follow the payroll surprise beyond doubt: p 0.0001, over 669–681
releases. But they go the expected way only 58% and 56% of the time, short of the 60% bar. Gold,
the S&P 500 and VIX have no agreed sign, so no hit rate, and *unclear* is the best they can reach.

**Without March 2020 – April 2021**, whose surprises the −20.5M April 2020 print distorts for a year,
every verdict is the same: yield 0.25 and 58%, dollar 0.17 and 56%, gold p 0.0082.

**Code.** As before: fetching and parsing in `sources.py`, measurement in `study.py`, statistics
in `stats.py`, commands in `__main__.py`. Event-specific values (series ID, release time, expected
signs, cut-off) sit in one dictionary per event type in `study.py`; that is three concrete cases,
which rule 2 allows.

## Results

Measured 2026-10-06, all on one database, with the rules the MVP fixed in advance (step 3:
ratio ≥ 1.10 and p < 0.01; step 4: p < 0.01 and hit rate ≥ 60%). Ordinary days exclude every
event's reaction day; each move starts at the last close before the event.

**Does the event move the market more than an ordinary day?** Ratio of medians, verdict.

| Market | CPI (649 releases) | Jobs report (681) | Fed decision (274) |
| --- | --- | --- | --- |
| 10-year yield | 1.33 moves | 1.67 moves | 1.23 unclear (p 0.03) |
| Dollar index | 1.18 moves | 1.25 moves | 1.22 moves (p 0.0096, borderline) |
| VIX | 1.22 moves | 1.31 moves | 1.25 moves |
| S&P 500 | 1.09 doesn't | 1.19 moves | 1.30 moves |
| Gold | 1.04 doesn't | 1.27 moves | 1.81 moves |

**Does the move follow the surprise?** Against the 12-month trend; no Fed surprise.

| Market | CPI (core) | Jobs report (payrolls) |
| --- | --- | --- |
| 10-year yield | tracks: corr 0.17, right 62% | unclear: corr 0.26, p 0.0001, right 58% |
| Dollar index | unclear: corr 0.14, right 53% | unclear: corr 0.16, p 0.0001, right 56% |
| VIX | doesn't | doesn't |
| S&P 500 | doesn't | doesn't |
| Gold | doesn't | unclear (no agreed sign, so at most unclear) |

**What it says.**

- **The jobs report is the strongest of the three events.** It moves all five markets, and the
  10-year yield most of all: 67% more than an ordinary day.
- **Fed days move the risk markets most:** the S&P 500, VIX and gold.
- **CPI moves rates, the dollar and VIX, but not equities or gold.** Against the clean baseline its
  ratios rose slightly and no verdict changed.
- **The yield's and the dollar's moves follow the payroll surprise more clearly than CPI's:** rank
  correlations of 0.26 and 0.16 at p 0.0001, over 670-odd releases. But they go the expected way
  only 58% and 56% of the time, under the 60% bar, so neither *tracks*. A surprise against the
  trend, not against the economists' consensus, is the likely limit; see
  [Precision](../precision.md).

**What it does not say.**

- **The Fed's dollar verdict is borderline** (p 0.0096 against 0.01), not a strong result.
- **Five of the 14 unscheduled Fed decisions were not rate changes:** 2007-08-10, 2007-08-17,
  2008-03-11, 2010-05-09 and 2019-10-11 were liquidity and implementation statements. They count
  as Fed days here.
- **One question is still open.** In 1990–2007 the yield and the dollar moved more the day after a
  Fed decision than on the day itself. Daily closes cannot say whether their close came before the
  statement then, or the reaction ran into the next day.
- **Nothing here predicts.** As with the MVP, these numbers describe the past.
