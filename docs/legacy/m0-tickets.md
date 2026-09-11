# M0 Tickets — Scaffold & Seed

> Written to be consumed by an LLM coding agent. Read the Shared Context once, then any ticket can
> be implemented in isolation. Every ticket states exact file paths, an explicit spec, and binary
> acceptance criteria.

## Shared Context (read once, applies to every ticket)

**Project.** FortuneTeller predicts market reactions to social/political/climate/macro events and
warns readers. M0 is scaffold + seed only — no feeds, no modeling, no web server. Goal: a repo that
clones-and-runs and has the reference data loaded into an embedded DB.

**Tech stack (M0 only).** Python 3.12+, uv (env/deps), ruff (lint+format), mypy (types), pytest
(tests), pydantic v2 + pydantic-settings (models/config), polars (CSV/Parquet I/O), duckdb
(embedded store). NO ORM — a thin SQL helper over DuckDB with schema in schema.sql.

**Repo layout (target).**

```
fortuneteller/
  pyproject.toml
  README.md
  .gitignore
  schema.sql
  data/seed/                # committed seed CSVs
  src/fortuneteller/
    __init__.py
    config.py
    models.py
    db.py
    seed.py
    __main__.py
  tests/
    conftest.py
    test_smoke.py
  .github/workflows/ci.yml       # CI (day one)
```

**Conventions.** Package name fortuneteller, src-layout. All public functions typed; `mypy --strict`
must pass. Line length 100. No network calls in src/ (only in scripts/). DB path from config,
default `data/fortuneteller.duckdb`. Seed CSV dir from config, default `data/seed/`.

**Definition of done for M0.**

1. `uv run fortuneteller init` creates the DuckDB file with all tables.
2. `uv run fortuneteller seed` loads every `data/seed/*.csv` into its table.
3. `uv run fortuneteller query-demo` prints a sample effect-size lookup row.
4. `uv run ruff check`, `uv run mypy src`, and `uv run pytest` all pass.
5. `just check` runs that same gate locally, and CI (`.github/workflows/ci.yml`) runs it on every push.

**Dependency order.** M0-01 → 02 → 03 → 04 → 05 → (06 with 07) → 07 → 08 → 09. M0-09 (CI) is
required and runs from the first push.

---

## M0-01 — Project skeleton & tooling

**Depends on:** none

**Context:** Stand up the repo so uv manages everything and lint/type/test commands exist.

**Files:** `pyproject.toml`, `.gitignore`, `README.md`, `justfile`,
`src/fortuneteller/__init__.py`, `src/fortuneteller/__main__.py`

**Spec:**

- pyproject.toml: build-system + project metadata; `requires-python = ">=3.12"`; deps:
  pydantic>=2, pydantic-settings, polars, duckdb. Dev deps: ruff, mypy, pytest, pytest-cov.
  Configure `[tool.ruff]` (line-length 100, target py312) and `[tool.mypy]` (strict = true,
  files = ["src"]).
- CLI: `__main__.py` exposes subcommands init, seed, query-demo (argparse; no extra deps).
  init → db.init_db(); seed → seed.load_all(); query-demo → demo lookup + print. Wire
  `[project.scripts]` `fortuneteller = "fortuneteller.__main__:main"`.
- .gitignore: `.venv/`, `__pycache__/`, `*.duckdb`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`.
- README.md: quickstart (uv sync, uv run fortuneteller init, seed, query-demo).
- justfile: recipes `setup`, `test`, `lint`, `fmt`, `typecheck`, `check` (lint+type+test), `init`,
  `seed`, `replay <fixture>` — the canonical command surface so commands aren't
  re-derived each session.

**Acceptance criteria:**

- [ ] `uv sync` resolves and installs.
- [ ] `uv run fortuneteller --help` lists init, seed, query-demo.
- [ ] `uv run ruff check` and `uv run mypy src` pass on the skeleton.
- [ ] `just --list` shows the recipes; `just check` runs lint + typecheck + test.

**Out of scope:** any feed/modeling deps.

## M0-02 — Configuration module

**Depends on:** M0-01

**Context:** Central typed config so paths aren't hard-coded.

**Files:** `src/fortuneteller/config.py`

**Spec:**

- `class Settings(BaseSettings)` with: `db_path: Path = Path("data/fortuneteller.duckdb")`,
  `seed_dir: Path = Path("data/seed")`, `schema_path: Path = Path("schema.sql")`.
  `model_config = SettingsConfigDict(env_prefix="FT_", env_file=".env")`.
- Module-level `settings = Settings()` singleton.

**Acceptance criteria:**

- [ ] `from fortuneteller.config import settings` works; overridable via `FT_DB_PATH`.
- [ ] mypy strict passes.

**Out of scope:** secrets, API keys.

## M0-03 — Domain models & enums

**Depends on:** M0-01

**Context:** The typed domain layer. These Pydantic models are the readability/safety backbone and
define table shapes.

**Enums (str-Enums):**

- Polarity: positive | negative | both
- Direction: up | down | mixed | conditional
- AssetClass: equity_index | sector_etf | single_stock | rates_bond | fx | commodity | crypto | volatility | credit_cds | prediction | carbon | freight | insurance_linked
- Region: us | europe | asia | em | global
- HalfLife: seconds_minutes | minutes_hours | hours_days | days_weeks | weeks_plus
- Confidence: high | medium | low

**Files:** `src/fortuneteller/models.py`

**Models (Pydantic v2 BaseModel):**

- EventType: event_type: str, tier: int (1-8), polarity: Polarity
- Instrument: symbol: str, name: str, asset_class: AssetClass, region: Region, primary_venue: str | None = None, notes: str | None = None
- EffectSizeSeed: event_type: str, instrument: str, direction: Direction, typical_magnitude: str, reaction_half_life: HalfLife | None = None, direction_confidence: Confidence, hit_rate_est: str | None = None, surprise_dependent: str, basis: str | None = None
- NewsSource: rank: int, source: str, type: str, domains_covered: str, speed: str, reliability: str, api_access: str, cost: str
- Country: rank: int, country: str, gdp_2026e: str, platforms_in_list: str | None = None, coverage_gap: str | None = None, primary_news_source: str | None = None
- EventInstance (fact, empty in M0): event_id: int, event_type: str, event_ts: datetime, country: str | None, detail: str | None, scheduled: bool, consensus: float | None, actual: float | None, surprise: float | None, surprise_sd: float | None, surprise_source: str | None, priced_in_prior: float | None, vix_t0: float | None, rate_regime: str | None, quality: str
- Observation (fact, empty in M0): obs_id: int, event_id: int, instrument: str, px_t0: float | None, ret_unit: str | None, ret_5m: float | None, ret_1h: float | None, ret_1d: float | None, ret_1w: float | None, abn_ret_1d: float | None, car: float | None, peak_move: float | None, half_life_min: float | None, realized_dir: str | None, data_source: str | None, quality: str | None
- Prediction (output shape, not produced in M0): event_type: str, instrument: str, direction: Direction, expected_magnitude: str, half_life: HalfLife | None, probability: float | None, magnitude_low: float | None, magnitude_high: float | None, regime: str | None, as_of: datetime
- `model_config = ConfigDict(extra="forbid")`; enums compare by value.

**Acceptance criteria:**

- [ ] All models import; valid data constructs; invalid enum raises ValidationError.
- [ ] mypy strict passes.

**Out of scope:** persistence logic (M0-05).

## M0-04 — Database schema (DDL)

**Depends on:** M0-03 (field parity)

**Context:** The DuckDB spine, in plain SQL so the later Postgres migration is cheap.

**Files:** `schema.sql`

**Spec:** `CREATE TABLE IF NOT EXISTS`, columns matching M0-03 exactly:

```sql
CREATE TABLE IF NOT EXISTS event_types (event_type TEXT PRIMARY KEY, tier SMALLINT, polarity TEXT);
CREATE TABLE IF NOT EXISTS instruments (symbol TEXT PRIMARY KEY, name TEXT, asset_class TEXT, region TEXT, primary_venue TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS effect_size_seed (event_type TEXT, instrument TEXT, direction TEXT, typical_magnitude TEXT, reaction_half_life TEXT, direction_confidence TEXT, hit_rate_est TEXT, surprise_dependent TEXT, basis TEXT, PRIMARY KEY(event_type, instrument));
CREATE TABLE IF NOT EXISTS news_sources (rank INTEGER, source TEXT PRIMARY KEY, type TEXT, domains_covered TEXT, speed TEXT, reliability TEXT, api_access TEXT, cost TEXT);
CREATE TABLE IF NOT EXISTS countries (rank INTEGER, country TEXT PRIMARY KEY, gdp_2026e TEXT, platforms_in_list TEXT, coverage_gap TEXT, primary_news_source TEXT);
CREATE TABLE IF NOT EXISTS event_instances (event_id BIGINT PRIMARY KEY, event_type TEXT, event_ts TIMESTAMP, country TEXT, detail TEXT, scheduled BOOLEAN, consensus DOUBLE, actual DOUBLE, surprise DOUBLE, surprise_sd DOUBLE, surprise_source TEXT, priced_in_prior DOUBLE, vix_t0 DOUBLE, rate_regime TEXT, quality TEXT);
CREATE TABLE IF NOT EXISTS observations (obs_id BIGINT PRIMARY KEY, event_id BIGINT REFERENCES event_instances(event_id), instrument TEXT, px_t0 DOUBLE, ret_unit TEXT, ret_5m DOUBLE, ret_1h DOUBLE, ret_1d DOUBLE, ret_1w DOUBLE, abn_ret_1d DOUBLE, car DOUBLE, peak_move DOUBLE, half_life_min DOUBLE, realized_dir TEXT, data_source TEXT, quality TEXT);
CREATE TABLE IF NOT EXISTS effect_size_matrix (event_type TEXT, instrument TEXT, direction TEXT, mag_per_sd DOUBLE, mag_ci_low DOUBLE, mag_ci_high DOUBLE, median_half_life TEXT, hit_rate DOUBLE, n_obs INTEGER, surprise_dep TEXT, last_calibrated TIMESTAMP, PRIMARY KEY(event_type, instrument));
```

**Acceptance criteria:**

- [ ] Running the file against a fresh DuckDB connection creates all 8 tables with no error.
- [ ] Column names/types match the M0-03 models 1:1 for the seed tables.

**Out of scope:** indexes, views.

## M0-05 — Database helper (thin SQL layer, no ORM)

**Depends on:** M0-02, M0-03, M0-04

**Context:** One module owns the connection and typed access; everything else calls it.

**Files:** `src/fortuneteller/db.py`

**Spec:**

- `get_connection() -> duckdb.DuckDBPyConnection` — opens settings.db_path (create parent dirs).
- `init_db() -> None` — opens connection, executes settings.schema_path contents.
- `insert_models(table: str, rows: Sequence[BaseModel]) -> int` — generic insert (Polars DataFrame
  registration or executemany); returns count.
- Typed query helpers returning Pydantic objects: `get_instrument(symbol) -> Instrument | None`;
  `get_effect_size(event_type, instrument) -> EffectSizeSeed | None`; `count_rows(table) -> int`.
- All functions accept an optional `con` param for test injection.

**Acceptance criteria:**

- [ ] `init_db()` on a temp path creates the file and tables.
- [ ] After inserting a known Instrument, `get_instrument(symbol)` returns an equal model.
- [ ] mypy strict passes; no raw f-string SQL with user values (use parameters).

**Out of scope:** migrations, async.

## M0-06 — Seed data files (CSV contracts)

**Depends on:** M0-04 (column parity)

**Context:** Committed seed data so the repo runs offline with no Notion credentials.

**Files:** `data/seed/event_types.csv`, `instruments.csv`, `effect_size_seed.csv`,
`news_sources.csv`, `countries.csv`

**Spec:** Each CSV's header columns MUST equal the corresponding table's seed columns (M0-04). Rows
sourced from the project's Notion tables (Events 31, Instruments 55, Effect-Size ~55, News Sources
27, Countries 50). If the full export isn't available, commit a non-empty representative subset
(>=5 rows each) with correct headers; the full tables live in the Notion workspace. UTF-8, comma-delimited,
quoted where needed.

**Acceptance criteria:**

- [ ] Each CSV exists, is UTF-8, has the exact header columns of its table.
- [ ] Each CSV has >=1 data row; enum columns use enum values from M0-03 (e.g., direction
  up/down/mixed/conditional).

**Out of scope:** the loader (M0-07).

## M0-07 — Seed loader

**Depends on:** M0-05, M0-06

**Context:** Read seed CSVs → validate via Pydantic → insert into DuckDB.

**Files:** `src/fortuneteller/seed.py`

**Spec:**

- For each (csv_file, model, table): read with Polars (`pl.read_csv`), coerce to the Pydantic model
  row-by-row (collect ValidationErrors, fail with a message naming file+row), then
  `db.insert_models(table, rows)`.
- `load_all() -> dict[str, int]` — loads all five seed tables, returns `{table: row_count}`.
  Idempotent: clear each table before load (or INSERT OR REPLACE).
- `query_demo() -> EffectSizeSeed | None` — return `db.get_effect_size("CPI / inflation surprise",
  "SPY / ES")` (or first row if absent) for the query-demo command.

**Acceptance criteria:**

- [ ] `uv run fortuneteller seed` loads all CSVs; printed counts equal CSV row counts.
- [ ] A malformed enum value causes a ValidationError naming the file and row.
- [ ] `uv run fortuneteller query-demo` prints a non-null effect-size row.

**Out of scope:** loading fact tables (empty in M0).

## M0-08 — Smoke tests

**Depends on:** M0-05, M0-07

**Context:** Encode the M0 'done when' as automated tests.

**Files:** `tests/conftest.py`, `tests/test_smoke.py`

**Spec:**

- conftest.py: a `tmp_db` fixture pointing settings.db_path at a tmp_path file and running
  `init_db()`.
- Tests: (1) init_db creates all 8 tables (count_rows returns 0 pre-seed); (2) load_all returns
  counts matching CSV row counts; (3) post-seed instruments and effect_size_seed counts > 0;
  (4) get_effect_size(...) returns an EffectSizeSeed; (5) one Pydantic round-trip (model → insert
  → query → equal).

**Acceptance criteria:**

- [ ] `uv run pytest` passes with all tests green.
- [ ] Tests use the temp DB only (never touch `data/fortuneteller.duckdb`).

**Out of scope:** coverage gates.

## M0-09 — CI workflow (required, day one)

**Depends on:** M0-01

**Context:** Run quality gates on every push from day one — the cheapest regression catch when an
agent is committing. Mirrors `just check`.

**Files:** `.github/workflows/ci.yml`

**Spec:** GitHub Actions on push/PR: set up Python 3.12 + uv, uv sync, then uv run ruff check, uv
run mypy src, uv run pytest.

**Acceptance criteria:**

- [ ] Workflow runs the three gates and fails if any fails.

**Out of scope:** deploy, release.

---

### Execution summary

Implement in order M0-01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 (CI).
After M0-08 passes, the five M0 milestone exit criteria are met and the repo is ready for M1 (the
thin vertical slice).
