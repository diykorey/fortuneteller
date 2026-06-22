# Spec — Detection & Confidence Calibration (detailed)

The two stages where event→market systems live or die. Part A turns a noisy multi-source
firehose into a trustworthy, deduplicated, timestamped event stream with an "is this real?"
confidence. Part B turns raw model scores into probabilities and magnitude bands that mean what
they say. Tech: Java/Flink streaming (A), Python statistical models (B).

# PART A — Detection & Corroboration

**Output contract:** one event instance per real-world event — deduplicated across all sources —
with `{t0, event_type, polarity, entities[], detection_confidence, provenance[]}`, emitted when
confidence crosses a threshold and updated as evidence arrives.

## A1. Common event envelope

```
RawItem {
  source_id, source_tier, reliability r       // from News Sources (Ranked)
  publisher_ts        // when the source published
  ingest_ts           // when we received it
  text, url, lang
  originator_id       // syndication root (e.g., "AP") if derivable
  raw_entities[]
}
```

reliability r and source_tier come straight from the News Sources (Ranked) table; they are the
weights everything else uses.

## A2. Timestamping (t0) — get this right or everything downstream is wrong

- Scheduled events (CPI, NFP, Fed): t0 = the official release time from the calendar, not when
  you saw the headline. Pre-register these.
- Unscheduled events: t0 = earliest credible publisher_ts across the cluster, sanity-checked
  against ingest_ts for clock skew. Reject impossible-latency timestamps.
- Store both event-occurrence time and first-reported time; they differ for things discovered
  late (a hack disclosed hours later). Reaction window anchors on first-reported; occurrence time
  matters for forensics.
- All UTC, millisecond precision.

## A3. Deduplication & clustering (the unit of an "event")

Different-worded reports of the same event must collapse into one cluster, or you double-count
corroboration and fire duplicate warnings. Two streaming layers:

1. Near-exact dedup — SimHash/MinHash on normalized text within a short window kills verbatim
   syndication.
2. Semantic clustering — embed the headline, then online single-pass clustering: assign to
   nearest open cluster if cosine ≥ tau_sim AND within window dt, else open a new cluster.
   Window is event-class-dependent.

```
on RawItem x:
   x.emb = embed(x.text)
   c = nearestOpenCluster(x.emb, within=dt)
   if c and cosine(x.emb, c.centroid) >= tau_sim:
        c.add(x); c.updateConfidence()
   else:
        openCluster(x)
```

State in a keyed store (Kafka Streams/RocksDB or Redis). Idempotency: dedup on
(source_id, url, hash).

## A4. Source independence (the subtle, critical part)

Confidence must count independent originators, not echoes. Fifty outlets reprinting one AP wire =
one independent observation. Before scoring: group items by originator_id / syndication root /
near-duplicate text; within a group take the single strongest source's reliability; only across
groups does evidence accumulate. Skipping this is the most common way these systems become
falsely confident.

## A5. Corroboration confidence — evidence accumulation in log-odds

Model "is this event real?" as naive-Bayes evidence accumulation. Each independent source is a
noisy detector with likelihood ratio LR = sensitivity / (1 − specificity):

```
l  = l0                                   # prior log-odds the event class is real
for each independence-group g:
    if g confirms:   l += ln(LR_g)
    if g denies:     l -= ln(LR_g)        # retractions/denials subtract
confidence = sigmoid(l)                    # P(event is real)
```

Confirm-only special case is noisy-OR: confidence = 1 − product(1 − r_g).

**Worked example** (noisy-OR, independent groups):

- Single X post, r=0.30 → conf 0.30 → unconfirmed / watch.
  - Benzinga, r=0.70 → 1 − (0.7×0.3) = 0.79.
  - Reuters, r=0.92 → 1 − (0.7×0.3×0.08) = 0.983 → fire.
- A gov primary / SEC filing alone, r~0.99 → 0.99 instantly.

## A6. Three separate confidences — don't conflate them

- P(real) — from A5 (did it happen?).
- P(classification correct) — from the LLM classifier.
- P(entity-link correct) — did we attach the right instruments?

detection_confidence = P(real) × P(class) × P(link). Keep separate for debugging; the product
feeds Part B as a prior multiplier.

## A7. Contradiction & retraction handling

- A credible denial subtracts log-odds; a high-reliability denial can push a cluster below
  threshold → issue a correction, not silence.
- Cluster state: WATCH → CONFIRMED → (RETRACTED | DECAYED).
- Time decay: a WATCH cluster with no corroboration in its window decays toward the prior (stale
  rumor dies).

## A8. State machine & thresholds

```
WATCH      : tau_watch <= conf < tau_emit   -> internal only, no reader alert
CONFIRMED  : conf >= tau_emit                -> emit event instance -> prediction
RETRACTED  : credible denial drops conf      -> emit correction
DECAYED    : no corroboration in window       -> drop silently
```

Tune tau per tier: systemic Tier-1 warrants a lower tau_emit (warn early) than a niche Tier-8
event.

## A9. Latency & reliability

Per-substage budget (seconds-low minutes end-to-end): embed+cluster < 200ms, classify (cached)
< 1s, corroboration continuous. Backpressure + dead-letter topic; Kafka replay for backtests.
Every emitted instance carries full provenance for audit/compliance.

## A10. Failure modes to design against

- Echo-chamber false confidence → independence grouping (A4).
- Single-source rumor fires → tau_watch gate + decay.
- Clock skew / fake-early timestamps → t0 sanity checks (A2).
- Cluster splitting (one event seen as two) → semantic threshold tuning + merge pass.
- Cluster merging (two events seen as one) → entity check; if entities diverge, split.

# PART B — Confidence Calibration

**Output contract:** `{direction, P(direction_correct) [calibrated], magnitude_median,
magnitude_band[low,high] @ coverage, horizon, regime, benchmark_skill, calibration_flag}`.

## B1. What gets calibrated (two distinct things)

1. Directional probability — P(the predicted sign is right).
2. Magnitude distribution — a band with a stated coverage, not a point. A model can be
   directionally sharp but magnitude-miscalibrated, or vice versa.

## B2. Directional probability calibration

Map raw score → true probability on a held-out set:

- Platt scaling (logistic): robust at low n.
- Isotonic regression: flexible, needs more data (>~1k).
- Venn-Abers: distribution-free, small-sample validity — good default when per-cell data is scarce.

```python
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
iso = IsotonicRegression(out_of_bounds="clip").fit(p_raw, y)   # large n
platt = LogisticRegression().fit(p_raw.reshape(-1,1), y)        # small n
p_cal = iso.predict(p_raw_new)
```

Fit per regime bucket (VIX low/med/high) — the same raw score means different things across
regimes.

## B3. Measuring calibration (the scoreboard)

- Reliability diagram — predicted vs observed frequency; diagonal is perfect.
- ECE = sum_b (n_b/N)×|acc_b − conf_b|.
- Brier score = mean((p − y)^2); decomposes into reliability − resolution + uncertainty.
- Log loss — punishes confident wrong calls harder.

Track over a rolling window; rising ECE triggers recalibration.

**Worked example:** raw scores in the 0.9 bucket only verify 0.72 of the time → isotonic remaps
0.9→0.72, so "90%" warnings stop overpromising. ECE drops; readers can trust the number.

## B4. Magnitude uncertainty — use conformal prediction

Returns are heteroskedastic and regime-shifting, so a fixed band is wrong. Split conformal gives
finite-sample coverage with no distributional assumption:

```
nonconformity s_i = |actual_return_i - predicted_i| / sigma_hat_i
q = ceil((n+1)(1-alpha))/n quantile of {s_i} on the calibration set
band = predicted +/- q * sigma_hat_new                       # coverage >= 1-alpha
```

Use Mondrian/regime-conditional conformal (separate quantiles per VIX bucket / asset class) so
coverage holds within each regime. Alternative: quantile regression for an asymmetric band.

## B5. Low-n cells — partial pooling, don't fake it

~31 events × ~55 instruments ~ 1,700 cells with uneven n. For sparse cells, shrink toward the
parent (event-type or asset-class average):

```
theta_hat_cell = (n/(n+k))*cell_mean + (k/(n+k))*parent_mean   # James-Stein / hierarchical
```

A cell with n<8 is flagged "uncalibrated — scenario prior" and never advertised with a precise
hit rate. Rare systemic events (pandemic, war, depeg) stay scenario priors with wide bands,
permanently.

## B6. Beat the benchmark or say so

For every prediction compute the market's own forecast and compare out-of-sample:

- Options-implied move — ATM straddle / IV → expected move over the horizon.
- Prediction-market odds — Polymarket/Kalshi, with a favorite-longshot bias correction (shrink
  extreme odds toward 0.5).
- Skill score vs benchmark (e.g., Brier skill score). No edge for a cell → the warning says
  "no edge vs market-implied".

## B7. Drift & recalibration

Monitor ECE, Brier, and coverage on a rolling window per cell/regime. Auto-trigger recalibration
when ECE > threshold or conformal coverage drifts outside [1−alpha ± tolerance]. Version
calibration models; the batch job refits and the prediction service hot-swaps.

## B8. Final warning probability (integration with Part A)

```
P(warning correct & real)
   ~ detection_confidence            # Part A: P(real)*P(class)*P(link)
   * P(direction_correct | calibrated)   # Part B2
combined with magnitude_band          # Part B4
```

Reader-facing warning surfaces: direction, this combined probability, the magnitude band with its
coverage, horizon, regime, benchmark comparison, calibration flag. Alerting severity =
expected_magnitude × combined_probability.

## B9. Backtest gate (no warning ships uncalibrated)

A cell may emit reader warnings only once it passes, out-of-sample: (1) ECE below threshold,
(2) conformal coverage within tolerance, (3) positive skill vs the market-implied benchmark,
(4) n above the minimum. Everything else stays internal/scenario.

## Where this connects

- Part A consumes the News Sources (Ranked) reliabilities and emits event instances matching the
  Calibration Dataset schema.
- Part B consumes the Effect-Size Matrix (priors), the Calibration Dataset (to fit calibrators),
  and the prediction-market instruments (benchmark); it writes the calibrated probability/band the
  alerting stage thresholds on.
- The two confidences multiply into the single number a reader sees — and the backtest gate (B9)
  is the contract that keeps it honest.
