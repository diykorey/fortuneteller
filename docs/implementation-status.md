# Implementation Status — What's Built and How It Works

> A precise, code-anchored account of what exists in the repository today, how each piece works, and
> what is deliberately not built yet. For the *why* see [Business Overview](business-overview.md);
> for the plan see the [Roadmap](roadmap.md) and the ticket sets it links.

## Snapshot

| Milestone | Scope | Status |
| --- | --- | --- |
| **M0** — Scaffold & data spine | uv/CI, Pydantic models, DuckDB schema, seed loader, CLI | ✅ Built & merged |
| **M0-R** — Replay harness | Deterministic offline episode-replay of the prediction core | ✅ Built & merged |
| **M1 (offline core)** — Thin vertical slice | Surprise computation + conditional-direction resolver wired into replay | ✅ Built & merged |
| **M1 (live path)** — FRED + econ calendar | `predict` CLI over a real CPI release | ⛔ Not built (optional validation) |
| **M2+** — Calibration, confidence, detection, product | Measured effect sizes, calibrated confidence, unscheduled events | ⛔ Not built |

The suite is green: **`ruff` + `mypy --strict` + 85 passing tests** (1 skipped). CI runs the same
gate on every push.

## The mental model: a 10-stage pipeline, middle first

The north-star pipeline has ten stages; the build starts from the **deterministic middle** and works
outward:

```
[1] ingest   [2] classify   [3] entity-link   [4] corroborate   ← detection (M4, NOT built)
[5] surprise → [6] effect-size lookup → [7] direction resolve → [8] warning   ← BUILT (M0-R + M1)
[9] calibrate confidence   [10] capture outcome → recalibrate   ← M2/M3 (NOT built)
```

Everything built today lives in **stages 5–8**: given an already-known event, compute its surprise,
look up the effect on each instrument, resolve a concrete direction, and emit a structured warning.
Detection (1–4) is noisy and non-deterministic, so it is deferred to M4; calibration (9–10) is M2/M3.

Call-by-call diagrams of each flow: [Sequence Diagrams & Use Cases](sequence-diagrams.md).

## Layer 1 — The data spine (M0)

The typed foundation everything else reads. **No ORM**: Pydantic models in, parameterized SQL over
DuckDB, typed models out.

| Module | Role |
| --- | --- |
| `src/fortuneteller/config.py` | Typed `settings` singleton (DB path, seed dir, schema path); override via `FT_`-prefixed env vars. |
| `src/fortuneteller/models.py` | Pydantic v2 models + lowercase str-enums (`Direction`, `HalfLife`, `Confidence`, …) with `extra="forbid"`. |
| `schema.sql` | Plain DuckDB DDL — 9 tables (reference + fact + the M1 `surprise_response`). Kept as SQL so a later Postgres migration stays cheap. |
| `src/fortuneteller/db.py` | The thin SQL helper: `get_connection`, `init_db`, `insert_models` (idempotent `INSERT OR REPLACE`), and typed getters (`get_effect_size`, `get_event_type`, `get_surprise_response`, …). |
| `src/fortuneteller/seed.py` | Reads the committed `data/seed/*.csv`, validates each row against its model (failing loudly with file+row), and loads them. Idempotent. |
| `src/fortuneteller/__main__.py` | The CLI: `init`, `seed`, `query-demo`, `replay`. |

**Reference data is config, not code.** The event taxonomy, instruments, effect-size seeds, and the
surprise-response mapping are committed CSVs in `data/seed/` that the pipeline *reads* — so the
system is tuned by editing data, not logic. (Seed values are illustrative placeholders until M2
calibration replaces them with measured numbers.)

## Layer 2 — The replay harness (M0-R)

**The fast dev loop and the spine of iteration.** It replays a canned event through the
deterministic core so prediction logic is built and verified against episodes instead of waiting for
live data. Full rationale: [Replay-harness design](superpowers/specs/2026-06-22-replay-harness-fast-dev-loop-design.md).

| Piece | Role |
| --- | --- |
| `src/fortuneteller/replay/models.py` | `Episode` / `EpisodeEvent` (an already-detected event + regime context) and `Warning` (the structured, assertable output). |
| `src/fortuneteller/replay/engine.py` | `replay(episode) -> list[Warning]` — the pure core; plus `load_episode`, `validate_keys`, and the JSON/table serializers the CLI wraps. |
| `episodes/*.json` | Committed scenarios (war, depeg, terror, CPI, no-edge). |
| `episodes/*.golden.json` | The exact expected `replay()` output for each episode, asserted byte-for-byte. |
| `tests/test_replay.py` | Parametrized golden + intent tests; `--update-golden` / `FT_UPDATE_GOLDEN=1` regenerates snapshots. |

**How `replay()` works.** For each instrument in the episode, it looks up the `effect_size_seed`
cell for `(event_type, instrument)`:

- **Found, concrete direction** (e.g. war → Brent `up`) → emit that direction.
- **Found, `conditional`** (CPI, Fed, …) → at M0-R this stayed `"conditional"`; M1 now resolves it
  (below).
- **Missing** → emit an honest `"no edge vs market-implied"` warning, never a crash.

The **determinism guarantee** is the property the whole loop rests on: `as_of` comes from the
episode's `t0` (never `now()`), warnings are ordered by the episode's instrument list, seed data is
committed, and there is no randomness. **Same inputs → identical bytes**, which is exactly what makes
golden-file testing possible and gives a fast build → verify → read-diff cycle with no live data or
credentials.

## Layer 3 — The prediction core (M1, offline)

M1 enriches the harness's thinnest-possible logic into real prediction logic for the CPI slice, all
**pure, offline, deterministic** (no LLM, no network) so the byte-for-byte guarantee holds.

### Surprise computation — `src/fortuneteller/predict/surprise.py` (stage 5)

Turns a release into a standardized surprise the predictor can act on:

- `compute_surprise(consensus, actual)` → the signed gap `actual − consensus`.
- `standardize(surprise, history)` → `surprise / stdev(recent history)`, or `None` when history is
  too short (< 24) or has no dispersion. This is `surprise_sd`.
- `surprise_sign(surprise_sd)` → `"above"` / `"below"` / `"unknown"`. This is the **single source of
  truth** the replay engine reads, so the harness has one convention.

### The surprise-response mapping — `data/seed/surprise_response.csv` (M1-02)

New reference data the resolver looks up, keyed `(event_type, instrument)`:

- `hot_direction` — the resolved direction on an **above-consensus** (hot) surprise.
- `regime_sensitive` — marks cells subject to the "good news is bad news" regime flip.

The CPI core slice is seeded: `SPY / ES → down`, `BUND / FGBL → down`, `DXY → up`, `GC / XAU → down`,
`VIX → up` (with `SPY / ES` and `DXY` regime-sensitive). The two missing CPI effect cells (`DXY`,
`VIX`) were also appended so all five core instruments exist.

### The conditional-direction resolver — `src/fortuneteller/predict/direction.py` (M1-03)

The headline feature — turn `conditional` + surprise sign + regime into a concrete up/down:

- **above** → the cell's `hot_direction`.
- **below** → the inverse of `hot_direction` (`up`↔`down`, `mixed`→`mixed`).
- **unknown / in-line / no mapping** → `mixed` (honest "no edge" — never invent a direction).
- **Regime flip:** for a regime-sensitive cell in a rate-cut-hungry regime, a benign (below) print
  stops being risk-on and inverts back — the documented "good news is bad news" override. (This is a
  deliberately simple placeholder over illustrative seed data; calibrated regime handling is M2/M3.)

### Wiring it into replay — `src/fortuneteller/replay/engine.py` (M1-04)

`replay()` now resolves a `conditional` cell against the instance's surprise and regime:

- Known surprise (above/below) with a mapping → a concrete `up`/`down`.
- In-line scheduled print (surprise present but ≈ 0) → an honest `mixed`.
- Genuinely absent surprise (unscheduled conditional event) → keeps the `"conditional"` placeholder.

Non-conditional cells and the no-edge path are unchanged — the war/depeg/terror/no-edge goldens stay
byte-identical.

## End-to-end: a worked example

Running the hot-CPI episode through the built pipeline:

```bash
uv run fortuneteller replay episodes/cpi-hot-2026-03.json
```

```
instrument   direction  magnitude  half_life        confidence  surprise_sign
-----------  ---------  ---------  ---------------  ----------  -------------
SPY / ES     down       0.5-1.5%   minutes_hours    high        above
BUND / FGBL  down       3-10 bps   minutes_hours    high        above
DXY          up         0.3-1%     minutes_hours    high        above
GC / XAU     down       0.4-1.2%   minutes_hours    medium      above
VIX          up         3-15%      seconds_minutes  medium      above
```

What happened, stage by stage: the episode supplies a CPI release with `actual` above `consensus`
(**stage 5** → `surprise_sd = 1.8` → sign `above`); for each instrument the engine looks up the
`effect_size_seed` cell (**stage 6**); each is `conditional`, so the resolver maps `above` +
`on-hold` regime to a concrete direction via `surprise_response` (**stage 7**); and each becomes a
structured `Warning` with `as_of` fixed to the episode's `t0` (**stage 8**). The cool episode yields
the inverses; the in-line episode yields all `mixed`.

## How to run it

```bash
uv sync                                              # install deps + dev group
uv run fortuneteller seed                            # load seed CSVs into DuckDB
uv run fortuneteller replay episodes/cpi-hot-2026-03.json [--json]
uv run pytest                                        # golden + intent + unit tests
uv run ruff check && uv run mypy src                 # the same gate CI enforces
```

`replay` refreshes the store from the committed CSVs on each run (idempotent), so it works from a
clean checkout without a manual seed step.

## What is deliberately not built yet

- **M1 live path (M1-06/07):** fetching a real CPI release from FRED + a free econ calendar and
  running it through the *same* core. This is optional live-validation, not the dev gate — the
  offline slice above is the demoable prototype.
- **Detection (M4):** stages 1–4 (ingest, classify, entity-link, corroborate). Episodes stand in for
  a detected event today.
- **Calibration & confidence (M2/M3):** measured effect sizes, calibrated probabilities, magnitude
  bands, and the backtest gate. Today's magnitudes/confidences are **illustrative seed placeholders**.
  M2 is decomposed into executable tickets in [m2-tickets.md](m2-tickets.md), mirrored as issues
  [#55](https://github.com/diykorey/fortuneteller/issues/55)–[#62](https://github.com/diykorey/fortuneteller/issues/62)
  (label `M2`), all open.
- **The causal-chain layer, coverage expansion, productization, and operations (M5–M7).**

## Where the code lives (branches)

- **`main`** — M0, M0-R, and the M1 offline core (M1-01…05) are all merged here; no feature branch
  is outstanding.

See the ticket sets for the executable breakdown: [M0](m0-tickets.md) · [M0-R](m0-r-tickets.md) ·
[M1](m1-tickets.md) · [M2](m2-tickets.md).
