# The release-day job

> Answers [rung 5](rung-5-live-path.md)'s open question, decided 2026-10-14: the release day's
> pull request opens with no one at the keyboard. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** on a release day, the call is made, logged and put up for review without
anyone running anything.

Rung 5 step 1 showed TradingView's actual within 8 seconds of the release and equal to the typed
one. What is left by hand is running `predict --fetch` at 08:30 New York and opening the pull
request. Every release day no one is there for is lost for good.

At the end: a timer on this machine runs `fortuneteller live` every weekday at 08:30 New York; on a
release day it opens the pull request, and on a failure it opens an issue.

## The rule, fixed before the job runs

- **One command decides the day.** `fortuneteller live` checks each flow with a consensus (CPI,
  jobs report, retail sales, core PCE, GDP) for a release today on the calendars, the same check
  `predict` makes, and runs `predict --fetch`'s path on each that has one. A day with none exits 0
  and does nothing; a failure on a release day exits 1. The job never reads the text it prints.
- **Started in New York's time, not this machine's.** The timer fires at 08:30:05
  `America/New_York`: Europe and the US change their clocks on different Sundays, and a start
  before 08:30 is refused.
- **Its own checkout.** The job works in a worktree of its own, branched from `origin/main`, never
  in the one in use. It reads the database and the calendar cache of the main checkout and writes
  only `data/calls.csv` in its own tree.
- **It opens, never merges.** Logged rows go to a branch `calls-<flows>-<day>` and a pull request
  to `main`, as by hand. Merging stays a person's.
- **Every failure on a release day is reported**: no actual within 30 minutes, calendars that
  disagree, a locked database, a push or `gh` error. The job opens an issue with the run's output;
  if it cannot reach GitHub at all, the output stays in the journal. A machine asleep or off misses
  the release and reports nothing: this is a job on one laptop, not a service.
- **Typing stays possible.** A release the job missed or failed is still logged with
  `predict --actual` on its day, as now.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `fortuneteller live` | Tests: a release day with an actual logs its rows and exits 0; a day with none exits 0 and logs nothing; no actual in 30 minutes exits 1 |
| 2 | `scripts/release-day.sh` and a systemd user timer and service, committed; installing is asked for separately | A run started with `systemctl --user start` on a day without a release exits 0, opens nothing, and the timer lists its next start in New York's 08:30:05 |
| 3 | Results: the first release logged by the job | Its pull request opened before the close, and its rows graded by `score` |

## What this does not do

Load the day's releases and prices or run `score` after the closes; that stays by hand until a
later spec. No delivery to anyone (rung 6), no change to how calls are made or graded, no job on any
other machine.
