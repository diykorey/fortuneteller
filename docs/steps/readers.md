# A page a stranger reads

> Step 44 of the [Roadmap](../roadmap.md), serving [step 23](be-seen.md)'s *readers* bar at the
> gate. Terms are in the [Glossary](../glossary.md): *holds*, *kind*, *cell*, *the gate*. Chosen
> 2026-11-21 by the owner, after a first-visitor review of the published page.

## The goal

**In plain words:** a stranger who opens the page from a post understands in ten seconds what it
offers, sees an answer with a direction first, and finds a dated reason to come back.

At the end the published [scoreboard page](scoreboard.md) opens on what it is and on the answers
that hold, in plain words; names markets, not codes, outside a closed *workings* part; and its
week ahead names the Dow companies reporting in the next seven days, each with what followed past
reports of each kind. `weekly-post` carries the same lines. The gate's bar is unchanged.

## The way to reach it

- **What the review found (2026-11-21).** A fresh reader, given only the page's address, said:
  - the first screen is the line "every link's record on the replay" and a Fed-cut table of
    *can't say*;
  - only 94 of 2,988 answers give a direction, and they sit behind the menu;
  - the week ahead is Wednesday's PCE with 14 rows of *silent*;
  - more than 20 market codes are left unexplained.

  That review is this step's baseline.
- **The first screen.** One sentence on what the page is: what followed past events of a kind,
  counted, an entertainment tool. Then *the answers that hold*: every cell whose verdict is
  *holds*, less those read off the kind's own definition (`kind_cell`), each one sentence from its
  `say`, linking to its `#ask/FLOW/KIND` address. Today that is seven. *Ask* then opens on the
  first of them, not on the Fed's cut.
- **Names, not codes.** Every table outside the workings names each market as *Ask* does, by
  `market_name`. The *replay*, *does the move follow* and *release days* sections go inside one
  `<details>` called *The workings*, closed. Their numbers do not change.
- **Earnings ahead.** The evening scoreboard run asks Nasdaq's earnings calendar (the same
  address [step 31](earnings.md) reads) for each of the next seven weekdays, and keeps the Dow's
  members as of that day. For each report: the company, the day, before or after the bell, and
  for each kind (above, in line, below) the page's day cell for that kind. A cell that holds
  shows its counts; any other shows its verdict.

  Nothing is said before the report lands. The kind comes from the actual, so the line reads
  *if it misses*, as the week ahead already reads *if above*.

  A failed ask writes *the earnings calendar could not be read*, as the week ahead does.
- **The obstacle: few Dow reports before the gate.** Only Salesforce (2026-12-02) and Nike
  (2026-12-17) are on step 34's list before January. The teaser is thin until mid-January, and
  this step says so rather than widening to the S&P 500. The S&P 500's reports are measured on a
  copy of the store (step 36), not on the page.

## The rule, fixed before measuring

- **The bar, a second first-visitor review.** It is run once the page is published, with the
  baseline review's prompt, by a fresh reader who sees only the page. It passes when all of these
  hold:
  1. the reader states what the page offers, in its own words, from the first screen;
  2. it quotes an answer with a direction from the first screen;
  3. it names a dated upcoming item with past counts, where there is one that week;
  4. it lists no market code as not understood outside the workings.
- **Counted, not barred:** the week's unique visitors, as step 23 counts them. This step's
  changes go up mid-week, so no week is credited to them alone.
- **Expected outcome, written first:**
  - the second review passes on 1, 2 and 4, and on 3 only in a week with a Dow report;
  - the gate's readers bar is still expected *not seen*, as step 23 wrote: the best week 30 to
    50 visitors.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The first screen and *the answers that hold* | A test writes the page from a stubbed data file. Every cell that holds and is not a kind cell is in the list, and none other is. *Ask*'s first pick is the first of them |
| 2 | Names, not codes, and *the workings* | A test finds no code from `markets` in the text outside the `<details>`, and the three sections inside it |
| 3 | Earnings ahead | Tests with a stubbed Nasdaq page cover a member reporting, a non-member left out, and a failed ask. Each line carries the three kinds' day cells, and a holding cell shows its counts |
| 4 | `weekly-post` gains the week ahead's lines and the first answer that holds | A test on a stubbed week |
| 5 | Published, then the second review | Its answers are written here against the four bars |

## How you know it is right

- The answers that hold equal, cell for cell, the cells with verdict *holds* that `follows` prints
  (step 29's check). A list typed by hand would drift.
- An earnings line never shows a direction for a kind whose cell does not hold.
- The workings' numbers are byte for byte those of today's page, only moved.

## What this step does not do

- No new kind, source of events or market.
- No call before a report.
- No S&P 500 earnings on the page.
- No change to *Beat the fortune teller*, to the post's channel or to the counter.

## Technical details

- **Template:** `src/fortuneteller/scoreboard.html`. The data gains `holds` (the list) and
  `earnings_ahead` (rows of company, day, time and three cells, or null when the ask failed),
  written by `scoreboard_data` in `__main__.py`.
- **The calendar:** Nasdaq's page is read with the headers `scripts/nasdaq_earnings.py` uses. Its
  `time` field (`time-pre-market`, `time-after-hours`, or neither) gives before or after the bell.
  The Dow's members come from `data/seed/dow.csv` as of each day.
- **Docs:** this spec; [scoreboard](scoreboard.md) for the new parts; the glossary
  (*the workings*, *answers that hold*); status, the changelog and roadmap row 44.
