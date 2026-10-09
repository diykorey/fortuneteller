"""The published consensus: Nasdaq's calendar, each release's row, checked against TradingView's."""

import json
from datetime import date
from pathlib import Path

import pytest

from fortuneteller import sources
from fortuneteller.expectations import Actual, match_consensus
from fortuneteller.sources import CalendarError, CalendarRow


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


DAY = date(2026, 9, 11)


def _match(
    rows: list[CalendarRow], checks: list[CalendarRow] | None = None, value: float = 0.31
) -> tuple[dict[tuple[int, str], float], list[str]]:
    actual = Actual(1, sources.CORE, date(2026, 8, 1), value, "percent")
    return match_consensus([actual], {1: DAY}, rows, checks or [])


def test_the_row_whose_actual_is_the_first_print_gives_the_consensus() -> None:
    # given core CPI's month-on-month row (0.3) and year-on-year row (2.4), and a first print of 0.31
    rows = [CalendarRow("Core CPI", DAY, 0.3, 0.2), CalendarRow("Core CPI", DAY, 2.4, 2.4)]

    # when the consensus is matched
    consensus, left_out = _match(rows)

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
    consensus, left_out = match_consensus([actual], {1: date(2008, 10, 16)}, rows, [])

    # then it has none, and says so
    assert consensus == {}
    assert left_out == ["core on 2008-10-16: no single Nasdaq row matches the first print"]


def test_a_consensus_far_from_tradingview_s_is_left_out() -> None:
    # given Nasdaq's 0.2 against TradingView's -0.1 (a 0.3 gap), and against 0.0 (0.2, the limit)
    rows = [CalendarRow("Core CPI", DAY, 0.3, 0.2)]
    far = [CalendarRow("Core Inflation Rate MoM", DAY, 0.3, -0.1)]
    near = [CalendarRow("Core Inflation Rate MoM", DAY, 0.3, 0.0)]

    # when each is matched
    left, left_out = _match(rows, far)
    kept, _ = _match(rows, near)

    # then the far one gets no consensus and is named; the one at the limit keeps it
    assert left == {}
    assert left_out == ["core on 2026-09-11: Nasdaq 0.2, TradingView -0.1"]
    assert kept == {(1, sources.CORE): 0.2}


def test_a_day_without_any_consensus_is_simply_skipped() -> None:
    # given a release day whose rows have no consensus (before 2008)
    rows = [CalendarRow("Core CPI", DAY, 0.3, None)]

    # when the consensus is matched
    consensus, left_out = _match(rows)

    # then there is nothing, and nothing to report
    assert (consensus, left_out) == ({}, [])
