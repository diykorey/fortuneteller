# MVP step 1 — Releases

> Step 1 of the four in the [Roadmap](roadmap.md); this document follows the step template in the
> [Legend](legend.md). Unfamiliar acronym or term? See the [Glossary](glossary.md).

## The goal

`event_instances` holds every US CPI release as a dated fact: **the day the number was actually
published, and the number that was actually printed that day.**

That is the entire deliverable. Nothing derived, nothing predicted, nothing scored.

It matters because every later step joins to this table. Step 2 attaches price moves to these
timestamps, step 3 compares those days against ordinary days, step 4 relates the move to the
surprise. **If the dates here are wrong, steps 2–4 still run and still print numbers — they are just
measuring the wrong days.** The expensive failure in this step is a silent wrong answer, not a
crash.

## The way to reach it

The obstacle: the obvious source gives the wrong date.

A CPI series is indexed by its **reference month** — the month whose prices were measured. August
2026 CPI is dated `2026-08-01`. But it was *published* around 11 September 2026, and that is the day
the market moved. Join prices to `2026-08-01` and you measure the first of every month: noise shaped
like data.

So: **ask FRED for the initial release, not the series.** FRED retains the publication history of
each series — which value was known on which day — and can return, per reference month, the value as
first published alongside the date it was first published. One view, both dates, no reconstruction.

Keep the reference month as well. Step 4 needs consecutive months to turn index levels into the
change that consensus is actually quoted for.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Get a free FRED API key; put it in `.env` | `FT_FRED_API_KEY` resolves through `settings` |
| 2 | Fetch the CPI initial-release history in one request | The response parses into dated records |
| 3 | Map each record to an `EventInstance` | Release timestamp, actual, and a stable id per row |
| 4 | Write them with `insert_models(replace=True)` | Re-running changes no row count |
| 5 | Print the count and the date range | `loaded N CPI releases, <first> … <last>` |

## How you know it is right

Not "it ran without error" — the failure mode is plausible-looking wrong data. Three checks:

- **Spot-check a stored date against the BLS release schedule.** Any date landing on the 1st of a
  month means the reference-month trap was not avoided.
- **Re-run the command.** The row count must not change. If it doubles, the id is not stable.
- **Read the first and last dates.** They should bracket real history, not end at today.

## What this step does not do

No prices, no returns, no surprise, no consensus, no second event type, no scheduling, no fetching
on a timer. `consensus`, `surprise` and `surprise_sd` stay `NULL` — step 4 fills them, or says why
it cannot.

## Technical details

**Source.** FRED `fred/series/observations`, series `CPIAUCSL` (headline CPI, seasonally adjusted),
with `output_type=4` — the initial-release view — over the full real-time range. Each row carries
`date` (reference month), `value` (as first published) and `realtime_start` (publication date).
Verify this against the live API before building on it; if `output_type=4` does not behave as
documented, fall back to `fred/release/dates` for the CPI release id, cross-checked by listing
`fred/releases` rather than hardcoding a guess.

**Column mapping.**

| Column | Value |
| --- | --- |
| `event_id` | Release date as `YYYYMMDD` — deterministic, readable, one release per day |
| `event_type` | `CPI / inflation surprise` — the exact key from `event_types.csv` |
| `event_ts` | Release date at 08:30 America/New_York, stored UTC |
| `country` | `United States` — the exact spelling from `countries.csv` |
| `detail` | The reference month |
| `scheduled` | `true` |
| `actual` | The index level as first published |
| `quality` | A literal marking these as first-release values |
| everything else | `NULL` |

**Why `event_id` is derived, not counted.** `insert_models(replace=True)` is only idempotent if the
key is stable across runs. A counter would append a duplicate set every time.

**Timezone is computed, not hardcoded.** CPI drops at 08:30 ET, which is 12:30 or 13:30 UTC
depending on daylight saving. `zoneinfo` handles it; a fixed offset would be wrong half the year.

**Where the code goes.** A new file `src/fortuneteller/study.py` — the event study that steps 2–4
also grow into. A new *file*, not a package: no `__init__.py`, per rule 1. `db.insert_models`
already accepts `event_instances`, and `EventInstance` already exists in `models.py`, so no schema
or model change is needed.

**No new dependency.** Stdlib `urllib.request`. One HTTP call does not justify a library.

**Tests.** Parse and mapping tested against a small saved FRED response — including the
reference-month-vs-release-date distinction, since that is the bug worth a regression test. The
network call itself stays out of the gate: CI runs on every push and has no API key.

**CLI.** `uv run fortuneteller load-releases`.
