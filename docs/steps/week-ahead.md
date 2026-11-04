# The week ahead

> Step 15 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-04 while the owner
> was away, toward the goal they restated on 2026-11-03: a prediction tool ordinary people can read.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** before each release in the coming week, the scoreboard says what the fortune
teller will say once the number lands, and how often it has been right. For example, from the
replay of 2026-11-03: "Friday 08:30 New York, the jobs report. Forecasters expect +63k. If above
+113k: the 10-year yield up, right 65 of 100 before. If below +13k: down."

Today the page shows only what already happened: calls, grades and verdicts. A reader cannot see
what is coming, or what a call will hinge on. The [Legend](../legend.md)'s 2026-10-23 amendment
counts a preview before a scheduled event as a fortune. This step gives one to every release `live`
calls.

At the end: the page opens with *The week ahead*.

## The way to reach it

- **Not a call.** A call is made from the number once it lands, never before it. The preview
  states the rule the call will follow, the condition first in each row. Above the table, one
  line: "Entertainment, not financial advice. Nothing is called until the number lands; this is
  the rule it will follow."
- **Only what `live` calls.** A flow `called_live` has a consensus the morning job reads, so its
  threshold is a number a reader can compare with the release. Its next release comes from
  `expectations.next_consensus`, asked from the day after the page is written, so a release that
  landed that morning is never listed. The window is the next seven days, New York time.
- **The threshold is the rule's own.** It is the consensus (Nasdaq's, else TradingView's) plus or
  minus the rule's `noticeable`. A smaller surprise is *silent*, and the page says so.
- **The outcome `live` would log.** For a flow whose rule is `alone`, a release on a day another
  release shares (`expectations.other_releases`, as `live` reads it) is *silent* on every link, and
  the row names the other release.
- **Each signed link, as the replay would call it.** The replay is `study.confident_links` against
  the rule's `predicted_from`, Nasdaq's consensus for every flow `live` calls, with a next
  surprise of +`noticeable`. Whether a link calls depends only on the releases before, not on the
  sign, so the direction below is the opposite of the one above. A link not open on the releases
  before is *silent*.
- **Every record shown, the weak ones marked.** Each link, silent or not, shows its record from
  `study.grade` on the replay's calls before the next release: right of predictions, its verdict,
  and how often its expected direction alone was right (`always_right`), so a drift does not read
  as skill. A *too few* record reads "8 of 9 so far, too few to judge (needs 30)", and a *doesn't
  hold* one says so, both in lighter text after the direction. `live` still calls those links, so
  hiding them would hide what it will do. The rule for *holds* is printed under the table.
- **The page says when it was written.** The evening job rewrites the page only on a day `score`
  changes. That is at least every Thursday, when claims are called. So the section shows the
  evening it was written, and the page drops a release whose day has passed.
- **A calendar that cannot be read does not stop the page.** `scoreboard` prints the error, the
  section says the calendar could not be read, and the rest of the page is written as today.
- **Nothing is measured, so nothing is graded.** No bar moves, no verdict changes, and the calls
  log is not touched.

## The rule, fixed before anything is shown

- The flows, thresholds, links and records are the ones `live` and the replay already use. Nothing
  is chosen for this page.
- **Expected outcome, written first.** Written on the evening of 2026-11-04, the page lists:
  - initial jobless claims on Thursday 2026-11-05, every link silent;
  - the jobs report on Friday 2026-11-06, with the 10-year and 5-year yields, the dollar and the
    euro each calling, each *holds*, as the 2026-11-03 replay gives them (65 of 100, 71 of 101, 55
    of 81, 56 of 81);
  - CPI on Tuesday 2026-11-10 with TradingView's 0.2 (Nasdaq lists none yet), the dollar, the DAX,
    the euro and the 5-year yield calling, each *too few*.
- Every existing key of `data.json`, `score` and `missed` stay identical.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scoreboard` writes `ahead` into `data.json`; the page shows *The week ahead* first | The tests below pass; on a copy of the store every other key of `data.json` is identical, and the section matches the expected outcome or the difference is explained here |

*Step 1, 2026-11-04:* on a copy of the store, written the morning of 2026-11-04, the section is
the expected outcome exactly: claims on 2026-11-05 with every link silent; the jobs report on
2026-11-06 at Nasdaq's +63k, thresholds +13k and +113k, the four links calling, each *holds* (the
10-year 65 of 100 against 61 for "up" alone, the 5-year 71 of 101 against 57, the dollar 55 of 81
against 38, the euro 56 of 81 against 45); CPI on 2026-11-10 at TradingView's 0.2, the dollar 8 of
9, the DAX 5 of 13, the euro 2 of 3 and the 5-year 6 of 8 calling, each *too few*. Every other key
of `data.json` is unchanged. *Amended 2026-11-04:* each release also says whose consensus it
shows (`consensus_from`). One known difference from `live`, left as it is: when
Nasdaq's and TradingView's consensus are further apart than `live` accepts, `live` logs nothing on
the morning and exits 1, while the preview has shown the directions the evening before.

## How you know it is right

- A release one and seven days ahead is listed; one landing the day the page is written, or eight
  days ahead, is not; a flow not `called_live` is never listed.
- The threshold is the consensus plus or minus `noticeable`, Nasdaq's consensus first and
  TradingView's where Nasdaq has none.
- An open link shows opposite directions above and below, and its record with `always_right`. A
  closed link is *silent* with its record. A *too few* record is marked.
- A release of an `alone` flow sharing its day is *silent* on every link, naming the other.
- For the same surprise, each link's direction matches the one `live` logs.
- A `CalendarError` leaves `ahead` as `null`, the page saying so, with exit code 0.
- The page drops a release whose day has passed and shows when it was written.

## What this step does not do

No call before the release, and no change to the calls log or to `live`. No preview for a flow
`live` does not call, such as the Fed's, the ECB's or the statements'. Their reaction record is a
later step. No new data source, and no delivery beyond the page.

## Technical details

- `__main__.week_ahead(con, today, cache_dir) -> list[dict[str, object]]` returns one dict per
  release, oldest first:
  - `day`, `time` (`flows.RELEASE_TIME`, New York), `event` (the flow's `cli_name`), `label`,
    `measure`, `consensus`, `below`, `above`, `step` (the rule's, as `50k`);
  - `shared`: the releases sharing its day, empty unless the flow is `alone`;
  - `links`: by market, each `{"above": ..., "below": ..., "right", "predictions",
    "always_right", "verdict"}`. The directions are `up`, `down` or `null` when silent; the record
    is `study.grade([c.call for c in calls[:-1]], sign)`, as the scoreboard's walk-forward entry
    grades.
- `_scoreboard` calls `week_ahead`, catches `sources.CalendarError`, prints `scoreboard: <error>`
  to stderr, and passes the list, or `None`, to `scoreboard_data`'s new keyword `ahead=None`. So
  existing tests stay off the network.
- `scoreboard.html`: the section first, the notice line, "written <date>", one row per release
  (day and time, the event, the consensus, "If above …" and "If below …"), and under each, its
  links: the market, the direction above, the record.
- **Docs:** `docs/steps/scoreboard.md` gets a line on `ahead`; `docs/status.md` and the roadmap's
  row are updated.
