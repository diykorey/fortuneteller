# Dated shocks, part 2: tariff actions

> Step 10 of the [Roadmap](../roadmap.md#next-steps-in-order), part 2 of four, chosen 2026-11-02
> after [elections](elections.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** do markets move when a US president signs a tariff, and is the move still
there a week later?

Elections were the easy dated shock: the day is fixed and nobody chooses which votes count. A
tariff is harder on both counts. Announcements come by speech, by post, by leak, and a list picked
by hand from the famous days would be picked by their moves. So the event here is the one record
nobody picks: the president's signed document, as the Federal Register lists it.

At the end: every presidential tariff action since 2018 as one lesser flow, from a hand-written
seed file with each row's Federal Register document number. It gets rung 1's test on the day and
over the week, as elections did.

## The events

- **Source:** the Federal Register's presidential documents (proclamations, executive orders,
  memoranda) whose full text mentions a tariff, read through its free API on 2026-11-02: 368
  since 1994. Copied by hand into `data/seed/tariffs.csv`, one row per document: the signing day,
  the document number and the title. The API is not read at run time.
- **What counts, by the document, not by the market:** a document counts if it imposes, raises,
  lowers, suspends or ends an additional US import duty, or directs that it be done. That covers
  Section 232 (*Adjusting Imports of …*), Section 301 actions, Section 201 safeguards (*To
  Facilitate Positive Adjustment …*), IEEPA duties and their amendments, and a trade deal's
  implementation where it changes one of those duties. Eases and pauses count: the test is on the
  size of the move, not its direction.
- **What does not:** an order to study or investigate (*Addressing the Threat to National Security
  From Imports of …*, the 2025 trade-policy memoranda), trade preferences (GSP, AGOA), routine
  trade-agreement and tariff-schedule housekeeping, quota allocations, import bans, duty-free
  emergencies, and observances (Labor Day, World Trade Week).
- **Since 2018.** Before it the list holds niche safeguards (brooms, lamb, wheat gluten) and the
  2002 steel and 2009 tyre actions: a decade between broad ones. Applied to the titles on
  2026-11-02 the rule keeps about 117 documents on **78 signing days**: 7 in 2018, 2 in 2019, 6 in
  2020, 4 in 2021, 5 in 2022, 3 in 2023, 6 in 2024, 27 in 2025 and 18 so far in 2026. Step 1
  reads each document whose title leaves it open and settles the count. *Amended 2026-11-03:*
  settled at **103 documents on 73 days**: 6, 2, 5, 4, 5, 3, 6, 28 and 14 a year. Out after
  reading: quota-only steps with no duty changed (2018-08-29, 2020-08-28), orders that leave a
  duty to a later decision (Venezuelan oil, Cuba, Iran), negotiations without a duty (aircraft, wind
  turbines, robotics, critical minerals) and the Graham Act's order, which waives its own duties.
  In: extensions that move the date a duty changes, and the 2025 orders that keep low-value
  shipments duty-free.
- **One event a day.** Several documents signed the same day are one event.
- **Time: the next trading day.** The Federal Register gives the signing day, not the hour. Each
  signing is taken as after the close, 16:00 New York, so its reaction is the next trading day's
  close; a weekend signing reacts on Monday. This is the elections' rule. *Amended 2026-11-03:*
  20:00 New York, not 16:00: VIX closes at 16:15 and bitcoin at midnight UTC, so 16:00 put their
  reaction on the signing day. At 20:00 every market reacts on its next close; bitcoin, which
  trades at weekends, on the Sunday. A signing is stored as not scheduled: its day was not known
  in advance.
- **Known misses, written down first:**
  - Announcements before the signing: steel and aluminium were announced on 2018-03-01 and signed
    on 2018-03-08.
  - Escalations by post: the China rate rises of 2019-05-05 and 2019-08-01.
  - Section 301 lists published by USTR, not the president: the China lists of 2018 and 2019.
  - Same-session signings: the 2025-04-09 pause was announced at 13:18 New York and moved the
    market that day; its row reacts on 2025-04-10.
- **Origin:** a new seed event type `Tariff action`, country `United States`. *Amended 2026-11-03:* the seed
  already holds `Tariff / trade-war / sanctions`, from Notion; the flow uses it, and no row is added.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, ordinary days from
  the flow's own years, *too few* under ten days a cell.
- **Lesser, as claims and elections are:** each tariff day stays an ordinary day for every other
  flow. The flow keeps only its lone reaction days, judged on the reaction day against the lead
  flows. Every existing output stays identical. *Amended 2026-11-03:* the scoreboard gains the
  flow's entry, and its cells with a verdict join the chance line's count, as elections' did.
- **No surprise and no call:** no free calendar forecasts a tariff, so there is no sign, no surprise
  table and no walk-forward.
- **And over a week:** `raw-move --week`, as built for elections. 2025's signings cluster
  (2025-03-02, 03-03 and 03-06), so their windows overlap each other as well as the ordinary
  ones; the [precision](../precision.md) doc records it.
- **Chance, counted:** 16 *does it move?* cells on the day, 0.16 *moves* by chance; as many over a
  week.
- **Expected outcome, written down first:** the routine proclamations (steel and aluminium
  country exemptions, safeguard extensions) are about half the days and dilute the rest. Over all
  the days no market moves at the bar on the day. The era split shows 2020–now well above the
  earlier years on the S&P 500 and VIX. Over a week nothing reaches the bar.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seed file with each counted document and its number, the flow stored, the misses named~~ **done** | A test's seed rows store a Saturday signing with a Monday reaction and two documents on one day as one event; every row's number is the Federal Register's for that title; every existing output identical on a copy of the store; the days left out as shared named |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | The flow's verdicts on the day and over a week, by era, against the expected outcome |

*Step 1, 2026-11-03:* 103 documents on 73 signing days, 2018-01-23 to 2026-10-23, each number the
Federal Register's for its title as its API listed them on 2026-11-02. On a copy of the store
every existing scoreboard entry is identical, and so are the calls and *missed*; the flow adds 16
cells to the chance line (270 → 286). The build takes 9 minutes 50 seconds. On the S&P 500 the
flow keeps 44 days. The 29 left out share their reaction day with a lead flow's release: ISM 10,
jobs reports 9, the euro-area flash 7, retail sales 5, CPI 5, core PCE 2, GDP 1. Some share
with two releases or three, so the counts add to more than 29. By signing day:
2018-03-08, 2018-04-30, 2018-05-31, 2020-08-06, 2021-01-14, 2022-03-31, 2022-05-27, 2022-05-31,
2023-05-31, 2024-05-14, 2024-05-31, 2024-07-10, 2025-02-01, 2025-03-02, 2025-03-06, 2025-04-09,
2025-04-29, 2025-05-12, 2025-06-16, 2025-07-30, 2025-07-31, 2025-08-11, 2025-09-04, 2026-04-02,
2026-06-01, 2026-07-15, 2026-07-31, 2026-08-06 and 2026-08-13. Among them the first steel and
aluminium proclamations (a jobs report the next day), the first IEEPA duties (ISM's Monday) and
the 2025-04-09 pause (CPI's Thursday).

## Results

Measured 2026-11-03 (`raw-move --event tariff`, with and without `--week`) on step 1's copy of
the store: 44 lone reaction days on most markets (on the day 45 on the DAX and bitcoin, 38 on the
euro; over a week 43 on three European indices),
against ordinary days since 2018.

| | On the day | Over a week |
| --- | --- | --- |
| **Moves** | **the DAX, 1.64 (p 0.004); the Euro Stoxx 50, 1.62 (p 0.004)** | **the DAX, 1.58 (p 0.002); the STOXX 600, 1.52 (p 0.003)** |
| *Unclear* | the STOXX 600 1.42 (p 0.02), gold 1.36, VIX 1.35 (p 0.05), the FTSE 100 1.29, bitcoin 1.12 | the FTSE 100 1.45 (p 0.01), the Euro Stoxx 50 1.42 (p 0.02), gold 1.17, the dollar 1.16 |
| Doesn't | the S&P 500 0.92, the Nasdaq 1.02, both yields (0.77, 0.71), the dollar 0.76, the euro, Brent, defence, energy | the S&P 500 0.94, the Nasdaq, both yields, VIX 1.05, the euro, Brent, defence, energy, bitcoin |

- **On the next close only Europe's stocks clear the bar.** The DAX and the Euro Stoxx 50 move
  about 1.6 times an ordinary day. The STOXX 600 (1.42) and the FTSE 100 (1.29) are *unclear*. The
  S&P 500, the Nasdaq, the yields and the dollar move as on an ordinary day.
- **Over the week the DAX is the one index to clear it on the day and over the week:** 1.58 over five closes, with the STOXX
  600 at 1.52. The Euro Stoxx 50 drops to *unclear* (1.42), and the dollar rises to *unclear*
  (1.16).
- **By era:** 2018–2019 has 5 days on every market, too few to compare with since 2020, when the
  DAX is 1.52, the Euro Stoxx 50 1.56, VIX 1.38 and the S&P 500 0.85.
- **A check, not a verdict: the signing day.** Europe's markets close by 11:30 New York. A
  signing or an announcement during New York's afternoon lands in New York's close that day but
  in Europe's next close, the one measured here. On the signing day itself, measured by a one-off script with
  rung 1's comparison (each market's moves on the signing days that are trading days and hold no
  lead release, 44 on the S&P 500 and 41 on the DAX, against ordinary days that are neither
  signing nor reaction days), the S&P 500 moves 1.22 (p 0.17, *unclear*) and the DAX 1.08. So part of what Europe shows may be news New York
  took the afternoon before; the measure cannot tell. That Europe's goods were the target of many
  of these duties is a guess, not tested.
- **Chance:** expected by chance, 0.16 *moves* of 16 cells; found, 2. Over a week the same: 2.
  The two are close to one finding, not two: the DAX, the Euro Stoxx 50 and the STOXX 600 hold
  many of the same companies. The week's p values are optimistic, since its windows overlap
  ([precision](../precision.md)).
- **No call.** A signing has no surprise and no sign.

**Against the expected outcome:**

- Routine proclamations dilute the rest: **not tested**; nothing here splits routine signings
  from broad ones.
- No market moves at the bar on the day: **wrong**, the DAX and the Euro Stoxx 50 move.
- 2020–now well above the earlier years on the S&P 500 and VIX: **not tested**, the earlier years
  have 5 days; since 2020 the S&P 500 is below an ordinary day (0.85) and VIX above (1.38).
- Over a week nothing reaches the bar: **wrong**, the DAX and the STOXX 600 move, both at p values the
  overlapping windows make optimistic.

**What it means.** On the next close after a president signs a tariff, Europe's main indices move
more than on an ordinary day and the S&P 500 does not. Whether that is Europe reacting to the
duty or catching up with New York's afternoon, this daily measure cannot separate. Two of New
York's largest tariff days, the 2025-04-09 pause and the first IEEPA duties, share their
reaction day with CPI and ISM and are not counted; 2025-04-02, the reciprocal rates, is.

## Technical details

Elections and tariffs are now two cases of one thing, a flow read from a hand-written seed file
with no surprise, so step 1 turns `ElectionFlow` into one class for both. Its file name and the
column holding the time are fields, and `measure_raw_moves`' election branch becomes a branch for
the class. The tariff flow's time is a fixed 16:00 New York, not a column. *Amended 2026-11-03:*
built as `flows.DatedShockFlow`, whose fields name the seed file, its day, detail and time
columns, an optional country column and the fixed time (20:00); the elections are built by
`flows.election_flow`. The document numbers stay in the seed file; the stored `detail` holds the
day's titles. Type code 21, CLI name
`tariff`. `docs/schema.md` gets the type, and `docs/legacy/data/` the seed file.

## What this does not do

It adds no tariff announced by speech or post, no USTR notice, no other country's tariffs and no
retaliation against the US. It does not split raises from eases, gives no sign, and adds no
preview of a signing. Debt-ceiling deadlines and summits are parts 3 and 4.
