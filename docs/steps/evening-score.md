# The evening score

> Follows [the release-day job](release-day-job.md): the calls it logs in the morning are graded in
> the evening, with no one at the keyboard. Chosen 2026-10-19. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** after the closes, the day's data is loaded and every logged call graded; the
result arrives as a pull request.

[Rung 4](rung-4-keep-score.md#results) graded the first live calls by hand: four commands, run in
order after 16:15 New York. That is the last step a person still has to remember.

At the end: a second timer loads the day and runs `score`; when the result changes, a pull request
shows it, and on a failure an issue.

## The rule, fixed before the job runs

- **The same commands, in order:** `load-releases`, `load-prices`, `load-surprises`, `score`, on
  the main checkout's database and calendar cache, the FRED key read from its `.env`.
- **The result is a file.** `score`'s output is committed as `data/score.txt`. When it differs
  from `origin/main`'s, it goes to a branch `score-<day>` and a pull request; when it is the same,
  nothing opens. `score` prints the same text twice on the same data (checked 2026-10-19).
- **It waits rather than mislabels.** While a `calls-*` pull request is open, its rows are not on
  `main` and would read as missed: the run exits 0 and loads nothing. So it does while a `score-*`
  pull request is open, which a second would repeat (*added 2026-10-20*). While any row is pending
  (its release, surprise or close not loaded yet), nothing is committed. The next run picks either
  up.
- **Weekdays at 18:00 New York**, well after the 16:15 VIX close. A run missed while the laptop was
  off runs at the next login (`Persistent=true`). Both jobs take one lock, so a late evening run
  and the morning's `live` never hold the database at once.
- **Every failure is reported** as the morning's are: an issue with the run's output. FRED's errors
  are printed with the key redacted (`sources._fred_get`, every path).
- **No hardening of the loaders.** `load-surprises` timed out on Nasdaq on 2026-10-16 while the
  calendar cache filled for the first time (about 940 days). Cached, the four commands take about
  90 seconds and fetch only the newest days; a timeout now is an issue, and the next run resumes.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`scripts/release-day.sh score`, the evening timer and service, a lock shared with the morning, `data/score.txt` committed~~ **done**; a run by hand against a scratch worktree loaded the day in 73 s, exited 0 and wrote `data/score.txt` byte for byte; installing is asked for separately | A run started by hand with nothing new exits 0 and opens nothing; the morning job still passes its check run |
| 2 | Results: the first release graded by the job | Its score's pull request opened with no one there, and its rows graded |

## Technical details

`scripts/release-day.sh` takes the step: `live` in the morning, `score` in the evening. Both share
the worktree, the report and the push, and take `flock` on a lock file beside the job's worktree.
Each run starts by discarding the worktree's changes, since a pending evening leaves
`data/score.txt` changed. The
evening service has `EnvironmentFile=` the main checkout's `.env` (plain `KEY=value`), never the key
in a committed unit, and `TimeoutStartSec=20min`. `score` runs with a relative `FT_CALLS_PATH`, so
`data/score.txt` names no home directory. Installing, like the morning's:

```bash
ln -s "$PWD"/scripts/systemd/fortuneteller-evening-score.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now fortuneteller-evening-score.timer
systemctl --user start fortuneteller-evening-score.service   # the check
```

## What this does not do

No change to how calls are made or graded, no delivery to anyone (rung 6), no retry inside the
loaders.
