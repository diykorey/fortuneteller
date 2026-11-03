# Beat the fortune teller

> Step 12 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-03 from its "later"
> list after step 11 closed. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** before a release, a person writes down which way a market will close that
day. After the close, the guess is graded the way the machine's calls are, and shown beside them.

The [Legend](../legend.md)'s 2026-10-23 amendment makes this an entertainment tool that shows its
record, and counts "being seen" as progress. The machine already logs its calls before the close
and grades them in the evening ([rung 4](rung-4-keep-score.md), [the evening score](evening-score.md)).
This step lets a person play against it under the same rules.

At the end, a person plays like this:
- they add a file of guesses through a GitHub pull request;
- `score` grades each guess, or voids it, and shows the machine's row beside it;
- [the scoreboard](scoreboard.md) shows every guess and each handle's count.

## The way to reach it

Two things make this hard. Both come from the person, not the machine, being the author:

- **Anyone must be able to play without the code.** An outsider has no store and no calendar
  cache, so a command is not the interface; the file is.
  - **How to play**, linked from the page: on GitHub, add a file `data/guesses/<day>-<handle>.csv`
    with one row per market, and open a pull request.
  - The pull request must be merged before the release time.
  - Every rule is checked in grading, so a hand-written file gets the same rules as any other.
- **The witness must hold against the person it binds.** Rung 4's pull request was opened by the
  machine, which had no reason to cheat. A person does, by changing a guess after the release or by
  keeping only the winner of two. So the witness is what was on `main`, not what a pull request said:
  - The guess counts at the time of the commit that added its file to `main`. That commit must be
    GitHub's own (committer `GitHub <noreply@github.com>`, as every merge on this repository is),
    so the time is GitHub's.
  - A pull request that was closed unmerged never reaches `main`.

## What a guess is

A file `data/guesses/<day>-<handle>.csv`, header `flow,instrument,direction`, one row per market:
- `flow`: a flow's CLI name;
- `instrument`: a market symbol as in `data/calls.csv` (`SPY / ES`);
- `direction`: `up` or `down`.

The day and the handle come from the file name. The handle is 1 to 20 letters, digits or `-`. It
is chosen by the player and **not checked**, so one person can play under two handles. The page
says so and shows every handle's full record, losses included.

## The rule, fixed before any guess is graded

**A guess is void, listed with its reason and not graded, if:**
- its flow is not one that `live` calls;
- its market is not one of the flow's links;
- the file reached `main` other than by GitHub's commit, or at or after the release time (08:30 New
  York, `flows.RELEASE_TIME`) on its day;
- the file was changed on `main` after the commit that added it;
- the flow had no release that day, known once the day's close is loaded;
- or it repeats a handle, flow, day and market already guessed. The earliest counts; there can be
  two files only through a renamed handle, so a repeat is within one file.

**Otherwise it is graded, as in rung 2:** right if the day's move on that market closed strictly
the called way, wrong if not. Until then it is *waiting*.
- *Waiting* is never printed as `pending:`. The evening job holds its commit on that word, and a
  guess for a later day must not hold the machine's grades.

**The machine's row beside it:** its logged row for that flow, day and market, as `score` grades
it:
- right or wrong when it has a direction (a call, or *too few* with a direction);
- "no call" when it is silent or small;
- "not logged" when there is no row.

**The record is counts, never a probability.** Each handle shows right out of graded, the count
always beside it.

**The page also says:**
- **the asymmetry:** the person guesses before the release; the machine calls after it, knowing
  the actual, and only on the links and days it chooses;
- **that a guess is public and permanent,** in the repository's history and on the page. A handle
  is dropped from the page on request; the history stays.

*Amends [the scoreboard](scoreboard.md)'s "our numbers only", 2026-11-03:* the guesses are also
shown, and they are their players' numbers.

**Expected outcome, written first.** A handle's right share sits near its markets' base rate of
closing up or down; the machine's calls are few. The step delivers the game, not a finding.

## How you know it is right

The step 1 tests include:
- a file added by a non-GitHub commit is void;
- a file added at 08:30 is void;
- a file changed after it was added is void;
- a market outside the flow's links is void;
- a day the flow did not release is void;
- a guess for a later day shows as *waiting*, and `score` prints no `pending:` line for it;
- planted rows are graded right and wrong, each beside a machine row that is right, too few,
  silent and not logged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `score` reads `data/guesses/`, grades or voids each guess and prints a `guesses` block | The tests above pass; `score` on the real data prints the same calls block as before |
| 2 | The scoreboard: every guess, each handle's count, the asymmetry and "how to play" | On a test database the JSON's counts equal `score`'s lines; the page shows a guess beside the machine's row |
| 3 | The first live round: a release `live` calls, guessed through a merged pull request; results here | At least one guess graded by the evening score that day or the next |

## What this step does not do

No `guess` command, no accounts, no web form, no stakes, no probability for a person, no
head-to-head total, no change to the machine's calls or rules or to the evening job.

## Technical details

- **Settings and data:**
  - `settings.guesses_dir` is `data/guesses`, with a `.gitkeep`.
  - `tests/conftest.py` points it at a temporary directory, as it does `calls_path`.
- **Reading:** `study.read_guesses(directory) -> list[Guess]`.
  - `Guess` holds `day`, `who`, `flow`, `instrument`, `direction` (+1 or −1), `path`.
  - A bad file name, header or row is an error, as in `read_calls`.
- **Witness:** `study.guess_witness(path) -> tuple[datetime, bool] | None`, read with `git log` on
  `main`.
  - It returns the committer time of the commit that added the file, and whether that committer is
    `GitHub <noreply@github.com>`.
  - It returns `None` when a later commit changed the file.
  - The tests build a temporary repository with `GIT_COMMITTER_*` set.
- **Grading:** `study.score_guesses(guesses, rows, con) -> list[GradedGuess]`, with
  `state ∈ {right, wrong, waiting, void}`, a reason, and the machine's grade.
  - The links are the items of `flow.surprise_rule.expected_sign` with a nonzero sign.
  - "Called by `live`" is `flows.called_live(flow)`.
  - The move is `observations.ret_1d` for the release's event.
- **Printing:** `score` prints its `guesses` block before `missed:`, one line per guess, then each
  handle's count. Its labels are `void` and `waiting`, indented, never `pending:`.
- **The page:**
  - `scoreboard` adds a `guesses` list and per-handle counts to `data.json`;
  - the template `src/fortuneteller/scoreboard.html` gets one table and the two notices.
- **Docs:**
  - `docs/glossary.md`: guess, void guess, handle;
  - `docs/precision.md`: the witness, the unchecked handle;
  - `docs/steps/scoreboard.md`: the amendment;
  - `docs/status.md`.
