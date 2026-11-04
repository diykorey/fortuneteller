# What follows from the next close

> Step 18, part 1, of the [Roadmap](../roadmap.md#next-steps-in-order), taken 2026-11-04 during
> the owner's "proceed with the project for the next 18 hours". Row 18 is amended with this spec.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** step 17 measured what followed each kind of event from the close *before* the
market reacted. A reader who hears the news has already missed that close. This part measures what
followed from the close *of* the reaction day: the next day, the next week and the next month.

Step 18 answers a trigger, an event the owner writes into a file once it has happened. The file is
dated by the merge of the pull request that adds it, and the merge comes after the event. Step 17's
spans start before the event, so a trigger merged after it would be graded on a move that had
partly happened. The owner could see that move and add only the triggers that look right. So the
spans a trigger answers start at the reaction close, and on each market the trigger counts only if
merged before that market's reaction close (part 2). Part 1 measures those spans and replays them
walk-forward, before any trigger exists.

At the end: `fortuneteller follows --event <flow> --after-the-day` prints step 17's table for the
spans that start at the reaction close, for the Fed, the jobs report, retail sales and CPI.

## The way to reach it

- **The same method, one close later.** Everything is part 1's and part 1b's: the kinds (part 1d's
  headline for CPI), spans of 1, 5 and 21 closes, the non-overlap rule, the base and its cut, the
  answer, the walk-forward and its bars, the chance lines, the release rule. One thing changes: a
  decision's span is keyed on the close after its reaction close on that market, so it runs from
  the reaction close to the 1st, 5th or 21st close after it.
- **Shifted by closes, not by days.** The key is the next close in the market's own closes, so a
  Friday's next day is the Monday. With *r* the reaction close's index and *i* = *r* + 1:
  - if *i* + *c* is past the market's closes, the event has no span yet and is neither left out
    nor a hole, as an event after the last close is now;
  - if the span keyed on close *i* has a hole, the event is a hole;
  - an event whose reaction close itself has a hole before it is a hole as now, even if the span
    after the day is clean, so the same events are counted with and without the flag;
  - an event whose span starts on the end close of the last one kept is kept, as now.
- **The placebo stays clear of every event.** The shift is the span's length plus one, or 10 if
  that is more (22 for the month), so the placebo before ends at the close before the reaction
  close and never holds the reaction move. A placebo keyed on any event's reaction close, or on any
  event's close after it, is skipped, so it never lands on an event's own span. Without the flag
  both rules are part 1's.
- **What this gives up.** After a jobs report above the consensus, the yields rise on the day and
  hold (part 1b). That move is over when the reaction close is in, and `live` already calls it on
  the morning of each report. A trigger is answered only for what comes after.
- **The answer a trigger will get.** The walk-forward answer at an event uses only the events whose
  span ended on or before its reaction close, and the base spans that ended by then. Part 2 gives a
  trigger that answer once the reaction close is stored, so it shows and grades the quantity this
  part replays. The graded move starts at that close, so nothing in it is seen.
- **Close times are already there.** Each market's close time and zone are in `MVP_PRICE_SERIES`,
  which `first_reaction_day` reads.

## What part 2 must do, fixed now

Part 2 (the file and the log) has its own spec. For it to grade what this part replays, it must:
- void a trigger per market when it was merged at or after that market's reaction close, read as
  the close's time in its zone (`series.close`), not its date. After a 14:00 New York Fed decision
  a trigger can be late for the S&P 500 and in time for gold and the DAX, which react next day;
- take the event's time and kind from the store, not the file: a trigger names the flow and the
  day, and is matched to the stored event, so the headline rounding, the threshold and the Fed's
  target rate decide the kind as here; a kind written in the file that disagrees voids it, with
  the reason;
- leave out, as here, a trigger whose span starts before the end of the last event's span kept;
- list every stored event of the flow since the first trigger that has no trigger in time, since
  the owner chooses which events to file after seeing the reaction day. Part 2's spec weighs the
  simpler design too: grade every stored scheduled event after a start date, with no file, and
  keep the file for the flows with no calendar.

## The rule, fixed before anything is shown

- Part 1's bars, the kinds and the release rule, none of them changed by what the run shows.
- **Expected outcome, written first.** An answer is a cell answering *up*, *about the same* or
  *down*.
  - Nothing holds walk-forward, on any of the four flows. A move after the reaction day is drift,
    and markets this liquid leave little of it.
  - On all history, each flow's answers are at most its chance line plus 3.
  - After a jobs report above the consensus, neither yield answers on the day after or over the
    week after; part 1b's week answers were the day's move not undone.
  - Each month cell counts within 2 of its step 17 count; the shift is one close. Its spans still
    hold the next release's reaction, as in part 1b.
- **If nothing holds,** part 2 is still built: a trigger is then answered *can't say* on most spans,
  shown and counted, as the [Legend](../legend.md#the-target) says. Stopping here would leave step
  20 with nothing to read into.
- Every existing output is unchanged byte for byte, including `follows` without the flag.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`follows --after-the-day`~~ **done** 2026-11-04 (PR #251) | The tests below pass. On a copy of the store, each of the four flows prints 144 cells with the flag, and its first line ends `, spans from the reaction close`. Without the flag, each flow's output equals the one before the change: the diff is empty |
| 2 | Write the results here and in [MVP results](../mvp-results.md), check the expected outcome, and update the roadmap row | Each flow's answers, release marks and walk-forward records are recorded against the expected outcome |

*Step 1, 2026-11-04 (PR #251):* on a copy of the store each flow prints 144 cells with the flag and
the header as written; without it, the four tables are byte for byte the ones before the change.

## How you know it is right

- On made-up closes with 12 or more events, where every reaction day rises 3% and the day after
  falls 3%, `follows` answers *up* on the day and the flag answers *down*. A key not shifted fails.
- An event whose reaction close is the market's last close has no span with the flag and is not
  counted as a hole.
- Events 10 closes apart, each day after rising 3%, other days flat: the flag answers *up* on the
  day and is not marked *the period*. A placebo allowed onto another event's day after would read
  *up* too and mark it.
- With the flag, no month placebo span holds a reaction close. A shift of 21 fails.
- `answer_before` with the shifted keys: changing every close after the last event's reaction
  close leaves its answer and base unchanged; changing the reaction close changes the base.
- The existing `follows` tests pass unchanged.

## What this part does not do

- No trigger file and no log: part 2.
- No new flow, market or span.
- Nothing is stored.
- Events are not independent; the chance says more than it should, as in step 17.

## Technical details

- **`study.py`:** `follow_market(decisions, closes, unit, c, order=KINDS, after=False)` and
  `follow_decisions(flow, kinds, order, con=None, after=False)`. With `after`, the key is the close
  after the reaction close, as above; `reacted` holds the reaction closes and those keys; the
  placebo shift is `max(PLACEBO_SHIFT, c + after)`. A bool, not an offset: one shift is the only
  case. Without it every line is as now.
- **`__main__.py`:** `follows` gains `--after-the-day` (dest `after_the_day`);
  `describe_follows(events, kinds, cells, order, noun, after=False)` ends the first line with
  `, spans from the reaction close`.
- **Tests:** in `tests/test_what_follows.py`.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 18 (amended: split into
  part 1, this, and part 2, the file and the log; "step 17's figures" are its method on spans from
  the reaction close; part 2's duties above), and `docs/status.md`.
