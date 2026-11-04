# Coffee

> Step 19, part 2a, of the [Roadmap](../roadmap.md#next-steps-in-order), taken 2026-11-04 during
> the owner's "proceed with the project for the next 18 hours". Row 19 is amended with this spec.
> Follows [the markets people feel](markets-people-feel.md), part 1, whose template it reuses.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the [Legend](../legend.md#the-target)'s own example is "the coffee market
rose". This part adds coffee. At the end, `load-prices` stores it, and `raw-move`, `surprise`,
`follows`, the scoreboard and the triggers show it. No call is made on it.

## The way to reach it

- **The front month, as gold and Brent are read.** Coffee has no fund left on Yahoo (`JO` closed in
  2023), so it is read through `KC=F`, ICE's arabica front-month future, daily since 2000-01-03.
  Its daily close is the settlement, set at the 13:30 New York close: on 2026-10-30 and 11-03 it is
  within 0.15 cents of the last 5-minute bars, on 11-02 2.05 cents (0.7%) below the last one, as a
  settlement can be.
- **Its roll, measured.** Yahoo moves `KC=F` to the next contract on the first trading day after
  the expiring one's last trading day (ICE: one business day before the last notice day, itself
  seven business days before the month's last business day; March, May, July, September,
  December). On 2026-09-21, `KC=F` fell 6.2% while the December contract fell 1.5%.
  - Over 134 roll days since 2000, found by that rule from `KC=F`'s own trading days, the median
    move is 1.92%, against 1.23% on all days and 1.31% to 1.42% on the days either side. So the
    rule finds the roll and a roll day's move is partly the spread.
  - About five days a year: a day's median barely changes, but a month's span holds a roll about
    four times in ten. [Precision](../precision.md) records it beside gold's and Brent's, with
    taking out each roll day's move as the better approach.
  - Of coffee's 15 largest day moves, one falls on a roll day: 2000-07-20 (−12.1%), in a week of
    10% swings either way. The second largest, 2026-07-06 (+15.3%), is no roll: the December
    contract rose 17.1% too.
- **No sign, so no call.** Coffee's sign is 0 in `with_more_outcomes`, as the seven's are.

| Symbol | Market | Yahoo | Venue | Daily since |
| --- | --- | --- | --- | --- |
| `KC` | Coffee (arabica), ICE front-month future | `KC=F` | ICE US | 2000-01-03 |

## The rule, fixed before anything is measured

- **Same tests, same bars** as part 1.
- **Every existing cell unchanged,** by part 1's procedure: copy the store, run `load-prices` at
  this branch, then on that copy each command at the base commit and at this branch; drop coffee's
  lines and the chance lines; the diff must be empty.
- **Expected outcome, written first:**
  - *Does it move?*: coffee *moves* on the ISM survey's day, as corn, soybeans and gasoline do, and
    on no other flow.
  - `follows`: coffee holds walk-forward for no flow, and gets at most 2 answers in any run.
  - The scoreboard is rebuilt in under 15 minutes alone (772 s at 23 markets).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Coffee: a seed row, an `MVP_PRICE_SERIES` row, a 0 sign in `with_more_outcomes`, `load-prices` stores it | The tests below pass. On a copy of the store the procedure gives an empty diff and the scoreboard's rebuild time is written here |
| 2 | Results here and in [MVP results](../mvp-results.md) | Coffee's *does it move?* verdict for every flow and its `follows` answers, against the expected outcome |

## How you know it is right

- `MVP_PRICE_SERIES` lists 24 markets, coffee last, and `with_more_outcomes` lists it last at 0.
- An 08:30 New York release falls on the same day's close for coffee (the parametrized test in
  `tests/test_event_flows.py`), and a 14:00 Fed decision on the next day's, after its 13:30
  settlement (the 14:00 test there gains coffee).
- The tests that count 23 markets count 24: `test_study_prices.py`, `test_study_observations.py`,
  `test_study_raw_move.py`, `test_study_surprise.py` and `test_scoreboard.py`. Their other values
  are unchanged.

## What this part does not do

- No roll-day exclusion: one market would be its only case.
- No robusta, no shelf price. No breakeven (part 2b) and no signs (part 2c).

## Technical details

- **`data/seed/instruments.csv`:** after `ITB`:
  `KC,Coffee (arabica front month),commodity,global,ICE US,Front-month future; rolls five times a year.`
- **`study.py`:** `"KC": PriceSeries("KC=F", "pct", time(13, 30), NEW_YORK)` after `ITB`, and the
  comment above it.
- **`flows.py`:** `with_more_outcomes` gains `"KC": 0` and its docstring.
- **Docs:** this spec; row 19 (amended: part 2 split into 2a coffee, 2b the breakeven, 2c signs);
  `docs/precision.md` (coffee's roll); `docs/schema.md` (the seed's rows, the market count); the
  glossary (`KC`); `README.md` where it counts markets; `docs/mvp-results.md`; `docs/status.md`.
