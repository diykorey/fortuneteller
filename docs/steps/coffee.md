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
  Its daily close is ICE's settlement at the 13:30 New York close: on 31 days since 2026-09-22 it
  is a median 0.48% from the last 5-minute bar before 13:30 (−1.3% to +0.7%), the settlement being
  set from the closing minutes' trades, not the last one.
- **Its roll, measured and recorded, not removed.** The daily series stays on the expiring contract
  until its last trading day, then rolls; a roll day's move is partly the spread between the two
  contracts (on 2026-09-21, −6.2% against the next contract's −1.5%). The figures are in
  [Precision](../precision.md)'s coffee row. Removing them for coffee alone would treat the third
  front month unlike the first two, and for all three would change gold's and Brent's cells, which
  this part forbids; Yahoo serves no prices for expired contracts either. It waits for a step of
  its own. Release days rarely fall on a roll day: none of the ISM
  survey's, the jobs report's or retail sales'; 5 of 937 CPI-type; 14 of 392 central-bank decisions.
- **Its gaps.** 19 of more than four days: 14 around Thanksgiving, Christmas and New Year, two
  around 4 July, 2003-02-14 to 02-19 (Presidents' Day and that week's blizzard), 2001-09-10 to
  09-17 (9/11) and 2012-10-26 to 10-31 (Hurricane Sandy).
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
  - `live`'s statement previews: a preview gains `KC` only if coffee *moves* on that statement's
    flow; under this outcome none does.
- **Chance, counted:** each command's chance line, as it prints it, now over 24 markets.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Coffee: a seed row, an `MVP_PRICE_SERIES` row, a 0 sign in `with_more_outcomes`, `load-prices` stores it~~ **done** 2026-11-04 (PR #260) | The tests below pass. On a copy of the store the procedure gives an empty diff, the store's counts are written in `docs/schema.md` and the scoreboard's rebuild time here |
| 2 | Results here and in [MVP results](../mvp-results.md) | Coffee's *does it move?* verdict for every flow and its `follows` answers, against the expected outcome |

*Step 1, 2026-11-04 (PR #260):*
- On a copy of the store `load-prices` stored coffee's 6,729 closes from 2000-01-03; 184,423 for the 24.
- The procedure gave an empty diff: `follows` for its four flows with and without the flag, `score`,
  `raw-move` and `surprise` for every flow, and the scoreboard's whole `data.json`, without coffee
  and the chance lines.
- The scoreboard was rebuilt in 801 s alone (967 s beside a second rebuild), under the 15-minute bar.

## How you know it is right

- `MVP_PRICE_SERIES` lists 24 markets, coffee last, and `with_more_outcomes` lists it last at 0
  (`test_the_more_outcomes_take_their_signs_by_analogy` gains `"KC": 0`).
- In `tests/test_event_flows.py`: an 08:30 New York release falls on the same day's close for
  coffee (the parametrized test's list gains `"KC"`), and a 14:00 Fed decision on the next day's,
  after its 13:30 settlement (the 14:00 test gains `"KC": date(2022, 9, 22)` and says so in its name).
- The tests that count markets count one more: `test_study_prices.py` (its bars too),
  `test_study_observations.py`, `test_study_raw_move.py` (its output slice too),
  `test_study_surprise.py` (context rows 69 → 72 and 46 → 48) and `test_scoreboard.py` (chance over
  24; walk-forward unchanged, coffee being unsigned; the seven's random stream gains coffee).
  Values that do not count markets are unchanged.

## What this part does not do

- No roll-day exclusion (above).
- No robusta, no shelf price. No breakeven (part 2b) and no signs (part 2c).

## Technical details

- **`data/seed/instruments.csv`:** after `ITB`:
  `KC,Coffee (arabica front month),commodity,global,ICE US,Front-month future; rolls five times a year.`
- **`study.py`:** `"KC": PriceSeries("KC=F", "pct", time(13, 30), NEW_YORK)` after `ITB`; the
  comment above gains "Coffee (docs/steps/coffee.md) is `KC=F`, ICE's arabica front month, at its
  13:30 settlement."
- **`flows.py`:** `with_more_outcomes` gains `"KC": 0`; its docstring "…, nor coffee
  (docs/steps/coffee.md)".
- **Docs, step 1:** this spec's step 1 note; `docs/schema.md` (30 seed rows, 24 measured, the rows per trading day, a `KC` row in the
  per-instrument table, the totals); the glossary (a `KC` entry, and `KC=F` beside `GC=F` under
  front-month futures); `README.md` (24 markets, coffee in its list); `docs/status.md`. Row 19 and `docs/precision.md`'s coffee row are written with this spec. `docs/legacy/data/` is not edited.
- **Docs, step 2:** this spec's results, `docs/mvp-results.md`, `docs/status.md`; the scoreboard as
  rebuilt by the evening job.
