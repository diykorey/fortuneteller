"""The published consensus: Nasdaq's calendar, each release's row, checked against TradingView's."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from fortuneteller import expectations, flows, sources
from fortuneteller.expectations import Actual, build_surprises, match_consensus
from fortuneteller.sources import CalendarError, CalendarRow, FirstRelease


def _nasdaq(*rows: tuple[str, str, str, str]) -> bytes:
    return json.dumps(
        {
            "data": {
                "rows": [
                    {"country": c, "eventName": n, "actual": a, "consensus": k}
                    for c, n, a, k in rows
                ]
            }
        }
    ).encode()


def test_a_nasdaq_day_keeps_the_named_us_rows_in_percent_and_thousands() -> None:
    # given a made-up day: core CPI month-on-month and year-on-year, payrolls, and rows not wanted
    payload = _nasdaq(
        ("United States", "Core CPI", "0.3%", "0.2%"),
        ("United States", "Core CPI", "2.4%", "2.4%"),
        ("United States", "Nonfarm Payrolls", "-20,537K", "&nbsp;"),
        ("United States", "Trade Balance", "-78.2B", " "),
        ("Germany", "Core CPI", "0.1%", "0.1%"),
    )

    # when it is parsed for core CPI and payrolls
    rows = sources.parse_nasdaq_day(payload, date(2026, 9, 11), ["Core CPI", "Nonfarm Payrolls"])

    # then both core rows and the payrolls come back as numbers, a blank consensus as none
    day = date(2026, 9, 11)
    assert rows == [
        CalendarRow("Core CPI", day, 0.3, 0.2),
        CalendarRow("Core CPI", day, 2.4, 2.4),
        CalendarRow("Nonfarm Payrolls", day, -20537.0, None),
    ]


def test_an_unreadable_value_in_a_wanted_row_is_refused() -> None:
    # given a payrolls row whose actual is not a number
    payload = _nasdaq(("United States", "Nonfarm Payrolls", "n/a", "150K"))

    # when / then parsing refuses it
    with pytest.raises(CalendarError, match="unreadable"):
        sources.parse_nasdaq_day(payload, date(2026, 9, 4), ["Nonfarm Payrolls"])


def test_nasdaq_is_asked_the_next_day_and_a_past_day_is_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given Nasdaq answering any request, and every URL asked recorded
    asked: list[str] = []

    def answer(url: str, what: str, timeout: float) -> bytes:
        asked.append(url)
        return b"{}"

    monkeypatch.setattr(sources, "_calendar_get", answer)
    today = date(2026, 10, 9)

    # when a past release day is read twice, and yesterday once
    sources.fetch_nasdaq_day(date(2026, 9, 11), tmp_path, today)
    sources.fetch_nasdaq_day(date(2026, 9, 11), tmp_path, today)
    sources.fetch_nasdaq_day(date(2026, 10, 8), tmp_path, today)

    # then each asks for the day after; the past day comes from the cache the second time
    assert [url.rsplit("=", 1)[1] for url in asked] == ["2026-09-12", "2026-10-09"]
    assert sorted(p.name for p in (tmp_path / "nasdaq").iterdir()) == ["2026-09-11.json"]


def test_tradingview_rows_are_on_their_new_york_day_and_an_empty_quarter_is_none() -> None:
    # given a release at 12:30 UTC and one at 03:00 UTC, still the evening before in New York
    payload = json.dumps(
        {
            "status": "ok",
            "result": [
                {
                    "title": "Non Farm Payrolls",
                    "country": "US",
                    "date": "2026-09-04T12:30:00.000Z",
                    "actual": 162,
                    "forecast": 56,
                },
                {
                    "title": "Non Farm Payrolls",
                    "country": "US",
                    "date": "2026-10-03T03:00:00.000Z",
                    "actual": None,
                    "forecast": 60,
                },
            ],
        }
    ).encode()

    # when they are parsed
    rows = sources.parse_tradingview(payload, ["Non Farm Payrolls"])

    # then each is on its New York date, and a quarter with no data gives no rows
    assert [(r.day, r.actual, r.consensus) for r in rows] == [
        (date(2026, 9, 4), 162.0, 56.0),
        (date(2026, 10, 2), None, 60.0),
    ]
    assert sources.parse_tradingview(b'{"status": "no_data"}', ["Non Farm Payrolls"]) == []
    assert sources.parse_tradingview(b'{"status": "ok"}', ["Non Farm Payrolls"]) == []


DAY = date(2026, 9, 11)


def _match(
    rows: list[CalendarRow], checks: list[CalendarRow] | None = None, value: float = 0.31
) -> tuple[dict[tuple[int, str], float], list[str], list[str]]:
    actual = Actual(1, sources.CORE, date(2026, 8, 1), value, "percent")
    return match_consensus([actual], {1: DAY}, rows, checks or [])


def test_the_row_whose_actual_is_the_first_print_gives_the_consensus() -> None:
    # given core CPI's month-on-month row (0.3) and year-on-year row (2.4), and a first print of 0.31
    rows = [CalendarRow("Core CPI", DAY, 0.3, 0.2), CalendarRow("Core CPI", DAY, 2.4, 2.4)]

    # when the consensus is matched
    consensus, left_out, _ = _match(rows)

    # then the month-on-month row's consensus is the release's
    assert consensus == {(1, sources.CORE): 0.2}
    assert left_out == []


@pytest.mark.parametrize(
    ("rows", "count"),
    [
        ([CalendarRow("Core CPI", DAY, 0.5, 0.2)], 0),
        ([CalendarRow("Core CPI", DAY, 0.3, 0.2), CalendarRow("Core CPI", DAY, 0.3, 0.1)], 2),
    ],
)
def test_no_row_or_two_rows_matching_the_first_print_are_refused(
    rows: list[CalendarRow], count: int
) -> None:
    # given rows of which none, or two, carry the first print

    # when / then the match is refused, naming the measure, the day and the count
    with pytest.raises(ValueError, match=f"core on 2026-09-11: {count} Nasdaq rows"):
        _match(rows)


def test_a_named_unreadable_day_is_left_out_not_refused() -> None:
    # given core CPI on 2008-10-16, whose Nasdaq actual is not our first print
    actual = Actual(1, sources.CORE, date(2008, 9, 1), 0.14, "percent")
    rows = [CalendarRow("Core CPI", date(2008, 10, 16), 0.4, 0.2)]

    # when the consensus is matched
    consensus, left_out, _ = match_consensus([actual], {1: date(2008, 10, 16)}, rows, [])

    # then it has none, and says so
    assert consensus == {}
    assert left_out == ["core on 2008-10-16: no single Nasdaq row matches the first print"]


def test_a_consensus_far_from_tradingview_s_is_left_out() -> None:
    # given Nasdaq's 0.2 against TradingView's -0.1 (a 0.3 gap), and against 0.0 (0.2, the limit)
    rows = [CalendarRow("Core CPI", DAY, 0.3, 0.2)]
    far = [CalendarRow("Core Inflation Rate MoM", DAY, 0.3, -0.1)]
    near = [CalendarRow("Core Inflation Rate MoM", DAY, 0.3, 0.0)]

    # when each is matched
    left, left_out, filled_in = _match(rows, far)
    kept, _, _ = _match(rows, near)

    # then the far one gets no consensus and is named; the one at the limit keeps it
    assert left == {}
    assert left_out == ["core on 2026-09-11: Nasdaq 0.2, TradingView -0.1"]
    assert filled_in == []
    assert kept == {(1, sources.CORE): 0.2}


def test_a_day_without_any_consensus_is_simply_skipped() -> None:
    # given a release day whose rows have no consensus (before 2008)
    rows = [CalendarRow("Core CPI", DAY, 0.3, None)]

    # when the consensus is matched
    consensus, left_out, filled_in = _match(rows)

    # then there is nothing, and nothing to report
    assert (consensus, left_out, filled_in) == ({}, [], [])


@pytest.mark.parametrize(
    "rows",
    [[], [CalendarRow("Core CPI", DAY, 0.3, None)], [CalendarRow("CPI", DAY, 0.3, 0.1)]],
)
def test_where_nasdaq_has_no_row_with_a_consensus_tradingview_s_forecast_is_taken(
    rows: list[CalendarRow],
) -> None:
    # given no Nasdaq row, one with no consensus, or only another measure's; TradingView's at 0.2
    checks = [CalendarRow("Core Inflation Rate MoM", DAY, None, 0.2)]

    # when the consensus is matched
    consensus, left_out, filled_in = _match(rows, checks)

    # then TradingView's forecast is the release's, and it is named
    assert consensus == {(1, sources.CORE): 0.2}
    assert left_out == []
    assert filled_in == ["core on 2026-09-11: TradingView 0.2"]


@pytest.mark.parametrize("rows", [[CalendarRow("Core CPI", date(2008, 10, 16), 0.4, 0.2)], []])
def test_an_unreadable_day_stays_out_though_tradingview_has_a_forecast(
    rows: list[CalendarRow],
) -> None:
    # given core CPI on 2008-10-16, unreadable, with a Nasdaq row or none, and TradingView's 0.2
    day = date(2008, 10, 16)
    actual = Actual(1, sources.CORE, date(2008, 9, 1), 0.14, "percent")
    checks = [CalendarRow("Core Inflation Rate MoM", day, None, 0.2)]

    # when the consensus is matched
    consensus, left_out, filled_in = match_consensus([actual], {1: day}, rows, checks)

    # then it still has none
    assert consensus == {}
    assert filled_in == []


def test_the_source_gives_each_release_its_consensus_known_the_evening_before(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given CPI released 2026-09-11 with a first print of 0.31, and calendars that agree on 0.2
    event = flows.to_event_instance(
        FirstRelease(date(2026, 8, 1), date(2026, 9, 11), 100.0), flows.CPI_FLOW
    )
    actual = Actual(event.event_id, sources.CORE, date(2026, 8, 1), 0.31, "percent")
    rows = [CalendarRow("Core CPI", DAY, 0.3, 0.2), CalendarRow("Core CPI", DAY, 2.4, 2.4)]
    checks = [CalendarRow("Core Inflation Rate MoM", DAY, 0.3, 0.2)]
    monkeypatch.setattr(expectations, "fetch_calendars", lambda days, cache_dir: (rows, checks))

    # when the source is asked
    found = expectations.NasdaqConsensus().expectations([event], [actual], "key")

    # then it expects 0.2, known at the end of the New York day before, which the shared check takes
    assert [(e.value, e.known_at) for e in found] == [(0.2, datetime(2026, 9, 11, 3, 59, 59))]
    assert len(build_surprises([event], [actual], found, [flows.CPI_EVENT_TYPE])) == 1


def test_the_source_takes_tradingview_s_forecast_where_nasdaq_has_no_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given CPI released 2026-09-11, no Nasdaq row that day, and TradingView's forecast of 0.2
    event = flows.to_event_instance(
        FirstRelease(date(2026, 8, 1), date(2026, 9, 11), 100.0), flows.CPI_FLOW
    )
    actual = Actual(event.event_id, sources.CORE, date(2026, 8, 1), 0.31, "percent")
    checks = [CalendarRow("Core Inflation Rate MoM", DAY, None, 0.2)]
    monkeypatch.setattr(expectations, "fetch_calendars", lambda days, cache_dir: ([], checks))
    source = expectations.NasdaqConsensus()

    # when the source is asked
    found = source.expectations([event], [actual], "key")

    # then it expects TradingView's 0.2, stored as the consensus surprise, and names it filled in
    assert [e.value for e in found] == [0.2]
    surprises = build_surprises([event], [actual], found, [flows.CPI_EVENT_TYPE])
    assert [(s.baseline, round(s.surprise, 9)) for s in surprises] == [
        (expectations.NASDAQ_CONSENSUS, 0.11)
    ]
    assert source.filled_in == ["core on 2026-09-11: TradingView 0.2"]


def _tradingview(*rows: tuple[str, str, float | None]) -> bytes:
    return json.dumps(
        {
            "status": "ok",
            "result": [
                {"title": t, "country": "US", "date": f"{d}T12:30:00.000Z", "forecast": f}
                for t, d, f in rows
            ],
        }
    ).encode()


def test_the_next_consensus_is_the_first_forecast_from_today_with_nasdaq_s_nearest_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given TradingView listing a past release, one with no forecast yet, and the next two with one,
    # the later in next quarter; and Nasdaq's core CPI month-on-month and year-on-year that day
    quarters = {
        date(2026, 10, 1): _tradingview(
            ("Core Inflation Rate MoM", "2026-10-01", 0.3),
            ("Core Inflation Rate MoM", "2026-10-13", None),
            ("Core Inflation Rate MoM", "2026-11-12", 0.2),
        ),
        date(2027, 1, 1): _tradingview(("Core Inflation Rate MoM", "2027-01-14", 0.4)),
    }
    asked: list[date] = []

    def nasdaq(day: date, cache_dir: Path) -> bytes:
        asked.append(day)
        return _nasdaq(
            ("United States", "Core CPI", "", "2.9%"), ("United States", "Core CPI", "", "0.3%")
        )

    monkeypatch.setattr(sources, "fetch_tradingview_quarter", lambda q, cache_dir: quarters[q])
    monkeypatch.setattr(sources, "fetch_nasdaq_day", nasdaq)

    # when the next consensus is read on 2026-10-12
    upcoming = expectations.next_consensus(sources.CORE, date(2026, 10, 12), tmp_path)

    # then it is November's, with Nasdaq's month-on-month row
    assert upcoming == expectations.NextConsensus(date(2026, 11, 12), 0.3, 0.2)
    assert asked == [date(2026, 11, 12)]


def test_no_upcoming_forecast_is_none_and_a_blank_nasdaq_row_is_no_consensus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given payrolls listed with a forecast on 2026-11-06, which Nasdaq has no consensus for yet
    tradingview = _tradingview(("Non Farm Payrolls", "2026-11-06", 60.0))
    monkeypatch.setattr(sources, "fetch_tradingview_quarter", lambda q, cache_dir: tradingview)
    monkeypatch.setattr(
        sources,
        "fetch_nasdaq_day",
        lambda day, cache_dir: _nasdaq(("United States", "Nonfarm Payrolls", "", "")),
    )

    # when the next consensus is read before it, and after it
    before = expectations.next_consensus(expectations.PAYROLLS, date(2026, 10, 12), tmp_path)
    after = expectations.next_consensus(expectations.PAYROLLS, date(2026, 11, 7), tmp_path)

    # then the first has TradingView's forecast but no Nasdaq consensus; the second has nothing
    assert before == expectations.NextConsensus(date(2026, 11, 6), None, 60.0)
    assert after is None
