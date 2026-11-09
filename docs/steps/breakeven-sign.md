# The breakeven's sign

> Step 19, part 2d, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [the signs](signs.md). Taken 2026-11-09 on the owner's "merge proceed". Row 19 is amended with
> this spec. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the breakeven is the market's own guess at inflation, so hotter inflation news
should push it up. This part writes that down and tests it like every other signed market. FRED
publishes its close a day late, so the evening learns to grade the other markets on time and the
breakeven when its close arrives.

At the end, `surprise` and `predict` give `T5YIE` real verdicts on CPI and core PCE, a link that
holds is called by the morning job, and a call on it no longer holds up any other market's grade.

## The way to reach it

- **A sign comes from a reason.** The breakeven *is* expected inflation, so a hotter inflation print
  should raise it: **+1 on CPI and core PCE, 0 on every other rule.** On growth news stronger demand
  and a tighter Fed pull opposite ways, as for homebuilders. On the Fed's statement it must not copy
  the 10-year's sign: a hawkish statement lifts yields and should lower expected inflation. `live`
  does not call that statement, so 0 loses nothing.
- **The result came first here, and the sign does not rest on it.** [The breakeven](breakeven.md)
  has already shown `follows` holding after a CPI above consensus. The sign is the series'
  definition and stands whatever `predict` finds. `surprise` and `predict` are not run signed on it
  until this spec is merged.
- **`follows` is not `predict`.** The 23 of 30 is by kind, from the day, against the consensus.
  `predict` uses the signed surprise, the verdict's baseline and its own walk-forward. A hold in one
  promises nothing in the other.
- **Waiting is not pending.** A logged row on a series published a day late, a `fred:` ticker, whose
  move is not loaded yet goes in a new `waiting` list, printed as `waiting: <n>`. The evening job
  greps only `^pending: `, so it goes on to the triggers and the scoreboard, and every other market
  is graded that evening. A missing release, surprise or Yahoo close stays `pending:` and still
  stops the job. The rule is about the source, so no market is named.
- **How long it waits.** Until FRED has the close, with no limit. It costs nothing while it waits:
  the row is listed in `data/score.txt`, and blocks nothing. CPI on 2026-11-10 followed by Veterans
  Day, a bond holiday, would wait two evenings. When the close lands `score` changes, so the next
  evening opens its own pull request.

## The rule, fixed before anything is measured

- **Same tests, same bars:** step 4's *tracks* and rung 2's *holds*. A link that holds is called; no
  market gets a call by hand.
- **Every other cell unchanged,** by [the signs](signs.md)' procedure, with `T5YIE`'s lines dropped.
- **The merge waits.** The build merges only after CPI's evening run of 2026-11-10, whatever it
  finds: that release is the first full test of the morning and evening jobs, and this changes the
  evening. So the first breakeven call can come no earlier than the following CPI.
- **Expected outcome, written first:**
  - `surprise`: `T5YIE` at most *unclear* on CPI against the verdict's baseline, *doesn't* on core
    PCE, whose noticeable surprises are few.
  - `predict`: neither link *holds*, so no new call. The 30 graded of 2b sit exactly at the bar, and
    the test differs.
  - The rebuild stays under the 15-minute bar (268 s at the signs).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The two signs, `waiting`, and a table of each link: opens, record, what `live` would log at its next release | The tests below pass, the procedure gives an empty diff, the job's check below is here. Merged after CPI's evening run of 2026-11-10 |
| 2 | Results here and in [MVP results](../mvp-results.md) | Each link's verdicts against the expected outcome |

## How you know it is right

- A row on `T5YIE` with no move is in `waiting`, not `pending`, and `score` prints no `pending:`.
- A Yahoo market's row with no move is still `pending`.
- With the move loaded the same row is graded.
- A test pins `T5YIE`: +1 in `EXPECTED_SIGN`, 0 in every other rule.
- **The job, end to end,** on a scratch worktree and a copy of the store, with a logged `T5YIE` call
  and its close held back: `release-day.sh score` exits 0, grades the others, lists the row as
  waiting and runs the triggers and the scoreboard. With its pull request merged and the close
  loaded, a second run grades the row and opens a new pull request. An open `score-*` pull request
  makes the second evening wait, as it does today.

## What this part does not do

- No limit on the wait and no void for a close that never comes. No change to the rule that a call
  or score pull request waits for a person.
- No sign on the farm and fuel funds or coffee. No new market, flow or bar.

## Technical details

- **`flows.py`:** `EXPECTED_SIGN = with_more_outcomes({...}) | {"ITB": -1, "T5YIE": 1}`, its comment
  saying why only there; `PCE_SURPRISE_RULE` follows.
- **`study.py`:** `LiveScore.waiting`; in `score_calls`, a row with no move goes to `waiting` if
  `MVP_PRICE_SERIES[r.instrument]` has a `fred:` ticker.
- **`__main__.py`:** `score` prints `waiting` beside `void` and `pending`; `_grade` returns
  `"pending"` for a waiting row, with its note, so the scoreboard and the guesses show it as they
  show any ungraded row.
- **Tests:** `test_event_flows.py`'s signs test and its comment, and the tests that count links.
- **Docs:** this spec, row 19, `docs/status.md`, the `pending` sentence of
  [the evening score](evening-score.md), [Precision](../precision.md)'s breakeven row, the glossary
  (*Waiting*).
