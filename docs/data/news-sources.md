# News Sources (Ranked)

The source stack the detection pipeline ingests, ranked by **reliability × speed**. Each source's
`reliability` and `speed` become the weights the corroboration model (Detection spec, Part A) uses.

> **Completeness:** the 25-source ranked stack below is reproduced in full from the
> [News-Source Stack spec](../news-source-stack.md). The Notion database carries ~27 rows (a couple
> of regional/state-wire additions); the exact set lives in the Notion source.
> Columns match the `news_sources` seed CSV: rank, source, type, domains_covered, speed,
> reliability, api_access, cost.

**Speed legend:** us/ms = co-located machine-readable; sec = fast wire/API/alert; release = official
at published time; 15-min = GDELT cadence; min-hr = curated.
**Cost legend:** Free / `$` indie / `$$` prosumer / `$$$` specialist / `$$$$` institutional.

| Rank | Source | Type | Domains covered | Speed | Reliability | API / access | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | LSEG / Reuters (Headlines Direct) | Wire + machine-readable | Everything; M&A exclusives, macro, geopolitics | us-ms / sec | Very high | Yes (institutional) | $$$$ |
| 2 | Bloomberg (Terminal, B-PIPE, News API) | Wire + data + machine-readable | Everything; rates, FX, credit, corporate, commodities | us-ms / sec | Very high | Yes (institutional) | $$$$ |
| 3 | Dow Jones Newswires / News Analytics | Wire + machine-readable headline feed | Corporate, macro, regulatory, M&A; co-located NY4 | us-ms | Very high | Yes (institutional) | $$$$ |
| 4 | AlphaFlash (Deutsche Börse) | Machine-readable macro feed | Scheduled macro data (CPI, NFP, GDP, PMI), 400+ indicators | us-sec | Very high | Yes | $$$ |
| 5 | Associated Press (AP) | Wire | Breaking global, politics, geopolitics, disasters | sec | Very high | Yes | $$–$$$ |
| 6 | Government / central-bank primary | Official | Rates, macro, filings, energy, weather, quakes | release (poll) | Authoritative | Mostly free APIs/RSS | Free |
| 7 | Benzinga (Pro, News API, Squawk) | Trader news + API | Equities, crypto, M&A, ratings, halts | sec | High | Yes | $$ |
| 8 | Moody's NewsEdge / Selerity / Nasdaq Event-Driven | Filtered low-latency news + econ | Macro indicators, filtered news, FX/sovereign | us-sec | High | Yes | $$$ |
| 9 | GDELT Project | Open event firehose | Geopolitics, wars, protests, coups, sentiment | 15-min | Medium (noisy) | Yes (free) | Free |
| 10 | X / Twitter (X API) | Social firehose | Fastest unofficial breaking signal; viral/meme, scandals | sec (noisy) | Low-medium | Yes | $$ |
| 11 | CoinDesk / The Block | Crypto media + data | Crypto news, regulation, exchange events | sec-min | High (crypto) | Yes | $–$$ |
| 12 | CoinGecko / CryptoCompare news API | Crypto data + news aggregation | Crypto prices + news from 100-150+ sources | sec | High | Yes | Free–$ |
| 13 | On-chain alerts (Whale Alert, Nansen, Arkham, Lookonchain) | On-chain intelligence | Crypto hacks/exploits, whale moves, depegs | sec | Medium-high | Yes | $$–$$$ |
| 14 | Polymarket / Kalshi APIs | Prediction-market odds | Elections, geopolitics, Fed/CPI, regulatory | sec | Medium (FL bias) | Yes | Free |
| 15 | ACLED | Curated conflict/protest data | Armed conflict, civil unrest, protests | min-hr | High | Yes | Free/$$ |
| 16 | S&P Global Commodity Insights (Platts) / Argus / ICIS | Commodity price reporting | Oil, gas, power, metals, carbon, ags | sec-min | Very high | Yes | $$$ |
| 17 | OPEC + IEA + EIA | Official energy | OPEC decisions, supply/demand, US inventories | release | Authoritative | RSS/API | Free |
| 18 | Lloyd's List / TradeWinds / Baltic Exchange / Freightos | Shipping & freight | Freight rates, disruptions, marine | sec-hr | High | Partial API | $$–$$$ |
| 19 | Artemis / Lloyd's / reinsurance press + NHC | Insurance / cat | Hurricanes, cat-bond pricing, reinsurance, ILS | hr | High | Mostly web | $–$$$ |
| 20 | EEX / ICE / national registries | Carbon & power | EU ETS (EUA), RGGI/CCA, power-market policy & prices | sec-release | High | Yes | $$–$$$ |
| 21 | Sports data feeds (Sportradar, Genius Sports, Betfair API) | Sports + odds | Sports outcomes/odds | sec | High | Yes | $$–$$$ |
| 22 | FT / WSJ / CNBC / Reuters.com / Economist | Premium media | Confirmation + analysis across all domains | min | Very high | RSS/site | $–$$ |
| 23 | Alpha Vantage / Finnhub / Marketaux / NewsAPI / Tiingo | Indie data + news APIs | Equities/FX/crypto prices + tagged news | sec-min | Medium | Yes | Free–$ |
| 24 | Yahoo Finance / Google News / Investing.com | Retail aggregators | Broad confirmation, economic calendars | min | Medium | Partial | Free |
| 25 | Art / private-market press (ArtNet, Artprice, PitchBook, Forge) | Niche | Auctions, NFT cycles, pre-IPO/secondary marks | hr-days | Medium-high | Partial | $$–$$$ |

For coverage-by-event and coverage-by-market-group matrices and the budget-tiered stack picks, see
the [News-Source Stack & Coverage](../news-source-stack.md) spec.
