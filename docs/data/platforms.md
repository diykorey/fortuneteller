# Markets & Trading Platforms

The 132 venues and platforms across which the tracked instruments trade — exchanges, ECNs, crypto
venues, prediction markets, and betting platforms. Used to scope coverage (which markets a
detected event can move) and to map countries → venues.

> **MVP build scope: none.** The provable core (scheduled-macro × ~5 liquid instruments) needs no
> platform breadth — this whole table is **post-proof reference**. See
> [mvp-architecture.md](../mvp-architecture.md).

> **Completeness: representative subset.** The full 132-row Notion database could not be exported
> with the available read-only access, and there is no platforms seed CSV in the M0 scope. The list
> below is a **representative sample of well-known venues by market group**, not the authoritative
> table. The full set lives in the Notion source.

| Market group | Representative platforms |
| --- | --- |
| Equities — US | NYSE, Nasdaq, Cboe (BZX/EDGX) |
| Equities — Europe | London Stock Exchange (LSEG), Deutsche Börse (Xetra), Euronext, SIX (Swiss), Borsa Italiana |
| Equities — Asia/EM | Japan Exchange (JPX), Hong Kong (HKEX), Shanghai/Shenzhen, NSE/BSE (India), Saudi Tadawul |
| Derivatives / futures | CME Group, ICE, Cboe (options/VIX), Eurex |
| Commodities | COMEX, NYMEX, LBMA, EEX (power/carbon) |
| Bonds / rates | Tradeweb, MarketAxess, BrokerTec |
| FX | EBS, LSEG FX, Bloomberg FXGO |
| Crypto (CeFi) | Binance, Coinbase, Kraken, OKX |
| Stablecoin issuers | Tether (USDT), Circle (USDC) |
| Prediction markets | Polymarket, Kalshi, PredictIt |
| Sports betting | Betfair, Betano, Stake |

The taxonomy spans 19 market groups in total (see
[News-Source Stack — Part 3](../news-source-stack.md#part-3--coverage-by-market-group-all-19)):
equities, forex, bonds/fixed income, derivatives, commodities, crypto, prediction markets, sports
betting, volatility, credit/CDS, energy/power, carbon/emissions, freight/shipping, weather, real
estate, private markets, art/collectibles, NFT, and insurance/reinsurance.
