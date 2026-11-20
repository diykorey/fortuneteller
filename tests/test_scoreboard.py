"""The scoreboard: its data holds what the commands print, and each call its popup's numbers."""

import io
import json
import random
import urllib.request
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, expectations, flows, sources, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.models import DailyBar
from fortuneteller.sources import CORE, NEW_YORK, FirstRelease


@pytest.fixture
def scoreboard_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    out = tmp_path / "scoreboard"
    monkeypatch.setattr(settings, "scoreboard_dir", out)
    monkeypatch.setattr(cli, "week_ahead", lambda con, today, cache_dir: [])
    monkeypatch.setattr(cli, "week_watch", lambda today, cache_dir: [])
    return out


PEOPLE_FEEL = list(study.MVP_PRICE_SERIES)[16:]


def _history(con: duckdb.DuckDBPyConnection) -> None:
    # 60 monthly CPI releases, 2017 to 2021, each with a consensus surprise, the trend given the
    # same one; every market's closes move 0.5% a day, and on a release day the surprise's way 85%
    # of the time, so the moves and surprises come from one set of prices
    rng = random.Random(7)
    # the markets people feel, coffee and the breakeven draw from a stream of their own, so the
    # sixteen keep their prices
    later = random.Random(8)
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
                draw = later if instrument in PEOPLE_FEEL else rng
                move = draw.gauss(0, 0.005)
                if surprise is not None:
                    move = sign * way * 0.05 * surprise + draw.gauss(0, 0.002)
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
        "raw_move": {"cells": 31, "p": 0.01, "by_chance": 0.31},
        "surprise": {"cells": 31, "p": 0.01, "by_chance": 0.31},
        "walk_forward": {"cells": 14, "p": 0.01, "by_chance": 0.14},
    }
    assert data["rules"]["raw_move"] == reports["raw-move"][-1]
    assert (data["data_until"], data["calls"], data["missed"]) == ("2022-01-31", [], [])
    page = (scoreboard_dir / "index.html").read_text()
    assert cli.SCOREBOARD_DATA_MARK not in page
    tags = re.findall(r"<script[^>]*cloud\.umami\.is[^>]*>", page)
    assert len(tags) == 1
    assert 'data-website-id="ed3ca059-ba91-40f1-937c-ace5118ffcb0"' in tags[0]
    assert 'data-do-not-track="true"' in tags[0]
    assert 'data-domains="diykorey.github.io"' in tags[0]
    assert (
        json.loads(
            page.split('<script id="data" type="application/json">')[1].split("</script>")[0]
        )
        == data
    )


def test_the_page_asks_about_each_kind_the_store_answers(
    tmp_db: Path, scoreboard_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a CPI history with prices, moves and surprises, and no FRED key
    monkeypatch.setattr(settings, "fred_api_key", None)
    _history(db.get_connection())

    # when the scoreboard is written
    code = main(["scoreboard"])
    data = json.loads((scoreboard_dir / "data.json").read_text())
    page = (scoreboard_dir / "index.html").read_text()

    # then the page holds the section, CPI's three kinds over three spans on every market, every
    # other flow named with its reason, and no sentence holds a percentage
    assert code == 0
    assert 'id="ask-kind"' in page and 'id="ask-left-out"' in page
    (cpi,) = data["ask"]
    assert [k["kind"] for k in cpi["kinds"]] == ["above", "as expected", "below"]
    assert len(cpi["cells"]) == 3 * 3 * len(study.MVP_PRICE_SERIES)
    assert [entry["name"] for entry in data["ask_left_out"]] == [
        "fomc",
        "nfp",
        "retail",
        "claims",
        "ecb",
        "ceo",
        "opec",
        "boe",
        "boj",
        "war",
        "crypto",
        "weather",
        "flood",
        "earnings",
    ]
    assert all("%" not in cell["say"] for cell in cpi["cells"])


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


def _week() -> tuple[datetime, datetime]:
    start = datetime(2026, 11, 16, tzinfo=study.UTC)
    return start, start + timedelta(days=7)


def test_a_week_s_post_names_each_call_and_its_grade_and_ends_with_the_disclaimer() -> None:
    # given
    start, end = _week()
    at = datetime(2026, 11, 17, 13, 30, 9, tzinfo=study.UTC)
    rows = [
        study.LoggedCall(
            at - timedelta(days=30), "retail", date(2026, 10, 15), 0.8, "UST10Y / ZN", "call", 1
        ),
        study.LoggedCall(at, "retail", date(2026, 11, 17), 0.9, "UST10Y / ZN", "call", 1),
        study.LoggedCall(at, "retail", date(2026, 11, 17), 0.9, "UST5Y / ZF", "call", -1),
        study.LoggedCall(at, "retail", date(2026, 11, 17), 0.9, "DXY", "too_few", 1),
    ]
    grades = {0: "wrong", 1: "right", 3: "right"}

    # when
    lines = cli.weekly_post_lines(rows, grades, start, end, {"UST10Y / ZN": "10-year yield"})

    # then
    assert lines[2:] == [
        "Releases: retail sales 2026-11-17.",
        "retail sales 2026-11-17: 10-year yield up, right.",
        "retail sales 2026-11-17: UST5Y / ZF down, pending.",
        "",
        "The record so far: 1 right, 1 wrong.",
        cli.SCOREBOARD_URL,
        "An entertainment tool, not advice.",
    ]


def test_a_week_without_a_call_says_so() -> None:
    # given
    start, end = _week()
    rows = [
        study.LoggedCall(
            datetime(2026, 11, 19, 13, 30, tzinfo=study.UTC),
            "claims",
            date(2026, 11, 19),
            220,
            "DXY",
            "silent",
        ),
    ]

    # when
    lines = cli.weekly_post_lines(rows, {}, start, end, {})

    # then
    assert "No call this week." in lines and "The record so far: 0 right, 0 wrong." in lines


def test_the_last_full_week_ends_on_the_sunday_before() -> None:
    # given
    sunday_night = datetime(2026, 11, 22, 23, 0, tzinfo=study.UTC)
    monday = datetime(2026, 11, 23, 1, 0, tzinfo=study.UTC)

    # when
    weeks = [study.last_full_week(sunday_night), study.last_full_week(monday)]

    # then
    assert [w[0].date() for w in weeks] == [date(2026, 11, 9), date(2026, 11, 16)]


def test_a_week_across_a_month_s_first_is_asked_in_two_parts_and_the_larger_kept() -> None:
    # given
    start = datetime(2026, 11, 30, tzinfo=study.UTC)
    end = start + timedelta(days=7)
    asked: list[tuple[datetime, datetime]] = []

    def ask(a: datetime, b: datetime) -> int:
        asked.append((a, b))
        return 30 if a == start else 45

    # when
    visitors = study.week_visitors(start, end, ask)

    # then
    first = datetime(2026, 12, 1, tzinfo=study.UTC)
    assert visitors == (45, True) and asked == [(start, first), (first, end)]


def test_a_week_inside_one_month_is_asked_once() -> None:
    # given
    start, end = _week()

    # when
    visitors = study.week_visitors(start, end, lambda a, b: 12)

    # then
    assert visitors == (12, False)


def test_visitors_are_asked_through_the_share_link_with_its_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given Umami answering the share link with a site and token, then the stats with a count
    seen: list[urllib.request.Request] = []
    replies = [
        {"websiteId": "site-1", "token": "signed"},
        {"pageviews": 9, "visitors": 4, "visits": 5},
    ]

    def answer(request: urllib.request.Request, timeout: float) -> io.BytesIO:
        seen.append(request)
        return io.BytesIO(json.dumps(replies[len(seen) - 1]).encode())

    monkeypatch.setattr(sources.urllib.request, "urlopen", answer)
    start, end = _week()

    # when
    visitors = sources.fetch_umami_visitors("code", start, end)

    # then the week's distinct visitors come back, asked over the exact range in milliseconds UTC
    assert visitors == 4
    assert seen[0].full_url == "https://cloud.umami.is/analytics/eu/api/share/code"
    stats = seen[1]
    assert stats.full_url == (
        "https://cloud.umami.is/analytics/eu/api/websites/site-1/stats"
        f"?startAt={int(start.timestamp() * 1000)}&endAt={int(end.timestamp() * 1000)}"
    )
    assert stats.get_header("X-umami-share-token") == "signed"
    assert stats.get_header("X-umami-share-context") == "1"


def test_a_share_link_without_a_token_is_an_umami_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # given a share link that no longer answers with a token
    monkeypatch.setattr(
        sources.urllib.request, "urlopen", lambda request, timeout: io.BytesIO(b"{}")
    )
    start, end = _week()

    # when / then
    with pytest.raises(sources.UmamiError, match="cannot be read"):
        sources.fetch_umami_visitors("code", start, end)


def test_the_page_carries_a_link_preview_whose_image_is_published_beside_it() -> None:
    # given the page's template and the published folder
    page = (Path(cli.__file__).parent / "scoreboard.html").read_text()
    image = Path(__file__).parent.parent / "docs" / "scoreboard" / "preview.png"

    # when its head's preview tags are read
    tags = dict(re.findall(r'<meta (?:property|name)="([^"]+)" content="([^"]*)">', page))

    # then a reader's link shows the title, a line and the image, which is a 1200 by 627 PNG
    url = "https://diykorey.github.io/fortuneteller/scoreboard/"
    assert tags["og:url"] == url
    assert tags["og:image"] == url + "preview.png"
    assert tags["og:title"] and tags["og:description"] and tags["description"]
    assert tags["twitter:card"] == "summary_large_image"
    head = image.read_bytes()[:24]
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    assert (int.from_bytes(head[16:20]), int.from_bytes(head[20:24])) == (1200, 627)
    assert "%" not in tags["og:description"] + tags["description"]


def test_the_page_asks_first_and_a_link_can_pick_the_kind() -> None:
    # given the page's template
    page = (Path(cli.__file__).parent / "scoreboard.html").read_text()

    # when its sections and its script are read
    ask = page.index('<h2 id="ask-the-fortune-teller">')

    # then the ask comes before the week ahead, and #ask/FLOW/KIND picks a kind and is kept
    assert ask < page.index("<h2>The week ahead</h2>")
    assert "#ask\\/([^/]+)\\/(.+)$" in page
    assert "history.replaceState(null, '', '#ask/'" in page
