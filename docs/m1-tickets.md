# M1 Tickets — Prototype: the thin vertical slice

> Written to be consumed by an LLM coding agent, same as [M0 Tickets](m0-tickets.md) and
> [M0-R Tickets](m0-r-tickets.md). Read the Shared Context once, then any ticket can be implemented
> in isolation. Every ticket states exact file paths, an explicit spec, and binary acceptance
> criteria.
>
> Milestone source: [Roadmap → M1](roadmap.md). Design sources:
> [MVP architecture](mvp-architecture.md), [Replay-harness spec](superpowers/specs/2026-06-22-replay-harness-fast-dev-loop-design.md),
> [Calibration dataset](calibration-dataset.md), [Event polarity & classifier prompts](event-polarity-and-classifier-prompts.md).

## Shared Context (read once, applies to every M1 ticket)

**Why.** M1 is the **thin vertical slice**: take one event type from input to a warning, end to end,
**deterministically**. It enriches the replay harness's *thinnest possible* logic into real
prediction logic — proper surprise handling, **conditional-direction resolution**, and instrument
selection — then wires a **free live path** (FRED + a free econ calendar) behind the same function.
No detection, no real calibration (still seed priors). This is the demoable prototype.

**Prerequisites (must land first).**
- **M0-01…09** — scaffold + data spine (`uv`, models, DuckDB, seed loader, CI). **Done / merged.**
- **M0-R-01…05** — the [replay harness](m0-r-tickets.md) (`Fixture` / `Warning` models, `replay()`
  core, `replay` CLI, synthetic fixtures + goldens, golden/intent tests). **Specified but not yet
  built** — there is no `src/fortuneteller/replay/` or `fixtures/` directory yet. **M0-R must be
  implemented before any M1 ticket.** M1 *enriches* this harness; it does not restate it.

**Scope discipline (the provable core).** M1 calibrates exactly one slice:
**`CPI / inflation surprise` × ~5 liquid instruments** — `SPY / ES`, `BUND / FGBL` (rates benchmark),
`DXY`, `GC / XAU`, `VIX`. The full 31-event taxonomy, the other ~50 instruments, unscheduled
detection, calibration, and confidence are **post-proof** — do not implement against their breadth.

**Conventions.** Reuses the M0 package (`src/fortuneteller`), the M0-03 enums, and the seeded DuckDB
from M0-05/07. Canonical `event_type` keys and instrument **symbols** are exactly those in
[`data/seed/event_types.csv`](../data/seed/event_types.csv) /
[`data/seed/instruments.csv`](../data/seed/instruments.csv) (e.g. `CPI / inflation surprise`,
`SPY / ES`, `BUND / FGBL`). Enum values stay **lowercase** (`up`, `down`, `mixed`, `conditional`) —
**do not reconcile casing**, that is M2's job. `mypy --strict` over `src`; line length 100; tests use
the `# given` / `# when` / `# then` structure.

**Resolution is deterministic — no LLM.** For the scheduled-macro CPI slice, direction is fully
determined by the surprise sign + rate regime + per-instrument asset rules
([price the surprise; "good news is bad news"](event-polarity-and-classifier-prompts.md)). The
Anthropic / `instructor` classifier is for *unscheduled free-text* events and belongs to **M4**. M1's
resolver must be a **pure, offline, deterministic function** so the replay harness keeps its
byte-for-byte guarantee.

**Determinism rule (the property the loop rests on).** No `now()` / randomness in the prediction
core; `as_of` comes from the fixture's `t0`; warnings are ordered by the fixture's instrument order;
seed data is committed. Same inputs → identical bytes. Networked code lives **only** in
`src/fortuneteller/live/` and is **never imported by `src/fortuneteller/replay/`**.

**Definition of done for M1.**
1. `uv run fortuneteller replay fixtures/cpi-hot-2026-03.json --json` resolves **concrete**
   directions for the conditional CPI cells (no longer `"conditional"`); exit 0.
2. `uv run pytest tests/test_replay.py` passes — every CPI fixture matches its golden and every
   `expect` direction holds.
3. `uv run fortuneteller predict --event "CPI / inflation surprise" --release-date <date>` runs the
   same prediction core over a live-fetched release (optional live-validation, not the dev gate).
4. Re-running `replay` twice yields byte-identical output.
5. `uv run ruff check` and `uv run mypy src` pass; `just check` is green.

**Dependency order.** M1-01 → M1-02 → M1-03 → M1-04 → M1-05, then the live path M1-06 → M1-07
(which reuse M1-01 / M1-03). Depends on M0-R-01…05 and M0-03/05/07 from the prior sets.

---

## M1-01 — Surprise computation (stage 5)

**Depends on:** M0-R-01 (`FixtureEvent`)

**Context:** The first enrichment — turn a release's `consensus` / `actual` into a standardized
surprise the predictor can act on.

**Files:** `src/fortuneteller/predict/__init__.py`, `src/fortuneteller/predict/surprise.py`

**Spec:**
- Pure functions, no clock / IO / randomness:
  - `compute_surprise(consensus: float, actual: float) -> float` → `actual - consensus` (signed).
  - `standardize(surprise: float, history: Sequence[float]) -> float | None` →
    `surprise / stdev(history)` over the last 24–36 historical surprises
    ([calibration-dataset § 3.b](calibration-dataset.md)); `None` when history is too short or
    `stdev == 0`.
  - `surprise_sign(surprise_sd: float | None) -> Literal["above","below","unknown"]` →
    `"above"` if `> 0`, `"below"` if `< 0`, else `"unknown"` (matches the M0-R-02 convention so the
    engine reads one source of truth).

**Acceptance criteria:**
- [ ] known `consensus` / `actual` → expected signed surprise; a hand-computed synthetic history
      reproduces `surprise_sd` exactly.
- [ ] zero / near-zero / short-history → `surprise_sign == "unknown"`.
- [ ] unit tests in `tests/test_surprise.py` (`# given` / `# when` / `# then`); mypy strict + ruff pass.

**Out of scope:** live data fetch (M1-06); abnormal returns / `observations` (M2).

## M1-02 — Complete the CPI core slice + surprise-response mapping (config)

**Depends on:** M0-05 / M0-07 (seed loader + schema), M0-R-01

**Context:** The resolver needs data M0 never captured — which way each cell moves on a hot
(above-consensus) surprise — and the CPI slice is missing two of its five cells. Add both as
committed config (reference tables are config the pipeline reads).

**Files:** `data/seed/effect_size_seed.csv` (append rows), `data/seed/surprise_response.csv` (new),
`schema.sql` (new `surprise_response` table), `src/fortuneteller/models.py` (new model),
`src/fortuneteller/seed.py` (load the new table), `src/fortuneteller/db.py` (getter)

**Spec:**
- **Complete the slice.** `effect_size_seed.csv` currently has CPI cells for `SPY / ES`,
  `BUND / FGBL`, `GC / XAU` only. Append `conditional` placeholder rows for
  `CPI / inflation surprise × DXY` and `CPI / inflation surprise × VIX` (illustrative magnitudes,
  `surprise_dependent = yes`, `basis = placeholder seed`) so all five core cells exist. Additive to
  the frozen M0 seed — no existing rows change.
- **Surprise-response mapping.** New `surprise_response.csv` keyed `(event_type, instrument)` with:
  `hot_direction` (the resolved `Direction` on an **above-consensus** surprise) and
  `regime_sensitive` (`yes`/`no`, marks cells subject to the "good news is bad news" flip). Seed the
  CPI slice: `SPY / ES`→`down`, `BUND / FGBL`→`down`, `DXY`→`up`, `GC / XAU`→`down`, `VIX`→`up`
  (`regime_sensitive = yes` for `SPY / ES`, `DXY`). Header comment states completeness: "CPI core
  slice only; illustrative placeholders, not authoritative."
- `SurpriseResponse` Pydantic model mirrors the CSV columns (`extra="forbid"`); `schema.sql` table
  PK `(event_type, instrument)`; loader is idempotent (`INSERT OR REPLACE`); `db.get_surprise_response(event_type, instrument)` returns the row or `None`.

**Acceptance criteria:**
- [ ] `uv run fortuneteller seed` loads idempotently (re-run is a no-op); `get_surprise_response`
      returns the new cells; all five `CPI ×` core cells resolve in `effect_size_seed`.
- [ ] a contract test (`tests/test_surprise_response.py`) asserts every `surprise_response` key
      exists in `event_types.csv` / `instruments.csv`, that the CPI slice has all five cells, and that
      the loader is idempotent (second `load_all` is a no-op).
- [ ] ruff + mypy strict pass.

**Out of scope:** the full matrix; calibrated magnitudes (M2); enum-casing reconciliation (M2).

## M1-03 — Conditional-direction resolver (the headline feature)

**Depends on:** M1-01, M1-02

**Context:** The core M1 deliverable deferred at M0-R — turn `conditional` + surprise sign + regime
into a concrete up / down.

**Files:** `src/fortuneteller/predict/direction.py`

**Spec:**
- Pure, deterministic, offline (no LLM, no network):
  `resolve_direction(event_type: str, instrument: str, surprise_sign: str, rate_regime: str | None, con=None) -> Direction`.
- Look up the `surprise_response` cell (M1-02):
  - `surprise_sign == "above"` → `hot_direction`.
  - `surprise_sign == "below"` → the inverse of `hot_direction` (`up`↔`down`; `mixed`→`mixed`).
  - `surprise_sign == "unknown"` (in-line), missing mapping, or genuinely undetermined → `mixed`
    (honest "no edge" — **never invent** a direction).
- Regime flip: when the cell is `regime_sensitive` and `rate_regime` indicates easing-hungry
  conditions, a hot print is extra-bearish for risk — apply the documented good-news-is-bad-news
  flip ([event-polarity § overriding rules](event-polarity-and-classifier-prompts.md)).

**Acceptance criteria:**
- [ ] hot CPI → `SPY / ES` `down`, `DXY` `up`, `GC / XAU` `down`, `BUND / FGBL` `down`, `VIX` `up`;
      cool CPI → the inverses; in-line → `mixed`.
- [ ] the `regime_sensitive` flag flips the documented cells; two calls with identical inputs are
      identical.
- [ ] unit tests in `tests/test_direction.py`; ruff + mypy strict pass.

**Out of scope:** LLM classification of free-text events (M4); magnitude calibration (M2); event
types / instruments beyond the CPI core slice.

## M1-04 — Enrich `replay()` to resolve conditional cells

**Depends on:** M0-R-02 (the engine exists), M1-03

**Context:** Wire the resolver into the deterministic engine so conditional cells emit a concrete
direction instead of `"conditional"`.

**Files:** `src/fortuneteller/replay/engine.py` (extend), `tests/test_engine_resolution.py` (new),
`fixtures/cpi-hot-2026-03.golden.json` (regenerate)

**Spec:**
- For a `conditional` seed cell, when `surprise_sign` is known (`"above"` / `"below"`), call
  `resolve_direction(event.event_type, symbol, surprise_sign, event.rate_regime)` and emit the
  concrete `up` / `down` on the `Warning`. When `surprise_sign == "unknown"` or the resolver returns
  `mixed`, keep the M0-R behaviour (`direction` stays `"conditional"` / `mixed`).
- Non-conditional cells and the "no edge" path are unchanged.
- Preserve every determinism guarantee: ordering by `fixture.instruments`, `as_of = fixture.t0`,
  `surprise_sign` passthrough, no clock / randomness, byte-identical reruns.
- **Golden sequencing:** this change re-points only the existing `cpi-hot-2026-03` golden (was
  `"conditional"`). Regenerate that one golden here so `tests/test_replay.py` stays green; the two
  *new* CPI fixtures + their goldens + all `expect` blocks land in M1-05.

**Acceptance criteria:**
- [ ] a focused test (`tests/test_engine_resolution.py`) asserts `replay()` resolves the
      `cpi-hot-2026-03` conditional CPI cells to concrete directions (not `"conditional"`), driven by
      the M1-03 resolver — independent of the golden file.
- [ ] `tests/test_replay.py` stays green: the regenerated `cpi-hot-2026-03` golden matches; the
      `war` / `depeg` / `terror` / `no-edge` goldens are byte-unchanged.
- [ ] two runs are byte-identical; ruff + mypy strict pass.

**Out of scope:** live data (M1-06); calibration / confidence (M2 / M3).

## M1-05 — CPI fixtures + goldens + intent `expect`s

**Depends on:** M1-04, M0-R-04 / M0-R-05 (fixture set + golden/intent test harness)

**Context:** Lock the resolved CPI behaviour into the fast loop, and fill in the `expect` directions
deferred at M0-R now that resolution exists.

**Files:** `fixtures/cpi-hot-2026-03.json` (add `expect`), `fixtures/cpi-cool-2026-04.json`,
`fixtures/cpi-inline-2026-05.json`, and matching `fixtures/*.golden.json`

**Spec:**
- Three CPI fixtures over the five core instruments (`SPY / ES`, `BUND / FGBL`, `DXY`, `GC / XAU`,
  `VIX`):
  - `cpi-hot-2026-03` — `surprise_sd > 0`; add resolved `expect`
    (`SPY / ES`→down, `DXY`→up, `GC / XAU`→down, `BUND / FGBL`→down, `VIX`→up).
  - `cpi-cool-2026-04` — `surprise_sd < 0`; `expect` = the inverses.
  - `cpi-inline-2026-05` — `surprise_sd ≈ 0`; `expect` = all `mixed` (no edge).
- Adding `expect` to `cpi-hot-2026-03.json` does **not** change its golden (`expect` is fixture
  metadata, not `replay()` output — that golden was settled in M1-04). Generate the goldens for the
  two **new** fixtures with `--update-golden` (M0-R-05), then read the git diff to confirm intent. The
  existing parametrized `tests/test_replay.py` auto-covers the new fixtures and their `expect`s.

**Acceptance criteria:**
- [ ] each fixture validates against `Fixture`; every `event_type` / instrument key exists in the
      seed CSVs.
- [ ] `uv run pytest tests/test_replay.py` is green — every CPI golden matches and every `expect`
      direction holds; a wrong-direction change still fails the intent test (cannot be silently
      blessed).

**Out of scope:** recorded real events (M2); non-CPI fixtures.

## M1-06 — Free live path: FRED + econ-calendar connector

**Depends on:** M1-01 (surprise), M0-R-01 (`Fixture` / `FixtureEvent`)

**Context:** Wire a real CPI release through the *same* prediction core — the optional
live-validation behind the function.

**Files:** `src/fortuneteller/live/__init__.py`, `src/fortuneteller/live/sources.py`,
`src/fortuneteller/live/build.py`, `pyproject.toml` (add `httpx` — the M1 dep per
[tech-stack](tech-stack.md))

**Spec:**
- `sources.py`: fetch CPI `actual` from **FRED** and `consensus` from a **free econ calendar**
  (Trading Economics free tier / Investing.com, [mvp-architecture § data acquisition](mvp-architecture.md));
  small typed functions over `httpx`. API keys from `pydantic-settings` (`FT_FRED_API_KEY`), never
  hard-coded.
- `build.py`: `build_cpi_event(release_date) -> Fixture` — pull the release + the trailing history,
  compute `surprise` / `surprise_sd` via M1-01, set `scheduled=True`, `rate_regime`, and the five
  core `instruments`; return a `Fixture` that replays through the **identical** engine.
- **Network isolation:** nothing in `live/` is imported by `replay/`; the deterministic harness stays
  offline. Errors are legible: missing API key, network failure, or unknown event each raise a
  message naming the cause.

**Acceptance criteria:**
- [ ] with recorded/mocked HTTP, `build_cpi_event` for a known release yields the expected
      `FixtureEvent` (surprise sign + regime) and a five-instrument `Fixture`.
- [ ] `tests/test_live.py` runs with **no live network** (mocked transport); a missing API key
      surfaces a legible error.
- [ ] ruff + mypy strict pass; `replay/` has no import of `live/`.

**Out of scope:** yfinance / Stooq prices + abnormal returns (M2); APScheduler (M2); paid vendors;
non-CPI events.

## M1-07 — `predict` CLI subcommand (optional live-validation)

**Depends on:** M1-06, M1-04, M0-01 (the argparse CLI)

**Context:** The one-shot live command — fetch a real CPI release and emit the same resolved
`Warning` list as `replay`.

**Files:** `src/fortuneteller/__main__.py` (extend), `tests/test_predict_cli.py` (new, mocked
sources), `justfile` (add a `predict` recipe)

**Spec:**
- `fortuneteller predict --event "CPI / inflation surprise" --release-date <YYYY-MM-DD> [--json]`:
  build the event (M1-06) → run the prediction core (M1-04) → print `Warning`(s), human table by
  default or structured JSON with `--json`, mirroring `replay`'s output contract.
- Unknown `--event` (not in `event_types.csv`) → an explicit error pointing at the seed CSV;
  missing FRED key / network failure → a legible non-zero exit.

**Acceptance criteria:**
- [ ] `uv run fortuneteller --help` lists `predict`; a `tests/test_predict_cli.py` case with mocked
      sources runs a known release and asserts a resolved `Warning` list + exit 0.
- [ ] a `tests/test_predict_cli.py` case asserts a missing FRED key exits non-zero with a legible
      message; ruff + mypy strict pass.

**Out of scope:** alerting / delivery channels (M6); scheduling (M2); watch / batch modes.

---

### Execution summary

Implement M1-01 → M1-02 → M1-03 → M1-04 → M1-05 to enrich the deterministic core (surprise →
conditional resolution → resolved CPI fixtures), then M1-06 → M1-07 for the live path. After M1-05 is
green the prototype is **demoable offline**: `replay` turns the CPI fixture's conditional cells into
concrete, asserted directions, deterministically. After M1-07, the same logic runs over a live FRED +
econ-calendar CPI release as optional validation. M1 is done when `just check` is green and both the
`replay` and `predict` paths produce the resolved CPI warning. Calibration (M2), confidence (M3), and
detection (M4) build on this slice next.
