# Floods

> Step 30 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19 by the owner as "floods and droughts". Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** after a costly US flood began, what followed for crops, fuel, insurers and the
indexes, over the day, the week and the month? Step 28 asked this of hurricane landfalls; the
floods and droughts it left out come here.

At the end: `follows --event flood` prints what followed each dated flood on NOAA's billion-dollar
list, measured as [step 17](what-follows.md) measures a kind, against the rule below written
first. It serves the [Legend](../legend.md#the-target)'s reader who brings a flood headline and
asks what followed such floods before. It cannot be a call on the day: a flood is known to be a
billion-dollar one only weeks later, so the answer is about floods that turned out costly, and the
flow takes no trigger.

## The way to reach it

- **The source: NOAA's Billion-Dollar Weather and Climate Disasters list, 1980 to 2024**: every
  US event of a billion dollars or more (*CPI-adjusted*: in today's dollars), each with its type,
  begin and end day. NOAA's climate data centre (NCEI) stopped updating it in May 2025 and keeps
  it archived. NCEI's address answered HTTP 503 on 2026-11-19, so the copy read is the Wayback
  Machine's of 2025-01-27 23:34:39 UTC
  (`web.archive.org/web/20250127233439/https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv`),
  sha256 `67831180c9f1f348ea560acd291e84a0e2410f6fa3e129fa8297f114fd8537e9`, 403 events from 1980
  to 2024. Nobody here picks the events.
- **The kind: a flood with a day.** Every row whose `Disaster` column is `Flooding` (45), its day
  the `Begin Date`; a `Severe Storm` or `Tropical Cyclone` row named "… and Flooding" is not one:
  the column is the rule, not the name. A row that begins on the first of a month and lasts 30
  days or more is a season's label, not a day, and is left out: six (the Gulf States 1982-12-01,
  California 1995-01-01, the Midwest 2008-04-01, the Northeast 2010-03-01, the Mississippi
  2011-04-01, the Missouri 2011-05-01). Two that begin on a first and last days are kept: the West
  Coast 1997-01-01 (10 days) and South Carolina 2015-10-01 (4 days). **39 floods**, 1980-04-10 to
  2024-06-16. One kind, `flood`.
- **Droughts are left out by the same rule.** All 32 of the list's droughts begin on the first of
  a month and last 91 days or more (212 at the median): seasons, not days anyone knew a drought
  had begun. A call is made from the actual once it lands. A drought day read from the weekly US
  Drought Monitor would need a threshold chosen here: its own spec, if ever.
  *Amended 2026-11-19:* [step 28](weather.md) left floods out as having "no single start day in a
  free record"; NOAA's list gives one for 39 of them.
- **No crop-region filter.** The list has no state or region column, so a filter would be read
  from the names, by hand. The crops are among the markets, so the crop question is still asked of
  every flood. *Amended 2026-11-19*, against the roadmap row's "in crop-growing regions".
- **The hour:** the list gives a day, no hour. The event is placed at 04:00 UTC of its begin day,
  war's and the hacks' rule ([war](war.md)): it reacts that day on every market whose close falls
  after 04:00 UTC (New York's, Europe's, Tokyo's at 06:00 UTC), and on the currencies, whose close
  is 00:00 London, the next day. A weekend or holiday flood reacts on the next close.
- **The flow:** a `DatedShockFlow` (the seed-file flow of the one-kind shocks), `flood`, code 33,
  event type `Extreme weather / climate policy` (*amended 2026-11-19, in step 1:* not `Natural
  disaster`, the landfalls', since two flows of one country may not share an event type), no surprise, unscheduled, lesser by its
  default, one kind in `study.ONE_KIND`. No new market.

## The rule, fixed before anything is shown

- The source, the kind and its season rule, the hour and step 17's bars, unchanged by what the
  run shows. *Both runs* means `follows --event flood` (spans from the close before) and
  `follows --event flood --after-the-day` (from the reaction close).
- **Expected outcome, written first:**
  - The header: `follows: 39 floods 1980-04-10 … 2024-06-16: 39 floods`.
  - Arithmetic, not a finding: an answer needs 10 earlier events, so 39 floods give at most 29
    graded walk-forward, under the 30 *holds* needs. **Nothing can hold, on any market or span.**
    Floods by market, from its first close (before overlap): the S&P 500, the 10- and 5-year
    yields, the dollar index, the Nasdaq and the Nikkei 39; the FTSE 36; VIX and the DAX 34;
    Allstate 33; the yen 29; gold, energy stocks, utilities and coffee 26; the euro, the pound,
    Europe's shares, defence, homebuilders and the breakeven 25; the Euro Stoxx 50, Brent,
    gasoline and natural gas 24; the three crops 22; bitcoin 19; ether 11; Coinbase 7.
  - On all history: no more answers than the chance line `follows` prints plus 2, in each run.
  - Corn, wheat, soybeans, gasoline, natural gas, Brent, energy stocks and Allstate on the day,
    the week and the month, in both runs: no answer (*can't say*, or *too few* where a span keeps
    fewer than 10). An answer, up, down or about the same, is a miss. A billion-dollar flood is
    local, and is known to be one only later.
  - Every other flow's `follows` and `raw-move` output unchanged byte for byte on a copy of the
    store, before and after; the scoreboard's events gain the floods' entry (32 → 33), and its
    three chance counts (raw-move, surprise, walk-forward) rise by the floods' cells alone,
    written before and after.
- **Outside the rule, recorded:** `raw-move --event flood`, and the floods' days shared with
  another flow on the same day (`scripts/shared_days.py flood`, which counts the same day only).

*Written 2026-11-19, before `follows` or `raw-move` ran on these floods; the counts above are from
the list and the markets' first closes.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seed and the flow: `scripts/noaa_floods.py` writes `data/seed/floods.csv` from the local copy; the `flood` flow in `follows`; the before-and-after outputs of every flow on a copy of the store~~ **done** 2026-11-19: 39 floods; every other flow's output byte-identical, the scoreboard 32 → 33 events and its raw-move chance 857 → 887 cells, the floods' 30 ([evidence](floods-steps.txt)) | The tests below pass; `follows --event flood` prints the header above; the outputs kept in `docs/steps/floods-steps.txt` |
| 2 | ~~Results~~ **done** 2026-11-19, [below](#results) | Each bullet of the rule judged right or wrong in Results, with its numbers and the command that prints them; a goldfish review, each finding fixed or answered in the PR |

## How you know it is right

- **The seed, by a test:** 39 rows; every row of the copy whose `Disaster` is `Flooding` is in it
  but the six named above; each row's day is its `Begin Date` (the Midwest's 2024-06-16, not its
  end, 2024-06-23); its cost is the copy's CPI-adjusted figure.
- **The hour, by a test:** a flood dated Sunday 2024-06-16 reacts on Monday 2024-06-17 on the S&P
  500; one dated Tuesday 2023-07-11 reacts that Tuesday on the S&P 500 and the Nikkei, and on
  Wednesday on the euro.
- **No trigger, by a test:** a `flood` trigger is void, its flow not one `triggers` reads.
- **By hand:** the copy's `Flooding` rows counted by its `Disaster` column (45), in the evidence.

## What this step does not do

- It measures no drought, adds no market, and takes no trigger.
- It adds the floods to `follows` only; the page's *Ask the fortune teller* section gains them in
  a later step. *Amended 2026-11-19:* [step 29](ask-phase-5.md), before its step 2.

## Technical details

- `scripts/noaa_floods.py PATH` reads the local copy (`python -I`), keeps the `Flooding` rows but
  the season rule's, and writes `day,name,cost` (`day` the `Begin Date`, `cost` the CPI-adjusted
  millions).
- `flows.FLOOD_FLOW = DatedShockFlow("Extreme weather / climate policy", UNITED_STATES, UTC, 33, "flood", "FLD",
  seed_file="floods.csv", noun="floods", day_column="day", detail_column="name",
  scheduled=False)`; `study.FLOOD = "flood"` in `ONE_KIND`; its noun in `FOLLOWS_NOUNS`; not in
  `TRIGGER_KINDS`; skipped by `ask_data` (the page's data) with a comment naming this step.
- **Docs:** `docs/schema.md` (code 33, the detail), `docs/glossary.md` (*Billion-dollar list*,
  *Flood*), status, roadmap, changelog. Tests in `tests/test_seed_data.py`,
  `tests/test_what_follows.py`, `tests/test_triggers.py`.

## Results

*2026-11-19.* Every line quoted is in [the evidence](floods-results.txt): a copy of the store of
the 2026-11-18 evening with the floods loaded, the whole output of `follows --event flood` (from
the close before), `follows --event flood --after-the-day` (from the reaction close), `raw-move
--event flood` and `scripts/shared_days.py flood`.

**In plain words:** after a billion-dollar US flood began, corn, wheat, soybeans, gasoline, natural
gas, oil, energy stocks and Allstate's shares gave no answer over the day, the week or the month,
counted from either close, and on the floods' own days none of them moved more than on ordinary
days by the bar: corn moved somewhat more (*unclear*), the rest no more. Across every market, one answer in each run, within the luck the chance line
allows; with 39 floods nothing could be graded enough to hold. The expected outcome held.

- **The header, as expected:** `follows: 39 floods 1980-04-10 … 2024-06-16: 39 floods`
  (`follows --event flood`). Right.
- **The arithmetic:** right. No cell reaches 30 graded: the most is 7 from the close before
  (wheat's day) and 5 from the reaction close (Europe's shares' day). Every market's floods on the
  day, counted plus out and holes, are the counts the rule lists, in both runs. From the close
  before (`follows --event flood`) the S&P 500, the 10- and 5-year yields, the dollar index and the
  Nasdaq counted 39, the Nikkei 37 (2 in holes), the FTSE 35 (1 in a hole), Allstate 33, the crops
  22; from the reaction close the Nikkei 36 (3 in holes) and the FTSE 36. Coinbase counted 7 and is
  *too few* on every span, in both runs.
- **Walk-forward: nothing holds** (both runs). Right.
- **On all history, against the chance line plus 2** (each run; chance about 2.7, so a bar of 4.7):
  from the close before **1 answer**, bitcoin *about the same* on the day, 3 up, 12 the same, 4
  down of 19, chance 0.0074 (1 graded, *too few*); from the reaction close **1**, Europe's shares
  (SXXP) *up* on the day, 17 up, 6 the same, 2 down of 25, chance 0.0011 (5 graded, 4 right, *too
  few*). Neither marked by the placebo. Right in both.
- **Corn, wheat, soybeans, gasoline, natural gas, Brent, energy stocks and Allstate on the day, the
  week and the month, both runs:** all 48 cells *can't say*; none *too few*. Right.
- **Every other flow's rows** ([step 1's evidence](floods-steps.txt), each file compared byte for
  byte by a one-off Python read of both, `data.json`'s `chance` read the same way): byte-identical;
  the scoreboard gained the floods' entry (32 → 33 events). The floods' own cells: 30 in raw-move
  (`raw-move --event flood` prints 30 verdicts, Coinbase's *too few* not counted), none in surprise
  (a flood has no surprise rule) and none in walk-forward (the scoreboard grades only the flows
  `live` calls). So raw-move's count rose 857 → 887, surprise stayed 372 and walk-forward 82. Right.
- **The size of the move** (`raw-move --event flood`, outside the rule, recorded): 28 markets
  *doesn't*, 2 *unclear* (corn, ratio 1.41, p 0.0921; the breakeven, 1.25, 0.2140), Coinbase *too
  few*; none *moves*. Allstate's lone flood days move less than its ordinary days (ratio 0.63).
- **Days shared with another flow** (`scripts/shared_days.py flood`): 13 of the 39, CPI and the
  ECB president's statements on 3 each, jobless claims and the Fed chair's statements on 2, seven
  others on 1; none with a hurricane landfall on the same day.

The expected outcome was **right on every count**.
