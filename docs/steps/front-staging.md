# The front page's guesses, approved

> Step 51 of the [Roadmap](../roadmap.md), on [the guess ledger](guess-ledger.md). Terms are in
> the [Glossary](../glossary.md): *our guess*, *stated forecast* (here *tested forecast*),
> *front page*, *front pull request*, *evening score*. Asked for 2026-11-22 by the owner:
> "we should have possibility to adjust prediction wording … some staging to discuss and approve
> wording before publishing public those 5 only", option A of four put to them: a pull request of
> its own each evening (the others: a private page with approve buttons, a hidden preview page
> changed through chat, or a second model pass with no person).

## The goal

**In plain words:** every guess still goes into the public ledger the evening it is made, as now.
Only the few shown on the front page wait: each evening the job proposes them, with their words,
in a pull request of their own, and the owner rewords, removes or approves them there. They reach
the front page when that pull request is merged, and not before. A rewording changes the words
shown, never what is graded: the market, the direction and the dates.

At the end:

- `docs/predicts/front.csv` holds the approved front-page guesses, one row each: `stated, market,
  direction, last, statement, why, source`;
- `docs/predicts/front-next.csv`, written by `fortuneteller scoreboard` each evening, holds that
  evening's proposal, in the same columns;
- the page shows the tested forecasts, then the open rows of `front.csv` in the file's order,
  five cards at most: a row is open while its end date is on or after New York's day, as a tested
  forecast is;
- `front.csv` starts with the two guesses the page showed when this step began (the yen to
  2026-12-31, the fear gauge to 2027-01-15), so the page loses nothing before the first merge.

## The way to reach it

- **The page reads `front.csv` itself,** in the reader's browser, so merging a reworded file
  publishes it at once (GitHub Pages serves `docs/` from `main` as it is). No step regenerates the
  page after the merge; the evening's page no longer carries the guesses.
- **The proposal:** `scoreboard` picks the guesses as step 50 does (a promoted tag, then
  confidence, then the soonest end date, enough to fill five cards after the tested forecasts) and
  writes them to `front-next.csv`, with the ledger's statement and reasoning as their words. A
  guess already in `front.csv` keeps its approved words.
- **The pull request:** the evening score (`scripts/release-day.sh score`) writes the page into
  a pull request it merges once its checks pass, as before. After it, the job copies `front-next.csv` over
  `front.csv` on a fresh `main`. When that changes `front.csv` it closes a front pull request of
  an earlier evening that holds only the job's commit, and opens *The front page's guesses, DAY*
  on branch `front-DAY` (DAY New York's date, `YYYY-MM-DD`). It never merges it. A front pull
  request the owner or anyone else has added a commit to is left open, and that evening proposes
  nothing, so no rewording is thrown away. Until the owner merges one, the page keeps the guesses last approved, each
  shown while its end date has not passed.
- **What the owner may change:** `statement` and `why`, or remove a row, or add one copied from
  an open ledger guess. `stated`, `market`,
  `direction`, `last` and `source` are locked: a test reads the two files and fails when a row of
  `front.csv` matches no ledger row on all five. The grade reads only the ledger, so a rewording
  cannot change it; the review and the lessons read the ledger's words, so the model learns from
  what it wrote. The card's *Higher* or *Lower* badge and its date come from the locked fields, so
  a statement reworded against its direction shows beside the badge that contradicts it; keeping
  the words true to the claim is the owner's part of approving them.
- **The page with no `front.csv`,** or one it cannot read, shows the tested forecasts alone.

## The rule, fixed before measuring

- **No bar:** this step changes who approves the words, not what is guessed or how it is graded.
- **Expected outcome:** on the first evening whose proposal differs from `front.csv`, one front
  pull request opens, and until it is merged the page shows the same two guesses as the seeded
  `front.csv`. (*Amended 2026-11-22, before any evening ran it:* it read "the first evening the
  job runs it"; the job opens one only when the proposal changes, and the results below found
  tonight's proposal unchanged.)

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scoreboard` writes `front-next.csv`; the page reads `front.csv` | Tests: the proposal is step 50's choice in its order with the ledger's words, and a guess already approved keeps its approved words; the page rendered by Chrome over a local server shows two tested forecasts and the open rows of `front.csv` with a comma and a quote in their words, and drops a row past its end date |
| 2 | Locked fields | A test fails on a `front.csv` row whose market, direction, end date, day stated or link differs from every ledger row, and passes on the repository's own files; it is part of `pytest`, which CI runs on every pull request, the front ones included |
| 3 | The job | `scripts/release-day.sh score` copies `front-next.csv` over `front.csv` only on a fresh `main` and commits only `front.csv` to `front-DAY`; it closes an earlier `front-` pull request only when it holds one commit, and calls no merge on a `front-` branch. Checked by reading the script, and on the first evening by the open pull request |
| 4 | Published | The first front pull request is open; its number and the date written in Results |

## How you know it is right

- **A rewording cannot regrade:** the grade is computed from `our-guesses.csv` alone, which the
  front pull request does not touch; the test of step 2 runs on each front pull request in CI.
- **Nothing reaches the front page unmerged:** `scoreboard` writes `front-next.csv` and never
  `front.csv` (`git diff --stat` of the evening's merged pull request shows it); the only commit
  to `front.csv` the job makes is on a `front-` branch.

## What this step does not do

No approval of the ledger itself: every guess stays public the evening it is made. No change to
the tested forecasts' words. No mark on the stats page for a reworded guess.

## Technical details

- **The files:** both written by `_write_rows` (`\n` line ends, quoted when needed); the page's
  parser reads quoted fields with commas, doubled quotes and line breaks.
- **Docs:** this spec, step 50's amendment (the front page's guesses wait for approval), the
  glossary (*front pull request*), a decisions entry, status, changelog, roadmap row 51.

## Results

**Steps 1 to 3, 2026-11-22.** `uv run pytest` passes the tests of each row (the Chrome one is
`tests/test_predicts.py`, which pytest runs with `google-chrome --headless`):

- the proposal keeps the owner's words for an approved guess and takes the ledger's for the next,
  in step 50's order;
- Chrome, at 420 and 1280 pixels wide over a local server, shows two tested forecasts and the two
  open rows of a `front.csv` worded with a comma, a quote and a line break, and drops the row past
  its end date;
- each of the five locked fields, changed, is refused, and the repository's own `front.csv`
  passes.

`docs/predicts/front.csv` is seeded with the two guesses the page showed: the yen to 2026-12-31
and the fear gauge to 2027-01-15. The repository's own page, served by `python3 -m http.server`
from `docs` and rendered by `google-chrome --headless=new --dump-dom` at 420 pixels, shows five
cards: the three tested forecasts and these two, each headed *Our guess · made Nov 22* with its
badge and words. `front-next.csv` was written by `stated_forecasts`, the function `fortuneteller
scoreboard` calls, run from Python on a copy of the store with closes to 2026-11-20; with three
tested forecasts it has two places, and proposes the same two, so no front pull request is due.

`scripts/release-day.sh` was read against row 3: it copies `front-next.csv` over `front.csv` on a
detached `origin/main`, goes on only when `git diff` finds `front.csv` changed, closes an
earlier `front-` pull request only when `git rev-list --count origin/main..` gives 1, commits only
`front.csv` to `front-DAY`, and calls no merge on it.

**Pending:** step 4, the first front pull request, from the first evening score whose proposal
differs, from Monday 2026-11-23; its number goes here. With it, the two checks of *How you know it
is right* (the evening's merged pull request leaves `front.csv` alone; CI runs the locked-field
test on the front pull request).
