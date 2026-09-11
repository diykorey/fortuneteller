# Effect-Size Matrix (event × instrument)

The prediction layer's lookup table: for each (event_type × instrument) cell, the typical
direction, magnitude, reaction half-life, and a direction confidence. At M0 these are **seed
estimates**; the [Event-Study Calibration Dataset](../calibration-dataset.md) overwrites them with
measured statistics (`mag_per_sd`, `hit_rate`, `n_obs`) once enough observations accrue.

> **⚠️ Completeness — placeholder seeds, NOT the Notion rows.** The actual seed values authored in
> the Notion "Effect-Size Matrix" database (~55 rows) could not be exported with the available
> read-only access. The rows below are **illustrative placeholders** — directionally consistent
> with the [Event Polarity spec](../event-polarity-and-classifier-prompts.md) and good enough to
> make `query-demo` return a sensible row — but the **numbers are not authoritative**. Replace them
> with the real matrix from the Notion source before using any value. Columns match the
> `effect_size_seed` CSV.

| Event type | Instrument | Direction | Typical magnitude | Half-life | Dir. confidence | Hit-rate est. | Surprise-dependent | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPI / inflation surprise | SPY / ES | conditional | 0.5–1.5% | minutes_hours | high | ~62% | yes | placeholder seed |
| CPI / inflation surprise | German Bund 10Y | conditional | 3–10 bps | minutes_hours | high | ~60% | yes | placeholder seed |
| CPI / inflation surprise | Gold | conditional | 0.4–1.2% | minutes_hours | medium | ~55% | yes | placeholder seed |
| Central-bank decision | SPY / ES | conditional | 0.5–2% | minutes_hours | high | ~58% | yes | placeholder seed |
| Central-bank decision | US Dollar Index | conditional | 0.3–1% | minutes_hours | high | ~60% | yes | placeholder seed |
| Major interstate war | Brent crude oil | up | 3–10% | hours_days | high | ~70% | no | placeholder seed |
| Major interstate war | SPY / ES | down | 1–5% | hours_days | medium | ~65% | no | placeholder seed |
| Major interstate war | Gold | up | 1–4% | hours_days | high | ~68% | no | placeholder seed |
| OPEC+ supply decision | Brent crude oil | conditional | 2–6% | minutes_hours | high | ~64% | yes | placeholder seed |
| Geopolitical escalation / terror | VIX | up | 5–20% | seconds_minutes | high | ~72% | no | placeholder seed |
| Cyber attack / hack | USDC | down | 0.2–5% | seconds_minutes | medium | ~55% | no | placeholder seed |
| Stablecoin / DeFi depeg | Bitcoin | down | 2–10% | seconds_minutes | medium | ~60% | no | placeholder seed |
| Earnings release | Nvidia | conditional | 3–12% | minutes_hours | high | ~58% | yes | placeholder seed |
| M&A announcement | Apple | conditional | 1–8% | hours_days | medium | ~55% | no | placeholder seed |
| Banking / financial crisis | Sovereign CDS (EM / periphery) | up | 20–100 bps | hours_days | high | ~70% | no | placeholder seed |

**Direction enum** (M0-03): `up`, `down`, `mixed`, `conditional`. Surprise-dependent cells use
`conditional` — the sign resolves at prediction time from the standardized surprise and regime.
**Half-life enum** — the prediction's *horizon*: how long the move persists before fading, defined
operationally as the **time to retrace 50% of the peak post-event move**. The name is the
radioactive-decay analogy — the characteristic time for the impact to fall to half. It is measured
per observation as `half_life_min` (minutes) and bucketed into one of five order-of-magnitude bands:

- `seconds_minutes` — transient snap, reverts almost immediately
- `minutes_hours` — intraday repricing (the common macro-surprise case in the table above)
- `hours_days` — settles over a session or two
- `days_weeks` — a repricing that sticks
- `weeks_plus` — structural / persistent (also the fallback when the move never retraces 50% within
  the measurement window)

This is the field that separates a fleeting blip from a durable move — central to a *warning*
product, since it sets how long a warning stays actionable. Precise measurement methodology:
[Calibration Dataset → Reaction half-life](../calibration-dataset.md). At M0 these are seed bands;
calibration overwrites each cell with the median measured `half_life_min`.
