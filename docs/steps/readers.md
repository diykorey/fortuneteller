# A page a stranger reads

> Step 44 of the [Roadmap](../roadmap.md), serving [step 23](be-seen.md)'s *readers* bar at the
> gate: at least 100 unique visitors in one week. Terms are in the [Glossary](../glossary.md):
> *holds*, *kind*, *cell*, *the answers that hold*, *the workings*, *the gate*. Chosen
> 2026-11-21 by the owner, after a first-visitor review of the published page.

## The goal

**In plain words:** a stranger who opens the page from a post understands in ten seconds what it
offers, sees an answer with a direction first, and finds a dated reason to come back.

At the end the published [scoreboard page](scoreboard.md):
- opens on what it is and on the answers that hold, in plain words;
- names markets, not codes, outside a closed *workings* part;
- shows, in its week ahead, the Dow companies reporting in the next seven weekdays, each with what
  followed past reports of each kind;
- is rewritten every weekday evening, so that list is never more than a day old.

`weekly-post` carries the same lines. The gate's bar is unchanged.

## The way to reach it

- **What the review found (2026-11-21, the baseline).** A fresh reader was given only the page's
  address and the prompt in [Technical details](#technical-details). It found:
  - the first screen is the line "every link's record on the replay" and a Fed-cut table of
    *can't say*;
  - an answer is given by 94 of the page's 2,988 cells (83 up or down, 11 about the same), and they
    sit behind the menu;
  - the week ahead is Wednesday's PCE with 14 rows of *silent*;
  - 21 market codes are listed as not understood.

  The counts are from `docs/scoreboard/data.json` as written 2026-11-19 (the command is in
  Technical details).
- **The first screen** is what a 1366 by 800 window shows before scrolling. It carries:
  - One sentence on what the page is: what followed past events of a kind, counted, an
    entertainment tool.
  - *The answers that hold*: every cell whose verdict is *holds*, less the kind cells (those read
    off the kind's own definition) and those the placebo reads as *the period*, as *Ask* marks
    neither as held. Each is shown as its cell's sentence (`say`) and links to its
    `#ask/FLOW/KIND` address. They are listed in *Ask*'s order of flows, kinds and cells. On
    2026-11-19's data that is seven:
    - the jobs report above → the 10-year and 5-year Treasuries' yields up on the day;
    - CPI above → the 5-year breakeven up;
    - OPEC+ *oil up* → gasoline up;
    - a Dow company in line with the consensus → down against the S&P 500 on the day;
    - a Dow company below the consensus → down against the S&P 500 on the day and over the week.
  - *Ask* opens on the first of them, not on the Fed's cut.
- **Names, not codes.** Every table outside the workings names each market as *Ask* does, by its
  name in the data (`market_name`). The *replay*, *does the move follow* and *release days*
  sections go inside one `<details>` called *The workings*, closed. Their numbers do not change.
- **Earnings ahead.**
  - **Where the list comes from:** `scoreboard` asks Nasdaq's earnings calendar (the address
    [step 31](earnings.md) reads) for each of the next seven weekdays. It keeps each company that
    is a Dow member on the report's day.
  - **What each report shows:** the company, the day, and before the open, after the close or
    *time not given*. Then, for each of the three kinds (above, as expected, below), *Ask*'s cell
    for that kind, the company against the S&P 500 on the day. It is measured from the close
    before, as the rest of the page is.
  - **How each cell reads:** a cell that holds shows its answer and its replay's counts ("down,
    right 156 of 219 replayed"). Any other cell shows no direction: *did not hold*, *too few*, or *it reads as the
    period*.
  - **Nothing is said before the report lands.** The kind comes from the actual, so the line
    reads *if it misses*, as the week ahead already reads *if above*.
  - **A failed ask** writes *the earnings calendar could not be read*, as the week ahead does.
  - *Amended 2026-11-21, by the owner ([step 45](sp500-on-the-page.md)):* the list is every S&P
    500 member's report, under the S&P 500 earnings group's three lines given once, in place of a
    row per Dow company. Step 44's bars are unchanged.
- **Written each weekday.** Today the page is written only when `score` commits.
  - The evening job also writes it on a day with nothing to score. If it differs, the job commits
    it in a pull request of its own, `scoreboard-DAY`.
  - That pull request is merged once its checks pass, as the score's is (decisions, 2026-11-20).
- **The obstacle: few Dow reports before the gate.** Only Salesforce (2026-12-02) and Nike
  (2026-12-17) are on step 34's list before January. The list is thin until mid-January, and this
  step says so rather than widening to the S&P 500. The S&P 500's reports are measured on a copy of
  the store (step 36), not on the page.

## The rule, fixed before measuring

- **The bar, a second first-visitor review.**
  - It is run once the page is published, by a fresh reader who sees only the page, with the
    prompt in Technical details.
  - It is run in a week with a Dow report on the list. The first is the week of 2026-11-30, for
    Salesforce; if the page is not published by then, the next such week.
  - It passes when all four hold:
    1. the reader states what the page offers, in its own words, from the first screen;
    2. it quotes an answer with a direction from the first screen;
    3. it names a dated upcoming report with past counts;
    4. it lists no market code as not understood outside the workings.
  - The review is read once, as written. It is not run again to get a better answer.
- **Counted, not barred:** the week's unique visitors, as step 23 counts them. This step's
  changes go up mid-week, so no week is credited to them alone.
- **Expected outcome, written first:**
  - the second review passes all four;
  - the gate's readers bar is still expected *not seen*, as step 23 wrote: the best week 30 to
    50 visitors.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The first screen and *the answers that hold* | A test writes the page from a stubbed data file of a holding cell, a kind cell that holds, and a cell that does not. Only the first is listed, in *Ask*'s order, and *Ask*'s first pick is its kind |
| 2 | Names, not codes, and *the workings* | A test reads the written page's text outside the `<details>` as whole words. No code from the data's market list is in it, written as the data writes it (`SPY / ES`, `ALL`, `COIN`), but where the market's name holds its code (`DAX`, `VIX (equity volatility)`). Text inside `<code>`, the guess file's format, is not read The three sections are inside the `<details>` |
| 3 | Earnings ahead | Tests with a stubbed Nasdaq page cover a member reporting, a non-member left out, a row without a time, and a failed ask. Each kind's line carries that kind's own cell from the close before. A holding cell shows its counts, and any other cell no direction |
| 4 | `weekly-post` gains the week ahead's lines and the first answer that holds | A test on a stubbed week finds each report's line, as on the page, and the first answer's sentence |
| 5 | The evening job writes the page each weekday | `scripts/release-day.sh` runs `scoreboard` on a day with nothing to score, commits only when the page differs, and waits on an open `scoreboard-` pull request as on the others. Checked on the first evening after it is installed |
| 6 | Published, then the second review | Its answers are written here against the four bars |

## How you know it is right

- The answers that hold equal, cell for cell, the cells with verdict *holds* that
  `fortuneteller follows` prints for each flow, less the kind cells and the period's
  ([step 29](ask-phase-5.md)'s check).
- On the published page, each earnings line's three cells equal *Ask*'s day cells for that kind.
  A test swaps the stubbed kinds' counts and checks that the lines follow.
- The workings' numbers equal the page of the same data written before this step.

## What this step does not do

- No new kind, source of events or market.
- No call before a report.
- No S&P 500 earnings on the page.
- No change to *Beat the fortune teller*, to the post's channel or to the counter.

## Technical details

- **Template:** `src/fortuneteller/scoreboard.html`. The data gains two keys, both written by
  `scoreboard_data` in `__main__.py`:
  - `holds`: the list;
  - `earnings_ahead`: rows of company, day, time and three cells, or null when the ask failed.
- **The calendar:** Nasdaq's page is read with the headers `scripts/nasdaq_earnings.py` uses. Its
  `time` field gives the time: `time-pre-market` is before the open, `time-after-hours` after the
  close, and anything else is *time not given*. The Dow's members come from `data/seed/dow.csv`, as
  of each report's day.
- **The baseline counts:** `python3 -c` over `docs/scoreboard/data.json`, counting every cell of
  every `ask` entry and those whose `answer` is up, down or about the same.
- **The review prompt** (the baseline's, used again): a first-time visitor from a LinkedIn link,
  who knows nothing of the project, fetches the page and renders it. It answers six questions:
  1. what the first screen says the page offers, quoting its first lines;
  2. the most interesting thing for an ordinary person;
  3. every word, abbreviation or number it could not understand;
  4. what would make it leave within 10 seconds;
  5. what would make it come back, and anything dated and upcoming;
  6. the three changes that would most help.

  The full text is in `steps/readers-review.txt`, with the baseline's answers.
- **Docs:**
  - this spec;
  - [scoreboard](scoreboard.md) for the new parts and the weekday writing;
  - the glossary (*the workings*, *the answers that hold*);
  - status, the changelog and roadmap row 44.
