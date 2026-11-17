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
  - *Amended 2026-11-14, after step 1, before step 2, by the owner
    ([why](../decisions.md#2026-11-14-the-store-travels-encrypted-by-the-owner)):* the rebuild does not reproduce (below), and
    an artifact of a public repository can be downloaded by anyone signed in to GitHub, which
    would republish Nasdaq's and TradingView's replies. So the store and the cache travel as one
    encrypted file instead: a `tar` of both, encrypted with `gpg --symmetric` (AES-256) under a
    key held as the repository secret `FT_STORE_KEY` and in the laptop's `.env`, kept as the asset
    `store.tar.gpg` of a prerelease named `store`. A run downloads and decrypts it; an evening that
    loaded anything uploads the new one. The laptop seeds the first from its own store. No
    `actions/cache`, no artifact of the store, and no rebuild: a run that cannot restore the file
    fails and opens an issue.
- **Started early, by New York's clock.** GitHub's schedule is in UTC and often starts late. The
  morning is scheduled at 11:30 and 12:30 UTC on weekdays, 06:30 or 07:30 New York in winter,
  07:30 or 08:30 in summer. A run goes on unless it starts before 07:00 New York or another of
  the day's morning runs already went on (the workflow's run list); it waits for 08:30:05. A run
  that starts after 08:30 still goes on, as the laptop's catch-up does, and its rows count late if
  logged after 08:45. So a schedule up to an hour late still logs on time. The evening is
  scheduled at 22:30 and 23:30 UTC, goes on at or after 18:00 New York once a day by the same
  rule; it has no deadline, and a late start only grades later.
  - *Amended 2026-11-14, before step 2:* a run goes on by the time it was scheduled for, not the
    time it started: the one scheduled for 07:30 New York is the morning, the one for 18:30 the
    evening, the other exits. Exactly one of each a day, however late GitHub starts it, and no run
    list to read.
  - *Amended 2026-11-17, after the first shadow day, by the owner
    ([why](../decisions.md#2026-11-17-the-runner-is-started-by-an-outside-timer-by-the-owner)):*
    GitHub started the schedule 5 h 41 min to 9 h 56 min late and, on retail sales day, not at
    all by 15:13 UTC ([below](#results)). The runs are started by an *outside timer* instead: two jobs at
    cron-job.org, a free service, each asking GitHub's API to run `jobs.yml` on `main`, with
    `step` set to `live` at 07:30 New York and to `score` at 18:30, Monday to Friday, on the
    service's New York clock, so summer and winter need nothing. The ask goes out with a
    fine-grained token of the owner's, for this repository only, allowed only *Actions: read and
    write*, kept at the service alone. The workflow's `schedule` is removed, so a run is only ever
    one asked for. The morning run still waits for 08:30:05; it never goes on before 07:00, now
    because nothing asks it to.
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
    (*Amended 2026-11-14:* the encrypted store above, not the artifact, is that copy.)
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
  - *Amended 2026-11-17, by the owner:* the first counting day, 2026-11-17, failed *on time*
    under GitHub's schedule. The shadow is run again with the outside timer on two new release
    days, the three bars and the 2026-12-18 date unchanged. A day the timer's ask fails, or the
    run starts late, fails *on time* as this one did; it is not dropped. Re-running the shadow
    after a fail is the owner's choice, written in [Decisions](../decisions.md), not a rule a
    later fail can lean on: a second fail goes to a decisions entry before a third try.
- **Expected outcome, written first:** *fails on the sources*: Yahoo, FRED, the Fed and TradingView
  answer the runner; Nasdaq's calendar refuses it with 403. The rebuild reproduces the laptop's
  `score.txt` in under 20 minutes. Were Nasdaq to answer, the shadow would pass.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`.github/workflows/jobs.yml`, run on demand: the store rebuilt from empty and each source fetched once; the rebuild timed; `score` against the laptop's | The step 1 rule's verdicts written here~~ **done** 2026-11-14, [below](#results) |
| 2 | The schedule and the encrypted store (*amended 2026-11-14*, was the cache) added; the shadow run on two release days. *Amended 2026-11-17:* the schedule removed, the runs asked for by the outside timer; the shadow again on two new release days | The three bars, per day, written here |
| 3 | Only if step 2 passes: the workflow opens the pull requests and issues; the laptop's timers disabled | The first release day on the runner alone logged on time, and a decisions entry retiring 2026-11-10's |

## Results

**Step 1, 2026-11-14.** Two runs of `gh workflow run jobs.yml -f step=rebuild`: 43628949150 on
`main` at #312, and 43630076184 at #313, which added the ask of each source. Every line quoted here
is in [the evidence](loop-off-the-laptop-step1.txt), committed because a run's artifacts last 90
days.

- **The sources: each answers the runner**, so step 2 goes on (run 43630076184's `sources.txt`).
  Yahoo gave the S&P 500's close of 2026-11-13; FRED the series `T5YIE`; the Fed its calendar page;
  TradingView this quarter's 1,466 rows; Nasdaq 74 rows for 2026-11-12. One ask each: FRED's
  release dates and a Fed statement were not asked, and the rebuild that would ask them stopped
  first. The expected outcome, Nasdaq refusing with 403, was **wrong**.
- **The rebuild: it does not reproduce the laptop**, so by the rule *the store is the only copy,
  and its loss is reported as a failure, never rebuilt*. The 20-minute bar could not be judged:
  no rebuild finished. The expected outcome, a rebuild reproducing the laptop's `score.txt` in
  under 20 minutes, was **wrong**. Each run's `timings.txt` shows `load-releases` exiting 1, and
  every later load with nothing to build on:
  - Run 43628949150, after 25 seconds: `jobless claims reports at two times or for two months on
    2025-11-18, 2025-11-20`. The same stop happens on the laptop from an empty store and cache.
    TradingView has rewritten those weeks: the laptop's copy of the quarter, written 2026-10-16,
    has seven weeks of initial claims published together at 13:30 UTC on 2025-11-20; fetched now,
    they are spread over 2025-11-18 and 2025-11-20 at half-hourly times. Only that first conflict
    is shown; what else in the history differs is not known.
  - Run 43630076184, after 9 seconds: `TradingView 2017-04-01: HTTP 429`. Asked for every quarter
    at once, TradingView rate-limits the runner. The morning's `live` asks one quarter, as the ask
    above did, and was answered.

The store's carrying is amended above, by the owner.

**Step 2, the first shadow day: retail sales, 2026-11-17. Fails the shadow, *on time*.** Retail
sales is a flow `live` calls: the laptop's `live` logged its rows, `logged_at` 13:30:13 UTC in
`data/calls.csv` (PR #331), for the release at 08:30 New York, 13:30 UTC. `gh run list -w jobs.yml`
at 15:13 UTC (by `date -u`), an hour and 43 minutes after the release, showed no run of the
morning started. The runs of the day before show why: GitHub started each scheduled run hours
after its time. *Scheduled* is the line `scheduled HH:MM UTC is HH:MM New York` in each run's
log (`gh run view RUN --log`); *Started* is the run's `createdAt` in `gh run list`.

| Run | Scheduled (UTC) | Started (UTC) | Late |
| --- | --- | --- | --- |
| 43957326575 | 11-16 11:30 | 11-16 21:10 | 9 h 40 min |
| 43970103818 | 11-16 12:30 | 11-16 22:26 | 9 h 56 min |
| 44018836200 | 11-16 22:30 | 11-17 04:40 | 6 h 10 min |
| 44022336694 | 11-16 23:30 | 11-17 05:11 | 5 h 41 min |

The spec's "a schedule up to an hour late still logs on time" was **wrong** by hours, and so was
the expected outcome's "were Nasdaq to answer, the shadow would pass": Nasdaq answered, and the
shadow failed on its first day. *The same rows* fails with it: the runner logged no row to compare.
*The same evening* is judged from the evening's run when it finishes, since loading and grading do
not depend on what started it; it is written here then.

Runs asked for start at once: the five runs of 2026-11-14 started by `gh workflow run` (43628949150,
43630076184, 43633700634, 43634405406, 43634459297) each began their job 3 to 4 seconds after the
ask (`gh api repos/diykorey/fortuneteller/actions/runs/RUN/jobs`, `started_at`, against the run's
`created_at`). The start is amended above, by the owner.

*The owner's test ask, 2026-11-17:* cron-job.org's test run of the morning job got HTTP 204, and
run 44116494543 (`workflow_dispatch`, created 15:37:39 UTC) began its job at 15:37:45, 6 seconds
later; its log reads `step: live` and `live: retail is already in data/calls.csv`, the main
checkout's row from the laptop, so it logged nothing new (`gh run view 44116494543 --log`).

## How you know it is right

*The store's three checks amended 2026-11-14 with the store's carrying above.*

- ~~In winter the 11:30 UTC morning run exits at once (06:30 New York) and the 12:30 one waits; in
  summer the 11:30 one waits and the 12:30 one exits, since the first went on.~~ *Amended
  2026-11-17:* the workflow has no `schedule`; the owner's test ask of the morning job appears in
  `gh run list -w jobs.yml` as a `workflow_dispatch` run started within a minute of the ask.
- A run on a weekday with no release exits 0 and commits nothing, as the laptop's does.
- Two runs never write the store at once: the workflow has one concurrency group for both steps.
- A shadow run opens no pull request and no issue.
- The store restored on the next run holds the closes the previous evening uploaded.
- Without `FT_STORE_KEY`, a run fails before any command and opens an issue; it never rebuilds.
- The release asset cannot be read without the key (`tar` refuses the downloaded file).

## What this step does not do

No new flow, no change to what `live` or `score` decide, no server. The popup stays on the laptop as
a second channel, reading nothing from the runner. The page (step 22) and the post (step 23) are
their own steps.

## Technical details

- **Workflow:** `.github/workflows/jobs.yml`, triggers `schedule` and `workflow_dispatch`
  (*amended 2026-11-17:* `workflow_dispatch` only, asked by the outside timer), a
  `step` input (`live`, `score`; *amended 2026-11-14:* `rebuild` was step 1's alone and is gone), actions only from those the repository allows
  (`actions/*`, `astral-sh/setup-uv`).
- **Script:** `scripts/release-day.sh` keeps the laptop's run; the runner's steps live in the
  workflow until a second caller needs them in a script.
- **The outside timer** (*amended 2026-11-17*): each cron-job.org job sends `POST
  https://api.github.com/repos/diykorey/fortuneteller/actions/workflows/jobs.yml/dispatches` with
  the headers `Authorization: Bearer` and the token, `Accept: application/vnd.github+json` and
  `X-GitHub-Api-Version: 2022-11-28`, and the body `{"ref":"main","inputs":{"step":"live"}}` (or
  `"score"`); GitHub answers 204. The service mails the owner when an ask fails. The token's
  expiry is in [Decisions](../decisions.md).
- **Docs:** this spec, [Decisions](../decisions.md) at step 3, `docs/status.md`, the changelog and
  roadmap row 21.
