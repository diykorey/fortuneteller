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
    *Amended 2026-11-25, in building:* who shares is unchanged (every flow but a lesser one, China's
    flows each other's), only the key: the stored close each event is paired with, so a weekend or
    a market holiday needs no rule of its own and China's weekday rule retires. `raw-move`, the
    links and `follows` leave out, in each market, the releases shared there; Canada's, Switzerland's
    and China's kinds keep a release alone in at least one market, and a trigger on one shared in a
    market says so for that market. The release-morning call still goes silent on another release
    the same calendar day, as before, by the owner's choice of 2026-11-25: for US releases in US markets the two agree but for a release
    after the close.

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

Measured 2026-11-24 and 25 on copies of the store (closes to 2026-11-23); the pull requests hold
the full lists. *Measured* below means two builds of the same command on two copies, one before
the fix and one after; *by its tests* means no build was compared.

**In plain words.** R3 and R4 changed what they were written to change; R9 changed far more than
expected. R3 took away OPEC's one answer that held, gasoline's day after *oil up*: it had been
counting the close that decides the kind. R9 changed the counts of 2,140 of *Ask*'s 5,913 cells
and 10 of their answers or verdicts, and one `raw-move` verdict, but no answer that holds. R4
changed 26 *Ask* answers and 29 `raw-move` verdicts and no answer that holds; China's and
Canada's tables keep many more releases, since a release is now left out only in the markets
where another event shares its close, not everywhere. The answers that hold went from 9 to 8.
Of the other fixes, R2, R8 and R10 were measured and changed nothing; R1, R5, R6, R7 and R11
were not compared, and are right by their tests only.

**The expected outcome, bullet by bullet:**

- **R1, R2, R5 to R11, every output the same but the four exceptions:** right where measured
  (R2, R8, R10); *wrong* for R9; not measured for R1, R5, R6, R7 and R11.
  - *R9's cells at the cut, expected under 10: wrong.* Rounding alone changed about 880 lines of
    the scoreboard's data, since T5YIE moves on a whole basis-point grid and its cut falls on
    1 bp. With the owner's choice of a move at the cut as *about the same* (given 2026-11-24 at
    21:31, written into the spec the next morning), 2,140 of *Ask*'s 5,913 cells changed their
    counts, in every kind of market; 10 changed their answer or verdict, none holding before or
    after; the 9 answers that held all still did; one `raw-move` verdict changed, T5YIE on US-ISM
    days, *moves* (p 0.0077) to *unclear* (p 0.0115). Counted from `scoreboard`'s
    `docs/scoreboard/data.json` (its *ask*, *holds* and *events*), built before and after (#460).
  - *R2's removed events, expected none or only moved ones: right.* `load-releases` on the copy
    removed none; it also found TradingView's current quarter lists no speeches at all, 6 of
    which a plain replace would have deleted (#452).
  - *R8's calls counted once, expected none: right.* `score` before and after gives the same
    rows; `data/calls.csv` holds no duplicate (#453).
  - *R10's forecasts refused, expected none: right.* `load-surprises` on the copy: 330 fallback
    fills, all jobless claims, none out of scale (#454).
  - *Not measured:* R1 changes what the cache keeps from now on and leaves its 324 Nasdaq
    refusals in place (counted in [Precision](../precision.md)); R5, R6, R7 and R11 change the
    jobs, not a command that measures. Each is right by its tests (#445 to #451, #459).
- **R3, no OPEC cell from before Brent's close counted, the cited answers gone, nothing outside
  OPEC: right.** `follows --event opec`, both runs, before and after: energy stocks' and
  gasoline's day, gasoline's week and month and Brent's week are no longer counted, and
  gasoline's day after *oil up*, 20 right of 31 replayed, no longer holds. 21 OPEC verdicts
  changed:

  | kind, span, market | before | after |
  | --- | --- | --- |
  | oil up, day: Brent / gasoline / energy stocks / T5YIE | up, holds (the kind) / up, holds / up, doesn't hold / up | can't say, all four |
  | oil up, week: Brent / energy stocks / gasoline | up / up / up | can't say |
  | oil up, month: Brent / energy stocks | up / up | can't say |
  | oil up, month: gasoline | up, 13 replayed, 9 right | up, 14 replayed, 8 right |
  | oil down, day: Brent / energy stocks / gasoline | down | can't say |
  | oil down, day: US 10-year / 5-year | can't say | down |
  | oil down, week: Brent / energy stocks / gasoline / T5YIE | down | can't say |
  | oil down, week: the dollar | can't say, 42 replayed, doesn't hold | can't say, 3 replayed |
  | oil down, month: defence stocks | can't say | down |

  The scoreboard's data, built before and after, differs only in OPEC's *Ask* cells, the
  gasoline answer leaving *holds*, and the dropped `kind_cell` key: every other flow's *Ask*
  cells, *events* (with each flow's `raw-move`) and links are the same (#455).
- **R4, the named pair shared, more shared than freed abroad, US flows in US markets under 5 in
  100: right.** Counted on the copy with a one-off script that reads every flow's releases and
  each market's closes under both rules (in #461's description), in release-markets: one release
  in one market.
  - *The named pair:* US CPI of 2023-10-12 and China's of 2023-10-13 share Shanghai's close, by
    a test.
  - *More shared than freed* in each of Shanghai (221 and 180), Tokyo (278 and 184), the yuan
    (268 and 124), the DAX, the Euro Stoxx 50, the Stoxx 600, the FTSE 100 and the SMI (292 to
    323 and 127 to 149): the flows other than the four company flows, which go the same way.
  - *US flows in US markets:* 0.7 in 100 changed side across them, and 4.0 in 100 for the one
    highest, the Fed chair's speeches (fomc 0.1, retail 0, pce 0.7, gdp 0, ism 1.2, claims 0).
  - *Every flow's count, shared before and after,* in release-markets: boc 1,250 and 1,186; boe
    1,585 and 1,908; boj 1,413 and 1,473; cacpi 1,346 and 1,303; claims 9,219 and 9,726; cncpi
    3,428 and 3,523; cnip 3,032 and 3,144; cnpmi 5,040 and 5,268; cntrade 2,369 and 2,550; decpi
    2,117 and 2,263; ecbchief 4,147 and 4,440; fedchair 2,482 and 2,611; fomc 1,919 and 2,042;
    gdp 1,071 and 1,094; hicp 2,918 and 2,914; ifo 256 and 266; ism 1,899 and 1,963; pce 2,348
    and 2,490; retail 1,634 and 1,569; snb 859 and 1,050; zew 1,623 and 1,626; the company flows
    earnings 24,505 and 26,128, earnings500 324,330 and 358,353, additions 2,081 and 2,013,
    splits 1,039 and 1,120. `surprise --event <flow>` now prints each market's count.
  - *Verdicts:* the 8 answers that hold are unchanged; `follows` for China's and Canada's flows
    counts more releases (the survey 59 to 175, CPI 116 to 183, output 110 to 169, trade 127 to
    176, Canada's CPI 189 to 213), nothing holding before or after; 26 *Ask* answers and 29
    `raw-move` verdicts in ten lesser flows changed, none holding, each listed in #461.
- **The bars are the flows' own:** unchanged; no verdict is re-argued.

**The jobs keep running:** the evening run of 2026-11-25, 01:00 to 01:34 (`systemctl --user show
fortuneteller-evening-score`), the first with R5's own checkout, R6 and R11: the pages merged
themselves (#456), the triggers' log was left open (#457), the front page's proposal waited for
the owner (#458), and 17 guesses were written to `docs/predicts/our-guesses.csv` with web search
alone. R5's wait for a held store (#459) merged after it and is checked by its tests only.
