"""The scoreboard: its data holds what the commands print, and each call its popup's numbers."""

import json
import random
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, expectations, flows, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.models import DailyBar
from fortuneteller.sources import CORE, NEW_YORK, FirstRelease


@pytest.fixture
def scoreboard_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    out = tmp_path / "scoreboard"
    monkeypatch.setattr(settings, "scoreboard_dir", out)
    return out


def _history(con: duckdb.DuckDBPyConnection) -> None:
    # 60 monthly CPI releases, 2017 to 2021, each with a consensus surprise, the trend given the
    # same one; every market's closes move 0.5% a day, and on a release day the surprise's way 85%
    # of the time, so the moves and surprises come from one set of prices
    rng = random.Random(7)
    releases = []
    for i in range(60):
        year, month = 2017 + i // 12, i % 12 + 1
        released = date(year + month // 12, month % 12 + 1, 14)
        while released.weekday() >= 5:
            released += timedelta(days=1)
        releases.append(FirstRelease(date(year, month, 1), released, 1.0))
    flows.store_releases(flows.CPI_FLOW, releases, con=con)
    events = flows.stored_events(flows.CPI_FLOW, con=con)
    surprises = {flows.release_date(e): round(rng.gauss(0, 0.15), 2) for e in events}
    day, prices, bars = date(2016, 12, 1), dict.fromkeys(study.MVP_PRICE_SERIES, 100.0), []
    while day < date(2022, 2, 1):
        if day.weekday() < 5:
            surprise, way = surprises.get(day), 1 if rng.random() < 0.85 else -1
            for instrument, series in study.MVP_PRICE_SERIES.items():
                sign = flows.EXPECTED_SIGN[instrument] or 1
                move = rng.gauss(0, 0.005)
                if surprise is not None:
                    move = sign * way * 0.05 * surprise + rng.gauss(0, 0.002)
                price = prices[instrument]
                prices[instrument] = (
                    price + move * 10 if series.unit == "bps" else price * (1 + move)
                )
                bars.append(
                    DailyBar(instrument=instrument, day=day, close=prices[instrument], source="s")
                )
        day += timedelta(days=1)
    db.insert_models("daily_bars", bars, con=con)
    study.store_observations(con=con)
    for e in events:
        for baseline in (expectations.NASDAQ_CONSENSUS, expectations.TREND_12M):
            con.execute(
                "INSERT INTO surprises VALUES (?, ?, ?, 0.3, 0, ?)",
                [e.event_id, CORE, baseline, surprises[flows.release_date(e)]],
            )


def _table(out: list[str], header: str) -> dict[str, list[str]]:
    # The rows under the first line starting with ``header``, to the next blank line, by market.
    start = next(i for i, line in enumerate(out) if line.startswith(header)) + 1
    rows = {}
    for line in out[start:]:
        if not line:
            break
        if line[:12].strip() in study.MVP_PRICE_SERIES:
            rows[line[:12].strip()] = line[12:].split()
    return rows


def test_the_scoreboard_holds_what_the_commands_print(
    tmp_db: Path, scoreboard_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a CPI history with prices, moves and surprises
    _history(db.get_connection())

    # when the scoreboard is written, and the three commands run on the same store
    code = main(["scoreboard"])
    data = json.loads((scoreboard_dir / "data.json").read_text())
    reports = {}
    for command in ("raw-move", "surprise", "predict"):
        capsys.readouterr()
        assert main([command, "--event", "cpi"]) == 0
        reports[command] = capsys.readouterr().out.splitlines()

    # then the one event's verdicts and records are the commands' lines, cell by cell, the page
    # embeds the data, and the chance count is the cells at the bar
    assert code == 0
    (cpi,) = data["events"]
    assert (cpi["name"], cpi["releases"], cpi["first"]) == ("cpi", 60, "2017-02-14")
    raw = _table(reports["raw-move"], "instrument   CPI days")
    for market, cell in cpi["raw_move"].items():
        assert raw[market][-3:] == [f"{cell['ratio']:.2f}", f"{cell['p']:.4f}", cell["verdict"]]
    assert (cpi["surprise"]["measure"], cpi["surprise"]["against"]) == (
        "core",
        "the 12-month trend",
    )
    tracking = _table(reports["surprise"], "instrument   n    expected")
    for market, link in cpi["surprise"]["links"].items():
        tokens = tracking[market]
        assert tokens[:4] == [
            str(link["n"]),
            link["expected"],
            f"{link['rank_corr']:.2f}",
            f"{link['p']:.4f}",
        ]
        assert tokens[-1] == link["verdict"]
    assert cpi["walk_forward"]["against"] == "Nasdaq's consensus"
    graded = _table(reports["predict"], "walk-forward (all)")
    for market, link in cpi["walk_forward"]["links"].items():
        tokens = graded[market]
        assert tokens[:4] == [
            link["expected"],
            link["first"] or "—",
            str(link["predictions"]),
            str(link["right"]),
        ]
        assert " ".join(tokens[7:]) == link["verdict"]
    assert "GC / XAU" not in cpi["walk_forward"]["links"]
    assert data["chance"] == {
        "raw_move": {"cells": 16, "p": 0.01, "by_chance": 0.16},
        "surprise": {"cells": 16, "p": 0.01, "by_chance": 0.16},
        "walk_forward": {"cells": 11, "p": 0.01, "by_chance": 0.11},
    }
    assert data["rules"]["raw_move"] == reports["raw-move"][-1]
    assert (data["data_until"], data["calls"], data["missed"]) == ("2022-01-31", [], [])
    page = (scoreboard_dir / "index.html").read_text()
    assert cli.SCOREBOARD_DATA_MARK not in page
    assert (
        json.loads(
            page.split('<script id="data" type="application/json">')[1].split("</script>")[0]
        )
        == data
    )


def _at(monkeypatch: pytest.MonkeyPatch, day: date) -> None:
    # The clock at 09:00 New York on ``day``, and both calendars' consensus at 0.2 for its release.
    now = datetime.combine(day, time(9, 0), tzinfo=NEW_YORK)
    monkeypatch.setattr(cli, "_now", lambda: now)
    monkeypatch.setattr(
        expectations,
        "next_consensus",
        lambda measure, today, cache_dir: expectations.NextConsensus(day, 0.2, 0.2),
    )


def _release(con: duckdb.DuckDBPyConnection, day: date, moves: dict[str, float]) -> None:
    # A CPI release on ``day``, its first print 0.3 against the consensus 0.2, and its moves.
    month = (day.replace(day=1) - timedelta(days=1)).replace(day=1)
    flows.store_releases(flows.CPI_FLOW, [FirstRelease(month, day, 0.3)], con=con)
    event = flows.stored_events(flows.CPI_FLOW, con=con)[-1]
    con.execute(
        "INSERT INTO surprises VALUES (?, ?, ?, 0.3, 0.2, 0.1)",
        [event.event_id, CORE, expectations.NASDAQ_CONSENSUS],
    )
    for instrument, move in moves.items():
        con.execute(
            "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
            "VALUES (?, ?, 'pct', ?)",
            [event.event_id, instrument, move],
        )


def test_a_call_row_carries_its_popup_s_numbers_and_its_grade(
    tmp_db: Path,
    scoreboard_dir: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the CPI history; a release called live, then loaded with stocks down and the dollar
    # down; a later one called but not loaded; and one in between never logged
    con = db.get_connection()
    _history(con)
    called, unlogged, unloaded = date(2026, 10, 14), date(2026, 11, 12), date(2027, 1, 13)
    _at(monkeypatch, called)
    assert main(["predict", "--event", "cpi", "--actual", "0.3"]) == 0
    popup = {
        m.group(1).strip(): m.groups()[1:]
        for m in (
            re.match(
                r"(\S.{10}) +(up|down) +closes \w+ today: right on (\d+) of (\d+) calls before, (.*)",
                line,
            )
            for line in capsys.readouterr().out.splitlines()
        )
        if m
    }
    _release(con, called, {"SPY / ES": -0.004, "UST10Y / ZN": 5.0, "DXY": -0.002})
    _release(con, unlogged, {})
    _at(monkeypatch, unloaded)
    assert main(["predict", "--event", "cpi", "--actual", "0.3"]) == 0
    capsys.readouterr()

    # when the scoreboard is written
    code = main(["scoreboard"])
    data = json.loads((scoreboard_dir / "data.json").read_text())

    # then each called row shows the popup's direction, record and band, graded on its close; a row
    # whose release is not loaded is pending with score's note; the unlogged release is missed; and
    # no row carries a probability
    assert code == 0
    assert "SPY / ES" in popup and "DXY" in popup
    rows = {(r["day"], r["market"]): r for r in data["calls"]}
    for market, (direction, right, calls, band) in popup.items():
        row = rows[(called.isoformat(), market.strip())]
        assert (row["direction"], row["record"], row["band"]) == (
            direction,
            {"right": int(right), "calls": int(calls)},
            band,
        )
    grades = {m: rows[(called.isoformat(), m)]["grade"] for m in ("SPY / ES", "UST10Y / ZN", "DXY")}
    assert grades == {"SPY / ES": "right", "UST10Y / ZN": "right", "DXY": "wrong"}
    assert rows[(called.isoformat(), "VIX")]["grade"] == "pending"
    later = rows[(unloaded.isoformat(), "SPY / ES")]
    assert (later["grade"], later["note"]) == (
        "pending",
        "cpi 2027-01-13: the release is not loaded",
    )
    assert data["missed"] == [{"event": "cpi", "day": "2026-11-12"}]
    assert not any("probability" in r for r in data["calls"])
    assert "%" not in json.dumps(rows[(called.isoformat(), "UST10Y / ZN")])


def test_a_silent_row_has_no_record_or_grade(
    tmp_db: Path, scoreboard_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and a release whose VIX link was silent
    con = db.get_connection()
    _history(con)
    day = date(2026, 10, 14)
    _release(con, day, {"VIX": 0.01})
    when = datetime.combine(day, time(9, 0), tzinfo=NEW_YORK)
    study.append_calls(
        settings.calls_path, [study.LoggedCall(when, "cpi", day, 0.3, "VIX", study.SILENT)]
    )
    monkeypatch.setattr(cli, "_now", lambda: when)

    # when the scoreboard is written
    code = main(["scoreboard"])
    data = json.loads((settings.scoreboard_dir / "data.json").read_text())

    # then the row says silent and nothing else
    assert code == 0
    (row,) = data["calls"]
    assert (row["outcome"], row["direction"], row["record"], row["band"], row["grade"]) == (
        "silent",
        None,
        None,
        None,
        None,
    )


def test_scoreboard_asks_for_the_loads_it_needs(
    tmp_db: Path, scoreboard_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given nothing stored

    # when the scoreboard is asked for
    code = main(["scoreboard"])

    # then it names the loads to run and writes nothing
    assert code == 1
    assert "load-releases" in capsys.readouterr().err
    assert not scoreboard_dir.exists()
