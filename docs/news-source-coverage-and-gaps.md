# News Source Coverage & Gaps

Coverage check for the project's event taxonomy and platform list. Primary = fastest/most reliable
trigger; Confirm = corroboration. **Every event and market group maps to at least one reliable
source.**

> This is the standalone coverage page. The same matrices, with the ranked master source list,
> also appear in [News-Source Stack & Coverage](news-source-stack.md).

## Part 1 — Coverage by event (all 28+3)

| Event | Primary source(s) | Confirm |
| --- | --- | --- |
| Pandemics / health emergencies | WHO + gov health agencies; AP/Reuters | GDELT, FT |
| Banking / financial crises | Reuters/Bloomberg/DJ; Fed/FDIC; on-chain (depegs) | Benzinga |
| Major wars / great-power conflict | AP/Reuters; GDELT; ACLED; OSINT | Polymarket |
| Central-bank decisions & guidance | Fed/ECB/BoJ/BoE primary; AlphaFlash; LSEG/Bloomberg | Benzinga |
| Tariffs / trade war / sanctions | USTR / OFAC / EU OJ; Reuters/DJ | Polymarket, GDELT |
| Sovereign-debt crises | Reuters/Bloomberg; rating agencies; CDS desks | FT |
| CPI / inflation | BLS primary; AlphaFlash; LSEG/Bloomberg | Benzinga |
| NFP / labor | BLS primary; AlphaFlash | Benzinga |
| Other macro (GDP, PMI, PCE, retail, claims) | BEA/Census/ISM/S&P PMI; AlphaFlash | Investing.com calendar |
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
| Real-estate / housing data | Census/NAR/Case-Shiller; Fed; Zillow | MBA |
| AI / tech breakthroughs (new) | Company/research blogs; X; Benzinga; exchange feeds | CoinDesk |
| Fiscal: debt-ceiling / shutdown (new) | Congress/Treasury; Reuters; Polymarket | FT |
| Stablecoin / DeFi depeg (new) | On-chain alerts; CoinDesk; CoinGecko | X |

## Part 2 — Coverage by market group (all 19)

| Market group | Best source(s) |
| --- | --- |
| Equities | LSEG/Bloomberg/DJ; SEC EDGAR; Benzinga; exchange feeds |
| Forex | AlphaFlash + central banks; LSEG/EBS; Bloomberg FXGO |
| Bonds / fixed income | Bloomberg/Tradeweb/MarketAxess; Fed/Treasury; BLS/BEA |
| Derivatives | CME/ICE/CBOE feeds; LSEG/Bloomberg |
| Commodities | Platts/Argus/ICIS; EIA/OPEC/IEA; exchange feeds |
| Crypto | CoinDesk/CoinGecko/CryptoCompare; on-chain alerts; exchange APIs |
| Prediction markets | Polymarket/Kalshi APIs (are the data); CFTC |
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

## Part 3 — Gap analysis

**Coverage is complete** — every event and market group has at least one reliable source.
Quality/speed is uneven:

- **Slow/specialist domains** (acceptable — they react in hours-days): freight, carbon, weather,
  insurance/cat, NFT/art, private markets. Curated feeds (Lloyd's List, Platts, Artemis, NOAA,
  EEX) suffice.
- **Noisy / needs filtering:** GDELT and X are fastest for unrest/geopolitics/viral but need NLP +
  source-tiering; pair with ACLED/AP to confirm.
- **Prediction markets double as source and market:** Polymarket/Kalshi odds are a leading signal
  but carry favorite-longshot bias.

**List updates already applied:**

- Added 3 events: AI / technology breakthroughs; Fiscal (debt-ceiling/shutdown/budget);
  Stablecoin / DeFi depeg.
- Added platforms: Deutsche Börse (Xetra), SIX, Borsa Italiana, Saudi Tadawul, BSE; Tether,
  Circle; Betano, Stake.

**Recommended stacks**

- Institutional / latency-critical: LSEG or Bloomberg + AlphaFlash + Dow Jones + on-chain alerts
  + X firehose.
- Prosumer build: Benzinga + government primary feeds + GDELT + CoinGecko/CoinDesk +
  Polymarket/Kalshi + X (~90% of taxonomy, cheaply).
- Free-only MVP: gov primary + GDELT + CoinGecko + Polymarket/Kalshi + AP + USGS/NOAA.
