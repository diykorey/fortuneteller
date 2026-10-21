# Rung 6 — delivery

> Rung 6 of the [Roadmap](../roadmap.md#after-the-mvp--the-feature-ladder)'s feature ladder.
> Chosen 2026-10-21, after [the record, not a probability](record-not-probability.md) restated its
> gate. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when a release lands, its call pops up on the screen; nobody has to look for a
pull request.

The [release-day job](release-day-job.md) logs each call and opens its pull request, and the
[evening score](evening-score.md) grades it, both unattended. Neither tells anyone: the job opens
pull requests and issues as the user, and GitHub does not notify a user of their own.

At the end: a desktop popup on this laptop for every logged call, and for every failed run.

## The rule, fixed before anything is delivered

- **What a call says** is what `live` printed for it, unchanged: the release line (actual,
  consensus, surprise) and each link's line, direction, record as counts and band, or why it is
  silent. No percentage, as rung 6's gate says.
- **When:** once per morning run that logged rows, right after their pull request opens; once per
  failed run of either job, beside its issue. A quiet day and the evening's score pull request pop
  nothing up.
- **How it stays seen:** critical urgency, so the popup stays until it is dismissed.
- **A popup never fails a job.** If `notify-send` fails, the run's outcome is unchanged.
- **This laptop only.** A start missed while it was off runs at the next login (`Persistent=true`),
  and its popup shows then; a call the job never made is not delivered.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scripts/release-day.sh`: `notify-send` after a calls pull request opens and on every report | Started by hand with a planted log line, a popup shows the release and link lines; a failing run pops up its title; with `notify-send` missing the run exits as before |
| 2 | Results: the first release delivered | Its popup seen on the release day, its lines equal to the logged rows |

## Technical details

The popup's body is the lines of the run's output (`$out`) that hold `: actual ` or a link's line;
its title is the pull request's (`Log the live cpi call of 2026-11-12`) or the failure's. The user
service already has `DISPLAY` and `DBUS_SESSION_BUS_ADDRESS` (checked 2026-10-21: a popup from
`systemd-run --user` showed). No new unit, no daemon-reload.

## What this does not do

No phone, email or chat; no forecast before the release; no change to how calls are made, graded
or worded.
