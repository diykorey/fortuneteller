# Decisions

The choices that set the project's direction, newest first, each with why and where it is written
out in full. Read this before reopening a question: if it is here, it was settled on purpose, and
changing it takes a new entry, not a quiet edit.

What belongs here: a choice of target, method, scope, order or way of working that later work must
respect. What does not: the bars and rules inside one step, which live in that step's spec and are
amended there with a date.

Each entry: **what** was decided, **why**, what it **retires**, and **where** the detail is. *By the
owner* marks a choice the owner made over another on the table.

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
- **Where:** [status](status.md).

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
