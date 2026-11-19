# Floods

> Step 30 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19 by the owner as "floods and droughts". Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** after a costly US flood began, what followed for crops, fuel, insurers and the
indexes, over the day, the week and the month? Step 28 asked this of hurricane landfalls; the
floods and droughts it left out come here.

At the end: `follows --event flood` prints what followed each of NOAA's billion-dollar US floods,
measured as [step 17](what-follows.md) measures a kind, against the rule below written first.

## The way to reach it

- **The source: NOAA's Billion-Dollar Weather and Climate Disasters list, 1980 to 2024**, every
  US event of a billion dollars or more (CPI-adjusted), each with its type, begin and end day. NOAA
  stopped updating it in May 2025 and keeps it archived; NCEI's own address answered 503 on
  2026-11-19, so the copy read is the Wayback Machine's of 2025-01-27 23:34:39 UTC
  (`web.archive.org/web/20250127233439/https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv`),
  sha256 `67831180c9f1f348ea560acd291e84a0e2410f6fa3e129fa8297f114fd8537e9`. It holds 403 events,
  1980 to 2024, the count NOAA published for its final release. Nobody here picks the events.
- **The kind: a flood, as NOAA codes it.** Every row whose `Disaster` is `Flooding`: 45, from
  1980-04-10 to 2024-06-16, its day the `Begin Date`. A `Severe Storm` or `Tropical Cyclone` row
  named "… and Flooding" is not one: the column is the rule, not the name. One kind, `flood`.
- **No crop-region filter.** The list has no state or region column, so a crop-growing filter
  would be read from the names, by hand. The crops are among the markets, so the crop question is
  still asked of every flood. *Amended 2026-11-19*, against the roadmap row's "in crop-growing
  regions".
- **Droughts are left out: they have no day.** All 32 of the list's droughts begin on the first
  of a month (1 June for most), a season's label, not a day anyone knew a drought had begun. A call
  is made from the actual once it lands, and a drought dated to 1 June breaks that. A drought day
  read from the weekly US Drought Monitor would need a threshold chosen here: its own spec, if
  ever.
- **The size is known only later.** A flood's billion-dollar cost is tallied weeks on, as a hack's
  $100 million is not: so a flood is measured as history only. The flow takes no trigger.
- **The hour:** the list gives a day, no hour; the event is placed at 04:00 UTC of its begin day,
  the rule of the other one-kind flows ([war](war.md)), so it reacts that day on every market.
  Eight floods begin on a first of the month (1982-12-01 among them); they are kept as coded,
  and counted in Results.
- **The flow:** a `DatedShockFlow`, `flood`, code 33, event type `Natural disaster` as the
  landfalls', no surprise, lesser, unscheduled, one kind in `study.ONE_KIND`. No new market.

## The rule, fixed before anything is shown

- The source, the kind, the hour and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - The header: `follows: 45 floods 1980-04-10 … 2024-06-16: 45 floods`.
  - Arithmetic, not a finding: 30 graded walk-forward needs 40 events ([OPEC's](opec.md) rule).
    A market whose closes start after 1983 has fewer than 40 floods and is *too few* walk-forward
    on every span; the counts per market, after overlap, are recorded in Results.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Corn, wheat, soybeans, gasoline, natural gas, Brent, energy stocks and Allstate on the day,
    the week and the month: *can't say*, in both runs. A billion-dollar flood is local, and is
    known to be one only later.
  - Every other flow's `follows` output unchanged byte for byte; the scoreboard gains the floods'
    entry (32 → 33 events) and nothing else.
- **Outside the rule, recorded:** `raw-move --event flood`, and the floods' days shared with
  another flow (`scripts/shared_days.py flood`), the landfalls first: storm floods may fall near
  them.

*Written 2026-11-19, before `follows` or `raw-move` ran on these floods; the counts above are from
the list.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed and the flow: `scripts/noaa_floods.py` writes `data/seed/floods.csv` from the local copy; the `flood` flow in `follows` | The tests below pass; `follows --event flood` prints the header above |
| 2 | Results | Each bullet of the rule judged in Results, with its numbers and the command that prints them; a goldfish review |

## How you know it is right

- **The seed, by a test:** 45 rows, each `Flooding` in the copy, none of another type; the first
  1980-04-10 (Southern Severe Storms and Flooding), the last 2024-06-16 (Upper Midwest Flooding).
- **The hour, by a test:** a flood dated 2024-06-16, a Sunday, reacts on Monday 2024-06-17 on the
  S&P 500; one dated a Tuesday reacts that Tuesday.
- **No trigger, by a test:** a `flood` trigger is void, not one of the flows.
- **By hand:** the script's 45 against the copy's `Flooding` rows, counted once with `grep -c`.

## What this step does not do

- It measures no drought, adds no market, and takes no trigger.
- It reads no news; the page's *ask* gains the floods only in a later step.

## Technical details

- `scripts/noaa_floods.py PATH` reads the local copy (`python -I`), keeps `Flooding` rows, and
  writes `day,name,cost` (`day` from `Begin Date`, `cost` the CPI-adjusted millions).
- `flows.FLOOD_FLOW = DatedShockFlow("Natural disaster", UNITED_STATES, UTC, 33, "flood", "FLD",
  seed_file="floods.csv", noun="floods", day_column="day", detail_column="name",
  scheduled=False)`; `study.FLOOD = "flood"` in `ONE_KIND`; `FOLLOWS_NOUNS`; schema code 33;
  not in `TRIGGER_KINDS`, and skipped by `ask_data` as steps 24 to 28 were before step 29.
- Tests in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`.
