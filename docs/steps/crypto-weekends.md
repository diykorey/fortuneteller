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

Yahoo's `BTC-USD` and `ETH-USD` send a bar for every UTC day (their close is the UTC day's last
price, [precision](../precision.md), *Bitcoin*), and `sources.parse_daily_bars` drops every bar
dated on a weekend, for all markets, as well as today's, still open; it already rejects two bars
on one date.
Since [step 58](publishing-schedule.md) guesses are drafted at weekends too; each one's baseline
(`guess_start`, [step 56](honest-page.md)) is rolled to Monday, as no weekend close is stored,
and from 2026-11-28 a weekend guess counts in no record (`weekend_draft`), since it starts from
the same close as Friday's.

Four changes:

- **Stored, for crypto only.** The loader keeps weekend bars for bitcoin and ether, the
  markets whose Yahoo day is a UTC day (*crypto markets*: `BTC`, `ETH`); every other market still
  drops them.
- **Measured as before.** `study.stored_closes` returns weekday closes unless asked for every
  day, and the two other readers of `daily_bars` read weekdays only: `shared_in`, which finds the
  releases whose reaction close another flow shares (step 57's R4), and the scoreboard's *data
  to* date, the latest stored close (`data_until`). So every release's move, every base rate, every replay and
  every stated forecast reads exactly the closes it read before.
- **Guesses graded from the next close.** For a crypto guess stated from 2026-11-28 (its
  `stated` column, the New York day it was drafted),
  `guess_start` no longer rolls a weekend day to Monday, and `grade_guesses` reads its market's
  every-day closes. A guess drafted at 14:00 New York on Saturday (19:00 UTC) starts from
  Saturday's close at 23:59 UTC. A weekday crypto guess drafted at 14:00 New York already starts
  that day (bitcoin's close is at 23:59 UTC, after it), so nothing changes for it; one made after
  19:00 New York in winter (00:00 UTC), as none is under step 58's schedule, would start the next
  UTC day, a Saturday after a Friday; a weekday guess
  graded over a span holding a weekend still ends on the last close on or before its end date,
  a weekday, as the guesser's end dates must be.
- **Counted.** `weekend_draft` no longer matches crypto guesses: from 2026-11-28 a Saturday or
  Sunday crypto guess counts in every record step 58 leaves weekend guesses out of
  (`guess_record`, `excess_record`, `counted_guesses`, `evenings_against`), every other weekend
  guess still in none.

The base rate filled beside a guess is read from weekday closes, as the record behind it was
measured, over the weekdays after its start to its end date (`_weekdays_between`). A Saturday or
Sunday start therefore counts the Monday after it, which a Monday start does not: a weekend
crypto guess's base rate is over one weekday more than under today's rule.

Both rules are read when the ledger is read, by the `stated` day, so a crypto row drafted on
2026-11-28 or 29 before the build is merged is graded and counted by them all the same. Its base
rate, filled when it was drafted under the old start, is not: the build is merged before the
first Saturday draft (14:00 New York, 2026-11-28), and if it is not, the base rates of those rows
are filled again at the build and listed in Results.

Rows stated before 2026-11-28 keep their rule: the one open crypto guess made at a weekend,
bitcoin of Sunday 2026-11-22, on the front page "than on November 23", still starts from
Monday 2026-11-23's close.

## The rule, fixed before anything is measured

Written 2026-11-25, before building; *amended 2026-11-25, after the goldfish review, before
building.*

**Expected outcome:** the three bars below all hold.

- **The comparison:** two copies of the job's store, taken together; within the same hour,
  `load-prices` with `main`'s code on one (*before*) and with this step's on the other
  (*after*), so both hold the same weekday closes.
- **The store:** *after* holds bitcoin's and ether's weekend closes and *before* none, and every
  other row is the same in both, weekday crypto rows included. Yahoo sent 1,272 weekend bars for
  `BTC-USD` (from 2014-09-17) and 944 for `ETH-USD` (from 2017-11-09) on 2026-11-25 (counted with
  `fetch_daily_bars` and the UTC date of each bar with a close), so the build day's counts are
  those plus one for each weekend day completed since; a weekend day still open is not stored.
- **Nothing measured changes:** on the two copies these print the same, byte for byte, apart
  from the time written: `scoreboard` (its `data.json`), `follows`, `raw-move --event` for each
  flow `raw-move` takes, `docs/predicts/forecasts.csv` (written by `scoreboard`), and every base
  rate of `our-guesses.csv` filled again from blank by `with_base_rates`, called from a short
  script with no model, the one way the ledger's base rates are filled.
- **The ledger:** no grade in `our-guesses.csv` changes, and no open row's start changes except
  crypto rows stated from 2026-11-28 at a weekend, each listed with its old and new start.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | The loader, the readers and the guesses | Tests: a Yahoo reply with weekend bars keeps them for `BTC-USD` and `ETH-USD` and drops them for `SPY`; `stored_closes` gives weekdays unless asked for every day; with a Sunday crypto close stored, `shared_in` and `data_until` read as without it; a crypto guess made at 14:00 New York on Saturday 2026-11-28 starts from that Saturday's close, is graded from it and counts in `guess_record`, and its base rate is read from weekday closes over the weekdays after that Saturday; the same guess on `SPY / ES` starts Monday and does not count; bitcoin's guess of Sunday 2026-11-22 still starts Monday; a crypto guess made at 14:00 New York on Friday 2026-11-27 starts Friday |
| 3 | The store compared | The rule's three bars checked on a copy of the store, the counts and every compared output in the pull request |
| 4 | The docs amended with a date | `precision.md` (*Bitcoin*, *Ether*), `schema.md` (`daily_bars`), the glossary's *bitcoin*, *ether* and *weekend close*, and the weekend lines of `publishing-schedule.md`, `honest-page.md` and `guess-ledger.md` |
| 5 | The first weekend | The store loaded on the Monday after the first weekend after the merge holds that Saturday's and Sunday's closes for both markets, each equal to Yahoo's bar for its UTC day as fetched that Monday, and Sunday's differs from Monday's; each crypto guess drafted that weekend listed in Results with its `made` and its start, the first close after `made` |

## How you know it is right

- **A leak into the measurements would show as a changed output:** step 3 compares every
  measured output before and after on the same store.
- **A guess that sees its baseline would show in the tests:** the Saturday guess at 14:00 New
  York starts from the close after it, 23:59 UTC that day, not the one before.
- **A weekend close in the wrong UTC day would show as two bars on one date,** which the parser
  already rejects, or as a Monday close equal to Sunday's, which step 5 checks against Yahoo.
- **A base rate read from every day's closes would show as a changed base rate:** step 3 fills
  every base rate again on both copies, and step 2 tests a weekend crypto guess's.
- **A *data to* date read from a weekend close shows in step 2's test**, whatever day step 3 runs on.

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
