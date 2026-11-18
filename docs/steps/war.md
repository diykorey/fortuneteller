# What follows a violent act that sets off a crisis

> Step 26 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the third of phase 5,
> *war and military strikes*. Terms are in the [Glossary](../glossary.md): *kind*, *span*, *base
> rate*, the four answers, *ICB*, *violent act*, *lesser release*, *hole*.

## The goal

**In plain words:** when a strike, a border clash, an invasion or a bombing set off an
international crisis, what did each market do over the next day, week and month?

At the end, `fortuneteller follows --event war` prints [step 17's](what-follows.md) table for
these acts, over the day, the week and the month, as [OPEC's](opec.md) does, and a trigger file may
name `war`. The next war or strike in the news can then be filed as a trigger and answered from its
past.

## The way to reach it

- **The days come from a list nobody here picks.** The International Crisis Behavior project's
  data, version 16 (Brecher, Wilkenfeld, Beardsley, James and Quinn 2025,
  [sites.duke.edu/icbdata](https://sites.duke.edu/icbdata/data-collections/), read 2026-11-18):
  511 international crises, 1918 to 2021. The system-level file (`icb1v16.csv`) dates each crisis
  by its trigger (`yrtrig`, `motrig`, `datrig`): the day its earliest actor perceived it. The
  actor-level file (`icb2v16.csv`) codes what that trigger was (`triggr`).
- **The obstacle: a crisis often begins with words, not shots.** A trigger may be a threat, a
  coup or a troop movement weeks before any fighting (Crimea-Donbass, 2014-02-22, is the ouster in
  Kyiv). A trigger filed live is the day of the violence. So only crises whose trigger is a
  **violent act** are taken: the earliest actor's `triggr` is 9, "violent act" (a border clash, a
  border crossing, an invasion of air space, a sinking, a bombardment, a full-scale invasion). The
  kind is that act, known the day it happens; nothing about how the crisis went later is used.
  - Since 1970 (the stored markets' first closes, the S&P 500's 1970-01-02): 139 such crises. Two
    have no day: `datrig` is 88 and 66, not a date (the codebook keeps only the year and month
    when the day cannot be determined):
    Cameroon/Nigeria III (1993-12) and the Korean land mine (2015-08). They are left out: 137
    crises, 1970-11-22 to 2021-04-28. Two fall on 1981-04-28 (Al-Biqa missiles I, Contras I) and
    are one event: **136 events**, one kind, *violent act*.
- **The day and the hour.** The source gives a date, no hour, in the place where the act happened;
  46 of the 136 days are a Saturday or a Sunday. The hour is a rule: **04:00 UTC**. That is before
  every stock market's close that day, Tokyo's 15:00 or 15:30 (06:00 or 06:30 UTC) included, and
  after the currencies' 00:00 London close, so they react the next day. A weekend act reacts on
  Monday. **Known misses, written now:** an act after a market's close that day is read a day
  early on that market. 2001-09-11 reacts on the S&P 500 at 2001-09-17, after five closes
  missing, a *hole* on US markets: left out there, as step 17 leaves it out.
- **Lesser, as OPEC's:** each day stays an ordinary day for every other flow, so no other flow's
  base or row changes; `raw-move --event war` keeps the flow's own lone days. `follows` keeps
  every event, a day shared with another flow included; the results name the other flow.
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES` (28 since
  step 25), and both runs: from the close before and, with `--after-the-day`, from the reaction
  close.
- **How many each market can answer.** Events after each market's first stored close (the store
  of 2026-11-17):

  | Events | Markets |
  | --- | --- |
  | 135 or 136 | S&P 500, Nasdaq, both yields, Nikkei, dollar index |
  | 40 to 83 | FTSE 100 (83), DAX (60), VIX (54), yen (42), utilities, energy stocks (40) |
  | 27 to 37 | gold and coffee (37), breakeven (32), euro, pound, STOXX 600 (31), defence stocks (ITA) and homebuilders (29), Euro Stoxx 50 (28), Brent, natural gas and gasoline (27) |
  | 20 to 25 | corn (25), wheat and soybeans (21), bitcoin (20) |

## The rule, fixed before anything is shown

- The source, the selection, the hour and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: 30 graded walk-forward needs 40 events. Only the first two rows of
    the table above have them; gold, oil, defence stocks and the rest are *too few* walk-forward.
    The month's no-overlap rule may take markets at 40 to 42 below it too.
  - The header: `follows: 136 violent acts 1970-11-22 … 2021-04-28: 136 violent acts`.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Oil (Brent), gold and defence stocks (ITA) on the day, the week and the month: *can't say*,
    in both runs. Most of these acts are far from oil fields and from the markets' home countries.
  - Every other flow's `follows` and `raw-move` rows unchanged byte for byte. The lines that count
    every cell change by the added cells alone: each `follows` chance line and the scoreboard's
    chance and grids, each written before and after. (`raw-move` prints no chance line.)

*Written 2026-11-18, before any `follows` or `raw-move` ran on these acts; the counts above are
from the source and the store's first closes, and are arithmetic.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed `data/seed/war.csv` (`day,time,kind,crisis`) from ICB's two files, by `scripts/icb_violent_acts.py`; the flow stored | The seed test checks the header, 137 rows, days in order, time `04:00`, kind `violent act`. On a copy of the store, the flow stores 136 events; every existing scoreboard entry identical, and its chance before and after written here; the five rows below checked |
| 2 | `follows --event war`; `war` in `TRIGGER_KINDS` | Tests: a Saturday act reacts on Monday; a weekday act on Tokyo's close the same day and the euro's the next; a `war` trigger for a day not stored is answered from an event made at 04:00 UTC that day. On a copy of the store the header is the expected one, and every other flow's `follows` and `raw-move` output byte for byte the one before, OPEC's included |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet of the expected outcome marked right or wrong with its numbers; each cell with 30 or more graded walk-forward and its record; the days shared with another flow, by the act's UTC day |

## How you know it is right

- **The rows match the source:** five named now, checked by hand against ICB's online crisis
  summaries (the project's *Crisis Summaries*, on the same page): 1970-11-22 Conakry raid,
  1990-08-02 Gulf War (Iraq into Kuwait), 2001-09-11 Afghanistan/US, 2001-12-13 India parliament
  attack, 2020-09-27 second Nagorno-Karabakh war. Each a violent act on that day.
- **The hour is UTC, not New York's:** a weekday act's stored `event_ts` is 04:00 that day, and
  it reacts on the Nikkei the same day (a wrong zone would push it to the next).
- **The reaction days:** a Saturday act reacts on Monday's close; 2001-09-11 on the S&P 500's
  2001-09-17, counted as a hole.
- **Nothing else changes:** every other flow's output byte for byte on a copy of the store holding
  OPEC's announcements.

## What this step does not do

No act after the list's last, 2021-04-28: not Russia's invasion of Ukraine (2022-02-24), not
2023-10-07, not the strikes on Iran in 2025. They join with ICB's next version, by a dated
amendment; adding them by hand would be picking. No crisis set off by words, a coup or a troop
movement; no terror attack, civil war or strike ICB does not list as a crisis's trigger; no
severity, no hour from the news. Not on the page's [*ask*](ask-the-fortune-teller.md). No live
link.

## Technical details

- **Seed:** `data/seed/war.csv`, columns `day` (the trigger date), `time` (`04:00`), `kind`
  (`violent act`) and `crisis` (ICB's `crisname`), 137 rows, written once by
  `scripts/icb_violent_acts.py` from the two downloaded files, which are not committed. Documented
  in `docs/legacy/data/README.md`.
- **Flow:** a `DatedShockFlow` in `flows.py`: event type `Geopolitical escalation / terror`
  (already in `data/seed/event_types.csv`), country `World`, zone UTC, type code 30, `war`, detail
  the kind; `lesser`, unscheduled. Kinds by `study.detail_kinds`, as OPEC's. `FOLLOWS_NOUNS`
  gains `violent acts`; `TRIGGER_KINDS` gains `war` with `violent act`; a live trigger's event is
  made as OPEC's is, at 04:00 UTC.
- **Tests** in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`.
- **Docs:** this spec; `docs/schema.md` (code 30, the detail, the event type); the glossary (*ICB*,
  *violent act*); roadmap row 26 and a decisions entry for the narrower kind; status, changelog.
