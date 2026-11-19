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

Step 31: earnings ([results](steps/earnings.md#results)). From the close before, a Dow member's
shares fall behind the S&P 500 after a miss or an in-line report, and run ahead over the week and
month after a beat; a miss's day and week and an in-line report's day hold walk-forward.

## In progress

- **Step 32: ask about earnings** ([the spec](steps/ask-earnings.md)): the page answers step 31's
  three earnings kinds, every cell carries the placebo's mark, and `load-prices` loads the
  companies every evening. Step 1 done on a copy of the store: 7 holds and 3 period marks, as
  expected. Step 2 waits for the evening job.
- **Step 29: ask about phase 5's kinds** ([the spec](steps/ask-phase-5.md)): the page's
  section answers OPEC+, the two banks, violent acts, hacks, landfalls and floods. Step 1 built; step 2
  waits for the evening job.
- **Step 23: be seen, and count it** ([the spec](steps/be-seen.md)): a cookie-free Umami counter
  on the page and a weekly LinkedIn post drafted by `weekly-post`, both the owner's choice. Step 1
  done: the counter is live and counts a visit once, read through Umami's share link. Next: the
  first post, after step 22's page is checked.
- **Step 21: the loop off the laptop** ([the spec](steps/loop-off-the-laptop.md)): the jobs on
  GitHub Actions. Step 1 done: every source answers the runner; the store cannot be rebuilt from
  empty (TradingView rewrote 2025's claims weeks), so it must travel encrypted. Step 2, the shadow
  run, beside the laptop: its first day, retail sales 2026-11-17, failed *on time*, GitHub's
  schedule starting runs almost 6 to 10 hours late. By the owner, an outside timer (cron-job.org) starts
  the runs instead; the shadow restarts on two new release days once its test ask reaches GitHub.
- **Step 18, part 2, step 3: the first triggers graded** ([the spec](steps/trigger-file.md)). The
  first trigger, CPI of 2026-11-10, is void: merged after every reaction close, and its kind read
  from the headline instead of the core print. It waits for the next one.
- **Waiting for a release day:** the scoreboard's first on the published page (step 3 of
  [its spec](steps/scoreboard.md)); the release-day job, evening score and rung 6's popup on one
  release end to end; [beat the fortune teller](steps/beat-the-fortune-teller.md)'s first live
  round. The two release days since 2026-11-06 were missed or late; the causes and fixes are in
  [Decisions](decisions.md) (2026-11-10, 2026-11-11) and PRs #280 and #290.

## Next

Step 23: the first weekly post, now that step 22's page is checked.

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
