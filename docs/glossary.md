# Glossary

Every acronym, ticker, and piece of jargon this project uses. If a term appears in a FortuneTeller
document and is not obvious from plain English, it belongs here.

Terms are grouped by what they are about, alphabetical within each group.

**Sections:** [The product](#the-product) · [Economic releases](#economic-releases-the-events) ·
[Instruments & markets](#instruments--markets) · [Measuring the effect](#measuring-the-effect) ·
[Confidence & calibration](#confidence--calibration) · [Data sources](#data-sources) ·
[Codebase & toolchain](#codebase--toolchain) · [Project shorthand](#project-shorthand)

---

## The product

- **Corroboration** — confirming a fast-but-unreliable report against slower, more reliable sources
  before acting on it. Prevents trading a rumour.
- **Detection** — the noisy front half of the pipeline: noticing that an event happened at all, from
  news, wires, or feeds. Hardest part of the system; deliberately last on the roadmap.
- **Entity linking** — deciding *which* instruments and countries a piece of text is actually about
  ("Apple supplier fire" → `AAPL`). Turns prose into rows the predictor can use.
- **Event** — something that happens in the world which may move markets: a data release, a
  decision, a disaster, a headline.
- **Event type** — the category an event belongs to (`CPI / inflation surprise`, `war / conflict
  escalation`, …). The reference taxonomy holds 31 of them; the MVP uses exactly one.
- **HFT** (High-Frequency Trading) — trading strategies competing on microseconds. **This project is
  explicitly not that**: the latency budget is seconds to minutes, because the product is a warning,
  not an execution engine.
- **Instrument** — a tradable thing whose price we measure: an index, a currency, a bond yield, a
  commodity, a coin.
- **Latency budget** — how long the system may take between event and warning. Seconds to minutes
  here, which is why a single process is enough and streaming infrastructure is not needed.
- **Polarity** — whether an event type is inherently good, bad, or context-dependent for risk
  assets (`positive`, `negative`, `both`).
- **Prediction** — the system's statement about what an instrument will do: direction, magnitude,
  horizon, confidence.
- **Scheduled vs unscheduled** — a scheduled event has a known date and a published expectation
  (CPI, a Fed meeting); an unscheduled one does not (an invasion, a hack). Scheduled events are
  measurable first, which is why the MVP uses one.
- **Tier** — a rough importance ranking of an event type, used to prioritise attention.
- **Warning** — the user-facing output: "CPI printed hot; expect SPY down 0.5–1.5% over minutes to
  hours, confidence medium."

## Economic releases (the events)

- **Actual** — the number a release actually printed.
- **Consensus** — what forecasters collectively expected the release to be, published in advance by
  economic calendars. The reference point that makes "surprise" meaningful, and the **scarcest free
  data in this project** — actuals are easy, history of expectations is not.
- **Core vs headline** — *headline* includes food and energy prices; *core* strips them out because
  they are volatile. Markets usually react more to core.
- **CPI** (Consumer Price Index) — the main US inflation measure, published monthly by the
  **BLS**, usually 8:30 a.m. New York time. The MVP's single event type: frequent, scheduled,
  heavily forecast, and reliably market-moving.
- **Fed / FOMC** (Federal Open Market Committee) — the committee that sets the US policy interest
  rate, meeting eight times a year with a decision at 2:00 p.m. New York time.
- **GDP** (Gross Domestic Product) — total economic output; a quarterly growth release.
- **Initial release / first print** — the value a statistical agency publishes the first time,
  before later revisions. The only version the market could have reacted to on the day, so it is the
  version this project measures against.
- **MoM / YoY** (month-over-month / year-over-year) — whether a change is measured against last
  month or the same month a year ago. Mixing the two silently corrupts a surprise calculation.
- **NFP** (Non-Farm Payrolls) — the monthly US jobs report, usually the first Friday, 8:30 a.m. New
  York time. Traditionally the biggest scheduled mover after CPI and the Fed.
- **PMI** (Purchasing Managers' Index) — a survey-based activity gauge where above 50 means
  expansion, below 50 contraction.
- **Reference month** — the month a release *measures*, as opposed to the day it is *published*.
  August CPI has an August reference month and a mid-September release date. Confusing the two is
  the classic way to measure the wrong days.
- **Release calendar** — the published schedule of when economic data comes out. Needed to know
  which days to measure.
- **Revision** — a later correction to an already-published figure. Real, but invisible to the
  market on release day; see **initial release**.
- **Seasonal adjustment (SA)** — smoothing out predictable within-year patterns so months are
  comparable. `CPIAUCSL` is the seasonally adjusted headline series.
- **Surprise** — `actual − expected`. The thing that actually moves prices: the expected part is
  already in the price before the release.
- **Surprise_sd / standardized surprise** — the surprise divided by how big surprises usually are
  for that release (its standard deviation). Makes a CPI miss and a payrolls miss comparable on one
  scale. `"unknown"` when there is too little history to standardize.

## Instruments & markets

- **Asset class** — the family an instrument belongs to: equity index, single stock, rates/bond, FX,
  commodity, crypto, volatility, credit, freight.
- **BDI** (Baltic Dry Index) — cost of shipping dry bulk cargo; a gauge of global trade demand.
- **Basis point** (bp, "bip") — one hundredth of a percent (0.01%). Bond and rate moves are quoted
  in bps: "10Y up 8 bps" means the yield rose 0.08 percentage points.
- **BRN** (Brent crude) — the global oil price benchmark, traded on ICE.
- **BTC** (Bitcoin) — the crypto bellwether.
- **BUND / FGBL** — the German 10-year government bond and its futures contract (Eurex); the
  eurozone's risk-free benchmark. Free price history is awkward, which is why the MVP uses the US
  10-year instead.
- **CDS** (Credit Default Swap) — insurance against a borrower defaulting; its price is a direct
  read on perceived default risk.
- **DXY** (US Dollar Index) — the dollar measured against a basket of major currencies (mostly the
  euro). Rises on risk-off and on hawkish Fed expectations.
- **ES** (E-mini S&P 500 future) — the futures contract on the S&P 500, which trades nearly around
  the clock and therefore reacts to releases outside US stock-market hours.
- **FX** (Foreign Exchange) — the currency market.
- **Gold / XAU / GC** — gold; `XAU` is its currency-style code, `GC` its COMEX futures symbol. A
  haven asset, sensitive to real interest rates.
- **Liquidity** — how easily something can be traded without moving its own price. The MVP sticks to
  highly liquid instruments so measured moves reflect the event, not thin trading.
- **Rates** — the government-bond / interest-rate market. Note the inversion: when bond **prices**
  rise, **yields** fall.
- **Risk-on / risk-off** — the market mood. Risk-on: money into stocks and commodities. Risk-off:
  money into dollars, gold, Treasuries, and volatility spikes.
- **S&P 500** — the index of 500 large US companies; the default "the market" benchmark.
- **SPY** — the largest ETF tracking the S&P 500; a cheap, free-data stand-in for the index.
- **Stablecoin depeg** — a coin meant to hold a fixed value (USDC at $1) trading away from it. A
  systemic-stress signal.
- **Ticker / symbol** — the short code identifying an instrument (`SPY`, `^VIX`). **These strings
  are load-bearing here** — they are join keys between seed data, measurements, and predictions, so
  drift silently breaks lookups.
- **UST 10Y** (US Treasury 10-year) — the 10-year US government bond yield; the world's benchmark
  interest rate and the most direct read on an inflation release.
- **VIX** — the Cboe Volatility Index, the market's expected S&P 500 volatility over the next 30
  days, derived from option prices. The "fear gauge": spikes on shocks.
- **^TNX** — Yahoo Finance's symbol for the US 10-year yield. Check its scaling convention against a
  known value the first time you load it.

## Measuring the effect

- **Abnormal return** — the part of a move that is *not* explained by the instrument's ordinary
  behaviour: actual return minus expected return. The honest way to say "the event caused this".
- **Baseline** — the ordinary behaviour an abnormal return is measured against: a typical day, or a
  simple model of one.
- **CAR** (Cumulative Abnormal Return) — abnormal returns added up across an event window, to
  capture a move that builds over hours rather than landing at once.
- **Daily bar / OHLC** — one row per trading day holding Open, High, Low, Close prices. The MVP's
  data resolution; enough to prove an effect exists.
- **Effect size** — how much an instrument moves per unit of event, the core number the whole system
  is built to estimate. Here: **`mag_per_sd`**, percent moved per one standard deviation of
  surprise.
- **Event study** — the standard finance method behind the MVP: take many past occurrences of the
  same event, measure returns in a window around each, and ask whether the average is distinguishable
  from a normal day.
- **Event window** — the stretch of time around an event over which the move is measured (the first
  hour, the day, the week).
- **Half-life** — how long until a move decays halfway back. Distinguishes a lasting repricing from
  a spike that round-trips in minutes.
- **Hit rate** — the fraction of past occurrences where the predicted direction was correct. 50% is
  a coin flip and therefore worthless.
- **n / n_obs** — how many observations a number is based on. **Always shown next to any estimate
  here**: an effect size from n=4 is a story, not a measurement.
- **Return** — the percentage price change over a period.
- **Standard deviation (SD)** — the typical size of variation in a series. Used both to standardize
  surprises and to judge whether a move is unusual.
- **Tick data** — every individual trade and quote, the highest-resolution (and most expensive)
  market data. Deliberately deferred: daily bars can prove the loop.

## Confidence & calibration

- **Backtest** — replaying the system over history to see how it would have performed, under strict
  rules against peeking.
- **Brier score** — the accuracy score for probabilistic forecasts: the mean squared gap between
  the probability said and what happened (0 is perfect).
- **Calibration** — making stated confidence match reality: of everything called "70% likely", about
  70% should actually occur. The project's central promise.
- **Conformal prediction** — a method producing ranges with a guaranteed hit-rate ("this move will
  land in this band 90% of the time") without assuming a distribution shape.
- **ECE** (Expected Calibration Error) — a single number summarizing how far stated probabilities
  drift from observed frequencies.
- **Gate** — the rule that keeps a cell silent until its numbers are good enough (enough
  observations, passing calibration). Prevents confident nonsense from reaching a reader.
- **Isotonic regression** — a calibration method that fits a flexible, always-increasing curve from
  raw scores to true probabilities. Needs more data than Platt scaling.
- **Look-ahead bias** — accidentally using information that was not available at prediction time.
  The classic way a backtest produces results that evaporate in live use.
- **Magnitude band / prediction interval** — the range a move is expected to fall in, rather than a
  single number.
- **Overfitting** — tuning to the quirks of past data so well that the result does not generalize.
- **Platt scaling** — a simple calibration method mapping raw scores to probabilities with a
  logistic curve.
- **Regime** — the prevailing market state (calm vs panicked, rate-hiking vs rate-cutting). The same
  event can move markets in opposite directions in different regimes — the "good news is bad news"
  effect.
- **Reliability diagram** — the plot of predicted probability against observed frequency. A
  perfectly calibrated system sits on the diagonal.

## Data sources

- **BLS** (Bureau of Labor Statistics) — the US agency that publishes CPI and Non-Farm Payrolls.
- **CPIAUCSL** — the **FRED series ID** for seasonally adjusted headline US CPI. The MVP's source
  for actuals.
- **Economic calendar** — a commercial listing of upcoming releases with forecasts. The usual source
  of **consensus**, and rarely free for long histories.
- **FRED** (Federal Reserve Economic Data) — the St. Louis Fed's free database and API of economic
  series, including CPI. Free, keyed, reliable; carries actuals but not market expectations.
- **GDELT** — a free global database of news events. A detection-stage source, deferred.
- **Series ID** — a data provider's unique code for one time series (e.g. `CPIAUCSL`). Load-bearing
  the way instrument symbols are: the wrong ID silently fetches the wrong data.
- **Stooq** — a free source of historical price data; a fallback when others rate-limit.
- **Vintage** — a snapshot of what a series looked like on a given past date, before revisions.
  FRED retains vintages, which is how the **initial release** and its publication date are
  recoverable.
- **yfinance** — a Python library pulling free price history from Yahoo Finance. Convenient and
  unofficial: fine for research, not something to depend on in production.

## Codebase & toolchain

- **CLI** (Command-Line Interface) — the project's only surface: `fortuneteller <subcommand>`.
- **DDL** (Data Definition Language) — the SQL that defines tables. Kept as plain SQL in
  `schema.sql` so moving to another database later stays cheap.
- **Determinism** — same inputs, same outputs, every time: no clock reads, no randomness, no
  network. What makes results reproducible and testable.
- **DuckDB** — an embedded analytical database: one file, no server, fast at exactly the
  column-crunching this project does. The store for the whole MVP.
- **Golden file** — a committed copy of expected output that a test compares against byte for byte.
- **mypy** — the static type checker, run in `--strict` mode here.
- **ORM** (Object-Relational Mapper) — a library that hides SQL behind objects. **Deliberately not
  used**: Pydantic models plus plain parameterized SQL keep the data layer obvious.
- **Pydantic** — the library that validates data against typed models, so malformed rows fail loudly
  at the edge instead of silently later.
- **pytest** — the test runner. Tests use `# given` / `# when` / `# then` comments.
- **ruff** — the linter and formatter (100-character lines).
- **Schema** — the table definitions in `schema.sql`, executed by `init`.
- **Seed data / seed CSV** — the committed reference tables in `data/seed/` that the pipeline reads
  as configuration: event types, instruments, starting effect-size guesses. Tuning happens by editing
  data, not code.
- **uv** — the Python package and environment manager used for every command (`uv run …`).

## Project shorthand

- **`effect_size_matrix`** — the table of **measured** effect sizes, written by calibration. Empty
  until the MVP fills it.
- **`effect_size_seed`** — the table of **guessed** effect sizes shipped as seed data. Illustrative
  placeholders, explicitly not ground truth; the MVP exists to replace them with measurements.
- **`event_instances`** — one row per occurrence of an event: when it happened, what printed, what
  the surprise was. MVP step 1 fills it.
- **Episode** (legacy) — a JSON file describing a pre-detected event, fed to the replay harness.
  Appears in legacy docs only.
- **Feature ladder** — the ordered list of what gets built after the MVP, in
  [the roadmap](roadmap.md).
- **Legacy docs** — everything under [`docs/legacy/`](legacy/README.md): the pre-reset design
  corpus, kept for reference, not authoritative.
- **M0 … M7** — the superseded milestone scheme from the old roadmap. **M0 (the data spine) shipped
  and is real**; M1–M7 describe a plan that has been replaced by the MVP and the feature ladder.
- **`main_05082026`** — the branch preserving the implementation discarded in the reset.
- **MVP** (Minimum Viable Product) — here, specifically: the measured answer to *does the edge
  exist*, defined in [the roadmap](roadmap.md). Not a shipped product.
- **`observations`** — one row per event per instrument: the prices and returns around that event.
  MVP step 2 fills it.
- **Provable core** — the scope discipline of calibrating one narrow slice (one event type × five
  liquid instruments) before widening to anything else.
- **Replay harness** (legacy) — the discarded mechanism for running canned events through the
  prediction core. Appears in legacy docs; not part of the current plan.
- **The reset** — 2026-08-05, when `main` was rolled back to the M0 spine because the
  implementation had become over-engineered for the stage. Recorded in [CLAUDE.md](../CLAUDE.md).
- **The spine** — the M0 data layer: models, schema, store, seed loader, CLI. Shipped.
