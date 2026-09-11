# Top Countries by GDP — Coverage

The country layer used by entity-linking and to check that the news stack covers the world's
largest economies (the Notion table ranks the top 50 by GDP and maps each to its trading platforms,
any coverage gap, and a primary news source).

> **Completeness: representative subset — 10 of 50, with approximate figures.** The Notion table's
> exact `gdp_2026e`, `platforms_in_list`, and `coverage_gap` values could not be exported. Country
> rank and a plausible primary news source are shown; **GDP figures are rough nominal estimates**
> and `platforms_in_list` / `coverage_gap` are left blank (`—`) rather than guessed. The
> authoritative table lives in the Notion source. Columns match the `countries` CSV.

| Rank | Country | GDP 2026e (≈ USD tn) | Platforms in list | Coverage gap | Primary news source |
| --- | --- | --- | --- | --- | --- |
| 1 | United States | ~30.3 | — | — | Bloomberg / Reuters / AP |
| 2 | China | ~19.5 | — | — | Reuters / Caixin |
| 3 | Germany | ~4.9 | — | — | Reuters / Handelsblatt |
| 4 | Japan | ~4.4 | — | — | Nikkei / Reuters |
| 5 | India | ~4.3 | — | — | Reuters / Economic Times |
| 6 | United Kingdom | ~3.7 | — | — | Reuters / FT |
| 7 | France | ~3.3 | — | — | Reuters / Les Échos |
| 8 | Italy | ~2.5 | — | — | Reuters / Il Sole 24 Ore |
| 9 | Canada | ~2.4 | — | — | Reuters / Globe and Mail |
| 10 | Brazil | ~2.3 | — | — | Reuters / Valor Econômico |

The full Notion table extends through rank 50 and records, per country, how many of the 132 tracked
[trading platforms](platforms.md) sit in that market and whether any coverage gap remains.

How each country maps onto the coarse `Region` buckets (and why China/India resolve to `em` while
Japan stays `asia`) is defined by the precedence rule in
[Region segmentation — rationale](region-segmentation.md).
