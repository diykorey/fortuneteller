# MVP step 1 — Releases

> Step 1 of the four in the [Roadmap](roadmap.md); this document follows the step template in the
> [Legend](legend.md). Unfamiliar acronym or term? See the [Glossary](glossary.md).

## The goal

**In plain words:** make a list of every day the US inflation number came out, and what that number
was.

Once a month the US government publishes CPI, the headline inflation figure, and markets often jump
that day. This step collects the whole history of those announcements — about 650, one a month
since 1972 — from FRED, the Federal Reserve's free statistics site, and saves them into one database
table, `event_instances`: the project's calendar of events that might move markets. When it runs
it prints one line, e.g. `loaded 648 CPI releases, 1972-08-22 … 2026-08-12` — 648 announcements
saved, first to latest. It is done when that table holds real history instead of made-up examples.

The whole project asks whether markets react to these announcements predictably. Before any
reaction can be measured, you need to know exactly *which days* to look at; this step builds that
list, and the next steps look up what prices did on those days. The one thing to get right is the
date: each figure is labelled by the month it measures, but published about six weeks later, and
the market reacts on the publication day.

In full: `event_instances` holds every US CPI release as a dated fact: **the day the number was actually
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
| 1 | ~~Get a free FRED API key; put it in `.env`~~ **done** | `settings.fred_api_key` resolves it |
| 2 | ~~Fetch the CPI initial-release history in one request~~ **done** | The response parses into dated records |
| 3 | Map each record to an `EventInstance` | Release timestamp, actual, and a stable id per row |
| 4 | Write them with `insert_models(replace=True)` | Re-running changes no row count |
| 5 | Print the count and the date range | `loaded N CPI releases, <first> … <last>` |

## How you know it is right

Not "it ran without error" — the failure mode is plausible-looking wrong data. Three checks:

- **Spot-check a stored date against the BLS release schedule.** Any date landing on the 1st of a
  month means the reference-month trap was not avoided.
- **Re-run the command.** The row count must not change. If it doubles, the id is not stable.
- **Read the first and last dates.** Expect the first to be `1972-07` by reference month, published
  1972-08-22, and the last to be the latest monthly print. The count grows by one a month: on
  2026-09-25 it was 649 rows after the valueless one was dropped, the last published 2026-09-11.

## What this step does not do

No prices, no returns, no surprise, no consensus, no second event type, no scheduling, no fetching
on a timer. `consensus`, `surprise` and `surprise_sd` stay `NULL` — step 4 fills them, or says why
it cannot.

## Technical details

**Source.** FRED `fred/series/observations`, series `CPIAUCSL` (headline CPI, seasonally adjusted),
with `output_type=4` — the initial-release view — over the full real-time range
(`realtime_start=1776-07-04&realtime_end=9999-12-31`). Each row carries `date` (reference month),
`value` (as first published) and `realtime_start` (publication date).

**Verified against the live API on 2026-09-11.** It returns **649 observations**, reference months
`1972-07` to `2026-07`, with publication dates genuinely distinct from reference months — real-time
coverage reaches back to 1972, not the 1997 floor that applies to many FRED series. Median lag from
reference month to publication is 46 days. No fallback to `fred/release/dates` is needed. The count
grows by one a month: on 2026-09-25 it was 650, through `2026-08` published 2026-09-11.

**Column mapping.**

| Column | Value |
| --- | --- |
| `event_id` | **Reference month** as `YYYYMM` — deterministic, unique, one row per print |
| `event_type` | `CPI / inflation surprise` — the exact key from `event_types.csv` |
| `event_ts` | Release date at 08:30 America/New_York, stored UTC |
| `country` | `United States` — the exact spelling from `countries.csv` |
| `detail` | The reference month |
| `scheduled` | `true` |
| `actual` | The index level as first published |
| `quality` | A literal marking these as first-release values |
| everything else | `NULL` |

**Why `event_id` comes from the reference month, not the release date.** Two reasons, the second
found by checking rather than assuming:

- A counter would break idempotency — `insert_models(replace=True)` only overwrites if the key is
  stable across runs, so a counter appends a duplicate set every time.
- **Release dates are not unique.** October and November 2025 CPI were *both* first published on
  2025-12-18, when the release schedule slipped. Keying on the release date would have collided on
  the primary key and silently dropped a print. Reference months are unique across all 649 rows.

**Data quirks, all verified present.** The history is not uniform, and each of these is a real row:

| Row | Quirk | Handling |
| --- | --- | --- |
| `2025-10` | Value is `"."` — published with no number | Skip rows whose value is `"."`; count and report them |
| `2025-10`, `2025-11` | Share release date 2025-12-18 | Distinct `event_id` by reference month; see below |
| `1995-12` | Published 1996-02-01, a 62-day lag | Accept — a genuine schedule slip, not corrupt data |
| `1992-11` | Published Sunday 1992-12-13 | Accept, but do not assume release dates are weekdays |

Where two prints share a release date they also share an `event_ts`. Steps 3 and 4 must therefore
count a **trading day** once, not once per event row, or that day's move is double-weighted. Today
this is moot — the `2025-10` row is dropped for having no value — but it is a property of the data,
not a coincidence to rely on.

**Timezone is computed, not hardcoded.** CPI drops at 08:30 ET, which is 12:30 or 13:30 UTC
depending on daylight saving. `zoneinfo` handles it; a fixed offset would be wrong half the year.

**Where the code goes.** A new file `src/fortuneteller/study.py` — the event study that steps 2–4
also grow into. A new *file*, not a package: no `__init__.py`, per rule 1. `db.insert_models`
already accepts `event_instances`, and `EventInstance` already exists in `models.py`, so no schema
or model change is needed.

**No new dependency.** Stdlib `urllib.request`. One HTTP call does not justify a library.

**The key is a `SecretStr`.** `settings.fred_api_key` masks itself in reprs and tracebacks; read it
with `.get_secret_value()` only where the request is built, and never interpolate it into a message.
FRED echoes the full request URL in its error bodies, so redact the key before printing any failure.

**Tests.** Parse and mapping tested against a small saved FRED response — including the
reference-month-vs-release-date distinction, since that is the bug worth a regression test. The
network call itself stays out of the gate: CI runs on every push and has no API key.

**CLI.** `uv run fortuneteller load-releases`.
