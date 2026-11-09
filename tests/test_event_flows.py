"""Plugging in: a new event flow and a new expectation source need only one line in a list each."""

import json
from collections.abc import Iterator, Sequence
from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import pytest
from pydantic import SecretStr

from fortuneteller import db, expectations, flows, sources, study
import fortuneteller.__main__ as cli
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
    type_code = 98
    cli_name = "housing"
    label = "Hou"
    per_month = 10.0
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
            announced = datetime.combine(released, time(8, 30), tzinfo=self.zone)
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
        return EventBatch(events, [f"loaded {len(events)} {self.label} releases"])

    def actuals(self, events: Sequence[EventInstance], api_key: str) -> list[Actual]:
        return [
            Actual(
                e.event_id,
                STARTS,
                event_month(e),
                self.per_month * event_month(e).month,
                "thousands",
            )
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


UK_CPI = ForeignCpiFlow("United Kingdom", "Europe/London", 96, "uk-cpi")
JAPAN_CPI = ForeignCpiFlow("Japan", "Asia/Tokyo", 97, "jp-cpi")


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
        ForeignCpiFlow("United States", "America/New_York", 96, "uk-cpi"),
        ForeignCpiFlow("United Kingdom", "Europe/London", flows.CpiFlow.type_code, "uk-cpi"),
        ForeignCpiFlow("United Kingdom", "Europe/London", 96, flows.CpiFlow.cli_name),
    ],
)
def test_two_flows_with_one_identity_are_refused(duplicate: ForeignCpiFlow) -> None:
    # given a flow sharing US CPI's event type and country, its type code or its command-line name
    registered = [*flows.EVENT_FLOWS, duplicate]

    # when / then the check refuses them, though it takes a flow that differs in all three
    with pytest.raises(ValueError, match="two event flows share"):
        flows.check_flows(registered)
    flows.check_flows([*flows.EVENT_FLOWS, UK_CPI])


class UkHousingFlow(HousingFlow):
    # The same release from the UK: same event type and measure, ten times the numbers.
    country = "United Kingdom"
    zone = ZoneInfo("Europe/London")
    type_code = 99
    cli_name = "uk-housing"
    label = "UKH"
    per_month = 100.0


def _moves(con: duckdb.DuckDBPyConnection, country: str, sign: int) -> None:
    # Every instrument moves with the toy surprise of the country's events, times ``sign``.
    rows = con.execute(
        "SELECT s.event_id, s.surprise FROM surprises s JOIN event_instances e USING (event_id) "
        "WHERE s.baseline = 'toy_consensus' AND e.country = ?",
        [country],
    )
    con.executemany(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'pct', ?)",
        [
            (event, instrument, sign * s / 1000)
            for event, s in rows.fetchall()
            for instrument in study.MVP_PRICE_SERIES
        ],
    )


def _us_surprises(con: duckdb.DuckDBPyConnection) -> list[tuple[object, ...]]:
    return con.execute(
        "SELECT s.* FROM surprises s JOIN event_instances e USING (event_id) "
        "WHERE e.country = 'United States' ORDER BY ALL"
    ).fetchall()


def test_a_second_country_leaves_the_firsts_trend_and_report_untouched(
    tmp_db: Path, plugged: ToyConsensus, capsys: pytest.CaptureFixture[str]
) -> None:
    # given US housing loaded, measured and reported on its own
    con = db.get_connection()
    assert main(["load-releases"]) == 0
    assert main(["load-surprises"]) == 0
    _moves(con, "United States", 1)
    capsys.readouterr()
    assert main(["surprise", "--event", "housing"]) == 0
    alone, us_rows = capsys.readouterr().out, _us_surprises(con)

    # when UK housing, same type and measure, ten times the numbers and moving the other way, joins
    flows.EVENT_FLOWS.append(UkHousingFlow())
    assert main(["load-releases"]) == 0
    assert main(["load-surprises"]) == 0
    _moves(con, "United Kingdom", -1)
    capsys.readouterr()
    assert main(["surprise", "--event", "housing"]) == 0
    beside = capsys.readouterr().out
    assert main(["surprise", "--event", "uk-housing"]) == 0
    uk = capsys.readouterr().out

    # then the US trend, surprises and report are as before, and the UK has its own
    assert _us_surprises(con) == us_rows
    assert beside == alone
    assert uk != alone
    uk_trend = con.execute(
        "SELECT s.expected_mom FROM surprises s JOIN event_instances e USING (event_id) "
        "WHERE e.country = 'United Kingdom' AND s.baseline = 'trend_12m' ORDER BY s.event_id"
    ).fetchall()
    assert uk_trend == [(650.0,), (650.0,)]


def test_a_markets_close_is_read_in_its_own_zone() -> None:
    # given a Fed decision at 14:00 New York, and a London market closing at 16:30 London
    london = study.PriceSeries("^FTSE", "pct", time(16, 30), ZoneInfo("Europe/London"))
    in_new_york = london._replace(zone=NEW_YORK)
    decision = flows.fomc_event_instance(sources.FomcDecision(date(2022, 9, 21), True))

    # when its first reaction day is found
    day = study.first_reaction_day(decision, london)

    # then it is the next day: 19:00 in London is after the close, 14:00 in New York is not
    assert day == date(2022, 9, 22)
    assert study.first_reaction_day(decision, in_new_york) == date(2022, 9, 21)


@pytest.mark.parametrize(
    "released",
    # Europe and the US on the same time, then the weeks in March and October when New York has
    # changed its clocks and Frankfurt not yet, or the other way round.
    [date(2026, 6, 10), date(2026, 3, 11), date(2026, 10, 28)],
)
@pytest.mark.parametrize("instrument", ["DAX", "SX5E"])
def test_an_08_30_release_in_new_york_reacts_in_frankfurt_the_same_day(
    released: date, instrument: str
) -> None:
    # given a CPI release at 08:30 New York
    event = flows.to_event_instance(FirstRelease(date(2026, 1, 1), released, 100.0), flows.CPI_FLOW)

    # when its first reaction day on a European market is found
    day = study.first_reaction_day(event, study.MVP_PRICE_SERIES[instrument])

    # then it is the release's own day: 13:30 or 14:30 in Frankfurt, before its 17:30 close
    assert day == released


@pytest.mark.parametrize("released", [date(2026, 6, 10), date(2026, 3, 11), date(2026, 10, 28)])
@pytest.mark.parametrize(
    "instrument",
    [
        "UKX",
        "SXXP",
        "BTC",
        "BRN",
        "UST5Y / ZF",
        "CORN",
        "WEAT",
        "SOYB",
        "UGA",
        "UNG",
        "XLU",
        "ITB",
        "KC",
        "T5YIE",
    ],
)
def test_an_08_30_release_in_new_york_reacts_the_same_day_in_london_zurich_and_utc(
    released: date, instrument: str
) -> None:
    # given a CPI release at 08:30 New York
    event = flows.to_event_instance(FirstRelease(date(2026, 1, 1), released, 100.0), flows.CPI_FLOW)

    # when its first reaction day is found on a market closing in London, Zurich, UTC or New York
    day = study.first_reaction_day(event, study.MVP_PRICE_SERIES[instrument])

    # then it is the release's own day: every one of these closes comes after 08:30 New York
    assert day == released


@pytest.mark.parametrize("released", [date(2026, 6, 10), date(2026, 3, 11), date(2026, 10, 28)])
def test_an_08_30_release_reacts_in_the_euro_s_next_london_day(released: date) -> None:
    # given a CPI release at 08:30 New York, and Yahoo's euro bar closing at 00:00 London of its day
    event = flows.to_event_instance(FirstRelease(date(2026, 1, 1), released, 100.0), flows.CPI_FLOW)

    # when its first reaction day is found
    day = study.first_reaction_day(event, study.MVP_PRICE_SERIES["EURUSD"])

    # then it is the next London day's bar, the first whose price follows the release
    assert day == released + timedelta(days=1)


def test_a_14_00_fed_decision_reacts_next_day_in_london_and_coffee_same_day_in_brent_and_breakeven() -> (
    None
):
    # given a Fed decision at 14:00 New York
    decision = flows.fomc_event_instance(sources.FomcDecision(date(2022, 9, 21), True))

    # when its first reaction day is found on the FTSE 100, bitcoin, Brent, coffee and the breakeven
    days = {
        instrument: study.first_reaction_day(decision, study.MVP_PRICE_SERIES[instrument])
        for instrument in ("UKX", "BTC", "BRN", "KC", "T5YIE")
    }

    # then London (19:00 there) and coffee's 13:30 settlement have passed; bitcoin's UTC day,
    # Brent's 14:30 settlement and the breakeven's 15:30 curve have not
    assert days == {
        "UKX": date(2022, 9, 22),
        "BTC": date(2022, 9, 21),
        "BRN": date(2022, 9, 21),
        "KC": date(2022, 9, 22),
        "T5YIE": date(2022, 9, 21),
    }


def test_the_more_outcomes_take_their_signs_by_analogy() -> None:
    # given a rule's signs for the seven markets measured first
    seven = {
        "SPY / ES": -1,
        "UST10Y / ZN": 1,
        "DXY": 1,
        "GC / XAU": 0,
        "VIX": 1,
        "DAX": -1,
        "SX5E": -1,
    }

    # when the more outcomes are added
    signs = flows.with_more_outcomes(seven)

    # then the euro mirrors the dollar index, the 5-year yield follows the 10-year's, the Nasdaq the
    # S&P 500's, the FTSE 100 and the STOXX 600 the DAX's, utilities the 10-year's reversed, the
    # others have none, in the markets' order
    assert {k: v for k, v in signs.items() if k not in seven} == {
        "BRN": 0,
        "EURUSD": -1,
        "COMP": -1,
        "UST5Y / ZF": 1,
        "UKX": -1,
        "SXXP": -1,
        "BTC": 0,
        "ITA": 0,
        "XLE": 0,
        "CORN": 0,
        "WEAT": 0,
        "SOYB": 0,
        "UGA": 0,
        "UNG": 0,
        "XLU": -1,
        "ITB": 0,
        "KC": 0,
        "T5YIE": 0,
    }
    assert list(signs) == list(study.MVP_PRICE_SERIES)


def test_utilities_and_homebuilders_take_their_signs_on_each_rule() -> None:
    # given every rule's signs
    fed = flows.FED_SENTIMENT_RULE.expected_sign
    rules = {
        "cpi": flows.EXPECTED_SIGN,
        "jobs": flows.NFP_EXPECTED_SIGN,
        "claims": flows.CLAIMS_EXPECTED_SIGN,
        "fed": fed,
        "euro": flows.EURO_EXPECTED_SIGN,
        "german": flows.GERMAN_SURVEY_EXPECTED_SIGN,
    }

    # when utilities', homebuilders' and the breakeven's are read
    signs = {name: (r["XLU"], r["ITB"], r["T5YIE"]) for name, r in rules.items()}

    # then utilities reverse the yield, and homebuilders and the breakeven are signed on inflation
    # news only
    assert signs == {
        "cpi": (-1, -1, 1),
        "jobs": (-1, 0, 0),
        "claims": (1, 0, 0),
        "fed": (-1, 0, 0),
        "euro": (0, 0, 0),
        "german": (0, 0, 0),
    }
    assert flows.PCE_SURPRISE_RULE.expected_sign is flows.EXPECTED_SIGN
    assert flows.RETAIL_SURPRISE_RULE.expected_sign is flows.NFP_EXPECTED_SIGN
    assert flows.GDP_SURPRISE_RULE.expected_sign is flows.NFP_EXPECTED_SIGN
    assert flows.ISM_SURPRISE_RULE.expected_sign is flows.NFP_EXPECTED_SIGN


def test_a_day_only_value_is_known_at_the_end_of_its_own_zones_day() -> None:
    # given a value dated 2022-09-12 in Tokyo
    # when its end of day is found
    known = expectations.end_of_day(date(2022, 9, 12), ZoneInfo("Asia/Tokyo"))

    # then it is Tokyo's midnight, in naive UTC
    assert known == datetime(2022, 9, 12, 14, 59, 59)


def _euro_quarter(*rows: tuple[str, str, float | None]) -> bytes:
    # A TradingView euro-area calendar reply holding ``rows`` of (title, UTC time, actual).
    return json.dumps(
        {
            "status": "ok",
            "result": [
                {"title": t, "country": "EU", "date": when, "actual": a, "forecast": a}
                for t, when, a in rows
            ],
        }
    ).encode()


def test_ecb_decisions_are_read_quarter_by_quarter_at_their_time(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given two quarters of the euro-area calendar: one with a decision, other news and a meeting
    # not yet held, and one with no decision at all
    replies = {
        date(2025, 1, 1): _euro_quarter(
            (sources.ECB_DECISION, "2025-01-30T13:15:00.000Z", 2.9),
            ("Deposit Facility Rate", "2025-01-30T13:15:00.000Z", 2.75),
            ("CPI", "2025-02-03T10:00:00.000Z", 2.5),
        ),
        date(2025, 4, 1): _euro_quarter((sources.ECB_DECISION, "2025-06-05T12:15:00.000Z", None)),
    }
    asked: list[str] = []

    def fetch(
        start: date, cache_dir: Path, today: date | None = None, country: str = "US"
    ) -> bytes:
        asked.append(country)
        return replies.get(start, b'{"status": "no_data"}')

    monkeypatch.setattr(sources, "fetch_tradingview_quarter", fetch)
    monkeypatch.setattr(flows, "ECB_FROM", date(2025, 1, 1))

    # when the decisions up to a day in the second quarter are loaded and mapped to events
    decisions = flows.load_ecb_decisions(tmp_path, today=date(2025, 6, 4))
    events = [flows.ecb_event_instance(d) for d in decisions]

    # then only the one held decision is an event, at 14:15 Frankfurt, from the euro-area calendar
    assert asked == ["EU", "EU"]
    assert [(e.event_id, e.country) for e in events] == [(720250130, "Euro area")]
    assert events[0].event_ts == datetime(2025, 1, 30, 13, 15)
    assert events[0].event_ts.replace(tzinfo=UTC).astimezone(sources.FRANKFURT).time() == time(
        14, 15
    )


def _us_quarter(*rows: tuple[str, str]) -> bytes:
    # A TradingView US calendar reply holding ``rows`` of (title, UTC time), with no values.
    return json.dumps(
        {
            "status": "ok",
            "result": [
                {"title": t, "country": "US", "date": when, "actual": None} for t, when in rows
            ],
        }
    ).encode()


def test_the_fed_chair_s_statements_are_the_ones_given_in_office_one_a_day(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a quarter of the US calendar across the 2014 handover: the chair's speeches and
    # testimonies, his successor's speech before her term, two on one day, a press conference,
    # another speaker, and a speech still ahead
    reply = _us_quarter(
        ("Fed Yellen Speech", "2014-01-15T15:00:00.000Z"),
        ("Fed Bernanke testifies", "2014-01-16T15:00:00.000Z"),
        ("Fed Yellen Testimony", "2014-02-11T20:00:00.000Z"),
        ("Fed Chair Yellen Speaks", "2014-02-11T15:00:00.000Z"),
        ("Fed Press Conference", "2014-03-19T18:30:00.000Z"),
        ("Fed Williams Speech", "2014-03-20T16:00:00.000Z"),
        ("FOMC Member Yellen Speech", "2014-03-21T16:00:00.000Z"),
        ("Fed Chair Yellen Speaks", "2014-03-31T16:00:00.000Z"),
    )
    monkeypatch.setattr(
        sources, "fetch_tradingview_quarter", lambda start, *_args, **_kwargs: reply
    )
    monkeypatch.setattr(flows, "STATEMENTS_FROM", date(2014, 1, 1))

    # when the statements given by noon UTC on 2014-03-31 are loaded
    batch = flows.FED_CHAIR_FLOW.load(tmp_path, datetime(2014, 3, 31, 12, 0, tzinfo=UTC))

    # then Bernanke's testimony and Yellen's earliest statement as chair are the events, at their
    # times, and the report counts what was left out
    assert [(e.event_id, e.detail) for e in batch.events] == [
        (1120140116, "Fed Bernanke testifies"),
        (1120140211, "Fed Chair Yellen Speaks"),
    ]
    assert batch.events[1].event_ts == datetime(2014, 2, 11, 15, 0)
    assert batch.report == [
        "loaded 2 Fed chair statements, 2014-01-16 … 2014-02-11",
        "  left out 1 titled with a holder out of office that day",
        "  1 days with two, the earliest kept",
    ]


def test_an_ecb_president_s_late_speech_is_on_its_frankfurt_day(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a Lagarde speech at 23:30 UTC, already the next day in Frankfurt
    reply = _euro_quarter(("ECB President Lagarde Speech", "2025-03-03T23:30:00.000Z", None))
    monkeypatch.setattr(
        sources, "fetch_tradingview_quarter", lambda start, *_args, **_kwargs: reply
    )
    monkeypatch.setattr(flows, "STATEMENTS_FROM", date(2025, 1, 1))

    # when the president's statements are loaded
    batch = flows.ECB_PRESIDENT_FLOW.load(tmp_path, datetime(2025, 3, 31, tzinfo=UTC))

    # then the event is a euro-area statement of 2025-03-04
    assert [(e.event_id, e.event_type, e.country) for e in batch.events] == [
        (1220250304, "Central-bank statement", "Euro area")
    ]


# The real method; the shared fixture makes every other test's day statement-free.
STATEMENT_AHEAD = flows.StatementFlow.ahead
PREVIEW_DAY = date(2026, 11, 12)
AT_0830 = datetime.combine(PREVIEW_DAY, time(8, 30), tzinfo=NEW_YORK)


def _statements_on_the_preview_day(
    monkeypatch: pytest.MonkeyPatch, us: Sequence[tuple[str, str]]
) -> None:
    monkeypatch.setattr(flows.StatementFlow, "ahead", STATEMENT_AHEAD)
    replies = {"US": _us_quarter(*us), "EU": b'{"status": "no_data"}'}
    monkeypatch.setattr(
        sources,
        "fetch_tradingview_quarter",
        lambda start, cache_dir, today, country: replies[country],
    )


@pytest.mark.parametrize(
    ("rows", "ahead"),
    [
        ([("Fed Chair Warsh Speech", "2026-11-12T15:00:00.000Z")], "Fed Chair Warsh Speech"),
        (
            [
                ("Fed Chair Warsh Speech", "2026-11-12T08:00:00.000Z"),
                ("Fed Chair Warsh Testimony", "2026-11-12T15:00:00.000Z"),
            ],
            None,
        ),
        ([("Fed Powell Speech", "2026-11-12T15:00:00.000Z")], None),
        ([("Fed Chair Warsh Speech", "2026-11-13T15:00:00.000Z")], None),
    ],
    ids=["at-10:00", "earliest-at-03:00", "out-of-office", "tomorrow"],
)
def test_a_statement_is_ahead_only_if_the_day_s_earliest_is_still_to_come(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    rows: list[tuple[str, str]],
    ahead: str | None,
) -> None:
    # given the US calendar on the preview day
    _statements_on_the_preview_day(monkeypatch, rows)

    # when the chair's statement ahead is asked at 08:30 New York
    found = flows.FED_CHAIR_FLOW.ahead(tmp_path, AT_0830)

    # then only a statement given in office today, the day's earliest and still to come, is ahead
    assert (found[1] if found else None) == ahead


def test_live_previews_a_statement_ahead_with_its_flow_s_movers(
    tmp_db: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given no release today, a chair's speech at 10:00 New York, and the scoreboard's data in which
    # the chair's lone days moved the 10-year yield and no other market
    monkeypatch.setattr(expectations, "next_consensus", lambda measure, today, cache_dir: None)
    _statements_on_the_preview_day(
        monkeypatch, [("Fed Chair Warsh Speech", "2026-11-12T15:00:00.000Z")]
    )
    monkeypatch.setattr(cli, "_now", lambda: AT_0830)
    cell = {"days": 176, "ratio": 1.0, "verdict": "doesn't"}
    data = {
        "events": [
            {
                "name": "fedchair",
                "raw_move": {
                    "SPY / ES": cell,
                    "UST10Y / ZN": {"days": 177, "ratio": 1.234, "verdict": "moves"},
                },
            },
            {"name": "ecbchief", "raw_move": {"SPY / ES": cell}},
        ]
    }
    monkeypatch.setattr(settings, "scoreboard_dir", tmp_path)
    (tmp_path / "data.json").write_text(json.dumps(data))

    # when the release-day job's command runs at 08:30
    code = main(["live"])

    # then it says there is no release and previews the speech with its record, no direction
    assert code == 0
    assert capsys.readouterr().out.splitlines() == [
        "live: no release today (2026-11-12)",
        "preview: Fed Chair Warsh Speech at 10:00 New York; on the Fed chair's 177 days alone "
        "before, moved more than on ordinary days: UST10Y / ZN 1.23",
    ]


def test_load_releases_reports_a_calendar_failure(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given every flow but the ECB's answering, and TradingView listing no ECB decision
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("test-key"))
    monkeypatch.setattr(flows, "EVENT_FLOWS", [flows.ECB_FLOW])
    monkeypatch.setattr(flows, "load_ecb_decisions", lambda _cache_dir: [])

    # when the command runs
    code = main(["load-releases"])

    # then it fails with one line and stores nothing
    assert code == 1
    assert capsys.readouterr().err == "load-releases: TradingView listed no ECB decisions\n"
    assert db.count_rows("event_instances", con=db.get_connection()) == 0


def _flash_row(
    title: str, when: str, actual: float | None, forecast: float | None, country: str = "EU"
) -> dict[str, object]:
    return {
        "title": title,
        "country": country,
        "date": when,
        "referenceDate": "2025-01-31T00:00:00Z",
        "actual": actual,
        "forecast": forecast,
    }


def _tradingview_quarter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, calendar: str, rows: list[dict[str, object]]
) -> None:
    """TradingView answering ``rows`` for ``calendar``'s 2025 first quarter, and listing every
    TradingView-only measure from then on."""
    reply = json.dumps({"status": "ok", "result": rows}).encode()

    def fetch(
        start: date, cache_dir: Path, today: date | None = None, country: str = "US"
    ) -> bytes:
        return (
            reply if (start, country) == (date(2025, 1, 1), calendar) else b'{"status": "no_data"}'
        )

    monkeypatch.setattr(sources, "fetch_tradingview_quarter", fetch)
    for measure, row in sources.TRADINGVIEW_ROWS.items():
        monkeypatch.setitem(sources.TRADINGVIEW_ROWS, measure, replace(row, since=date(2025, 1, 1)))
    monkeypatch.setattr(settings, "cache_dir", tmp_path)


def _stored_with_surprises(
    flow: flows.TradingViewFlow,
) -> tuple[list[EventInstance], list[Actual], list[expectations.Surprise]]:
    events = flow.events("unused").events
    flows.store_events(events)
    stored = flows.stored_events(flow)
    actuals = flow.actuals(stored, "unused")
    expected = expectations.TradingViewForecast().expectations(stored, actuals, "unused")
    return (
        stored,
        actuals,
        expectations.build_surprises(stored, actuals, expected, [flow.event_type]),
    )


def test_a_flash_estimate_is_stored_at_its_time_with_both_surprises(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a quarter of the euro-area calendar with one flash, its month-on-month row, Germany's
    # row of the same name and a flash not yet out
    core, headline = (
        sources.TRADINGVIEW_ROWS[sources.EURO_CORE].title,
        sources.TRADINGVIEW_ROWS[sources.EURO_HEADLINE].title,
    )
    rows = [
        _flash_row(core, "2025-02-03T10:00:00.000Z", 2.7, 2.6),
        _flash_row(headline, "2025-02-03T10:00:00.000Z", 2.5, 2.4),
        _flash_row("Inflation Rate MoM Flash", "2025-02-03T10:00:00.000Z", -0.3, None),
        _flash_row(headline, "2025-02-03T13:00:00.000Z", 2.3, 2.6, country="DE"),
        _flash_row(core, "2025-03-03T10:00:00.000Z", None, 2.6),
    ]
    _tradingview_quarter(monkeypatch, tmp_path, "EU", rows)

    # when the flow's events are stored and its actuals paired with TradingView's forecast
    stored, actuals, rows_out = _stored_with_surprises(flows.HICP_FLOW)

    # then the one flash is an event at 11:00 Frankfurt, with a core and a headline surprise
    assert [(e.event_id, e.country, e.detail) for e in stored] == [
        (820250203, "Euro area", "2025-01")
    ]
    at = stored[0].event_ts.replace(tzinfo=UTC).astimezone(sources.FRANKFURT)
    assert at.time() == time(11, 0)
    assert {(r.measure, r.baseline, round(r.surprise, 2)) for r in rows_out} == {
        (sources.EURO_CORE, expectations.TRADINGVIEW_FORECAST, 0.1),
        (sources.EURO_HEADLINE, expectations.TRADINGVIEW_FORECAST, 0.1),
    }
    assert expectations.Trend12m().expectations(stored, actuals, "unused") == []


def test_an_ism_release_is_stored_at_its_new_york_time_with_its_surprise(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a quarter of the US calendar with one ISM release, a row of the same name abroad, the
    # services survey and a release not yet out
    title = sources.TRADINGVIEW_ROWS[sources.ISM_PMI].title
    rows = [
        _flash_row(title, "2025-02-03T15:00:00.000Z", 50.9, 49.8, country="US"),
        _flash_row(title, "2025-02-03T09:00:00.000Z", 46.6, 46.1, country="EU"),
        _flash_row("ISM Services PMI", "2025-02-05T15:00:00.000Z", 52.8, 54.3, country="US"),
        _flash_row(title, "2025-03-03T15:00:00.000Z", None, 50.5, country="US"),
    ]
    _tradingview_quarter(monkeypatch, tmp_path, "US", rows)

    # when the flow's events are stored and its actual paired with TradingView's forecast
    stored, actuals, rows_out = _stored_with_surprises(flows.ISM_FLOW)

    # then the one release is an event at 10:00 New York, a point and a tenth stronger than expected
    assert [(e.event_id, e.country, e.detail) for e in stored] == [
        (920250203, "United States", "2025-01")
    ]
    assert stored[0].event_ts.replace(tzinfo=UTC).astimezone(NEW_YORK).time() == time(10, 0)
    assert [(a.value, a.unit) for a in actuals] == [(50.9, flows.POINTS)]
    assert [(r.measure, r.baseline, round(r.surprise, 2)) for r in rows_out] == [
        (sources.ISM_PMI, expectations.TRADINGVIEW_FORECAST, 1.1)
    ]
    assert expectations.Trend12m().expectations(stored, actuals, "unused") == []


@pytest.mark.parametrize(
    ("flow", "when", "at", "actual", "forecast", "event_id", "unit"),
    [
        (flows.ZEW_FLOW, "2025-02-18T10:00:00.000Z", time(11, 0), 26.0, 20.0, 1320250218, "points"),
        (flows.IFO_FLOW, "2025-02-24T09:00:00.000Z", time(10, 0), 85.2, 85.8, 1420250224, "points"),
        (
            flows.DE_CPI_FLOW,
            "2025-02-14T13:00:00.000Z",
            time(14, 0),
            2.3,
            2.2,
            1520250214,
            "percent",
        ),
    ],
    ids=["zew", "ifo", "decpi"],
)
def test_a_german_release_is_stored_at_its_frankfurt_time_with_its_surprise(
    tmp_db: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    flow: flows.TradingViewFlow,
    when: str,
    at: time,
    actual: float,
    forecast: float,
    event_id: int,
    unit: str,
) -> None:
    # given a quarter of the German calendar with the flow's release, a row of its name on the
    # euro-area calendar and its next release not yet out
    title = sources.TRADINGVIEW_ROWS[flow.measures[0]].title
    rows = [
        _flash_row(title, when, actual, forecast, country="DE"),
        _flash_row(title, when, actual + 5, forecast, country="EU"),
        _flash_row(title, "2025-03-20T10:00:00.000Z", None, forecast, country="DE"),
    ]
    _tradingview_quarter(monkeypatch, tmp_path, "DE", rows)

    # when the flow's events are stored and its actual paired with TradingView's forecast
    stored, actuals, rows_out = _stored_with_surprises(flow)

    # then the one release is a German event at its Frankfurt time, a lesser one, with its surprise
    assert flow.lesser
    assert [(e.event_id, e.country, e.detail) for e in stored] == [(event_id, "Germany", "2025-01")]
    assert stored[0].event_ts.replace(tzinfo=UTC).astimezone(sources.FRANKFURT).time() == at
    assert [(a.value, a.unit) for a in actuals] == [(actual, unit)]
    assert [(r.measure, r.baseline, round(r.surprise, 2)) for r in rows_out] == [
        (flow.measures[0], expectations.TRADINGVIEW_FORECAST, round(actual - forecast, 2))
    ]


def _claims_first_prints(
    monkeypatch: pytest.MonkeyPatch, prints: list[tuple[str, str, str]]
) -> None:
    """FRED answering ``prints`` (week, release day, people) for the claims' first prints."""
    observations = [
        {"date": week, "realtime_start": day, "realtime_end": day, "value": value}
        for week, day, value in prints
    ]
    reply = json.dumps({"count": len(observations), "observations": observations}).encode()

    def fetch(api_key: str, series_id: str = sources.CPI_SERIES_ID) -> bytes:
        assert series_id == sources.CLAIMS_SERIES_ID
        return reply

    monkeypatch.setattr(sources, "fetch_first_releases", fetch)


def test_a_claims_actual_is_freds_first_print_of_its_week_not_tradingviews_revision(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given TradingView showing two Thursdays' weeks as revised, 199k and 198k, and FRED the first
    # print of the first on its day, 197k, and of the second only for another week
    title = sources.TRADINGVIEW_ROWS[sources.INITIAL_CLAIMS].title
    rows = [
        _flash_row(title, "2025-02-06T13:30:00.000Z", 199.0, 200.0, country="US"),
        _flash_row(title, "2025-02-13T13:30:00.000Z", 198.0, 200.0, country="US"),
    ]
    for row, week in zip(rows, ("2025-02-01", "2025-02-08"), strict=True):
        row["referenceDate"] = f"{week}T00:00:00Z"
    _tradingview_quarter(monkeypatch, tmp_path, "US", rows)
    _claims_first_prints(
        monkeypatch,
        [("2025-02-01", "2025-02-06", "197000"), ("2025-02-01", "2025-02-13", "205000")],
    )

    # when the flow's events are stored and their actuals read
    _, actuals, _ = _stored_with_surprises(flows.CLAIMS_FLOW)

    # then the first week's actual is FRED's first print, the second TradingView's
    assert [(a.period, a.value) for a in actuals] == [
        (date(2025, 2, 1), 197.0),
        (date(2025, 2, 8), 198.0),
    ]


def test_a_claims_report_is_stored_on_its_thursday_with_its_week_and_surprise(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a quarter of the US calendar with one Thursday publishing two weeks at once, continuing
    # claims beside them and the next week's report not yet out
    title = sources.TRADINGVIEW_ROWS[sources.INITIAL_CLAIMS].title
    rows = [
        _flash_row(title, "2025-02-06T13:30:00.000Z", 219.0, 213.0, country="US"),
        _flash_row(title, "2025-02-06T13:30:00.000Z", 224.0, 210.0, country="US"),
        _flash_row("Continuing Jobless Claims", "2025-02-06T13:30:00.000Z", 1886.0, 1870.0, "US"),
        _flash_row(title, "2025-02-13T13:30:00.000Z", None, 215.0, country="US"),
    ]
    weeks = ("2025-02-01", "2025-01-25", "2025-01-25", "2025-02-08")
    for row, week in zip(rows, weeks, strict=True):
        row["referenceDate"] = f"{week}T00:00:00Z"
    _tradingview_quarter(monkeypatch, tmp_path, "US", rows)
    _claims_first_prints(monkeypatch, [])

    # when the flow's events are stored and its actual paired with TradingView's forecast
    report = flows.CLAIMS_FLOW.events("unused").report
    stored, actuals, rows_out = _stored_with_surprises(flows.CLAIMS_FLOW)

    # then the Thursday is one event at 08:30 New York, the newer week its detail and its actual,
    # 6k above the forecast, and the week carried with it is reported
    assert report == [
        "loaded 1 jobless claims reports, 2025-02-06 … 2025-02-06",
        "  1 earlier weeks first published with a later one: 2025-02-06",
    ]
    assert [(e.event_id, e.country, e.detail) for e in stored] == [
        (1020250206, "United States", "2025-02-01")
    ]
    assert stored[0].event_ts.replace(tzinfo=UTC).astimezone(NEW_YORK).time() == time(8, 30)
    assert [(a.period, a.value, a.unit) for a in actuals] == [
        (date(2025, 2, 1), 219.0, flows.THOUSANDS)
    ]
    assert [(r.measure, r.baseline, round(r.surprise, 2)) for r in rows_out] == [
        (sources.INITIAL_CLAIMS, expectations.TRADINGVIEW_FORECAST, 6.0)
    ]
