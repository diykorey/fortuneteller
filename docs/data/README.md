# Reference data

The FortuneTeller knowledge base is a set of Notion databases that the pipeline reads as config.
This directory mirrors them as markdown; the machine-readable seed lives in
[`/data/seed`](../../data/seed).

> **Scope note:** these full tables (31 events, 55 instruments, 132 platforms) are **post-proof
> reference**, *not* the build scope. The MVP calibrates only the **provable core** — scheduled-macro
> events × ~5 instruments — see [mvp-architecture.md](../mvp-architecture.md). Don't implement
> against the full breadth until that core is proven.

## Provenance & completeness

The Notion **narrative/spec pages** are reproduced in full elsewhere in [`/docs`](../README.md).
The **standalone databases**, however, can't be bulk-exported with the read-only Notion access
available here (the SQL / view-query APIs are gated behind a paid Notion plan, and search returns
at most 25 ranked rows per call). So each table below is one of:

| Status | Meaning |
| --- | --- |
| **Full** | Every row is present (the data was embedded in a narrative page). |
| **Representative subset** | A correct-schema sample of real rows; the complete table lives in the Notion source. |

| Table | Rows in Notion | Here | File |
| --- | --- | --- | --- |
| Market-Moving Events (Ranked) | 31 | Full (polarity); tier inferred — see note | [events.md](events.md) |
| News Sources (Ranked) | ~27 | Full (25-source ranked stack) | [news-sources.md](news-sources.md) |
| Instruments / Tickers | 55 | Representative subset (12) | [instruments.md](instruments.md) |
| Effect-Size Matrix (event × instrument) | ~55 | Representative seed subset | [effect-size-matrix.md](effect-size-matrix.md) |
| Top 50 Countries by GDP — Coverage | 50 | Representative subset (10) | [countries.md](countries.md) |
| Markets & Trading Platforms | 132 | Representative subset | [platforms.md](platforms.md) |
| Platform → Top 10 Impactful Events | — | Not mirrored (mapping, derivable) | — |
| Event → Top 10 Impacted Platforms | — | Not mirrored (mapping, derivable) | — |
| Event-Study Calibration Dataset | worked examples | Empty fact table at M0 — see [calibration-dataset.md](../calibration-dataset.md) | — |

> **Inferred fields are flagged inline.** Event polarity is authoritative (from the Event Polarity
> spec); event **tier** is inferred here from the documented 8-tier scheme because the per-event
> tier column lives only in the Notion database. Effect-size rows are *seed estimates* by
> definition (that is what the matrix holds until calibration overwrites them). Reconcile against
> the Notion source before relying on any inferred value.

## Full data

The complete tables live in the project's Notion workspace; the subsets here are re-exported from
there when the build scope needs them.
