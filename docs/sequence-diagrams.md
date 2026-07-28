# Sequence Diagrams & Use Cases

"What happens" in FortuneTeller, call-by-call over time, complementing the prose in
[implementation-status.md](implementation-status.md) and the data-flow sketch in
[architecture.md](architecture.md).

**Status legend** (matches [implementation-status.md](implementation-status.md)): ✅ built & merged
(M0 + M0-R + M1 offline core) · 🧭 planned, not built (M1 live path, M1-06/07) · 🌟 north-star
(eventual; deliberately not scaffolded).

## Actors & use cases

| Actor | Use case (goal) | Entry point | Realized by | Status |
| --- | --- | --- | --- | --- |
| Operator | Create the local DuckDB store | `fortuneteller init` | *init* | ✅ |
| Operator | Load reference/seed data | `fortuneteller seed` | *seed* | ✅ |
| Operator | Inspect a sample effect-size edge | `fortuneteller query-demo` | *query-demo* | ✅ |
| Analyst / operator | Predict an event's market impact offline | `fortuneteller replay episodes/<id>.json` | *replay* | ✅ |
| Coding agent / dev | Change prediction logic and see exactly what moved | `uv run pytest` / `--update-golden` | *golden dev loop* | ✅ |
| Analyst | Validate the core against a real CPI release | `fortuneteller predict --event … --release-date …` | *predict (live)* | 🧭 M1-06/07 |
| Reader / subscriber | Receive a calibrated warning | delivery (stage 9) | *north-star* | 🌟 |
| Calibration job | Learn from realized outcomes, re-estimate the matrix | batch job | *north-star* feedback loop | 🌟 |

## ✅ `init`

Creates the DuckDB store and every table.

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as __main__
    participant db
    participant DuckDB
    Operator->>CLI: fortuneteller init
    CLI->>db: init_db()
    db->>db: get_connection()
    db->>DuckDB: mkdir db_path.parent + connect(settings.db_path)
    db->>DuckDB: execute(schema.sql)  %% idempotent DDL, 9 tables
    CLI-->>Operator: print "init: created {db_path}" (exit 0)
```

## ✅ `seed`

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as __main__
    participant seed
    participant db
    participant Polars
    participant Pydantic
    participant DuckDB
    Operator->>CLI: fortuneteller seed
    CLI->>db: get_connection()
    db->>DuckDB: mkdir db_path.parent + connect(settings.db_path)
    CLI->>db: init_db(con)
    db->>DuckDB: execute(schema.sql)  %% idempotent DDL, 9 tables
    CLI->>seed: load_all(con)
    loop 6 SEED_TABLES (event_types, instruments, effect_size_seed, surprise_response, news_sources, countries)
        seed->>Polars: read_csv(path)
        loop each data row
            seed->>Pydantic: Model.model_validate(row)
            Note right of Pydantic: bad row -> ValueError naming file:line
        end
        seed->>db: insert_models(table, rows, replace=True)
        db->>DuckDB: INSERT OR REPLACE  %% idempotent by primary key
    end
    seed-->>CLI: {table: count}
    CLI-->>Operator: print "table: count" per table (exit 0)
```

## ✅ `query-demo`

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as __main__
    participant seed
    participant db
    participant DuckDB
    Operator->>CLI: fortuneteller query-demo
    CLI->>db: get_connection()
    CLI->>db: init_db(con)
    CLI->>seed: query_demo(con)
    seed->>db: get_effect_size("CPI / inflation surprise", "SPY / ES", con)
    db->>DuckDB: SELECT * FROM effect_size_seed WHERE event_type = ? AND instrument = ?
    alt row found
        DuckDB-->>seed: EffectSizeSeed row
    else no row for that pair
        seed->>db: first_effect_size(con)
        db->>DuckDB: SELECT * FROM effect_size_seed LIMIT 1
        DuckDB-->>seed: EffectSizeSeed row (or none)
    end
    seed-->>CLI: EffectSizeSeed | None
    alt row is None
        CLI-->>Operator: print "query-demo: no effect-size rows (run `fortuneteller seed` first)" (exit 1)
    else row present
        CLI-->>Operator: print "{event_type} x {instrument}: direction=… magnitude=… confidence=…" (exit 0)
    end
```

## ✅ `replay <episode>` — pipeline stages 5–8

The headline diagram: an already-detected event goes in, resolved `Warning`s come out, deterministically.

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as __main__
    participant seed
    participant engine
    participant surprise
    participant direction
    participant db
    participant DuckDB
    Operator->>CLI: fortuneteller replay episodes/<id>.json [--json]
    CLI->>db: get_connection()
    CLI->>db: init_db(con)
    CLI->>seed: load_all(con)  %% refresh from committed CSVs on every run
    CLI->>engine: load_episode(path)
    engine->>engine: Episode.model_validate_json(text)  %% extra="forbid"
    alt invalid episode JSON
        engine-->>CLI: ValueError("invalid episode <name>: …")
        CLI-->>Operator: stderr + exit 1
    end
    CLI->>engine: validate_keys(episode, con)
    engine->>db: get_event_type(episode.event.event_type, con)
    engine->>db: get_instrument(symbol, con)  %% per instrument
    alt unknown event_type or instrument
        engine-->>CLI: ValueError naming the seed CSV
        CLI-->>Operator: stderr + exit 1
    end
    CLI->>engine: replay(episode, con)
    engine->>surprise: surprise_sign(event.surprise_sd)
    surprise-->>engine: "above" | "below" | "unknown"
    loop episode.instruments
        engine->>db: get_effect_size(event_type, symbol, con)
        db->>DuckDB: SELECT * FROM effect_size_seed WHERE event_type = ? AND instrument = ?
        alt cell missing
            engine->>engine: Warning(direction=mixed, magnitude="no edge vs market-implied", half_life=None, confidence=low)
        else cell concrete (e.g. war -> Brent up)
            engine->>engine: Warning(direction=cell.direction, magnitude=cell.typical_magnitude, ...)
        else cell conditional
            engine->>direction: resolve_direction(event_type, symbol, sign, rate_regime, con)
            direction->>db: get_surprise_response(event_type, instrument, con)
            db->>DuckDB: SELECT * FROM surprise_response WHERE event_type = ? AND instrument = ?
            Note right of direction: above resolves to hot_direction, below to its inverse,<br/>with a good-news-is-bad-news flip when regime_sensitive is yes<br/>and rate_regime is easing-hungry or cut-hungry, else mixed
            direction-->>engine: Direction
            Note right of engine: mixed plus sign unknown plus surprise_sd is None<br/>keeps the M0-R conditional placeholder (unscheduled, nothing to resolve)
            engine->>engine: Warning(direction=resolved, ...)
        end
        engine->>engine: set as_of = event.t0, disclaimer (stage 8)
    end
    engine-->>CLI: list[Warning]
    alt --json
        CLI-->>Operator: warnings_to_json(warnings)
    else
        CLI-->>Operator: warnings_to_table(warnings)
    end
    opt episode.expect is set
        CLI->>CLI: compare each direction vs expect
        alt any mismatch
            CLI-->>Operator: stderr "expect mismatch: …" + exit 1
        end
    end
```

Determinism guarantee: `as_of` comes from `event.t0`, never `now()`; instrument order follows
`episode.instruments`; seed data is committed; there is no randomness — the same inputs always
serialize to identical bytes.

## ✅ Golden dev loop — how a coding agent changes logic safely

```mermaid
sequenceDiagram
    actor Dev as Dev / coding agent
    participant pytest
    participant seeded_con as seeded_con fixture
    participant engine
    participant golden as episodes/*.golden.json
    participant git
    Dev->>pytest: uv run pytest
    loop every episodes/*.json (excluding *.golden.json)
        pytest->>seeded_con: build in-memory DuckDB, init_db + seed.load_all
        pytest->>engine: replay(episode, con=seeded_con)
        engine-->>pytest: warnings
        pytest->>pytest: warnings_to_json(warnings)
        alt --update-golden / FT_UPDATE_GOLDEN=1
            pytest->>golden: write_text(produced)
        else
            pytest->>golden: read_text()
            pytest->>pytest: assert produced == golden (byte-exact)
        end
        pytest->>pytest: assert episode.expect directions hold (intent test)
    end
    Dev->>Dev: edit prediction logic
    Dev->>pytest: uv run pytest --update-golden
    pytest->>golden: rewrite affected goldens
    Dev->>git: git diff
    Dev->>Dev: read the diff, confirm the change was intended
```

This is the loop CLAUDE.md calls "the spine of iteration" — offline and deterministic, no waiting
for live data.

## 🧭 `predict --event … --release-date …` — the free live path (NOT built)

Spec only, from [m1-tickets.md](m1-tickets.md)
(issues [#29](https://github.com/diykorey/fortuneteller/issues/29) /
[#30](https://github.com/diykorey/fortuneteller/issues/30), both open).

```mermaid
sequenceDiagram
    actor Analyst
    participant CLI as __main__ 🧭
    participant build as live/build.py 🧭
    participant sources as live/sources.py 🧭
    participant FRED as FRED API 🧭
    participant Calendar as econ calendar 🧭
    participant surprise
    participant engine
    Analyst->>CLI: fortuneteller predict --event CPI --release-date … 🧭
    CLI->>build: build_cpi_event(release_date) 🧭
    build->>sources: fetch actual (FRED, httpx, FT_FRED_API_KEY) 🧭
    sources->>FRED: GET release value 🧭
    build->>sources: fetch consensus (free econ calendar) + trailing history 🧭
    sources->>Calendar: GET consensus + history 🧭
    build->>surprise: compute_surprise(consensus, actual) 🧭
    build->>surprise: standardize(surprise, history) 🧭
    build->>build: assemble Episode (scheduled=True, rate_regime, 5 core instruments) 🧭
    build-->>CLI: Episode 🧭
    CLI->>engine: replay(episode)  %% identical deterministic engine as offline replay 🧭
    engine-->>CLI: list[Warning] 🧭
    CLI-->>Analyst: same output contract as replay 🧭
    Note right of build: nothing in live/ is imported by replay/ (hard isolation).<br/>Missing key or network failure exits non-zero with a legible message. 🧭
```

## 🌟 North-star — the 10-stage pipeline + calibration loop

Stage names taken verbatim from the flowchart in
[architecture.md](architecture.md#1-data-flow).

```mermaid
sequenceDiagram
    participant Sources as Ranked news stack 🌟
    participant Ingest as 1 Ingestion 🌟
    participant Classify as 2 Classify 🌟
    participant EntityLink as 3 Entity-link 🌟
    participant Corroborate as 4 Corroborate 🌟
    participant Surprise as 5 Surprise 🌟
    participant Predict as 6 Prediction 🌟
    participant Confidence as 7 Confidence + calibration 🌟
    participant Severity as 8 Severity/dedup 🌟
    participant Warn as 9 Warning delivery 🌟
    participant Reader 🌟
    participant Outcome as 10 Outcome capture 🌟
    participant CalDS as Calibration dataset 🌟
    participant CalJob as Calibration job 🌟
    participant ESM as Effect-size matrix 🌟
    Sources->>Ingest: raw items 🌟
    Ingest->>Classify: normalized, deduped, t0-stamped 🌟
    Classify->>EntityLink: event type + polarity 🌟
    EntityLink->>Corroborate: entities / instruments / countries 🌟
    Corroborate->>Surprise: corroborated, source-tiered event 🌟
    Surprise->>Predict: actual - consensus 🌟
    Predict->>Confidence: effect-size x regime lookup 🌟
    Note right of Confidence: options-implied / prediction-market benchmark feeds this stage 🌟
    Confidence->>Severity: probability + CI 🌟
    Severity->>Warn: deduped, anti-fatigue-filtered warning 🌟
    Warn->>Reader: push / email / web 🌟
    Warn->>Outcome: realized-return tracking begins 🌟
    Outcome->>CalDS: realized returns 🌟
    CalDS->>CalJob: batch re-estimation 🌟
    CalJob->>ESM: updated mag_per_sd / hit_rate / n_obs 🌟
    ESM->>Predict: refreshed effect sizes 🌟
```

This is what stages 5–8 of `replay` above grow into; the MVP runs them as pure functions in one
process (mapping table in [mvp-architecture.md](mvp-architecture.md#the-core-idea)). Detection
(1–4) is M4; calibration (9–10) is M2/M3.
