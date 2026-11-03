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
  older ones. A vote after midnight and before the next session is dated by the evening it began,
  as the Congressional Record dates it (2018-02-08, 2021-12-14); a law passed over a veto by the
  override (1980-06-06). Laws cleared on one day are one event: **73 days**, with two laws each
  on 1981-09-29 and 1990-10-27. Stored as not scheduled: even when a
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
    House at about 13:20 on 10-03, and its reaction lands on 10-06; the failed House vote of
    09-29 is in no window. Step 1 records which final votes since 2005 came before 16:00 New
    York, from the roll-call times, and lists them here.
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
| 1 | The seed file with 75 laws on 73 days, the flow stored, each market's lone days counted, the days left out as shared named by lead flow | A test's seed rows store a vote cleared on a Saturday with each market's next close as its reaction, and two laws cleared on one day as one event; the seed test checks the header, each law number's form (`\d{2,3}-\d{1,3}`), that no number repeats, `action` in raise/temporary/suspend, `vehicle` in debt/rider, `cleared` in order since 1970-06-29 and never after `signed`; each market's lone days and the left-out days written here; every existing scoreboard entry identical on a copy of the store |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The flow's verdicts on the day and over a week, the two checks, against the expected outcome |

## Technical details

One more `flows.DatedShockFlow`, `DEBT_LIMIT_FLOW`: type code 22, CLI name `debt`, label `DBT`,
noun `debt-limit laws`, event type `Fiscal: debt-ceiling / shutdown`; seed file `debt_limit.csv`
with the header `cleared,signed,public_law,action,vehicle`, day column `cleared`, detail column
`public_law`, the fixed 20:00, `scheduled=False`. No new code path. The checks run as one-off
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
