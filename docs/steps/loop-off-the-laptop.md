# The loop off the laptop

> Step 21 of the [Roadmap](../roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen), the first
> of phase 4. Terms are in the [Glossary](../glossary.md): *release-day job*, *evening score*,
> *shadow run*, *the gate*.

## The goal

**In plain words:** the morning call and the evening grading run on GitHub's machines, not on a
laptop that sleeps, so no release day is lost to a closed lid.

Today the [release-day job](release-day-job.md) and the [evening score](evening-score.md) are
systemd timers on the owner's laptop (`scripts/release-day.sh`). Two of the last release days were
missed or late ([Decisions](../decisions.md), 2026-11-10 and 2026-11-11). At the end, a scheduled
workflow runs the same commands on a GitHub runner, opens the same pull requests and issues, and
the laptop's timers are off. The gate on 2027-01-31 then needs four straight weeks of release days
logged within 15 minutes, none missed.

## The way to reach it

- **The same commands, a new caller.** The workflow runs `live` in the morning and the evening
  steps (`load-releases`, `load-prices`, `load-surprises`, `score`, `triggers`, `scoreboard`) as the
  script does. The script's laptop parts (the worktree, the lock, the popup) stay on the laptop.
- **The store on a runner that starts empty.** The store (`data/fortuneteller.duckdb`, 104 MB on
  2026-11-14) and the source cache (`data/cache/`, 118 MB: Fed statements, Nasdaq's and
  TradingView's calendars) travel between runs as one `actions/cache` entry, a new key each run,
  the newest restored. Since a cache can be evicted, each evening also uploads both as an artifact
  kept 90 days, and a run that finds no cache restores the newest artifact. Only a run with
  neither rebuilds from empty (`init`, `seed`, every `load-*`) and says so. Whether a rebuild
  reproduces the laptop is measured in step 1, not assumed: the cache holds calendars that may not
  be fetchable again.
- **Started early, by New York's clock.** GitHub's schedule is in UTC and often starts late. The
  morning is scheduled at 11:30 and 12:30 UTC on weekdays, 06:30 or 07:30 New York in winter,
  07:30 or 08:30 in summer. A run goes on unless it starts before 07:00 New York or another of
  the day's morning runs already went on (the workflow's run list); it waits for 08:30:05. A run
  that starts after 08:30 still goes on, as the laptop's catch-up does, and its rows count late if
  logged after 08:45. So a schedule up to an hour late still logs on time. The evening is
  scheduled at 22:30 and 23:30 UTC, goes on at or after 18:00 New York once a day by the same
  rule; it has no deadline, and a late start only grades later.
- **The obstacle: a source that refuses a datacenter.** Nasdaq's calendar answered a different
  Python with HTTP 403 on 2026-11-10
  ([Decisions](../decisions.md#2026-11-11-python-pinned-to-312)); its servers may refuse GitHub's
  addresses outright. The sources the jobs read: Yahoo (closes), FRED (series and releases), the
  Fed's site (statements), TradingView's calendar (the actual and a consensus) and Nasdaq's
  calendar (a consensus, which a flow whose rule predicts from Nasdaq needs). A source that
  refuses the runner is the result; it is written here and in [Decisions](../decisions.md).
- **The shadow run.** On two release days the workflow runs beside the laptop. It commits nothing
  and opens nothing: it uploads its `data/calls.csv` rows of the day as the run's artifact. The
  evening shadow scores `main`'s `data/calls.csv`, the laptop's merged rows, from its own store:
  it tests the runner's loading and grading, while the morning's rows are tested by the second
  bar. An evening the laptop's job waits (a pull request still open) is compared on the next
  evening both run.
- **Secrets and rights.** `FT_FRED_API_KEY` as a repository secret. The workflow's token gets
  `contents`, `issues` and `pull-requests: write`. GitHub refuses a workflow's pull request unless
  the repository allows Actions to create them, an owner's setting, off today; it is needed from
  step 3 only. A pull request opened by the workflow's token starts no CI; `main` has no required
  checks, so the job's own merge of an all-silent pull request still works.

## The rule, fixed before the first run

- **The sources (step 1):** a run on demand fetches once from each of the five sources. A source
  *answers* when it returns the data the job parses, not an error page. The rebuild from empty is
  timed, and its `score.txt` compared with the laptop's on the same commit of `main` and the same
  day.
  - Every source answers: step 2 goes on. One refuses: *fails on the sources*, naming it; the
    laptop keeps the job, and only a way around that source (a decision of its own) reopens this.
  - The rebuild's `score.txt` equal and the rebuild under 20 minutes: a lost cache costs nothing.
    Otherwise the artifact is the only copy, and its loss is reported as a failure, never rebuilt.
- **The shadow (step 2), on each of two release days of a flow `live` calls:**
  - *On time:* the runner logs each of the day's rows within 15 minutes of the release, by its
    `logged_at` (UTC).
  - *The same rows:* the runner's rows of the day and the laptop's are the same set, equal in every
    column but `logged_at`.
  - *The same evening:* its `score.txt` and `data/trigger-log.csv` equal the laptop's, byte for
    byte.
  - All three on both days: *passes*. Any missed: *fails the shadow*, with the bar and the day. A
    day the laptop itself misses does not count, and another is taken; if two counting days are
    not done by 2026-12-18, a decisions entry says what happens instead, since the gate's four weeks
    must start by 2027-01-03.
- **Expected outcome, written first:** *fails on the sources*: Yahoo, FRED, the Fed and TradingView
  answer the runner; Nasdaq's calendar refuses it with 403. The rebuild reproduces the laptop's
  `score.txt` in under 20 minutes. Were Nasdaq to answer, the shadow would pass.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `.github/workflows/jobs.yml`, run on demand: the store rebuilt from empty and each source fetched once; the rebuild timed; `score` against the laptop's | The step 1 rule's verdicts written here |
| 2 | The schedule and the cache added; the shadow run on two release days | The three bars, per day, written here |
| 3 | Only if step 2 passes: the workflow opens the pull requests and issues; the laptop's timers disabled | The first release day on the runner alone logged on time, and a decisions entry retiring 2026-11-10's |

## How you know it is right

- In winter the 11:30 UTC morning run exits at once (06:30 New York) and the 12:30 one waits; in
  summer the 11:30 one waits and the 12:30 one exits, since the first went on.
- A run on a weekday with no release exits 0 and commits nothing, as the laptop's does.
- Two runs never write the store at once: the workflow has one concurrency group for both steps.
- A shadow run opens no pull request and no issue.
- The store restored on the next run holds the closes the previous evening loaded.
- With the cache deleted, a run restores the newest artifact, not a rebuild.

## What this step does not do

No new flow, no change to what `live` or `score` decide, no server. The popup stays on the laptop as
a second channel, reading nothing from the runner. The page (step 22) and the post (step 23) are
their own steps.

## Technical details

- **Workflow:** `.github/workflows/jobs.yml`, triggers `schedule` and `workflow_dispatch`, a
  `step` input (`live`, `score`, and `rebuild`, step 1's run from empty), actions only from those the repository allows
  (`actions/*`, `astral-sh/setup-uv`).
- **Script:** `scripts/release-day.sh` keeps the laptop's run; the runner's steps live in the
  workflow until a second caller needs them in a script.
- **Docs:** this spec, [Decisions](../decisions.md) at step 3, `docs/status.md`, the changelog and
  roadmap row 21.
