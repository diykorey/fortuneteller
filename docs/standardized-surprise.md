# Standardized Surprise — the central feature

> **`surprise_sd` is the regressor the whole prediction core rests on.** Direction resolution and
> magnitude both read off it; if you understand one feature in this system, understand this one.
> The formula is owned by [Calibration Dataset § 3.b](calibration-dataset.md); this page explains the
> *why*. Source of truth for the sign is the [replay engine](m0-r-tickets.md) (M0-R-02).

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
prior surprises) or when `stdev == 0`. This rule is the **one source of truth**: the
[replay engine](m0-r-tickets.md) (M0-R-02) derives `surprise_sign` exactly this way, the M1-01
`surprise_sign()` function matches it deliberately, and it is the type of the `Warning.surprise_sign`
field (`Literal["above","below","unknown"]`). The engine and the predictor read one definition, not
two.

## Where it sits

Surprise is **stage 5** of the pipeline — the first enrichment after an event is parsed:

```
release (consensus, actual) → surprise → effect-size lookup → direction resolution → Warning
```

It is implemented by ticket **M1-01** in `src/fortuneteller/predict/surprise.py`, as three pure
functions:

| Function | Returns |
| --- | --- |
| `compute_surprise(consensus, actual)` | `actual - consensus` — the signed raw miss |
| `standardize(surprise, history)` | `surprise / stdev(history)`, or `None` when history is too short or `stdev == 0` |
| `surprise_sign(surprise_sd)` | `"above"` / `"below"` / `"unknown"` |

## Scope & boundaries

- **Deterministic and pure.** No clock, no IO, no randomness — the surprise functions must keep the
  replay harness byte-for-byte reproducible (see [CLAUDE.md](../CLAUDE.md) determinism rule).
- **Surprise ≠ direction.** Producing a concrete up/down for a `conditional` cell (e.g.
  `CPI / inflation surprise` × `SPY / ES`) is M1's resolver (M1-02/03), not this feature. Surprise
  stops at the standardized number and its sign.
- **Live consensus fetch is M1-06.** Networked code (a free econ calendar / FRED) lives only in
  `src/fortuneteller/live/` and feeds the same pure functions.
- **Abnormal-returns / `observations` modeling is M2.** Surprise is the *input* feature; regressing
  returns on it is downstream.

## See also

- [Calibration Dataset § 3.b](calibration-dataset.md) — the owning spec for the formula and the
  `event_instances` data model.
- [M1 Tickets → M1-01](m1-tickets.md) — the buildable spec (files, functions, acceptance criteria).
- [M0-R Tickets → M0-R-02](m0-r-tickets.md) — the replay engine that established the `surprise_sign`
  convention.
