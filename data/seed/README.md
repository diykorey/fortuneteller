# Seed data

Committed CSVs that the embedded store loads at `fortuneteller seed` time, so the repo
clones-and-runs offline with no Notion credentials (see [M0-06](../../docs/m0-tickets.md)). Headers
match the DuckDB tables in `schema.sql`; enum columns use the M0-03 enum *values* (lowercase, e.g.
`both`, `conditional`, `equity_index`).

| File | Table | Rows | Status |
| --- | --- | --- | --- |
| `event_types.csv` | event_types | 31 | Full. Polarity authoritative; **tier inferred** from the 8-tier scheme. |
| `instruments.csv` | instruments | 12 | Representative subset of 55 — real Notion rows, mapped to the asset-class enum. |
| `effect_size_seed.csv` | effect_size_seed | 15 | **Placeholder seeds** — directionally consistent with the specs, *numbers not authoritative*. |
| `news_sources.csv` | news_sources | 25 | Full ranked stack (Notion DB has ~27). |
| `countries.csv` | countries | 10 | Representative subset of 50; GDP figures approximate; `platforms_in_list`/`coverage_gap` blank. |

## Why some tables are partial

The standalone Notion databases can't be bulk-exported with read-only API access (the SQL /
view-query endpoints require a paid Notion plan). The narrative pages supplied the full
`event_types` and `news_sources` data; the rest are correct-schema samples per the M0-06 fallback
("commit a non-empty representative subset …"). The full tables live in the project's Notion
workspace. See [`docs/data/README.md`](../../docs/data/README.md) for the full provenance breakdown.

## Cross-references

- `effect_size_seed.instrument` keys instruments by **symbol** (e.g. `SPY / ES`), matching
  `instruments.symbol` and the `query-demo` lookup `get_effect_size("CPI / inflation surprise",
  "SPY / ES")`.
- `effect_size_seed.event_type` and `event_types.event_type` use the same canonical keys.

## Full data

The complete tables live in the project's Notion workspace; re-export the subsets here from there
when the build scope needs them.
