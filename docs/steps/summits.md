# Dated shocks, part 4: summits

> Step 10 of the [Roadmap](../roadmap.md#next-steps-in-order), part 4 of four, chosen 2026-11-03
> after [the debt limit](debt-limit.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** do markets move when the leaders of the largest economies meet, and is the move
still there a week later?

The roadmap names "summits". Which ones count is a judgement unless a list fixes it. Two forums keep
one: the G7, whose leaders have met every year since 1975, and the G20, whose leaders have met since
the crisis of 2008. Both are dated, both are fixed months ahead, and both end in a communiqué.

At the end: both forums' summits as one lesser flow, from a hand-written seed file. It gets rung
1's test on the day and over the week.

## The events

- **Source:** the University of Toronto's G7 Research Group and G20 Research Group summit lists,
  each date checked against the summit's own page there. Compiled 2026-11-03. Copied by hand into
  `data/seed/summits.csv`, each row with its page's address; no source is read at run time.
- **What counts:** every in-person annual leaders' summit: **51 G7** (G8 from 1997 to 2013),
  1975-11-17 to 2026-06-17, and **19 G20**, 2008-11-15 to 2025-11-23; **70 summits**. **Out:**
  - two one-off G7 summits: Moscow's nuclear safety summit of 1996-04-20, and Brussels on
    2022-03-24, called because of the invasion of Ukraine, so its day measures the war, not a
    summit;
  - 15 G7 video or hybrid meetings from 2020 to 2026 and 4 G20 ones, the G7's meeting with NATO
    beside the 2022 G20 in Bali, the suspended Sochi G8 of 2014 (its replacement in Brussels
    counts) and the 2020 G7, never held;
  - Miami's G20 of 2026-12-14/15: not in the seed file; added by a dated amendment once it ends.
- **One flow, not two:** the G20's 19 days alone would leave most markets *too few*, and the
  expected outcome is the same for both forums. The G7 alone is a check below.
- **The day: the summit's last day,** when the communiqué is normally issued. The sources give no
  hour, so the hour is a rule, kept in a `time` column in New York time: **08:00** for a weekday
  last day in Europe or Asia (23 G7, 7 G20), when the local afternoon has begun in Europe and passed in Asia and every market
  measured, Europe's included, still has that day's close ahead; **20:00**, after every close, as
  tariff actions, for a weekend last day or a summit in the Americas. A last day on a
  weekend, 20 of the G7's and 9 of the G20's, reacts on Monday, bitcoin on its next close. A last
  day on a US holiday (1983-05-30, 2016-09-05) reacts on New York's next open day, as every flow.
  The G7 at Muskoka ended on 2010-06-26 and the G20 at Toronto on 06-27: two events, one reaction
  day.
- **Where the sources disagree:** the Toronto index and a summit's own page differ on four summits
  kept; the index is used. Only Naples 1994 changes its last day, 07-10 or 07-09, a Sunday or a
  Saturday, with the same Monday reaction.
- **Stored as scheduled:** each summit's dates are announced months ahead, as an election's are,
  unlike a tariff signing or a debt vote.
- **Known misses, written down first:**
  - A dated leaders' text issued on a trading day before the day measured: the G7 of 1996
    (Friday, for a Monday), 2007, 2008, 2009, 2014, 2024 and 2026, and the G20 of 2017 and 2024; the G7's
    own statement on the Friday before the G8's weekend end, 1998–2001. St. Petersburg 2006's
    Sunday texts, Hiroshima 2023's and the G20's of 2010, 2023 and 2025 react on the same day as
    the last day.
  - A European text after Europe's close, or one later than 16:00 New York: measured a day early
    or a day late. A weekday summit in the Americas whose text lands before New York's close is
    measured the next day: G7 Kananaskis 2002, Sea Island 2004 and Kananaskis 2025, G20
    Pittsburgh 2009 and Los Cabos 2012 date their texts on the last day, with no hour. The check below measures the other day.
  - News made beside a summit, not by it, falls in its window all the same.
- **Origin:** a new seed event type `Leaders' summit`, tier 4, polarity `both`, as `National
  election`: none of the 39 types fits, the nearest being `Geopolitical escalation / terror`. A new
  seed country row, `0,G7 / G20,~100,,Not a country: the forums whose leaders meet yearly;
  unranked,Reuters / G7 and G20 Research Groups`, as `European Union`'s.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, ordinary days from
  the flow's own years, *too few* under ten days a cell.
- **Lesser, as elections, tariffs and the debt limit:** each day stays an ordinary day for every
  other flow, and the flow keeps only its lone reaction days. Every existing scoreboard entry
  stays identical; the page gains the flow's entry, and its cells with a verdict join the chance
  line.
- **No surprise and no call:** no sign, no surprise table, no walk-forward.
- **And over a week:** `raw-move --week`, as before. Its windows overlap where two summits fall
  within a week of each other ([precision](../precision.md)).
- **Read as two families:** the DAX, the Euro Stoxx 50, the STOXX 600 and the FTSE 100; the 10-year
  and 5-year yields. A *moves* within one counts as one finding.
- **Two checks, not verdicts, planned now,** each a one-off script with rung 1's comparison: the G7
  alone; and the other day for each weekday last day (the next close for the 08:00 summits, the
  last day's own close for the 20:00 ones in the Americas), as tariffs' signing-day check: days
  holding a lead release left out, ordinary days neither a summit's reaction day nor its other
  day.
- **Chance, counted:** 16 cells on the day, 0.16 *moves* by chance; as many over a week.
- **Expected outcome, written down first:** a summit is long announced and its communiqué mostly
  drafted in advance. No market moves at the bar, on the day or over the week. No era claim. The
  G7 often meets in June, near a Fed decision; each market's lone days are counted in step 1,
  before any move is measured, and the markets under ten named then.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed file with 70 summits, the flow stored, each market's lone days counted, the days left out as shared named by lead flow | A test's seed rows store a Saturday last day with a Monday reaction on the S&P 500 and a Sunday one on bitcoin; a weekday European last day reacting that day; the seed test checks the header, `summit` opening with `G7 ` or `G20 `, `time` 08:00 or 20:00, `source_url` on `utoronto.ca`, last days in order since 1975-11-17 and by today, no repeated `last_day` or `source_url`; each market's lone days and the left-out days written here; every existing scoreboard entry identical on a copy of the store |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The flow's verdicts on the day and over a week, the two checks, against the expected outcome |

## Technical details

One more `flows.DatedShockFlow`, `SUMMIT_FLOW`: event type constant `SUMMIT_EVENT_TYPE = "Leaders'
summit"`, country constant `G7_G20 = "G7 / G20"` beside `EUROPEAN_UNION`, zone `NEW_YORK`, type
code 23, CLI name `summit`, label `SUM`, noun `summits`; seed file `summits.csv` with the header
`last_day,time,summit,source_url` in date order (`summit` as `G7 Muskoka`, `G20 Toronto`), day column
`last_day`, time column `time`, detail column `summit`, `scheduled=True`. No new code path. The checks
run as one-off scripts on the store copy; `raw-move` is unchanged.

Tests: `tests/test_study_raw_move.py` gets the Saturday and weekday test; `tests/test_seed_data.py` the seed test
and `summits.csv` in the expected set; `tests/test_study.py`'s load-releases test writes a one-row
`summits.csv`, expects its report line and one more stored event. `docs/schema.md` gets code 23,
the event type and the country in `event_type`, `event_id`, `event_ts`, `country`, `detail`,
`scheduled` and `quality`, and the countries paragraph; `docs/precision.md` the dating and the
overlapping weeks; the glossary G7, G20 and communiqué; `docs/legacy/data/README.md` the seed file
and `docs/legacy/data/countries.md` the country row.

## What this does not do

It adds no communiqué text and no reported hour, no other forum (the European Council, NATO, OPEC, BRICS)
and no bilateral meeting. It gives no sign. It closes step 10; step 11, news as a feed, is next.
