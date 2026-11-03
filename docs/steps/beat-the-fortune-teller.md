# Beat the fortune teller

> Step 12 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-03 from its "later"
> list after step 11 closed. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** before a release, a person writes down which way a market will close that
day. After the close, their call is graded the way the machine's is, and shown beside it.

The [Legend](../legend.md)'s 2026-10-23 amendment makes this an entertainment tool that shows its
record, and counts "being seen" as progress. The machine already logs its calls before the close
and grades them in the evening ([rung 4](rung-4-keep-score.md),
[the evening score](evening-score.md)). This step lets a person play against it with the same rules.

At the end: a `guess` command logs a person's call, `score` grades it beside the machine's, and
[the scoreboard](scoreboard.md) shows each person's record.

## What a guess is

One row per person, release and market, in a committed `data/guesses.csv`:

| Column | Holds |
| --- | --- |
| `logged_at` | when the row was written, UTC |
| `who` | a handle the person chooses (letters, digits, `-`, at most 20 characters) |
| `flow`, `day` | the flow's CLI name and the release day, New York |
| `instrument` | a market one of the flow's links names |
| `direction` | `up` or `down` |

`fortuneteller guess <flow> <instrument> up|down --who <handle> --day <YYYY-MM-DD>` appends one
row. It refuses:
- a flow that `live` does not call;
- a market that is not one of the flow's links;
- a day already past, or today at or after 08:30 New York;
- a second guess by the same handle on the same flow, day and market.

## The rule, fixed before any guess is graded

- **Witness:** as for the machine's calls, GitHub's time. A guess counts only if it is on `main`
  through a pull request opened before 08:30 New York on the release day. Otherwise it is **void**:
  listed, not graded. The person opens that pull request; `score` checks `logged_at`, and the
  results check the pull request's time by hand, as rung 4 did.
- **Right or wrong** as in rung 2: the day's move on that market closed strictly the called way.
  Pending until the close is loaded.
- **The machine's call beside it,** for the same flow, day and market: right, wrong, or no call
  (*too few*, silent or small all show as "no call").
- **The record is counts,** never a probability: per person, right out of graded; and head to head,
  on the guesses where the machine also called, how often each was right. No verdict, no p value.
- **The asymmetry is shown, not fixed.** The person calls before the release; the machine calls
  after it, knowing the actual. The page says so.

**Expected outcome, written first.** A person is right about half the time; the machine calls on
only a few links a release; so head-to-head rows stay few for months. The step delivers the game,
not a finding.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `guess` and the log; `score` grades guesses beside the machine's calls | Tests: a guess after 08:30 on its day is refused; a second guess on the same market is refused; a guess on a market outside the flow's links is refused; planted rows are graded right, wrong and pending, with the machine's call beside each |
| 2 | The scoreboard shows each person's record and the head-to-head | On a test database the JSON's counts equal `score`'s lines; the page shows a guess beside the machine's call and states the asymmetry |
| 3 | The first live round, the jobs report on 2026-11-06 or the next release `live` calls; results here | At least one guess merged through a pull request opened before 08:30, graded by the evening score |

## What this step does not do

No accounts, no web form, no betting or stakes, no probability for a person, no change to the
machine's calls or rules, no leaderboard across people beyond counts.

## Technical details

- **The log:** `settings.guesses_path` (`data/guesses.csv`), read and written with `csv`, like
  `calls_path`. `study.read_guesses` and `study.append_guesses` mirror `read_calls` and
  `append_calls`.
- **The command:** `guess` in `__main__.py`. A flow's links and whether `live` calls it come from
  the same place `predict` reads them.
- **Grading:** `study.score_guesses` reuses rung 2's right-or-wrong on `observations`; `score`
  prints a "guesses" block after the calls. Since the evening job commits `score`'s output, the
  guesses reach the score pull request with no change to the job.
- **The page:** `scoreboard` adds a `guesses` list to `data.json`, and `index.html` renders one more
  table.
- **Docs:** `docs/glossary.md` (guess), `docs/schema.md` if a table is touched (none is planned),
  `docs/precision.md` (the pull request time checked by hand), `docs/status.md`.
