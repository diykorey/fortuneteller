# Market-Moving Events (Ranked)

The event taxonomy — 31 types, each with a polarity (direction of the market reaction) and a tier
(systemic importance). This is the label space the classifier maps into and the row key of the
effect-size matrix.

> **MVP build scope:** only the **scheduled-macro** events are in the provable core — **CPI /
> inflation surprise (#7), NFP / labor data (#8), Central-bank decision (#4)** (optionally Other
> macro, #9). The other 27 types are **post-proof reference**, not build scope. Don't implement
> against the full taxonomy until the core is proven — see [mvp-architecture.md](../mvp-architecture.md).

> **Completeness:** event names and **polarity** are authoritative (from the
> [Event Polarity spec](../event-polarity-and-classifier-prompts.md)). **Tier** is *inferred here*
> from the documented 8-tier scheme — the per-event tier column lives only in the Notion database.
> Events 29–31 were added after the polarity spec was written, so their polarity is inferred too
> (marked *inf.*). Reconcile with the Notion source.

## Tier scheme

| Tier | Name |
| --- | --- |
| 1 | Systemic / Black Swan |
| 2 | Policy & Macro |
| 3 | Scheduled Macro Data |
| 4 | Political & Geopolitical |
| 5 | Commodity / Energy / Climate |
| 6 | Corporate / Idiosyncratic |
| 7 | Tech / Social / Behavioral |
| 8 | Niche / Lower Impact |

## Events

| # | Event | Tier | Polarity | What makes it + vs − |
| --- | --- | --- | --- | --- |
| 1 | Global pandemics & health emergencies | 1 | Negative | Demand collapse + risk-off; only narrow exceptions (vaccine names, gold, staples) go up. |
| 2 | Major financial / banking-system crises | 1 | Negative | Confidence/funding shock; broad bearish, safe-havens (UST, gold) the only beneficiaries. |
| 3 | Major interstate wars / great-power conflict | 1 | Both | − for broad equities/risk; + for oil, gas, gold, defense, ag commodities. |
| 4 | Central-bank decisions & forward guidance | 2 | Both | Dovish surprise / cut = +; hawkish surprise / hike = −. Pure surprise play. |
| 5 | Major tariff / trade-war announcements & sanctions | 2 | Both | Escalation = − (risk-off); de-escalation/removal = +. Protected sectors can buck the move. |
| 6 | Sovereign-debt crises and defaults | 1 | Negative | Risk-free benchmark repricing cascades; bearish for affected sovereign + EM/credit. |
| 7 | CPI / inflation surprises | 3 | Both | Cooler-than-expected = +; hotter = −. Classic surprise event. |
| 8 | Non-farm payrolls (NFP) & labor data | 3 | Both | Direction depends on surprise AND regime (strong jobs can be − if it removes cuts). |
| 9 | Other macro data (GDP, PMI, retail, PCE, claims) | 3 | Both | Beat/miss vs consensus; regime-dependent. |
| 10 | National elections | 4 | Both | Depends on which outcome wins vs. what was priced, and the winner's policy mix. |
| 11 | Geopolitical escalations / terrorism | 4 | Negative | Reliable risk-off shock; oil/gold/defense rise but broad market falls. |
| 12 | Coups, regime change, sanctions, capital controls | 4 | Both | − for the affected sovereign/EM; + for substitute producers / rival exporters. |
| 13 | OPEC+ supply decisions & energy disruptions | 5 | Both | Cut/disruption = + for oil & energy equities, − for airlines/consumers; increase = opposite. |
| 14 | Natural disasters | 5 | Both | − on impact (insurers, region); + later for reinsurance pricing, cat-bonds, rebuilding. |
| 15 | Extreme weather & climate-policy announcements | 5 | Both | Tightening = + carbon price, − emitters; weather extremes = + energy/ags, − consumers. |
| 16 | Corporate scandals, frauds & mega-bankruptcies | 6 | Negative | Bearish for the firm and often peers/CDS; only shorts and competitors gain. |
| 17 | Earnings releases | 6 | Both | Beat + raise = +; miss / weak guide = −. Surprise vs. consensus and guidance. |
| 18 | M&A announcements | 6 | Both | Target almost always + (premium); acquirer often − (esp. stock-financed). |
| 19 | Regulatory & legal events | 6 | Both | Approval / favorable ruling = +; lawsuit / ban / fine / grounding = −. |
| 20 | Leadership changes & C-suite departures | 6 | Both | Depends on who, why, and whether seen as upgrade or instability. |
| 21 | Cyber attacks, hacks & IT outages | 7 | Negative | Bearish for victim; cybersecurity vendors can rise (narrow exception). |
| 22 | Social-media / viral / meme-driven events | 7 | Both | Positive virality = +; controversy / boycott / negative virality = −. |
| 23 | Strikes, labor unrest, civil protests | 7 | Negative | Supply disruption + political risk; bearish for affected sectors/region. |
| 24 | Freight & shipping disruptions | 8 | Both | + for freight rates & shipping equities; − for importers, retailers, consumers. |
| 25 | Carbon & emissions policy events | 5 | Both | Tightening / ambition = + carbon price, − emitters; loosening = opposite. |
| 26 | Routine credit-rating agency actions | 6 | Both | Upgrade = +; downgrade = −. Clean binary. |
| 27 | NFT / collectibles / art events | 8 | Both | Boom / hype / strong sale = +; bust / fraud / weak sale = −. |
| 28 | Real-estate / housing data | 3 | Both | Strong data = + for builders/REITs (unless it lifts rates); weak data = −. |
| 29 | AI / technology breakthroughs | 7 | Both *inf.* | Breakthrough/leadership = + for winners; disruption (e.g. DeepSeek) = − for incumbents. |
| 30 | Fiscal: debt-ceiling / shutdown / budget | 4 | Both *inf.* | Brinkmanship/shutdown = − (risk-off, UST/USD wobble); resolution = +. |
| 31 | Stablecoin / DeFi depeg | 7 | Both *inf.* | Depeg = − for the coin & crypto risk; can be + for competitors / safe stablecoins. |

**Polarity summary**

- **Reliably Negative (7):** pandemics, banking crises, sovereign-debt crises, geopolitical/terror,
  corporate scandals, cyber attacks, strikes.
- **Both / conditional (21 + 3 new):** everything else — wars (asset-split) and all data, policy,
  and corporate-outcome events.
- **Reliably Positive (0 standalone):** positivity is the favorable *branch* of a Both event.
