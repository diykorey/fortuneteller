# Ask the fortune teller

> Step 22 of the [Roadmap](../roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen), phase 4,
> chosen 2026-11-14. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the scoreboard page gets a section where a reader picks a kind of event and
sees what followed it. For example, from [step 17, part 1b](what-follows-jobs.md#results): "After a
jobs report above the consensus, the 10-year yield over the next day: up 47 times, about the same
8, down 13, of 68. On every day of its history: up N, about the same N, down N, of M. Answer: up.
Replayed, it held: right 38 of 57." Most kinds read "can't say", with what markets did anyway.

The [Legend](../legend.md#the-target)'s target is a reader who brings a headline and is told what
followed. Step 17 measured those answers, but they live only in what the follows command prints.
Nobody outside the project can see them. Until step 20 reads the kind from the news, the reader
picks it.

At the end: the page's new section, *Ask the fortune teller*, answers every kind below, and the
evening job keeps it current. This is the gate's second bar
([roadmap](../roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen)).

| Flow | Its kinds | Spans |
| --- | --- | --- |
| Fed decisions | cut, hold, hike | day, week, month; quarter and year |
| The jobs report, retail sales, CPI, jobless claims | above, as expected, below the consensus | day, week, month |
| ECB decisions | cut, hold, hike | day, week, month |
| A CEO's conduct in question (step 20) | scandal, the company against the S&P 500 | day, week, month |

Spans start from the event's day, as follows prints by default, never from the reaction close
(that is step 18's question).

## The way to reach it

- **One computation, two readers.** The code that picks a flow's kinds and computes its cells moves
  out of the follows command into one function, and both the command and the page call it.
- **The words are written in Python, not on the page.** Each cell's sentence is built next to its
  numbers and stored in the data, so a test can read it. The page's script only lays out what the
  data holds.
- **Counts, not rates.** Each base is today a share of all spans. The reader is promised counts,
  never a percentage, so the base also keeps how many spans it rests on. The CEO kind is the
  exception: its base is an average over each company's own past two years, so it has no single
  count; its sentence says so and gives no base numbers.
- **Every walk-forward verdict has words.** "Replayed, it held: right 38 of 57"; "replayed, it did
  not hold: right 17 of 34"; "too few replayed to judge: right 4 of 6"; "not replayed" when none was
  graded. Only *holds* is marked.
- **"Can't say" still says something.** Such a cell shows its counts beside its base, so the reader
  sees what markets did anyway. It is never coloured as an answer.
- **A flow that cannot be computed is named, never shown stale.** The Fed's kinds need a FRED key,
  the ECB's its rates; with no events stored, a flow cannot be computed either. The page lists such
  a flow with the reason, and the others still show. A CEO event whose company has no closes is a
  hole, as follows counts it, not a failure.

## The rule, fixed before measuring

This step measures nothing new: it shows step 17's, step 19's and step 20's numbers. The rule is
that it shows them exactly.

- **Same numbers:** for each flow, every cell in the data equals the line follows prints for that
  kind, span and market. The counts, the graded and right counts, and the cycles column of the Fed's
  long spans are equal as integers; the base's shares equal follows' to two decimals, as it prints
  them; the answer and the verdict are the same words.
- **Expected outcome, written before the page is first built on real data:** exactly three cells
  hold walk-forward, all on the day: after a jobs report above the consensus, the 10-year and the
  5-year yields up ([step 17, part 1b](what-follows-jobs.md#results)); after a CPI above the
  consensus, the 5-year breakeven up, 23 of 30 graded ([step 19, part 2b](breakeven.md#results)).
  A release since those results may move a count by one or two; it should not add or remove a
  hold, though the breakeven sits on the bar of 30 graded. A fourth hold, or a missing one, is a
  finding to explain before the step is done.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~One function returns a flow's events, kinds, cell order and cells; the follows command calls it~~ **done** 2026-11-14 | The existing follows tests pass unchanged, and a new one runs follows for the CEO flow through it |
| 2 | ~~The base keeps how many spans it rests on~~ **done** 2026-11-14 | A test gives a base of 9 moves and reads 9 |
| 3 | ~~The scoreboard data gains *ask*: per flow its kinds, events per kind, first and last day, and per cell the numbers and its sentence; and *ask_left_out*, each flow with its reason~~ **done** 2026-11-14; each cell also carries its market's name from data/seed/instruments.csv | A test on test_what_follows.py's store compares every cell with the follows lines for the same store, field by field; a second gives no FRED key and finds the Fed left out and the others there |
| 4 | ~~The page shows the section: a choice of kind, then a table per span, one row per market, the sentence under it~~ **done** 2026-11-14: the page written from test_scoreboard.py's store, opened in headless Chrome, showed three tables of 25 rows and the reasons for the six flows left out, with no script error | A test finds the section in the written page, and the page, opened in a browser on the test data, shows a kind's tables |
| 5 | ~~On the published page, after the evening job~~ **done** 2026-11-19, [below](#step-5) | Every kind in the table above appears with its cells; none is left out |

### Step 5

*2026-11-19*, [the evidence](ask-the-fortune-teller-step5.txt): the published page after the
evening job of 2026-11-18.

- **Every kind is there, none left out:** the seven flows of the table above, 19 kinds in the
  picker, each with its cells: 93 per span (31 markets × 3 kinds), the Fed's also over the quarter
  and the year, the CEO's 1 per span (the company against the S&P 500); `ask_left_out` empty.
- **The expected outcome, right:** exactly three cells hold, all on the day: after a jobs report
  above the consensus the 10-year yield (39 right of 58) and the 5-year (38 of 58); after a CPI
  above the consensus the breakeven (23 of 31). A release since step 19 moved the breakeven's
  graded count from 30 to 31; no hold was added or lost.
- **On screen:** opened in Chrome, a jobs report above the consensus shows the day's, the week's
  and the month's tables of 31 markets, each row with its sentence; no console error.

## How you know it is right

- **Same numbers, by a test:** step 3's test fails if the data and follows' lines differ on any
  field of any cell.
- **The sentence matches its cell, by a test:** for a cell built by hand, the sentence names its
  event counts and its base counts, not its walk-forward counts, and its verdict's words.
- **No silent gap, by a test:** with no FRED key, the Fed is listed as left out with the reason.
- **No percentage, by a test:** no sentence in the data holds a "%" sign.
- **The expected outcome:** step 5 is checked against the three holds above, on the real data.

## What this step does not do

- It reads no news. The reader picks the kind; step 20 reads it from a headline.
- It adds no kind, market or span, and changes no bar.
- It shows no percentage and grades nothing live.
- It needs no server: the page stays static, its data written by the evening job.

## Technical details

- **Step 1:** in __main__.py, follows_cells(name, con, after, long) returns the events, the kinds,
  the order, the cells and the noun, or raises with the message follows prints today. _follows
  and scoreboard_data call it. No new module.
- **Step 2:** study.Base gains n; base_of fills it; the CEO's averaged base passes none.
- **Step 3:** scoreboard_data gains "ask", a list with one entry per flow: name, noun, kinds,
  events per kind, first, last, and cells, each with kind, span, market, up, same, down, base
  shares and base n (none for the CEO), answer, graded, right, verdict, cycles (the Fed's long
  spans), and say, its sentence. "ask_left_out" lists flow and reason. The Fed's quarter and year
  come from a second, long run.
- **Step 4:** scoreboard.html gains the section after the week ahead: a select of kinds, a table per
  span, the sentences under it.
- **Tests:** tests/test_what_follows.py (its store and the Fed and release flows),
  tests/test_ceo_scandals.py (the CEO flow), tests/test_scoreboard.py (the data and the page), in
  the given / when / then shape.
