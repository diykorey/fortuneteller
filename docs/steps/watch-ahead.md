# The week ahead, without a call

> Step 16 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen by the owner 2026-11-04 after
> [step 15](week-ahead.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the week ahead also lists the scheduled events the fortune teller does not
call, and says how markets moved on such days before. For example: "Tuesday 2026-11-17 05:00 New
York, Germany's ZEW survey. No call. On its days before, no market moved more than on ordinary
days." Or, for an ECB decision, on the store of 2026-11-04: "No call. On its days before, the
euro moved 1.68 times as much as on an ordinary day, the dollar index 1.49 times."

Step 15 previews only the releases `live` calls, six US releases. The calendar holds more that a
reader can watch: the Fed's and the ECB's decisions, the Fed chair's and the ECB president's
statements, and the euro-area, ISM and German releases. For each, the scoreboard already holds a
measured record of whether its days move each market ([the raw move](step-3-raw-move.md)). The
[Legend](../legend.md)'s 2026-10-23 amendment counts that record as a fortune: "a measured reaction
to a kind of event, never advice".

At the end: *The week ahead* has a second table, *Also on the calendar*.

## The way to reach it

- **No direction, ever.** These flows give no call. The row says "No call" and shows only the
  markets whose verdict on the event's days is *moves*, each with its ratio to an ordinary day, as
  the `live` statements' preview does (`_previews`). When no market moves, it says so.
- **Which flows.** Every flow with a scheduled date ahead on TradingView's calendar, other than the
  ones `live` calls:
  - the Fed's decisions, the calendar's "Fed Interest Rate Decision";
  - the ECB's decisions, its "ECB Interest Rate Decision";
  - each `StatementFlow`'s speeches and testimonies, by the holder in office that day, as
    `StatementFlow.ahead` reads them;
  - each `TradingViewFlow` that is not `called_live`, by its rows' titles: the euro-area flash,
    ISM, ZEW, Ifo and the German flash CPI.

  The dated shocks are left out: their seed files hold only events that have happened.
- **The same window as step 15:** from the day after the page is written to seven days after,
  New York time, from this calendar quarter's reply and the next one's. A flow with two dates in
  the window lists both.
- **The record is the page's own.** The row names its flow, and the page reads that flow's
  `raw_move` cells from `events`, so the preview and the table below it cannot differ. For a lesser
  flow, the record is its lone days, as the table says.
- **A calendar that cannot be read** leaves both tables out, as in step 15.

## The rule, fixed before anything is shown

- Nothing is measured, chosen or graded: the flows, dates and verdicts already exist.
- **Expected outcome, written first.** On the morning of 2026-11-04 the calendar lists none of
  these from 2026-11-05 to 2026-11-11. So the table says nothing is scheduled that week. The next
  ones are ZEW on 2026-11-17 and Ifo on 2026-11-24.
- Every existing key of `data.json`, `ahead` included, `score` and `missed` stay identical.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scoreboard` writes `watch` into `data.json`; the page shows *Also on the calendar* under step 15's table | The tests below pass; on a copy of the store every other key is identical and the table matches the expected outcome |

## How you know it is right

- A Fed decision, an ECB decision, a statement by the holder in office, and a ZEW release inside
  the window are listed; one outside it, or a statement by someone out of office, is not.
- A flow `live` calls is never in `watch`, even when its row is on the calendar.
- The page shows a listed flow's *moves* markets with their ratios, or says that none moves.
- A `CalendarError` leaves `watch` as `null`, with exit code 0.

## What this step does not do

No direction, no call, and no surprise preview for the flows with a surprise rule that `live` does
not call (ISM's yields track its surprise, but nothing calls it before it lands). No dated shocks
and no new data source.

## Technical details

- `sources.calendar_rows(payload) -> list[tuple[datetime, str, str]]`: each row's time in UTC, its
  title and its country, wrapping `_tradingview_rows` with the same malformed-reply error.
- `__main__.week_watch(today, cache_dir) -> list[dict[str, object]]`, one dict per scheduled
  event, oldest first: `day`, `time` (New York), `event` (the flow's `cli_name`), `label`, and
  `title` (the calendar's).
- `_scoreboard` calls it beside `week_ahead`, in the same `try`, and passes `watch` to
  `scoreboard_data`'s new keyword `watch=None`.
- `scoreboard.html`: the table under step 15's, one row per event: the day and time, the event and
  its title, then "No call" and the record from `events`.
- **Docs:** `docs/steps/scoreboard.md` (the `watch` key), `docs/status.md`, the roadmap's row.
