"""Plugging in: a new event flow and a new expectation source need only one line in a list each."""

from collections.abc import Iterator, Sequence
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from pydantic import SecretStr

from fortuneteller import db, expectations, flows, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.expectations import Actual, Expectation, event_month, own_actuals
from fortuneteller.flows import EventBatch, SurpriseRule
from fortuneteller.models import EventInstance
from fortuneteller.sources import NEW_YORK, FirstRelease

STARTS = "starts"


class HousingFlow:
    # A made-up monthly release: housing starts, 14 months, rising 10k a month through each year.
    event_type = "Real-estate / housing data"
    country = "United States"
    zone = NEW_YORK
    type_code = 9
    cli_name = "housing"
    label = "Hou"
    surprise_rule = SurpriseRule(
        ((STARTS, "toy_consensus"), (STARTS, expectations.TREND_12M)),
        {instrument: 1 for instrument in study.MVP_PRICE_SERIES},
        10.0,
        "10k",
    )

    def events(self, api_key: str) -> EventBatch:
        events = []
        for i in range(14):
            month = date(2024 + i // 12, i % 12 + 1, 1)
            released = date(month.year + month.month // 12, month.month % 12 + 1, 17)
            announced = datetime.combine(released, time(8, 30), tzinfo=NEW_YORK)
            events.append(
                EventInstance(
                    event_id=flows.event_id(self, released),
                    event_type=self.event_type,
                    event_ts=announced.astimezone(UTC).replace(tzinfo=None),
                    country=self.country,
                    detail=f"{month:%Y-%m}",
                    scheduled=True,
                    consensus=None,
                    actual=1000.0 + 100 * i,
                    surprise=None,
                    surprise_sd=None,
                    surprise_source=None,
                    priced_in_prior=None,
                    vix_t0=None,
                    rate_regime=None,
                    quality="first_release",
                )
            )
        return EventBatch(events, [f"loaded {len(events)} Hou releases"])

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        return [
            Actual(e.event_id, STARTS, event_month(e), 10.0 * event_month(e).month, "thousands")
            for e in events
        ]


class ToyConsensus:
    # A made-up forecaster: below the number by the month's number in thousands, known the day before.
    name = "toy_consensus"
    label = "the toy consensus"

    def __init__(self, known_before: timedelta = timedelta(days=1)) -> None:
        self.known_before = known_before

    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], api_key: str
    ) -> list[Expectation]:
        when = {event.event_id: event.event_ts for event in events}
        return [
            Expectation(
                a.event_id,
                a.measure,
                self.name,
                a.value - a.period.month,
                a.unit,
                when[a.event_id] - self.known_before,
            )
            for a in own_actuals(events, actuals)
        ]


@pytest.fixture
def plugged(monkeypatch: pytest.MonkeyPatch) -> Iterator[ToyConsensus]:
    # Registering is one line in each list; the real flows are taken out so nothing is fetched.
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))
    saved_flows, saved_sources = list(flows.EVENT_FLOWS), list(expectations.EXPECTATION_SOURCES)
    source = ToyConsensus()
    flows.EVENT_FLOWS[:] = [HousingFlow()]
    expectations.EXPECTATION_SOURCES[:] = [expectations.Trend12m(), source]
    yield source
    flows.EVENT_FLOWS[:] = saved_flows
    expectations.EXPECTATION_SOURCES[:] = saved_sources


def test_a_new_flow_and_source_run_through_every_command(
    tmp_db: Path, plugged: ToyConsensus, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the housing flow and the toy consensus registered, and every move equal to the surprise
    assert main(["load-releases"]) == 0
    assert main(["load-surprises"]) == 0
    loaded = capsys.readouterr().out.splitlines()
    con = db.get_connection()
    rows = con.execute("SELECT event_id, surprise FROM surprises WHERE baseline = 'toy_consensus'")
    con.executemany(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'pct', ?)",
        [
            (event, instrument, s / 1000)
            for event, s in rows.fetchall()
            for instrument in study.MVP_PRICE_SERIES
        ],
    )

    # when the surprise is measured for it
    code = main(["surprise", "--event", "housing"])

    # then every command took it in: releases, both sources' surprises, and its own report
    out = capsys.readouterr().out.splitlines()
    assert loaded[0] == "loaded 14 Hou releases"
    assert loaded[1].startswith("starts    toy_consensus  14 surprises")
    assert loaded[2].startswith("starts    trend_12m    2 surprises")
    assert code == 0
    assert out[0] == "starts against the toy consensus"
    assert "per 10k" in out[1]


def test_a_new_source_is_checked_like_the_others(
    tmp_db: Path, plugged: ToyConsensus, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the toy consensus claiming to know each number an hour after it came out
    plugged.known_before = timedelta(hours=-1)
    assert main(["load-releases"]) == 0

    # when the surprises are loaded
    code = main(["load-surprises"])

    # then the shared check refuses it, and nothing is stored
    assert code == 1
    assert "not before the event" in capsys.readouterr().err
    assert db.count_rows("surprises", con=db.get_connection()) == 0


class ForeignCpiFlow:
    # US CPI's event type released in another country: only its identity differs.
    event_type = flows.CPI_EVENT_TYPE
    label = "CPI"
    surprise_rule = flows.CPI_FLOW.surprise_rule

    def __init__(self, country: str, zone: str, type_code: int, cli_name: str) -> None:
        self.country, self.zone = country, ZoneInfo(zone)
        self.type_code, self.cli_name = type_code, cli_name

    def events(self, api_key: str) -> EventBatch:
        return EventBatch([], [])

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        return []


UK_CPI = ForeignCpiFlow("United Kingdom", "Europe/London", 7, "uk-cpi")
JAPAN_CPI = ForeignCpiFlow("Japan", "Asia/Tokyo", 8, "jp-cpi")


@pytest.fixture
def abroad() -> Iterator[None]:
    saved = list(flows.EVENT_FLOWS)
    flows.EVENT_FLOWS[:] = [*saved, UK_CPI, JAPAN_CPI]
    yield
    flows.EVENT_FLOWS[:] = saved


def test_one_event_type_in_two_countries_is_stored_and_read_apart(
    tmp_db: Path, abroad: None
) -> None:
    # given US and UK CPI for August 2022, both released on 2022-09-13
    con = db.get_connection()
    release = FirstRelease(date(2022, 8, 1), date(2022, 9, 13), 100.0)
    flows.store_releases(flows.CPI_FLOW, [release], con=con)
    flows.store_releases(UK_CPI, [release], con=con)

    # when each flow's events are read back
    us, uk = flows.stored_events(flows.CPI_FLOW, con=con), flows.stored_events(UK_CPI, con=con)

    # then each holds only its own, under its own id and at its own country's 08:30
    assert [e.country for e in us] == ["United States"]
    assert [e.country for e in uk] == ["United Kingdom"]
    assert us[0].event_id != uk[0].event_id
    assert us[0].event_ts == datetime(2022, 9, 13, 12, 30)
    assert uk[0].event_ts == datetime(2022, 9, 13, 7, 30)
    assert [flows.flow_of(e) for e in us + uk] == [flows.CPI_FLOW, UK_CPI]


def test_the_release_date_is_the_day_in_the_events_own_country(abroad: None) -> None:
    # given Japan's CPI at 08:30 in Tokyo on 2022-09-20: still the 19th in New York
    event = flows.to_event_instance(
        FirstRelease(date(2022, 8, 1), date(2022, 9, 20), 100.0), JAPAN_CPI
    )

    # when its release date is read
    released = flows.release_date(event)

    # then it is Tokyo's date
    assert event.event_ts == datetime(2022, 9, 19, 23, 30)
    assert released == date(2022, 9, 20)


@pytest.mark.parametrize(
    "duplicate",
    [
        ForeignCpiFlow("United States", "America/New_York", 7, "uk-cpi"),
        ForeignCpiFlow("United Kingdom", "Europe/London", flows.CpiFlow.type_code, "uk-cpi"),
        ForeignCpiFlow("United Kingdom", "Europe/London", 7, flows.CpiFlow.cli_name),
    ],
)
def test_two_flows_with_one_identity_are_refused(duplicate: ForeignCpiFlow) -> None:
    # given a flow sharing US CPI's event type and country, its type code or its command-line name
    registered = [*flows.EVENT_FLOWS, duplicate]

    # when / then the check refuses them, though it takes a flow that differs in all three
    with pytest.raises(ValueError, match="two event flows share"):
        flows.check_flows(registered)
    flows.check_flows([*flows.EVENT_FLOWS, UK_CPI])
