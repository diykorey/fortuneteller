# Database schema

What every table and column in the DuckDB store means, who fills it, and whether anything fills it
yet. [`schema.sql`](../schema.sql) is the source of truth for names and types; this document is the
source of truth for meaning, including what each allowed value of a column means. **Change both
in the same commit.** Unfamiliar term? See the [Glossary](glossary.md).

The store is one DuckDB file (`data/fortuneteller.duckdb` by default, `FT_DB_PATH` to override).
`uv run fortuneteller init` creates every table; the DDL is idempotent. There is no ORM: each table
that code writes has a Pydantic model of the same shape in `src/fortuneteller/models.py`, written
through `db.insert_models` (`effect_size_matrix`, which nothing writes yet, has none).

## The tables at a glance

| Table | Kind | One row per | Filled by | Rows once loaded |
| --- | --- | --- | --- | --- |
| [`event_types`](#event_types) | Reference | Kind of market-moving event | `seed` | 31 |
| [`instruments`](#instruments) | Reference | Tradable instrument | `seed` | 13 |
| [`effect_size_seed`](#effect_size_seed) | Reference | Event type × instrument guess | `seed` | 15 |
| [`news_sources`](#news_sources) | Reference | News or data feed | `seed` | 25 |
| [`countries`](#countries) | Reference | Country | `seed` | 10 |
| [`event_instances`](#event_instances) | Fact | Real event that happened | `load-releases` (MVP step 1, rung 1) | 649 CPI + 856 NFP releases + 275 Fed decisions |
| [`daily_bars`](#daily_bars) | Fact | Instrument × trading day closing price | `load-prices` (MVP step 2) | about 58,500 |
| [`observations`](#observations) | Fact | Event × instrument reaction | `load-prices` (MVP step 2, rung 1) | 2,698 CPI + 2,785 NFP + 1,316 Fed |
| [`surprises`](#surprises) | Fact | CPI or jobs-report release × measure × expected value | `load-surprises` (MVP step 4, rung 1) | 1,287 CPI + 844 NFP |
| [`effect_size_matrix`](#effect_size_matrix) | Derived | Event type × instrument measurement | Nothing planned yet | 0 |

**Reference** tables are configuration: committed CSVs in `data/seed/`, loaded by
`uv run fortuneteller seed`, and re-loadable at any time. Most are partial exports of a Notion
workspace; [`legacy/data/`](legacy/data/README.md) says how complete each one is. **Fact** tables
hold what really happened, fetched from outside sources. The **derived** table would hold numbers
computed from the facts.

**Keys are load-bearing strings.** `event_type`, instrument `symbol` and `country` values are joined
by exact match, so `CPI / inflation surprise` and `SPY / ES` must be spelled exactly as in the seed
CSVs. No foreign key enforces this except `observations.event_id`; tests guard the MVP keys.

**Enum casing is lowercase** (`positive`, `up`, `equity_index`). The legacy DDL in
`legacy/calibration-dataset.md` capitalizes them; that DDL is not in use.

---

## event_types

The taxonomy of market-moving events. Source: `data/seed/event_types.csv`, complete (31 rows). The
MVP uses exactly one row, `CPI / inflation surprise`.

| Column | Type | Meaning |
| --- | --- | --- |
| `event_type` | TEXT, **PK** | Canonical name, e.g. `CPI / inflation surprise`. Every other table refers to event types by this exact string. |
| `tier` | SMALLINT | Importance band, 1 (systemic / black swan) to 8 (niche). **Inferred**, not authoritative. Values below. |
| `polarity` | TEXT | Whether the event is inherently good or bad for risk assets: `positive`, `negative`, or `both` (depends on the details). |

### Values

**`tier`** — how systemic the event type is. Lower is bigger.

| Value | Name | Meaning |
| --- | --- | --- |
| `1` | Systemic / Black Swan | Can move every market at once: pandemics, banking and sovereign-debt crises, major interstate war. |
| `2` | Policy & Macro | Central-bank decisions; tariffs, trade wars and sanctions. |
| `3` | Scheduled Macro Data | Data releases on a known calendar: CPI, payrolls, other macro data, housing data. CPI is here. |
| `4` | Political & Geopolitical | Elections, coups and capital controls, debt-ceiling and shutdown standoffs, geopolitical escalation and terror. |
| `5` | Commodity / Energy / Climate | OPEC+ supply decisions, natural disasters, extreme weather, carbon policy. |
| `6` | Corporate / Idiosyncratic | Single companies: earnings, M&A, scandals, leadership changes, rating actions, legal events. |
| `7` | Tech / Social / Behavioral | Technology breakthroughs, hacks, viral and meme events, stablecoin depegs, strikes and protests. |
| `8` | Niche / Lower Impact | Narrow effects: freight disruptions, NFT and collectibles events. |

**`polarity`** — the usual effect on risk assets (stocks, credit, crypto).

| Value | Meaning |
| --- | --- |
| `positive` | Good for risk assets: they usually rise. None of the 31 seed rows uses it today. |
| `negative` | Bad for risk assets: they usually fall, and safe havens (Treasuries, gold) rise. |
| `both` | Depends on the details. For CPI, a hotter-than-expected print is usually bad and a cooler one good. |

## instruments

The instruments whose prices can be measured. Source: `data/seed/instruments.csv`, a representative
13-row subset of 55. The MVP uses five: `SPY / ES`, `UST10Y / ZN`, `DXY`, `GC / XAU`, `VIX`.

| Column | Type | Meaning |
| --- | --- | --- |
| `symbol` | TEXT, **PK** | Canonical symbol, e.g. `SPY / ES` (the ETF / the future). A project key, not a data-vendor ticker. |
| `name` | TEXT | Human name, e.g. `S&P 500`. |
| `asset_class` | TEXT | One of `equity_index`, `sector_etf`, `single_stock`, `rates_bond`, `fx`, `commodity`, `crypto`, `volatility`, `credit_cds`, `prediction`, `carbon`, `freight`, `insurance_linked`. |
| `region` | TEXT | Dominant macro regime driving it: `us`, `europe`, `asia`, `em`, `global`. Rationale in [`legacy/data/region-segmentation.md`](legacy/data/region-segmentation.md). |
| `primary_venue` | TEXT | Where it mainly trades, e.g. `NYSE / Cboe / CME`. Informational. |
| `notes` | TEXT | Free text, including how it is measured (`UST10Y / ZN` is measured as yield in bps). |

### Values

**`asset_class`** — what kind of thing the instrument is.

| Value | Meaning |
| --- | --- |
| `equity_index` | A stock-market index or its ETF / future, e.g. `SPY / ES`. |
| `sector_etf` | An ETF holding one sector's stocks. No seed row uses it yet. |
| `single_stock` | One company's shares, e.g. `NVDA`. |
| `rates_bond` | A government bond, measured by its yield, e.g. `UST10Y / ZN`. |
| `fx` | A currency or currency index, e.g. `DXY`. |
| `commodity` | A raw material: gold, oil. |
| `crypto` | A cryptocurrency or stablecoin. |
| `volatility` | An index of expected volatility, e.g. `VIX`. |
| `credit_cds` | Credit default swaps: the price of insuring against a default. |
| `prediction` | A prediction-market contract. No seed row uses it yet. |
| `carbon` | Emission allowances. No seed row uses it yet. |
| `freight` | Shipping rates, e.g. the Baltic Dry Index. |
| `insurance_linked` | Catastrophe bonds and similar. No seed row uses it yet. |

**`region`** — the economic bloc whose news moves the instrument most, **not** where it is listed.
VIX is `us` because it tracks US stocks; DXY is `global`.

| Value | Meaning |
| --- | --- |
| `us` | Driven by US data and the Fed. Includes developed North America (Canada). |
| `europe` | Driven by the ECB or the Bank of England: the eurozone and the UK. |
| `asia` | Developed Asia, e.g. Japan. No seed row uses it yet. |
| `em` | Emerging markets, whatever the continent: China, India, Brazil. Checked before `asia`. |
| `global` | No single bloc dominates: gold, oil, crypto, the dollar index, freight. |

## effect_size_seed

Hand-written **guesses** at how each event type moves each instrument. Source:
`data/seed/effect_size_seed.csv`, 15 rows. **Placeholders, not measurements**: the MVP exists to
replace guesses like these with measured numbers. Nothing in the pipeline reads them for a
decision; `query-demo` prints one as a sample lookup. Key: (`event_type`, `instrument`).

| Column | Type | Meaning |
| --- | --- | --- |
| `event_type` | TEXT, **PK** | An `event_types.event_type`. |
| `instrument` | TEXT, **PK** | An `instruments.symbol`. |
| `direction` | TEXT | Expected move: `up`, `down`, `mixed`, or `conditional` (depends on the surprise sign and regime; unresolved by design). |
| `typical_magnitude` | TEXT | Guessed size as text, e.g. `0.5-1.5%` or `3-10 bps`. |
| `reaction_half_life` | TEXT | How long the move lasts: `seconds_minutes`, `minutes_hours`, `hours_days`, `days_weeks`, `weeks_plus`. |
| `direction_confidence` | TEXT | Confidence in `direction`: `high`, `medium`, `low`. |
| `hit_rate_est` | TEXT | Guessed share of times the direction is right, e.g. `~62%`. |
| `surprise_dependent` | TEXT | `yes` if the move depends on the size of the surprise. |
| `basis` | TEXT | Where the numbers come from. Today always `placeholder seed`. |

### Values

**`direction`** — which way the instrument is guessed to move when the event happens.

| Value | Meaning |
| --- | --- |
| `up` | Rises. |
| `down` | Falls. |
| `mixed` | Moves both ways across past cases with no clear pattern. No seed row uses it yet. |
| `conditional` | Up or down depending on the surprise's sign and the market regime. Turning it into a concrete direction is future work. |

**`reaction_half_life`** — how long until half of the move has faded.

| Value | Meaning |
| --- | --- |
| `seconds_minutes` | A spike, mostly gone within minutes. |
| `minutes_hours` | Fades within the trading day. |
| `hours_days` | Lasts into the next days. |
| `days_weeks` | A repricing that holds for weeks. No seed row uses it yet. |
| `weeks_plus` | Effectively permanent. No seed row uses it yet. |

**`direction_confidence`** — how sure the guess about `direction` is.

| Value | Meaning |
| --- | --- |
| `high` | The direction is well established. |
| `medium` | Usually right, with frequent exceptions. |
| `low` | Weak or disputed. No seed row uses it yet. |

**`surprise_dependent`**: `yes` — the move scales with how far the release differed from what was
expected; `no` — the event moves the instrument regardless (a war has no consensus to miss).

**`basis`**: `placeholder seed` — invented to give the table a shape, not derived from any data.
The only value today.

## news_sources

Ranked news and data feeds, for the future detection stage (roadmap rung 7). Source:
`data/seed/news_sources.csv`, complete (25 rows). Nothing in the MVP reads it.

| Column | Type | Meaning |
| --- | --- | --- |
| `rank` | INTEGER | Position in the ranking, 1 = most useful. |
| `source` | TEXT, **PK** | Name of the feed, e.g. `LSEG / Reuters (Headlines Direct)`. |
| `type` | TEXT | What kind of feed: wire, official, social, … |
| `domains_covered` | TEXT | What it reports on. |
| `speed` | TEXT | Typical latency, e.g. `us-ms / sec`. |
| `reliability` | TEXT | How far it can be trusted, e.g. `Very high`. |
| `api_access` | TEXT | Whether and how it can be read by a program. |
| `cost` | TEXT | Price band, `Free` to `$$$$`. |

### Values

These columns are short free-text labels from the Notion export, not a fixed set, so the scale is
explained rather than every variant.

- **`type`** — free text describing the feed, e.g. `Wire`, `Official`, `Social firehose`.
- **`speed`** — how soon after an event the feed reports it, fastest first: `us-ms` (microseconds
  to milliseconds), `sec`, `min`, `15-min`, `hr`, `days`. A range such as `sec-min` spans both.
  `release` means the moment an official publication appears; `(poll)` that it must be checked
  repeatedly rather than pushed. `(noisy)` marks a fast but unreliable feed.
- **`reliability`** — how often it is right, highest first: `Authoritative` (the primary source
  itself), `Very high`, `High`, `Medium-high`, `Medium`, `Low-medium`. A note in brackets limits
  it, e.g. `High (crypto)` is reliable only for crypto, `Medium (FL bias)` has a known slant.
- **`api_access`** — whether a program can read it: `Yes` (an API), `Yes (free)`,
  `Yes (institutional)` (only under an enterprise contract), `RSS/API`, `Partial`, `Mostly web`
  (a person has to read it).
- **`cost`** — price band from `Free` through `$` to `$$$$` (institutional-terminal prices). A range
  such as `$-$$` means the tiers differ.

## countries

Countries by GDP, with news coverage notes. Source: `data/seed/countries.csv`, a representative
10-row subset of 50. The MVP uses one row, `United States`, as the `event_instances.country` key.

| Column | Type | Meaning |
| --- | --- | --- |
| `rank` | INTEGER | Rank by 2026 GDP estimate. |
| `country` | TEXT, **PK** | Country name, e.g. `United States`. Joined by exact string. |
| `gdp_2026e` | TEXT | Estimated 2026 GDP in USD trillions, as text, e.g. `~30.3`. |
| `platforms_in_list` | TEXT | Trading platforms from that country in the platform list. Often empty. |
| `coverage_gap` | TEXT | Where news coverage of that country is thin. Often empty. |
| `primary_news_source` | TEXT | Main sources for that country's news. |

---

## event_instances

One row per event that actually happened: the calendar that price moves are measured against.
Today it holds every US CPI release since 1972, every jobs report (NFP) since 1955 and every Fed
rate decision (FOMC) since February 1994, loaded by
`uv run fortuneteller load-releases` ([step 1](steps/step-1-releases.md),
[rung 1](steps/rung-1-more-events.md)). Re-running overwrites rows by `event_id`, so the count does not
change.

| Column | Type | Meaning | Filled today |
| --- | --- | --- | --- |
| `event_id` | BIGINT, **PK** | Stable id: the event type's code, then the release day as `YYYYMMDD` — CPI on 2022-09-13 is `120220913` (`study.event_id`). Codes: `1` CPI, `2` NFP, `3` US central-bank decision. Unique across event types, and sorted by date within one. | Yes |
| `event_type` | TEXT | An `event_types.event_type`: `CPI / inflation surprise`, `NFP / labor data` or `Central-bank decision`. | Yes |
| `event_ts` | TIMESTAMP | When the market learned of the event: for CPI and NFP, the release day at 08:30 New York time; for a Fed decision, the time its statement came out: 14:15 New York until 2013-03-20 and 14:00 since, with the exceptions listed in `study.FOMC_ANNOUNCED_AT` (unscheduled decisions, and 12:30 on the 2011–2012 press-conference days); sources in [rung 1](steps/rung-1-more-events.md). Stored as **naive UTC**, because DuckDB would shift a time-zone-aware value into the session's time zone. | Yes |
| `country` | TEXT | A `countries.country`. Today always `United States`. | Yes |
| `detail` | TEXT | What the event is about. For CPI and NFP, the reference month as `YYYY-MM`, i.e. the month measured: about six weeks before `event_ts` for CPI, about one for NFP. When a release day first publishes two months (NFP, October and November 2025), the row is the newer month. For a Fed decision, `scheduled meeting` or `unscheduled`. | Yes |
| `scheduled` | BOOLEAN | `true` if the date was known in advance (a data release, a scheduled Fed meeting), `false` if not (an emergency Fed cut, a war, a hack). | Yes |
| `consensus` | DOUBLE | What forecasters expected before the release, from a survey. | No: no free survey history exists. Step 4's expected values are a trend and a model, so they go in [`surprises`](#surprises) instead |
| `actual` | DOUBLE | The number released, as first published, before any revision. For CPI, the index level; for NFP, total non-farm payrolls in thousands. NULL for a Fed decision: this rung measures only that it happened. | Yes, except Fed decisions |
| `surprise` | DOUBLE | `actual − consensus`: the part the market did not expect. | No; see `consensus` |
| `surprise_sd` | DOUBLE | `surprise` divided by the typical size of past surprises, so surprises of different events compare. | No; nothing planned before a second event type |
| `surprise_source` | TEXT | Where `consensus` came from. | No; see `consensus` |
| `priced_in_prior` | DOUBLE | How much the market had priced in beforehand (e.g. from options or prediction markets). | No; nothing planned |
| `vix_t0` | DOUBLE | VIX level at the event, as a measure of market nervousness. | No; nothing planned |
| `rate_regime` | TEXT | Whether the Fed was hiking, cutting, or on hold. | No; nothing planned |
| `quality` | TEXT | How trustworthy the row is. CPI and NFP rows are `first_release`: values as first printed, not revised. Fed decisions are `fed_calendar`. | Yes |

### Values

**`scheduled`**: `true` — the release date was published in advance, so the market knew when to
watch (every CPI and NFP row, and every scheduled Fed meeting); `false` — the event arrived without
warning: the 14 unscheduled Fed decisions since 1994 (e.g. 2001-09-17, 2020-03-15).

**`quality`** — how far the row can be trusted.

| Value | Meaning |
| --- | --- |
| `first_release` | `actual` is the number as first published on `event_ts`, before any later revision — the number the market actually reacted to. Every CPI and NFP row. |
| `fed_calendar` | The day comes from the Fed's own meeting calendar, cross-checked: every target-rate change since 1994 falls on a stored decision or up to 3 days after it. Every Fed row. |

**`rate_regime`** (not filled yet): intended values `hiking`, `cutting`, `on-hold`, per the legacy
design.

## daily_bars

**In plain words:** each market's closing price for every trading day. One row is one market on
one day — "the S&P 500 closed at 3,932.69 on 2022-09-13". Market jargon calls one period's price
data a *bar*; a daily bar is one day of it, and here only the closing price is kept.

It exists for two reasons. [Step 2](steps/step-2-prices.md) reads it to measure each CPI release:
it looks up the close before the announcement and the close after it, and writes the difference to
`observations`. Step 3 reads the rest of it — the ordinary days — as the baseline that tells whether
release days are unusual. Storing the prices means Yahoo is asked once and later steps read locally.
Nothing is computed here: the rows are the prices exactly as the source reported them.

Filled by `uv run fortuneteller load-prices` (through `study.load_daily_bars`). Key: (`instrument`, `day`).
Each load replaces all of an instrument's rows, so the table holds exactly what the current ticker
returned: closes from an earlier ticker for the same instrument cannot mix in.

Example rows:

| `instrument` | `day` | `close` | `source` |
| --- | --- | --- | --- |
| `SPY / ES` | 2022-09-12 | 4110.41 | `yahoo:^GSPC` |
| `SPY / ES` | 2022-09-13 | 3932.69 | `yahoo:^GSPC` |
| `UST10Y / ZN` | 2022-09-13 | 3.422 | `yahoo:^TNX` |

**How much data.** Counted from the live source on 2026-09-28, after the empty and weekend rows are
dropped. It grows by about five rows per trading day, one per instrument.

| Instrument | Rows | From |
| --- | --- | --- |
| `SPY / ES` | 14,305 | 1970-01-02 |
| `UST10Y / ZN` | 14,203 | 1970-01-02 |
| `DXY` | 14,152 | 1971-01-04 |
| `GC / XAU` | 6,544 | 2000-08-30 |
| `VIX` | 9,254 | 1990-01-02 |
| **Total** | **58,458** | |

A few megabytes in all. `observations` is these same days thinned down to the CPI release days —
about 2,700 rows.

| Column | Type | Meaning |
| --- | --- | --- |
| `instrument` | TEXT, **PK** | An `instruments.symbol`, e.g. `SPY / ES` — the project's key, not the data vendor's ticker. |
| `day` | DATE, **PK** | The trading date, **as a calendar date in the exchange's own time zone**. A DATE rather than a TIMESTAMP, so no session or machine time zone can move a price onto the neighbouring day. |
| `close` | DOUBLE | The closing value that day. A price for four instruments; for `UST10Y / ZN` it is the **yield in percent** (`3.422` means 3.422%), because bonds are measured by yield. Today's bar is never stored: while the market is open its close is not final, so the latest row is the last finished trading day. |
| `source` | TEXT | Where the value came from, as `<provider>:<vendor ticker>`, so any number can be traced back. |

### Values

**`source`** — today always `yahoo:` followed by the vendor ticker:

| Value | Instrument | What it is |
| --- | --- | --- |
| `yahoo:^GSPC` | `SPY / ES` | The S&P 500 index itself, which covers every CPI release since 1972; the SPY fund starts only in 1993 |
| `yahoo:^TNX` | `UST10Y / ZN` | The 10-year Treasury yield, in percent |
| `yahoo:DX-Y.NYB` | `DXY` | The US Dollar Index |
| `yahoo:GC=F` | `GC / XAU` | Gold futures, the contract nearest expiry. When one contract expires and the next takes over, the price can jump for reasons unrelated to any event |
| `yahoo:^VIX` | `VIX` | The Cboe Volatility Index |

## observations

One row per event × instrument: how that instrument moved around that event. Built from
`daily_bars` and `event_instances` by `study.store_observations`
([step 2](steps/step-2-prices.md)): for each stored release of every event type (CPI, NFP, Fed) and each of the five instruments, the last close before the event and the move to the first close after it. Each instrument has its
own close time (`study.MVP_PRICE_SERIES`): an event at or after it, such as a 14:00 Fed decision for
gold, which settles at 13:30, reacts at the next day's close (`study.first_reaction_day`). CPI and
NFP at 08:30 come before every close. No row when either close is more than 4 calendar days from the release, or the release
predates the instrument's history. Every run rebuilds the whole table in one transaction — deletes them and inserts
what it measured — so the table always matches that run, with no rows left from earlier rules or data.
A run stops with an error if an instrument has no `daily_bars` at all, rather than counting every
release as before its history.

About 2,698 rows (checked 2026-09-28): 649 each for `SPY / ES` and `DXY`, 648 for `UST10Y / ZN`
(the May 1978 release has no close within 4 days before it), 312 for `GC / XAU` (from 2000), 440 for
`VIX` (from 1990). On 2026-10-05, NFP adds 2,785 rows and Fed decisions 1,316: 274 for each
instrument but gold (220, from 2000). The one Fed decision without a row is 2001-09-17, the cut
announced as markets reopened after a week closed.

The horizon columns come from the pre-reset design, which planned intraday data; the MVP has only
daily prices, so the intraday ones stay empty.

| Column | Type | Meaning | Filled today |
| --- | --- | --- | --- |
| `event_id` | BIGINT, **PK** | The `event_instances.event_id` it reacts to (a foreign key). | Yes |
| `instrument` | TEXT, **PK** | An `instruments.symbol`. One row per event and instrument. | Yes |
| `px_t0` | DOUBLE | Price (or yield) just before the event: the last close before the event, the starting point the returns are measured from. | Yes |
| `ret_unit` | TEXT | Unit of the `ret_*` columns: `pct` (relative change, `0.01` = 1%) for prices, `bps` (basis points, `(yield₁ − yield₀) × 100`) for yields. Values in different units must never be averaged together. | Yes |
| `ret_5m` | DOUBLE | Move over 5 minutes after the event. Needs intraday data. | No; not in the MVP |
| `ret_1h` | DOUBLE | Move over 1 hour after the event. Needs intraday data. | No; not in the MVP |
| `ret_1d` | DOUBLE | Move from the last close before the release date to the first close on or after it, in `ret_unit`. On 2022-09-13: `−0.0432` for `SPY / ES`, `6.0` for `UST10Y / ZN`. | Yes |
| `ret_1w` | DOUBLE | Move over about a week after the event. | No; nothing planned |
| `abn_ret_1d` | DOUBLE | `ret_1d` minus what the instrument would normally have done that day: the part attributable to the event. | No; nothing planned |
| `car` | DOUBLE | Cumulative abnormal return: abnormal moves summed over several days around the event. | No; nothing planned |
| `peak_move` | DOUBLE | Largest move reached after the event. Needs intraday data. | No; not in the MVP |
| `half_life_min` | DOUBLE | Minutes until half of `peak_move` was given back. Needs intraday data. | No; not in the MVP |
| `realized_dir` | TEXT | Direction the instrument actually moved. | No; nothing planned |
| `data_source` | TEXT | Where the prices came from. | Yes |
| `quality` | TEXT | How the move was measured. | Yes |

### Values

**`ret_unit`** — the unit of every `ret_*` column in the row.

| Value | Meaning |
| --- | --- |
| `pct` | Relative change: `price₁ / price₀ − 1`, so `0.01` is a 1% rise. For prices and index levels. |
| `bps` | Basis points of yield: `(yield₁ − yield₀) × 100`, so 4.20% → 4.30% is `10`. For bonds, which are measured by yield. |

**`realized_dir`** (not filled yet): intended values `up`, `down`, `flat`, per the legacy design.

**`data_source`** — where the prices behind the row came from.

| Value | Meaning |
| --- | --- |
| `yahoo` | Daily closes from Yahoo Finance, via `daily_bars` (whose `source` names the exact ticker). |

**`quality`** — how the move was measured.

| Value | Meaning |
| --- | --- |
| `daily_close` | From daily closing prices, not intraday data: the move includes everything else that happened that day, not only the release. |

## surprises

**In plain words:** for every CPI release and jobs report, how far the number landed from what was expected. One
row is one release, one CPI measure and one way of saying what was expected — "in August 2022
(released 2022-09-13), core CPI rose 0.57% against a nowcast of 0.48%: a surprise of +0.09 percentage points".

It exists because the market moves on the part of a release it did not expect.
[Step 4](steps/step-4-surprise.md) pairs each surprise with that release's move in `observations`
and asks whether bigger surprises bring bigger moves. There is no free history of what forecasters
expected, so each release gets two expected values, and step 4 compares the answers they give.

Filled by `uv run fortuneteller load-surprises` (step 4, and rung 1 for payrolls). Key:
(`event_id`, `measure`, `baseline`). 1,287 CPI rows on 2026-10-05: against the 12-month trend, core
342 (from 1998) and headline 635 (from 1973); against the nowcast, 155 each (from 2013). 844
payroll rows on 2026-10-06, against the trend only (from 1956): every stored jobs report but the
first twelve.

Example row:

| `event_id` | `measure` | `baseline` | `actual_mom` | `expected_mom` | `surprise` |
| --- | --- | --- | --- | --- | --- |
| 120220913 | `core` | `nowcast` | 0.567 | 0.480 | 0.087 |

| Column | Type | Meaning |
| --- | --- | --- |
| `event_id` | BIGINT, **PK** | The release, an `event_instances.event_id`. Core and headline come out in the same BLS release, so they share it. |
| `measure` | TEXT, **PK** | Which CPI number; see below. |
| `baseline` | TEXT, **PK** | Where the expected value came from; see below. |
| `actual_mom` | DOUBLE | The month-over-month change **as first published**: for CPI in percent (`0.567` means +0.567%); for `payrolls` in thousands of jobs (`315` means +315,000). The number the market saw, not today's revised one. |
| `expected_mom` | DOUBLE | What `baseline` expected that change to be, in the same unit. |
| `surprise` | DOUBLE | `actual_mom − expected_mom`: percentage points for CPI, thousands of jobs for payrolls. Positive means hotter or stronger than expected. |

### Values

**`measure`** — which CPI number the row is about:

| Value | Meaning |
| --- | --- |
| `core` | CPI without food and energy (FRED `CPILFESL`). Step 4's verdicts are about this one: markets have traded core since the 2000s. First-published history starts in 1997. |
| `headline` | All items (FRED `CPIAUCSL`), the series `event_instances.actual` holds. Shown as context, without a verdict. |
| `payrolls` | The jobs report's monthly change in total non-farm payrolls (FRED `PAYEMS`), in thousands: the month's first level minus the previous month's level as revised that same day. Only with `trend_12m`. |

**`baseline`** — what "expected" means:

| Value | Meaning |
| --- | --- |
| `trend_12m` | The average of the previous 12 months' first-published changes, counting only those published before the release day. Available for every release once a year of history exists, but it measures surprise against the trend, not against what the market expected. |
| `nowcast` | The Cleveland Fed's model estimate, the last one published before the release day. Close to what the market saw, but only from 2013. |

## effect_size_matrix

The measured counterpart of `effect_size_seed`: one row per event type × instrument, computed from
`observations`. Created but empty. The MVP steps print their measurements, and none is planned to
write here yet. Key: (`event_type`, `instrument`).

| Column | Type | Meaning |
| --- | --- | --- |
| `event_type` | TEXT, **PK** | An `event_types.event_type`. |
| `instrument` | TEXT, **PK** | An `instruments.symbol`. |
| `direction` | TEXT | Measured typical direction. |
| `mag_per_sd` | DOUBLE | Typical move per one standard deviation of surprise. |
| `mag_ci_low` | DOUBLE | Lower end of the confidence interval for `mag_per_sd`. |
| `mag_ci_high` | DOUBLE | Upper end of the confidence interval for `mag_per_sd`. |
| `median_half_life` | TEXT | Typical duration of the move, in the `reaction_half_life` buckets. |
| `hit_rate` | DOUBLE | Share of events where the instrument moved in `direction`. |
| `n_obs` | INTEGER | Number of observations behind the row. A number with a small `n` means little. |
| `surprise_dep` | TEXT | Whether the move depends on the size of the surprise. |
| `last_calibrated` | TIMESTAMP | When the row was last computed. |

### Values

Nothing fills this table yet. When something does, `direction` and `median_half_life` take the same
values as `effect_size_seed.direction` and `effect_size_seed.reaction_half_life` above, and
`surprise_dep` the same `yes` / `no` as `effect_size_seed.surprise_dependent`.

