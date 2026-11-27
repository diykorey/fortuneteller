# The 2-year yield

> Step 63 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-27 by the owner
> from a review of possible sources ([Decisions](../decisions.md)). It follows
> [the breakeven](breakeven.md), the first market read from FRED, and signs the new market as
> [more outcomes](more-outcomes.md) signed the 5-year yield. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** the interest the US government pays to borrow for two years. It moves with
what traders expect the Fed to do next, so it should react to jobs, inflation and spending
releases. In the links that hold so far, a release is compared with its forecast and the market
is an interest rate or a currency, the 5-year yield most often. The 2-year is shorter still, so it
is the market most likely to add more of them.

When this step is done, `load-prices` stores it; `raw-move`, `surprise`, `predict`, `follows`,
the scoreboard, the triggers, the guesses and the big moves show it; and a link on it that holds
walk-forward is called by the morning job, like the 5-year's.

## The way to reach it

- **FRED's `DGS2`,** the Treasury's daily 2-year yield (*constant maturity*: read from the
  Treasury's curve at exactly two years, not from one bond), read exactly as the
  breakeven is read (a `fred:` ticker). On 2026-11-27 it held 12,617 closes from 1976-06-01 to
  2026-11-24, in percent with at most two decimals. Its longest gap is 5 days (1978-05-26 and
  1982-02-11). Since 2003 its median daily move is 2 bp. Yahoo has no 2-year yield, so FRED is the
  only free daily source here.
- **Its close is 15:30 New York,** the time of the quotes the Treasury builds its curve from, as for
  `T5YIE`. An 08:30 release and a 14:00 Fed decision fall on that day's close. An event from
  15:30 on falls on the next day's.
- **A day late,** as the breakeven. FRED publishes a day's value the next business day. A logged
  call on it goes in `score`'s `waiting` list, which holds up no other market, and is graded the
  evening its close lands ([the breakeven's sign](breakeven-sign.md)). The rule names the
  source, not the market, so no code changes for it.
- **Its sign comes from the 10-year's,** by the same analogy as the 5-year's: `with_more_outcomes`
  gives `"UST2Y / ZT": signs["UST10Y / ZN"]` in every flow's rule. No sign comes from a result.
- **On the 1 bp grid,** most daily medians tie at 1 or 2 bp, so a *does it move?* ratio moves in
  steps of a half, as the breakeven's did ([Precision](../precision.md)).

| Symbol | Market | Source | Daily since |
| --- | --- | --- | --- |
| `UST2Y / ZT` | US Treasury 2Y | FRED `DGS2` | 1976-06-01 |

## The rule, fixed before anything is measured

- **Same tests, same bars:** rung 1's raw move, `raw-move` (*moves*: a median ratio ≥ 1.10 to
  ordinary days and p < 0.01); step 4's surprise verdict, `surprise` (*tracks*: rank correlation
  p < 0.01 and hit rate ≥ 60%); `predict`'s walk-forward (*holds*: right on ≥ 60% of ≥ 30
  predictions, p < 0.01); and [step 17's](what-follows.md) `follows`, from the close before and
  from the reaction close (a cell *holds* with ≥ 30 graded, right on ≥ 60% and 10 points above
  their mean base rate, chance < 0.01). All unchanged.
- **The 5-year is the yardstick.** Step 1 prints `raw-move`, `surprise` and `predict` for every
  flow on the copy of the store before the 2-year is added and records the 5-year's numbers here.
  The expected outcome below is judged against those numbers, not against older ones.
- **Every existing row unchanged.** On a copy of the store, every flow's `raw-move`,
  `surprise`, `predict` and `follows` output (both runs), and the scoreboard's `data.json`, are
  compared before and after with the 2-year's lines and the chance lines dropped. The diff must be
  empty.
- **Calls follow on their own.** A signed link that holds is called by `predict` and the morning
  job. None is added or removed by hand.
- **Expected outcome, written first:**
  - *Does it move?*: *moves* on the days of CPI, the jobs report, the Fed, GDP and ISM, where the
    5-year *moved* on 2026-10-27 ([more outcomes](more-outcomes.md#results)), and on no other
    flow.
  - `surprise`: *tracks* on CPI, retail sales and ISM, where the 5-year tracked then.
  - `predict`, walk-forward: *holds* on the jobs report, retail sales and ISM, where the 5-year
    held then (71 of 101, 49 of 74, 34 of 50), and on no other flow. On each, its hit rate is
    within 5 points of the 5-year's in step 1's before run.
  - `follows`, from the close before: after a jobs report above the consensus, the 2-year *up* on
    the day *holds*, as the 10-year's and the 5-year's do on the page (right 39 and 37 of 58).
  - Live: the morning job calls it on the jobs report and retail sales (ISM lands at 10:00, after
    the morning job).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The 2-year: a seed row, a `fred:DGS2` price series, its sign, its plain name and area; `load-prices` stores it | The tests below pass; on a copy of the store the comparison gives an empty diff; the closes stored equal FRED's non-blank values to the copy's last day, their count and first and last dates here; the 5-year's before-run numbers here; the scoreboard's rebuild time here, under the evening job's 15 minutes (*amended 2026-11-27, after measuring:* the evening job's limit is its `TimeoutStartSec`, 40 minutes since 2026-11-04, not 15, and the rebuild before the 2-year already took 962 s; the bar becomes the time recorded here and the evening job's limit raised to 60 minutes); not merged on a day in the scoreboard's `ahead` list before that day's evening run |
| 2 | Results here, in [MVP results](../mvp-results.md) and the roadmap row | Each verdict against the expected outcome, each number with the command that prints it |

**Step 1, done 2026-11-27.** The tests pass. The comparison was run on a copy of the store from
01:31 that day.
- **The diff:** with the 2-year's lines and the chance lines dropped, it is empty, apart from three
  things. Two flows' lists of answer counts wrap at `UST2Y /`. In `data.json`, the 2-year's answer
  in `holds` names the market in words. And three market capitalisations in `earnings_ahead`
  differ; they are fetched from Nasdaq when the page is built, not read from the store.
- **The closes:** 12,617 stored from 1976-06-01 to 2026-11-24. That is FRED's count of non-blank
  values that day, with the same days and the same values (554 blank days are absent). By hand:
  1976-06-01 7.26, 2008-09-15 1.78 (down 45 bp from 2.23 on 2008-09-12), and 2026-11-24 4.63, each
  equal to FRED's.
- **The 5-year, before the 2-year** (`raw-move`, `surprise`, `predict --event <flow>`):

  | Flow | *Does it move?* | `surprise` | `predict`, walk-forward |
  | --- | --- | --- | --- |
  | CPI | 1.29, p 0.0004, *moves* | 0.21, 64% of 107, *tracks* | 6 of 8, *too few* |
  | Jobs report | 1.90, p 0.0001, *moves* | 0.27, 60% of 467, *unclear* | 72 of 102 (71%), *holds* |
  | Fed | 1.39, p 0.0001, *moves* | 51% of 55, *doesn't* | none, *too few* |
  | GDP | 1.76, p 0.0001, *moves* | 38% of 13, *doesn't* | none, *too few* |
  | ISM | 1.48, p 0.0001, *moves* | 0.38, 69% of 54, *tracks* | 33 of 50 (66%), p 0.0164, *doesn't hold* |
  | Retail sales | 1.23, p 0.0010, *moves* | 0.30, 70% of 91, *tracks* | 49 of 74 (66%), *holds* |

  It also *moves* on jobless claims, the BoE, the debt limit and the S&P 500's earnings, and on
  no other flow. Where the expected outcome counts ISM among the 5-year's holds (34 of 50), it
  now holds 33 of 50 and doesn't hold.
- **The rebuild:** 962 s before and 1,069 s after, on the same machine. Both are over the old
  15-minute bar. The evening of 2026-11-26 took 39 of its 40 minutes (its pull request opened 31
  minutes in, merged 8 minutes later). So the evening job's `TimeoutStartSec` goes from 40 to 60
  minutes in this change, and the unit is installed again.

## Results

Measured 2026-11-27 on the copy of step 1, with the 2-year added (#485). Each command is run as
`fortuneteller <command> --event <flow>`.

**In plain words:** the 2-year yield goes up after a jobs report above its forecast, and on ISM's
manufacturing survey above its forecast. Both hold when each release is predicted only from the
ones before it. So it adds a call on the jobs report, beside the 10-year's and the 5-year's, and
one link on ISM, which lands too late in the morning to be called live. It does not add a call on
retail sales or on CPI.

| Expected | Found | |
| --- | --- | --- |
| *moves* on CPI, the jobs report, the Fed, GDP and ISM, no other flow | *moves* on the jobs report (5 bp against 3, 1.67, p 0.0001), the Fed (4 against 2, 2.00, p 0.0001) and GDP (2.00, p 0.0007); CPI *doesn't* (3 against 3, 1.00), ISM *unclear* (1.50, p 0.0112); also *moves* on the debt limit (2.00, p 0.0003, 47 days) and the Fed chair's statements (1.50, p 0.0048) | **wrong** in part |
| `surprise`: *tracks* on CPI, retail sales and ISM | *tracks* on ISM (0.51, 74% of 54) and the jobs report (0.34, 61% of 408); CPI *unclear* (0.21, 60% of 107, the bar's edge), retail sales *unclear* (0.28, 53% of 91) | **wrong** in part |
| `predict` *holds* on the jobs report, retail sales and ISM, each within 5 points of the 5-year | the jobs report 69 of 105 (66%, p 0.0008), 4.9 points under the 5-year's 72 of 102 (71%); ISM 36 of 49 (73%, p 0.0007), 7.5 points over the 5-year's 33 of 50, which doesn't hold; retail sales 13 of 28, *too few*; no other flow | **wrong** in part |
| `follows`: after a jobs report above the consensus, *up* on the day holds | up after 44 of 69 such reports; replayed, 34 of 54 right (63%), *holds* (`follows --event nfp`) | right |
| Live calls on the jobs report and retail sales | the scoreboard's `ahead` lists the 2-year on the jobs report of 2026-12-04, *holds*; retail sales none | **wrong** in part |

- **Why CPI and retail sales miss:** on the 1 bp grid, the median on ordinary days ties at the
  release days' 3 bp (CPI) and 2 bp, as [Precision](../precision.md) warned. On retail sales the
  surprise sends it the expected way on 53% of noticeable surprises, against the 5-year's 70%, so
  walk-forward predicts on only 28 releases.
- **By chance:** with the 2-year, about 15.5 *moves* (1,548 cells), 6.8 *tracks* (684) and 0.9
  walk-forward *holds* (90) would pass by chance at p < 0.01 (the scoreboard's `chance`). The
  2-year adds 2 holds.
- **Its other answers in `follows`:** four lean but don't hold walk-forward. After a BoC hold, up
  over the week (30 of 85 right). After jobless claims above, down on the day (26 of 69). After
  retail sales below, down on the day (21 of 46). After a jobs report below, down on the day (13
  of 27, *too few*).

## How you know it is right

- **The source:** a test serves `DGS2` through the patched `sources.fetch_series`, as for `T5YIE`,
  and `daily_bars.source` reads `fred:DGS2`. A FRED error stores nothing, as now.
- **The values:** on the copy, three stored closes, the first, 2008-09-15 and the last, equal
  FRED's `DGS2` for that day read by hand. The 2-year's move on 2008-09-15 is the difference in
  bp. FRED's blank (`.`) days are absent from `daily_bars`, not zero or carried forward, so the
  count equals FRED's non-blank values.
- **The hours:** in `test_event_flows.py`, an 08:30 release and a 14:00 Fed decision fall on the
  2-year's close that same day.
- **The sign:** the signs test gives `UST2Y / ZT` the 10-year's sign in every flow's rule.
- **Waiting:** a call on the 2-year with no close yet is listed as `waiting:`, not `pending:`.
- **Nothing else moved:** the empty diff of step 1.
- **The counts:** the tests that count markets count 38 where they counted 37.

## What this step does not do

No 30-year yield, no slope between two yields, no 2-year futures. No new release (the US releases
with forecasts come next, as a step of their own). No change to the bars, the guesser's prompt or
the front page's areas: the 2-year joins *interest rates and inflation*.

## Technical details

- **`data/seed/instruments.csv`:** `UST2Y / ZT,US Treasury 2Y,rates_bond,us,CBOT (CME) / OTC
  cash,The short end of the curve, read from FRED's DGS2; measured as yield in bps like the
  10-year.`
- **`study.py`:** `"UST2Y / ZT": PriceSeries("fred:DGS2", "bps", time(15, 30), NEW_YORK)`, last.
- **`flows.py`:** `"UST2Y / ZT": signs["UST10Y / ZN"]` in `with_more_outcomes`, and its
  docstring.
- **`__main__.py`:** the plain name "the interest the US government pays to borrow money for 2
  years", and the area *interest rates and inflation*.
- **Docs, step 1:** this spec's note, `docs/schema.md` (the seed row, the counts), the glossary,
  [the guess ledger](guess-ledger.md)'s list of markets (37 to 38), `README.md`, status, the changelog.
- **Docs, step 2:** the results here, `docs/mvp-results.md`, the roadmap row, status, the changelog.
