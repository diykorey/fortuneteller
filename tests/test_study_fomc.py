"""Fed decisions: dates from the Fed's meeting calendars, checked against target-rate changes."""

import json
from datetime import date, datetime, time
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, flows, sources, study
from fortuneteller.models import EventInstance
from fortuneteller.sources import (
    DailyClosingPrice,
    FedError,
    FomcDecision,
    parse_fomc_calendar,
    parse_fomc_history,
)

DATA = Path(__file__).parent / "data"


def test_a_year_page_gives_each_decision_on_the_day_it_was_announced() -> None:
    # given the Fed's 1994 page: statements only on changes, and one unscheduled call
    payload = (DATA / "fed_fomc_history_1994.htm").read_bytes()

    # when it is parsed
    decisions = parse_fomc_history(payload)

    # then every scheduled meeting is a decision, dated by its statement or else its last day,
    # and of the calls only the one that issued a statement counts
    assert decisions == [
        FomcDecision(date(1994, 2, 4), scheduled=True),
        FomcDecision(date(1994, 3, 22), scheduled=True),
        FomcDecision(date(1994, 4, 18), scheduled=False),
        FomcDecision(date(1994, 5, 17), scheduled=True),
        FomcDecision(date(1994, 7, 6), scheduled=True),
        FomcDecision(date(1994, 8, 16), scheduled=True),
        FomcDecision(date(1994, 9, 27), scheduled=True),
        FomcDecision(date(1994, 11, 15), scheduled=True),
        FomcDecision(date(1994, 12, 20), scheduled=True),
    ]


def test_cancelled_meetings_and_notation_votes_are_not_decisions() -> None:
    # given the Fed's 2020 page: two emergency meetings, one cancelled, four notation votes
    payload = (DATA / "fed_fomc_history_2020.htm").read_bytes()

    # when it is parsed
    decisions = parse_fomc_history(payload)

    # then the emergency meetings count on their announcement days, and nothing else in March does
    march = [d for d in decisions if d.day.month == 3]
    assert march == [
        FomcDecision(date(2020, 3, 3), scheduled=False),
        FomcDecision(date(2020, 3, 15), scheduled=False),
    ]
    assert len(decisions) == 9


def test_a_meeting_without_a_statement_is_a_decision_only_before_may_1999() -> None:
    # given a 1999 meeting before statements became routine, and a 2003 briefing with none
    payload = b"""
        <h5>February 2-3 Meeting - 1999</h5><a href="/fomc/minutes/19990202.htm">Minutes</a>
        <h5>September 15 Meeting - 2003</h5><a href="/files/FOMC20030915Agenda.pdf">Agenda</a>
        <h5>September 16 Meeting - 2003</h5>
        <a href="/boarddocs/press/monetary/2003/20030916/default.htm">Statement</a>
    """

    # when it is parsed
    decisions = parse_fomc_history(payload)

    # then the 1999 meeting counts on its last day, the 2003 briefing does not
    assert decisions == [
        FomcDecision(date(1999, 2, 3), scheduled=True),
        FomcDecision(date(2003, 9, 16), scheduled=True),
    ]


def test_the_current_calendar_gives_meetings_with_a_statement() -> None:
    # given the current calendar's 2025 meetings, and a statement on long-run goals that year
    payload = (DATA / "fed_fomc_calendar_2025.htm").read_bytes()

    # when it is parsed
    decisions = parse_fomc_calendar(payload)

    # then the eight meetings count, dated by their statements, and the goals statement does not
    assert [d.day for d in decisions] == [
        date(2025, 1, 29),
        date(2025, 3, 19),
        date(2025, 5, 7),
        date(2025, 6, 18),
        date(2025, 7, 30),
        date(2025, 9, 17),
        date(2025, 10, 29),
        date(2025, 12, 10),
    ]
    assert all(d.scheduled for d in decisions)


@pytest.mark.parametrize("parse", [parse_fomc_history, parse_fomc_calendar])
def test_a_page_with_no_meetings_is_refused(parse: object) -> None:
    # given a page that is not a Fed calendar, e.g. an error page
    payload = b"<html><body>Service unavailable</body></html>"

    # when / then it is refused rather than read as a year without decisions
    with pytest.raises(FedError, match="no FOMC meetings"):
        parse(payload)  # type: ignore[operator]


def test_a_target_change_without_a_decision_is_named() -> None:
    # given decisions on 2017-03-15 and 2020-03-15, and target changes the following days
    decisions = [FomcDecision(date(2017, 3, 15), True), FomcDecision(date(2020, 3, 15), False)]
    rates = [
        (date(2017, 3, 15), 0.75),
        (date(2017, 3, 16), 1.0),
        (date(2020, 3, 13), 1.0),
        (date(2020, 3, 16), 0.25),
        (date(2022, 3, 16), 0.25),
        (date(2022, 3, 17), 0.5),
    ]

    # when the changes are matched to decisions
    unmatched = flows.unmatched_target_changes(decisions, rates)

    # then a change effective a day or a weekend after its decision is matched, a lone one is not
    assert unmatched == [date(2022, 3, 17)]


def test_a_decision_becomes_an_event_at_its_announced_time() -> None:
    # given the unscheduled cut announced at 17:00 New York on Sunday 2020-03-15
    decision = FomcDecision(date(2020, 3, 15), scheduled=False)

    # when it is mapped
    event = flows.fomc_event_instance(decision)

    # then it is a US central-bank decision keyed 3 + its day, at 21:00 UTC, unscheduled
    assert event.event_id == 3_2020_03_15
    assert event.event_type == "Central-bank decision"
    assert event.country == "United States"
    assert event.event_ts == datetime(2020, 3, 15, 21, 0)
    assert not event.scheduled
    assert event.actual is None


@pytest.mark.parametrize(
    ("day", "announced"),
    [
        (date(2008, 12, 16), time(14, 15)),
        (date(2012, 6, 20), time(12, 30)),
        (date(2013, 1, 30), time(14, 15)),
        (date(2013, 3, 20), time(14, 0)),
        (date(2001, 9, 17), time(8, 20)),
    ],
)
def test_a_scheduled_statement_came_at_14_15_until_march_2013(day: date, announced: time) -> None:
    # given a decision day: a scheduled one before or after 2013-03-20, or a listed exception

    # when its announcement time is looked up
    looked_up = flows.fomc_announced_at(day)

    # then it is the era's time, or the exception's own
    assert looked_up == announced


def test_loading_refuses_when_a_target_change_has_no_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the Fed's pages answering with only 1994, and the target rising on a day with no decision
    monkeypatch.setattr(flows, "FED_HISTORY_YEARS", range(1994, 1995))
    pages = {
        sources.fed_history_url(1994): (DATA / "fed_fomc_history_1994.htm").read_bytes(),
        sources.FED_CALENDAR_URL: (DATA / "fed_fomc_calendar_2025.htm").read_bytes(),
    }
    monkeypatch.setattr(sources, "fetch_fed_page", lambda url: pages[url])
    target = {
        "count": 2,
        "observations": [
            {"date": "1994-06-01", "value": "3.75"},
            {"date": "1994-06-02", "value": "4.00"},
        ],
    }
    monkeypatch.setattr(sources, "fetch_series", lambda _key, _series: json.dumps(target).encode())

    # when / then the load is refused, naming the day
    with pytest.raises(ValueError, match="1994-06-02"):
        flows.load_fomc_decisions("key")


def test_stored_decisions_are_measured_like_any_other_event() -> None:
    # given one decision stored
    con = duckdb.connect(":memory:")
    db.init_db(con=con)

    # when it is stored and read back
    flows.store_fomc_decisions([FomcDecision(date(2020, 3, 15), scheduled=False)], con=con)

    # then it is one event of its type, released the day it was announced
    events = flows.stored_events(flows.FOMC_EVENT_TYPE, con=con)
    assert [flows.release_date(e) for e in events] == [date(2020, 3, 15)]


GOLD_CLOSE = study.MVP_PRICE_SERIES["GC / XAU"].close
SPX_CLOSE = study.MVP_PRICE_SERIES["SPY / ES"].close


def _event_at(utc: datetime) -> EventInstance:
    decision = flows.fomc_event_instance(FomcDecision(date(2020, 1, 29), scheduled=True))
    return decision.model_copy(update={"event_ts": utc})


def test_a_decision_after_gold_settles_reacts_in_gold_the_next_day() -> None:
    # given a decision at 14:00 New York on 2020-01-29
    event = _event_at(datetime(2020, 1, 29, 19, 0))

    # when its first reaction day is found for gold (13:30) and the S&P 500 (16:00)
    gold, spx = (study.first_reaction_day(event, close) for close in (GOLD_CLOSE, SPX_CLOSE))

    # then gold's is the next day, the S&P 500's the same day
    assert (gold, spx) == (date(2020, 1, 30), date(2020, 1, 29))


def test_a_winter_release_at_8_30_reacts_in_gold_the_same_day() -> None:
    # given a release at 08:30 New York in January: 13:30 UTC, gold's close as a UTC clock reads it
    event = _event_at(datetime(2020, 1, 14, 13, 30))

    # when its first reaction day is found for gold
    first = study.first_reaction_day(event, GOLD_CLOSE)

    # then the time is compared in New York, so it is the same day
    assert first == date(2020, 1, 14)


def test_a_sunday_evening_decision_pairs_fridays_close_with_mondays() -> None:
    # given the cut announced at 17:00 New York on Sunday 2020-03-15, and closes either side
    event = flows.fomc_event_instance(FomcDecision(date(2020, 3, 15), scheduled=False))
    closes = [DailyClosingPrice(date(2020, 3, 13), 1.0), DailyClosingPrice(date(2020, 3, 16), 0.9)]

    # when the S&P 500's closes are paired around it
    pair = study.closing_price_before_after(closes, study.first_reaction_day(event, SPX_CLOSE))

    # then the move runs from Friday's close to Monday's
    assert pair == (closes[0], closes[1])
