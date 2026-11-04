# The week ahead, without a call

> Step 16 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen by the owner 2026-11-04 after
> [step 15](week-ahead.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the week ahead also lists the scheduled events the fortune teller does not
call, and says how markets moved on such days before. For example, an ECB decision on the store of
2026-11-04: "No call. On its 116 days, 3 of 16 markets moved more than on an ordinary day: the
euro 1.68 times, the dollar index 1.49 times, the FTSE 100 1.37 times."

Step 15 previews only the releases `live` calls, six US releases. The calendar holds more that a
reader can watch: the Fed's and the ECB's decisions, the Fed chair's and the ECB president's
statements, and the euro-area, ISM and German releases. For each, the scoreboard already holds a
measured record of whether its days move each market ([the raw move](step-3-raw-move.md)). The
[Legend](../legend.md)'s 2026-10-23 amendment counts that record as a fortune: "a measured reaction
to a kind of event, never advice".

At the end: *The week ahead* has a second table, *Also on the calendar*.

## The way to reach it

- **No direction, ever.** Above the table, step 15's notice, then: "No call: no direction is given
  for these events. The ratio is the typical size of the day's move, either way, against an
  ordinary day's."
- **The record with its denominator.** Each row says on how many days its record rests and how
  many of the markets tested moved more than on an ordinary day, then names those markets with
  their ratios: "On its 116 days, 3 of 16 markets moved more than on an ordinary day: …", or "0 of
  16". An *unclear* market is never named; a *too few* market is not counted. A flow whose markets
  are all *too few* reads "too few days to judge"; a flow not in `events` reads "no record yet".
  The days are the most any market has, as `_previews` counts them; a lesser flow reads "on its 32
  days alone". Under the table goes the raw move's chance line, from `data.chance.raw_move`.
- **The record is the page's own.** The row names its flow, and the page reads that flow's
  `raw_move` cells from `events`, so the preview and the table below it cannot differ.
- **Which flows, and where each is read.** Each flow below gets
  `scheduled(cache_dir, start, end) -> list[tuple[datetime, str]]`: its scheduled times (UTC) and
  titles from TradingView's calendar, from this quarter's reply and the next one's, by the
  constants that exist:
  - `FedFlow`: the US calendar's `expectations.FED_DECISION_ROW`;
  - `EcbFlow`: the EU calendar's `sources.ECB_DECISION`;
  - `StatementFlow`: its own calendar's `parse_statements(payload, prefix)`, a statement counting
    when the holder in office that day (in the flow's zone) is in its title;
  - `TradingViewFlow`, for the flows not `called_live` (the euro-area flash, ISM, ZEW, Ifo and the
    German flash CPI): each measure's `TRADINGVIEW_ROWS` country and title, matched as
    `parse_tradingview_releases` matches them.

  A row ahead has no actual, and the existing parsers drop such rows, so `scheduled` reads them
  itself. `StatementFlow.ahead`, the `live` preview, is rewritten on `scheduled`, so the two cannot
  disagree. The dated shocks are left out: their seed files hold only events that have happened.
- **One event per flow per day,** the earliest, as each flow's `events` counts them. The euro-area
  flash's core and headline rows are one entry, titled by the first. The window is step 15's: from
  the day after the page is written to seven days after, New York time.
- **Its own calendar error.** `week_watch` also reads the EU and DE calendars, so it gets its own
  `try`. A `CalendarError` leaves `watch` `null`, the table reading "The calendar could not be read
  on <written>.", while `ahead` is unchanged.

## The rule, fixed before anything is shown

- Nothing is measured, chosen or graded: the flows, dates and verdicts already exist.
- **Expected outcome, written first.**
  - Against the live calendar on 2026-11-04, nothing is listed from 2026-11-05 to 2026-11-11, and
    the table reads "Nothing else is scheduled in the week from 2026-11-04." This can be checked
    only that day, since the current quarter's reply is not cached.
  - On a copy of the store, with the page written as on 2026-11-12, ZEW is listed on 2026-11-17 at
    05:00 New York, with its record of 113 days: "0 of 16".
- Every existing key of `data.json`, `ahead` included, `score` and `missed` stay identical.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scheduled` on the four flow types; `scoreboard` writes `watch`; the page shows *Also on the calendar* under step 15's table | The tests below pass; both expected outcomes hold; the page is checked in a browser on the copy |

## How you know it is right

- A Fed decision, an ECB decision, a statement by the holder in office, and a ZEW release inside
  the window are listed, each from a row with no actual. One outside it, or a statement by someone
  out of office, is not.
- A window crossing into the next quarter reads that quarter's reply.
- The euro-area flash's two rows are one entry, and a second statement the same day is not listed.
- A flow `live` calls is never in `watch`.
- `StatementFlow.ahead` gives what it gave before.
- A `CalendarError` on the DE calendar leaves `watch` `null` and `ahead` as it was, exit code 0.

## What this step does not do

No direction, no call, and no surprise preview for the flows with a surprise rule that `live` does
not call (ISM's yields track its surprise, but nothing calls it before it lands). No dated shocks
and no new data source.

## Technical details

- `scheduled` on `FedFlow`, `EcbFlow`, `StatementFlow` and `TradingViewFlow`, as above.
- `__main__.week_watch(today, cache_dir) -> list[dict[str, object]]`, one dict per event, oldest
  first: `day`, `time` (`%H:%M` New York), `event` (the flow's `cli_name`), `label`, `title` and
  `lesser`.
- `_scoreboard` calls it in its own `try` and passes `watch` to `scoreboard_data`'s new keyword
  `watch=None`.
- `scoreboard.html`: the table under step 15's, with the day and time, the event and its title, then
  the record as above; the chance line goes under it.
- **Docs:** `docs/steps/scoreboard.md` (the `watch` key), `docs/status.md`, the roadmap's row.
