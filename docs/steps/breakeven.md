# The breakeven

> Step 19, part 2b, of the [Roadmap](../roadmap.md#next-steps-in-order), taken 2026-11-04 during
> the owner's "proceed with the project for the next 18 hours". Follows [coffee](coffee.md),
> part 2a, whose template it reuses. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** what the bond market expects prices to rise by, a year on average over the next
five: the 5-year *breakeven*. It is the market's own answer to "will things get dearer?". At the
end, `load-prices` stores it, and `raw-move`, `surprise`, `follows`, the scoreboard and the
triggers show it. No call is made on it.

## The way to reach it

- **FRED's `T5YIE`, the first price series not from Yahoo.** The 5-year Treasury yield less the
  5-year inflation-protected (TIPS) yield, both from the Treasury's daily curve: on the last 399
  days `T5YIE` equals FRED's `DGS5` less `DFII5` exactly. Daily since 2003-01-02, in percent, so
  its move is in basis points, as the yields', on a 1 bp grid (two decimals). Its longest gap is
  four days, over long weekends; Hurricane Sandy took out 2012-10-30 alone.
- **Its close: 15:30 New York,** the time of the bid quotes the Treasury builds its daily curve
  from, by its own description. A day's match can't tell 15:00 from 15:30, but it fixes the day:
  FRED's `DGS5` is a median 0.7 bp from Yahoo's `^FVX` on the same day, 3.4 bp a day either way
  (5,953 days since 2003). `^FVX` keeps the 15:00 measured for it. An 08:30 release and a 14:00 Fed
  decision fall on the same day's close; an event from 15:30 on, the next day's. On 39 days `^FVX`
  has a close and `DGS5` none: the bond market's own holidays (Columbus Day, Veterans Day).
- **A day late.** FRED publishes a day's value the next business day, so on a release's evening
  the breakeven has no reaction close yet. In 2b, unsigned, that costs nothing wrong:
  - `load-prices` reports the release skipped (no close nearby) and stores it the next evening;
  - a trigger waits for the close and is answered from the reaction close the evening after;
  - no call or guess can be on it, so `score` has nothing pending for it;
  - the published scoreboard, rebuilt only on an evening that grades a call, may show the breakeven
    a release behind the other markets until the next such evening.

  **Once it has a sign (2c), this blocks:** a call on it leaves `score` pending on the release's
  evening, and the evening job then stops before the triggers and the scoreboard, for every market.
  Part 2c must solve that before signing it.
- **One jump that is no move.** On 2008-12-01 the breakeven rose 192 bp while the 5-year yield fell
  22 bp: the TIPS curve's 5-year point fell 214 bp in a day as the curve's construction changed
  between issues. No stored event falls on that day, but it enters the ordinary days' median and
  every month's span from October and November 2008; [Precision](../precision.md) records it.
- **No sign, so no call.** `with_more_outcomes` gives it 0. Part 2c weighs the signs.

| Symbol | Market | Source | Daily since |
| --- | --- | --- | --- |
| `T5YIE` | US 5-year breakeven inflation | FRED `T5YIE` | 2003-01-02 |

## The rule, fixed before anything is measured

- **Same tests, same bars, same procedure** as coffee's; drop the breakeven's lines and the chance
  lines; the diff must be empty. Chance lines now over 25 markets.
- **Expected outcome, written first:**
  - *Does it move?*: the breakeven *moves* on `cpi`'s days and `fomc`'s, and on no other flow.
  - `follows`: it holds walk-forward for no flow, and gets at most 2 answers in any run.
  - The scoreboard is rebuilt in under 15 minutes alone (801 s at 24 markets).
  - `live`'s statement previews: a preview gains `T5YIE` only if it *moves* on that statement's
    flow (the Fed chair's, the ECB chief's, posts); under this outcome none does.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The breakeven: a seed row, an `MVP_PRICE_SERIES` row read from FRED, a 0 sign, `load-prices` stores it, with the FRED key~~ **done** 2026-11-04 (PR #263) | The tests below pass. On a copy of the store the procedure gives an empty diff, the counts are in `docs/schema.md` and the rebuild time here |
| 2 | ~~Results here and in [MVP results](../mvp-results.md)~~ **done** 2026-11-04 (PR #264) | Its *does it move?* verdict for every flow and its `follows` answers, against the expected outcome |

*Step 1, 2026-11-04 (PR #263):*
- On a copy of the store `load-prices` stored the breakeven's 5,964 closes, 2003-01-02 to
  2026-11-03 (the 4th not yet published that evening); 190,387 for the 25.
- The procedure gave an empty diff: `follows` for its four flows with and without the flag, `score`,
  `raw-move` and `surprise` for every flow, and the scoreboard's whole `data.json`, without the
  breakeven and the chance lines.
- The scoreboard was rebuilt in 826 s alone (990 s beside a second rebuild), under the 15-minute
  bar, now with 74 s to spare: the next market may not fit without making the rebuild faster.

## Results

Measured 2026-11-04 on a copy of the store with the 25 markets loaded, at PR #263.

**Does it move?** The breakeven *moves* on `cpi`'s days (median 3 bp against 2 bp, ratio 1.50,
p 0.0001), and on US elections' (4.5 bp, 10 days). It is *unclear* on Germany's Ifo (1.50, p 0.017)
and the second term's posts; five flows have too few days; on the other 16 it *doesn't*. The
expected outcome said `cpi` and `fomc`: **`fomc` is wrong**, its median is the ordinary day's 2 bp
(ratio 1.00), and the elections are more. On a 1 bp grid most medians tie at 2 bp, as precision
warned, so a ratio here moves in steps of a half. `surprise` gives it nothing beyond *unclear*, as it
can't without a sign.

**What follows** (`follows`, four flows, from the day and from the reaction close). **After a CPI
above consensus, the breakeven rises on the day, and it holds walk-forward:** up after 43 of 61 such
releases since 2003 (the base 35%), chance 0.0000, and replayed in order 23 of 30 graded right (77%).
It is the first market people feel with a link that holds, against an expected outcome of none, and
by chance about 0.0 would. Where the 10-year and 5-year yields *can't say* after the same releases,
the breakeven, the inflation they carry, rises. Its other answers:

- after CPI above, up over the week too (61 events; 12 of 22 right, too few); below, down on the day
  (78; 17 of 34 right walk-forward, doesn't hold);
- after CPI as expected, *about the same* over the month from the reaction close (51; 14 of 30,
  doesn't hold);
- after a jobs report above consensus, up on the day (68; 15 of 22, too few).

Five answers, three in `cpi`'s run, against an expected outcome of at most 2 in any run: **wrong**,
and for the same reason as the hold.

In plain words: when US inflation comes in hotter than economists expected, the bond market's guess
at the next five years' inflation goes up that day, about seven times in ten, and the record says it
would have called it right ahead of time. It is the market's own "things will get dearer".

Part 2c may sign it (+1 on a hotter CPI). Before it can be called live, the evening grade must
learn to wait a day for FRED's close, as above.

## How you know it is right

- `load-prices` reads `T5YIE` from FRED and every other series from Yahoo, all fetched before any
  is stored; `daily_bars.source` is `fred:T5YIE` and `observations.data_source` `fred` for it. A
  FRED error or an empty series exits 1 with the message and stores nothing
  (`test_load_prices_stores_nothing_when_fred_fails`). Without a key it exits 1 naming
  `FT_FRED_API_KEY`, after the releases check (`test_load_prices_needs_the_fred_key`).
- Every test that runs `load-prices` or `load_daily_bars` pins the key and serves `T5YIE` by
  patching `sources.fetch_series`, so none reaches FRED: a few closes around 2022-09-13 inline, so
  the hot print in `test_study_observations.py` reads `T5YIE        1 observations`.
- In `test_event_flows.py`: the 08:30 test's list gains `"T5YIE"`; the 14:00 test gains
  `"T5YIE": date(2022, 9, 21)`, the same day, and its name says so; the signs test gains
  `"T5YIE": 0`, last.
- The tests that count markets count one more, as coffee's did: `test_study_prices.py` (its bars
  too), `test_study_observations.py`, `test_study_raw_move.py` (its slice too),
  `test_study_surprise.py` (72 → 75, 48 → 50) and `test_scoreboard.py` (chance over 25; the
  later stream gains the breakeven).

## What this part does not do

- No 10-year breakeven, no 5-year-5-year forward. No signs (part 2c).

## Technical details

- **`data/seed/instruments.csv`:** after `KC`:
  `T5YIE,US 5-year breakeven inflation,rates_bond,us,OTC cash (Treasury curve),5-year Treasury yield less 5-year TIPS yield.`
- **`study.py`:** after `KC`, `"T5YIE": PriceSeries("fred:T5YIE", "bps", time(15, 30), NEW_YORK)`;
  the comment above it says a `fred:` ticker is FRED's series and why 15:30.
  `load_daily_bars(api_key: str, con=None)`: a ticker starting `fred:` is read with
  `sources.fetch_series(api_key, ticker.removeprefix("fred:"))` and `parse_series` into
  `DailyClosingPrice`s, an empty one a `FredError`; every other from Yahoo, as now.
  `store_daily_bars` stores a `fred:` ticker as its source, any other as `yahoo:<ticker>`; the
  observations' `data_source` is the source's provider, `fred` or `yahoo`.
- **`__main__.py`:** `_load_prices` calls `_fred_key("load-prices")` after the releases check and
  catches `sources.FredError` beside `YahooError`; its help and the module docstring say "from
  Yahoo and FRED".
- **`flows.py`:** `"T5YIE": 0` after `"KC"` in `with_more_outcomes`; its docstring "…, nor the
  breakeven (docs/steps/breakeven.md)".
- **Docs, step 1:** this spec's note; `docs/schema.md` (31 seed rows, 25 measured, the counts, a
  `T5YIE` row, `source`'s `fred:` value, a `fred` row under `data_source`, the `close` column
  holding a spread in percent); the glossary (*Breakeven*, `T5YIE`, `fred:` under vendor tickers);
  `docs/accounts.md` (the FRED key feeds `load-prices` too); `README.md`; `docs/status.md`. Row 19
  and `docs/precision.md`'s breakeven row are written with this spec. `docs/legacy/data/` is not
  edited.
- **Docs, step 2:** this spec's results, `docs/mvp-results.md`, `docs/status.md`.
