# Status

Where the work is and what comes next: the task last finished, the tasks in progress, and the next one. Kept short; history lives elsewhere.

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next*, so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add a row to the
  [changelog](changelog.md), in the same change.
- **Keep each task to a few lines:** what it is, where it stands, a link to its spec. Detail of
  what happened belongs in the spec, the pull request or an issue; a choice that sets direction
  belongs in [Decisions](decisions.md).

## Last completed

Step 20, part 1: a CEO's conduct in question, the company against the S&P 500
([the spec](steps/ceo-scandals.md)). It falls on the day, 17 of 26, chance 0.004; from the
reaction close *can't say*; nothing holds walk-forward. A `ceo` trigger names its company and is
graded on it (step 2b).

## In progress

- **Step 20, part 2: a pasted article read into a trigger** ([the spec](steps/article-to-trigger.md)),
  by rules, tested on part 1's dataset. It reads both kinds the owner chose: a departure for the
  CEO's conduct, answered, and conduct with no departure (Nvidia), read but not answered until
  part 1b measures it. Next in it: step 1, the sets.
- **Step 18, part 2, step 3: the first triggers graded** ([the spec](steps/trigger-file.md)). The
  first trigger, CPI of 2026-11-10, is void: merged after every reaction close, and its kind read
  from the headline instead of the core print. It waits for the next one.
- **Waiting for a release day:** the scoreboard's first on the published page (step 3 of
  [its spec](steps/scoreboard.md)); the release-day job, evening score and rung 6's popup on one
  release end to end; [beat the fortune teller](steps/beat-the-fortune-teller.md)'s first live
  round. The two release days since 2026-11-06 were missed or late; the causes and fixes are in
  [Decisions](decisions.md) (2026-11-10, 2026-11-11) and PRs #280 and #290.

## Next

Step 21, the loop off the laptop: its spec, then the shadow run, started now so four straight
on-time weeks fit before the gate on 2027-01-31; step 20, part 2, step 1 (the dev and test sets)
goes on beside it, once the owner has settled that spec. Then step 22, the page
([roadmap phase 4](roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen)).

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- CPI release dates for 1972–1989, and NFP release dates before 1994, have not been checked against
  BLS. Later dates are checked; see step 1's spec and rung 1's.
- In 1990–2007 the 10-year yield and the dollar move more the day after a Fed decision than on the
  day; either their close then came before the statement, or the reaction ran on. See
  [Precision](precision.md), "Close times".
- Since 2008, 19 CPI releases share their day with retail sales, and 7 jobs reports with retail
  sales or core PCE; CPI's and the jobs report's tables keep those days. See
  [step 4](steps/step-4-more-events.md#shared-days).
