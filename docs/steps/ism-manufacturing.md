# The US manufacturing survey (ISM)

> Step 4b of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-23, after
> [euro-area inflation](euro-inflation.md) found New York moving on flash days for a reason it
> could not test. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** does the ISM manufacturing survey move markets, does the move follow its
surprise, and is it why the S&P 500 and VIX move on euro-area flash days?

The ISM's index (a **PMI**) comes out at 10:00 New York on the month's first working day, the day
the euro-area flash often lands. Part 3 found the S&P 500 and VIX moving on flash days, still on
the 79 days with no other stored release, and named ISM as the likely cause, untested. Measured
2026-10-23: 17 of those 79 days are ISM days (25 of all 142), so ISM can explain part of that move,
not all; part 3's "often" is corrected in step 2.

At the end: ISM releases loaded as an event flow with their surprise, run through rung 1 and step
4 for all seven markets, and the flash-day check repeated without ISM days.

## The events

- **Source:** TradingView's US calendar, the row `ISM Manufacturing PMI`, from the quarters
  already fetched for the consensus check. Checked 2026-10-23: 162 releases, 2013-04-01 to
  2026-09-01, every one with an actual and a forecast.
- **Not Nasdaq's consensus,** unlike the other US flows: Nasdaq lists ISM back to 2008 (seen in
  cached 2008 days), but a day per request on days not yet known, and a measure in
  `CONSENSUS_ROWS` is asked for by `live`, which runs before 10:00. So ISM has no second calendar
  to check its forecast or its actual against, as the flash has none; the 60 releases before 2013
  wait.
- **Time:** the calendar's own, 10:00 New York (one row, 2015-08-03, says 10:30), before every
  close, Frankfurt's 17:30 included, so all seven markets react the same day.
- **Origin:** `United States`, a new seed event type `Manufacturing survey`.
- **Measure:** the index itself, `ism_pmi`, in index points. Its actual is TradingView's: there is
  no free first print to check it against (FRED does not carry ISM), and the survey is not revised
  but for seasonal factors.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** ratio ≥ 1.10 and p < 0.01 for every market.
- **The surprise: actual minus TradingView's forecast**, the flash's baseline. Noticeable from 1.0
  point, about two thirds of a typical miss as known from outside this project, as in
  [more events](step-4-more-events.md); not measured here. No 12-month trend.
- **Expected signs for a stronger survey:** growth news, so the jobs report's: the yield and the
  dollar index up; the S&P 500, gold, VIX, the DAX and the Euro Stoxx 50 none.
- **Shared days left out** of its surprise table, as for every flow since step 4.
- **Ordinary days lose ISM days** for every market; each changed verdict of another flow is
  reported, and so are the releases other flows now leave out as shared.
- **No live calls.** ISM lands 90 minutes after the release-day job's 08:30 run, so `live` skips
  it, as it skips the flash; `predict` grades its links walk-forward like the others.
- **The flash-day check, repeated:** part 3's S&P 500 and VIX ratios on flash days with no other
  stored release, now that ISM days are stored; the same test, the same bar.
- **Expected outcome, written down first:** ISM moves the S&P 500, the yield and VIX; the yield
  and the dollar index follow its surprise; on flash days without ISM the S&P 500 and VIX still
  move more than on ordinary days, short of the bar as before.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The ISM flow: events and actuals from TradingView, the forecast as its expectation, the rule above~~ **done**; `load-releases` stored 163 releases, 2013-04-01 to 2026-10-01, and `load-surprises` 163 surprises; HICP's and every US flow's stored rows identical. Other flows' outputs moved by the rule: shared releases left out, retail 48 (was 47), core PCE 67 (55), HICP 81 (64); three verdicts, reported in step 2 | A test's calendar quarter stores a release at its New York time with its surprise; `raw-move` and `surprise --event ism` print seven verdicts; `live` unchanged; HICP's stored rows identical through the shared flow (143 events, 124 core and 143 headline surprises), though its verdicts may move by shared days |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | Seven verdicts on both tests, the flash-day check, other flows' verdicts before and after, against the expected outcome |

## Results

Measured 2026-10-23 (`raw-move`, `surprise` and `predict --event ism`): 163 releases, 2013-04 to
2026-10.

| Market | Does it move? ratio, p | Does it follow the surprise? rank corr, p, hit rate |
| --- | --- | --- |
| S&P 500 | 1.19, 0.045, unclear | 0.16, 0.10, doesn't |
| 10-year yield | 1.47, 0.0006, **moves** | 0.33, 0.0002, 67%, **tracks** |
| Dollar index | 1.26, 0.017, unclear | 0.26, 0.003, 67%, **tracks** |
| Gold | 1.23, 0.031, unclear | 0.41, 0.0001, unclear (no expected sign) |
| VIX | 1.14, 0.09, unclear | 0.15, 0.12, doesn't |
| DAX | 1.37, 0.001, **moves** | 0.10, 0.31, doesn't |
| Euro Stoxx 50 | 1.28, 0.014, unclear | 0.08, 0.43, doesn't |

The surprise test runs on 110 releases: 53 share their day with another stored release and are
left out. A point of surprise moves the yield 1.3 bp and the dollar index 0.08%; gold falls 0.25%
(no expected sign, so unclear).

**ISM is growth news the bond market reads.** The yield moves 47% more on ISM days and follows the
surprise as closely as it follows the jobs report's; so does the dollar. Every market moves more on
ISM days than on ordinary ones, the DAX by 37% (Frankfurt is open at 10:00 New York).

**Walk-forward, no call.** The yield's link opens in 2014-09 and is right on 31 of 49 (63%, p 0.04),
short of *holds*; the dollar's opens in 2019-12, 7 of 11, too few. ISM would get no call even if
`live` ran after 10:00.

**The flash-day check, repeated.** On flash days with no other stored release, now 62 (17 of the
79 were ISM days), the S&P 500's ratio falls from 1.40 to 1.25 (p 0.09) and VIX's stays 1.25
(p 0.07): ISM explains part of New York's flash-day move, not all; the rest is unexplained, short of
the bar as before.

**Other flows** (*with ISM days out of ordinary days and shared days grown*). Left out as shared:
retail sales 48 (was 47), core PCE 67 (55), the flash 81 (64). Three verdicts changed: CPI's S&P 500
on release days, *doesn't* to unclear (ratio crossing 1.10, p 0.04); GDP's gold on release days,
*doesn't* to unclear (1.10, p 0.22); the flash's Euro Stoxx 50 against the surprise, *doesn't* to
unclear (0.16, p 0.14, 61% on 53). Every call is unchanged; retail sales' yield still holds.

**Against what was written down first.** *Moves the S&P 500, the yield and VIX:* right on the yield;
the S&P 500 and VIX are unclear, and the DAX moves. *The yield and the dollar index follow its
surprise:* right, both track. *Flash days without ISM still move more, short of the bar:* right.

## Technical details

ISM is the second flow read from TradingView alone, after the flash, so the two share one: the
flash's `HicpFlow` and `parse_euro_flashes` become a TradingView flow and parser taking the country,
the rows and the zone; HICP and ISM are two instances. `TradingViewForecast` covers every measure
such a flow stores, with each flow's own zone. Type code 9, cli `ism`. `docs/schema.md` gets the
measure and the event type.

## What this does not do

No ISM before 2013, no services survey, no sub-indices (prices paid, new orders, employment), no
live ISM calls.
