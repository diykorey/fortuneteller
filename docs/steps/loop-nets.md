# The loop's safety nets

> Step 46 of the [Roadmap](../roadmap.md). Terms are in the [Glossary](../glossary.md):
> *release-day job*, *evening score*, *shadow run*, *outside timer*, *safety net*, *the gate*.
> Chosen 2026-11-21 by the owner
> ([Decisions](../decisions.md#2026-11-21-the-postponed-list-worked-through-the-page-first-by-the-owner)):
> "an alert when a release day goes unlogged and a fallback when a source fails", wanted before
> the jobless claims and PCE of Wednesday 2026-11-25.

## The goal

**In plain words:** when the laptop misses a release morning, or the outside timer never starts
the runner, an issue says so the same day; and a source that fails for a minute no longer fails
the run.

Today a failure the job sees opens an issue, but a job that never runs says nothing: the jobs
report of 2026-11-06 was missed under a closed lid, and on 2026-11-17 the outside timer's evening
ask was off and nobody noticed. And one HTTP 500 fails a whole run: FRED's on 2026-11-19 (issue
#371) stopped the evening before any price loaded. The gate needs four straight weeks of release
days logged within 15 minutes, none missed.

## The way to reach it

- **Each machine watches the other,** since one that sleeps cannot report itself.
  - *The runner's morning watches the laptop.* `live` calls only releases of 08:30 New York
    (`flows.RELEASE_TIME`), so the laptop's rows are due by 08:45. After its own `live`, if the
    runner logged rows, it waits until 08:45 New York and fetches `main` and every `calls-*`
    branch. Each row it logged (flow, day, market) that none of them holds is listed in the issue
    *The laptop did not log DAY's calls*. A run that logged nothing checks nothing.
  - *The runner's morning watches its own evening.* It lists the jobs workflow's
    `workflow_dispatch` runs. If none was created between 22:00 UTC of the weekday before and
    06:00 UTC today (the evening ask is at 23:30 UTC), it opens *The runner's evening was not
    started on DAY*, DAY the weekday before. This is the 2026-11-17 case.
  - *The laptop's evening watches the runner's morning.* At the end of `score`, run on its own
    day (before midnight New York), if no `workflow_dispatch` run was created between 11:00 and
    17:00 UTC that day, it opens *The runner's morning was not started on DAY*. A catch-up after
    midnight skips this check rather than check the wrong day. It never fails the evening.
  - All four checks are in `fortuneteller`'s two commands below, which read files, so tests can
    replay the incidents; the workflow and the script only fetch the files and open the issue.
    Both machines down at once is not caught.
- **A source that fails is asked again,** in one helper every fetch in `sources.py` uses: after an
  HTTP 5xx, a timeout or a broken connection, it prints `retrying SOURCE after REASON, in N s` and
  asks again after 30 seconds, then a last time after 90. A 4xx is never retried (Nasdaq's 403 of
  2026-11-10 was not a blip). A process waits at most 300 seconds in all; a wait that would go
  past it is not taken, and the failure raises at once. A failure that is not retried, or still
  fails, raises the source's own error as today (`FredError`, `YahooError`, ...), so a source down
  for good fails the run at most five minutes later than today, and its issue opens as now.
- **This changes step 21's shadow rule.** *A shadow run opens no pull request and no issue* gets a
  dated amendment in [the loop off the laptop](loop-off-the-laptop.md): the runner's morning opens
  the two issues named above, nothing else.

## The rule, fixed before measuring

- **No bar on a market:** nothing is measured; the nets change no row, call or grade.
- **Expected outcome:** on the first two weekdays from 2026-11-24 with a release `live` calls, both
  machines run and none of the three issues above opens. An issue opened on a day both machines
  ran makes it *wrong*, written with its number.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The retry~~ **done 2026-11-23**; [results](#results) | Tests: a fetch answered 500, 500, then 200 returns the 200 after two printed retries; answered 500 three times raises the source's error; a 403 or 404 is asked once; with less budget left than the next wait, the failure raises at once |
| 2 | ~~The watches~~ **done 2026-11-23**; [results](#results) | Tests replaying the incidents: `unlogged` with the runner's claims rows of 2026-11-19 against `main` before PR #364 prints the five; after it, nothing. `unstarted --evening 2026-11-17` with that week's run list prints it; with 2026-11-18's, nothing. `unstarted --morning` with no run that day prints it. `bash -n scripts/release-day.sh` passes |
| 3 | Live | Results: the two days, each machine's morning and evening, and the issues opened |

## How you know it is right

- **The incidents are caught:** step 2's tests use the real run list and rows of those days.
- **No false alarm:** the expected outcome above.
- **Nothing measured changes:** `follows`, `score` and the scoreboard are not touched; CI's tests
  pass unchanged.

## What this step does not do

No other source for Nasdaq, no move off the laptop (step 21), no change to what `live` or `score`
decide, no popup from the runner, no check of the laptop's evening.

## Technical details

- **Commands:** `fortuneteller unlogged DAY OURS THEIRS...` prints each (flow, market) row of DAY
  in the runner's `data/calls.csv` (`OURS`) that no `THEIRS` file holds (each written by `git
  show`). `fortuneteller unstarted --morning|--evening DAY RUNS` reads `gh run list --json
  createdAt,event` saved to `RUNS` and prints the missing run, if any. Both exit 0.
- **Retry:** `_ask(request, timeout, source)` in `sources.py`; `RETRY_WAITS = (30, 90)`,
  `RETRY_BUDGET = 300` seconds per process; tests patch the sleep.
- **Files:** `src/fortuneteller/sources.py`, `__main__.py`, `.github/workflows/jobs.yml` (its
  token gains `issues: write`), `scripts/release-day.sh`, tests. The laptop runs the script from
  the main checkout, which is pulled after the merge.
- **Docs:** this spec, step 21's amendment, a decisions entry, the glossary (*safety net*),
  roadmap row 46, status, changelog.

## Results

### Steps 1 and 2: the retry and the watches, 2026-11-23

**In plain words:** a source that answers 500 is asked again twice and the third answer is used;
a 403 or 404 is asked once. Replayed on the real rows and runs, the watches find the five claims
rows of 2026-11-19 that `main` lacked until PR #364, and the runner's evening of 2026-11-17 that
the outside timer never asked; they find nothing on the days that went right. Nothing measured
changed: the tests that were there pass unchanged.

The tests are in `tests/test_loop_nets.py`; their real data, trimmed, in `tests/data/`.

- **The retry.** Every request in `sources.py` (FRED, Yahoo, the Cleveland Fed, the Fed's pages,
  Nasdaq and TradingView, Umami) goes through `_ask`, and each still raises its own error with
  today's words. FRED answered 500, 500, 200 returns the 200 after waits of 30 and 90 s, printing
  `retrying FRED after HTTP 500, in 30 s` and `..., in 90 s`; 500 three times raises `FredError`
  with the key `<redacted>`, as before, and no retry line holds it. Yahoo's 403 and 404 are asked
  once and raise `YahooError` without a wait. A timeout and a refused connection are asked again,
  the line naming only the failure's kind (`TimeoutError`, `ConnectionRefusedError`), since its
  text can hold the URL with FRED's key. With 29 s of the budget left a 503 raises at once; three
  failing fetches in one process wait 30, 90, 30, 90 and 30 s, 270 in all.
- **`unlogged`.** The runner's rows of 2026-11-19 (run 44524466043's artifact, logged 13:30 UTC)
  against `main` before PR #364 print the five claims rows, UST10Y / ZN, DXY, EURUSD, UST5Y / ZF and
  XLU; against `main` after it (the laptop's rows, logged 14:07 UTC), nothing, nor with a calls
  branch holding them, nor with an empty file beside them, as `git show` leaves for a branch
  without the log.
- **`unstarted`.** On the real runs of 2026-11-16 to 2026-11-20: `--evening 2026-11-17` prints the
  evening not started (only the schedule ran that night); `--evening 2026-11-18` prints nothing (the
  timer's 23:30 UTC ask); `--morning 2026-11-16` prints the morning not started; each morning of
  2026-11-17 to 2026-11-20 is found started.
- **The script.** `bash -n scripts/release-day.sh` passes, as a test. The laptop's check is called
  at each of `score`'s three ends that do not fail (waiting on a pull request, rows pending, done),
  so a day whose calls wait for review is checked too. Its own day is made concrete as a weekday in
  New York, past 13:00 there, when the morning's window has closed in either offset, and still the
  day the run started; a catch-up after midnight carries the next day and skips the check.
- **The workflow.** The watches are one step after the morning call, run even when `live` failed.
  Listing the runs needs the token's `actions: read` beside `issues: write`: a `permissions` block
  sets every scope it does not name to none. A failed `gh run list` skips the check rather than
  open an issue on an empty list, on both machines.
