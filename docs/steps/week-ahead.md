# The week ahead

> Step 15 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-04 while the owner
> was away, toward the goal they restated on 2026-11-03: a prediction tool ordinary people can read.
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** the scoreboard says, before each release in the coming week, what the
fortune teller will say once the number lands, and how often it has been right. For example: "Friday
08:30 New York, the jobs report. Forecasters expect +63k. Above +113k, the fortune teller says the
10-year yield rises (right 65 of 100 times before); below +13k, that it falls."

Today the page shows only what already happened: calls, grades and verdicts. A reader cannot see
what is coming, or what the calls will hinge on. The [Legend](../legend.md)'s 2026-10-23 amendment
counts a preview before a scheduled event as a fortune. This step gives one to every release `live`
calls.

At the end: the evening job's page opens with *The week ahead*.

## The way to reach it

- **Not a call.** A call is made from the number once it lands, never before it. The preview
  states the rule the call will follow: the threshold and the direction on each side. The page
  says this in one line above the table.
- **Only what `live` calls.** A flow `called_live` has a consensus the morning job reads, so the
  threshold is a number a reader can compare with the release. Its next release comes from
  `expectations.next_consensus`, as `live` finds it. A release counts when it falls within seven
  days of the evening the page is written, New York time.
- **The threshold is the rule's own.** It is the consensus (Nasdaq's, else TradingView's) plus or
  minus the rule's `noticeable`, as `walk_forward` uses it. A smaller surprise is *silent*, and the
  page says so.
- **Each signed link, as the replay would call it.** The replay is `study.confident_links` with a
  next surprise of +`noticeable`, then −`noticeable`. A link that makes no call for the next
  release, because it is not open on the releases before, is listed as *silent*. A link that calls
  shows its direction and its replay record: right and predictions, and its verdict.
- **A calendar that cannot be read does not stop the page.** The section says the calendar could
  not be read, `scoreboard` prints the error, and the rest of the page is written as today.
- **Nothing is measured, so nothing is graded.** No bar moves, no verdict changes, and the calls
  log is not touched.

## The rule, fixed before anything is shown

- The flows, the threshold and the links are the ones `live` and the replay already use. Nothing
  is chosen for this page.
- **Expected outcome, written first.** Written on the evening of 2026-11-04, the page lists:
  - initial jobless claims on Thursday 2026-11-05, with every link silent;
  - the jobs report on Friday 2026-11-06, with the 10-year and 5-year yields, the dollar and the
    euro each calling, each with a record of *holds*.

  CPI on 2026-11-10 is outside the seven days.
- Every existing entry, `score` and `missed` stay identical.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `scoreboard` writes `ahead` into `data.json`; the page shows *The week ahead* first | The tests below pass; on a copy of the store, every other key of `data.json` is identical, and the section matches the expected outcome |

## How you know it is right

- A release six days ahead is listed; one eight days ahead is not; a flow not `called_live` is
  never listed.
- The threshold is the consensus plus or minus `noticeable`, taking Nasdaq's consensus first and
  TradingView's where Nasdaq has none.
- An open link shows its direction on each side and its record. A closed link is *silent*.
- A `CalendarError` leaves `ahead` as `null`, the page saying so, and the exit code 0.

## What this step does not do

No call before the release, and no change to the calls log or to `live`. No preview for a flow
`live` does not call, such as the Fed's, the ECB's or the statements'. Their reaction record is a
later step. No new data source, and no delivery beyond the page.

## Technical details

- `__main__.week_ahead(con, today, cache_dir) -> list[dict[str, object]]` returns one dict per
  release:
  - `day`, `event`, `label`, `measure`, `consensus`, `below`, `above`, `unit`;
  - `links`, keyed by market, each with `up` and `down`: the direction called for a surprise
    above or below, or `null` when silent;
  - `right`, `predictions` and `verdict`.
- `scoreboard_data` gets `ahead`, the dicts, or `null` on a `CalendarError`. The release's time
  comes from `flows.RELEASE_TIME`.
- `scoreboard.html` adds the section, its one-line notice and the table, first on the page.
- **Docs:** `docs/steps/scoreboard.md` gets a line on the new key, and `docs/status.md` and the
  roadmap's row are updated.
