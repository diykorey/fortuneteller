# Rung 5 — the live path

> Rung 5 of the [Roadmap](../roadmap.md#after-the-mvp--the-feature-ladder)'s feature ladder, and its
> step template. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when a release lands, read its number from the calendar instead of typing it.

[Rung 4](rung-4-keep-score.md) logs a call only if someone types the actual between 08:30 New York
and the earliest close, and a typo voids the row. Every release with no one at the keyboard is
missed for good.

At the end: `predict --fetch` waits from 08:30 for the release's actual on TradingView's calendar
and makes the same call `--actual` would.

## Why now, and why not yet

The roadmap says a manual step must first be worth automating. What the manual step costs is
known: someone at the keyboard at 08:30 New York on every release day, the pull request before
gold's close, and a void row for every typo. What is not known is whether the calendar is fast
enough to help, so step 1 is a measurement, made on the first live releases by hand. No rung 5 code
is merged before the first live release has been logged by hand.

## The source

**TradingView's calendar**, already read for the consensus and for shared days: one source for all
six measures. Its actual for every stored release since 2014 matches FRED's first print on 804 of
806 (2026-10-13); the two that differ are core PCE 2014-08-01 (a shared day) and GDP 2014-07-30
(unreadable). That shows TradingView keeps the first print, not a revision; it does not show what
it shows at 08:31 on the day. Step 1 measures that.

## The rule, fixed before anything is fetched live

- **The fetched actual is the typed one's stand-in**, graded by `score` exactly the same way: void
  unless it matches FRED's first print. `score` stays the guard; no second calendar is asked.
- **It waits, and gives up.** From 08:30 New York, the row is read every 15 seconds; with no actual
  by 30 minutes past, `predict` stops and says so, and the release can still be typed with
  `--actual`.
- **It says where the number came from**: "actual X from TradingView at HH:MM:SS New York".
- **Before 08:30, or on another day**, `--fetch` refuses: there is nothing to fetch.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Measure on the first live releases: how long after 08:30 TradingView's actual appears, and whether it equals the one typed | Both recorded here for at least one release |
| 2 | `predict --fetch` | Tests: an actual appearing after two empty reads is called and logged with its source line; none in 30 minutes stops with the reason; before 08:30 it refuses |
| 3 | Results: the first release logged with `--fetch` | Its rows merged after a pull request opened before its close, and graded by `score` |

## Open question for after step 1

Opening the release day's pull request without anyone there: a scheduled job that runs
`predict --fetch`, commits the rows and opens the pull request. It pushes from this machine
unattended, which is the user's decision, not this rung's default; it is decided once step 1 shows
the fetch is fast enough to be worth it.

## What this does not do

No delivery to anyone (rung 6), no second source for the actual, no change to how calls are made
or graded.
