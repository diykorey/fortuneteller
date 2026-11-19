# What follows a crypto hack

> Step 27 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), the fourth of phase
> 5, *crypto shocks*. Terms are in the [Glossary](../glossary.md): *kind*, *span*, *base rate*,
> the four answers, *DefiLlama*, *hack*, *lesser release*.

## The goal

**In plain words:** when $100 million or more was stolen from a crypto exchange, a protocol or a
wallet, what did bitcoin, ether, Coinbase's shares and every other market do over the next day,
week and month?

At the end, `fortuneteller follows --event crypto` prints [step 17's](what-follows.md) table for
these hacks, as [OPEC's](opec.md) does, and a trigger file may name `crypto`, so the next big
hack in the news can be answered from its past.

## The way to reach it

- **The days come from a list nobody here picks.** DefiLlama's hacks list
  ([api.llama.fi/hacks](https://api.llama.fi/hacks), free, no key, read 2026-11-18): 1,362 hacks
  from 2011-06-19 to 2026-11-17, each with its day (`date`, 00:00 UTC), the amount taken in
  dollars at the time (`amount`), its target and technique. The list is kept up as hacks happen.
- **The kind: a hack of $100 million or more**, by the list's `amount`, one kind, *hack*. A live
  trigger is filed when the first reports put the theft at $100 million or more; the list's
  `amount` is settled later, so a hack first reported smaller and later counted bigger joins the
  past but would have been missed live: a known miss, written now. 44 rows,
  2014-02-07 to 2026-10-29, no two on one day, 12 on a weekend: exchanges (14), protocols (24),
  wallets, a chain and others (6). Funds later returned (4 rows) do not change the kind: the
  return came later.
- **The markets: two added.** Ether (`ETH-USD`, Yahoo, from 2017-11-09; *ETH*), with bitcoin's
  close, the UTC day's last price, weekend bars dropped as every market's are
  ([Glossary](../glossary.md), *BTC*); and Coinbase's shares (`COIN`, from its listing on 2021-04-14), the
  Nasdaq's close, 16:00 New York. Both **unsigned**, as step 25's three: no live link. Hacks
  after each market's first close ([Schema](../schema.md), *How much data*): bitcoin (from
  2014-09-17) 43, Mt. Gox falling before; ether 42; Coinbase 37; each of the other 28 markets,
  all stored before 2014, 44.
- **The hour.** The list gives the day at 00:00 UTC. The hour is a rule, as [war's](war.md):
  **04:00 UTC**, before every stock market's and the crypto markets' close that day, after the
  currencies' 00:00 London close. A weekend hack (12 of the 44) reacts on Monday on every market,
  bitcoin and ether included, since no market keeps a weekend close: a known miss for the two
  coins, which trade then. **Known misses, written now:** a hack found after a market's close is
  read a day early there. A hack made public long after its day is read on its day: LuBian
  (2020-12-28, $3.5 billion, made public in 2025).
- **Lesser, as OPEC's:** each day stays an ordinary day for every other flow; `raw-move --event
  crypto` keeps the flow's own lone days. `follows` keeps every hack; the results name days shared
  with another flow (`scripts/shared_days.py`).
- **Step 17's method, unchanged:** the spans, the base and its cut, the answers, the placebo, the
  walk-forward and its bars, the chance line, every market in `MVP_PRICE_SERIES` (30 with the two
  added), and both runs, from the close before and from the reaction close.

## The rule, fixed before anything is shown

- The source, the $100 million line, the hour, the two markets and step 17's bars, unchanged by
  what the run shows. A hack added to the list later joins with a dated amendment.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: 30 graded walk-forward needs 40 events ([OPEC's](opec.md)
  rule). The 28 markets with all 44 and bitcoin (43) and ether (42) have them on the day and the
  week; Coinbase (37) is *too few* walk-forward on every span. Over the month the no-overlap rule
  drops a hack within a month of the one before, so a market may fall below 40 there; the month's
  counts are recorded, not predicted.
  - The header: `follows: 44 crypto hacks 2014-02-07 … 2026-10-29: 44 hacks`.
  - Walk-forward: nothing holds.
  - On all history: no more answers than the chance line `follows` prints plus 2, for each run.
  - Bitcoin, ether and Coinbase on the day, the week and the month: *can't say*, in both runs. A
  hack takes coins from one place; it does not change what a coin is worth.
  - Every other flow's `follows` and `raw-move` output unchanged byte for byte except the two new
  markets' rows (step 1), which are recorded, not judged; each other flow's `follows` chance line
  rises by its two markets' cells alone, and the scoreboard's chance counts by the added cells
  alone, each written before and after.
- **Outside the rule, recorded:** `raw-move --event crypto`, whether hack days move more than
  ordinary days. Nothing is expected.

*Written 2026-11-18, before any closes of ether or Coinbase were loaded and before `follows` or
`raw-move` ran on these hacks; the counts above are from the list and the markets' first closes.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | **Done** 2026-11-18, the close check missed on 2 of 10 closes, [below](#step-1). The two markets: seed rows, series, `load-prices`; the seed `data/seed/crypto.csv` (`day,time,kind,target,amount`) from the list by `scripts/defillama_hacks.py` | `load-prices` stores both; each close of 2026-11-09 to 2026-11-13 checked against the close of Yahoo's last hourly bar before its time (`interval=60m`: ether's 23:00 UTC bar, Coinbase's 15:30 New York bar), within 0.05%; the seed test checks the header, 44 rows, order, time `04:00`, kind `hack`, each amount at least 100000000. On a copy of the store, before and after: every other flow's `follows` and `raw-move` output identical but for the two markets' rows and the chance lines, each chance line and the scoreboard's written here |
| 2 | **Done** 2026-11-18, [below](#step-2). Flow `crypto`; `follows --event crypto`; `crypto` in `TRIGGER_KINDS` | Tests: a Saturday hack reacts on Monday on bitcoin and on the S&P 500; a `crypto` trigger for a day not stored is answered from a hack made at 04:00 UTC. On a copy of the store the header is the expected one, and every other flow's output byte for byte the one of step 1's store |
| 3 | **Done** 2026-11-18, [below](#results). Results here and in [MVP results](../mvp-results.md), against the expected outcome; the roadmap row | Every bullet marked right or wrong with its numbers and command; each cell with 30 or more graded walk-forward and its record; the days shared with another flow, by the hack's UTC day |

### Step 1

*2026-11-18.* Every line quoted is in [the evidence](crypto-steps.txt), on a copy of the store
without and with the two markets.

- **The seed:** `scripts/defillama_hacks.py` wrote 44 rows, 2014-02-07 to 2026-10-29; the seed
  test holds, the four rows named above included (Coincheck, Ronin Bridge, FTX, Bybit, each its
  day and amount).
- **The closes:** ether 2,354 from 2017-11-09, Coinbase 1,407 from 2021-04-14. **The 0.05% check
  misses on 2 of 10 closes:** ether's of 2026-11-11 by 0.09% and Coinbase's of 2026-11-11 by
  0.059%; the other eight are within 0.04%. The five-minute bars give the same differences, so
  the gap is between Yahoo's daily close and its last intraday print, not the close's time: the
  first bar after each close is 0.15% to 9.9% off. Recorded as missed; the bar is not changed.
- **Every other flow's output:** all 53 `raw-move` and `follows` outputs identical once the two
  markets' rows and the chance lines are taken out. Each `follows` chance line rises by the two
  markets' cells (the Fed's 7.6 → 8.0, OPEC's 5.0 → 5.4, war's 2.5 → 2.6, each in the evidence);
  the scoreboard's raw-move chance 726 → 769 cells and its surprise 336 → 360, walk-forward 82
  unchanged, and its data otherwise identical but for the market list and its data date (the new
  closes run a day later).
- **A fault found and fixed:** `raw-move` and `scoreboard` stopped with *no median for empty data*
  on the president's tweets, which end before Coinbase's listing, so Coinbase has neither tweet
  days nor ordinary days there. A market with no days now gets a *too few* row (a test added).

### Step 2

*2026-11-18*, [the evidence](crypto-steps.txt), on a copy of step 1's store with the hacks loaded.

- **The header, as expected:** `follows: 44 crypto hacks 2014-02-07 … 2026-10-29: 44 hacks`.
- **The tests hold:** a Saturday hack reacts on Monday on bitcoin and the S&P 500; a `crypto`
  trigger for a day not stored is answered from a hack at 04:00 UTC.
- **Every other flow's output** (53 files) byte for byte step 1's. The scoreboard gains the hacks'
  entry (30 → 31 events) and its raw-move chance the flow's cells, 769 → 799; surprise and
  walk-forward unchanged; its data otherwise identical.
- War's one kind and the hack's share one rule (`study.ONE_KIND`), now that there are two.

## How you know it is right

- **The rows match the news:** four named now, each checked by hand against its Wikipedia article
  and the list's own description: 2018-01-26 Coincheck ($534
  million), 2022-03-23 Ronin Bridge ($624 million), 2022-11-12 FTX ($450 million, the theft after
  its collapse, which ran from late on 11-11 into 11-12 UTC; the list's day is kept), 2025-02-21 Bybit ($1.4 billion). Each a theft on that day.
- **The new closes are at their times:** the 0.05% check above; a wrong close time would show as
  a gap of a day's move.
- **The hour is UTC:** a weekday hack's stored `event_ts` is 04:00 that day and reacts on bitcoin
  and the S&P 500 the same day.
- **Nothing else changes:** every other flow's output on a copy of the store, OPEC's included.

## What this step does not do

Only hacks: not exchange collapses (FTX's bankruptcy, Celsius, Terra), which have no free dated
list; not spot ETF approvals (two, 2024-01-10 for bitcoin and 2024-05-23 for ether) or halvings
(three in bitcoin's stored history), too few for an answer. Hacks under $100 million are not
taken. No other coin, no stock but Coinbase. Not on the page's [*ask*](ask-the-fortune-teller.md).
No live link.

## Technical details

- **Markets:** `ETH` (`ETH-USD`, 23:59 UTC) and `COIN` (`COIN`, 16:00 New York) in
  `study.MVP_PRICE_SERIES`, seed rows in `data/seed/instruments.csv`, sign 0 in every flow's rule.
- **Seed:** `data/seed/crypto.csv`, columns `day`, `time` (`04:00`), `kind` (`hack`), `target`
  (the list's `name`) and `amount` (dollars), 44 rows, written by `scripts/defillama_hacks.py`
  from the downloaded list, which is not committed. Documented in `docs/legacy/data/README.md`.
- **Flow:** a `DatedShockFlow` in `flows.py`: event type `Cyber attack / hack` (already seeded),
  country `World`, zone UTC, type code 31, `crypto`, detail the target; `lesser`, unscheduled. One
  kind, as war's. `FOLLOWS_NOUNS` gains `crypto hacks`; `TRIGGER_KINDS` gains `crypto` with
  `hack`; a live trigger's hack is made at 04:00 UTC.
- **Tests** in `tests/test_seed_data.py`, `tests/test_what_follows.py`, `tests/test_triggers.py`,
  `tests/test_study_raw_move.py`.
- **Docs:** this spec; `docs/schema.md` (code 31, the detail, the instruments); the glossary
  (*DefiLlama*, *hack*, *ETH*, *COIN*); roadmap row 27 amended to hacks; status, changelog.

## Results

*2026-11-18.* Every line quoted is in [the evidence](crypto-results.txt): step 2's copy of the
store, the whole output of `follows --event crypto` (from the close before), `follows --event
crypto --after-the-day` (from the reaction close) and `raw-move --event crypto`, and
`scripts/shared_days.py`'s count.

**In plain words:** after $100 million or more was stolen in a crypto hack, bitcoin, ether and
Coinbase's shares did nothing an ordinary day, week or month would not, counted from either close.
Across every market there is one answer: the VIX rose on the day counted from the close after,
within what luck alone gives. No market moves more on hack days than on ordinary days by the bar,
though 16 are *unclear*. The expected outcome held but for one piece of arithmetic: fewer markets
than expected had 40 hacks counted over the week.

- **The header, as expected:** `follows: 44 crypto hacks 2014-02-07 … 2026-10-29: 44 hacks`
  (`follows --event crypto`). Right.
- **Walk-forward: nothing holds** (both runs). Right. No cell reaches 30 graded: the most is
  coffee's week from the reaction close, 14 graded, 5 right; the 5-year yield's month 5 and 7
  (3 and 4 right), the rest 1 to 4.
- **On all history, against the chance line plus 2** (each run; chance about 2.7, so a bar of
  4.7): from the close before **0 answers**; from the reaction close **1**, the VIX *up* on the day
  (24 up, 8 the same, 12 down of 44, chance 0.0087), *too few* walk-forward, not marked by the
  placebo. Right in both.
- **Bitcoin, ether and Coinbase** (both runs): *can't say* on all 18 cells. Right. Counted:
  bitcoin 43 on the day, 40 over the week, 31 over the month (11 left out for overlap); ether 42,
  39, 30; Coinbase 37, 34, 26. The smallest chance is bitcoin's week from the close before, 0.0214,
  12 up, 20 the same, 8 down of 40, against the bar of 0.01.
- **The arithmetic: wrong for the week.** Coinbase is *too few* on every span, as expected. But the
  week has fewer than 40 counted where 40 were expected: from the close before, ether 39, the
  Nikkei 39, the DAX, the Euro Stoxx 50 and the STOXX 600 37, the FTSE 100 35; from the reaction
  close each of these 39. A week's span ends past the next hack's start on those markets and is
  left out for overlap. No cell reached 30 graded either way.
- **Every other flow's rows** ([step 1](#step-1), [step 2](#step-2), the `cmp` and the chance
  lines in [their evidence](crypto-steps.txt)): unchanged but for the two markets' rows; the chance
  lines rose by the added cells alone. Right.
- **The size of the move** (`raw-move --event crypto`, outside the rule, recorded): on the hacks'
  lone days no market *moves*: 14 *doesn't*, 16 *unclear*, among them energy stocks (ratio 1.59,
  p 0.0148) and the euro (1.45, 0.039); bitcoin's ratio 0.95, ether's 1.18, Coinbase's 1.05.
- **Days shared with another flow** (`scripts/shared_days.py crypto`): 25 of the 44, by the hack's
  UTC day; jobless claims on 8, the ECB president's statements on 5, the euro area's flash HICP,
  ISM, the Fed chair's statements and the president's second-term posts on 3 each, and twelve
  others on 1 or 2 (in the evidence).
