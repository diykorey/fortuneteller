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
  - The pull request must be merged before the release time. Only the owner can merge, so a guess
    counts only if the owner merges it in time. The page says so, and lists the guess pull requests
    that were not merged in time.
  - A pull request that touches anything but its own new file is refused.
  - Every rule is checked in grading, so a hand-written file gets the same rules as any other.
- **The witness must hold against the person it binds.** Rung 4's pull request was opened by the
  machine, which had no reason to cheat. A person does, by changing a guess after the release or by
  keeping only the winner of two. A commit's own committer and date are plain text anyone with push
  can write, so the witness is GitHub's record of the merge:
  - The commit that added the file to `main` is found along `main`'s first parents, which gives the
    merge (or squash) commit.
  - GitHub is asked which pull request has that commit as its `merge_commit_sha`. That pull
    request's `merged_at` is the guess's time, and GitHub sets it.
  - The guess is read as that commit holds it, so a later edit to the file, by anyone, changes
    nothing.
  - A pull request closed unmerged never reaches `main`, and a file pushed without a pull request
    has no `merged_at`.

## What a guess is

A file `data/guesses/<day>-<handle>.csv`, header `flow,instrument,direction`, one row per market:
- `flow`: a flow's CLI name;
- `instrument`: a market symbol as in `data/calls.csv` (`SPY / ES`);
- `direction`: `up` or `down`.

The day and the handle come from the file name: the day is its first ten characters, the handle the
rest, 1 to 20 lowercase letters, digits or `-`. The handle is chosen by the player and **not
checked**, so one person can play under two handles. The page
says so and shows every handle's full record, losses included.

## The rule, fixed before any guess is graded

**A guess is void, listed with its reason and not graded, if:**
- its flow is unknown, or not one that `live` calls;
- its market is not one of the flow's links;
- its file reached `main` without a merged pull request, or the pull request was merged at or after
  the release time (08:30 New York, `flows.RELEASE_TIME`) on its day;
- the flow had no release that day: none is stored for that day, though a later release of the
  flow is (so a late load waits, not voids);
- or it repeats a flow and market already in its file: the first row counts.

**Otherwise it is graded, as in rung 2:** right if the day's move on that market closed strictly
the called way, wrong if not. Until then it is *waiting*.
- *Waiting* is never printed as `pending:`. The evening job holds its commit on that word, and a
  guess for a later day must not hold the machine's grades.

**The machine's row beside it:** its logged row for that flow, day and market, as `score` grades
it:
- right or wrong when it has a direction (a call, or *too few* with a direction);
- void or waiting when `score` voids it or waits on it;
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
- in a temporary repository: a file added on a side branch and merged is found at the merge commit,
  and one added by a squash commit at that commit;
- a file whose pull request was merged at 08:30 is void, and one with no pull request is void (the
  GitHub lookup replaced in the test);
- a file edited after it was added is graded as added;
- a market outside the flow's links is void;
- a day the flow did not release is void, and one whose release is not loaded yet waits;
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
  - Only `*.csv` files are read, so the `.gitkeep` is skipped. A bad file name, header or row voids
    that file's guesses, with the reason, so one bad pull request cannot stop `score`.
- **Witness:** two functions.
  - `study.added_in(repo, path) -> str`: the commit that added the file, from
    `git -C <repo> log --first-parent --diff-filter=A --format=%H HEAD -- <path>`. `HEAD` is the
    checkout `score` runs in (the job's is `origin/main`, freshly fetched). If git fails or the
    history is missing, it is an error, not a void.
  - `study.merged_at(sha) -> datetime | None`: GitHub's `merged_at` for the pull request whose
    `merge_commit_sha` is `sha`, from `gh api repos/{repo}/commits/{sha}/pulls`. Tests replace it.
  - The guesses are read from `git show <sha>:<path>`.
- **Grading:** `study.score_guesses(guesses, rows, con) -> list[GradedGuess]`, with
  `state ∈ {right, wrong, waiting, void}`, a reason, and the machine's grade.
  - The links are the items of `flow.surprise_rule.expected_sign` with a nonzero sign.
  - "Called by `live`" is `flows.called_live(flow)`.
  - The move is `observations.ret_1d` for the release's event.
- **Printing:** `score` prints its `guesses` block before `missed:`, and none when there are no
  guesses, so the output is unchanged today.
  - The header is `guesses: N`.
  - Then one line per guess: `  <day> <handle> <flow> <instrument> <up|down>: <state>; machine:
    <grade>`, with the reason after a void.
  - Then one line per handle: `  <handle>: <right> of <graded> right`.
  - No line starts with `pending:`.
- **The page:**
  - `scoreboard` adds a `guesses` list and per-handle counts to `data.json`;
  - the template `src/fortuneteller/scoreboard.html` gets one table and the two notices.
- **Docs:**
  - `docs/glossary.md`: guess, void guess, handle;
  - `docs/precision.md`: the witness (GitHub's `merged_at`), the owner's merge as a selection, the
    unchecked handle;
  - `docs/steps/scoreboard.md`: the amendment;
  - `docs/status.md`.
