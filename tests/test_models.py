"""Tests for the M0-03 domain models and enums."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from fortuneteller.models import (
    AssetClass,
    Country,
    Direction,
    EffectSizeSeed,
    EventInstance,
    EventType,
    HalfLife,
    Instrument,
    NewsSource,
    Observation,
    Polarity,
    Prediction,
)


def test_enums_compare_by_value() -> None:
    # given str-enum members
    # when compared to their string value
    # then they are equal
    assert Polarity.positive == "positive"
    assert Direction.conditional == "conditional"
    assert AssetClass.equity_index == "equity_index"
    assert HalfLife.minutes_hours == "minutes_hours"


def test_reference_models_construct() -> None:
    # given valid reference-table data
    # when the models are constructed
    event_type = EventType(event_type="CPI / inflation surprise", tier=1, polarity="negative")
    instrument = Instrument(
        symbol="SPY / ES", name="S&P 500", asset_class="equity_index", region="us"
    )
    seed = EffectSizeSeed(
        event_type="CPI / inflation surprise",
        instrument="SPY / ES",
        direction="conditional",
        typical_magnitude="0.5-1.5%",
        reaction_half_life="minutes_hours",
        direction_confidence="high",
        surprise_dependent="yes",
    )
    news = NewsSource(
        rank=1,
        source="Reuters",
        type="Wire",
        domains_covered="all",
        speed="fast",
        reliability="high",
        api_access="yes",
        cost="$$$$",
    )
    country = Country(rank=1, country="United States", gdp_2026e="~30.3")
    # then values coerce to enums and unset optionals default to None
    assert event_type.polarity is Polarity.negative
    assert instrument.primary_venue is None
    assert seed.basis is None
    assert news.rank == 1
    assert country.coverage_gap is None


def test_fact_and_output_models_construct() -> None:
    # given valid fact/output data with nullable fields passed explicitly
    ts = datetime(2026, 6, 22, 12, 30)
    event = EventInstance(
        event_id=1,
        event_type="CPI / inflation surprise",
        event_ts=ts,
        country=None,
        detail=None,
        scheduled=True,
        consensus=None,
        actual=None,
        surprise=None,
        surprise_sd=None,
        surprise_source=None,
        priced_in_prior=None,
        vix_t0=None,
        rate_regime=None,
        quality="high",
    )
    observation = Observation(
        obs_id=1,
        event_id=1,
        instrument="SPY / ES",
        px_t0=None,
        ret_unit=None,
        ret_5m=None,
        ret_1h=None,
        ret_1d=None,
        ret_1w=None,
        abn_ret_1d=None,
        car=None,
        peak_move=None,
        half_life_min=None,
        realized_dir=None,
        data_source=None,
        quality=None,
    )
    prediction = Prediction(
        event_type="CPI / inflation surprise",
        instrument="SPY / ES",
        direction="up",
        expected_magnitude="0.5-1.5%",
        half_life="minutes_hours",
        probability=0.62,
        magnitude_low=None,
        magnitude_high=None,
        regime=None,
        as_of=ts,
    )
    # then they construct and keep their values
    assert event.scheduled is True
    assert observation.quality is None
    assert prediction.direction is Direction.up


def test_invalid_enum_raises() -> None:
    # given an invalid enum value
    # when constructing a model
    # then a ValidationError is raised
    with pytest.raises(ValidationError):
        EventType(event_type="x", tier=1, polarity="sideways")


def test_extra_field_forbidden() -> None:
    # given an unexpected field
    # when constructing a model
    # then extra="forbid" rejects it
    with pytest.raises(ValidationError):
        EventType(event_type="x", tier=1, polarity="positive", bogus=1)


def test_tier_out_of_range_raises() -> None:
    # given a tier outside the 1-8 range
    # when constructing EventType
    # then a ValidationError is raised
    with pytest.raises(ValidationError):
        EventType(event_type="x", tier=9, polarity="positive")
