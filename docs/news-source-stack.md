# Spec — News-Source Stack & Coverage

Built for the project's event taxonomy and platform list. Ranked by **reliability × speed**, then
mapped to every event and market group, with a gap analysis. (Built when the taxonomy was 28
events / 109 platforms; since extended to 31 / 132.)

**Speed legend:** us/ms = co-located machine-readable feed; sec = fast wire/API/alert; release =
official at published time (poll); 15-min = GDELT cadence; min-hr = curated.

**Cost legend:** Free / `$` indie API / `$$` prosumer / `$$$` specialist / `$$$$` institutional.

## Part 1 — Ranked master source list

| # | Source | Type | Domains it covers best | Speed | Reliability | API / access | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | LSEG / Reuters (Headlines Direct) | Wire + machine-readable | Everything; M&A exclusives, macro, geopolitics | us-ms / sec | Very high | Yes (institutional) | $$$$ |
| 2 | Bloomberg (Terminal, B-PIPE, News API) | Wire + data + machine-readable | Everything; rates, FX, credit, corporate, commodities | us-ms / sec | Very high | Yes (institutional) | $$$$ |
| 3 | Dow Jones Newswires / News Analytics | Wire + machine-readable headline feed | Corporate, macro, regulatory, M&A; co-located NY4 | us-ms | Very high | Yes (institutional) | $$$$ |
| 4 | AlphaFlash (Deutsche Börse) | Machine-readable macro feed | Scheduled macro data (CPI, NFP, GDP, PMI), 400+ indicators | us-sec (often ahead) | Very high | Yes | $$$ |
| 5 | Associated Press (AP) | Wire | Breaking global, politics, geopolitics, disasters | sec | Very high | Yes | $$–$$$ |
| 6 | Government / central-bank primary (Fed, ECB, BoJ, BoE; BLS, BEA; SEC EDGAR; CFTC; EIA; NOAA/NHC; USGS) | Official | Authoritative origin for rates, macro, filings, energy, weather, quakes | release (poll) | Authoritative | Mostly free APIs/RSS | Free |
| 7 | Benzinga (Pro, News API, Squawk) | Trader news + API | Equities, crypto, M&A, ratings, halts; affordable | sec | High | Yes | $$ |
| 8 | Moody's NewsEdge / Selerity / Nasdaq Event-Driven | Filtered low-latency news + econ | Macro indicators, filtered news, FX/sovereign | us-sec | High | Yes | $$$ |
| 9 | GDELT Project | Open event firehose | Geopolitics, wars, protests, coups, sentiment (100+ languages) | 15-min | Medium (noisy) | Yes (free) | Free |
| 10 | X / Twitter (X API) | Social firehose | Fastest unofficial breaking signal; viral/meme, scandals | sec (noisy) | Low-medium | Yes | $$ |
| 11 | CoinDesk / The Block | Crypto media + data | Crypto news, regulation, exchange events | sec-min | High (crypto) | Yes | $–$$ |
| 12 | CoinGecko / CryptoCompare news API | Crypto data + news aggregation | Crypto prices + news from 100-150+ sources | sec | High | Yes | Free–$ |
| 13 | On-chain alerts (Whale Alert, Nansen, Arkham, Lookonchain) | On-chain intelligence | Crypto hacks/exploits, whale moves, depegs | sec | Medium-high | Yes | $$–$$$ |
| 14 | Polymarket / Kalshi APIs | Prediction-market odds | Elections, geopolitics, Fed/CPI, regulatory — probabilities as leading signal | sec | Medium (FL bias) | Yes | Free |
| 15 | ACLED | Curated conflict/protest data | Armed conflict, civil unrest, protests (structured) | min-hr | High | Yes | Free/$$ |
| 16 | S&P Global Commodity Insights (Platts) / Argus / ICIS | Commodity price reporting | Oil, gas, power, metals, carbon, ags benchmarks | sec-min | Very high | Yes | $$$ |
| 17 | OPEC + IEA + EIA | Official energy | OPEC decisions, supply/demand, US inventories | release | Authoritative | RSS/API | Free |
| 18 | Lloyd's List / TradeWinds / Baltic Exchange / Freightos | Shipping & freight | Freight rates (Baltic Dry, FBX), disruptions, marine | sec-hr | High | Partial API | $$–$$$ |
| 19 | Artemis / Lloyd's / reinsurance press + NHC | Insurance / cat | Hurricanes, cat-bond pricing, reinsurance, ILS | hr | High | Mostly web | $–$$$ |
| 20 | EEX / ICE / national registries | Carbon & power | EU ETS (EUA), RGGI/CCA, power-market policy & prices | sec-release | High | Yes | $$–$$$ |
| 21 | Sports data feeds (Sportradar, Genius Sports, Betfair API) | Sports + odds | Sports outcomes/odds | sec | High | Yes | $$–$$$ |
| 22 | FT / WSJ / CNBC / Reuters.com / Economist | Premium media | Confirmation + analysis across all domains | min | Very high | RSS/site | $–$$ |
| 23 | Alpha Vantage / Finnhub / Marketaux / NewsAPI / Tiingo | Indie data + news APIs | Equities/FX/crypto prices + tagged news for builders | sec-min | Medium | Yes | Free–$ |
| 24 | Yahoo Finance / Google News / Investing.com | Retail aggregators | Broad confirmation, economic calendars | min | Medium | Partial | Free |
| 25 | Art / private-market press (ArtNet, Artprice, PitchBook, Forge) | Niche | Auctions, NFT cycles, pre-IPO/secondary marks | hr-days | Medium-high | Partial | $$–$$$ |

**Practical stack picks by budget**

- *Institutional / latency-critical:* LSEG or Bloomberg + AlphaFlash + Dow Jones + on-chain
  alerts + X firehose.
- *Prosumer build:* Benzinga + gov primary feeds + GDELT + CoinGecko/CoinDesk + Polymarket/Kalshi
  + X — covers ~90% of the taxonomy cheaply.
- *Free-only MVP:* gov primary + GDELT + CoinGecko + Polymarket/Kalshi + AP headlines + USGS/NOAA.

## Part 2 — Coverage by event (all mapped)

Primary = fastest/most reliable trigger; Confirm = corroboration. Every event has at least one
source.

| Event | Primary source(s) | Confirm |
| --- | --- | --- |
| Pandemics / health emergencies | WHO + gov health agencies; AP/Reuters | GDELT, FT |
| Banking / financial crises | Reuters/Bloomberg/DJ; Fed/FDIC; on-chain | Benzinga |
| Major wars / great-power conflict | AP/Reuters; GDELT; ACLED; OSINT | Polymarket |
| Central-bank decisions & guidance | Fed/ECB/BoJ/BoE primary; AlphaFlash; LSEG/Bloomberg | Benzinga |
| Tariffs / trade war / sanctions | USTR / OFAC / EU OJ; Reuters/DJ | Polymarket, GDELT |
| Sovereign-debt crises | Reuters/Bloomberg; rating agencies; CDS desks | FT |
| CPI / inflation | BLS primary; AlphaFlash; LSEG/Bloomberg | Benzinga |
| NFP / labor | BLS primary; AlphaFlash | Benzinga |
| Other macro (GDP, PMI, PCE, retail, claims) | BEA/Census/ISM/S&P PMI; AlphaFlash | Investing.com |
| Elections | Polymarket/Kalshi (leading); AP/Decision Desk | PredictIt, odds |
| Geopolitical escalations / terror | AP/Reuters; GDELT; OSINT | Polymarket |
| Coups / regime change / capital controls | AP/Reuters; GDELT; ACLED | OFAC |
| OPEC / energy supply | OPEC/EIA/IEA; Platts/Argus; Reuters | ICE/CME prices |
| Natural disasters | NOAA/NHC/USGS; Artemis; reinsurance press | AP |
| Extreme weather / climate policy | NOAA; EEX/ICE (carbon); EU/UNFCCC | Platts |
| Corporate scandals / fraud / bankruptcy | SEC EDGAR (8-K); Reuters/DJ; on-chain | Benzinga, dockets |
| Earnings | SEC EDGAR + IR; Benzinga; Bloomberg/LSEG | Refinitiv estimates |
| M&A | LSEG Headlines Direct / DJ (exclusives); SEC EDGAR | Benzinga |
| Regulatory / legal | SEC/CFTC/FDA/FTC/DOJ/FAA; CourtListener | Reuters |
| Leadership changes | SEC 8-K; company IR; Reuters/Benzinga | X |
| Cyber attacks / hacks / outages | On-chain alerts; company 8-K; Cloudflare Radar; security press | X, AP |
| Social / viral / meme | X/Twitter firehose; Reddit; Google Trends | Benzinga |
| Strikes / protests / unrest | ACLED + GDELT; AP; local press | X |
| Freight / shipping | Baltic Exchange / Freightos / Lloyd's List | AIS trackers |
| Carbon / emissions policy | EEX / ICE; EU Commission; ICIS carbon | Platts |
| Credit-rating actions | Moody's / S&P / Fitch releases; Reuters | CDS desks |
| NFT / art | OpenSea/Blur/Magic Eden APIs; ArtNet; CoinDesk | X |
| Real-estate / housing data | Census/NAR/Case-Shiller; Fed; Zillow research | MBA |
| AI / tech breakthroughs | Company/research blogs; X; Benzinga; exchange feeds | CoinDesk |
| Fiscal: debt-ceiling / shutdown | Congress/Treasury; Reuters; Polymarket | FT |
| Stablecoin / DeFi depeg | On-chain alerts; CoinDesk; CoinGecko | X |

## Part 3 — Coverage by market group (all 19)

| Market group | Best source(s) |
| --- | --- |
| Equities | LSEG/Bloomberg/DJ; SEC EDGAR; Benzinga; exchange feeds |
| Forex | AlphaFlash + central banks; LSEG/EBS; Bloomberg FXGO |
| Bonds / fixed income | Bloomberg/Tradeweb/MarketAxess; Fed/Treasury; BLS/BEA |
| Derivatives | CME/ICE/CBOE feeds; LSEG/Bloomberg |
| Commodities | Platts/Argus/ICIS; EIA/OPEC/IEA; exchange feeds |
| Crypto | CoinDesk/CoinGecko/CryptoCompare; on-chain alerts; exchange APIs |
| Prediction markets | Polymarket/Kalshi APIs; CFTC |
| Sports betting | Sportradar/Genius Sports; Betfair API; league feeds |
| Volatility (VIX) | CBOE feed; Bloomberg/LSEG; macro primary |
| Credit / CDS | Bloomberg/Tradeweb/MarketAxess; rating agencies; ICE Credit |
| Energy / power | EEX/Nord Pool/EPEX/PJM; Platts/Argus; EIA |
| Carbon / emissions | EEX/ICE; EU Commission; ICIS carbon |
| Freight / shipping | Baltic Exchange/Freightos/Lloyd's List; AIS |
| Weather | NOAA/NWS/NHC; CME weather; Speedwell Climate |
| Real estate | Census/NAR/Case-Shiller; Fed; Zillow; REIT filings |
| Private markets | PitchBook/Forge data; SEC; tech-comp earnings |
| Art / collectibles | ArtNet/Artprice; auction-house results |
| NFT | OpenSea/Blur/Magic Eden APIs; on-chain; CoinDesk |
| Insurance / reinsurance | Artemis/Lloyd's; NOAA/NHC; reinsurance press |

## Part 4 — Gap analysis

**Coverage is complete** — every event and market group has at least one reliable source.
Quality/speed is uneven:

- **Slow/specialist domains** (acceptable — react in hours-days): freight, carbon, weather,
  insurance/cat, NFT/art, private markets. Curated feeds (Lloyd's List, Platts, Artemis, NOAA,
  EEX) suffice.
- **Noisy/needs filtering:** GDELT and X are fastest for unrest/geopolitics/viral but need NLP +
  source-tiering; pair with ACLED/AP to confirm.
- **Prediction markets double as source and market:** Polymarket/Kalshi odds are a leading signal
  but carry favorite-longshot bias.

**List updates (since applied):** added 3 events (AI/tech, fiscal/shutdown, stablecoin depeg) and
platforms (Deutsche Börse Xetra, SIX, Borsa Italiana, Tadawul, BSE; Tether, Circle; Betano,
Stake), plus national/regional press and state-wire sources.
