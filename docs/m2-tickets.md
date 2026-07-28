# M2 Tickets — Historical dataset + event-study calibration

> Written to be consumed by an LLM coding agent, same as [M0 Tickets](m0-tickets.md),
> [M0-R Tickets](m0-r-tickets.md) and [M1 Tickets](m1-tickets.md). Read the Shared Context once, then
> any ticket can be implemented in isolation. Every ticket states exact file paths, an explicit spec,
> and binary acceptance criteria.
>
> Milestone source: [Roadmap → M2](roadmap.md). Design sources:
> [Event-Study Calibration Dataset](calibration-dataset.md) (the methodology — tickets **cite** it,
> they do not restate it), [MVP architecture](mvp-architecture.md),
> [Standardized Surprise](standardized-surprise.md).

## Shared Context (read once, applies to every M2 ticket)

**Why.** Every magnitude, half-life, hit-rate and confidence the system emits today is an
**illustrative placeholder** — `data/seed/effect_size_seed.csv` says so in its own `basis` column.
M2 replaces those guesses with **measured** numbers for the scheduled-macro core, from free data.
This is the milestone that makes the product's one claim — *calibrated* confidence — true rather
than aspirational, and the roadmap makes it the critical path: *"Strictly sequential: M0 → M1 → M2 →
M3"*, and *"Never widen (M4/M5) or productize (M6) ahead of honesty (M3)"*.

**M2 fills empty tables; it does not design a schema.** `schema.sql` already declares all three
target tables — `event_instances`, `observations`, `effect_size_matrix` — and `db.py`'s `_TABLES`
registry and `tests/test_schema.py` already assert them. M0 created them deliberately empty
(`seed.py`: *"Out of scope: the fact tables … which stay empty in M0"*). Read the existing DDL before
writing any INSERT.

**Prerequisites (must land first).**
- **M0-01…09** — scaffold + data spine (`uv`, models, DuckDB, seed loader, CLI). **Done / merged.**
- **M1-01** — `src/fortuneteller/predict/surprise.py` (`compute_surprise` / `standardize` /
  `surprise_sign`). **Done / merged.** M2 **reuses** it; it must never re-derive `surprise_sd`, or the
  offline and calibration paths drift apart.
- **M1-06** — `src/fortuneteller/live/` (FRED + free econ-calendar connectors), issue
  [#29](https://github.com/diykorey/fortuneteller/issues/29). **Not built.** *Strongly recommended
  first*: M2-02 extends exactly those connectors. **If `live/` does not exist when M2-02 starts**,
  M2-02 creates `live/sources.py` itself with the minimal FRED client it needs — under `live/`, never
  under `calibrate/` — so M1-06 later extends one connector rather than deleting a duplicate.

**Scope discipline (the provable core).** M2 calibrates exactly **3 event types × 5 instruments =
15 cells**, using the canonical keys verbatim from
[`data/seed/event_types.csv`](../data/seed/event_types.csv) and
[`data/seed/instruments.csv`](../data/seed/instruments.csv):

| Event types (3) | Instruments (5) |
| --- | --- |
| `CPI / inflation surprise` | `SPY / ES` |
| `NFP / labor data` | `BUND / FGBL` (the rates benchmark) |
| `Central-bank decision` (this is the canonical key for "Fed" — there is no `Fed` row) | `DXY` |
| | `GC / XAU` |
| | `VIX` |

The full 31-event taxonomy, the other ~50 instruments, unscheduled detection, and paid/tick data are
**post-proof**. Do not implement against their breadth.

**Known seed gap (do not discover this at M2-06).** `effect_size_seed.csv` covers only **7** of the
15 core cells — `CPI / inflation surprise` × all five, and `Central-bank decision` × `SPY / ES` /
`DXY`. There are **zero** `NFP / labor data` rows. `surprise_response.csv` is thinner still: the CPI
slice only. The missing cells are not an error to fix by inventing priors — they enter
`effect_size_matrix` at **M2-06** as prior-less rows (`n_obs = 0`, NULL magnitudes) and become real
only when n≥8 observations measure them. M2-06 owns extending `surprise_response.csv` to the NFP and
`Central-bank decision` cells, because its hit-rate join needs a concrete predicted direction.

**Free-stack decision (binding).** Consensus/actuals from **FRED** + a free econ calendar (Trading
Economics free tier / Investing.com); daily and 1-minute bars from **yfinance / Stooq / Tiingo free
tier** ([mvp-architecture → data acquisition](mvp-architecture.md), *"a binding decision so M2 does
not stall on a 'which vendor?' debate"*). **A ticket may not introduce a paid vendor.** Tick data and
Polygon / Databento stay deferred until post-proof.

**A free-data ceiling to design around, not to work around.** yfinance serves
1-minute bars for roughly the **last 30 days only**, and Stooq has no free intraday history. A
multi-year backfill therefore **cannot** produce `ret_5m` / `ret_1h` / a minute-resolution
`half_life_min` for historical releases. Those columns stay **NULL** for old events; `ret_1d` /
`ret_1w` from daily closes are the calibration grain for the backfill. The intraday columns fill
*forward* over time via M2-08's scheduled capture, which sees each new release inside the 30-day
window. Writing a fabricated intraday number is a look-ahead-bias defect
([calibration-dataset § 8](calibration-dataset.md)), not a convenience.

**The determinism firewall (the rule the whole dev loop rests on).** The replay harness guarantees
*same inputs → identical bytes*, and it holds that guarantee by reading **committed** seed CSVs. If
`replay()` ever read a locally-calibrated `effect_size_matrix`, the goldens would depend on whoever
last ran a backfill. Therefore:

- Networked and calibration code lives **only** in `src/fortuneteller/live/` and
  `src/fortuneteller/calibrate/`.
- **`src/fortuneteller/replay/` imports neither.** M2-02 adds the test that enforces this.
- `replay()` keeps reading `data/seed/*.csv`. Calibration writes to `effect_size_matrix` **in
  DuckDB** only.
- The **only** path from a measured number into the prediction core is **M2-07**: an explicit,
  reviewed, committed edit to `data/seed/effect_size_seed.csv` with regenerated goldens in the same
  diff. Never an implicit read.

**Conventions.** Enum values are **lowercase** throughout, as settled by M2-01. `mypy --strict` over
`src`; ruff line length 100; tests use the `# given` / `# when` / `# then` structure; loaders and
writers are idempotent (`INSERT OR REPLACE`). `just check` (= `ruff check` + `mypy src` + `pytest`)
must be green.

**Definition of done for M2** (from [Roadmap → M2](roadmap.md)):
1. `effect_size_matrix` carries measured `mag_per_sd`, `hit_rate`, `n_obs` and `last_calibrated` for
   the scheduled-macro core cells that reached **n ≥ 8**; cells below the gate remain visible priors
   with `n_obs < 8` and NULL measured columns.
2. `uv run fortuneteller calibrate` reproduces those numbers from the stored observations.
3. The loop re-runs on a schedule (APScheduler, M2-08) and captures outcomes.
4. `replay` output is still byte-identical run to run, and `just check` is green.

**Dependency order.** M2-01 → M2-02 → M2-03 → M2-04 → M2-05 → M2-06 → M2-07 → M2-08.

---

## M2-01 — Reconcile enum casing and constrain the calibration tables

**Depends on:** M0-03 (models), M0-07 (`schema.sql`)

**Goal:** One settled casing for every enum the calibration tables use, enforced by `CHECK`
constraints and typed Pydantic enums, plus the `UNIQUE (event_id, instrument)` the observations grain
depends on — all **before** any ticket writes a row.

**Context:** `CLAUDE.md` records the debt explicitly: the M0-03 models and seed CSVs use lowercase
values (`positive`, `up`, `conditional`, `equity_index`) while
[calibration-dataset § 4](calibration-dataset.md)'s DDL uses capitalized (`'Positive'`, `'Up'`,
`'High'`) — *"Reconcile to one casing when implementing M2."* Nothing enforces either today:
`grep -n CHECK schema.sql` returns nothing, and `EventInstance` / `Observation` type `quality`,
`ret_unit` and `realized_dir` as bare `str`. This is M2's first ticket because every later ticket
writes those columns, and a casing split discovered at M2-06 means re-running the whole backfill.
Lowercase wins: three shipped milestones, all six existing enums, and every seed CSV already use it;
the capitalized DDL is a document no code reads.

**Files:** `schema.sql`, `src/fortuneteller/models.py`, `docs/calibration-dataset.md`, `CLAUDE.md`,
`tests/test_models.py` (extend), `tests/test_schema.py` (extend)

**Spec:**
- **New enums** in `models.py`, following the existing `StrEnum` style:
  - `Quality`: `high` / `medium` / `low`.
  - `RetUnit`: `pct` / `bps`.
  - `RealizedDir`: `up` / `down` / `flat`. **Do not reuse `Direction`** — it carries `mixed` and
    `conditional`, which a *realized* move cannot be, and it lacks `flat`.
- **Retype the existing models** (they already exist — `EventInstance` at `models.py:131`,
  `Observation` at `models.py:149`): `EventInstance.quality: Quality | None`,
  `Observation.ret_unit: RetUnit | None`, `Observation.realized_dir: RealizedDir | None`,
  `Observation.quality: Quality | None`.
- **New model** `EffectSizeMatrixRow` mirroring the `effect_size_matrix` columns
  (`event_type`, `instrument`, `direction: Direction`, `mag_per_sd`, `mag_ci_low`, `mag_ci_high`,
  `median_half_life: HalfLife | None`, `hit_rate`, `n_obs`, `surprise_dep`, `last_calibrated`),
  `extra="forbid"` via `_DomainModel`.
- **`schema.sql`:** add `CHECK` constraints matching the lowercase sets —
  `event_instances.quality IN ('high','medium','low')`,
  `observations.ret_unit IN ('pct','bps')`,
  `observations.realized_dir IN ('up','down','flat')`,
  `observations.quality IN ('high','medium','low')` — and the
  **`UNIQUE (event_id, instrument)`** on `observations` that
  [calibration-dataset § 4](calibration-dataset.md) specifies but `schema.sql` omits. The tables are
  empty, so this is a pure DDL edit; `CREATE TABLE IF NOT EXISTS` means an existing local
  `data/fortuneteller.duckdb` will **not** pick up the constraints — note in the ticket's commit
  message that developers re-run `fortuneteller init` on a fresh file.
- **`docs/calibration-dataset.md`:** lowercase the § 4 DDL `CHECK` literals and the § 5 query's
  `CASE esm.direction WHEN 'Up' … WHEN 'Down' …` → `'up'` / `'down'`.
- **`CLAUDE.md`:** replace the "Enum casing" gotcha bullet with a one-line statement of the settled
  rule (lowercase everywhere, enforced by `CHECK` constraints since M2-01). Do not leave a
  now-false instruction in place.

**Acceptance criteria:**
- [ ] `uv run fortuneteller init` on a fresh DB file succeeds; inserting `quality='High'` into
      `event_instances` raises a constraint error, `quality='high'` succeeds.
- [ ] a second insert of the same `(event_id, instrument)` into `observations` violates the new
      `UNIQUE` constraint.
- [ ] `tests/test_models.py` asserts the three new enums reject capitalized input and that
      `EffectSizeMatrixRow` round-trips a full row; `tests/test_schema.py` asserts the constraints
      exist.
- [ ] `grep -rn "'Up'\|'High'\|'Positive'" docs/calibration-dataset.md` returns nothing.
- [ ] ruff + mypy strict pass; the existing test suite is unchanged and green.

**Out of scope:** populating any table (M2-02 / M2-03); the `Direction` / `Polarity` / `HalfLife`
enums, which are already lowercase and already used by shipped code.

## M2-02 — Historical scheduled-macro backfill → `event_instances`

**Depends on:** M2-01, M1-01 (`predict.surprise`), M0-05 (seed loader)

**Goal:** A `fortuneteller backfill` command that fills `event_instances` with real CPI / NFP /
`Central-bank decision` releases — each carrying a correct `event_ts`, a `surprise_sd` computed by
the *same* M1-01 code the prediction core uses, and its regime context.

**Context:** Everything downstream is a `GROUP BY` over this table, so its grain and its timestamps
are load-bearing. Two details decide whether the whole milestone measures anything real. First,
`event_ts` is the **release timestamp, not the bar date** ([calibration-dataset § 3.a](calibration-dataset.md))
— a CPI print lands at 08:30 ET and the reaction is anchored there; using the session date silently
smears the event across a day of unrelated flow. Second, `surprise_sd` must come from
`predict/surprise.py` rather than a local re-implementation, because the number the calibration
regresses on and the number the live path predicts from have to be the same number. This ticket also
installs the determinism firewall as an executable test rather than a paragraph.

**Files:** `src/fortuneteller/calibrate/__init__.py`, `src/fortuneteller/calibrate/backfill.py`,
`src/fortuneteller/__main__.py` (extend), `src/fortuneteller/live/sources.py` (create only if M1-06
has not landed), `tests/test_backfill.py` (new, mocked transport),
`tests/test_import_firewall.py` (new), `pyproject.toml` (add `httpx` if not already present)

**Spec:**
- CLI: `fortuneteller backfill --event "<canonical event_type>" --from <YYYY-MM-DD> --to <YYYY-MM-DD>`.
  An `--event` value absent from `event_types.csv` exits non-zero pointing at the seed CSV.
- **Sources (free stack only):** `actual` from FRED (`CPIAUCSL` for CPI, `PAYEMS` for NFP,
  `DFEDTARU` for the Fed target); `consensus` from the free econ calendar. Reuse
  `live/sources.py` if it exists; otherwise create it with the minimal typed `httpx` client this
  ticket needs. `FT_FRED_API_KEY` comes from `pydantic-settings`, never hard-coded; a missing key is a
  legible non-zero exit.
- **`event_ts`** is the official release instant in UTC, not the bar date: 08:30 ET for CPI and NFP,
  14:00 ET for an FOMC statement. Store as UTC; honour US DST when converting.
- **`surprise` / `surprise_sd`** via `predict.surprise.compute_surprise` and `standardize` over the
  trailing **24–36** releases ([calibration-dataset § 3.b](calibration-dataset.md)). A history shorter
  than 24 yields `surprise_sd = NULL` — that row is kept (it is still a real event) but M2-06's query
  filters it out.
- **Regime context:** `rate_regime` ∈ `hiking` / `cutting` / `on_hold`, derived from the trailing
  change in the FRED fed-funds target as of `event_ts` (**as-of only** — no look-ahead);
  `vix_t0` = the VIX close on the prior session.
- **Deterministic ids.** `event_instances.event_id` is a plain `BIGINT PRIMARY KEY` (DuckDB has no
  `bigserial`), so idempotency needs a stable derivation, not a counter:
  `event_id = int.from_bytes(blake2b(f"{event_type}|{event_ts:%Y-%m-%dT%H:%M:%SZ}".encode(), digest_size=8).digest(), "big") >> 1`
  (the shift keeps it inside signed `BIGINT`). Write with `INSERT OR REPLACE` so re-running any date
  range is a no-op.
- **Determinism firewall test** (`tests/test_import_firewall.py`): walk every module under
  `src/fortuneteller/replay/` and assert none imports `fortuneteller.live` or
  `fortuneteller.calibrate` — parse with `ast`, do not import the modules. This is what turns the
  Shared Context rule into something CI enforces.

**Acceptance criteria:**
- [ ] with mocked HTTP, `fortuneteller backfill --event "CPI / inflation surprise" --from … --to …`
      inserts one row per release with the correct UTC `event_ts` (08:30 ET), a `surprise_sd` equal to
      the value `predict.surprise` returns for the same inputs, and a populated `rate_regime`.
- [ ] re-running the identical command changes no rows (`count_rows("event_instances")` is stable and
      the row contents are unchanged) — `INSERT OR REPLACE` on the derived `event_id`.
- [ ] a release with fewer than 24 prior surprises stores `surprise_sd IS NULL` rather than a
      fabricated value.
- [ ] `tests/test_import_firewall.py` passes, and fails if a `from ..live import …` line is added to
      any `replay/` module.
- [ ] `tests/test_backfill.py` runs with **no live network**; a missing `FT_FRED_API_KEY` surfaces a
      legible error. ruff + mypy strict pass.

**Out of scope:** prices and returns (M2-03); unscheduled events, which have no consensus and stay
scenario priors ([calibration-dataset § 3.b](calibration-dataset.md)); event **detection** (M4);
event types beyond the three core ones (M5).

## M2-03 — Price history → `observations` returns

**Depends on:** M2-02 (rows to attach to), M2-01 (`RetUnit`, the `UNIQUE` constraint)

**Goal:** One `observations` row per (event × core instrument), carrying `px_t0` and the raw horizon
returns in an explicitly-typed unit — the grain everything downstream aggregates over.

**Context:** This is where the free-data ceiling becomes concrete, and where the milestone's most
expensive silent bug lives. [calibration-dataset § 8](calibration-dataset.md) names it: *"keep
`ret_unit` explicit so bps never get averaged with %"*. Four of the five core instruments are priced
(log returns, `pct`); the rates benchmark moves in **yield**, and a 5 bps move averaged into a set of
percentage returns produces a number that is not wrong-looking, merely wrong. Splitting the raw
returns (here) from the abnormal-return model (M2-04) keeps the expensive, mockable network fetch in
one place and the statistics in another, so each is testable alone.

**Files:** `src/fortuneteller/calibrate/prices.py`, `src/fortuneteller/calibrate/observe.py`,
`src/fortuneteller/__main__.py` (extend), `tests/test_prices.py`, `tests/test_observe.py`,
`pyproject.toml` (add `yfinance`)

**Spec:**
- CLI: `fortuneteller observe [--event <type>] [--from <date>] [--to <date>]` — fetch bars for every
  `event_instances` row in range and write `observations`.
- **Symbol map** (canonical instrument → free source), stated once in `prices.py` as a module-level
  table:

  | Instrument | Free source | `ret_unit` |
  | --- | --- | --- |
  | `SPY / ES` | yfinance `SPY` | `pct` |
  | `DXY` | yfinance `DX-Y.NYB` | `pct` |
  | `GC / XAU` | yfinance `GC=F` | `pct` |
  | `VIX` | yfinance `^VIX` | `pct` |
  | `BUND / FGBL` | FRED `DGS10` (UST-10Y daily yield) | `bps` |

  The free stack has **no** Bund series. The [roadmap](roadmap.md)'s own core definition names the
  rates leg as *"UST 10Y or Bund"*, so the UST-10Y stand-in is in-scope — but it must be **recorded,
  not hidden**: `data_source = "FRED:DGS10 (UST-10Y proxy for BUND / FGBL)"` on every such row.
- **Returns.** Price instruments: log return `ln(p_t / p_t0)`, `ret_unit = pct`. The rates
  benchmark: change in yield in **basis points**, `ret_unit = bps`
  ([calibration-dataset § 3.a](calibration-dataset.md)). `px_t0` is the last level strictly **before**
  `event_ts`.
- **Horizons and the intraday ceiling.** `ret_1d` and `ret_1w` from daily closes for every event.
  `ret_5m` and `ret_1h` **only** where 1-minute bars are actually available (yfinance's ~30-day
  window); otherwise **NULL**. Never interpolate a daily bar into an intraday return. An
  after-close release starts at the next open ([calibration-dataset § 3.a](calibration-dataset.md)).
- **Deterministic ids**, as in M2-02:
  `obs_id = int.from_bytes(blake2b(f"{event_id}|{instrument}".encode(), digest_size=8).digest(), "big") >> 1`.
  `INSERT OR REPLACE`; the M2-01 `UNIQUE (event_id, instrument)` is the backstop.
- `quality`: `high` when the full horizon set is present, `medium` when only daily bars are,
  `low` when `px_t0` had to come from a stale session.

**Acceptance criteria:**
- [ ] for a mocked bar set, `observe` writes exactly one row per (event × instrument) for the five
      core instruments, with hand-computable `ret_1d` values.
- [ ] `BUND / FGBL` rows carry `ret_unit = 'bps'` and a `data_source` naming the UST-10Y
      substitution; the other four carry `ret_unit = 'pct'`.
- [ ] an event older than the free 1-minute window stores `ret_5m IS NULL AND ret_1h IS NULL` while
      `ret_1d` is populated — asserted explicitly, so a future "helpful" fallback fails the test.
- [ ] re-running `observe` over the same range changes no rows.
- [ ] `tests/test_prices.py` / `tests/test_observe.py` run with **no live network**; ruff + mypy
      strict pass.

**Out of scope:** abnormal returns, CAR, `realized_dir`, `peak_move` (M2-04); `half_life_min`
(M2-05); tick data and paid vendors (post-proof); instruments beyond the core five (M5).

## M2-04 — Abnormal returns + CAR

**Depends on:** M2-03

**Goal:** `abn_ret_1d`, `car`, `peak_move` and `realized_dir` on every observation — the raw move with
ordinary market drift removed, so a cell's measured effect is attributable to the event.

**Context:** A raw +0.8% on a CPI day is not an 0.8% CPI effect; part of it is whatever the market was
doing anyway. [calibration-dataset § 3.c](calibration-dataset.md) removes that with a market model
estimated over t0−250…t0−20 trading days. The subtlety the spec flags and this ticket must settle:
the market model needs a benchmark the instrument is *not*. `SPY / ES` **is** the equity benchmark, so
regressing it on itself is degenerate (β≡1, AR≡0); `DXY`, `GC / XAU` and `VIX` have no equity
benchmark; `BUND / FGBL` is a yield. So all five core instruments use the **mean-return / mean-change**
variant the spec allows for exactly this case — the market-model path is implemented and tested
because M5's single-stock breadth needs it, not because the core five use it. The estimation window
ends at t0−20 to keep the estimate free of the event's own run-up
([§ 8, look-ahead bias](calibration-dataset.md)).

**Files:** `src/fortuneteller/calibrate/abnormal.py`, `src/fortuneteller/__main__.py` (extend),
`tests/test_abnormal.py`, `pyproject.toml` (add `statsmodels`)

**Spec:**
- **Estimation window:** t0−250 … t0−20 **trading** days, strictly before the event. Fewer than 60
  usable observations → leave `abn_ret_1d` NULL rather than fit a noisy model.
- **Two estimators**, one selected per instrument:
  - *Market model* (`statsmodels` OLS): `r_i,t = α_i + β_i · r_mkt,t + ε`, then
    `AR_i,t = r_i,t − (α_i + β_i · r_mkt,t)`. Implemented and unit-tested; used for equities that
    have a distinct benchmark. **No core-five instrument selects this path today.**
  - *Mean-return / mean-change model*: `AR_i,t = r_i,t − mean(r_i)` over the estimation window.
    Selected for all five core instruments — `SPY / ES` because it is the benchmark, `DXY` /
    `GC / XAU` / `VIX` because they have none, `BUND / FGBL` as a mean-**change** model in bps.
  - The selection is a declared table in the module, not an `if` chain buried in the fit function.
- **Outputs:** `abn_ret_1d` at the 1-day horizon; `car` = Σ AR over the event window (t0 … t0+1 for
  daily-grain events); `peak_move` = maximum absolute excursion in the window, in the row's
  `ret_unit`; `realized_dir` = `up` / `down` from `sign(abn_ret_1d)`, with a documented deadband
  (|abn_ret_1d| below it → `flat`) so noise is not recorded as a directional hit.
- Units are never mixed: every arithmetic path reads `observations.ret_unit`.

**Acceptance criteria:**
- [ ] on a synthetic series with known α / β, the market-model estimator recovers them and `AR` is
      zero to floating-point tolerance for a no-event day.
- [ ] the mean-change estimator on a hand-built bps series yields the hand-computed `abn_ret_1d`;
      `SPY / ES` resolves to the mean-return path, never the degenerate self-regression.
- [ ] `realized_dir` is `flat` inside the deadband, `up` / `down` outside it, and never `mixed` or
      `conditional` (the M2-01 `RealizedDir` enum makes this a type error).
- [ ] an event with fewer than 60 estimation-window observations leaves `abn_ret_1d` NULL.
- [ ] `tests/test_abnormal.py` uses fixed synthetic series (no network, no randomness); ruff + mypy
      strict pass.

**Out of scope:** `half_life_min` (M2-05); the aggregation into `effect_size_matrix` (M2-06);
confidence intervals on the *cell* magnitude, which M2-06 computes; regime **interactions** beyond
storing `vix_t0` / `rate_regime` (M3 / M5).

## M2-05 — Reaction half-life

**Depends on:** M2-04

**Goal:** `half_life_min` and a `HalfLife` bucket per observation — the answer to *"is this a spike
that retraces or a repricing that sticks?"*

**Context:** Magnitude alone cannot support a warning product with a stated horizon: a 1% move that is
gone in nine minutes and a 1% move that holds for a week are different products.
[calibration-dataset § 3.d](calibration-dataset.md) defines the measure — peak absolute excursion,
then time to retrace 50%. The free-data ceiling from M2-03 lands squarely here: with daily bars only,
a minute-resolution half-life **cannot** be measured for historical releases, and the honest response
is to bucket coarsely from the daily path and leave the numeric column NULL rather than to invent
minutes. The buckets already exist as the `HalfLife` enum
(`models.py:52`), which `effect_size_seed.reaction_half_life` already uses — reuse it, do not define a
parallel scale.

**Files:** `src/fortuneteller/calibrate/half_life.py`, `src/fortuneteller/__main__.py` (extend),
`tests/test_half_life.py`

**Spec:**
- **Intraday path** (1-minute bars present): find the peak absolute excursion from `px_t0` within the
  event window, then the first bar at which the move has retraced **50%** of that peak. Store the
  elapsed minutes in `half_life_min` and the matching `HalfLife` bucket.
- **Daily-only path** (the historical backfill): `half_life_min` stays **NULL**. Bucket from the daily
  path instead — peak day → first day retracing 50% — which can only ever resolve to `hours_days`,
  `days_weeks` or `weeks_plus`. Never emit `seconds_minutes` or `minutes_hours` from daily bars.
- **No 50% retrace in the window** → the longest bucket (`weeks_plus`), per § 3.d.
- Bucket boundaries are a single declared mapping (minutes → `HalfLife`), stated in the module so
  M2-06's median aggregation and this function cannot drift apart.

**Acceptance criteria:**
- [ ] a synthetic intraday spike that retraces 50% after 12 minutes yields `half_life_min == 12` and
      bucket `minutes_hours`; one retracing after 40 hours yields `hours_days`.
- [ ] a series that never retraces 50% yields `weeks_plus`.
- [ ] a daily-only series yields `half_life_min IS NULL` and a bucket in
      {`hours_days`, `days_weeks`, `weeks_plus`} — asserted, so an intraday bucket from daily bars
      fails the test.
- [ ] every returned bucket is a `HalfLife` member (no new scale introduced); ruff + mypy strict pass.

**Out of scope:** the per-cell **median** half-life (M2-06 aggregates it); horizon *prediction* from
the bucket (M3); intraday backfill of historical events, which the free stack cannot serve.

## M2-06 — The calibration query → `effect_size_matrix`

**Depends on:** M2-04, M2-05

**Goal:** `fortuneteller calibrate` — turn the observations into per-cell measured statistics
(`mag_per_sd`, `hit_rate`, `n_obs`, median half-life, `last_calibrated`) behind the **n ≥ 8** gate,
with a per-cell before/after report.

**Context:** This is the milestone's payoff, and it contains the one trap a verbatim port of the spec
walks into. [calibration-dataset § 5](calibration-dataset.md)'s query is an
`UPDATE effect_size_matrix … FROM calc` — it assumes the table already holds prior rows to overwrite.
In this repo it does **not**: M0 created `effect_size_matrix` deliberately empty and the priors live
in `effect_size_seed`. Ported verbatim, the query updates **zero rows**, and its `hit_rate` term —
which reads `esm.direction` — compares against NULL. So calibration here is explicitly **two steps**:
materialize the core grid first, then measure into it. The n ≥ 8 gate is not a detail either: with
~1,700 potential cells, low-n cells are noise wearing a decimal point
([§ 8, multiple testing](calibration-dataset.md)), and they must stay visible **as priors** rather
than be silently dropped.

**Files:** `src/fortuneteller/calibrate/calibrate.py`, `src/fortuneteller/__main__.py` (extend),
`data/seed/surprise_response.csv` (extend), `tests/test_calibrate.py`

**Spec:**
- **Step 1 — materialize the grid.** `INSERT OR REPLACE` the **15** core cells (3 event types × 5
  instruments) into `effect_size_matrix`:
  - `direction`: for a `conditional` cell take `surprise_response.hot_direction`, which is the
    concrete direction on an above-consensus print and therefore the one `hit_rate` can score
    against; otherwise the `effect_size_seed.direction`. A cell with neither stays `conditional` and
    is excluded from the hit-rate aggregation rather than scored against a guess.
  - `surprise_dep` from `effect_size_seed.surprise_dependent`; measured columns NULL; `n_obs = 0`;
    `last_calibrated` NULL.
  - The **8 cells with no seed prior** (all five `NFP / labor data` cells, plus
    `Central-bank decision` × `BUND / FGBL` / `GC / XAU` / `VIX`) are inserted prior-less. This is
    intentional — see *Known seed gap* in the Shared Context.
  - **Extend `data/seed/surprise_response.csv`** with the `NFP / labor data` and
    `Central-bank decision` cells so those directions exist. Keep the header comment's completeness
    statement accurate ("scheduled-macro core slice only; illustrative placeholders, not
    authoritative").
- **Step 2 — measure.** Port [calibration-dataset § 5](calibration-dataset.md) to DuckDB, **lowercase
  per M2-01** (`WHEN 'up' THEN 1 WHEN 'down' THEN -1`):
  - `mag_per_sd = Σ(abn_ret_1d · surprise_sd) / Σ(surprise_sd²)` — the per-1-SD sensitivity.
  - `hit_rate` = share of observations whose `realized_dir` matches the cell's `direction`.
  - `median_half_life` = the median `HalfLife` bucket over the cell's observations (bucket-median, not
    a mean of minutes — `half_life_min` is NULL for the daily-only history).
  - `n_obs = count(*)`; `last_calibrated` stamped at run time.
  - `WHERE surprise_sd IS NOT NULL` and **`HAVING count(*) >= 8`**. Cells below the gate keep their
    prior row, `n_obs` at the true count, and NULL measured columns — they are **not** deleted.
  - Aggregate per `ret_unit`; a cell never mixes `pct` and `bps` observations.
- **Confidence intervals:** `mag_ci_low` / `mag_ci_high` from the `statsmodels` regression of
  `abn_ret_1d ~ surprise_sd` with `cov_type="HC3"` ([§ 5](calibration-dataset.md)), per cell.
- **Report:** print one line per cell — `event_type × instrument`, prior vs measured `mag_per_sd`,
  `hit_rate`, `n_obs`, and whether it passed the gate. `--json` for the structured form.
- Writes to **DuckDB only**. Nothing here touches `data/seed/` except the `surprise_response.csv`
  extension above, and nothing here is read by `replay()`.

**Acceptance criteria:**
- [ ] on a fixture DB with 10 synthetic observations for one cell, `calibrate` produces the
      hand-computed `mag_per_sd` and `hit_rate`, `n_obs == 10`, and a non-NULL `last_calibrated`.
- [ ] a cell with 7 observations keeps NULL measured columns and is reported as gated — asserted
      explicitly, since a silently-calibrated low-n cell is the failure this gate exists to prevent.
- [ ] step 1 alone, on an empty `observations` table, still yields **15** rows in
      `effect_size_matrix` with `n_obs = 0` — proving the query is not a no-op against this repo's
      empty-table starting state.
- [ ] re-running `calibrate` twice yields identical values (only `last_calibrated` advances).
- [ ] `uv run fortuneteller seed` still loads `surprise_response.csv` idempotently and its contract
      test (`tests/test_surprise_response.py`) still passes with the new rows.
- [ ] ruff + mypy strict pass.

**Out of scope:** writing anything back into `data/seed/effect_size_seed.csv` (M2-07); probability
calibration, conformal bands and the reader-visibility gate (M3); regime-bucketed cells beyond
storing `vix_t0` / `rate_regime` (M5).

## M2-07 — Promote calibrated cells into the prediction core

**Depends on:** M2-06

**Goal:** `fortuneteller promote` — the single, explicit, reviewable path by which a measured number
reaches `replay()`, as a committed `effect_size_seed.csv` diff plus regenerated goldens.

**Context:** This ticket exists to *protect* the determinism firewall, not to bypass it. The dev loop
rests on *same inputs → identical bytes*, which holds only because `replay()` reads **committed** CSVs;
if it read the locally-calibrated `effect_size_matrix`, every golden would depend on whoever last ran a
backfill. So promotion is a human-reviewed commit, and it is deliberately `--dry-run` by default. The
step is also not a copy: the two tables have **different column shapes**. `effect_size_matrix` holds
numerics (`mag_per_sd`, `hit_rate` as a float, `n_obs`); `effect_size_seed.csv` holds human strings
(`typical_magnitude` = `"0.5-1.5%"`, `hit_rate_est` = `"~62%"`, `reaction_half_life` = a `HalfLife`
value). Promotion is a **formatting** step with a stated mapping — left unstated, every executor
invents a different one.

**Files:** `src/fortuneteller/calibrate/promote.py`, `src/fortuneteller/__main__.py` (extend),
`tests/test_promote.py`

**Spec:**
- CLI: `fortuneteller promote [--apply]`. **Default is a dry run** that prints the diff and writes
  nothing; `--apply` rewrites `data/seed/effect_size_seed.csv` in place.
- **Eligibility:** only cells with `n_obs >= 8` **and** a non-NULL `last_calibrated`. Everything else
  is left exactly as it is.
- **Column mapping** (`effect_size_matrix` → `effect_size_seed.csv`):

  | Target column | Source | Rule |
  | --- | --- | --- |
  | `typical_magnitude` | `mag_ci_low` / `mag_ci_high` | absolute values, one decimal, joined `low-high`, suffixed `%` when the cell's `ret_unit` is `pct` and ` bps` when it is `bps` (e.g. `0.4-1.1%`, `3-9 bps`). Missing CIs → a ±25% band around `mag_per_sd`. |
  | `hit_rate_est` | `hit_rate` | `~NN%`, rounded to a whole percent — matching the existing file's style. |
  | `reaction_half_life` | `median_half_life` | the `HalfLife` value verbatim. |
  | `basis` | — | `calibrated YYYY-MM-DD (n=NN)`, replacing `placeholder seed`. |
  | `direction` | — | **unchanged.** `conditional` cells stay conditional; the M1-03 resolver owns direction. |
  | `direction_confidence` | — | **unchanged.** Confidence calibration is M3. |

- A cell with no existing CSV row is **appended**; existing rows are edited in place. Row order and
  the header comment are preserved so the diff stays readable.
- **Regenerate goldens in the same change:** `uv run pytest --update-golden` (the flag is defined in
  `tests/conftest.py`; `FT_UPDATE_GOLDEN=1` is the env-var equivalent). Then read the diff — a
  magnitude change that alters a warning is exactly what review is for.
- The executor must confirm `git diff --stat` shows only `data/seed/effect_size_seed.csv` and
  `episodes/*.golden.json`.

**Acceptance criteria:**
- [ ] a dry run prints the intended per-cell changes and leaves `data/seed/effect_size_seed.csv`
      byte-unchanged — asserted on the file's bytes, not on stdout alone.
- [ ] `--apply` on a fixture matrix produces the exact expected CSV text, including the
      `calibrated YYYY-MM-DD (n=NN)` basis and the `~NN%` hit-rate format.
- [ ] a `bps` cell renders ` bps` and a `pct` cell renders `%`; a cell with `n_obs = 7` is untouched.
- [ ] `direction` and `direction_confidence` are byte-identical before and after.
- [ ] after `--apply` plus `pytest --update-golden`, `uv run pytest` is green and two consecutive
      `replay` runs are byte-identical.
- [ ] ruff + mypy strict pass.

**Out of scope:** automatic promotion (it is a reviewed human step, by design); confidence values
(M3); any `replay/` code change — the engine keeps reading the CSV exactly as it does today.

## M2-08 — Scheduled recalibration + outcome capture

**Depends on:** M2-06

**Goal:** `fortuneteller recalibrate` plus an APScheduler job that re-runs the pipeline on a rolling
window and records how past warnings actually turned out — closing the feedback loop.

**Context:** [Roadmap → M2](roadmap.md)'s "done when" includes *"the loop re-runs on a schedule"*, and
[§ 8](calibration-dataset.md) gives the reason: regime non-stationarity. A matrix calibrated once
decays — the same CPI surprise moves a 2022 market and a 2026 market differently, so a fixed
calibration silently becomes a stale one. Scheduling is also the **only** way the intraday columns
ever fill: `ret_5m`, `ret_1h` and a minute-resolution `half_life_min` are unavailable for historical
releases (M2-03), but a job that runs shortly after each release sees the data inside the free 30-day
1-minute window. Every run makes the dataset strictly better than a one-shot backfill could.

**Files:** `src/fortuneteller/calibrate/schedule.py`, `src/fortuneteller/__main__.py` (extend),
`tests/test_schedule.py`, `pyproject.toml` (add `apscheduler`)

**Spec:**
- CLI: `fortuneteller recalibrate [--window-days N] [--once]`. `--once` runs the chain immediately and
  exits (this is what tests and CI exercise); without it, an APScheduler `BlockingScheduler` runs it on
  the configured interval.
- **The chain**, in order, over the rolling window: `backfill` → `observe` → abnormal returns →
  half-life → `calibrate`. Each step is the same function the corresponding CLI subcommand calls — no
  duplicated logic.
- **Outcome capture:** for each `event_instances` row now old enough to have a settled reaction,
  record the realized outcome against what the effect-size matrix predicted at the time
  (`direction` hit / miss and realized vs expected magnitude), so `hit_rate` reflects live behaviour
  and not just the backfill. Store it in the existing `observations` columns — this ticket adds **no
  new table**.
- Idempotent throughout: every write is the `INSERT OR REPLACE` on a derived id from M2-02 / M2-03, so
  overlapping windows converge instead of duplicating.
- Schedule and window are configuration (`pydantic-settings`, `FT_`-prefixed), not constants.
- Errors in one step are logged and do not abort the remaining events — a single missing release
  must not stall the loop.

**Acceptance criteria:**
- [ ] `fortuneteller recalibrate --once` with mocked sources runs the full chain and leaves
      `effect_size_matrix` in the same state a manual `backfill` → `observe` → `calibrate` produces.
- [ ] running it twice over an overlapping window changes no row counts.
- [ ] a simulated fetch failure for one event is logged and the remaining events still process
      (asserted, not just observed).
- [ ] `tests/test_schedule.py` runs with **no live network and no real sleep** — the scheduler is
      exercised via `--once` or a mocked trigger, never by waiting.
- [ ] ruff + mypy strict pass.

**Out of scope:** alerting and delivery channels (M6); a long-running service, containers or process
supervision (M7); the backtest harness and the reader-visibility gate (M3); detection (M4).

---

### Execution summary

Implement M2-01 first — it settles enum casing and adds the constraints, and every later ticket
writes the columns it constrains. Then build the dataset bottom-up: M2-02 fills `event_instances`
with correctly-timestamped releases and their standardized surprises; M2-03 attaches raw returns in
explicit units; M2-04 strips market drift to get abnormal returns; M2-05 measures how long each
reaction lasts. M2-06 is the payoff — it materializes the 15-cell core grid and overwrites it with
measured statistics behind the n ≥ 8 gate. M2-07 promotes the cells that earned it into the committed
seed CSV, with regenerated goldens, as the single reviewed path across the determinism firewall.
M2-08 puts the loop on a schedule so the numbers stay current and the intraday columns fill forward.

M2 is done when the core cells carry measured `mag_per_sd`, `hit_rate` and `n_obs` from n ≥ 8
observations, `replay` is still byte-identical run to run, and `just check` is green. **M3** then makes
the probabilities honest (calibration, conformal bands, the backtest gate) and blocks reader warnings
for cells that have not earned them.
