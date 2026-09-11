# Instruments / Tickers

The instrument universe the predictor maps events onto (~55 in Notion). Each is the column key of
the effect-size matrix and a node in the entity-linking gazetteer.

> **MVP build scope (~5):** the provable core predicts only **SPY / ES**, a rates benchmark
> (**BUND / FGBL** or UST 10Y), **DXY**, **Gold (GC / XAU)**, and **VIX** — all present in the
> subset below. The rest of the universe is **post-proof reference**, not build scope. See
> [mvp-architecture.md](../mvp-architecture.md).

> **Completeness: representative subset — 12 of 55.** These rows are pulled directly from the
> Notion database (real `Symbol` / `Asset Class` / `Region` / venue / notes), chosen to span every
> asset class. The full 55 live in the Notion source. The `asset_class`
> values below use the Notion labels; the `instruments` seed CSV maps them to the M0-03 enum
> (e.g. "Equity index" → `equity_index`, "Rates / Bond" → `rates_bond`, "Credit / CDS" →
> `credit_cds`).

| Symbol | Instrument | Asset class | Region | Primary venue / source | Notes |
| --- | --- | --- | --- | --- | --- |
| SPY / ES | S&P 500 | Equity index | US | NYSE / Cboe / CME | Broad US market benchmark; the default 'risk-on/off' gauge. |
| NVDA | Nvidia | Single stock | US | Nasdaq | AI bellwether; can move whole indices (DeepSeek Jan 2025 −17%). |
| AAPL | Apple | Single stock | US | Nasdaq | Largest weight; China-supply & tariff sensitive. |
| GC / XAU | Gold | Commodity | Global | COMEX (CME) / LBMA | Safe-haven & real-rate/inflation hedge. |
| BRN | Brent crude oil | Commodity | Global | ICE | Global oil benchmark; geopolitics-sensitive. |
| BTC | Bitcoin | Crypto | Global | Binance / Coinbase / CME | Crypto bellwether; liquidity/regulation/risk sensitive. |
| USDC | USDC (stablecoin peg) | Crypto | Global | On-chain / Circle | Peg = systemic-stress gauge (depegged Mar 2023). |
| DXY | US Dollar Index | FX | Global | ICE | Broad USD; rises on risk-off and hawkish Fed. |
| BUND / FGBL | German Bund 10Y | Rates / Bond | Europe | Eurex | Eurozone risk-free benchmark. |
| VIX | VIX (equity volatility) | Volatility | US | Cboe | The 'fear gauge'; spikes on every risk-off event. |
| CDS | Sovereign CDS (EM / periphery) | Credit / CDS | EM | ICE / Markit | Default-risk gauge (Russia 2022, Italy, EM). |
| BDI | Baltic Dry Index | Freight | Global | Baltic Exchange | Dry-bulk freight; China-demand & disruption gauge. |

**Asset classes in the full universe** (M0-03 enum): equity_index, sector_etf, single_stock,
rates_bond, fx, commodity, crypto, volatility, credit_cds, prediction, carbon, freight,
insurance_linked. Other instruments in Notion not shown above include sector ETFs (Semiconductors,
Regional banks, Financials, Utilities, Gold miners, Airlines), more indices (Nikkei 225, FTSE 100,
KOSPI, TAIEX), single names, Ethereum/Solana, the MOVE index, and others.

## Region semantics

`region` (the `Region` enum — `us | europe | asia | em | global`) means the **dominant macro-driver
regime** an instrument responds to — *which central-bank / macro bloc's surprises move it most* —
**not** its listing venue or issuer domicile. (So VIX is `us` because it tracks US-equity vol, even
though it's a "global fear gauge"; the German Bund is `europe` because it follows the ECB.)

**Precedence rule** — gives every instrument exactly one home and kills the geography-vs-development
overlap:

1. **No single regional driver → `global`.** Cross-region benchmarks priced off worldwide
   supply/demand or broad risk rather than one bloc: gold, oil, crypto, the broad-USD index (DXY),
   the Baltic Dry Index.
2. **Otherwise classify by macro bloc; development status wins over geography.** Emerging economies
   → `em` (**China, India, Brazil → `em`**, not `asia`); developed economies by geography → `us` /
   `europe` / `asia` (**Japan → `asia`**; the UK and the eurozone → `europe`; the US and
   US-correlated developed North America, incl. Canada → `us`).

Applying this to the seed above reproduces every current label, so no data changes are needed — it
just makes future labeling deterministic. `region` is descriptive metadata, **not** a calibration
axis (calibration conditions on VIX bucket and asset class — see
[Detection & Calibration](../detection-and-calibration.md)); the five buckets are deliberately
coarse for the MVP. Full reasoning, known limits, and the post-proof refinement plan:
[Region segmentation — rationale](region-segmentation.md).
