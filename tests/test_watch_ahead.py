import json
from datetime import date
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import db, sources
from fortuneteller.config import settings
from fortuneteller.expectations import FED_DECISION_ROW

TODAY = date(2026, 11, 12)
NO_DATA = b'{"status": "no_data"}'


def _reply(country: str, *rows: tuple[str, str]) -> bytes:
    # A TradingView reply of ``country``'s calendar holding ``rows`` of (title, UTC time), none
    # held yet.
    return json.dumps(
        {
            "status": "ok",
            "result": [
                {"title": t, "country": country, "date": when, "actual": None, "forecast": None}
                for t, when in rows
            ],
        }
    ).encode()


def _calendars(
    monkeypatch: pytest.MonkeyPatch, replies: dict[tuple[date, str], bytes]
) -> list[tuple[date, str]]:
    asked: list[tuple[date, str]] = []

    def fetch(
        start: date, cache_dir: Path, today: date | None = None, country: str = "US"
    ) -> bytes:
        asked.append((start, country))
        return replies.get((start, country), NO_DATA)

    monkeypatch.setattr(sources, "fetch_tradingview_quarter", fetch)
    return asked


Q4 = date(2026, 10, 1)


def test_the_scheduled_events_not_called_are_listed_from_rows_not_yet_held(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given, in the week after 2026-11-12, a Fed decision, claims, the chair's speech and a former
    # chair's, an ECB decision, the ECB president's speech and ZEW, and a ZEW a day past the week
    _calendars(
        monkeypatch,
        {
            (Q4, "US"): _reply(
                "US",
                (FED_DECISION_ROW, "2026-11-18T19:00:00.000Z"),
                ("Initial Jobless Claims", "2026-11-19T13:30:00.000Z"),
                ("Fed Chair Warsh Speech", "2026-11-16T15:00:00.000Z"),
                ("Fed Powell Speech", "2026-11-17T15:00:00.000Z"),
            ),
            (Q4, "EU"): _reply(
                "EU",
                (sources.ECB_DECISION, "2026-11-19T13:15:00.000Z"),
                ("ECB President Lagarde Speech", "2026-11-13T08:00:00.000Z"),
            ),
            (Q4, "DE"): _reply(
                "DE",
                ("ZEW Economic Sentiment Index", "2026-11-17T10:00:00.000Z"),
                ("ZEW Economic Sentiment Index", "2026-11-20T10:00:00.000Z"),
            ),
        },
    )

    # when the week is read
    watch = cli.week_watch(TODAY, Path("cache"))

    # then each event not called inside the week is listed at its New York time, oldest first,
    # and neither claims, which `live` calls, nor the former chair's speech is
    assert [(w["day"], w["time"], w["event"], w["title"], w["lesser"]) for w in watch] == [
        ("2026-11-13", "03:00", "ecbchief", "ECB President Lagarde Speech", True),
        ("2026-11-16", "10:00", "fedchair", "Fed Chair Warsh Speech", True),
        ("2026-11-17", "05:00", "zew", "ZEW Economic Sentiment Index", True),
        ("2026-11-18", "14:00", "fomc", FED_DECISION_ROW, False),
        ("2026-11-19", "08:15", "ecb", sources.ECB_DECISION, False),
    ]


def test_a_week_crossing_into_the_next_quarter_reads_its_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given ZEW listed only in the next quarter's reply
    q1 = date(2027, 1, 1)
    asked = _calendars(
        monkeypatch,
        {(q1, "DE"): _reply("DE", ("ZEW Economic Sentiment Index", "2027-01-02T10:00:00.000Z"))},
    )

    # when the week from 2026-12-28 is read
    watch = cli.week_watch(date(2026, 12, 28), Path("cache"))

    # then both quarters are read and ZEW is listed
    assert {(Q4, "DE"), (q1, "DE")} <= set(asked)
    assert [w["event"] for w in watch] == ["zew"]


def test_a_release_s_two_rows_and_a_second_statement_are_one_entry_a_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the euro-area flash's core and headline rows at one time, and two of the president's
    # speeches on one day
    _calendars(
        monkeypatch,
        {
            (Q4, "EU"): _reply(
                "EU",
                ("Inflation Rate YoY Flash", "2026-11-17T10:00:00.000Z"),
                ("Core Inflation Rate YoY Flash", "2026-11-17T10:00:00.000Z"),
                ("ECB President Lagarde Speech", "2026-11-16T15:00:00.000Z"),
                ("ECB President Lagarde Testimony", "2026-11-16T09:00:00.000Z"),
            ),
        },
    )

    # when the week is read
    watch = cli.week_watch(TODAY, Path("cache"))

    # then the flash is one entry titled by its first row, and the day's earliest statement is kept
    assert [(w["event"], w["title"]) for w in watch] == [
        ("ecbchief", "ECB President Lagarde Testimony"),
        ("hicp", "Core Inflation Rate YoY Flash"),
    ]


def test_a_calendar_that_cannot_be_read_leaves_only_the_watch_empty(
    tmp_db: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given the German calendar failing, the week ahead read, and the page's other numbers
    def fetch(
        start: date, cache_dir: Path, today: date | None = None, country: str = "US"
    ) -> bytes:
        if country == "DE":
            raise sources.CalendarError("TradingView is down")
        return NO_DATA

    def data(rows, con, today, graded, bad, ahead, watch):  # type: ignore[no-untyped-def]
        return {"events": [], "data_until": None, "ahead": ahead, "watch": watch}

    ahead = [{"day": "2026-11-13", "event": "nfp"}]
    monkeypatch.setattr(sources, "fetch_tradingview_quarter", fetch)
    monkeypatch.setattr(cli, "week_ahead", lambda con, today, cache_dir: ahead)
    monkeypatch.setattr(cli, "scoreboard_data", data)
    monkeypatch.setattr(cli, "_read_guesses", lambda con: ([], []))
    monkeypatch.setattr(db, "count_rows", lambda table, con=None: 1)
    monkeypatch.setattr(settings, "scoreboard_dir", tmp_path / "scoreboard")

    # when the scoreboard is written
    code = cli.main(["scoreboard"])

    # then the error is printed and the page is written with the week ahead and no watch
    assert code == 0
    assert "also on the calendar: TradingView is down" in capsys.readouterr().err
    written = json.loads((tmp_path / "scoreboard" / "data.json").read_text())
    assert (written["ahead"], written["watch"]) == (ahead, None)
