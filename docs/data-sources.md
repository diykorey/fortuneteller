# Free data sources, surveyed

> Taken from an analysis of [FinceptTerminal](https://github.com/Fincept-Corporation/FinceptTerminal)
> (commit on `main` as of 2026-10-09), an open-source terminal that wraps about 250 free data
> sources as Python scripts in `fincept-qt/scripts/`. Each one is graded here for FortuneTeller:
> **useful**, **could be useful** (and on what condition), or **useless**. Terms are in the
> [Glossary](glossary.md).

## How this was done

Every script's description, endpoints and functions were read; none was run. Three sources that
bear on the current roadmap step were queried directly on 2026-10-09: TradingView's and Nasdaq's
economic calendars, and the Forex Factory copy of [free consensus](steps/free-consensus.md). The
scripts are thin wrappers, and several promise more than they call (named below); anything marked
*check* was not verified.

FinceptTerminal's C++ connectors (`src/screens/data_sources/connectors/`) are left out: they are
paid enterprise feeds (Refinitiv, FactSet, PitchBook, Bloomberg Second Measure, RavenPack) or
plumbing (Kafka, FIX, REST, databases). So are its helper scripts (portfolio, translation,
technical analysis), which fetch nothing.

What FortuneTeller needs, in roadmap order: expected values for scheduled releases (consensus);
more US events (GDP, PCE, retail sales) and a Fed surprise; non-US events and markets
(cross-country effects); intraday prices; later, unscheduled events.

## Which free consensus is best

Three free sources publish the forecast before each US CPI and jobs report. Measured on every
stored release since 2007:

| | Nasdaq calendar | TradingView calendar | Forex Factory copy |
| --- | --- | --- | --- |
| Years | 2008 → today, live | 2013 → today, live | 2007 → April 2025, a static file |
| Releases with a forecast (core CPI / headline / payrolls) | 222 / 221 / 223 | 160 / 161 / 163 | 219 / 219 / 220 |
| Its actual matches our first print | all but 2 | all | all but April 2020 |
| Mean miss against our first print, on the ~130 releases all three share, without COVID (core, headline, payrolls) | 0.077 pp, 0.092 pp, 70.9k | 0.078 pp, 0.091 pp, 71.0k | 0.078 pp, 0.089 pp, 70.2k |
| Access | undocumented JSON, ~4 s a request, one request a day | undocumented JSON, one request a quarter | one 68 MB CSV from HuggingFace |

The three agree: the same CPI forecast on 84–97% of shared releases, and payroll forecasts within
1–7k on average. Their misses are the same size, and smaller than the 12-month trend's (79.6k) and
the [payroll model](steps/nfp-forecast.md)'s (76.6k), as a real consensus's should be. None is
more accurate than the others; they differ in **how many years they cover and whether they go on
updating**.

**Nasdaq's calendar is the best single source**: the longest history that is still updated (2008
to today, about 220 releases per measure), as accurate as the others. TradingView is the cleanest
to read but five years shorter; it is the natural cross-check. The Forex Factory copy adds 2007
only and stops in April 2025.

## Useful

### TradingView economic calendar — `tradingview_data`

- **Data:** every scheduled release with actual, forecast and previous, its time in UTC and an
  importance rank, for every country; no key. `economic-calendar.tradingview.com/events`.
- **Why useful:** the expected value we lack, cleanly. For US core CPI, headline CPI and payrolls it
  has a forecast for every release from about mid-2013 to today, and already for the next scheduled
  one. Its actuals match our first prints on every release checked (484 of 484), and each indicator
  has its own name. Best used to cross-check the Nasdaq calendar, or as the source if Nasdaq fails.
- **Condition:** an undocumented public endpoint with no stated terms: pin what is fetched, cache
  it, never redistribute it. Nothing before 2013.
- **Effort:** small. One fetch per quarter and a parser in `sources.py`, one expectation source, as
  the [free-consensus](steps/free-consensus.md) spec already describes for Forex Factory.

### Nasdaq economic calendar — `nasdaq_data`

- **Data:** each day's releases with actual, consensus and previous, by country;
  `api.nasdaq.com/api/calendar/economicevents?date=`. No key. The `date` returns the *previous*
  day's events, so a release on day D is read with D + 1.
- **Why useful:** the longest free consensus history that is still updated: core CPI, headline CPI
  and payrolls from early 2008 to today, about 220 releases each, as accurate as the others (table
  above), and the live expected value rung 2 would need. Its actuals match our first prints on all
  but 2 of 666.
- **Condition:** undocumented, slow (about 4 seconds a request, one request per day), and core CPI
  m/m and y/y share one name, so the m/m row must be told apart by order or size.
- **Effort:** small to medium; a day-by-day backfill once, then one request per release.

### FRED / ALFRED — `fred_data`, `fred_economic_data`

- **Data:** about 800,000 US series, with every past vintage.
- **Why useful:** already the backbone: CPI, payrolls, the Fed's target, ADP, jobless claims. It
  also has first prints for the next US events on the roadmap (PCE, retail sales, GDP).
- **Effort:** none new.

### Yahoo Finance — `yfinance_data`, `yh_finance_data`

- **Data:** daily prices for indices, futures, currencies and yields.
- **Why useful:** already the price source for all five markets.
- **Effort:** none new.

### CBOE indices — `cboe_vix_data`, `cboe_data`

- **Data:** official daily history of VIX, VIX3M, VVIX, SKEW and other CBOE indices from CBOE's
  CDN (CSV); the VIX futures term structure.
- **Why useful:** a second source for VIX, checked against Yahoo the way gold is checked; VIX3M and
  SKEW could be context later.
- **Effort:** small; one CSV.

### Stooq — `stooq_data`

- **Data:** daily OHLCV for about 21,000 symbols: indices, futures, currencies, bond yields; CSV
  download.
- **Why useful:** a cross-check for Yahoo, and the cheapest source of non-US markets for
  cross-country effects (roadmap 4a): DAX, FTSE, Nikkei, gilt and Bund yields (*check* coverage and
  depth).
- **Effort:** small to medium; a `PriceSeries` per market with its own close time and zone.

### European Central Bank — `ecb_sdmx_data`, `ecb_data`

- **Data:** ECB policy rates and their change dates, euro-area HICP, euro reference rates, bond
  yields, balance of payments; SDMX, no key.
- **Why useful:** the roadmap's ECB decisions (step 4) as an event flow, and euro-area data for
  cross-country effects.
- **Effort:** medium; an `EventFlow` in Frankfurt time. No free expected value for the decision.

## Could be useful

### Forex Factory, live scraper — `economic_calendar`

- **Data:** the day's calendar with forecasts, scraped with Selenium from forexfactory.com.
- **When useful:** to extend the [Forex Factory copy](steps/free-consensus.md) past April 2025.
  TradingView and Nasdaq already cover those years.
- **Effort:** medium to high: a browser, Cloudflare, and terms that forbid scraping.

### Investing.com calendar — `investing_calendar_data`

- **Data:** economic, earnings, IPO and dividend calendars with forecasts, from an undocumented API.
- **When useful:** if the three sources above fail; it may reach further back (*check*).
- **Effort:** medium; Cloudflare and unclear terms.

### Kalshi — `prediction_kalshi`

- **Data:** prices of regulated contracts on CPI, payrolls, the Fed's decision and more, 2021 on;
  the script is a trading bridge, history comes from Kalshi's public market API.
- **When useful:** for the market's own expected value, as context: about 45 releases, too few for
  p < 0.01. Kalshi's API does not answer from this network (connection dropped at TLS).
- **Effort:** medium, once reachable.

### Polymarket — `prediction_polymarket`

- **Data:** prediction-market odds, including on Fed decisions, about 2023 on; the script places
  orders, history would come from Polymarket's public price-history API (*check*).
- **When useful:** the one free expected value for a Fed decision, which today has no surprise.
- **Effort:** medium; short history, possibly geo-restricted.

### CME Group public API — `cme_data`, `comex_data`, `nymex_data`, `grain_futures_data`

- **Data:** settlements, volume and open interest of CME futures from `cmegroup.com/api/v1`.
- **When useful:** fed funds futures (ZQ) are the textbook measure of a Fed surprise; only if the
  public endpoints give enough history (*check*; the script reads recent days).
- **Effort:** medium to high; likely needs a paid archive for history.

### Databento — `databento_provider`, `databento_live`, `databento_fno_chain`

- **Data:** CME futures from tick to 1-minute bars, 16+ years; usage-based pricing.
- **When useful:** when intraday prices are taken up again (deferred on 2026-10-09). A new
  account's $125 credit likely covers 1-minute bars around every release.
- **Effort:** small to medium.

### Freemium price APIs — `alphavantage_data`, `alpha_vantage_extra_data`, `polygon_io_data`, `tiingo_data`, `twelve_data`

- **Data:** stock, ETF, FX and crypto prices, some intraday, with a free key.
- **When useful:** cheap intraday for SPY or other ETFs without Databento: Polygon's free tier has
  about two years of minute bars; Alpha Vantage may give long minute history on a free key
  (*check*).
- **Effort:** small each; free tiers allow about 5–25 calls a day.

### New York Fed / Federal Reserve — `federal_reserve_data`

- **Data:** effective fed funds, SOFR, OBFR, Treasury rates, yield curve, money supply, Fed
  holdings.
- **When useful:** day-by-day policy-rate levels for the Fed flow; most are on FRED already.
- **Effort:** small.

### US Treasury — `treasury_data`, `fiscal_data`, `government_us_data`

- **Data:** debt, average interest rates, Treasury exchange rates (FiscalData); auction results
  (TreasuryDirect).
- **When useful:** Treasury auctions as events that move the 10-year yield; a surprise needs the
  when-issued yield, which is not free.
- **Effort:** medium.

### BLS and BEA — `bls_data`, `bea_data`

- **Data:** official CPI and employment (BLS), GDP, PCE and income (BEA), with release schedules.
- **When useful:** to cross-check release dates, or for series FRED lacks; neither gives first
  prints, ALFRED does.
- **Effort:** small; free keys.

### CFTC Commitments of Traders — `cftc_data`

- **Data:** weekly positioning by trader type in each futures market.
- **When useful:** positioning as a condition in later rungs: do surprises hit harder when traders
  lean one way?
- **Effort:** medium.

### NBER — `nber_data`

- **Data:** business-cycle dates and NBER datasets.
- **When useful:** splitting results by regime, recession or expansion.
- **Effort:** small.

### Other central banks — `boe_data`, `boc_data`, `boj_fetcher`, `rba_data`, `snb_data`, `riksbank_data`, `norges_bank_data`, `bcb_data`, `nbp_data`, `cnb_data`, `boi_data`, `tcmb_data`

- **Data:** policy rates, exchange rates, statistics of the Bank of England, Canada, Japan,
  Australia, Switzerland, Sweden, Norway, Brazil, Poland, Czechia, Israel and Turkey.
- **When useful:** their decisions as event flows for cross-country effects (roadmap 4, 4a).
- **Effort:** medium each; no free expected value.

### Other statistics offices — `ons_data`, `statcan_data`, `abs_data`, `eurostat_data`, `eurostat_extra_data`, `estat_japan_api`

- **Data:** CPI, labour, GDP and trade for the UK, Canada, Australia, the EU and Japan.
- **When useful:** other countries' releases as events. Most give the latest revised values, not
  first prints, so a surprise needs care.
- **Effort:** medium to high.

### US energy — `eia_data`, `eia_petroleum_data`, `eia_natural_gas_data`, `eia_steo_data`, `eia_electricity_data`

- **Data:** weekly crude and gas inventories, prices, production, the short-term outlook.
- **When useful:** the weekly inventory reports as events, if oil or gas markets are added.
- **Effort:** medium; free key.

### US agriculture — `usda_crop_data`, `usda_nass_data`, `usda_fas_data`, `usda_ers_data`

- **Data:** WASDE supply and demand estimates, crop production, global stocks, food prices.
- **When useful:** WASDE as an event, if grain markets are added.
- **Effort:** medium.

### Conflict, disasters and weather — `acled_data`, `reliefweb_data`, `noaa_climate_data`, `open_meteo_data`

- **Data:** dated, geocoded conflict and protest events (ACLED); disaster reports (ReliefWeb);
  storms and weather history (NOAA, Open-Meteo).
- **When useful:** unscheduled geopolitical and climate events, in later rungs.
- **Effort:** medium; ACLED needs a free key and has licence limits.

### US politics — `congress_gov_data`, `govtrack_data`, `govinfo_data`

- **Data:** bills, votes, committees, federal publications.
- **When useful:** legislative events, in later rungs.
- **Effort:** medium.

### Attention — `wikipedia_pageviews_data`

- **Data:** daily page traffic for any Wikipedia article.
- **When useful:** how salient an unscheduled event was.
- **Effort:** small.

### Housing — `zillow_data`, `redfin_data`

- **Data:** monthly home values, rents, inventory and sales by metro.
- **When useful:** housing releases as events; the official ones (starts, Case-Shiller) are on FRED.
- **Effort:** small.

## Useless

For other products: a general terminal, Chinese markets, crypto, development research. One row per
script, with the data its own description promises.

### China markets

Why not: Chinese (and Indian) market data; not our markets or events.

| Script | Data |
| --- | --- |
| `akshare_alternative` | Wrapper for alternative and specialized data sources |
| `akshare_analysis` | Comprehensive wrapper for AKShare stock technical analysis, fund flow, and fundamental data |
| `akshare_bonds` | Wrapper for bond market data (treasury, corporate, convertible bonds) |
| `akshare_company_info` | AKShare Company Information API Fetches detailed company information for stocks |
| `akshare_crypto` | Provides access to cryptocurrency data: Bitcoin, CME futures, spot prices |
| `akshare_currency` | Provides access to forex data: exchange rates, currency pairs, historical data |
| `akshare_data` | - COMPREHENSIVE VERSION Most comprehensive Chinese financial data API with 1,200+ endpoints |
| `akshare_derivatives` | Wrapper for options and derivatives market data |
| `akshare_economics_china` | Wrapper for Chinese economic indicators and macro data |
| `akshare_economics_global` | Wrapper for global economic indicators |
| `akshare_energy` | Provides access to energy data: carbon trading, oil prices, energy markets |
| `akshare_funds_expanded` | Comprehensive wrapper for enhanced fund market data and analysis |
| `akshare_futures` | Provides access to futures data: contracts, warehouse receipts, positions, spot prices |
| `akshare_index` | Provides access to index data: constituents, weights, historical data, global indices |
| `akshare_macro` | Covers 96 macroeconomic functions from akshare library (version 1.18.20) Organized by region: Australia, Brazil, India, Russia, New Zealand, Canada, Euro, Germa |
| `akshare_misc` | Covers 129 remaining functions from akshare library (version 1.18.20) Categories: get, spot, amac, stock, article, fx, air, car, sw, fund, movie, qdii, fred, mi |
| `akshare_news` | Provides access to financial news: CCTV, Baidu economic news, trade notifications |
| `akshare_reits` | Provides access to REIT data: realtime, historical, minute data |
| `akshare_stocks_board` | (Batch 6) Provides access to industry boards, concept boards, sector data ~50 endpoints |
| `akshare_stocks_financial` | (Batch 3) Provides access to financial statements, analysis, and reports ~50 endpoints |
| `akshare_stocks_funds` | (Batch 5) Provides access to fund flows, capital movement, block trades ~50 endpoints |
| `akshare_stocks_historical` | (Batch 2) Provides access to historical price data: daily, minute, intraday ~50 endpoints |
| `akshare_stocks_holders` | (Batch 4) Provides access to shareholder data, holdings, institutional ownership ~50 endpoints |
| `akshare_stocks_hot` | (Batch 8) Provides access to hot stocks, news, comments, ESG, notices, and miscellaneous data ~50 endpoints |
| `akshare_stocks_margin` | (Batch 7) Provides access to margin trading, HSGT (Stock Connect), and related data ~50 endpoints |
| `akshare_stocks_realtime` | (Batch 1) Provides access to realtime/spot stock data: A-shares, HK, US, B-shares, indices ~50 endpoints |
| `baostock_corporate_actions` | BaoStock Corporate Actions Collects dividend and adjust-factor datasets incrementally. |
| `baostock_daily_backfill` | BaoStock Daily Backfill Incremental daily OHLCV backfill for all BaoStock symbols. |
| `baostock_data` | Provides a CLI-style endpoint interface with JSON output for Fincept Terminal. |
| `baostock_fundamentals_quarterly` | BaoStock Fundamentals Quarterly Incremental quarterly fetch for profit/growth/balance/cashflow/dupont/operation. |
| `cninfo_announcements_incremental` | CNINFO Announcements Incremental Incremental filings sync by stock and category with watermark-based pagination. |
| `cninfo_data` | Provides disclosure search endpoints for Chinese listed companies. |
| `cninfo_entity_resolver` | CNINFO Entity Resolver Builds/maintains stock_code -> org_id/sec_name/market master mapping. |
| `cninfo_pdf_downloader` | CNINFO PDF Downloader Downloads announcement PDFs with retry, checksum, and dedupe index. |
| `cninfo_pdf_text_extractor` | CNINFO PDF Text Extractor Extracts text from downloaded CNINFO PDFs with dedupe/checkpoint state. |
| `cnstats_data` | A COMPLETE wrapper for accessing China's National Bureau of Statistics data. Provides access to ALL Chinese economic indicators, price indices, industrial data, |
| `fii_dii_scraper` | fii_dii_scraper.py — NSE cash-market FII/DII daily flows. NSE publishes the daily institutional buy/sell numbers on |

### Crypto

Why not: crypto assets are out of scope.

| Script | Data |
| --- | --- |
| `alternative_me_data` | Alternative.me: Fear & Greed Index, crypto fear gauge, global market sentiment (no API key required). |
| `blockchain_com_data` | Bitcoin network stats, hashrate, mempool, tx volumes, address data. No API key required. |
| `coincap_data` | 1000+ crypto prices, market caps, volumes, exchange data, candles. No API key required (rate limited). Optional key via COINCAP_API_KEY. |
| `coingecko` | A complete and literal wrapper for all 75+ public CoinGecko API endpoints. This is a comprehensive utility for accessing the full range of CoinGecko's data. |
| `coinglass_data` | Crypto futures open interest, funding rates, liquidations, long/short ratios across 30+ exchanges. |
| `coinmarketcap_data` | CoinMarketCap Basic tier: top crypto listings, prices, market caps, categories, and global metrics via the CoinMarketCap Pro API. |
| `coinpaprika_data` | 71000+ assets, market caps, OHLCV, exchanges, events. No API key required for public endpoints. |
| `cryptocompare_data` | OHLCV historical for 5700+ coins, social stats, news, exchange volume. Free key optional via CRYPTOCOMPARE_API_KEY. |
| `defillama_data` | TVL for 3000+ DeFi protocols, chain TVL, yield pools, bridges, fees. No API key required. |
| `dexscreener_data` | DEX pair prices, volume, liquidity across 80+ chains. No API key required. |
| `glassnode_data` | Bitcoin/Ethereum on-chain metrics — active addresses, tx count, hash rate, NVT ratio. |
| `messari_data` | Crypto asset metrics, profiles, market data, on-chain fundamentals. Free key optional via MESSARI_API_KEY. |

### Company and stock data

Why not: single stocks and valuation; we study macro events.

| Script | Data |
| --- | --- |
| `alpha_spread_data` | Intrinsic value, DCF, comparable company analysis for stocks — free tier. |
| `eodhd_data` | End-of-day historical data for 70+ exchanges, fundamental data, bulk downloads. |
| `finnhub_data` | Real-time quotes, fundamentals, earnings calendar, SEC filings, sentiment, forex, and crypto data via the Finnhub Stock API. |
| `fmp_data` | Financial Modeling Prep: quotes, company profiles, price history, financial statements, ratios |
| `fmp_extra_data` | DCF valuations, analyst estimates, insider trading, institutional holdings — extended free tier. |
| `iex_cloud_data` | US stock quotes, news, earnings, financials, economic data — free tier. **IEX Cloud shut down in 2024.** |
| `intrinio_data` | Financial data, news sentiment, economic indicators — free tier. |
| `lei_data` | Fetches Legal Entity Identifier (LEI) data including global company identification, ownership structures, and parent-child relationships from the GLEIF API. |
| `marketstack_data` | End-of-day data for 70+ global exchanges, tickers, splits, dividends. |
| `multpl_data` | multpl.com: long-run S&P 500 valuation series (P/E, CAPE, dividend yield) |
| `openCorporates_data` | Fetches global corporate registry data — company information, officers, and filings for 200M+ companies worldwide. Requires a free API key for full access. |
| `open_ownership_data` | Fetches beneficial ownership data — who owns and controls companies across 130+ countries from the OpenOwnership Beneficial Ownership Data Standard (BODS) API. |
| `openfigi_data` | Map tickers/ISINs/CUSIPs to global FIGI identifiers. 1700+ asset classes globally. No key for basic use (higher rate with OPENFIGI_API_KEY). |
| `quandl_nasdaq_data` | Financial, economic, and alternative datasets — Fed data, commodities, futures. |
| `quandl_wiki_data` | Fetches adjusted end-of-day US stock prices, dividends, and splits for 3000+ stocks via the Nasdaq Data Link (formerly Quandl) WIKI dataset. |
| `quiverquant_data` | Congress trades, government contracts, insider transactions, lobbying — free tier. |
| `sec_data` | SEC EDGAR: company filings, insider trades, institutional ownership, company facts |
| `sec_xbrl_data` | SEC EDGAR XBRL Company Facts: structured financial data — revenue, EPS, balance sheet for all public US companies (no API key required). |
| `simfin_data` | Free fundamental financial data — income statements, balance sheets, cash flows for 4000+ US companies. |
| `wisesheets_macro_data` | Long-term historical macro data — P/E ratios, Shiller CAPE, Buffett indicator via public endpoints. |

### Development and long-run macro

Why not: annual or quarterly indicators, revised, with no release-day timing.

| Script | Data |
| --- | --- |
| `adb_data` | Fetches macroeconomic and social indicators from Asia-Pacific region |
| `adb_data_extended` | Additional indicators covering poverty, gender, climate, and infrastructure for Asia-Pacific countries via the ADB Key Indicators Database (KIDB). |
| `afdb_data` | African economic data, projects, infrastructure, and development indicators from the AfDB Open Data for Africa portal. |
| `bis_data` | BIS (Bank for International Settlements) SDMX API wrapper Provides access to global economic and financial statistics data from BIS |
| `bis_data_extended` | Bank for International Settlements extended statistics: global credit gap, property prices, exchange rates, banking stats, and policy rates via SDMX API. |
| `bis_stats_data` | Global credit, debt securities, banking stats, effective exchange rates, property prices. No API key required. |
| `census_international_data` | US Census International Data: population, demographics, economic development indicators for all countries (IDB). |
| `doing_business_data` | World Bank Doing Business / B-READY indicators: business environment scores for 190 countries. |
| `ebrd_data` | Transition indicators, project data, and economic data for Eastern Europe and Central Asia from the EBRD open data portal. |
| `econdb_data` | Fetches global economic indicators from EconDB (econdb.com) |
| `fitch_connect_data` | Fetches sovereign debt data, budget transparency, and fiscal statistics using the World Bank Open Finances and WDI APIs — no API key required. **Despite the name, calls World Bank APIs.** |
| `gfd_data` | Banking system depth, efficiency, stability, and access indicators for 200+ countries via the World Bank Global Financial Development database. |
| `global_competitiveness_data` | IMD World Competitiveness Yearbook + WEF GCI proxy via World Bank: competitiveness indicators by country. |
| `global_debt_monitor_data` | Government, corporate, and household debt ratios globally via the IMF Data Mapper API (covers fiscal monitor, WEO, and global debt database indicators). |
| `global_findex_data` | Fetches financial inclusion data — bank accounts, digital payments, credit access, savings rates, and mobile money for 140+ countries from the Global Findex dat |
| `global_innovation_data` | Global Innovation Index (WIPO/Cornell): innovation ranking and scores for 130+ countries. |
| `global_price_index_data` | Various global price indices: Big Mac Index, Economist commodity indices, CPI comparisons, PPP rates — fetched from public sources. |
| `iadb_data` | Latin America and Caribbean development data, projects, and economic indicators from the IDB/IADB open data portal. |
| `ilostat_data` | Fetches international labour statistics from the ILO ILOSTAT SDMX REST API and the ILOSTAT Bulk Download Facility. |
| `ilostat_data_extended` | ILO Statistics SDMX API: global labour force, unemployment, wages, working hours, and employment data for 200+ countries. |
| `imf_data` | IMF data services: economic indicators, direction of trade |
| `imf_datamapper_data` | IMF DataMapper API: WEO forecasts, global debt, fiscal monitor, and financial soundness indicators for 190+ countries. |
| `isdb_data` | Member country data, project financing, and economic indicators for Muslim-majority countries from the IsDB public data portal. |
| `maddison_project_data` | Fetches long-run GDP per capita estimates for 169 countries back to year 1 from the Maddison Project Database (MPD 2020). |
| `oecd_data` | Modular, fault-tolerant wrapper for OECD economic data using SDMX RESTful API Sources: OECD SDMX API (https://sdmx.oecd.org/public/rest/) |
| `oecd_dev_data` | Official Development Assistance (ODA) flows, aid effectiveness, donor statistics, and recipient country data via the OECD SDMX-JSON stats API. |
| `penn_world_table_data` | Fetches national accounts, productivity, and living standards data from the Penn World Tables (PWT 10.x) for 183 countries from 1950 to 2019. |
| `statista_free_data` | Open/free statistics portals: IndexMundi and other free stat aggregators for cross-country data (no key required). |
| `un_comtrade_data` | Comprehensive wrapper for the United Nations Comtrade Database API. Provides access to global bilateral trade flows for 200+ countries at |
| `un_comtrade_extended_data` | Detailed bilateral trade flows by HS chapter, trade balances, and services trade via the UN Comtrade public preview API (500 records per call, no key required). |
| `un_sdg_data` | All 17 SDG goals, 230+ indicators for all countries. No API key required. |
| `un_stats_data` | Fetches national accounts, environment accounts, demographic statistics, and gender statistics for all countries from the UN Statistics Division SDG and SNA API |
| `unctad_data` | United Nations Conference on Trade and Development: world trade, FDI flows, maritime transport, investment policy, and development data. |
| `undp_data` | Human Development Index (HDI), Gender Inequality Index (GII), and Multidimensional Poverty Index (MPI) for all countries via the UNDP HDR API. |
| `weforum_data` | Global Competitiveness Index, travel & tourism competitiveness, and energy transition data via the TC Data 360 (World Bank-hosted WEF datasets) API. |
| `wits_trade_data` | Fetches international trade, tariff, and non-tariff data from World Bank WITS platform |
| `world_bank_extra_data` | World Bank extended indicators: climate, poverty, gender, education, health, and governance data beyond basic coverage. |
| `world_inequality_data` | Provides income and wealth inequality metrics including top income shares, wealth distribution, Gini coefficients, and pre-tax income for 100+ countries. |
| `worldbank_data` | Fetches economic, development, and commodity data from the World Bank Open Data API |
| `wto_data` | This script provides access to multiple WTO APIs: |
| `wto_data_extended` | World Trade Organization Statistics: global tariffs, trade in goods and services, trade profiles, and trade indicators. |

### Governance and society

Why not: yearly scores and surveys; no market-moving dates.

| Script | Data |
| --- | --- |
| `eiu_data` | EIU Democracy Index + Economist open data: democracy scores, regime types for 167 countries. |
| `freedom_house_data` | Freedom House: Freedom in the World, Freedom on the Net, Nations in Transit scores for all countries. |
| `global_risks_data` | WEF Global Risks Report data: risk likelihood, impact scores, interconnections from annual survey. |
| `global_trade_alert_data` | Global Trade Alert: protectionist and liberalizing measures, trade policy interventions worldwide. |
| `open_parliament_data` | Open Parliament / They Vote For You: parliamentary votes, member records for multiple countries (TheyWorkForYou API). |
| `open_secrets_data` | OpenSecrets: US campaign finance, lobbying data, PAC contributions, revolving door. |
| `pew_research_data` | Pew Research Center: global public opinion, religion, demographics, internet use surveys. |
| `prs_group_data` | Political stability, rule of law, corruption control, and regulatory quality via the World Bank Worldwide Governance Indicators (WGI) API. |
| `rsf_press_freedom_data` | Reporters Without Borders Press Freedom Index: annual rankings and scores for 180 countries. |
| `transparency_budget_data` | Provides government budget transparency scores, Open Budget Index (OBI), fiscal openness rankings, and governance dimensions for countries globally. |
| `transparency_intl_data` | Provides Corruption Perception Index (CPI) scores, country rankings, historical trends, and regional averages from Transparency International. |
| `world_justice_rule_data` | World Justice Project Rule of Law Index: rule of law scores for 140 countries across 8 factors. |
| `world_values_survey_data` | World Values Survey: cross-national survey data on values, beliefs, norms from 100+ countries. |

### Health, education, population

Why not: health and demographic statistics, not market events.

| Script | Data |
| --- | --- |
| `global_health_security_data` | Provides Global Health Security Index scores, pandemic preparedness assessments, country rankings, category scores, and historical trend data. |
| `oecd_health_data` | Provides health expenditure, life expectancy, disease burden, pharmaceutical market data, health workforce, and hospital statistics for OECD countries. |
| `un_population_data` | UN World Population Prospects: population projections, demographic indicators for all countries 1950-2100. |
| `unesco_data` | Comprehensive wrapper for UNESCO UIS Data API providing access to global education, science, culture, and demographic statistics |
| `unfpa_data` | Demographic data, reproductive health, and population projections from the United Nations Population Fund open data resources. |
| `unhcr_data` | Provides refugee populations, displacement figures, asylum applications, demographic breakdowns, stateless persons, and returns data from UNHCR. |
| `unicef_data` | Child health, education, nutrition, and water/sanitation data for all countries via the UNICEF SDMX public data API. |
| `who_data` | Provides mortality, disease burden, health systems, nutrition, and immunization data for 200+ countries via the WHO GHO OData API. |
| `who_immunization_data` | Provides vaccination coverage rates, disease incidence, immunization schedules, stockout data, and global coverage statistics via WHO and UNICEF data sources. |
| `world_pop_data` | High-resolution population grids, demographic estimates, and urbanization data from the University of Southampton WorldPop project REST API. |
| `worldbank_health_data` | Provides life expectancy, literacy, Gini coefficient, HDI-related indicators, and poverty headcount data for countries worldwide. |
| `worldometers_data` | Worldometers real-time statistics: world population counter, COVID stats, countries data via disease.sh API. |

### Climate, energy and environment statistics

Why not: long-run or physical statistics, not dated shocks to our markets.

| Script | Data |
| --- | --- |
| `carbon_price_data` | Carbon pricing data: EU ETS prices, California CCA, RGGI allowances, global carbon markets. |
| `climate_trace_data` | GHG emissions for 350M+ assets globally, country/sector level, 2015-2025. No API key required (beta). |
| `copernicus_data` | Provides ERA5 reanalysis data, seasonal forecasts, climate indicators, sea level data, and temperature anomalies via the CDS API. |
| `ember_energy_data` | Provides yearly/monthly electricity generation, demand, CO2 emissions, and carbon intensity for 200+ countries. Data licensed under CC BY 4.0. |
| `energy_transition_data` | Provides global renewable energy capacity, energy transition indicators, clean technology deployment, EV adoption, and CO2 intensity via IEA and IRENA open data |
| `entso_e_data` | ENTSO-E (European electricity grid): power generation, load, cross-border flows, capacity, prices. |
| `fao_data_extended` | Food security, nutrition, fisheries, forestry, land use, and emissions data beyond basic FAOSTAT via the FAO Fenix Services API. |
| `faostat_data` | Wrapper for the UN Food and Agriculture Organization (FAO) FAOSTAT database. Covers crop production, trade, food security, emissions, prices, land use, and more |
| `gas_infrastructure_data` | ENTSO-G (European gas grid): gas flows, storage levels, LNG sendout, interconnection capacities. |
| `global_forest_watch_data` | Deforestation alerts, tree cover loss, forest carbon stock, protected areas, and fire data via the Global Forest Watch Data API. |
| `global_solar_atlas_data` | Global Solar Atlas (World Bank/Solargis): solar irradiance, PV output potential for any location worldwide. |
| `global_wind_atlas_data` | Global Wind Atlas (DTU/World Bank): wind speed, power density, capacity factor data for any location. |
| `iea_data` | IEA open statistics: energy supply, demand, CO2, renewables for 180+ countries via IEA public API (no key for public endpoints). |
| `irena_data` | International Renewable Energy Agency: renewable capacity, generation, investment, costs by country/technology. |
| `oecd_energy_data` | OECD Energy Statistics: energy supply/demand, electricity, oil, gas, renewables for OECD countries. |
| `opec_data` | OPEC Annual Statistical Bulletin: oil production, reserves, exports, revenues by member country. |
| `openaq_data` | Air quality data from 30,000+ stations in 100+ countries — PM2.5, PM10, NO2, CO, SO2, O3 via OpenAQ API v3 (free key required via OPENAQ_API_KEY). |
| `opsd_energy_data` | Provides European electricity consumption, generation by source, renewable capacity, power plant data, and price time series for European countries. |
| `owid_co2_data` | CO2 emissions, energy mix, per-capita emissions for all countries via OWID GitHub raw CSV (no key required). |
| `owid_data` | CO2, energy, health, poverty, GDP per capita, democracy data for all countries. Chart data comes from the public OWID grapher CSV endpoint |
| `paris_agreement_data` | National climate pledges (NDCs), GHG emissions inventories, sectoral targets, and adaptation data via the Climate Watch API. |
| `unep_data` | Environmental indicators covering forests, freshwater, biodiversity, marine, and land use via the UNEP Environmental Live data portal. |
| `waqi_data` | AQI for 11000+ stations globally, PM2.5/PM10/NO2/CO/SO2/O3. Requires free API key via WAQI_TOKEN env var. |
| `world_bank_climate_data` | Temperature projections, precipitation, climate risk by country via World Bank Climate Knowledge Portal API (no key required). |

### Shipping, geo and satellites

Why not: alternative data for other strategies.

| Script | Data |
| --- | --- |
| `aisstream_data` | Global real-time AIS vessel positions, vessel info, port calls via AISStream REST API (free key required). |
| `freightos_fbx_data` | Global container freight rates for 12 tradelanes — fetch from public data sources and Freightos public chart endpoints. |
| `global_fishing_watch_data` | Provides vessel tracking, fishing activity hours, port events, and AIS data for vessels worldwide via the Global Fishing Watch public API. |
| `marinetraffic_data` | MarineTraffic free tier: vessel positions, expected arrivals, port congestion data via MarineTraffic API (free key required). |
| `n2yo_satellite_data` | Complete coverage of all N2YO.com REST API v1 endpoints for satellite tracking and orbital data. |
| `nasa_gibs_api` | Complete coverage of all NASA GIBS services with hierarchical structure: 1. Catalogue - Lists all available imagery layers across all services |
| `nominatim_data` | Global geocoding, reverse geocoding, place search, address lookup via Nominatim public API (no key, 1 req/sec policy). |
| `oscar_data` | Comprehensive wrapper for WMO OSCAR API providing access to satellite instruments, satellites, and Earth observation variables data |
| `overpass_api_data` | Query OSM features — banks, ATMs, hospitals, airports, ports, industrial areas globally via Overpass API (no key required). |
| `port_congestion_data` | Global port congestion and container shipping data from public sources. |
| `sentinelhub_data` | Access to satellite imagery for financial analysis and alternative data |
| `shipping_data` | Baltic Exchange indices: BDI (Baltic Dry Index), BCI, BPI, BSI, BHSI — dry bulk shipping rates. **Baltic Exchange indices are paid.** |

### Open-data portals

Why not: catalogues of datasets, not series we need.

| Script | Data |
| --- | --- |
| `canada_gov_api` | Fetches Canadian government data using hierarchical structure: 1. Catalogue - Lists all data publishers (organizations) |
| `data_gov_hk_api` | A comprehensive wrapper for Hong Kong Government Data Portal APIs |
| `datagov_au_api` | A wrapper for the data.gov.au (CKAN-based) API to access Australian government data. |
| `datagovsg_data` | Provides access to Singapore's open data portal including real-time APIs and catalog APIs. |
| `datagovuk_api` | Fetches UK government data using hierarchical structure: 1. Catalogue - Lists all data publishers (organizations) |
| `french_gov_api` | (English Version) Provides access to multiple French government APIs: 1. API Géo - Administrative boundaries and geographic data |
| `govdata_de_api_complete` | Fetches German government data using CKAN-based hierarchical structure: 1. Organizations - Lists all data providers/publishers (organizations) |
| `hdx_data` | Direct CKAN API implementation - no external dependencies required Based on HDX CKAN API Cookbook |
| `openafrica_api` | - African Open Data Portal API A wrapper for the open.africa (CKAN-based) API to access African open data. |
| `pxweb_fetcher` | Standardized PxWeb API wrapper for Statistics Finland. |
| `scb_data` | Comprehensive wrapper for SCB PxWebApi providing access to Swedish statistical data |
| `spain_data` | Access to Spanish government datasets through hierarchical catalogue → dataset → resources structure |
| `swiss_gov_api` | (opendata.swiss) Fetches Swiss government data using CKAN platform structure: 1. Catalogue - Lists all data publishers (organizations) |
| `universal_ckan_api` | A comprehensive wrapper for accessing multiple CKAN-based data portals worldwide. |
| `universal_socrata_api` | A comprehensive wrapper for querying any Socrata-powered open data portal. |

### Research and misc. reference

Why not: papers, registries and local statistics; not event data.

| Script | Data |
| --- | --- |
| `arxiv_data` | Fetches research papers in finance, economics, machine learning, and quantitative finance from the ArXiv API — full metadata and abstracts. |
| `census_data` | US Census Bureau API: ACS demographics, trade statistics, economic census, and population estimates. |
| `crossref_data` | Fetches academic paper metadata, citations, and DOI resolution for 130M+ scholarly articles from the CrossRef API. Supports polite pool with email header. |
| `data_world_data` | Fetches community-published datasets from data.world covering finance, economics, ESG, demographics, and more. Requires a free API token. |
| `fdic_data` | US bank financial health, assets, capital ratios, NPL, and data for all FDIC-insured banks via the FDIC BankFind Suite API. |
| `fdic_fetcher` | Robust, auto-paginated wrapper for the FDIC Bank Data API. |
| `github_stats_data` | Repo commit activity, star history, contributor stats, language breakdown, trending repos. No key required (60 req/hr); GITHUB_TOKEN for 5000/hr. |
| `global_petrol_prices_data` | Retail fuel prices (gasoline, diesel, LPG) by country — weekly updates from GlobalPetrolPrices public data (no key required). |
| `harvard_dataverse_data` | Fetches research datasets in social science, economics, and public health from the Harvard Dataverse repository. |
| `hud_data` | HUD: Fair Market Rents, income limits, public housing, opportunity zones via HUD User API (free key required). |
| `irs_data` | Fetches US tax data from the IRS Statistics of Income (SOI) program — individual income, corporate taxes, and estate taxes by state and income bracket. |
| `kaggle_data` | Fetches public finance, economics, and ML datasets from Kaggle — stock prices, economic indicators, alternative data, and competitions. |
| `numbeo_data` | Numbeo: Cost of living, quality of life, crime, healthcare, property prices by city/country (free key required via NUMBEO_API_KEY). |
| `semantic_scholar_data` | AI-powered academic search with citation graphs and paper recommendations for 200M+ papers from the Semantic Scholar API. |
| `ssrn_data` | Fetches working papers from the Social Science Research Network — finance, economics, accounting — including abstracts, citations, and download statistics. |
| `wipo_data` | Patent filings, trademark applications, industrial designs, and IP statistics by country via the WIPO IP Statistics Data Center. |
| `zenodo_data` | Fetches open research data from Zenodo (CERN) — datasets, software, and papers across all scientific disciplines. Supports optional access token for higher rate |

### FX and commodity reference prices

Why not: reference FX and commodity prices; our dollar and gold come from Yahoo already.

| Script | Data |
| --- | --- |
| `bnm_data` | Fetches data from the BNM Open API. |
| `bnr_data` | Fetches data from the BNR public XML API. |
| `exchangerate_data` | 200+ currencies, no key, no rate limit. Uses open.er-api.com and fawazahmed0 CDN as fallback. |
| `frankfurter_data` | ECB reference exchange rates, 30+ currencies, daily history back to 1999. No API key required. |
| `hnb_data` | Fetches exchange rate data from the HNB public REST API. |
| `lme_data` | London Metal Exchange prices: copper, aluminium, zinc, lead, nickel, tin — cash and 3-month prices. **LME prices are licensed, not free.** |
| `metals_prices_data` | Gold, silver, platinum, palladium, and copper real-time and historical prices via the Metals.dev API. |
| `mnb_data` | Fetches exchange rate data from the MNB SOAP web service. |
| `open_exchange_data` | Open Exchange Rates free tier: 170+ currency rates, historical rates, time-series, and OHLC data. |
| `platts_data` | S&P Global Commodity Insights free tier / public commodity price indices. **S&P Global Platts has no real free tier.** |
| `public_apis_finance_data` | Aggregated open financial APIs: NBP Poland, Croatian National Bank, Czech National Bank — no key required. |
| `world_bank_commodity_data` | World Bank Pink Sheet: 70+ commodity prices monthly from 1960 via World Bank API (no key required). |

### Duplicates and play money

Why not: see each row.

| Script | Data |
| --- | --- |
| `openbb_data` | OpenBB Platform public endpoints: stocks, macro, alternatives, ETF holdings, economic calendar. **Thin wrapper over OpenBB's hosted endpoints; duplicates sources listed above.** |
| `polymarket` | Prediction markets data fetcher Uses Manifold Markets API (globally accessible, no auth required) as a fallback since Polymarket is geo-restricted in some regio **Actually calls Manifold Markets, play money: its odds are not expectations.** |
| `trading_economics_data` | Fetches sovereign credit ratings and government bond yields from the Trading Economics API. **Paid key; this script only fetches credit ratings and bond yields.** |
