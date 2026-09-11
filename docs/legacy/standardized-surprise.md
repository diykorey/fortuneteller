# Standardized Surprise — the central feature

> **`surprise_sd` is the regressor the whole prediction core rests on.** Direction resolution and
> magnitude both read off it; if you understand one feature in this system, understand this one.
> The formula is owned by [Calibration Dataset § 3.b](calibration-dataset.md); this page explains the
> *why*. **Nothing here is implemented yet** — it is the concept the prediction layer will be built
> around, not a description of code in the repo.

## Why "surprise"?

By the time a scheduled release like CPI or NFP prints, its *expected* value is already in the price.
Economists publish a **consensus** forecast ahead of the release and traders position for it — so a
result that lands exactly on consensus carries almost no new information, and prices barely move.

What actually moves an instrument is the gap between what was **expected** and what was **delivered**:

```
surprise = actual - consensus
```

That delta *is* the new information — the part the market did not already know, the part it is
"surprised" by. A zero-surprise release is maximally boring; the bigger the miss in either direction,
the bigger the reaction. This is why the prediction core acts on the surprise, not on the headline
number.

## Computing it

Two steps, taken verbatim from [Calibration Dataset § 3.b](calibration-dataset.md) so this page can
never drift from the calibration spec:

```
surprise    = actual - consensus
surprise_sd = surprise / rolling_stdev(historical surprises, last 24-36 releases)
```

1. **`surprise`** — the signed raw miss (`actual - consensus`).
2. **`surprise_sd`** — the raw miss divided by the rolling standard deviation of the last **24–36**
   historical surprises for that series.

**Why standardize?** A raw surprise is not comparable across event types — a 0.2-point CPI miss and a
50k-job NFP miss live on totally different scales. Dividing by the typical size of recent surprises
re-expresses everything as *"standard deviations of a normal surprise."* A `surprise_sd` of +2 means
"about twice as far above expectations as a typical release," and that statement means the same thing
for CPI, NFP, or GDP. That common scale is exactly why § 3.b calls it **the key feature**: it is the
regressor for magnitude. Unscheduled events have no consensus, so they have no `surprise_sd` — they
are treated as scenario priors, not calibrated cells.

## The sign

The direction of the surprise is collapsed into one label:

```
surprise_sign = "above"   if surprise_sd > 0
                "below"   if surprise_sd < 0
                "unknown" otherwise        # short history or stdev == 0 → surprise_sd is None
```

`"unknown"` is the honest answer when there isn't enough history to standardize (fewer than ~24
prior surprises) or when `stdev == 0`. Whatever computes the sign, this rule is the **one source of
truth** — one definition, read by everything downstream, never two.

## Where it sits

Surprise is **stage 5** of the pipeline — the first enrichment after an event is parsed:

```
release (consensus, actual) → surprise → effect-size lookup → direction resolution → Warning
```

It is three small computations: the signed miss (`actual − consensus`), its standardization by the
stdev of recent surprises, and the sign that falls out. None of it exists in the repo yet.

## Scope & boundaries

- **Deterministic and pure.** No clock, no IO, no randomness — surprise is arithmetic over numbers
  that were handed to it.
- **Surprise ≠ direction.** Producing a concrete up/down for a `conditional` cell (e.g.
  `CPI / inflation surprise` × `SPY / ES`) is a separate step. Surprise stops at the standardized
  number and its sign.
- **Fetching a live consensus is separate too.** Networked code stays out of these functions and
  feeds them instead.
- **Abnormal-returns / `observations` modeling is M2.** Surprise is the *input* feature; regressing
  returns on it is downstream.

## See also

- [Calibration Dataset § 3.b](calibration-dataset.md) — the owning spec for the formula and the
  `event_instances` data model.
- [Roadmap](roadmap.md) — where the prediction layer that consumes this feature sits.
