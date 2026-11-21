---
description: FortuneTeller status — where we are, what's next, what we can forecast
---

Answer three questions about FortuneTeller from the repository as it stands now. Read only; change
nothing, run no loader and no network command. First run `git fetch -q origin` and read the files
as on `origin/main` (`git show origin/main:<path>`), so the answer is not a stale branch's.

Read:
- `docs/status.md` (last completed, in progress, next)
- `docs/roadmap.md` (the steps, the next gate and its date)
- `README.md`, its *Status* section and **What it predicts**
- `docs/scoreboard/data.json`: `calls` for the live calls' record so far (counts, not
  probabilities), `ahead` for the releases coming up, `written` for how fresh it is
- `docs/changelog.md`, the top five rows
- each step spec's *Step 5* forward log named in status (e.g. `docs/steps/*-forward.csv`): how many
  rows are logged and graded so far

Then reply with three sections, each short:

## 1. Where we are
The last completed step in one line, with its main finding in plain words; each task in progress
in one line with where it stands; the latest merged pull request.

## 2. What's next
The next task, then anything with a date in the next 14 days from today: the next gate, a job or a
pull request due before a release, a crontab line to add. Give each date as a weekday and date.

## 3. What we can forecast
Only what holds walk-forward and is called live: each link (event → market, direction, span), its
record as counts from the scoreboard, and the next release day it will be called on. Then, in one
line each, what is being measured or logged forward but does not forecast yet. Never present a
probability, a placeholder or an untested rule as a forecast; if nothing holds for a kind of event,
say so.

Keep the whole answer under 40 lines. Name the file each fact comes from. $ARGUMENTS
