# What follows a war or serious clashes

> Step 26 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the third of phase 5.
> Terms are in the [Glossary](../glossary.md): *kind*, *span*, *base rate*, the four answers,
> *ICB*, *lesser release*.

## The goal

**In plain words:** when an international crisis broke out that went on to full-scale war or to
serious clashes, what did each market do over the next day, week and month?

At the end, `fortuneteller follows --event war` prints [step 17's](what-follows.md) table for
these crises, by kind, over the day, the week and the month, as [OPEC's](opec.md) does, and a
trigger file may name `war`.

## The way to reach it

- **The days come from a list nobody here picks.** The International Crisis Behavior project's
  system-level data, version 16 (`icb1v16.csv`, Brecher, Wilkenfeld, Beardsley, James and Quinn
  2025, [sites.duke.edu/icbdata](https://sites.duke.edu/icbdata/data-collections/), read
  2026-11-18): 511 international crises from 1918 to 2021, each with its trigger's date
  (`yrtrig`, `motrig`, `datrig`), the day the crisis began for its first actor.
- **The kind is the crisis's violence, as ICB codes it** (`viol`): 4, full-scale war, is *war*;
  3, serious clashes, is *clashes*. Crises with minor clashes (2) or none (1) are not taken.
  Since 1970: 49 *war*, 70 *clashes*. Two have no trigger day (`datrig` 77 and 88: the
  Afghanistan invasion of 1979 and Cameroon/Nigeria III of 1993) and are left out, so 117 rows,
  1970-03-13 to 2021-04-28: 49 *war*, 68 *clashes*. No two share a day.
  - The kind is known only after the crisis has run its course. A trigger filed live names the
    kind by the filer's judgement, as a CEO scandal's is.
- **The day and the hour.** The source gives a date, no hour, in the place where the crisis began;
  40 of the 117 fall on a weekend. The hour is a rule: **04:00 UTC**. That is before every stock
  market's close that day, Tokyo's included in both of its eras, and after the currencies' 00:00
  London close, so they react the next day. A weekend trigger reacts on Monday. **Known misses,
  written now:** a trigger after a market's close that day is read a day early on that market. A
  trigger on a day markets were shut reacts at their reopening: 2001-09-11 (*war*, Afghanistan/US)
  on the S&P 500's 2001-09-17.
- **Lesser, as OPEC's:** each day stays an ordinary day for every other flow, so no other flow's
  base or row changes. The table keeps every crisis, a day shared with another flow included; the
  results name the other flow.
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES`, and both runs:
  from the close before and, with `--after-the-day`, from the reaction close.
- **The obstacle: the markets that matter most start late.** Oil (Brent) is stored from
  2007-07-30, gold from 2000-08-30, defence stocks (ITA) from 2006-05-05. After those days the
  list holds 11, 14 and 12 *war* and 9, 10 and 10 *clashes*. So they can answer on all history
  only where 10 or more are counted, and never walk-forward. That is the result's boundary,
  written now, not a reason to widen the list by hand.

## The rule, fixed before anything is shown

- The source, the kind, the hour and step 17's bars, unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: 30 graded walk-forward needs 40 events of a kind on a market.
    *War* has them only on the S&P 500, the Nasdaq, both yields, the Nikkei and the dollar index
    (47 to 49); *clashes* on the same six (67 or 68). Everywhere else it is *too few*
    walk-forward. Brent's 9 *clashes* are *too few* on all history too.
  - The header: `follows: 117 wars and clashes 1970-03-13 … 2021-04-28: 49 war, 68 clashes`.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Oil and gold on the day after a *war*: *can't say*, in both runs. Most of the list is wars far
    from oil fields and from the markets' home countries.
  - Every existing row of every output unchanged byte for byte; only the lines that count every
    cell (the chance lines and the scoreboard's grids) change, by the added cells alone, each
    written before and after.

*Written 2026-11-18, before any `follows` or `raw-move` ran on these crises; the counts above are
from the source and the store's first closes, and are arithmetic.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed `data/seed/war.csv` (`day,time,kind,crisis`) from `icb1v16.csv`; the flow stored | The seed test checks the header, 117 rows, days in order and unique, time `04:00`, kind *war* or *clashes*, 49 and 68. On a copy of the store, the flow stores 117 events; every existing scoreboard entry identical, and its chance before and after written here |
| 2 | `follows --event war`; `war` in `TRIGGER_KINDS` with its two kinds | Tests: an event's kind comes from the seed; a Saturday trigger reacts on Monday; a `war` trigger for a day not stored is answered from a crisis made at 04:00 UTC with the filed kind. On a copy of the store the header is the expected one, and every other flow's `follows` and `raw-move` byte for byte the ones before |
| 3 | Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet of the expected outcome marked right or wrong with its numbers; each kind's walk-forward records with 30 or more graded; the days shared with another flow |

## How you know it is right

- **The rows match the source:** five checked by hand against ICB's crisis summaries: 1990-08-02
  *war* (Gulf War, Iraq into Kuwait), 2001-09-11 *war* (Afghanistan/US), 2014-02-22 *war*
  (Crimea-Donbass), 2020-09-27 *war* (second Nagorno-Karabakh war), and one *clashes* row of the
  2010s, named in step 1.
- **The reaction days:** a test finds a Saturday trigger on Monday's close, and 2001-09-11 on the
  S&P 500's 2001-09-17.
- **Nothing else changes:** every existing row byte for byte on a copy of the store, OPEC's
  included, the copy holding OPEC's announcements.

## What this step does not do

No crisis after the list's last, 2021-04-28: not Russia's invasion of Ukraine (2022-02-24), not
2023-10-07, not the strikes on Iran in 2025. They join with ICB's next version, by a dated
amendment; adding them by hand would be picking. No terror attacks, coups or civil wars outside
ICB's list, no minor clashes, no severity beyond the two kinds, no hour from the news. Not on the
page's *ask*. No live link.

## Technical details

- **Seed:** `data/seed/war.csv`, columns `day` (the trigger date), `time` (`04:00`), `kind`
  (`war`, `clashes`) and `crisis` (ICB's `crisname`), written once by `scripts/icb_wars.py` from
  the downloaded `icb1v16.csv`, which is not committed. Documented in `docs/legacy/data/README.md`.
- **Flow:** a `DatedShockFlow` in `flows.py`: event type `Major interstate war`, country `World`,
  zone UTC, type code 30, `war`, detail the kind; `lesser`, unscheduled. Kinds by
  `study.detail_kinds`, as OPEC's. `FOLLOWS_NOUNS` gains `wars and clashes`; `TRIGGER_KINDS`
  gains `war` with `war` and `clashes`; a live trigger's crisis is made as OPEC's is, at 04:00 UTC.
- **Tests** in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`.
- **Docs:** this spec; `docs/schema.md` (code 30, the detail); the glossary (*ICB*, *war*,
  *clashes*); status, changelog, roadmap row 26.
