# MVP step 2 — Prices

> Step 2 of the four in the [Roadmap](../roadmap.md); this document follows the step template in the
> [Legend](../legend.md). Unfamiliar acronym or term? See the [Glossary](../glossary.md). Tables and
> columns are described in the [Schema](../schema.md).

## The goal

**In plain words:** for every CPI announcement, write down how much each of five markets moved that
day.

Step 1 produced the calendar: 649 days on which US inflation was announced. This step fetches the
daily price history of five markets — US stocks (the S&P 500), the 10-year US Treasury yield, the
dollar index, gold, and the VIX fear gauge — and, for each announcement, records the move from the
last close before it to the first close after it. When it runs it prints how many moves it recorded
per market and in total, e.g. `5 instruments × 649 releases = 2698 observations`.

The whole project asks whether markets react to these announcements predictably. This step does not
answer that; it produces the raw numbers that step 3 compares against ordinary days and step 4
relates to the surprise. **If a move is attached to the wrong day, steps 3 and 4 still run and still
print numbers — they are just measuring noise.** As in step 1, the expensive failure is a silent
wrong answer, and the one thing to get right is the date.

In full: `daily_bars` holds every daily close of the five instruments, and `observations` holds one
row per release × instrument: **the close before the release, and the move to the first close after
it.** Nothing derived beyond that, nothing predicted, nothing scored.

## The way to reach it

Two obstacles, both about dates.

**Which two closes.** CPI is published at 08:30 New York time, before any of these five markets
closes that day. So the reaction is the close of the last trading day **before** the release date
(`t0`) to the close of the first trading day **on or after** it (`t1`). "On or after" matters: CPI
has been released on a Sunday (1992-12-13), and then the first reaction is Monday's close. Opening
prices are no use here — Yahoo's history before the 1990s records only closes, with the open copied
from the close.

**Which calendar date a bar belongs to.** Yahoo stamps each daily bar with a moment in time, not a
date, and the moment differs per ticker: 13:30 UTC for the S&P 500, 04:00 UTC (midnight New York)
for the dollar index and gold. Reading that moment as a date in UTC or in the machine's own time
zone gives the right answer on some machines and shifts every bar by a day on others — on a machine
set to US Pacific time, 04:00 UTC is the previous evening. So the date is always read in **the
exchange's time zone, which Yahoo reports in every response.**

Keep the daily closes, not only the release-day moves: step 3 needs every ordinary day's move to
compare against, and should read them from the database rather than fetch again.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | Add `daily_bars` to `schema.sql` and `docs/schema.md` | `init` creates it; the schema doc describes it |
| 2 | Fetch one Yahoo ticker and parse it into dated closes | Dates come from the exchange's time zone; empty and weekend rows are dropped |
| 3 | Store the closes of all five tickers in `daily_bars` | Re-running changes no row count |
| 4 | Build `observations` from `daily_bars` and `event_instances` | Before/after rule, units, and skips as specified below |
| 5 | `uv run fortuneteller load-prices` prints the counts | Per-instrument counts and `5 instruments × N releases = M observations` |

## How you know it is right

Not "it ran without error". Five checks, each able to fail:

- **A known day.** CPI for August 2022, released 2022-09-13, came in hot and the S&P 500 fell
  **4.32%** — its worst day in two years. That observation must read `ret_1d ≈ −0.0432`. A value
  near zero means the closes are a day off.
- **Cross-check the yield against FRED.** On release days, the `^TNX` move must match the move in
  FRED's `DGS10` to within **10 bps** on every release. On 2026-09-25, across 648 releases, the
  difference had a median of 0.2 bp, a 95th percentile of 2.1 bp and a maximum of 6.6 bp; the
  levels themselves are identical before 1990.
- **Release days look like trading days.** The median absolute S&P move on release days must be
  about half a percent — 0.55% on 2026-09-25, against 0.52% on all days since 1972 — and no release
  day may show a move of exactly zero. A median near zero, or several times larger, means the join
  is broken. Whether release days move *more* than other days is step 3's question, not this one.
- **Re-run the command.** The row counts of `daily_bars` and `observations` must not change.
- **Coverage matches history.** No gold observation before 2000, no VIX observation before 1990.
  Anything there is a mapping bug. Expected on 2026-09-25:

  | Instrument | Observations | Skipped |
  | --- | --- | --- |
  | `SPY / ES` | 649 | 0 |
  | `UST10Y / ZN` | 648 | 1: `1978-04`, see below |
  | `DXY` | 649 | 0 |
  | `GC / XAU` | 312 | 337 before its history starts |
  | `VIX` | 440 | 209 before its history starts |
  | **Total** | **2698** | |

## What this step does not do

No intraday prices, so no `ret_5m`, `ret_1h`, `peak_move` or `half_life_min`. No `ret_1w`, no
abnormal return, no comparison with ordinary days (step 3), no surprise (step 4). No refresh on a
schedule. No instrument beyond the five. `observations` columns not named below stay `NULL`.

## Technical details

**Source.** Yahoo Finance's chart API, one request per ticker:
`https://query1.finance.yahoo.com/v8/finance/chart/<ticker>?period1=0&period2=9999999999&interval=1d`.
Stdlib `urllib.request`, no new dependency. A browser-like `User-Agent` header is required. No key.
Yahoo is unofficial: fine for research, and the FRED cross-check above is what keeps it honest.
(Stooq, the other free source considered, now sits behind a JavaScript bot check and cannot be read
by a program.)

**The five tickers**, one constant in `study.py`:

| Instrument | Ticker | Unit | History from | Note |
| --- | --- | --- | --- | --- |
| `SPY / ES` | `^GSPC` | `pct` | 1970 | The S&P 500 index, not the SPY fund (1993+); same move on the day |
| `UST10Y / ZN` | `^TNX` | `bps` | 1970 | The 10-year yield in percent, e.g. `4.2` |
| `DXY` | `DX-Y.NYB` | `pct` | 1971 | |
| `GC / XAU` | `GC=F` | `pct` | 2000 | Front-month futures; see quirks |
| `VIX` | `^VIX` | `pct` | 1990 | |

**Parsing.** The response carries parallel arrays `timestamp` and `indicators.quote[0].close`, and
`meta.exchangeTimezoneName`. Each bar's date is `datetime.fromtimestamp(ts, ZoneInfo(<that zone>))
.date()`. Drop a bar whose close is `null`, or whose date is a Saturday or Sunday.

**`daily_bars`** — new table:

| Column | Type | Value |
| --- | --- | --- |
| `instrument` | TEXT, **PK** | The `instruments.symbol`, e.g. `SPY / ES` |
| `day` | DATE, **PK** | Trading date in the exchange's time zone |
| `close` | DOUBLE | Closing price; for `UST10Y / ZN`, the yield in percent |
| `source` | TEXT | `yahoo:<ticker>`, e.g. `yahoo:^GSPC` |

A DATE, not a TIMESTAMP, so the session-time-zone shift found in step 1 cannot apply.

**Observations.** For each `event_instances` row × each of the five instruments, with `d` the
release date (`event_ts` converted back to New York time):

- `t0` = the latest bar with `day < d`; `t1` = the earliest bar with `day ≥ d`.
- No row when `t0` or `t1` is missing, or either is more than **4 calendar days** from `d`. The
  limit admits a release after a long weekend (Friday → Tuesday) and rejects a real hole in the
  data. Skips are counted per instrument and printed.
- `pct`: `ret_1d = close(t1) / close(t0) − 1`. `bps`: `ret_1d = (close(t1) − close(t0)) × 100`.

| Column | Value |
| --- | --- |
| `obs_id` | `event_id × 10 + position of the instrument in the table above` (0–4), e.g. `2026082` for DXY and August 2026. Unique only while `event_id` is; same caveat as in step 1 |
| `event_id` | The `event_instances.event_id` |
| `instrument` | The `instruments.symbol` |
| `px_t0` | `close(t0)` |
| `ret_unit` | `pct` or `bps`, per the table above |
| `ret_1d` | As above |
| `data_source` | `yahoo` |
| `quality` | `daily_close` — measured from daily closes, not intraday; add it to the schema doc's values |
| everything else | `NULL` |

Both tables are written with `insert_models(replace=True)`, so a re-run overwrites by key.

**Data quirks, all verified present on 2026-09-25.**

| Quirk | Handling |
| --- | --- |
| Pre-1990s bars have `open == close` for `^TNX`, `DX-Y.NYB` and early `^VIX` | Use closes only |
| 3,119 `DX-Y.NYB` bars have a `null` close; smaller numbers in the others | Drop them |
| 2,907 `DX-Y.NYB` bars fall on weekends | Drop them; a weekend "close" is not a trading price and would give the Sunday 1992-12-13 release a fake `t1` |
| `^TNX` has no bar for Tuesday 1978-05-30, the day after Memorial Day | The `1978-04` release (Wednesday 1978-05-31) has `t0` five days back: skipped, and reported. FRED's `DGS10` has the same hole |
| `GC=F` is a continuous front-month futures series | When one contract expires and the next takes over, the price can jump for reasons unrelated to CPI. Accepted and named here; rare on any given release day |
| Two CPI prints share the release date 2025-12-18 | They get identical moves. Step 3 must count a trading day once, as step 1 already notes |

**Order of operations.** `load-prices` needs `event_instances` to be loaded; if it is empty, it
stops with a message to run `load-releases` first. `observations.event_id` is a foreign key, so the
order is also enforced by the database.

**Where the code goes.** `src/fortuneteller/study.py`, next to the step 1 code. No new file, no new
package.

**Tests.** A small saved Yahoo response per behaviour, trimmed from real responses. The network stays
out of the gate. Covered:

- the date is read in the exchange's time zone — a bar stamped 04:00 UTC lands on the same New
  York date, with the process time zone set to US Pacific
- `null`-close and weekend bars are dropped
- the before/after rule: a weekday release uses the previous trading day → the same day; a Sunday
  release uses Friday → Monday
- more than 4 days to the nearest close skips and counts
- `pct` versus `bps`
- an instrument with no history at a release gets no row
- re-running changes no row count, and `daily_bars.day` round-trips under a non-UTC DuckDB session
- the command's output, and its message when `event_instances` is empty

**CLI.** `uv run fortuneteller load-prices`. Output shape:

```
SPY / ES     649 observations
UST10Y / ZN  648 observations, 1 skipped (no close within 4 days)
DXY          649 observations
GC / XAU     312 observations, 337 skipped (before its history)
VIX          440 observations, 209 skipped (before its history)
5 instruments × 649 releases = 2698 observations
```
