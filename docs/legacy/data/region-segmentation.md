# Region segmentation — rationale

Why the `Region` enum (`us | europe | asia | em | global`) is shaped the way it is, what it can and
can't express, and when to revisit it. The **normative rule** lives in
[instruments.md → Region semantics](instruments.md#region-semantics); this page is the reasoning
behind it.

> **Status:** design note for the M0 data model (the `Region` str-enum in
> [M0-03](../m0-tickets.md)). The MVP decision is **keep the five buckets, define their meaning,
> don't expand** — following the provable-core scope discipline in
> [mvp-architecture.md](../mvp-architecture.md).

## What `region` is for (and the stakes)

`region` is a field on [instruments](instruments.md) and [countries](countries.md). Before judging
the buckets, note what actually consumes it:

- **Not calibration.** The calibration design conditions on **VIX bucket** and **asset class** —
  "Fit per regime bucket (VIX low/med/high)" and "Mondrian/regime-conditional conformal (separate
  quantiles per VIX bucket / asset class)"
  ([Detection & Calibration](../detection-and-calibration.md)). Region is not a conditioning axis.
- **Not a join key.** The [effect-size matrix](effect-size-matrix.md) keys on
  `(event_type, instrument)`; `event_instances` carries a free-text `country` and a separate
  `rate_regime`, not `region`.

So `region` is **descriptive metadata / grouping**, not a statistical or relational primitive. Its
granularity is therefore low-stakes at the MVP stage — which is why we define its meaning rather
than re-engineer the buckets.

## Why the raw five-bucket set is not a clean taxonomy

The buckets mix **three incompatible axes**:

- developed-market **geography**: `us`, `europe`, `asia`
- development **status**: `em` (cross-geography)
- **scope**: `global` (cross-region)

Run the seed [countries](countries.md) (top 10 by GDP) through it and the collisions surface:

| Country | Problem without a rule |
| --- | --- |
| US, Germany, France, Italy | none — clean `us` / `europe` |
| China, India | ambiguous — Asian *and* emerging: `asia` or `em`? |
| Japan | developed, but `asia` would lump it with EM-Asia |
| United Kingdom | own FX/rates regime (GBP / gilts / BoE), folded into `europe` |
| Canada | no native bucket — not us / europe / asia / em |
| Brazil | only fits `em`; no LatAm bucket |

There is also a **semantic inconsistency** in how the seed populates the field: `BUND → europe` and
`VIX → us` are by listing geography, while `DXY → global` is by macro driver. Same field, different
rules — exactly what produces silent mislabeling as the universe grows.

## The decision

Rather than expand the enum — which would churn the **canonical instrument keys** (see the repo
`CLAUDE.md`) and force a seed-CSV migration for buckets no MVP-core instrument uses — we fix the
*meaning*:

1. **One definition:** `region` = the **dominant macro-driver regime** (which macro bloc's surprises
   move the instrument most), not listing venue or domicile. This is the dimension a market-impact
   predictor actually cares about.
2. **A precedence rule** that gives every instrument exactly one home (global-first, then
   development-status-wins). Full statement + worked mapping:
   [instruments.md → Region semantics](instruments.md#region-semantics).

Applying the rule to the current 12-instrument seed **reproduces every existing label**
(VIX → `us`, Bund → `europe`, Gold / Brent / BTC / USDC / DXY / BDI → `global`, CDS → `em`,
equities → `us`), so **no data migration is needed** — the rule simply makes future labeling
deterministic. The two edge cases it explicitly settles are VIX and DXY, classified by dominant
driver rather than by the "fear-gauge / currency-basket" framing.

## Limits and when to revisit

The rule resolves ambiguity but does not add resolution. It is **deliberately coarse for the MVP**,
where the provable core (US-macro events × {SPY/ES, rates, DXY, Gold, VIX}) touches only
`us` / `europe` / `global` and exercises zero `em` / `asia` instruments.

Revisit only when EM/Asia instruments actually enter (post-proof). At that point the better shape is
likely **two orthogonal fields** — geography (`north_america | europe | uk | japan | asia_pacific |
latam | emea`) plus a separate `dm | em` flag — which removes the geography-vs-development overlap at
the root instead of arbitrating it. A flat enum could instead grow the buckets the data needs (a
North-America / Canada home, a UK split). Either is a post-proof change governed by the
[roadmap](../roadmap.md) graduation triggers, not an MVP task.

## See also

- [Instruments / Tickers](instruments.md) — the `Region` semantics rule (normative) and the seed universe
- [Top Countries by GDP](countries.md) — the other region-classified entity
- [M0 Tickets — M0-03](../m0-tickets.md) — where the `Region` enum is defined
- [Detection & Calibration](../detection-and-calibration.md) — the calibration conditioning axes (VIX bucket, asset class)
- [MVP Architecture](../mvp-architecture.md) — provable-core scope discipline
