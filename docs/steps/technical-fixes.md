# The technical review's required fixes

> Step 57 of the [Roadmap](../roadmap.md). The owner's choice of 2026-11-24 ("A then b then c";
> [Decisions](../decisions.md), 2026-11-24): after step 56, the technical review's required fixes,
> one pull request each. The technical review of 2026-11-24 (an outside read of the code, kept
> with this spec's pull request) named ten required fixes, R1 to R10; an eleventh, R11, was found
> during [step 56](honest-page.md). Terms are in the [Glossary](../glossary.md): *kind (of event)*, *first
> reaction day*, *days alone*, *lesser release*, *walk-forward*, *chance line*, *our guess*,
> *front page*, *front pull request*, *shared day*, *cell*, *kind-defining close*. The
> *reaction close* is the close of an event's first reaction day in a market.

## The goal

**In plain words:** nothing the jobs store, measure or publish can be quietly wrong because a
source sent an error, a release moved, a cell measured the move that defined it, two releases
reached a market at the same close, or a job ran beside a person's session.

At the end: the eleven fixes below are on `main`, each with the test that shows it, and the two
that change measured numbers (R3, R4) have their new numbers in Results against the outcome
written below.

## The way to reach it

Eleven pull requests, in this order, the ones that can lose an evening's work first:

1. **R7, a guess that crashes the evening.** `guess` checks each answered guess's fields (strings,
   a direction of *up* or *down*) and drops a bad one with its reason, as it drops a market it does
   not know; one bad guess never stops the run. The ledger is written before the lessons.
2. **R11, guesses held off `main`.** On an evening with nothing to score, the evening job writes
   the scoreboard and predictions pages (`docs/scoreboard/`, `docs/predicts/`, the guess ledger
   among them) and merges them once their checks pass. When the triggers' log had changed too, both
   went into the triggers' pull request, which the job never merges, so the evening's guesses
   stayed off `main` ([#433](https://github.com/diykorey/fortuneteller/pull/433), 2026-11-23). The
   pages now go in their own pull request, merged on passing checks as on any such evening, and
   the log in the triggers' one, as before. The front pull request is untouched: the job never
   merges it.
3. **R6, the evening's environment.** The evening unit loads no `.env`; the model `guess` starts
   gets only `PATH` and `HOME`, runs in an empty temporary folder, and may use web search alone.
4. **R5, the job's own checkout and store.** The units start a small script that fetches and
   switches the job's own worktree, then runs `release-day.sh` from it; the job's store and cache
   move to `~/.local/share/fortuneteller/` (copied once); the commands that only read open the store
   read-only, and a locked store prints one line instead of a trace.
   *Amended 2026-11-24, by the owner, before building the store part:* the job keeps the one store
   it shares with the sessions, since a copy would go stale on the S&P 500 companies' prices and on
   every load done by hand. Each job command waits for a held store, trying every 15 seconds for up
   to 30 minutes (`FT_DB_WAIT=1800`), then stops with one line naming the holder; outside the jobs
   it stops at once, in the same line.
5. **R1, the cache.** A reply is cached only once its parser accepted it, never TradingView's
   `no_data` or an error status, nor Nasdaq's `data: null`; it is written to a temporary file and
   moved into place.
   *Amended 2026-11-24, before building:* Nasdaq's "No record found" (code 1002) is a day without
   releases and is kept; its "Error while calling vendor" (2004) is not. The 328 refusals already
   cached are left, so nothing measured changes; [Precision](../precision.md) holds them.
6. **R2, a moved release.** Loading a flow's events replaces that flow's events, its observations
   and surprises first, in one transaction, so an event whose date moved leaves no copy behind.
   *Amended 2026-11-24, while building:* an event the source no longer gives is removed only when
   the source gives a new event of the flow within 7 days of it, a moved date; one it merely stops
   listing is kept. Replacing every event removed six speeches on a copy of the store (the Fed
   chair's of 2026-10-15, the ECB president's of 2026-10-01, 14, 17, 21 and 27): TradingView's
   current quarter lists no speeches at all on 2026-11-24, for the US or the euro area. DuckDB
   refuses a row's removal in the transaction that removed the rows referring to it, so the
   observations and surprises go first, in a transaction of their own; both are rebuilt each
   evening.
7. **R8, a call logged twice.** The call log is appended under a file lock after reading it again;
   `score` keeps one call per flow, day and market, the earliest logged.
8. **R9, float noise at the cut.** A move in basis points is rounded to six decimals.
   *Amended 2026-11-24, after measuring, the owner's choice:* rounding alone changed about 880
   lines of the scoreboard, not under 10 cells: T5YIE moves on a whole basis-point grid, so its cut
   falls on 1 bp and 1,811 of its 5,976 days sat on one side of it by float noise. A move of
   exactly the cut is now *about the same* in every market (`outcome`, and the walk-forward's
   base alike), as a lower third read from the moves includes the move it falls on.
9. **R10, the unit check.** Today the check compares a value's unit with itself. A forecast from
   TradingView's fallback, the one source not checked against the first print, is refused and
   counted when it is more than 20 times the actual print or less than a twentieth of it (both
   non-zero), so a unit slip of a hundred or a thousand is caught.
10. **R3, OPEC's cells.** OPEC's kind is the sign of Brent's move on the reaction day, so every
    cell measured from the close before contains the *kind-defining close*, and so do a market's
    cells from its own reaction close when it closes before Brent (Europe's indices at 11:30 New
    York, Brent at 14:30). Each market's cells are judged, for the chance line, the walk-forward,
    the scoreboard and *Ask*, only from its first close after Brent's reaction close; the run from
    the close before is still printed, marked *not judged*.
    *Amended 2026-11-24, in building:* "first close after" is read as at or after, so Brent's own
    cells start at its reaction close; `--after-the-day` gives the same judged run, since Europe's
    and gold's reaction closes come before Brent's; a live OPEC trigger is answered the same way;
    and the kind cell, `(the kind)` and `kind_cell`, retire, as no judged cell holds that close.
11. **R4, shared by reaction close.** Today a release's day is *shared* when another flow has a
    release on the same calendar date, each in its own zone, for every flow. From now on it is
    shared in a market when another flow's event reaches that market at the same reaction close,
    as `raw-move` already decides its busy days.

## The rule, fixed before anything is shown

R1, R2 and R5 to R11 measure nothing new; R3 and R4 change which cells are judged and which
releases count as alone. Written 2026-11-24, before any is built.

- **Expected outcome, R1, R2, R5 to R11:** every `follows`, `raw-move`, scoreboard and *Ask*
  output byte for byte the same on a copy of the store, built before and after each, with four
  exceptions, each listed: a cell where R9 moves a move of exactly the "about the same" cut to the
  other side (expected under 10 cells, on 1 bp grids alone); an event R2 removes (expected none,
  or only events a date correction moved); a call R8 counts once (expected none, the call logs
  holding no duplicate today); a forecast R10 refuses (expected none).
- **Expected outcome, R3:** no OPEC cell starting before Brent's reaction close is counted in the
  chance line, the walk-forward, the scoreboard or *Ask*; every answer OPEC's spec cites from the
  close before (energy stocks' and gasoline's day, gasoline's week and month, Brent's week) is no
  longer counted. Nothing outside OPEC changes. Every OPEC verdict that changes is listed, old
  beside new.
- **Expected outcome, R4:** US CPI of 2023-10-12 and China's of 2023-10-13 share Shanghai's close.
  Counts move both ways: a pair a day apart across time zones becomes shared, and a pair on one
  date that reaches a market at two closes becomes alone. Expected: more pairs shared than freed in
  Shanghai, Tokyo, the yuan and Europe's markets; for US flows in US markets, under 5 in 100 of
  their releases change side. Every flow's count of releases shared per market printed before and
  after, and every verdict that changes listed.
- **The bars are the flows' own:** an answer at p < 0.01 against chance, too few under 10, and
  the walk-forward rule each flow's spec wrote, unchanged; they judge the cells after R3 and R4,
  and a verdict that changes is reported, never re-argued.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | R7 | Test: an answer with a list for `market` and one with direction *sideways* drop with their reasons while a good guess is kept; the ledger is written when the lessons fail |
| 2 | R11 | The evening's script run against a scratch repository with the log and the pages both changed: two pull requests, the pages' one merged on passing checks, the triggers' left open |
| 3 | R6 | The unit has no `EnvironmentFile`; test: the model is started with only `PATH` and `HOME`, in an empty folder, with only web search allowed |
| 4 | R5 | The units run the job tree's script; the store and cache under `~/.local/share/fortuneteller/`, the copy's table row counts equal the old store's; a read-only command runs while another process holds the store; the timers reloaded, and the next evening run's pull requests opened from the new store. *Amended 2026-11-24:* the store stays shared; tests: a held store stops a command in one line naming its holder, and with a wait it opens once the holder lets go |
| 5 | R1 | Tests: `no_data`, an error status and `data: null` are not cached; a cache write killed halfway leaves no file |
| 6 | R2 | Test: an event whose date moves leaves one event, and its observations follow it; on the store copy, every removed event is one a date correction moved |
| 7 | R8 | Tests: two appends of one call log it once; a duplicated row scores once |
| 8 | R9 | Test: (2.35 − 2.34) and (0.57 − 0.56) are each exactly 1 bp; under 10 cells change, each listed |
| 9 | R10 | Tests: a fallback forecast 100 and 1,000 times the actual is refused, one 3 times it kept |
| 10 | R3 | `follows --event opec`, both runs, before and after: no cell starting before Brent's reaction close counted; every other flow's output byte for byte the same |
| 11 | R4 | Test: a US release on day D and a Chinese one at 09:30 Shanghai on D+1 share Shanghai's close; counts before and after per flow and market, US flows in US markets under 5 in 100 changed |
| 12 | Results here, the roadmap row | Every bullet of the expected outcome marked right or wrong |

## How you know it is right

- **Nothing measured changes by accident:** each step but R3 and R4 compares every output on a copy
  of the store, as the country steps did ([China](china.md), [Switzerland](switzerland.md)).
- **The unit check catches the slips that happen:** its tests use a hundred and a thousand, the
  sizes of a percent read as a fraction and of thousands read as units.
- **R3 and R4 move only what they name:** the outputs before and after differ only in OPEC's
  judged cells (R3) and in the cells whose releases are no longer alone (R4).
- **The jobs keep running:** after R5, R6 and R11, the next evening run's pull requests and the
  next morning's call are read.

## What this step does not do

The review's improvements (multiple comparisons, a grace period before a quarter is frozen, a
shortened price history refused, a flow registry), the publishing schedule (step 58), and moving
the jobs off the laptop (step 21).

## Technical details

- **Code:** `__main__.py` (`guess`, `_why_not`, `_run_model`, `_predict_release`), `sources.py`
  (`_cached`), `flows.py` (`store_events`), `study.py` (`append_calls`, `score_calls`,
  `release_move`, `shared_days`, OPEC's judged cells), `expectations.py` (`build_surprises`),
  `scripts/release-day.sh`, `scripts/systemd/`.
- **Docs:** this spec; dated amendments where a step's spec states what changes (OPEC's, the
  release-day job's, the evening score's, front staging's); `docs/precision.md` where a shortcut
  closes; the glossary; status; the changelog; roadmap row 57.

## Results

Not yet measured.
