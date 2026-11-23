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

Step 46, steps 1 and 2: the retry and the watches ([results](steps/loop-nets.md#results)). Every
source's 5xx, timeout or broken connection is asked again after 30 and 90 s, 300 s a process at
most; `unlogged` and `unstarted` find the incidents of 2026-11-17 and 2026-11-19 on their real
rows and runs, and nothing on the days that went right.

Step 52: Canada ([results](steps/canada.md#results)). 153 Bank of Canada decisions and 189
Canadian inflation releases on their days alone, the Canadian dollar and Toronto's stocks added:
nothing holds walk-forward; the Bank's 12 answers from the close before exceed chance plus 2, and
the Canadian dollar strengthens on the day of 13 of 19 hikes, too few to replay.

Step 33, step 2: the first earnings refresh ([results](steps/earnings-current.md#results)). One
new report, Walmart's of 2026-11-19 (EPS $0.65 against $0.64, *as expected*). No line removed,
the hand check against Yahoo passed, and no answer or verdict on the page changed.

## In progress

- **Step 55: guesses against the base rate** ([the spec](steps/guesses-vs-base-rate.md)): each
  guess carries its base rate; a grounded guesser, given the record, runs beside today's news
  guesser as the control. Asked for 2026-11-23 by the owner. Spec written. Next: the goldfish
  review, then step 1, the base rate on every row.
- **Step 53: China** ([the spec](steps/china.md)): China's inflation, factory survey, output and
  exports, each against its forecast, the yuan and Shanghai's stocks added. Asked for 2026-11-22
  by the owner. Spec written. Next: the goldfish review, then step 1, the two markets.
- **Step 46: the loop's safety nets** ([the spec](steps/loop-nets.md)): each machine watches the
  other and opens an issue for what it missed; a source's 5xx asked again. Chosen 2026-11-21 by the
  owner. Steps 1 and 2 built. Next: merged before Wednesday 2026-11-25's releases, then step 3,
  live on the first two release days from 2026-11-24.

- **Step 45: the S&P 500 on the page** ([the spec](steps/sp500-on-the-page.md)): steps 35 to
  37's groups on *Ask*, frozen from a copy of the store, and every S&P 500 member's report in the
  reports ahead. Chosen 2026-11-21 by the owner, after step 44. Published 2026-11-21; the frozen
  file agrees with steps 35 to 37. Next: step 4's count in the week of 2026-11-30, then step 46,
  the loop's safety nets.
- **The page as bright cards** ([the spec](steps/predicts.md), amended 2026-11-22): the owner's
  option A of five designs. Next: published, then the first week of the ledger.
- **Step 51: the front page's guesses, approved** ([the spec](steps/front-staging.md)): each
  evening's front-page guesses wait in a pull request the owner rewords and merges. Asked for by
  the owner 2026-11-22. Next: the first front pull request, from the first evening whose proposal changes.
- **Step 50: the guess ledger** ([the spec](steps/guess-ledger.md)): up to 50 guesses an evening,
  reviewed and learned from monthly. Asked for by the owner 2026-11-22. Published with its first
  10. Next: the first week's counts; the first lessons on 2026-12-01; then step 46.
- **Step 49: our guesses** ([the spec](steps/our-guesses.md)): the evening's guesses from the
  news beside the tested forecasts, scored apart; no *if* cards. Asked for by the owner
  2026-11-22. Published with its first two guesses; the evening job guesses each weekday. Next:
  the test at 30 graded guesses; then step 46.
- **Step 48: stated forecasts** ([the spec](steps/stated-forecasts.md)): the page says what
  will happen, from the long run and after news, each kept and graded. Asked for by the owner
  2026-11-21. 5 of 29 pairs hold; three forecasts stated and kept, the first graded on
  2026-12-21. Next: step 4, its first grades in Results; then step 46.
- **Step 47: Fortuneteller predicts** ([the spec](steps/predicts.md)): a page of one to five
  dated *if* cards from what holds, asked for by the owner 2026-11-21. Published 2026-11-21, then
  reworded for a reader without financial training. Next: step 3's bars checked on the live page.
- **Step 44: a page a stranger reads** ([the spec](steps/readers.md)): the first screen on the
  answers that hold, market names outside a closed *workings*, and the Dow's reports of the next
  seven days with what followed each kind, for step 23's readers. Chosen 2026-11-21 by the owner.
  Spec reviewed; steps 1 to 5 built. Next: the page published, the evening job's first
  weekday write checked, then the second first-visitor review in the week of 2026-11-30.
- **Step 42, step 5: the forward log** ([the spec](steps/exposure-scores.md)): each OPEC+, CPI,
  Fed and retail event after the scores' commit, its spread per rubric written to
  `steps/exposure-forward.csv` and graded, to the 2027-01-31 gate.
- **Step 43, step 5: the forward log** ([the spec](steps/filing-severity.md)): members' 8-Ks of
  the five items after the scores' commit, scored and committed before their reaction close,
  graded at the span's end, to the 2027-01-31 gate.
- **Step 41, step 5: the forward log** ([the spec](steps/expert-hypotheses.md)): each new event
  meeting rules 11, 23, 25 or 26 written to `steps/expert-forward.csv` before its reaction close
  and graded at its span's end, to the 2027-01-31 gate.
- **Step 34: a same-day source for earnings** ([the spec](steps/earnings-same-day.md)): step 1
  done, Yahoo's kind is Nasdaq's on 102 of 110 reports (92.7%, bar 90%). Next: the speed, asked on
  each member's report from 2026-11-23 to 2027-01-31.
- **Step 33: the earnings kept current** ([the spec](steps/earnings-current.md)): steps 1 and 2
  done; the first refresh, 2026-11-23, added Walmart's report of 2026-11-19 and changed no answer.
  Next: the refresh of Monday 2026-11-30, LAST 2026-11-27.
- **Step 23: be seen, and count it** ([the spec](steps/be-seen.md)): a cookie-free Umami counter
  on the page and a weekly LinkedIn post drafted by `weekly-post`, both the owner's choice. Step 1
  done: the counter is live and counts a visit once, read through Umami's share link. The first
  week's row: 8 visitors, no post. Next: the first post, published by the owner.
- **Step 21: the loop off the laptop** ([the spec](steps/loop-off-the-laptop.md)): the jobs on
  GitHub Actions. Step 1 done: every source answers the runner; the store cannot be rebuilt from
  empty (TradingView rewrote 2025's claims weeks), so it must travel encrypted. Step 2, the shadow
  run, beside the laptop: its first day, retail sales 2026-11-17, failed *on time*, GitHub's
  schedule starting runs almost 6 to 10 hours late. By the owner, an outside timer (cron-job.org) starts
  the runs instead. Claims 2026-11-19, the first day under the timer, does not count (the laptop's
  evening failed on FRED); its morning was on time with the same rows, and the runner's evening
  matched once a one-commit checkout, which made the trigger read late, was fixed (#372). Two
  counting days are still needed by 2026-12-18.
- **Step 18, part 2, step 3: the first triggers graded** ([the spec](steps/trigger-file.md)). The
  first trigger, CPI of 2026-11-10, is void: merged after every reaction close, and its kind read
  from the headline instead of the core print. It waits for the next one.
- **Waiting for a release day:** the scoreboard's first on the published page (step 3 of
  [its spec](steps/scoreboard.md)); the release-day job, evening score and rung 6's popup on one
  release end to end; [beat the fortune teller](steps/beat-the-fortune-teller.md)'s first live
  round. The two release days since 2026-11-06 were missed or late; the causes and fixes are in
  [Decisions](decisions.md) (2026-11-10, 2026-11-11) and PRs #280 and #290.

## Next

Step 54, Switzerland, with step 46's live days (2026-11-24 onward) recorded alongside.

Monday 2026-11-23: step 23's first weekly post, drafted by `weekly-post` and published by the
owner. Then step 44's page, published before the post if it is ready.

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
