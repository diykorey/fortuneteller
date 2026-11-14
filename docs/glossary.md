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
- **Prediction** — the system's statement about what a market will do. Today it is a direction
  only, for a link that holds walk-forward, printed with its record as counts and its band; never
  a probability until one proves honest ([the record, not a probability](steps/record-not-probability.md)).
- **Scheduled vs unscheduled** — a scheduled event has a known date and a published expectation
  (CPI, a Fed meeting); an unscheduled one does not (an invasion, a hack). Scheduled events are
  measurable first, which is why the MVP uses one.
- **Tier** — a rough importance ranking of an event type, used to prioritise attention.
- **Warning** — the user-facing output: today a call on release day (a market's direction, its
  walk-forward record as counts and its band), delivered as a popup and on the scoreboard, or a
  span's answer after a kind of event (*up*, *down*, *about the same*, *can't say*, with the
  counts).

## Economic releases (the events)

- **Actual** — the number a release actually printed.
- **ADP** (ADP National Employment Report) — a private payroll processor's monthly count of
  private-sector jobs, published two days before the jobs report and watched as a preview of it.
  Changed method in 2022 after a three-month pause; FRED has each method as its own series.
- **Consensus** — what forecasters collectively expected the release to be, published in advance by
  economic calendars. The reference point that makes "surprise" meaningful, and the **scarcest free
  data in this project** — actuals are easy, history of expectations is not. The free stand-in used
  is Nasdaq's calendar consensus ([free consensus](steps/free-consensus.md)).
- **Core vs headline** — *headline* includes food and energy prices; *core* strips them out because
  they are volatile. Markets usually react more to core.
- **CPI** (Consumer Price Index) — the main US inflation measure, published monthly by the
  **BLS**, usually 8:30 a.m. New York time. The MVP's single event type: frequent, scheduled,
  heavily forecast, and reliably market-moving.
- **ECB** (European Central Bank) — sets the euro area's interest rates; its Governing Council
  decides eight times a year (monthly until 2015). Its decisions are the first non-US event
  ([ECB decisions](steps/ecb-decisions.md)). **Euro area** — the countries that use the euro.
  **Deposit facility rate** — what the ECB pays banks on overnight deposits, the rate it has steered
  by since its rates went negative; **main refinancing rate** — what it charges on its weekly loans.
  A decision's kind is read from the first where the calendar lists it, from 2015-12-03
  ([what follows an ECB decision](steps/what-follows-ecb.md)).
- **Fed / FOMC** (Federal Open Market Committee) — the committee that sets the US policy interest
  rate, meeting eight times a year with a decision at 2:00 p.m. New York time.
- **Flash estimate** — Eurostat's first print of the month's euro-area inflation, around the first
  working day of the next month at 11:00 Frankfurt; the final follows two weeks later
  ([euro-area inflation](steps/euro-inflation.md)).
- **HICP** (Harmonised Index of Consumer Prices) — the euro area's inflation measure, the
  counterpart of US CPI, published by **Eurostat**.
- **Inter-meeting (unscheduled) decision** — a Fed rate change made outside the published meeting
  calendar, usually in a crisis (2001, 2008, March 2020). Stored with `scheduled = false`.
- **Jobless claims (initial claims)** — the weekly count of new unemployment-insurance filings,
  published each Thursday; its 4-week average smooths the weekly noise. Rises when layoffs rise.
- **Survey week** — the week that includes the 12th of the month: the week the jobs report's
  payroll survey counts. The jobs-report forecast compares claims between survey weeks.
- **GDP** (Gross Domestic Product) — total economic output; a quarterly growth release.
- **Initial release / first print** — the value a statistical agency publishes the first time,
  before later revisions. The only version the market could have reacted to on the day, so it is the
  version this project measures against.
- **MoM / YoY** (month-over-month / year-over-year) — whether a change is measured against last
  month or the same month a year ago. Mixing the two silently corrupts a surprise calculation.
- **NFP** (Non-Farm Payrolls) — the monthly US jobs report, usually the first Friday, 8:30 a.m. New
  York time. Traditionally the biggest scheduled mover after CPI and the Fed.
- **PCE / core PCE** (Personal Consumption Expenditures price index) — the Fed's preferred US
  inflation measure, published monthly by the Bureau of Economic Analysis at 8:30 a.m. New
  York time; *core* leaves out food and energy ([more events](steps/step-4-more-events.md)).
- **ISM** (Institute for Supply Management) — publishes the US manufacturing PMI at 10:00 New
  York on the month's first working day ([the ISM survey](steps/ism-manufacturing.md)).
- **ZEW** (Leibniz Centre for European Economic Research) — its *Economic Sentiment Index* asks
  financial analysts whether Germany's economy will be better or worse in six months, out at 11:00
  Frankfurt in the month's second or third week ([Germany's calendar](steps/germany-calendar.md)).
- **Ifo** (Ifo Institute, Munich) — its *Business Climate* index surveys German firms on their
  current business and their outlook, out at 10:00 Frankfurt late in the month.
- **German flash CPI** (TradingView's *Inflation Rate YoY Prel*) — Destatis's first print of the
  month's German inflation, at 14:00 Frankfurt, after six states have published theirs that
  morning.
- **National election** — a country's vote for its president or parliament, here a dated shock with
  no forecast: its result lands when the polls close, and the market's reaction is the next
  trading day ([elections](steps/elections.md)).
- **Tariff action** — a presidential document that imposes, raises, lowers, suspends or ends an
  additional US import duty, dated by its signing; a dated shock with no forecast
  ([tariff actions](steps/tariffs.md)). Under **Section 232** (national security), **Section 301**
  (unfair trade practices), **Section 201** (safeguards against a surge of imports) or **IEEPA**
  (the International Emergency Economic Powers Act).
- **Debt limit** (debt ceiling) — the most the US Treasury may borrow, set by law; when it is
  reached Treasury uses **extraordinary measures** (accounting steps that free room under the
  limit) until Congress raises or suspends it, or until the **X-date**, the day Treasury expects
  to run out of cash ([the debt limit](steps/debt-limit.md)).
- **G7 / G8** (Group of Seven) — the yearly summit of the leaders of the US, Japan, Germany, France,
  the UK, Italy and Canada, with the EU; the G8 with Russia, 1997–2013 ([summits](steps/summits.md)).
- **G20** (Group of Twenty) — nineteen countries, the EU and since 2023 the African Union; its
  leaders have met since the crisis of 2008.
- **Communiqué** — the joint statement a summit's leaders issue, normally on its last day.
- **Too few** (raw move) — a cell with fewer than ten event days, given no verdict.
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
- **Tone / Net Index** — how hawkish a Fed statement sounds, counted from adjective–noun phrases
  ("higher inflation" hawkish, "slower growth" dovish) on a published word list: hawkish over all
  phrases minus dovish over all phrases, plus 1, so 0 is all dovish and 2 all hawkish. No phrase,
  no tone ([the Fed statement's tone](steps/fed-statement-tone.md)).
- **Hold** — a Fed decision after which the target rate is the one of the day before it.
- **Sentiment index** — how strong a Fed statement reads on Gardner, Scotti and Vega's dictionary
  built from the FOMC's own statements: each **keyword** (a topic word such as "unemployment" or
  "inflation") times its closest **modifier** (a word such as "declined" or "elevated", scored 1, 0
  or −1), plus long phrases and future-policy rules, summed over the square root of the words. About
  −1 to 1; positive means a stronger economy or higher inflation
  ([the Fed statement's sentiment](steps/fed-statement-sentiment.md)).

## Instruments & markets

- **Asset class** — the family an instrument belongs to: equity index, single stock, rates/bond, FX,
  commodity, crypto, volatility, credit, freight.
- **BDI** (Baltic Dry Index) — cost of shipping dry bulk cargo; a gauge of global trade demand.
- **Basis point** (bp, "bip") — one hundredth of a percent (0.01%). Bond and rate moves are quoted
  in bps: "10Y up 8 bps" means the yield rose 0.08 percentage points.
- **BRN** (Brent crude) — the global oil price benchmark, traded on ICE. Measured from
  2026-10-27 ([more outcomes](steps/more-outcomes.md)) as Yahoo's `BZ=F`, the front month, at its
  14:30 New York settlement.
- **BTC** (Bitcoin) — the crypto bellwether. Measured from 2026-10-27 as Yahoo's `BTC-USD`, the
  UTC day's last price; its weekend bars are dropped, as every market's are.
- **BUND / FGBL** — the German 10-year government bond and its futures contract (Eurex); the
  eurozone's risk-free benchmark. Free price history is awkward, which is why the MVP uses the US
  10-year instead.
- **Carry trade** — borrowing in a low-interest currency (classically the yen) to buy
  higher-yielding assets elsewhere. Profitable while calm; unwinds violently when the funding
  currency's rates rise.
- **CDS** (Credit Default Swap) — insurance against a borrower defaulting; its price is a direct
  read on perceived default risk.
- **COMP** (Nasdaq Composite) — the index of every Nasdaq-listed stock, the growth end of US
  equities; closes 16:00 New York. Yahoo's `^IXIC`. Takes the S&P 500's expected sign.
- **Contagion** — a shock spreading from where it started to firms or markets exposed to it: one
  bank's failure raising doubts about similar banks.
- **DAX** — Germany's index of its 40 largest listed companies, closing 17:30 Frankfurt time. One
  of the two European markets in [cross-country effects](steps/cross-country.md), with the
  **Euro Stoxx 50** (`SX5E`), the euro area's 50 largest.
- **DXY** (US Dollar Index) — the dollar measured against a basket of major currencies (mostly the
  euro). Rises on risk-off and on hawkish Fed expectations.
- **ES** (E-mini S&P 500 future) — the futures contract on the S&P 500, which trades nearly around
  the clock and therefore reacts to releases outside US stock-market hours.
- **EURUSD** — the euro in dollars, the dollar index's largest weight (58%), so mostly its mirror;
  it takes the dollar index's expected sign reversed. Yahoo's `EURUSD=X`, whose daily close is the
  price at 00:00 London of the bar's own day, so the bar after a US release is the next London
  day's.
- **Flight to safety** — money leaving risky assets for havens (Treasuries, gold, the dollar, the
  yen) during a shock. Usually lowers Treasury yields; see scenario 6 for when it did not.
- **Front-month / continuous futures** — a futures contract expires, so a long price history is
  stitched together from the contract nearest expiry (the *front month*), switching to the next one
  at each expiry (the *roll*). Yahoo's `GC=F`, `BZ=F` and `KC=F` are such series; their price can jump on a roll day
  for reasons unrelated to any event.
- **FX** (Foreign Exchange) — the currency market.
- **Gold / XAU / GC** — gold; `XAU` is its currency-style code, `GC` its COMEX futures symbol. A
  haven asset, sensitive to real interest rates.
- **CORN, WEAT, SOYB** — the Teucrium corn, wheat and soybean funds, which hold those grains'
  futures and roll them over days, so their price has no roll jump; bread, feed and cooking oil
  ([the markets people feel](steps/markets-people-feel.md)). Close 16:00 New York; no expected sign.
- **ITA** — the iShares U.S. Aerospace & Defense ETF; the defence outcome of dated shocks. Closes
  16:00 New York; no expected sign.
- **ITB** — the iShares U.S. Home Construction ETF, US homebuilders; housing and mortgages. Closes
  16:00 New York; no expected sign yet.
- **KC** — arabica coffee, read through ICE's front-month future `KC=F`, which rolls five times a
  year ([coffee](steps/coffee.md)). Settles 13:30 New York; no expected sign.
- **KRE** — an ETF of US regional-bank shares; the market's read on regional-bank stress. Not in
  the instrument universe.
- **Liquidity** — how easily something can be traded without moving its own price. The MVP sticks to
  highly liquid instruments so measured moves reflect the event, not thin trading.
- **Nikkei 225** — Japan's main stock index. Not in the instrument universe.
- **Rates** — the government-bond / interest-rate market. Note the inversion: when bond **prices**
  rise, **yields** fall.
- **Risk-on / risk-off** — the market mood. Risk-on: money into stocks and commodities. Risk-off:
  money into dollars, gold, Treasuries, and volatility spikes.
- **S&P 500** — the index of 500 large US companies; the default "the market" benchmark.
- **SPY** — the largest ETF tracking the S&P 500; a cheap, free-data stand-in for the index.
- **Stablecoin depeg** — a coin meant to hold a fixed value (USDC at $1) trading away from it. A
  systemic-stress signal.
- **SXXP** (STOXX Europe 600) — 600 companies across Europe, computed in Zurich, closing 17:30
  there. Yahoo's `^STOXX`. Takes the DAX's expected sign.
- **Ticker / symbol** — the short code identifying an instrument (`SPY`, `^VIX`). **These strings
  are load-bearing here** — they are join keys between seed data, measurements, and predictions, so
  drift silently breaks lookups.
- **UGA, UNG** — the United States Gasoline Fund and Natural Gas Fund, holding gasoline and
  natural gas futures; petrol at the pump and heating. Close 16:00 New York; no expected sign.
- **UKX** (FTSE 100) — London's 100 largest listed companies, closing 16:30 London (the closing
  auction). Yahoo's `^FTSE`. Takes the DAX's expected sign.
- **UST 10Y** (US Treasury 10-year) — the 10-year US government bond yield; the world's benchmark
  interest rate and the most direct read on an inflation release. Its canonical symbol in
  `instruments.csv` is **`UST10Y / ZN`** (the cash note and its CBOT futures code), mirroring
  `BUND / FGBL`. Measured as a **yield in bps**, so it moves opposite to the bond's price.
- **UST 5Y** (US Treasury 5-year) — the 5-year yield, the front end of the curve and the most
  policy-sensitive maturity. Symbol **`UST5Y / ZF`** (the note and its CBOT futures code), Yahoo's
  `^FVX`, in bps like the 10-year, whose expected sign it takes.
- **VIX** — the Cboe Volatility Index, the market's expected S&P 500 volatility over the next 30
  days, derived from option prices. The "fear gauge": spikes on shocks.
- **^TNX** — Yahoo Finance's symbol for the US 10-year yield. A *vendor* ticker, deliberately not
  the canonical symbol: keys must not move when the data source does — see **UST 10Y**. Quotes the
  yield in percent (`4.2`); checked on 2026-09-25 against FRED's `DGS10`, which it matches to about
  1 bp.
- **Vendor ticker** — a data provider's own code for an instrument, as opposed to the project's
  canonical symbol. Step 2 maps five: `^GSPC` (S&P 500 index), `^TNX`, `DX-Y.NYB` (dollar index),
  `GC=F` (gold futures), `^VIX`; cross-country two, `^GDAXI` and `^STOXX50E`; more outcomes nine,
  `BZ=F`, `EURUSD=X`, `^IXIC`, `^FVX`, `^FTSE`, `^STOXX`, `BTC-USD`, `ITA` and `XLE`; the markets
  people feel seven, each its own symbol; coffee `KC=F`. FRED's series for the breakeven is
  stored as `fred:T5YIE`.
- **XLE** — the Energy Select Sector SPDR ETF, the US energy sector; oil's equity echo. Closes
  16:00 New York; no expected sign.
- **XLU** — the Utilities Select Sector SPDR ETF, US utilities; household bills, bought for their
  rates. Closes 16:00 New York; no expected sign yet.

## Measuring the effect

- **Abnormal return** — the part of a move that is *not* explained by the instrument's ordinary
  behaviour: actual return minus expected return. The honest way to say "the event caused this".
- **Aftershock** — what follows a market shock over the next days to weeks: contagion, a policy
  response, a reversal, the next failure. Used with *shock* (the first reaction, up to the first
  close) and *resolution* (what ends it) in [scenarios](scenarios.md).
- **Baseline** — the ordinary behaviour an abnormal return is measured against: a typical day, or a
  simple model of one.
- **CAR** (Cumulative Abnormal Return) — abnormal returns added up across an event window, to
  capture a move that builds over hours rather than landing at once.
- **Computed baseline / 12-month trend** — step 4's always-available expected value: the average of
  the previous 12 months' first-published m/m changes. Surprise against it is surprise against the
  trend, not against what the market expected.
- **Close-to-close return** — the move from one day's closing price to a later day's closing
  price. The MVP's measure of a release-day reaction, because old price history has closes only.
  Each market's close is at its own time: stocks 16:00 New York, while gold futures' daily close
  is the COMEX *settlement*, 13:30 New York — before a 14:00 Fed decision, so gold's reaction to
  one lands on the next day's close.
- **Ordinary day** — step 3's baseline: a trading day that is no stored event's reaction day (no
  CPI, jobs report or Fed decision), since rung 1's sub-step 6; and, since
  [own years](steps/own-years-baseline.md), none before the flow's first reaction day on that market.
- **Span** — *added 2026-11-04* ([Legend](legend.md#the-target)): how long after an event its
  move is measured: a day, a week (5 closes), a month (21), a quarter (63) or a year (252).
- **Base rate** — *added 2026-11-04*: how often a market went one way over every span of a length
  in a kind's own years, events or not. Unlike an *ordinary day*, a span is never "alone": other
  events fall inside a month or a year by design. Unlike the *drift probability*, it counts every
  span, not earlier releases.
- **Cycle** — *added 2026-11-12* ([part 2](steps/what-follows-long.md)): Fed decisions taken as one
  story. A cut cycle runs from a cut to the last cut before the next hike, holds between included;
  a hike cycle likewise; a run of holds is consecutive holds. Over a quarter or a year an answer
  stands only if it also holds counting each cycle once.
- **Excess move** — *added 2026-11-13* ([step 20, part 1](steps/ceo-scandals.md)): a company's
  move over a span less the S&P 500's over the same closes, in percent: what the company did
  beyond the market.
- **Kind (of event)** — *added 2026-11-04*: what a reader names ("the Fed cuts rates"); in the
  code an event flow, and for a decision what was decided (cut, hold or hike).
- **Up / down / about the same / can't say** — *added 2026-11-04*: a span's four answers against
  its base rate, by the rule in [what follows](steps/what-follows.md); under ten events, *too few*.
  *Can't say* is shown and counted, never graded.
- **Above / as expected / below** — *added 2026-11-04*: a release's kind for a reader of the
  headline, its surprise against the consensus at least the rule's noticeable size either way, or
  between ([what follows a jobs report](steps/what-follows-jobs.md)).
- **Breakeven inflation** — *added 2026-11-04*: the inflation bond markets expect, a Treasury
  yield less the inflation-protected yield of the same maturity; FRED's 5-year series `T5YIE`.
- **Vintage / new-and-revised view** — a series' values as they stood on one release day. FRED's
  `output_type=3` returns one column per release day; payrolls need it because every jobs report
  revises the two months before. FRED keeps every vintage, which is how a release's first print
  and its publication date are recovered.
- **Event flow** — one event type's way in from one origin country (`flows.py`, from step 2 of
  [event flows](steps/event-flows.md)): fetch from its own source, run its own checks, return the
  common records. Identified by (event type, country), so UK CPI would be a flow apart from US CPI
  ([country-aware events](steps/country-aware-events.md)).
- **Expectation source** — one way of saying what was expected (`expectations.py`): the 12-month
  trend, the Cleveland Fed's nowcast. Each returns `Expectation`s, checked against their event before
  a surprise is computed.
- **Least squares (OLS)** — fitting a straight-line formula by making the squared misses as small
  as possible (`stats.least_squares`). The payroll model fits payrolls on ADP's change, the claims
  change and the 12-month trend this way, refitted before every report on earlier reports only.
- **Nasdaq consensus** — the `Consensus` column of Nasdaq's economic calendar, 2008 to today; the
  `nasdaq_consensus` expectation source, checked against TradingView's calendar, whose forecast
  fills in where Nasdaq has no row ([consensus fallback](steps/consensus-fallback.md)). Compared with
  other free sources in [Data sources](data-sources.md#which-free-consensus-is-best).
- **Walk-forward** — replaying history one release at a time, each decision made only from the
  releases before it, so that what is graded was never seen when deciding
  ([rung 2](steps/rung-2-predict.md)).
- **Link** — one event flow and one market, as a pair whose move is measured against the flow's
  surprise. A **signed link** has a direction written down first (a hotter CPI lifts the yield);
  a link **holds** when its direction is right walk-forward by the bar in
  [rung 2](steps/rung-2-predict.md). Only links that hold are called live.
- **Moves / unclear / doesn't** (raw move) — MVP step 3's verdict on whether an event's days move
  a market more than ordinary days: *moves* if the ratio of event-day to ordinary-day moves is at
  least 1.10 **and** p < 0.01; *unclear* if only one holds; *doesn't* if neither
  ([step 3](steps/step-3-raw-move.md)).
- **Tracks / unclear / doesn't** (surprise) — MVP step 4's verdict on whether the move follows the
  surprise: a rank correlation in the expected direction at p < 0.01 **and** the direction right on
  at least 60% of noticeable surprises; *unclear* if only one holds; *doesn't* if neither
  ([step 4](steps/step-4-surprise.md)).
- **Holds** — rung 2's verdict on a link replayed walk-forward: at least 30 calls, right on at
  least 60%, one-sided binomial p < 0.01 ([rung 2](steps/rung-2-predict.md)).
- **Noticeable surprise** — one at least the size its flow's rule sets (0.1 pp for core CPI);
  hit rates count only these, since a tiny surprise has no direction worth grading.
- **Placebo** — the same test run with each event's key close moved away (10 closes earlier and
  10 later, or a span's length if longer), so an answer the period alone would give is caught
  ([what follows](steps/what-follows.md)).
- **Open link** — in rung 2, an event × market link allowed to predict at a release because it
  passes the surprise test on earlier releases; a closed link stays silent.
- **Payroll model** — the jobs report's free forecast, the `payroll_model` expectation source
  (`expectations.PayrollModel`, [nfp-forecast](steps/nfp-forecast.md)). It leaves out
  March 2020 – April 2021 when fitting, so COVID's prints cannot dominate the formula.
- **First reaction day** — the first day whose close can carry an event: its own day if it came
  before the instrument's close, otherwise the next (`study.first_reaction_day`).
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
- **Exchange time zone** — the time zone of the market where an instrument trades, which decides
  what calendar date a price belongs to. Yahoo reports it per ticker; reading a bar's timestamp in
  any other zone can shift it to the wrong day.
- **Half-life** — how long until a move decays halfway back. Distinguishes a lasting repricing from
  a spike that round-trips in minutes.
- **Hit rate** — the fraction of past occurrences where the predicted direction was correct. 50% is
  a coin flip and therefore worthless.
- **Median** — the middle value once a list is sorted. Used instead of the average where one
  extreme day (a crash) would otherwise decide the answer.
- **Move ratio** — step 3's measure: the median absolute move on CPI days divided by the median on
  ordinary days. `1.00` means CPI days are ordinary; `1.30` means they move 30% more.
- **n / n_obs** — how many observations a number is based on. **Always shown next to any estimate
  here**: an effect size from n=4 is a story, not a measurement.
- **Nowcast** — an estimate of a number for the current period, made before the official figure is
  published.
- **Permutation test** — a way to ask "could chance alone give this?" without assuming a
  distribution: relabel days at random many times and see how often the made-up labels produce a
  result as extreme as the real one.
- **p-value** — the share of those random relabellings that did at least as well as the real data.
  Small means chance rarely does it; `p < 0.01` means fewer than 1 in 100.
- **Return** — the percentage price change over a period.
- **Shared day** — a day holding releases of two event flows, so its close-to-close move carries
  both. From [step 4](steps/step-4-more-events.md#shared-days), a new flow's release on one is
  left out of its surprise and prediction tables.
- **Spearman rank correlation** — how consistently one quantity rises with another, computed on
  their ranks instead of their values: +1 always together, 0 unrelated, −1 always opposite. One
  extreme day can shift it only by one rank.
- **Standard deviation (SD)** — the typical size of variation in a series. Used both to standardize
  surprises and to judge whether a move is unusual.
- **Theil–Sen slope** — the median of the slopes between every pair of points. A line fit that one
  extreme point cannot drag. Step 4's "move per 0.1 pp of surprise".
- **t0 / t1** — the two closes a release-day move is measured between: `t0` is the last trading day
  before the release date, `t1` the first trading day on or after it.
- **T5YIE** — FRED's 5-year breakeven inflation, the 5-year Treasury yield less the 5-year TIPS
  yield, read at 15:30 New York and published a day later ([the breakeven](steps/breakeven.md)); its
  move is in basis points; no expected sign.
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
- **Drift probability** — in rung 3, how often a market moved a call's way on the earlier
  noticeable releases, whatever the surprise. The baseline a stated probability must beat: a call
  no better than it only rides the market's drift.
- **ECE** (Expected Calibration Error) — a single number summarizing how far stated probabilities
  drift from observed frequencies.
- **Gate** — the rule that keeps a cell silent until its numbers are good enough (enough
  observations, passing calibration). Prevents confident nonsense from reaching a reader.
- **Isotonic regression** — a calibration method that fits a flexible, always-increasing curve from
  raw scores to true probabilities. Needs more data than Platt scaling.
- **Live call** — in rung 4, a call written to `data/calls.csv` on the release day, before its
  market's close, and graded afterwards. Unlike a replayed call, it cannot have been fitted to the
  outcome. A logged call outside that window, or on a mistyped actual, is **void**; a release with
  no logged rows is **missed**; a call whose release, surprise or move is not loaded yet is
  **pending**.
- **Look-ahead bias** — accidentally using information that was not available at prediction time.
  The classic way a backtest produces results that evaporate in live use.
- **Magnitude band / prediction interval** — the range a move is expected to fall in, rather than a
  single number.
- **Sign-flip test** — a paired permutation test: each pair's difference keeps its size but gets a
  random sign, many times over; p is the share of draws that sum to at least the real total. Rung
  3 uses it to ask whether a link's Brier score beats a coin's or the drift's by more than chance.
- **Power** — how often a test detects an effect that is really there. Rung 3's Brier check has
  little at today's call counts: a perfectly honest 68% probability on 80 calls passes it about one
  time in five ([the record, not a probability](steps/record-not-probability.md)).
- **Too close to tell** — rung 3's verdict for a link whose Brier score is below a coin's and the
  drift's, but not by enough to rule out chance (sign-flip p not under 0.05). Not honest.
- **Move band** — in rung 3, a call's 50% band: the slope times the surprise, plus the 25th to
  75th percentile of earlier misses. Its **coverage** is the share of moves that land inside;
  about half if the band is honest.
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
- **Cleveland Fed nowcast** — the Federal Reserve Bank of Cleveland's daily model estimate of this
  month's CPI change, from oil and gasoline prices and past inflation, published since 2013 with
  free history. Step 4's market-like expected value: a model, not a survey.
- **CPILFESL** — the FRED series ID for seasonally adjusted core US CPI (all items less food and
  energy). Its first-release history on FRED starts in 1997.
- **Economic calendar** — a commercial listing of upcoming releases with forecasts. The usual source
  of **consensus**, and rarely free for long histories.
- **Federal Register** — the US government's daily journal of rules and presidential documents,
  with a free API; the source of the tariff actions' signing days and document numbers.
- **FRED** (Federal Reserve Economic Data) — the St. Louis Fed's free database and API of economic
  series, including CPI. Free, keyed, reliable; carries actuals but not market expectations.
- **FRED new-and-revised view** (`output_type=3`) — one column per release day, holding the month
  first published that day and the months revised that day. Rung 1 reads NFP's first-published
  changes from it in one request.
- **GDELT** (Global Database of Events, Language and Tone) — a free, machine-coded record of the
  world's news as dated events since 2015 (daily since 1979), each with its actors, type and tone.
  The only free history of statements and shocks as events, and noisy: [roadmap](roadmap.md) step
  11 measures one narrow question against a bar fixed first.
- **Trump Twitter Archive** — a public dump of the president's tweets, each with its time to the
  second, to the 2021 ban; with **CNN's Truth Social archive** (his posts since 2022), the source
  of [the president's trade posts](steps/presidential-posts.md) and its
  [part 2](steps/presidential-posts-2.md).
- **CAMEO / GKG** — GDELT's event codes (who did what to whom) and its Global Knowledge Graph
  (themes tagged per article). Neither has a trade-statement code or a speaker.
- **PAYEMS** — the FRED series ID for total US non-farm payrolls, in thousands of jobs: the NFP
  headline number.
- **Prediction market** — a market in contracts that pay on an event's outcome (an election, a
  rate decision); its price is a crowd's probability, the nearest thing to a consensus for a
  political event. Polymarket's history is free from 2020. Not used yet.
- **Series ID** — a data provider's unique code for one time series (e.g. `CPIAUCSL`). Load-bearing
  the way instrument symbols are: the wrong ID silently fetches the wrong data.
- **DFEDTAR / DFEDTARU** — FRED series IDs for the Fed's federal funds target: a single rate until
  2008-12-15 (`DFEDTAR`), then the upper end of a range (`DFEDTARU`). Rung 1 uses them to check that
  no Fed decision is missing from the calendar.
- **DGS10** — the FRED series ID for the daily 10-year Treasury yield. Used to cross-check Yahoo's
  `^TNX`.
- **Stooq** — a free source of historical price data. Since at least 2026-09 it sits behind a
  JavaScript bot check and cannot be read by a program, so the MVP does not use it.
- **Yahoo Finance chart API** — the unofficial endpoint (`query1.finance.yahoo.com/v8/finance/chart`)
  behind Yahoo's charts; returns daily history as JSON with no key. Step 2's price source.
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
- **Naive datetime** — a Python `datetime` with no time zone attached (as opposed to an *aware*
  one). `event_ts` is stored naive but always means UTC, because DuckDB converts an aware value to
  the session's time zone on write.
- **ORM** (Object-Relational Mapper) — a library that hides SQL behind objects. **Deliberately not
  used**: Pydantic models plus plain parameterized SQL keep the data layer obvious.
- **Parquet** — a compact file format for tables that keeps each column's type. `db.insert_models`
  writes rows to a temporary Parquet file and loads it in one statement; row-by-row inserts took
  about four minutes for the 58,000 daily bars, the file takes a fraction of a second.
- **Pydantic** — the library that validates data against typed models, so malformed rows fail loudly
  at the edge instead of silently later.
- **pytest** — the test runner. Tests use `# given` / `# when` / `# then` comments.
- **Delivery** — rung 6: a logged call reaching a person unasked. Here, a desktop popup on this
  laptop for each logged call and each failed job run ([rung 6](steps/rung-6-delivery.md)).
- **Evening score** — the second timer on this machine: weekdays at 18:00 New York it loads the
  day's data, runs `score`, and opens a pull request when the result changes. See
  [the evening score](steps/evening-score.md).
- **Release-day job** — the timer on this machine that runs `fortuneteller live` at 08:30 New
  York every weekday and opens the release's pull request, or an issue if it fails. See
  [the release-day job](steps/release-day-job.md).
- **ruff** — the linter and formatter (100-character lines).
- **Schema** — the table definitions in `schema.sql`, executed by `init`.
- **Seed data / seed CSV** — the committed reference tables in `data/seed/` that the pipeline reads
  as configuration: event types, instruments, starting effect-size guesses. Tuning happens by editing
  data, not code.
- **systemd user timer** — Linux's scheduler for a user's own jobs: a `.timer` unit starts a
  `.service` unit at set times, here in New York's time zone.
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
- **Elephant, goldfish** — the author of a spec, who carries the whole conversation behind it, and
  a reviewer who has seen none of it and reads only the page and its links. Every spec is read by
  a goldfish before measuring and again when its results are in
  ([Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish)).
- **Feature ladder** — the ordered list of what gets built after the MVP, in
  [the roadmap](roadmap.md).
- **Step** — a word with three uses, told apart by what comes with it:
  - **MVP step 1 to 4**: the four sequential experiments of the MVP, files step-1-releases.md to
    step-4-surprise.md.
  - **Roadmap step N** (1 to 20, with 1a, 4a, 4b, 8a): one numbered entry in the roadmap's "Next
    steps" tables, planned after the ladder's rungs 1 to 6. Its spec is named for its subject, as
    in ceo-scandals.md; step-4-more-events.md is roadmap step 4, not MVP step 4.
  - **A step inside a spec**: one row of that spec's "The steps" table, each with its own "done
    when". "Step 18, part 2, step 3" means roadmap step 18, its part 2 spec, that spec's third row.
- **Part** — one spec of a roadmap step too big for one: roadmap step 17 has parts 1 to 2, with
  1b to 1f between. Each part has its own spec, bars and pull requests.
- **Rung** — one entry of the feature ladder, 1 to 7; each is built only because the one below it
  worked. Specs are named rung-N-name.md.
- **Legacy docs** — everything under [`docs/legacy/`](legacy/README.md): the pre-reset design
  corpus, kept for reference, not authoritative.
- **M0 … M7** — the superseded milestone scheme from the old roadmap. **M0 (the data spine) shipped
  and is real**; M1–M7 describe a plan that has been replaced by the MVP and the feature ladder.
- **`main_05082026`** — the branch preserving the implementation discarded in the reset.
- **Lesser release** — a flow whose days count as no other flow's shared or busy days, and whose
  own tables keep only the days it has alone: [jobless claims](steps/jobless-claims.md), out on a
  fifth of all trading days, is the first.
- **Statement flow** — a lesser flow of one person's scheduled speeches and testimonies, with no
  number and so no surprise: the Fed chair's and the ECB president's, in
  [scheduled statements](steps/scheduled-statements.md). `fedchair` and `ecbchief` on the command
  line, **FCH** and **ECP** in its tables.
- **Preview** — the morning job's line about a statement still ahead that day: its time and the
  markets that *move* on its flow's past days, a record and never a direction.
- **MVP** (Minimum Viable Product) — here, specifically: the measured answer to *does the edge
  exist*, defined in [the roadmap](roadmap.md). Not a shipped product.
- **`observations`** — one row per event per instrument: the prices and returns around that event.
  MVP step 2 fills it.
- **Provable core** — the scope discipline of measuring a narrow slice before widening: it began as
  one event type × five liquid instruments (the MVP), and widens one flow or one set of markets per
  pull request, each with its bars written first.
- **Replay harness** (legacy) — the discarded mechanism for running canned events through the
  prediction core. Appears in legacy docs; not part of the current plan.
- **Scoreboard** — the static page `fortuneteller scoreboard` writes to `docs/scoreboard/` and the
  evening job rewrites with the score ([roadmap](roadmap.md) step 5): every call graded, every
  link's record, every event's verdicts for every market, and the chance count beside each grid.
  The first thing delivered to anyone but this laptop: GitHub Pages serves it at
  <https://diykorey.github.io/fortuneteller/scoreboard/> since 2026-10-27.
- **Guess** — a person's call on a release, up or down for one market, in a file
  `data/guesses/<day>-<handle>.csv` added through a pull request; graded beside the machine's call
  ([beat the fortune teller](steps/beat-the-fortune-teller.md)).
- **Handle** — the name a player picks in a guess file's name, lowercase, unchecked.
- **Void guess** — a guess listed with why and never graded: not a flow `live` calls, not one of its
  links, not merged through a pull request before the release, no release that day, or a repeat.
- **Waiting** — a logged call whose close FRED publishes a day late and has not published yet; `score`
  lists it under `waiting:` and, unlike a *pending* row, it stops nothing
  ([the breakeven's sign](steps/breakeven-sign.md)).
- **Trigger** — an event the owner files after it happens, a row `flow,day,kind` in a CSV under
  `data/triggers/` added through a pull request; answered from the reaction close on each market it
  was merged in time for, logged in `data/trigger-log.csv` and graded when the span ends
  ([a trigger arrives](steps/trigger-file.md)). It stands in for a news item until step 20 reads
  the news. Not a *graduation trigger*.
- **The reset** — 2026-08-05, when `main` was rolled back to the M0 spine because the
  implementation had become over-engineered for the stage. Recorded in [CLAUDE.md](../CLAUDE.md).
- **The spine** — the M0 data layer: models, schema, store, seed loader, CLI. Shipped.
