# The markets people feel

> Step 19, part 1, of the [Roadmap](../roadmap.md#next-steps-in-order), taken 2026-11-04 during
> the owner's "proceed with the project for the next 18 hours". Row 19 is amended with this spec.
> Builds on [more outcomes](more-outcomes.md), the template for adding a market. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** a reader pays for bread, petrol, heating and a mortgage, not for the S&P 500.
This part adds the markets behind four of those everyday things (grain, petrol, heating gas) and
two kinds of stocks a reader feels through rates. Every table the project prints gains a column for
each, under the same tests and bars.

The [Legend](../legend.md#the-target) says "the coffee market rose" is enough. At the end,
`load-prices` stores seven more series, and `raw-move`, `surprise`, `follows`, the scoreboard and
the triggers show them. No call is made on them yet.

## The way to reach it

- **Funds that hold the futures, not the front month.** Yahoo's front-month futures (`ZC=F`,
  `RB=F`, `NG=F` and so on) jump each time they roll from one contract to the next. Probed
  2026-11-04, their largest day moves include roll days: corn 23.6% on 2013-07-15, the switch to the
  new crop; gasoline 24.2% on 2016-03-01, the switch to summer grade. A jump like that is no event's
  move. Each commodity is read instead through the US fund that holds its futures and rolls them
  over several days, so its price has no jump. The cost is the roll itself. Measured 2026-11-04
  over every 21-close span both series share, the fund less the front month, median:
  - corn −0.7%, wheat −0.8%, soybeans −0.3%, gasoline +0.5%, natural gas −1.6% (mean −2.6%);
  - on a single day the two differ by a median of 0.3% to 0.5%.

  Over a day or a week that is small beside the moves. Over a month natural gas's drift is not, and
  part 2's quarter and year would be worse. [Precision](../precision.md) records it, and a `follows`
  answer for natural gas over the month is read with it.

| Symbol | Market | Yahoo | Venue | Daily since |
| --- | --- | --- | --- | --- |
| `CORN` | Corn, through the Teucrium Corn Fund | `CORN` | NYSE Arca | 2010-06-09 |
| `WEAT` | Wheat, through the Teucrium Wheat Fund | `WEAT` | NYSE Arca | 2011-09-19 |
| `SOYB` | Soybeans, through the Teucrium Soybean Fund | `SOYB` | NYSE Arca | 2011-09-19 |
| `UGA` | Gasoline, through the United States Gasoline Fund | `UGA` | NYSE Arca | 2008-02-28 |
| `UNG` | Natural gas, through the United States Natural Gas Fund | `UNG` | NYSE Arca | 2007-04-18 |
| `XLU` | US utilities, the Utilities Select Sector SPDR | `XLU` | NYSE Arca | 1998-12-22 |
| `ITB` | US homebuilders, the iShares U.S. Home Construction ETF | `ITB` | Cboe BZX | 2006-05-05 |

- **Their close.** Each trades until 16:00 New York, as `ITA` and `XLE` do. Step 1 checks the
  close against Yahoo's last 5-minute bar of 16:00 on recent days, for the thinly traded wheat,
  soybean and gasoline funds at least. Their gaps of more than four days are the market closures
  every US series has: 2012-10-26 to 10-31 (Hurricane Sandy) in all seven, 2006-12-29 to 2007-01-03
  in `XLU` and `ITB`, and 2001-09-10 to 09-17 in `XLU`. Yahoo's close is split-adjusted: UNG's
  2024 reverse split shows no jump. It is not adjusted for dividends: `XLU` drops about 0.7% on
  each quarter's ex-dividend day, as `XLE` and `ITA` already do. Precision records it.
- **No signs yet, so no calls.** Every flow's rule gives the seven a sign of 0 (`with_more_outcomes`).
  So they are asked only "does it move?" and step 17's spans, as oil and bitcoin are. No call
  goes out for them, unattended, on the next releases (jobless claims on 2026-11-05 and the jobs
  report on 2026-11-06). Utilities and homebuilders could be signed later through the yields, but
  homebuilders also rise with a stronger economy, so a sign by analogy is not clear. Part 2 weighs
  signs after these results, with the coffee and the breakeven.
- **Coffee and the 5-year breakeven wait for part 2.** Coffee has no fund left on Yahoo (`JO` closed
  in 2023), so it needs a rule for its front month's roll days. The breakeven is a FRED series, not
  a Yahoo one, with its own close to establish.
- **Triggers.** No trigger is filed yet, so none gains rows for the seven. A trigger filed later is
  answered on all 23 markets.

## The rule, fixed before anything is measured

- **Same tests, same bars:** rung 1's raw move, step 4's surprise correlation (no verdict beyond
  *unclear* without a sign), and step 17's spans.
- **Every existing cell unchanged,** by this procedure. Copy the store and run `load-prices` on the
  copy at this branch. Then, on that copy, run each of these at the base commit and at this branch:
  - `raw-move` and `surprise` for every `--event`;
  - `follows` for its four, with and without `--after-the-day`;
  - `predict`, `score` and `scoreboard`.

  Drop the seven markets' lines and the chance lines. The diff must be empty.
- **Chance, counted:** each command's chance line, as it prints it, now over 23 markets.
- **Expected outcome, written first:**
  - *Does it move?*: homebuilders *moves* on the days of the jobs report, CPI and the Fed's
    decisions; utilities *moves* on the Fed's; none of the five funds *moves* on any flow beyond the
    chance line's share.
  - `follows`: no new market holds walk-forward for any of the four flows. Answers on the new
    markets are at most their share of each flow's chance line plus 2.
  - The scoreboard is rebuilt in under 15 minutes alone (502 s at sixteen markets).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seven markets: seed rows, `MVP_PRICE_SERIES` rows, a 0 sign in `with_more_outcomes`, `load-prices` stores them~~ **done** 2026-11-04 (PR #257) | The tests below pass. On a copy of the store, `load-prices` stores the seven, the procedure above gives an empty diff, the closes check out, and the scoreboard's rebuild time is written here |
| 2 | Results here and in [MVP results](../mvp-results.md) | Each new market's *does it move?* verdict for every flow and its `follows` answers, against the expected outcome |

*Step 1, 2026-11-04 (PR #257):*
- On a copy of the store `load-prices` stored the seven: 33,521 closes, from `XLU`'s 7,009 to the
  3,804 each of wheat and soybeans, and 177,692 for the 23.
- The procedure gave an empty diff: `follows` for its four flows with and without the flag, `score`,
  and the scoreboard's whole `data.json` (every flow's `raw-move`, `surprise` and walk-forward
  cells) without the seven and the chance lines.
- Each fund's daily close, on 2026-10-29 to 11-03, is within 0.25% of its last 5-minute bar,
  15:55 to 16:00, so the 16:00 close stands.
- The scoreboard was rebuilt in 772 s alone (829 s beside a second rebuild), against 492 s at sixteen
  markets: under the 15-minute bar. The evening job's `TimeoutStartSec` goes from 20 to 40 minutes.

## How you know it is right

- `MVP_PRICE_SERIES` lists 23 markets, each a symbol in the seed, the seven after `XLE` in the order
  of the table above, and `with_more_outcomes` lists them in the same order, each at 0.
- An 08:30 New York release falls on the same day's close for each of the seven (the parametrized
  test in `tests/test_event_flows.py`).
- The tests that count sixteen markets count 23: `test_study_prices.py`, `test_study_observations.py`,
  `test_study_raw_move.py` and `test_scoreboard.py`. The other values in them are unchanged.

## What this part does not do

- No coffee, breakeven or signs (part 2). No mortgage rate: the yields already stand for it.
- No new flow or span. No shelf prices. No change to `live`.
- A fund's price is the futures it holds less its fees and roll costs, not the spot price.

## Technical details

- **`data/seed/instruments.csv`:** seven rows, `region` `us`, after `XLE`:
  - `CORN,Corn (Teucrium Corn Fund),commodity,us,NYSE Arca,Holds corn futures; bread and feed.`
  - `WEAT,Wheat (Teucrium Wheat Fund),commodity,us,NYSE Arca,Holds wheat futures; bread.`
  - `SOYB,Soybeans (Teucrium Soybean Fund),commodity,us,NYSE Arca,Holds soybean futures; cooking oil and feed.`
  - `UGA,Gasoline (United States Gasoline Fund),commodity,us,NYSE Arca,Holds RBOB gasoline futures; petrol at the pump.`
  - `UNG,Natural gas (United States Natural Gas Fund),commodity,us,NYSE Arca,Holds natural gas futures; heating.`
  - `XLU,US utilities sector ETF,sector_etf,us,NYSE Arca,Utilities Select Sector SPDR; household bills and rates.`
  - `ITB,US homebuilders ETF,sector_etf,us,Cboe BZX,iShares U.S. Home Construction; housing and mortgages.`

  `commodity`, `sector_etf` and `us` already exist in the models.
- **`study.py`:** the seven rows in `MVP_PRICE_SERIES` after `XLE`, each `PriceSeries(<ticker>,
  "pct", time(16, 0), NEW_YORK)`, and the comment above it.
- **`flows.py`:** `with_more_outcomes` gains the seven at 0, in that order, and its docstring.
- **Docs:** this spec, row 19 (amended: funds for the futures; coffee, the breakeven and signs in
  part 2), `docs/precision.md` (the roll cost, dividends), `docs/schema.md` (the seed's rows and the
  market count), the glossary (each symbol), `README.md` where it counts the markets, `docs/mvp-results.md`, `docs/status.md`; the scoreboard as rebuilt.
  `docs/legacy/data/` is not edited.
