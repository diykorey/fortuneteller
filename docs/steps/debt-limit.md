# Dated shocks, part 3: the debt limit

> Step 10 of the [Roadmap](../roadmap.md#next-steps-in-order), part 3 of four, chosen 2026-11-03
> after [tariff actions](tariffs.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** do markets move on the day Congress raises or suspends the US debt limit, and
is the move still there a week later?

The roadmap names "debt-ceiling deadlines". A deadline is a guess until it passes: Treasury's
letters naming the day it would run out of cash start in 2011, and most name a range. What has a
date is how each standoff ended: the day Congress cleared the law that raised or suspended the
limit. That day, not the president's signature, is when markets learn the outcome: in 2011, 2013
and 2023 the signature came one to two days after the final vote.

At the end: every law that changed the debt limit since 1970 as one lesser flow, from a
hand-written seed file with each law's number. It gets rung 1's test on the day and over the week.

## The events

- **Source:** the public laws that changed the statutory debt limit, from the Congressional
  Research Service's history (RL31967) and the budget's historical table, each signing checked
  against the Statutes at Large on govinfo and, since 2005, Treasury's daily limit series on
  Fiscal Data. Compiled 2026-11-03: 77 laws, 1970-06-30 to 2025-07-04. For each, the day Congress
  cleared it: the later chamber's final passage, from the law's legislative history in the
  Statutes at Large or Congress.gov's actions. Copied by hand into `data/seed/debt_limit.csv`;
  no source is read at run time.
- **What counts:** a law that raises the limit, extends a temporary limit, or suspends it. **Out:**
  the two 1996 laws (P.L. 104-103 and 104-115) that exempted certain obligations without changing
  the limit, and the 2011 Budget Control Act's later increases, made by presidential certification,
  not by law. That leaves **75 laws**, by decade 18, 24, 11, 9, 9 and 4.
- **The day: Congress's final vote.** Taken at 20:00 New York, after every market's close, as
  tariff actions: many final votes come in the evening, and the record gives no hour for the
  older ones. *Amended 2026-11-03, before any move was measured:* 11 of the 19
  final votes since 2005 came before 16:00 New York in the day: 109-182 (11:17), 110-289
  (11:00), 110-343 (13:22), 111-123 (07:16), 111-139 (15:49), 112-25 (12:16), 113-3 (15:37),
  113-83 (14:55), 115-56 (10:33), 116-37 (11:54) and 119-21 (14:31); three more came
  after midnight (114-74 at 02:43, 115-123 at 05:32, 117-73 at 00:20). So the seed file has a `time` column: the
  roll-call time since 2005, on the calendar day the vote was taken (2015-10-30 02:43, 2018-02-09
  05:32, 2021-12-15 00:20), and 20:00 before it. Each market reacts on its first close after that
  time. ~~A vote after midnight is dated by the evening it began (2018-02-08, 2021-12-14).~~ The
  after-midnight votes keep the same reaction close either way. A law passed over a veto is dated
  by the override (1980-06-06). Laws cleared on one day are one event: **73 days**, with two laws
  each on 1981-09-29 and 1990-10-27. Stored as not scheduled: even when a
  temporary limit's expiry was known, the day Congress would act was not.
- **Two kinds, written down first.** `debt` if the law's title is about the public debt alone;
  `rider` if the change rides inside a broader act: budget reconciliations, the Budget Control Act,
  the Fiscal Responsibility Act, the 2008 housing and bank-rescue acts, the 2009 stimulus. A
  rider's day carries the rest of its act. A named short title decides it over a debt-only long
  title (Gramm-Rudman, Statutory PAYGO, No Budget No Pay). Compiled: 50 `debt`, 25 `rider`; the
  riders are 8 of 9 in the 2010s.
- **Known misses, written down first:**
  - A deal announced before the vote: 2011-07-31 and 2023-05-27.
  - A vote in market hours: the Senate's 2011 vote at midday on 08-02, after the House's the
    evening before, and the 2013 Senate deal at midday on 10-16; the 20:00 rule puts their
    reactions on the next day. The bank rescue of 2008 (P.L. 110-343, a rider) cleared the
    House at about 13:20 on 10-03, and its reaction lands on 10-06; *amended 2026-11-03:* with
    the vote times 2011 and 2008 react on their own day (2011-08-02, 2008-10-03); 2013 still
    reacts on 10-17, its final House vote came at 22:18; the failed House vote of 09-29 is in no window. The final votes before 16:00
    are listed under *The day* above.
  - Inside a week window: the S&P downgrade of 2011-08-05 falls in the 2011 law's week.
  - Left out entirely: the days the limit was reached and extraordinary measures began (dated by
    Treasury's own letters only since 2011, eleven episodes), the X-date letters, shutdowns.
- **Clusters:** five stopgaps signed in October 1990, cleared days apart, and runs in 1980 and 1987;
  their week windows overlap each other.
- **Origin:** the seed's existing event type `Fiscal: debt-ceiling / shutdown`, country `United
  States`.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, ordinary days from
  the flow's own years, *too few* under ten days a cell.
- **Lesser, as elections and tariffs are:** each day stays an ordinary day for every other flow,
  and the flow keeps only its lone reaction days. Every existing scoreboard entry stays
  identical; the page gains the flow's entry, and its cells with a verdict join the chance line.
- **No surprise and no call:** no sign, no surprise table, no walk-forward.
- **And over a week:** `raw-move --week`, as before.
- **Read as one family:** the DAX, the Euro Stoxx 50, the STOXX 600 and the FTSE 100 hold many of
  the same companies; a *moves* among them counts as one finding.
- **Two checks, not verdicts, planned now:** the same comparison on `debt` laws alone, without
  the riders; and on the day before each reaction day, for news that reached markets in the
  session before the final vote.
- **Chance, counted:** 16 cells on the day, 0.16 *moves* by chance; as many over a week.
- **Expected outcome, written down first:** 42 of the 75 laws are from 1970–1989, when raising
  the limit was routine. No market moves at the bar, on the day or over the week. No era claim:
  since 2020 there are 4 laws, too few. Each market's lone days are counted in step 1, before any
  move is measured, and the markets under ten named then.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seed file with 75 laws on 73 days, the flow stored, each market's lone days counted, the days left out as shared named by lead flow~~ **done** | A test's seed rows store a vote cleared on a Saturday with each market's next close as its reaction, and two laws cleared on one day as one event; the seed test checks the header, each law number's form (`\d{2,3}-\d{1,3}`), that no number repeats, `action` in raise/temporary/suspend, `vehicle` in debt/rider, `cleared` in order since 1970-06-29 and never after `signed`, each `time` as hours and minutes; each market's lone days and the left-out days written here; every existing scoreboard entry identical on a copy of the store |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | The flow's verdicts on the day and over a week, the two checks, against the expected outcome |

*Step 1, 2026-11-03:* 75 laws on 73 days stored, 1970-06-29 to 2025-07-03. On a copy of the store
every existing scoreboard entry is identical, and so are the calls and *missed*; the flow adds 10
cells with a verdict to the chance line (286 → 296). The build takes 9 minutes 15 seconds. Lone
days by market: the S&P 500 60, the 10-year and 5-year yields 59, the Nasdaq 59, the dollar 58,
the FTSE 100 33, the DAX 21, VIX 19, the STOXX 600 10, energy 10; *too few*: gold 9, the Euro
Stoxx 50 9, the euro 9, defence 8, Brent 7, bitcoin 3. Left out as shared on the S&P 500, 13 laws:
105-33 (a jobs report), 107-199 (core PCE), 109-182 (CPI), 110-91 (core PCE), 110-343 (a jobs
report), 112-25 (core PCE), 113-3 (core PCE), 114-74 (core PCE and the euro-area flash), 116-37
(ISM), 117-50 (CPI), 117-73 (the Fed and retail sales), 118-5 (a jobs report), 119-21 (a jobs
report). Among them three of the four standoffs the spec names: the 2008 bank rescue, 2011 and
2023. Of the modern standoffs only 2013 is measured.

## Results

Measured 2026-11-03 (`raw-move --event debt`, with and without `--week`) on step 1's copy of the
store: each market's lone reaction days (60 on the S&P 500, 59 on both yields; over a week 20 on
the DAX and 31 on the FTSE 100), against ordinary days from each market's own years (1970 at the
earliest).

| | On the day | Over a week |
| --- | --- | --- |
| **Moves** | **the 10-year yield, 1.97 (p 0.0002); the 5-year yield, 1.94 (p 0.0002)** | **the 10-year yield, 1.51 (p 0.006); the 5-year yield, 1.57 (p 0.003)** |
| *Unclear* | the STOXX 600 1.83 (p 0.04, 10 days), the FTSE 100 1.19, VIX 1.18, the dollar 1.13, the S&P 500 1.11, the Nasdaq 1.11 | the FTSE 100 1.36 (p 0.07), VIX 1.34, the DAX 1.31, the STOXX 600 1.28, the S&P 500 1.17, the dollar 1.12 |
| Doesn't | the DAX 1.03, energy 0.86 | the Nasdaq 0.73, energy 1.05 |
| *Too few* | gold, the Euro Stoxx 50, the euro, defence, Brent, bitcoin | the same |

- **Treasury yields move; stocks do not.** On the close after Congress's final vote the 10-year
  and 5-year yields move about twice an ordinary day's (5.9 and 6.0 basis points against 3.0 and
  3.1). The S&P 500 and the Nasdaq move 1.11 times an ordinary day, the dollar 1.13.
- **Over the week the yields still clear the bar,** at about 1.5, the excess smaller than on the
  day. Nothing else does. The week's p values are optimistic, since its windows overlap
  ([precision](../precision.md)).
- **By era, with no p value:** the 10-year is 1.67 in 1970–1989 (41 days) and 2.26 in 1990–2007
  (11); 2008–2019 has 7 days, too few. The S&P 500 is 0.87 in 1970–1989 and 1.88 in 1990–2007,
  each era's ratio a check, not a verdict.
- **Check 1, not a verdict: `debt` laws alone.** Without the 25 riders, on 49 days on the S&P
  500: the 10-year 1.67 (p 0.005) and the 5-year 1.94 (p 0.0001) still move; the S&P 500 is 0.93.
  So the yields' move is not the budget acts riding with the limit.
- **Check 2, not a verdict: the session before.** On the close before each reaction day, no market
  quoted moves at the bar: the S&P 500 1.31 (p 0.07, *unclear*), the 10-year 0.78.
- **Check 3, added after measuring, not a verdict: month ends.** Many raises came at a month's or
  a quarter's end, when bond portfolios rebalance. Ordinary month-end days move the 10-year 1.07
  times other ordinary days; debt days away from a month end still move it 1.97 (p 0.0004, 41
  days). So month ends do not explain the move.
- **Chance:** 10 cells with a verdict on the day (16 less the six *too few*), 0.1 *moves* by
  chance; found 2. Over a week the same: 2. The two yields are read as one finding, not two, a
  grouping added after measuring as the European family was before it: the 5-year and the
  10-year are neighbouring maturities on one curve.
- **No call.** A vote has no surprise this project can grade and no sign.

**Against the expected outcome:**

- 42 of the 75 laws routine, from 1970–1989: **not tested** as a cause; that era's 41 days give
  the 10-year 1.67 and the S&P 500 0.87, with no p value.
- No market moves at the bar on the day: **wrong**, both Treasury yields move, about twice an
  ordinary day.
- Nor over the week: **wrong**, both yields move, at p values the overlapping windows make
  optimistic.
- No era claim: kept; since 2020 every law is left out as shared on the S&P 500 and both yields.
- Lone days counted and the markets under ten named: done in step 1.

**What it means.** The day Congress settles the debt limit is a day for the bond market, not the
stock market: Treasury yields move about twice an ordinary day, with and without the riders,
and over the week they still move more than in an ordinary week, by less than on the day. No
stock market moves at the bar. Three of the four standoffs the spec names, 2008, 2011 and 2023,
are left out as shared with a jobs report or core PCE, so the measure is mostly the routine
raises; which way the yields go, this measure does not ask.

## Technical details

One more `flows.DatedShockFlow`, `DEBT_LIMIT_FLOW`: type code 22, CLI name `debt`, label `DBT`,
noun `debt-limit laws`, event type `Fiscal: debt-ceiling / shutdown`; seed file `debt_limit.csv`
with the header `cleared,signed,public_law,action,vehicle`, day column `cleared`, detail column
`public_law`, the fixed 20:00, `scheduled=False`. No new code path. *Amended 2026-11-03:* the
header is `cleared,time,signed,public_law,action,vehicle`, read with `time_column="time"` in place
of the fixed 20:00, so the midday votes under known misses are measured on their own day. The checks run as one-off
scripts on the store copy, as tariffs' signing-day check did; `raw-move` is unchanged.

Tests: `tests/test_study_raw_move.py` gets the Saturday and one-day test; `tests/test_seed_data.py`
the seed test and `debt_limit.csv` in the expected set; `tests/test_study.py`'s load-releases test
writes a one-row `debt_limit.csv`, expects its report line and one more stored event.
`docs/schema.md` gets code 22 and the file in `event_type`, `event_id`, `event_ts`, `country`,
`detail`, `scheduled` and `quality`; `docs/precision.md` the dating and the clusters;
`docs/legacy/data/` the seed file.

## What this does not do

It adds no deadline, no X-date, no extraordinary-measures day, no shutdown and no rating action. It
gives no sign. Summits are part 4.
