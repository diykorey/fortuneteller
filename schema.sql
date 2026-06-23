-- FortuneTeller data spine (M0-04).
--
-- Plain DuckDB DDL so the eventual Postgres migration stays cheap. Columns mirror the
-- M0-03 Pydantic models 1:1 for the seed/fact tables; effect_size_matrix is computed
-- during calibration (M2) and has no seed model. Read and executed by db.init_db()
-- (M0-05) from settings.schema_path. Out of scope here: indexes, views.
--
-- Order matters: observations references event_instances, so that table is created first.

CREATE TABLE IF NOT EXISTS event_types (
    event_type TEXT PRIMARY KEY,
    tier       SMALLINT,
    polarity   TEXT
);

CREATE TABLE IF NOT EXISTS instruments (
    symbol        TEXT PRIMARY KEY,
    name          TEXT,
    asset_class   TEXT,
    region        TEXT,
    primary_venue TEXT,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS effect_size_seed (
    event_type           TEXT,
    instrument           TEXT,
    direction            TEXT,
    typical_magnitude    TEXT,
    reaction_half_life   TEXT,
    direction_confidence TEXT,
    hit_rate_est         TEXT,
    surprise_dependent   TEXT,
    basis                TEXT,
    PRIMARY KEY (event_type, instrument)
);

CREATE TABLE IF NOT EXISTS news_sources (
    rank            INTEGER,
    source          TEXT PRIMARY KEY,
    type            TEXT,
    domains_covered TEXT,
    speed           TEXT,
    reliability     TEXT,
    api_access      TEXT,
    cost            TEXT
);

CREATE TABLE IF NOT EXISTS countries (
    rank                INTEGER,
    country             TEXT PRIMARY KEY,
    gdp_2026e           TEXT,
    platforms_in_list   TEXT,
    coverage_gap        TEXT,
    primary_news_source TEXT
);

CREATE TABLE IF NOT EXISTS event_instances (
    event_id        BIGINT PRIMARY KEY,
    event_type      TEXT,
    event_ts        TIMESTAMP,
    country         TEXT,
    detail          TEXT,
    scheduled       BOOLEAN,
    consensus       DOUBLE,
    actual          DOUBLE,
    surprise        DOUBLE,
    surprise_sd     DOUBLE,
    surprise_source TEXT,
    priced_in_prior DOUBLE,
    vix_t0          DOUBLE,
    rate_regime     TEXT,
    quality         TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    obs_id        BIGINT PRIMARY KEY,
    event_id      BIGINT REFERENCES event_instances(event_id),
    instrument    TEXT,
    px_t0         DOUBLE,
    ret_unit      TEXT,
    ret_5m        DOUBLE,
    ret_1h        DOUBLE,
    ret_1d        DOUBLE,
    ret_1w        DOUBLE,
    abn_ret_1d    DOUBLE,
    car           DOUBLE,
    peak_move     DOUBLE,
    half_life_min DOUBLE,
    realized_dir  TEXT,
    data_source   TEXT,
    quality       TEXT
);

CREATE TABLE IF NOT EXISTS effect_size_matrix (
    event_type      TEXT,
    instrument      TEXT,
    direction       TEXT,
    mag_per_sd      DOUBLE,
    mag_ci_low      DOUBLE,
    mag_ci_high     DOUBLE,
    median_half_life TEXT,
    hit_rate        DOUBLE,
    n_obs           INTEGER,
    surprise_dep    TEXT,
    last_calibrated TIMESTAMP,
    PRIMARY KEY (event_type, instrument)
);
