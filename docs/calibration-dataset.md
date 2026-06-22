# Spec — Event-Study Calibration Dataset (Methodology & DDL)

This is the dataset that turns the **Effect-Size Matrix** from *seed estimates* into *measured
statistics*. Every magnitude, half-life, and hit-rate should ultimately be a `GROUP BY` over this
table. Notion holds worked examples; the real store should be Postgres.

## 1. Data model (normalized, not one wide table)

Three reference tables + two fact tables:

- `event_types` — the taxonomy (mirror of the Events DB).
- `instruments` — the ~55 instruments (mirror of the Instruments DB).
- `event_instances` — one row per real event occurrence; holds surprise + regime context.
- `observations` — one row per (event_instance × instrument × horizon); holds the measured
  reaction. The calibration grain.
- `effect_size_matrix` — the calibration target: priors get overwritten by aggregates of
  observations.

The split matters: surprise/regime belong to the event, returns belong to the reaction.

## 2. Data dictionary

### event_instances

| Field | Type | Description | Source |
| --- | --- | --- | --- |
| event_id | bigserial PK | Unique event occurrence | — |
| event_type | text FK | One of the taxonomy types | Detection pipeline |
| event_ts | timestamptz | Precise release/headline timestamp (UTC); t0 anchor | Wire / official |
| country | text | ISO-2 or region | — |
| detail | text | Human description | — |
| scheduled | bool | Scheduled vs unscheduled | — |
| consensus | numeric | Expected value (scheduled only) | Econ-calendar API |
| actual | numeric | Released value | Official primary |
| surprise | numeric | actual − consensus (signed) | Computed |
| surprise_sd | numeric | surprise / stdev(historical surprises) | Computed |
| surprise_source | text | Which consensus feed | — |
| priced_in_prior | numeric | Pre-event implied prob/level | Polymarket/Kalshi, options |
| vix_t0 | numeric | VIX at t0 (regime feature) | Cboe |
| rate_regime | text | hiking / cutting / on-hold | Derived |
| quality | text | High/Medium/Low | — |

### observations

| Field | Type | Description | Source |
| --- | --- | --- | --- |
| obs_id | bigserial PK | — | — |
| event_id | bigint FK | Parent event | — |
| instrument | text FK | Symbol | — |
| px_t0 | numeric | Mid-price/level immediately before t0 | Market data |
| ret_unit | text | pct for prices, bps for rates/credit | — |
| ret_5m / ret_1h / ret_1d / ret_1w | numeric | Returns/moves over each horizon from t0 | Computed |
| abn_ret_1d | numeric | Abnormal 1d return = actual − market-model expected | Computed |
| car | numeric | Cumulative abnormal return over event window | Computed |
| peak_move | numeric | Max absolute excursion in window | Computed |
| half_life_min | numeric | Minutes to retrace 50% of peak (NULL if none) | Computed |
| realized_dir | text | sign of primary-horizon move | Computed |
| data_source | text | Price-data provenance | — |
| quality | text | High/Medium/Low | — |

## 3. Methodology

**a. Timestamping & windows.** t0 = release/headline timestamp, not bar date. Intraday windows
need tick/1-min data anchored to t0; daily windows use session closes. After-close events start at
the next open and CAR spans the multi-day reaction. Price instruments: log return ln(p_t/p_t0).
Rates/credit: change in yield/spread in bps with ret_unit='bps'.

**b. Standardized surprise (the key feature).**

```
surprise    = actual - consensus
surprise_sd = surprise / rolling_stdev(historical surprises, last 24-36 releases)
```

Makes a CPI surprise and an NFP surprise comparable; it is the regressor for magnitude.
Unscheduled events have no consensus → treat as scenario priors, not calibrated cells.

**c. Abnormal return (market model).** Estimate over t0−250..t0−20 trading days:

```
r_i,t = alpha_i + beta_i * r_mkt,t + eps        (OLS)
AR_i,t = r_i,t - (alpha_i + beta_i * r_mkt,t)    # abnormal return
CAR_i  = sum of AR_i,t over the event window
```

For FX/commodities/crypto use the relevant benchmark or a mean-return model.

**d. Reaction half-life.** Find peak absolute excursion in the window, then time to retrace 50%.
Bucket into the half-life categories. No 50% retrace → longest bucket. Distinguishes transient
spikes from durable repricing.

**e. Regime conditioning.** Add vix_t0 bucket (<15 / 15-25 / >25) and rate_regime as `GROUP BY`
dimensions or regression interactions. Encodes the good-news-is-bad-news flip and crypto's looser
post-ETF Fed sensitivity.

**f. Direction & hit rate.** realized_dir = sign(abn_ret) at the primary horizon. Hit rate = % of
observations in a cell whose realized direction matches the predicted direction. Only meaningful
with enough n.

## 4. Postgres DDL

```sql
CREATE TABLE event_types (
  event_type   text PRIMARY KEY,
  tier         smallint,
  polarity     text CHECK (polarity IN ('Positive','Negative','Both'))
);
CREATE TABLE instruments (
  symbol text PRIMARY KEY, name text, asset_class text, region text
);
CREATE TABLE event_instances (
  event_id bigserial PRIMARY KEY,
  event_type text NOT NULL REFERENCES event_types(event_type),
  event_ts timestamptz NOT NULL,
  country text, detail text,
  scheduled boolean NOT NULL DEFAULT false,
  consensus numeric, actual numeric, surprise numeric, surprise_sd numeric,
  surprise_source text, priced_in_prior numeric, vix_t0 numeric, rate_regime text,
  quality text CHECK (quality IN ('High','Medium','Low'))
);
CREATE INDEX ix_ei_type_ts ON event_instances(event_type, event_ts);
CREATE TABLE observations (
  obs_id bigserial PRIMARY KEY,
  event_id bigint NOT NULL REFERENCES event_instances(event_id),
  instrument text NOT NULL REFERENCES instruments(symbol),
  px_t0 numeric, ret_unit text CHECK (ret_unit IN ('pct','bps')),
  ret_5m numeric, ret_1h numeric, ret_1d numeric, ret_1w numeric,
  abn_ret_1d numeric, car numeric, peak_move numeric, half_life_min numeric,
  realized_dir text CHECK (realized_dir IN ('Up','Down','Flat')),
  data_source text, quality text CHECK (quality IN ('High','Medium','Low')),
  UNIQUE (event_id, instrument)
);
CREATE INDEX ix_obs_instr ON observations(instrument);
CREATE TABLE effect_size_matrix (
  event_type text REFERENCES event_types(event_type),
  instrument text REFERENCES instruments(symbol),
  direction text, mag_per_sd numeric, mag_ci_low numeric, mag_ci_high numeric,
  median_half_life text, hit_rate numeric, n_obs integer, surprise_dep text,
  last_calibrated timestamptz,
  PRIMARY KEY (event_type, instrument)
);
```

## 5. Calibration query (overwrite priors with measured stats)

```sql
WITH calc AS (
  SELECT ei.event_type, o.instrument, count(*) AS n_obs,
    sum(o.abn_ret_1d * ei.surprise_sd)
      / nullif(sum(ei.surprise_sd * ei.surprise_sd),0) AS mag_per_sd,
    avg( CASE WHEN sign(o.abn_ret_1d) =
             CASE esm.direction WHEN 'Up' THEN 1 WHEN 'Down' THEN -1 ELSE 0 END
         THEN 1.0 ELSE 0.0 END ) AS hit_rate,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY o.half_life_min) AS median_hl_min
  FROM observations o
  JOIN event_instances ei USING (event_id)
  LEFT JOIN effect_size_matrix esm
         ON esm.event_type = ei.event_type AND esm.instrument = o.instrument
  WHERE ei.surprise_sd IS NOT NULL
  GROUP BY ei.event_type, o.instrument, esm.direction
  HAVING count(*) >= 8
)
UPDATE effect_size_matrix esm
SET mag_per_sd = calc.mag_per_sd, hit_rate = calc.hit_rate,
    n_obs = calc.n_obs, last_calibrated = now()
FROM calc
WHERE esm.event_type = calc.event_type AND esm.instrument = calc.instrument;
```

For magnitude confidence intervals and regime interactions, regress in Python:

```python
import statsmodels.formula.api as smf
m = smf.ols("abn_ret_1d ~ surprise_sd * C(vix_bucket)", data=df).fit(cov_type="HC3")
# m.params['surprise_sd'] -> magnitude per 1-SD; m.conf_int() -> CI
```

## 6. Where each input comes from

- consensus / surprise → economic-calendar APIs (Trading Economics, Econoday, AlphaFlash) +
  official actual.
- prices / returns → market-data vendor (Polygon, Databento, Tiingo); tick data for intraday.
- vix_t0 / MOVE → Cboe / ICE.
- priced_in_prior → Polymarket/Kalshi (events), options-implied move (earnings/macro).
- event detection & timestamp → the ranked news stack, corroborated.

## 7. Build sequence (MVP first)

1. Start with scheduled macro (CPI, NFP, Fed, PMI, GDP) where consensus is clean and surprise_sd
   is computable.
2. Add earnings & M&A (clean, high-n).
3. Add unscheduled/systemic (war, banking, hacks) as scenario rows flagged n_obs<8, never
   calibrated coefficients.
4. Run the calibration query; replace seed magnitudes/hit-rates; record last_calibrated.
5. Backtest (directional accuracy, Brier, reliability diagram) before warnings go live.

## 8. Pitfalls

- Look-ahead bias — only t0-available info as features for the prediction.
- Overlapping windows — clustered events violate independence; de-overlap or cluster-robust stats.
- Multiple testing — ~1,700 cells; require n≥8-10, report CIs, treat low-n as priors.
- Rare/systemic events can't be calibrated statistically (n~1-3) — keep as scenario estimates.
- Regime non-stationarity — recalibrate on a rolling window, condition on regime.
- Units — keep ret_unit explicit so bps never get averaged with %.
