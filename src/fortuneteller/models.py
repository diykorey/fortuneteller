"""Domain models and enums — the typed table shapes for the data spine.

Pydantic v2 models with ``extra="forbid"`` (unknown columns fail loudly on load) and lowercase
str-enums that compare equal to their value, matching the seed CSVs in ``data/seed``. Persistence
is out of scope here (M0-05).
"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Polarity(StrEnum):
    positive = "positive"
    negative = "negative"
    both = "both"


class Direction(StrEnum):
    up = "up"
    down = "down"
    mixed = "mixed"
    conditional = "conditional"


class AssetClass(StrEnum):
    equity_index = "equity_index"
    sector_etf = "sector_etf"
    single_stock = "single_stock"
    rates_bond = "rates_bond"
    fx = "fx"
    commodity = "commodity"
    crypto = "crypto"
    volatility = "volatility"
    credit_cds = "credit_cds"
    prediction = "prediction"
    carbon = "carbon"
    freight = "freight"
    insurance_linked = "insurance_linked"


class Region(StrEnum):
    us = "us"
    europe = "europe"
    asia = "asia"
    em = "em"
    global_ = "global"


class HalfLife(StrEnum):
    seconds_minutes = "seconds_minutes"
    minutes_hours = "minutes_hours"
    hours_days = "hours_days"
    days_weeks = "days_weeks"
    weeks_plus = "weeks_plus"


class Confidence(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


class _DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EventType(_DomainModel):
    event_type: str
    tier: Annotated[int, Field(ge=1, le=8)]
    polarity: Polarity


class Instrument(_DomainModel):
    symbol: str
    name: str
    asset_class: AssetClass
    region: Region
    primary_venue: str | None = None
    notes: str | None = None


class EffectSizeSeed(_DomainModel):
    event_type: str
    instrument: str
    direction: Direction
    typical_magnitude: str
    reaction_half_life: HalfLife | None = None
    direction_confidence: Confidence
    hit_rate_est: str | None = None
    surprise_dependent: str
    basis: str | None = None


class NewsSource(_DomainModel):
    rank: int
    source: str
    type: str
    domains_covered: str
    speed: str
    reliability: str
    api_access: str
    cost: str


class Country(_DomainModel):
    rank: int
    country: str
    gdp_2026e: str
    platforms_in_list: str | None = None
    coverage_gap: str | None = None
    primary_news_source: str | None = None


class EventInstance(_DomainModel):
    event_id: int
    event_type: str
    event_ts: datetime
    country: str | None
    detail: str | None
    scheduled: bool
    consensus: float | None
    actual: float | None
    surprise: float | None
    surprise_sd: float | None
    surprise_source: str | None
    priced_in_prior: float | None
    vix_t0: float | None
    rate_regime: str | None
    quality: str


class Observation(_DomainModel):
    obs_id: int
    event_id: int
    instrument: str
    px_t0: float | None
    ret_unit: str | None
    ret_5m: float | None
    ret_1h: float | None
    ret_1d: float | None
    ret_1w: float | None
    abn_ret_1d: float | None
    car: float | None
    peak_move: float | None
    half_life_min: float | None
    realized_dir: str | None
    data_source: str | None
    quality: str | None


class Prediction(_DomainModel):
    event_type: str
    instrument: str
    direction: Direction
    expected_magnitude: str
    half_life: HalfLife | None
    probability: float | None
    magnitude_low: float | None
    magnitude_high: float | None
    regime: str | None
    as_of: datetime
