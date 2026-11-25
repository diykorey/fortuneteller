# Crypto's weekend closes

> Step 59 of the [Roadmap](../roadmap.md). The owner's choice of 2026-11-24, after step 58
> ([why](../decisions.md#2026-11-24-bitcoins-and-ethers-weekend-closes-from-yahoo-after-step-58-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *our guess*, *weekend close*, *draft*.

## The goal

**In plain words:** bitcoin and ether trade every day, so a guess about them made on a Saturday
or Sunday starts from that weekend's price, not Monday's, and counts like any other guess.

At the end: the store keeps bitcoin's and ether's Saturday and Sunday closes from Yahoo; a
bitcoin or ether guess stated from 2026-11-28 is graded from the first close after it was made,
a weekend close included, and one stated at a weekend counts in every record; every measured
number is what it was.

## The way to reach it

Yahoo's `BTC-USD` and `ETH-USD` send a bar for every UTC day, and `sources.parse_daily_bars`
drops every bar dated on a weekend, for all markets ([precision](../precision.md), *Bitcoin*).
Since [step 58](publishing-schedule.md) guesses are drafted at weekends too; each one's baseline
(`guess_start`, [step 56](honest-page.md)) is rolled to Monday, as no weekend close is stored,
and from 2026-11-28 a weekend guess counts in no record (`weekend_draft`), since it starts from
the same close as Friday's.

Four changes:

- **Stored, for crypto only.** The loader keeps weekend bars for bitcoin and ether, the
  markets whose Yahoo day is a UTC day (*crypto markets*: `BTC`, `ETH`); every other market still
  drops them.
- **Measured as before.** `study.stored_closes` returns weekday closes unless asked for every
  day, and the two other readers of `daily_bars` (`shared_in`'s query and the scoreboard's
  *data to* date) read weekdays only. So every release's move, every base rate, every replay and
  every stated forecast reads exactly the closes it read before.
- **Guesses graded from the next close.** For a crypto guess stated from 2026-11-28,
  `guess_start` no longer rolls a weekend day to Monday, and `grade_guesses` reads its market's
  every-day closes. A guess drafted at 14:00 New York on Saturday (19:00 UTC) starts from
  Saturday's close at 23:59 UTC. Weekday crypto guesses already start the same day (bitcoin's
  close is at 23:59 UTC, after 14:00 New York), so nothing changes for them; a weekday guess
  graded over a span holding a weekend still ends on the last close on or before its end date,
  a weekday, as the guesser's end dates must be.
- **Counted.** `weekend_draft` leaves crypto guesses out: from 2026-11-28 a Saturday or Sunday
  crypto guess counts in every record, every other weekend guess still in none.

The base rate printed with a guess still counts weekdays from its start, from weekday closes:
the record behind it was measured that way, and this step changes no measurement.

Rows stated before 2026-11-28 keep their rule: the one open crypto guess made at a weekend,
bitcoin of Sunday 2026-11-22, on the front page "than on November 23", still starts from
Monday 2026-11-23's close.

## The rule, fixed before anything is measured

Written 2026-11-25, before building.

- **The store:** on a copy of the store, `load-prices` adds bitcoin's and ether's weekend closes
  and no other market's: Yahoo sent 1,272 weekend bars for `BTC-USD` (from 2014-09-17) and 944 for
  `ETH-USD` (from 2017-11-09) on 2026-11-25, so the build day's counts are those plus 2 for each
  weekend since, and every other market's row count is unchanged.
- **Nothing measured changes:** on that copy, before and after, these print the same, byte for
  byte, apart from the time written: `scoreboard` (its `data.json`), `follows`, `raw-move` for
  every flow, `docs/predicts/forecasts.csv` and the base rates in `our-guesses.csv`.
- **The ledger:** no grade in `our-guesses.csv` changes; no open row's baseline changes, as no
  crypto row is stated from 2026-11-28 yet.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | The loader, the readers and the guesses | Tests: a Yahoo reply with weekend bars keeps them for `BTC-USD` and `ETH-USD` and drops them for `SPY`; `stored_closes` gives weekdays unless asked for every day; a crypto guess made at 14:00 New York on Saturday 2026-11-28 starts from that Saturday's close and counts in the records; the same guess on `SPY / ES` starts Monday and does not count; bitcoin's guess of Sunday 2026-11-22 still starts Monday; a crypto guess made on Friday starts Friday |
| 3 | The store compared | The rule's three bars checked on a copy of the store, the counts and every compared output in the pull request |
| 4 | The docs amended with a date | `precision.md` (*Bitcoin*, *Ether*), `schema.md` (`daily_bars`), the glossary's *bitcoin*, *ether* and *weekend close*, and the weekend lines of `publishing-schedule.md`, `honest-page.md` and `guess-ledger.md` |
| 5 | The first weekend | After the build is merged, the store loaded on a weekday holds the Saturday and Sunday before it for both markets, matching Yahoo's bars; any crypto guess drafted that weekend shown with its baseline in Results |

## How you know it is right

- **A leak into the measurements would show as a changed output:** step 3 compares every
  measured output before and after on the same store.
- **A guess that sees its baseline would show in the tests:** the Saturday guess at 14:00 New
  York starts from the close after it, 23:59 UTC that day, not the one before.
- **A weekend close in the wrong UTC day would show as two bars on one date,** which the parser
  already rejects, or as a Monday close equal to Sunday's, which step 5 checks against Yahoo.

## What this step does not do

It does not measure crypto's moves around releases or hacks with weekend closes (each would be a
new measurement with its own bars), add a crypto source, let a guess end on a weekend, or change
the base rates' weekday count.

## Technical details

- **Code:** `sources.parse_daily_bars` (`weekends`), `study.load_daily_bars` and
  `study.stored_closes` (`weekends`), `study.CRYPTO`, the query in `shared_in`, the
  `data_until` query in `__main__.py`, `guess_start`, `grade_guesses`' closes in `_guess`, and
  `weekend_draft`; tests beside the parser's and the ledger's.
- **Docs:** this spec, the amendments of step 4, status, the changelog, roadmap row 59.

## Results

Not yet measured.
