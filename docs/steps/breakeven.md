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
  its move is in basis points, as the yields'. No gap of more than four days.
- **Its close.** The Treasury's curve is read from bid quotes near 15:30 New York. FRED's `DGS5`
  matches Yahoo's `^FVX` on the same day within a median 0.7 bp (5,953 days since 2003; 3.4 bp a
  day either way), as `^TNX` matches `DGS10`. So the close is 15:30 New York: an 08:30 release and
  a 14:00 Fed decision fall on the same day's. On 39 days `^FVX` has a close and `DGS5` none: the
  bond market's own holidays (Columbus Day, Veterans Day), when the breakeven has no close either.
- **A day late.** FRED publishes a day's value the next business day, so the evening job sees the
  breakeven a day behind: its reaction close is missing on the release's evening and there the next.
  The triggers and the scoreboard already wait for a close that is not there.
- **One jump that is no move.** On 2008-12-01 the breakeven rose 192 bp while the 5-year yield fell
  22 bp: the TIPS curve's 5-year point fell 214 bp in a day as the curve's construction changed
  between issues. [Precision](../precision.md) records it; no stored event falls on that day.
- **No sign, so no call.** `with_more_outcomes` gives it 0. Part 2c weighs the signs.

| Symbol | Market | Source | Daily since |
| --- | --- | --- | --- |
| `T5YIE` | US 5-year breakeven inflation | FRED `T5YIE` | 2003-01-02 |

## The rule, fixed before anything is measured

- **Same tests, same bars, same procedure** as coffee's; drop the breakeven's lines and the chance
  lines; the diff must be empty. Chance lines now over 25 markets.
- **Expected outcome, written first:**
  - *Does it move?*: the breakeven *moves* on CPI's days and on the Fed's, and on no other flow.
  - `follows`: it holds walk-forward for no flow, and gets at most 2 answers in any run.
  - The scoreboard is rebuilt in under 15 minutes alone (801 s at 24 markets).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The breakeven: a seed row, an `MVP_PRICE_SERIES` row read from FRED, a 0 sign, `load-prices` stores it | The tests below pass. On a copy of the store the procedure gives an empty diff, the counts are in `docs/schema.md` and the rebuild time here |
| 2 | Results here and in [MVP results](../mvp-results.md) | Its *does it move?* verdict for every flow and its `follows` answers, against the expected outcome |

## How you know it is right

- `load-prices` reads `T5YIE` from FRED and every other series from Yahoo; `daily_bars.source` is
  `fred:T5YIE` for it. Without a FRED key `load-prices` exits 1 and names the key, as
  `load-releases` does, before storing anything.
- An 08:30 release and a 14:00 Fed decision react on the same day's close.
- The tests that count markets count 25, as coffee's did; the tests that run `load-prices` set a
  FRED key and serve `T5YIE`.

## What this part does not do

- No 10-year breakeven, no 5-year-5-year forward. No signs (part 2c).

## Technical details

- **`data/seed/instruments.csv`:** after `KC`:
  `T5YIE,US 5-year breakeven inflation,rates_bond,us,FRED,5-year Treasury yield less 5-year TIPS yield.`
- **`study.py`:** `"T5YIE": PriceSeries("fred:T5YIE", "bps", time(15, 30), NEW_YORK)`.
  `load_daily_bars(con, api_key)` reads a ticker that starts `fred:` with `sources.fetch_series`
  and `parse_series`, every other with Yahoo as now; `store_daily_bars` writes the source as given
  (`yahoo:` is added to Yahoo's tickers, `fred:` is already there).
- **`__main__.py`:** `load-prices` takes the FRED key as `load-releases` does.
- **`flows.py`:** `"T5YIE": 0` in `with_more_outcomes`.
- **Docs, step 1:** this spec's note; `docs/schema.md` (the `source` column's `fred:` value, the
  seed's rows, the counts); the glossary
  (*Breakeven*, `T5YIE`); `README.md`; `docs/status.md`. Row 19 and `docs/precision.md`'s breakeven row are written with
  this spec. `docs/legacy/data/` is not edited.
- **Docs, step 2:** this spec's results, `docs/mvp-results.md`, `docs/status.md`.
