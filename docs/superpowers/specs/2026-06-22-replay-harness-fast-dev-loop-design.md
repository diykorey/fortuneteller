# Design — Replay harness for a superfast dev loop

**Date:** 2026-06-22
**Status:** Approved (brainstorming) — ready for implementation plan

**Terminology:** this spec's *episode* is now the **episode** — renamed to avoid the pytest
collision; see CLAUDE.md.

## Context & problem

The FortuneTeller docs (mirrored from Notion) describe *what* to build (roadmap M0–M7, tech stack,
M0 tickets) and the tech stack is already iteration-friendly (uv, embedded DuckDB, no ORM,
scripts-before-services, deferred deps). What they do **not** provide is a fast feedback loop for
building the prediction logic.

The sharpest friction: **M1's exit criterion is "a *real* CPI release produces a
directionally-correct warning."** CPI prints monthly — so the core prediction logic has a
once-a-month feedback cycle, the opposite of "superfast." Nothing in the docs lets a developer (or
an LLM coding agent) run the pipeline against a canned event on demand.

This spec adds a **deterministic, offline, agent-runnable replay harness as the first runnable
thing**, and reframes the roadmap so every milestone is built against an instant loop.

## Decisions (from brainstorming)

- **Target:** the dev feedback loop (changes roadmap/tickets, not just prose).
- **Primary consumer:** an LLM coding agent — optimize for deterministic one-shot commands,
  structured/asserted output, and golden-file tests.
- **Episodes:** synthetic now, recorded later (phased). Phase 1 ships hand-authored episodes;
  Phase 2 (designed, not built here) backfills recorded real events through the same schema.
- **Approach:** Harness-first — fold the harness into M0, before the prediction logic matures, and
  reframe M1's gate to episode-replay.

## Goals / Non-goals

**Goals**
- A `fortuneteller replay <episode>` command that runs a canned event through the deterministic
  core and emits a structured, assertable `Warning`.
- Golden-file + intent tests that run sub-second in CI, giving an agent a tight
  build → verify → read-diff cycle with no live data or credentials.
- Roadmap/ticket amendments that make the fast loop available from M0 and remove the real-CPI dev
  gate.

**Non-goals (stay in their later milestones)**
- Calibration (M2/M3), detection/corroboration (M4), live feeds (M1+), the `record` implementation
  and backtest scoring (Phase 2 / M2–M3), any web service.

## Architecture

The harness wraps the **deterministic middle of the pipeline only**. From the
[architecture sketch](../../architecture.md)'s 10 stages, detection (stages 1–4: ingest, classify,
entity-link, corroborate) is noisy and non-deterministic — that is M4. A episode supplies an
**already-detected, classified, entity-linked event** plus its price/regime context, so replay
starts at **stage 5 (surprise estimation)** and runs through **stage 8 (the warning)**.

The harness ships with the *thinnest possible* prediction function — an `effect_size_seed` lookup →
`Warning`, no calibration — so there is something real to replay on day one. M1 then enriches the
logic (proper surprise handling, instrument selection) **test-first** against the harness instead
of building it blind. The harness becomes the spine M2 (calibration), M3 (confidence), and M5
(coverage) develop against — each adds episodes and tightens golden assertions.

## Components & interfaces

### Episode (`episodes/<id>.json`, committed)

One JSON file per replayable scenario. Carries a pre-detected event plus the context the core needs.
The primary example uses a **non-conditional** event (a war headline) — its instrument directions
are fixed in the seed, so M0-R's thin logic resolves them fully and deterministically:

```json
{
  "id": "war-oil-shock-2026",
  "event": {
    "event_type": "Major interstate war",
    "t0": "2026-04-02T06:00:00Z",
    "scheduled": false,
    "surprise_sd": null,
    "vix_t0": 31.0, "rate_regime": "on-hold"
  },
  "instruments": ["BRN", "GC / XAU", "SPY / ES"],
  "expect": { "BRN": "up", "GC / XAU": "up", "SPY / ES": "down" }
}
```

- `surprise_sd` is supplied directly for scheduled-data episodes (synthetic episodes need no price
  history); it is `null` for unscheduled events. `consensus` / `actual` are optional, for display.
- `instruments` scopes which effect-size cells to predict.
- `expect` (optional) is a coarse, human-readable intent check (direction per instrument), distinct
  from the byte-exact golden file. For **conditional** cells (see below) `expect` directions are
  added at M1, once resolution exists.
- `event_type` and instrument keys are the **same canonical keys** as
  [`event_types.csv`](../../../data/seed/event_types.csv) /
  [`instruments.csv`](../../../data/seed/instruments.csv), so the lookup joins cleanly.

### `replay(episode) -> list[Warning]` (pure function)

Validate episode (Pydantic) → for each instrument, look up the `effect_size_seed` cell → assemble a
`Warning`. No I/O beyond the seeded, read-only DB; no clock; no randomness.

**Conditional cells stay thin at M0-R.** Non-conditional seed cells (e.g. war→Brent `up`,
terror→VIX `up`, depeg→BTC `down`) resolve to a concrete direction directly. For `conditional`
cells (CPI, Fed, OPEC, earnings, M&A) M0-R emits `direction: "conditional"` together with the
standardized-surprise sign (`surprise_sign`: `above` / `below` / `unknown`) — it does **not** invent
an up/down. Turning `conditional` + surprise + regime into a concrete direction is M1's enrichment,
added test-first against these same episodes (M1 then fills in their `expect` directions).

### CLI: `fortuneteller replay <episode.json> [--json]`

Prints warnings (human table by default, structured JSON with `--json`). Exits non-zero if the
episode's `expect` block fails. This is the agent's one-shot command.

### Output — `Warning` (structured, assertable)

```json
{
  "instrument": "BRN", "direction": "up",
  "magnitude": "3-10%", "half_life": "hours_days",
  "confidence": "high", "event_type": "Major interstate war",
  "surprise_sign": "unknown",
  "as_of": "2026-04-02T06:00:00Z",
  "disclaimer": "Not investment advice."
}
```

`direction` is `"conditional"` (not a concrete up/down) for conditional cells at M0-R; `surprise_sign`
carries the standardized-surprise direction. `as_of` is set from the episode's `t0`, **never
`now()`** — this is what keeps replay byte-for-byte deterministic and golden-comparable.

## Data flow

```
episodes/<id>.json
  -> load + validate (Pydantic Episode)
  -> for each instrument:
       effect_size_seed lookup (seeded DuckDB)
       non-conditional cell -> concrete direction; conditional cell -> "conditional" + surprise_sign
       -> assemble Warning (as_of = episode.t0)
  -> emit list[Warning]  (table | --json)
golden test: replay(episode) == episodes/<id>.golden.json   (byte-exact)
intent test: each Warning.direction matches episode.expect[instrument]
```

## Testing strategy (primary consumer = an agent)

- **Golden-file tests.** Each episode has a committed `episodes/<id>.golden.json` with the exact
  `replay(...)` output. One parametrized pytest iterates every episode and asserts equality. When
  logic legitimately changes output, `pytest --update-golden` (or `FT_UPDATE_GOLDEN=1`) rewrites
  the snapshots; the agent regenerates, then reads the git diff to confirm intent.
- **Intent assertions.** The episode's optional `expect` block (coarse direction per instrument) is
  checked separately, so a wrong-direction regression cannot be silently blessed by
  `--update-golden`.
- **Speed.** Pure functions over a session-scoped, seeded in-memory DuckDB → sub-second suite; CI
  runs it on every push.
- **Day-one episode set (~5):** interstate-war headline, stablecoin depeg, and a geopolitical-terror
  shock (all **non-conditional** → fully resolved + asserted at M0-R); a hot-CPI episode
  (**conditional** → golden shows `conditional` + `surprise_sign` at M0-R, gets resolved-direction
  `expect` at M1); and one "no edge" case (event×instrument with no seed cell) to exercise the empty
  path.

## Error handling (every failure is legible)

- Missing effect-size cell → emit a `"no edge vs market-implied"` warning, **not** a crash (matches
  the Detection spec's B6 honesty rule).
- Invalid/malformed episode → Pydantic `ValidationError` naming the file + field.
- Unknown `event_type` / instrument (not in seed) → explicit error naming the bad key and pointing
  at `event_types.csv` / `instruments.csv`.
- `expect` mismatch → non-zero exit listing instrument, expected vs actual direction.

## Determinism guarantees

No `now()` / random in the core; `as_of` comes from episode `t0`; warnings ordered by the episode's
instrument order; seed data is committed. Same inputs → identical bytes, always. This is the
property the whole loop rests on.

## Roadmap & ticket amendments (the deliverable)

### New ticket group — M0-R (Replay & episodes), added to `docs/m0-tickets.md`

Same format as existing tickets (exact file paths + binary acceptance criteria). Depends on
M0-03/04/05/07; slots after M0-07, with/before M0-08.

- **M0-R-01 — Episode & Warning models** (`src/fortuneteller/replay/models.py`): Pydantic
  `Episode`, `EpisodeEvent`, `Warning`; `extra="forbid"`.
- **M0-R-02 — `replay()` core** (`src/fortuneteller/replay/engine.py`): the pure function;
  effect-size lookup; concrete direction for non-conditional cells, `"conditional"` + `surprise_sign`
  for conditional cells (no up/down resolution here — that is M1); the "no edge" path.
- **M0-R-03 — `replay` CLI subcommand** (extend `src/fortuneteller/__main__.py`): `--json`, exit
  codes, `expect` checks.
- **M0-R-04 — Synthetic episodes + goldens** (`episodes/*.json` + `episodes/*.golden.json`): the
  ~5 day-one scenarios above.
- **M0-R-05 — Golden + intent tests** (`tests/test_replay.py`, seeded-DB conftest fixture) and the
  `--update-golden` switch.

### Edits to existing docs

- `docs/roadmap.md` — rewrite M1's "Done when" to the episode-replay criterion; add a one-line
  "fast loop from M0" note; add M0-R to M0's build list.
- `docs/m0-tickets.md` — add the M0-R group; extend the Definition-of-Done to include
  `uv run fortuneteller replay <episode>` and green golden tests.
- New `docs/dev-loop.md` — how the replay loop works and how an agent uses it (the "superfast
  iteration" guide); link it from `docs/README.md`.

## Phase 2 hook (designed, not built here)

A future `fortuneteller record` path captures **real historical events** into the *same* `Episode`
schema (real consensus/actual + realized prices), so recorded events replay through the identical
harness — and that recorded set seeds the M2 calibration dataset / backtest harness. Documented as a
forward pointer in `dev-loop.md` and M2, so the simple harness grows into the backtest harness
exactly when M2/M3 need it.

## Scope guard (YAGNI)

This spec is strictly the deterministic synthetic fast loop + the roadmap reframe. No calibration,
detection, live feeds, `record` implementation, or backtest scoring.

## Verification

- `uv run fortuneteller replay episodes/war-oil-shock-2026.json --json` prints a `Warning` list with
  `BRN` direction `up`, `GC / XAU` `up`, `SPY / ES` `down`; exit code 0.
- `uv run pytest tests/test_replay.py` passes: every episode matches its golden file and every
  `expect` direction holds.
- Re-running `replay` twice yields byte-identical output (determinism).
- `uv run ruff check` and `uv run mypy src` pass (the harness lives under `src/`, episodes do not).
