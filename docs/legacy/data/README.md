# Reference data

The FortuneTeller knowledge base is a set of Notion databases that the pipeline reads as config.
This directory mirrors them as markdown; the machine-readable seed lives in
[`/data/seed`](../../../data/seed).

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
| National elections (not from Notion) | — | Full for five electorates: 87 vote days, US from 1970, UK from 1970, Germany from 1972, France from 1974, the European Parliament from 1979, each checked against its official record ([elections](../../steps/elections.md)) | `data/seed/elections.csv` |
| Tariff actions (not from Notion) | — | Full by its rule: 103 presidential documents on 73 signing days, 2018-01-23 to 2026-10-23, each imposing, changing or ending an additional US import duty, with its Federal Register document number ([tariff actions](../../steps/tariffs.md)) | `data/seed/tariffs.csv` |
| Debt-limit laws (not from Notion) | — | Full by its rule: 75 public laws on 73 days that raised, extended or suspended the US debt limit, 1970 to 2025, each dated by the day of Congress's final vote, with its roll-call time since 2005, its signing day and whether it was a rider ([the debt limit](../../steps/debt-limit.md)) | `data/seed/debt_limit.csv` |
| G7 and G20 summits (not from Notion) | — | Full by its rule: 70 annual in-person leaders' summits, 51 G7 from 1975 and 19 G20 from 2008, each dated by its last day with the rule's hour and its University of Toronto page ([summits](../../steps/summits.md)); its event type `Leaders' summit` and country `G7 / G20` are seed rows added with it, not from Notion | `data/seed/summits.csv` |
| OPEC announcements (not from Notion) | — | Full by its source: Känzig's 169 OPEC announcements, 1983-07-19 to 2025-12-01, vintage 2025M12, each with the sign of its oil supply surprise as its kind and the rule's 08:00 ([OPEC+ decisions](../../steps/opec.md)); its country `OPEC` is a seed row added with it, not from Notion | `data/seed/opec.csv` |
| Violent acts (not from Notion) | — | Full by its source: the International Crisis Behavior project's (version 16) 137 crises since 1970 whose earliest actor's trigger is a violent act, 1970-11-22 to 2021-04-28, on 136 days, each at the rule's 04:00 UTC with ICB's crisis name; written by `scripts/icb_violent_acts.py` ([war](../../steps/war.md)); its country `World` is a seed row added with it, not from Notion | `data/seed/war.csv` |
| Hurricane landfalls (not from Notion) | — | Full by its source: each Atlantic storm's first US landfall as a hurricane since 1970 in the National Hurricane Center's HURDAT2 (`hurdat2-1851-2025-092326.txt`, read 2026-11-18), 79 from 1970-08-03 to 2024-10-10, each at the record's UTC minute with its name, wind in knots and place; written by `scripts/hurdat_landfalls.py` ([weather](../../steps/weather.md)) | `data/seed/hurricanes.csv` |
| Crypto hacks (not from Notion) | — | Full by its source: DefiLlama's 44 hacks of $100 million or more (`api.llama.fi/hacks`, read 2026-11-18), 2014-02-07 to 2026-10-29, each at the rule's 04:00 UTC with its target and the dollars taken; written by `scripts/defillama_hacks.py` ([crypto](../../steps/crypto.md)) | `data/seed/crypto.csv` |
| Bank Rate changes (not from Notion) | — | Full by its source: the Bank of England's 34 changes of Bank Rate from 2008-02-07 to 2026-11-05, copied by hand from its *Official Bank Rate history* on 2026-11-17; `time` the London hour of the announcement, 12:00 but the emergency cut of 2020-03-11 at 07:00 ([other central banks](../../steps/other-central-banks.md)) | `data/seed/boe-changes.csv` |
| Target overnight rate changes (not from Notion) | — | Full by its source: the Bank of Canada's 42 changes of its target for the overnight rate from 2008-01-22 to 2026-10-28, each on its announcement day, built on 2026-11-22 from the Bank's daily series (Valet `V39079`, from 2009-04-21, whose dates are the effective day from 2022 and for 2020-03-13) and TradingView's calendar before it, with the unscheduled cut of 2008-10-08 the calendar lacks; `time` the Toronto hour of the announcement, the calendar's (09:00 to 2012, 10:00 to 2023, 09:45 from 2024; 2020-03-13 11:00 and 2020-03-27 09:00), 07:00 for 2008-10-08 ([Canada](../../steps/canada.md)) | `data/seed/boc-changes.csv` |
| The president's trade tweets (not from Notion) | — | Full by its rule: 179 New York days in the first term (2017-01-20 to 2021-01-08) with a tweet matching `tariff`, `trade war` or `trade deal`, built by `scripts/presidential_posts.py` from a pinned Trump Twitter Archive dump, days, times and counts only ([the president's trade posts](../../steps/presidential-posts.md)); its event type `Presidential post` is a seed row added with it, not from Notion | `data/seed/presidential_posts.csv` |
| The president's second-term trade posts (not from Notion) | — | Full by its rule: 220 New York days (2025-01-20 to 2026-10-30) with a Truth Social post matching part 1's topic rule, built by `scripts/presidential_posts.py` from an md5-pinned snapshot of CNN's archive, days, times and counts only ([part 2](../../steps/presidential-posts-2.md)); its event type `Presidential post (second term)` is a seed row added with it, not from Notion | `data/seed/presidential_posts_2.csv` |
| Platform → Top 10 Impactful Events | — | Not mirrored (mapping, derivable) | — |
| Event → Top 10 Impacted Platforms | — | Not mirrored (mapping, derivable) | — |
| Event-Study Calibration Dataset | worked examples | Empty fact table at M0 — see [calibration-dataset.md](../calibration-dataset.md) | — |

> **Inferred fields are flagged inline.** Event polarity is authoritative (from the Event Polarity
> spec); event **tier** is inferred here from the documented 8-tier scheme because the per-event
> tier column lives only in the Notion database. Effect-size rows are *seed estimates* by
> definition (that is what the matrix holds until calibration overwrites them). Reconcile against
> the Notion source before relying on any inferred value.

## Design notes

- [Region segmentation — rationale](region-segmentation.md) — what the `Region` enum means
  (dominant macro-driver regime), the precedence rule that resolves the `asia` / `em` overlap, and
  when to revisit the buckets post-proof.

## Full data

The complete tables live in the project's Notion workspace; the subsets here are re-exported from
there when the build scope needs them.
