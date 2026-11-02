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
  reads each document whose title leaves it open and settles the count.
- **One event a day.** Several documents signed the same day are one event.
- **Time: the next trading day.** The Federal Register gives the signing day, not the hour. Each
  signing is taken as after the close, 16:00 New York, so its reaction is the next trading day's
  close; a weekend signing reacts on Monday. This is the elections' rule.
- **Known misses, written down first:**
  - Announcements before the signing: steel and aluminium were announced on 2018-03-01 and signed
    on 2018-03-08.
  - Escalations by post: the China rate rises of 2019-05-05 and 2019-08-01.
  - Section 301 lists published by USTR, not the president: the China lists of 2018 and 2019.
  - Same-session signings: the 2025-04-09 pause was announced at 13:18 New York and moved the
    market that day; its row reacts on 2025-04-10.
- **Origin:** a new seed event type `Tariff action`, country `United States`.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, ordinary days from
  the flow's own years, *too few* under ten days a cell.
- **Lesser, as claims and elections are:** each tariff day stays an ordinary day for every other
  flow. The flow keeps only its lone reaction days, judged on the reaction day against the lead
  flows. Every existing output stays identical.
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
| 1 | The seed file with each counted document and its number, the flow stored, the misses named | A test's seed rows store a Saturday signing with a Monday reaction and two documents on one day as one event; every row's number is the Federal Register's for that title; every existing output identical on a copy of the store; the days left out as shared named |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The flow's verdicts on the day and over a week, by era, against the expected outcome |

## Technical details

Elections and tariffs are now two cases of one thing, a flow read from a hand-written seed file
with no surprise, so step 1 turns `ElectionFlow` into one class for both. Its file name and the
column holding the time are fields, and `measure_raw_moves`' election branch becomes a branch for
the class. The tariff flow's time is a fixed 16:00 New York, not a column. Type code 21, CLI name
`tariff`. `docs/schema.md` gets the type, and `docs/legacy/data/` the seed file.

## What this does not do

It adds no tariff announced by speech or post, no USTR notice, no other country's tariffs and no
retaliation against the US. It does not split raises from eases, gives no sign, and adds no
preview of a signing. Debt-ceiling deadlines and summits are parts 3 and 4.
