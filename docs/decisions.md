# Decisions

The choices that set the project's direction, newest first, each with why and where it is written
out in full. Read this before reopening a question: if it is here, it was settled on purpose, and
changing it takes a new entry, not a quiet edit.

What belongs here: a choice of target, method, scope, order or way of working that later work must
respect. What does not: the bars and rules inside one step, which live in that step's spec and are
amended there with a date.

Each entry: **what** was decided, **why**, what it **retires**, and **where** the detail is. *By the
owner* marks a choice the owner made over another on the table.

## 2026-11-20: Four more kinds, by the owner

- **What:** asked which kind phase 5 measures next, the owner answered all four offered: S&P 500
  additions (step 35), earnings beyond the Dow, stock splits, and a CEO's conduct with no
  departure; one step each, in that order.
- **Why:** phase 5 goes on (the answers above); the four were the candidates with a free dated
  record or a known gap.
- **Retires:** nothing.
- **Where:** [roadmap](roadmap.md), [step 35](steps/sp500-additions.md).

## 2026-11-20: The owner's answers to the zoom-out

- **What:** four answers, given the same day.
  1. **Phase 5 goes on:** new kinds keep coming, one a pull request, before the gate; the zoom-out's
     freeze is declined.
  2. **The evening's score merges itself:** a score pull request, opened only when every row is
     graded, is merged by `scripts/release-day.sh` once its checks pass; a failed check leaves it
     for a person. The runner's evening (step 21) then finds nothing to wait on.
  3. **A free same-day source for earnings** is looked for, as a step of its own: Nasdaq's
     calendar fills too late for a live call ([step 33](steps/earnings-current.md)).
  4. **The out/hole column stays as it is:** an event outside a market's closes counts in
     neither; the [Glossary](glossary.md) says so.
- **Why:** 1, the owner's choice of 2026-11-17 stands; 2, a person merging before 01:30 Kyiv every
  night is the flaw the shadow found on 2026-11-18; 3 and 4, as asked.
- **Retires:** a person reviewing each score pull request before it merges.
- **Where:** `scripts/release-day.sh`, [step 21](steps/loop-off-the-laptop.md), the Glossary.

## 2026-11-20: The earnings are kept current, by hand, weekly

- **What:** step 33 refreshes step 31's reports each Monday in a pull request, until the gate.
- **Why:** the page's most-held answers (step 32) stop at 2026-11-18 otherwise, and a post quoting
  them grows stale. Nasdaq fills a report's EPS days late, so no evening fetch or live call.
- **Retires:** nothing.
- **Where:** [step 33](steps/earnings-current.md).

## 2026-11-20: The first monthly zoom-out

- **What:** a goldfish, given only the Legend, the roadmap, status and these decisions, zoomed out
  over the plan, as the [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish)
  asks once a month. Its findings, most serious first:
  1. Phase 5 repeats what phase 4 was opened to stop: nine steps in four days, most *can't say*
     or within chance, while no post has gone out and the readers bar has no count.
  2. The loop bar has no release day yet logged clean on both the laptop and the runner; the
     shadow owes two counting days by 2026-12-18, before the gate's four weeks begin.
  3. 2026-11-19 may be a second shadow failure, which the 2026-11-17 entry sends here before a
     third try; status puts the lost day down to the laptop's FRED failure.
  4. The Bank of England and the Bank of Japan (step 25) went before the euro area, against the
     Legend's "one country at a time once the US answers hold".
  5. Smaller: roadmap rows 21 and 23 and the Later list were behind status; status' *Next*
     repeated step 23's own next part; three items have waited for a release day since before
     2026-11-06 without saying which release ends the wait.
  It would cut: phase 5 until the gate; step 21 to the evening job, or the morning kept on the
  laptop; the popup and *beat the fortune teller* until there are readers.
- **Why:** recorded as found. Finding 5 is fixed in the same change. Findings 1, 2 and 4 would
  reverse the owner's choices of 2026-11-17 (widen the kinds now; the outside timer), so they wait
  for the owner. Finding 3 goes to step 21's spec. What phase 5 did gain: steps 31 and 32 put three
  links that hold on the page, the most of any kind.
- **Retires:** nothing.
- **Where:** [roadmap](roadmap.md), [status](status.md), [step 21](steps/loop-off-the-laptop.md).

## 2026-11-19: Earnings go on the page, and the page shows the placebo's mark

- **What:** step 32 adds step 31's three earnings kinds to the page's *Ask the fortune teller*,
  and gives every cell on the page the placebo's mark, which step 22 left off.
- **Why:** the earnings are the kind the news brings most and three of their links hold
  walk-forward, more than any kind on the page; it was kept off only by its 11-minute run, which
  PR #367 brought to a minute. Step 31 found a beat's day *up* that the placebo reads as the
  period; the page would show it as the beat's answer, and so it may already show other cells.
- **Retires:** the earnings skip in `ask_data`; step 22's page without the placebo.
- **Where:** [the spec](steps/ask-earnings.md).

## 2026-11-19: Earnings, the Dow's members, one event per report, by the owner

- **What:** step 31 measures earnings reports: the Dow's members on each report's day, Nasdaq's
  calendar for the EPS and its consensus, the SEC's 8-K for the minute. An event's id gains the
  report's place in its day, so a flow can hold several events on one day.
- **Why:** the kind the news brings most; a dated membership list picks the companies without
  hindsight, where today's market caps would choose the survivors.
- **Retires:** one event per flow per day.
- **Where:** [the spec](steps/earnings.md).

## 2026-11-19: Floods from NOAA's billion-dollar list; droughts left out

- **What:** step 30 measures the US floods of NOAA's Billion-Dollar Disasters list (1980 to
  2024) that have a day, 39 of its 45, the owner's "floods and droughts", as history only, with
  no crop-region filter.
- **Why:** the list is free and nobody here picks it. Its 32 droughts, and six of its floods, begin on the first of
  a month and last a month or more: a season, not a day the news knew; a call is made from the actual once it lands. A
  region filter would be read from the names by hand. A flood's cost is known weeks later, so no
  trigger.
- **Retires:** droughts as a kind, until a dated source is found; roadmap row 28's "floods and
  droughts in crop-growing regions" as a later step.
- **Where:** [the spec](steps/floods.md).

## 2026-11-19: Phase 5's kinds go on the page, by the owner

- **What:** step 29 adds the six flows of steps 24 to 28 to the page's *Ask the fortune teller*,
  before any new kind or reading the news into them.
- **Why:** they are measured and the page is the gate's second bar; a reader who brings an OPEC+
  or hurricane headline should find its kind. Small, and it shows only numbers already graded.
- **Retires:** the skip in `ask_data` that kept steps 24 to 28 off the page.
- **Where:** [the spec](steps/ask-phase-5.md).

## 2026-11-18: War is measured as ICB's violent acts

- **What:** step 26's *war and military strikes* is every international crisis since 1970 that
  the International Crisis Behavior project codes as set off by a violent act: 136 days, 1970 to
  2021, one kind.
- **Why:** a free list nobody here picks, with a day for each. A crisis's trigger is often words
  weeks before the shooting, and a crisis's violence is known only once it has run its course; the
  violent act is the day a trigger would be filed, known that day.
- **Retires:** nothing. Wars after 2021 wait for ICB's next version.
- **Where:** [war](steps/war.md).
## 2026-11-17: The runner is started by an outside timer (by the owner)

- **What:** the release-day job and the evening score on GitHub's runner are started by two jobs at
  cron-job.org, a free service, asking GitHub's API to run the workflow at 07:30 and 18:30 New
  York on weekdays. The ask carries the owner's fine-grained token for this repository only,
  allowed *Actions: read and write*, kept at that service alone, expiring 2027-03-31 (renewed
  before then, or the loop stops). The workflow's own schedule is removed.
- **Why:** GitHub started the scheduled runs 5 h 41 min to 9 h 56 min late on 2026-11-16 and had
  not started the morning of retail sales, 2026-11-17, by 15:13 UTC, so the shadow failed *on
  time*; runs asked for start within seconds. The owner chose to run the shadow again with the new
  start rather than keep the laptop; a second fail comes back here before a third try. Of the
  three ways weighed, the laptop starting the runner keeps the laptop awake, and fixing the
  laptop's sleep keeps the job on it; an outside timer frees both.
- **Retires:** step 21's 2026-11-14 rule that a run goes on by the time it was scheduled for.
  The token at a third party can start, cancel, re-run and delete this repository's workflow runs;
  it cannot read or change the code or the secrets.
- **Where:** [step 21](steps/loop-off-the-laptop.md), its amendments and results of 2026-11-17.

## 2026-11-17: Widen the kinds now (by the owner)

- **What:** phase 4's pause on new kinds is lifted. Phase 5 adds, one per pull request: OPEC+
  decisions, other central banks (the Bank of England, the Bank of Japan), war and military
  strikes, crypto shocks, and weather and climate events. A hot event of a measured kind is filed
  by hand as a trigger; reading the news into kinds by a small local model goes to the backlog.
- **Why:** the owner wants the fortune teller to answer the news people talk about, and a kind can
  only be answered once its past is measured. Each kind is a dated list on the building block the
  tariff, election, summit and CEO kinds already use, so each costs a list and a spec.
- **Retires:** phase 4's "no new flow or kind starts until steps 21 to 23 are done". The gate on
  2027-01-31 keeps its three bars; steps 21 to 23 finish beside the new kinds.
- **Where:** [roadmap phase 5](roadmap.md#phase-5-the-kinds-the-news-brings).

## 2026-11-17: The visitor count is read through Umami's share link (by the owner)

- **What:** step 23's weekly count stays on Umami Cloud's free plan and is read through the site's
  public share link, not a paid API key. If the link stops answering, the week is read from the
  dashboard by hand.
- **Why:** the free plan has no API key, and the owner pays nothing before there are customers.
  The share link gave the exact Monday-to-Sunday UTC count on 2026-11-17, and its token is listed
  in Umami's own API description. The owner chose it over GoatCounter (a free API, but a switch of
  counter and its own count of a visitor) and over reading the dashboard every week.
- **Retires:** the spec's `FT_UMAMI_API_KEY`.
- **Where:** [be seen](steps/be-seen.md#the-way-to-reach-it).

## 2026-11-15: Step 20 parked until the gate (by the owner)

- **What:** step 20 stops where it stands until the 2027-01-31 gate: part 1 measured, part 2's
  word rules *doesn't read*, `read-article` kept but not trusted. Part 1b, part 2's next try and
  part 3 wait. The work goes to steps 21 to 23. A `ceo` trigger is still filed by hand from part 1.
- **Why:** the rules read 5 of 12 test positives and misread 6 of 99 other departures, and Nvidia's
  article read as *not a measured kind*. The next try, a small model on this machine (Gemma 3 4B or
  Qwen 2.5 3B, on the CPU), with a fresh test set from part 1's conduct departures left out for
  their prices, is a new method that phase 4 says waits for the gate. The owner chose this over
  the model now and over pasting alone.
- **Retires:** phase 4's exception for step 20's part 2; and its spec's line that a *doesn't read*
  is answered before part 3, which this entry answers.
- **Where:** [part 2's results](steps/article-to-trigger.md#results),
  [roadmap step 20](roadmap.md#next-steps-in-order).

## 2026-11-14: The store travels encrypted (by the owner)

- **What:** on GitHub's runners, the store and the source cache travel between runs as one
  gpg-encrypted file, a release asset, under the secret `FT_STORE_KEY`; never as a cache or a
  plain artifact, and never rebuilt from empty. The owner set `FT_FRED_API_KEY` and
  `FT_STORE_KEY` as repository secrets.
- **Why:** step 21's first run showed the store cannot be rebuilt: TradingView rewrote 2025's
  shutdown weeks of claims and rate-limits a runner asking for every quarter. And an artifact of a
  public repository can be downloaded by anyone signed in, which would republish Nasdaq's and
  TradingView's replies.
- **Retires:** step 21's `actions/cache` and 90-day artifact for the store.
- **Where:** [step 21](steps/loop-off-the-laptop.md#results).

## 2026-11-14: Prove the loop, show the page, be seen; then widen

- **What:** roadmap phase 4. Steps 21 to 23 come first: the jobs off the laptop, the page where a
  reader picks a kind of event and sees what followed, and a counted audience. No new flow or kind
  starts before them, except step 20's part 2, already in progress. A gate on 2027-01-31 judges
  them together: four straight weeks of release days logged on time and graded, none missed; the
  page live for every kind step 17 and step 20 answer; at least 100 unique visitors in one week. A
  miss is answered with a new entry here before any new step. The number of live calls is reported,
  not a bar. Prediction markets lead the Later list once the gate passes. Once a month a goldfish
  zooms out over the whole plan.
- **Why:** a review of every document on 2026-11-14 found the measurement sound and the product
  unseen. After a month live, data/calls.csv held 47 rows and one call (retail sales, 2026-10-15,
  wrong); two of the last release days were missed or late; the page the target describes did not
  exist; 20 roadmap steps had widened what is measured while almost every new kind answered
  *can't say*. Being seen was named as progress on 2026-10-23 and never measured. A goldfish read
  of the first draft dropped a bar of 10 live calls, which the work cannot control.
- **Retires:** "chosen one at a time after step 18's results" for the Later list; it now waits on
  the gate. Part 1b of step 20 waits for the gate too.
- **Where:** [roadmap phase 4](roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen),
  [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish).

## 2026-11-14: A CEO's conduct without a departure is a kind too (by the owner)

- **What:** step 20 keeps two company kinds: a CEO leaving over their own conduct (`ceo`, part 1)
  and a CEO's conduct coming out while they stay (Nvidia, 2026-11-08). Part 2's reader tells them
  apart; the second gets no trigger and no answer until it has its own measured history (part 1b).
- **Why:** the news the owner pastes is mostly the second kind: a board investigates and the CEO
  stays. Part 1's dataset holds departures only, so it cannot answer for it.
- **Retires:** part 2's reading of Nvidia as *not a measured kind*.
- **Where:** [part 2](steps/article-to-trigger.md), [roadmap step 20](roadmap.md#next-steps-in-order).

## 2026-11-14: Every spec is read twice by a fresh reviewer

- **What:** each step's spec gets a goldfish review before anything is measured, and another when
  its results are in. The goldfish sees only the spec, the documents it links, the Legend and the
  Glossary; the author fixes each finding or says why it stands. The template gains two sections
  practice had already added: the rule fixed before measuring, and the results. Specs are named
  for their subject.
- **Why:** the author of a spec carries the conversation that led to it and can no longer see what
  the page leaves out; bars written first protect the result only if a stranger can read them.
- **Retires:** the step-N file naming for steps after the MVP, and step 1 as the worked example.
- **Where:** [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish).

## 2026-11-14: Docs have one way in, and decisions one home

- **What:** a newcomer, human or agent, starts at [docs/README.md](README.md). Choices that set
  direction are recorded here, newest first; the notes inside specs stay where they are. Each fact
  has one home: the roadmap carries one line per step, its spec the bars and the results,
  [status](status.md) only the task in hand, and the [changelog](changelog.md) every finished task.
- **Why:** the documents had grown by appending. A reader had to work through the history to learn
  what was true today, and 91 notes of what was decided or chosen were spread over 43 files.
- **Retires:** the root README's pre-reset design summary, the frozen "Current state" in
  docs/README.md, the results and amendments inside roadmap rows, and the done table in status.
- **Where:** [docs/README.md](README.md), [CLAUDE.md](../CLAUDE.md).

## 2026-11-13: News into triggers now, company news first (by the owner)

- **What:** roadmap step 20 is taken ahead of step 18's grades and step 17's replay. Its first kind
  is a CEO's conduct in question, the company against the S&P 500, from a published dataset of CEO
  dismissals rather than a hand-picked list.
- **Why:** the Nvidia CEO scandal of 2026-11-08 is the kind of headline the tool exists to answer.
- **Where:** [roadmap step 20](roadmap.md#next-steps-in-order), [the spec](steps/ceo-scandals.md).

## 2026-11-11: Python pinned to 3.12

- **What:** the project runs on Python 3.12 only.
- **Why:** Nasdaq's calendar answered the release-day job's Python 3.14 with HTTP 403, and CPI on
  2026-11-10 was logged 49 minutes late (issues #277 to #279).
- **Where:** PR #282, .python-version.

## 2026-11-10: The laptop stays open (by the owner)

- **What:** the laptop that runs the release-day and evening jobs is kept open on release days.
- **Why:** a closed lid suspends it even on power; the jobs report of 2026-11-06 was missed that way.
- **Where:** this entry is the record; it was first noted in status on 2026-11-10.

## 2026-11-04: A headline, answered with what followed (by the owner)

- **What:** the tool finds the event in the news, names its kind, and answers with what followed
  every past event of that kind, for the markets behind what people pay for, over a day, a week, a
  month, a quarter and a year. Each span answers up, down, about the same or can't say, against the
  base rate. The answer is arithmetic on history, never a model's opinion; a model may only read
  the news into a trigger, and runs on this machine. Predicting is built before collecting. The US
  first, then one country at a time.
- **Why:** the reader of the news wonders what comes next; a graded record of past reactions is
  what can answer honestly. The owner first proposed a model's guess, then chose arithmetic.
- **Retires:** "for news the product is a graded reaction record" from 2026-10-23.
- **Where:** [Legend](legend.md#the-target), [roadmap steps 17 to 20](roadmap.md#next-steps-in-order).

## 2026-11-03: News in general is not measured

- **What:** roadmap step 11 closed with no, by the rule written first: no US market moves on the
  president's trade posts. Live detection (rung 7) waits for another reason.
- **Where:** [part 1](steps/presidential-posts.md), [part 2](steps/presidential-posts-2.md).

## 2026-11-03: A statement's tone from a published word list, not a model (by the owner)

- **What:** the Fed statement's direction is read with published dictionaries (steps 13 and 14),
  not a language model.
- **Why:** free, fixed in advance, and checkable.
- **Where:** [step 13](steps/fed-statement-tone.md), [step 14](steps/fed-statement-sentiment.md).

## 2026-10-28: The release-day job merges an all-silent pull request

- **What:** when every row of the day is silent and the run exited cleanly, the job merges its own
  pull request. A call, or anything unusual, stays open for a person.
- **Why:** a silent row claims nothing, and jobless claims bring one every Thursday.
- **Retires:** the job's "it opens, never merges", for silent days only.
- **Where:** [jobless claims](steps/jobless-claims.md), [the release-day job](steps/release-day-job.md).

## 2026-10-23: An entertainment tool with a realistic approach

- **What:** a fortune teller who shows their record, never advice. The bars stay where they were
  fixed; what counts as progress widens to more kinds of events and markets, a steadier cadence,
  and being seen. So: show what is measured (the scoreboard), raise the call count, then widen.
  A statement nobody scheduled is never called before it happens.
- **Why:** the five monthly flows added since step 4 gave no new call, nothing reached anyone but
  the laptop's popup, and half the taxonomy (statements, shocks, news) was unmeasured.
- **Retires:** paid consensus and intraday prices, deferred: they serve a trading use.
- **Where:** [Legend](legend.md#the-target), [roadmap steps 5 to 16](roadmap.md#next-steps-in-order).

## 2026-10-21: Delivery is a desktop popup on this laptop

- **What:** rung 6 delivers each call as a popup on one laptop.
- **Where:** [rung 6](steps/rung-6-delivery.md). The scoreboard page later became the first
  delivery to anyone else.

## 2026-10-20: The record, not a probability

- **What:** a call prints its direction, its walk-forward record as counts and its band, never a
  percentage, until a probability proves honest by rung 3's rule.
- **Why:** rung 3's probabilities were not honest (stated 68%, right 61 to 65%), and on today's
  history no method can pass the test.
- **Where:** [the spec](steps/record-not-probability.md).

## 2026-10-14: The release-day job runs unattended

- **What:** on a release day the call is made, logged and opened as a pull request with no one at
  the keyboard.
- **Where:** [the release-day job](steps/release-day-job.md), answering [rung 5](steps/rung-5-live-path.md).

## 2026-10-13: TradingView's forecast where Nasdaq has none

- **What:** when Nasdaq's calendar has no row, the free consensus falls back to TradingView's.
- **Why:** the day before the first live CPI release, Nasdaq listed no CPI row.
- **Where:** [the spec](steps/consensus-fallback.md).

## 2026-10-09: Free consensus only (by the owner)

- **What:** the expected value is Nasdaq's free published consensus, checked against TradingView's,
  shown beside the trend. Paid consensus and intraday prices are deferred, not dropped.
- **Where:** [the spec](steps/free-consensus.md), [Data sources](data-sources.md#which-free-consensus-is-best).

## 2026-10-07: Sharpen the measurement, then predict, then widen

- **What:** the order of roadmap steps 1 to 4b, after rung 1.
- **Why:** two jobs-report links were clearly real but sat just under the bar, and a better
  expected value was the known, free shortcut.
- **Where:** [roadmap](roadmap.md#next-steps-in-order).

## 2026-10-05: How a CPI surprise is read

- **What:** core CPI against its 12-month trend decides the verdict; the nowcast and headline CPI
  are context. A link's expected direction is fixed in advance, never learned from the data.
- **Where:** [MVP step 4](steps/step-4-surprise.md), its decisions table.

## 2026-09-11: The documents rewritten

- **What:** the current set (legend, roadmap, status, step specs, glossary) replaced the pre-reset
  corpus, which moved to [legacy/](legacy/README.md) as reference, not instructions.
- **Why:** the old corpus described code that did not exist.

## 2026-08-05: The reset

- **What:** main was reset to the M0 data spine, discarding a built replay harness and prediction
  core. Three rules followed: no new package until a second caller needs it; no indirection for a
  single case; a plan doc shorter than the code it specifies. Measure before predicting.
- **Why:** it was over-engineered for the stage, and emitted confident output from placeholder
  values.
- **Retires:** the M0 to M7 milestone scheme.
- **Where:** [CLAUDE.md](../CLAUDE.md); the discarded work is on the main_05082026 branch.
