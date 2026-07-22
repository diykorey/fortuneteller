# M0-R Tickets — Replay Harness

> **Status: shipped.** M0-R-01 … 05 are implemented and merged; GitHub issues #40–#44 (label
> `M0-R`) are closed. Acceptance criteria below are ticked to match. Current build state:
> [Implementation Status](implementation-status.md).

> Written to be consumed by an LLM coding agent, same as [M0 Tickets](m0-tickets.md). Read the
> Shared Context once, then any ticket can be implemented in isolation. Every ticket states exact
> file paths, an explicit spec, and binary acceptance criteria.
>
> Design source: [Replay-harness spec](superpowers/specs/2026-06-22-replay-harness-fast-dev-loop-design.md).

## Shared Context (read once, applies to every M0-R ticket)

**Why.** M0-R is the **fast dev loop**: a deterministic, offline, agent-runnable replay of the
prediction core, so logic is built and verified against canned events instead of waiting for live
data. It folds into M0 and reframes M1's gate from a *real* CPI release to *episode replay*.

**What it wraps.** The deterministic middle of the pipeline only — stages 5–8 (surprise →
prediction → warning). A episode supplies an **already-detected, classified, entity-linked event**
plus its regime context; detection (stages 1–4) is out of scope (M4). At M0-R the prediction logic
is the *thinnest possible*: an `effect_size_seed` lookup → `Warning`, no calibration.

**Conventions.** Reuses the M0 package (`src/fortuneteller`), the M0-03 enums, and the seeded DuckDB
from M0-05/07. Canonical `event_type` keys and instrument **symbols** are exactly those in
`data/seed/event_types.csv` and `data/seed/instruments.csv` (e.g. `Major interstate war`,
`SPY / ES`). `mypy --strict` over `src`; line length 100; no network anywhere; episodes live in
`episodes/` (not under `src/`).

**Determinism rule (the property the loop rests on).** No `now()` / randomness in the core;
`as_of` comes from the episode's `t0`; warnings are ordered by the episode's instrument order; seed
data is committed. Same inputs → identical bytes.

**Conditional cells stay thin.** Non-conditional seed cells (e.g. war→Brent `up`) resolve to a
concrete direction. `conditional` cells (CPI, Fed, …) emit `direction: "conditional"` + the
standardized-surprise sign — turning that into a concrete up/down is **M1's** job.

**Definition of done for M0-R.**
1. `uv run fortuneteller replay episodes/war-oil-shock-2026.json --json` prints a `Warning` list; exit 0.
2. `uv run pytest tests/test_replay.py` passes — every episode matches its golden file and every `expect` holds.
3. Re-running `replay` twice yields byte-identical output.
4. `uv run ruff check` and `uv run mypy src` pass.

**Dependency order.** M0-R-01 → 02 → 03 → (04 alongside 02) → 05. Depends on M0-03, M0-05, M0-07
from the [M0 set](m0-tickets.md).

---

## M0-R-01 — Episode & Warning models

**Depends on:** M0-03 (reuses the `Direction` / `HalfLife` / `Confidence` enums)

**Context:** The typed contract for a replayable scenario and its output.

**Files:** `src/fortuneteller/replay/__init__.py`, `src/fortuneteller/replay/models.py`

**Spec:**
- `EpisodeEvent`: `event_type: str`, `t0: datetime`, `scheduled: bool`, `consensus: float | None = None`, `actual: float | None = None`, `surprise_sd: float | None = None`, `vix_t0: float | None = None`, `rate_regime: str | None = None`.
- `Episode`: `id: str`, `event: EpisodeEvent`, `instruments: list[str]`, `expect: dict[str, Direction] | None = None`.
- `Warning`: `instrument: str`, `direction: Direction`, `magnitude: str`, `half_life: HalfLife | None`, `confidence: Confidence`, `event_type: str`, `surprise_sign: Literal["above","below","unknown"]`, `as_of: datetime`, `disclaimer: str`.
- `model_config = ConfigDict(extra="forbid")`; reuse M0-03 enums (don't redefine).

**Acceptance criteria:**
- [x] models import; the example episode JSON parses; an unknown field raises `ValidationError`.
- [x] mypy strict passes.

**Out of scope:** the engine, any IO.

## M0-R-02 — `replay()` core (pure function)

**Depends on:** M0-R-01, M0-05 (`get_effect_size`), M0-07 (seeded data present)

**Context:** The deterministic engine — one episode in, a list of warnings out.

**Files:** `src/fortuneteller/replay/engine.py`

**Spec:**
- `replay(episode: Episode, con: DuckDBPyConnection | None = None) -> list[Warning]`.
- For each symbol in `episode.instruments`, look up the `effect_size_seed` cell for `(event.event_type, symbol)`:
  - **found, non-conditional** → `Warning` with the seed `direction`, `magnitude`, `half_life`, `confidence`.
  - **found, `conditional`** → `direction="conditional"` (no up/down resolution — that's M1).
  - **missing** → a "no edge" `Warning`: `direction="mixed"`, `magnitude="no edge vs market-implied"`, `confidence="low"` (never raise).
- `surprise_sign` = `"above"` if `surprise_sd > 0`, `"below"` if `< 0`, else `"unknown"`.
- `as_of = episode.event.t0`; output ordered by `episode.instruments`. No IO beyond the read-only DB; no clock; no randomness.

**Acceptance criteria:**
- [x] non-conditional cell → concrete direction; conditional cell → `"conditional"` + correct `surprise_sign`.
- [x] a missing cell yields a "no edge" `Warning`, not an exception.
- [x] `as_of` equals the episode `t0`; order matches `instruments`; two runs are byte-identical.
- [x] mypy strict passes.

**Out of scope:** conditional direction resolution (M1), calibration, confidence calibration.

## M0-R-03 — `replay` CLI subcommand

**Depends on:** M0-R-02, M0-01 (the argparse CLI)

**Context:** The agent's one-shot command.

**Files:** `src/fortuneteller/__main__.py` (extend)

**Spec:**
- `fortuneteller replay <episode.json> [--json]`: load + validate the episode, run `replay`, print a human table by default or structured JSON with `--json`.
- If `episode.expect` is present, check each listed instrument's resolved `direction`; on any mismatch, print the diffs and exit non-zero.
- Invalid/malformed episode → `ValidationError` naming the file + field; unknown `event_type` / instrument → an explicit error pointing at `event_types.csv` / `instruments.csv`.

**Acceptance criteria:**
- [x] `uv run fortuneteller replay episodes/war-oil-shock-2026.json --json` prints a `Warning` list; exit 0.
- [x] an `expect` mismatch exits non-zero, listing instrument / expected / actual.
- [x] mypy strict passes.

**Out of scope:** watch mode, batch replay of a directory.

## M0-R-04 — Synthetic episodes + golden files

**Depends on:** M0-R-01 (schema), M0-R-02 (to generate the goldens)

**Context:** The day-one canned scenarios the loop runs against.

**Files:** `episodes/*.json`, `episodes/*.golden.json`

**Spec:** ~5 episodes, each with a committed `<id>.golden.json` equal to `replay()` output:
- `war-oil-shock-2026` — Major interstate war → `BRN` up, `GC / XAU` up, `SPY / ES` down (non-conditional; `expect` set).
- `depeg-2026` — Stablecoin / DeFi depeg → `BTC` down, `USDC` down (non-conditional; `expect` set).
- `terror-shock-2026` — Geopolitical escalation / terror → `VIX` up (non-conditional; `expect` set).
- `cpi-hot-2026-03` — CPI / inflation surprise, `surprise_sd > 0` → `SPY / ES`, `GC / XAU`, `BUND / FGBL`; golden shows `direction="conditional"` + `surprise_sign="above"` (no `expect` at M0-R; added at M1).
- `no-edge-2026` — an `(event_type × instrument)` pair with no seed cell → a "no edge" `Warning`.

**Acceptance criteria:**
- [x] each episode validates against `Episode`; every `event_type` / instrument key exists in the seed CSVs.
- [x] each episode has a matching `<id>.golden.json` equal to `replay()` output.

**Out of scope:** recorded real events (Phase 2 / M2).

## M0-R-05 — Golden + intent tests

**Depends on:** M0-R-02, M0-R-04, M0-08 (the seeded temp-DB fixture pattern)

**Context:** Encode the fast loop as automated, deterministic tests.

**Files:** `tests/test_replay.py` (reuse the seeded-DB `conftest` fixture)

**Spec:**
- Parametrized over `episodes/*.json`: assert `replay(episode)` serializes byte-exact to `episodes/<id>.golden.json`.
- Intent test: for each instrument in `episode.expect`, assert `Warning.direction == expected`.
- A `--update-golden` pytest option (or `FT_UPDATE_GOLDEN=1`) rewrites the golden files.

**Acceptance criteria:**
- [x] `uv run pytest tests/test_replay.py` is green — all goldens match and all `expect` directions hold.
- [x] `pytest --update-golden` regenerates goldens; a wrong-*direction* change still fails the intent test (can't be silently blessed).
- [x] tests use the seeded temp DB only (never `data/fortuneteller.duckdb`).

**Out of scope:** backtest scoring / calibration metrics (M3).

---

### Execution summary

Implement M0-R-01 → 02 → 03 → 04 → 05 (04 can proceed alongside 02). After M0-R-05 is green, the
deterministic fast loop exists: an agent edits prediction logic, runs `uv run pytest` (or
`fortuneteller replay <episode>`), and reads a byte-level diff — no live data, no waiting. This is
the substrate M1–M5 develop against.
