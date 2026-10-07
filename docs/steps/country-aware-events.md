# Country-aware events

> A refactor before the [jobs-report forecast](nfp-forecast.md)'s step 2; part 1 of two. Part 2,
> cross-country effects, is on the [Roadmap](../roadmap.md#next-steps-in-order). Follows the step
> template in the [Legend](../legend.md); builds on [event flows](event-flows.md).

## The goal

**In plain words:** let a second country's events be added without mixing them up with the US's,
and prepare for measuring how one country's event moves other countries' markets.

Everything today is US-only, but the code tells events apart by **event type** alone. The seed
taxonomy has one `CPI / inflation surprise` type, with the country in its own column. So UK CPI
added as a flow would be read back with US CPI, averaged into the US's 12-month trend, and paired
in the same reports.

At the end: an event flow is identified by its event type **and origin country**; everything that
reads events, actuals, trends and surprises goes through that pair; release dates and day-only
times use the flow's own time zone; and each market's close carries its own time zone. Every US
number prints exactly as today.

## The model this prepares for

Two things differ by country, and they live in different places:

- **The surprise belongs to the event, in its origin country.** US CPI coming in 0.2 pp hot is one
  surprise, whoever reacts to it. It stays one row per event × measure × source in `surprises`.
- **Its power differs by affected market.** How much the Bund, the gilt or the yen move per unit of
  US surprise is the event's *effect* on each market, measured per (event type, origin country) ×
  market. That is part 2: non-US markets with their country, moves and surprises in standard units
  so powers compare across markets, and the `effect_size_matrix` filled, keyed by origin country.

A US event can also shift another country's own expectations (say, of the ECB). Here that shows as
that country's markets moving; a derived second event belongs to the later aftershock layer.

## The way to reach it

**Identity.** `EventFlow` gains `country` (a `countries.country`, e.g. `United States`) and `zone`
(its release time zone). A flow is the pair (event type, country): `stored_events` filters on both,
and `EVENT_FLOWS` is checked at import for unique pairs, type codes and command-line names.

**Grouping.** `Trend12m` averages a measure's past values within one flow, not across every flow
that names the measure `core`. `surprise_pairs` and `track_surprises` read one flow's surprises,
joined through `event_instances`, not every row with that measure and source.

**Time zones.** `release_date` uses the event's flow's zone; `end_of_day` takes the source's zone;
each market's close is a local time in its exchange's zone, so a Frankfurt close and a New York
event compare correctly across the weeks when Europe and the US change clocks on different dates.

**Clean baseline: unchanged for now.** Ordinary days exclude every stored event's reaction day, in
any country. Whether a market's baseline should drop only events measured against it is decided in
part 2, when there is a second country to decide it with.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~Flow identity: `country` and `zone` on `EventFlow`; `stored_events(flow)` by event type and country; `EVENT_FLOWS` checked for duplicates; `release_date` in the flow's zone~~ **done** | A UK flow of the same event type, in a test, stores and reads back apart from the US's |
| 2 | ~~Surprises per flow: `Trend12m` grouped by flow; `surprise_pairs` / `track_surprises` per flow; `end_of_day(day, zone)`; each market's close in its own zone~~ **done** | The same test's UK trend and report leave the US's untouched; every US output byte-identical to `main` |

## How you know it is right

- **No mixing.** A test registers a made-up UK CPI flow beside US CPI, with the same event type and
  measure names, and checks that events, trends, surprises and reports stay apart.
- **No change for the US.** Every load and report, and `surprises` row for row, identical to
  `main`'s on real data.
- **Duplicates refused.** Two flows with the same (event type, country), type code or command-line
  name fail at import.

## What this step does not do

No non-US data, markets or events. No effects table, no standard units, no per-country report:
part 2. No change to the clean baseline.

## Technical details

`flows.py`: `EventFlow.country`, `EventFlow.zone`, `stored_events`, `release_date`, the
duplicate check. `expectations.py`: `Trend12m`'s grouping, `end_of_day`. `study.py`:
`PriceSeries.zone`, `first_reaction_day`, `surprise_pairs`, `track_surprises`. The recipe in
[Extending](../extending.md) gains `country` and `zone`.

## Results

Done 2026-10-07. Every event flow is now identified by (event type, origin country):

- Stored events, the 12-month trend and the `surprise` report all read one flow at a time. A made-up
  UK housing flow, with the same event type and measure as a US one, ten times the numbers and
  moving markets the other way, leaves the US trend, surprises and report byte-identical; the UK's
  trend is its own (`tests/test_event_flows.py`).
- Release dates, day-only expectations (`end_of_day`) and each market's close are read in their own
  time zones. A Fed decision at 14:00 New York reacts the next day in a London market closing at
  16:30 London time.
- Two flows sharing a (type, country) pair, type code or command-line name fail at import.
- On real data, every load and report, and `event_instances`, `observations`, `surprises` and
  `daily_bars` row for row, are identical to `main`'s before this work.

Part 2, [cross-country effects](../roadmap.md#next-steps-in-order), builds on this.
