"""Rung 2's walk-forward: each release predicted only from the releases before it."""

import random
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, expectations, flows, sources, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import CORE, NEW_YORK, CalendarError, FirstRelease
from fortuneteller.stats import binomial_p
from fortuneteller.study import (
    DOESNT_HOLD,
    HOLDS,
    TOO_FEW,
    Prediction,
    grade,
    is_open,
    walk_forward,
)

STEP = 0.1


def _releases(count: int, follows: float, seed: int = 11) -> list[tuple[int, str, float, float]]:
    # Surprises around zero; each move goes the surprise's way with probability ``follows``, its size
    # in proportion to the surprise, plus a little noise.
    rng = random.Random(seed)
    releases = []
    for i in range(count):
        surprise = round(rng.gauss(0, 0.15), 2)
        way = 1 if rng.random() < follows else -1
        releases.append((i, f"r{i}", surprise, way * 0.01 * surprise + rng.gauss(0, 0.0002)))
    return releases


def test_a_link_that_follows_80_percent_of_surprises_opens_and_grades_near_80() -> None:
    # given 200 releases whose moves follow 80% of surprises
    releases = _releases(200, 0.8)

    # when they are replayed
    predictions = walk_forward(releases, expected_sign=1, step=STEP)

    # then it predicts most noticeable releases, and is right about 80% of the time
    noticeable = sum(abs(r[2]) >= STEP for r in releases)
    right = sum(p.right for p in predictions) / len(predictions)
    assert len(predictions) > 0.7 * noticeable
    assert 0.7 < right < 0.9


def test_a_link_with_no_relation_rarely_opens() -> None:
    # given 200 releases whose moves ignore the surprise
    rng = random.Random(5)
    releases = [(i, f"r{i}", round(rng.gauss(0, 0.15), 2), rng.gauss(0, 0.01)) for i in range(200)]

    # when they are replayed
    predictions = walk_forward(releases, expected_sign=1, step=STEP)

    # then it stays silent on almost every release
    noticeable = sum(abs(r[2]) >= STEP for r in releases)
    assert len(predictions) < 0.1 * noticeable


def test_each_decision_uses_only_the_releases_before_it() -> None:
    # given releases that follow 80% of surprises
    releases = _releases(120, 0.8)

    # when they are replayed
    predicted = {p.event_id for p in walk_forward(releases, expected_sign=1, step=STEP)}

    # then every noticeable release is predicted exactly when the link is open on those before it
    for i, (event_id, _month, surprise, _move) in enumerate(releases):
        if abs(surprise) < STEP:
            continue
        earlier = releases[:i]
        expected = is_open([e[2] for e in earlier], [e[3] for e in earlier], 1, STEP)
        assert (event_id in predicted) == expected, event_id


def test_nothing_at_or_after_a_release_changes_its_call() -> None:
    # given releases near the gate's bars (moves follow 70% of surprises); for each noticeable
    # release, two versions: its own move with its surprise, or against it, and new releases after
    releases = _releases(70, 0.7, seed=4)
    rng = random.Random(9)
    tail = [(70 + i, f"r{70 + i}", rng.gauss(0, 0.3), rng.gauss(0, 0.01)) for i in range(5)]

    def called(versions: list[tuple[int, str, float, float]], at: int) -> tuple[int, ...]:
        return tuple(p.direction for p in walk_forward(versions, 1, STEP) if p.event_id == at)

    # when each is replayed
    differing = []
    for event_id, month, surprise, move in releases:
        if abs(surprise) < STEP:
            continue
        size = abs(move) + 0.01
        before = releases[:event_id]
        with_it = called([*before, (event_id, month, surprise, size * surprise), *tail], event_id)
        against = called([*before, (event_id, month, surprise, -size * surprise), *tail], event_id)
        if with_it != against:
            differing.append(event_id)

    # then no release's call depends on its own move or on anything after it
    assert differing == []


def test_a_link_with_too_little_history_is_closed() -> None:
    # given no earlier releases, or only small surprises
    # when / then the gate stays closed
    assert not is_open([], [], 1, STEP)
    assert not is_open([0.01, 0.02, 0.03], [0.1, 0.2, 0.3], 1, STEP)


def test_a_link_expected_to_fall_predicts_against_the_surprise() -> None:
    # given 150 releases whose moves go against 80% of surprises, as stocks on a hot CPI print
    releases = [(i, m, s, -move) for i, m, s, move in _releases(150, 0.8)]

    # when they are replayed with an expected sign of -1
    predictions = walk_forward(releases, expected_sign=-1, step=STEP)

    # then each call is the opposite of the surprise's sign, and mostly right
    assert predictions
    assert all(p.direction == (-1 if p.surprise > 0 else 1) for p in predictions)
    assert sum(p.right for p in predictions) / len(predictions) > 0.7


def test_the_binomial_p_is_the_chance_a_coin_does_as_well() -> None:
    # given a few records
    # when / then the one-sided chance of doing at least as well with a fair coin
    assert binomial_p(10, 10) == 1 / 1024
    assert binomial_p(5, 10) == 638 / 1024
    assert binomial_p(0, 0) == 1.0


def _made(rights: int, wrongs: int) -> list[Prediction]:
    # Every prediction says up; the right ones' moves are up, the wrong ones' down.
    return [Prediction(i, "2020-01", 0.2, 1, 0.01) for i in range(rights)] + [
        Prediction(rights + i, "2020-01", 0.2, 1, -0.01) for i in range(wrongs)
    ]


@pytest.mark.parametrize(
    ("rights", "wrongs", "verdict"),
    [(20, 5, TOO_FEW), (40, 10, HOLDS), (340, 260, DOESNT_HOLD), (33, 17, DOESNT_HOLD)],
)
def test_a_link_holds_only_on_enough_predictions_right_often_enough(
    rights: int, wrongs: int, verdict: str
) -> None:
    # given a record: too short; 80% of 50; 57% of 600, significant but under 60%; 66% of 50,
    # over 60% but not significant (p 0.016)
    # when it is graded
    g = grade(_made(rights, wrongs), expected_sign=1)

    # then the verdict follows the rule
    assert (g.predictions, g.right, g.verdict) == (rights + wrongs, rights, verdict)


def test_the_baseline_is_the_expected_direction_whatever_the_surprise() -> None:
    # given four calls of a link expected to rise: two say down on a falling day, two up on rising
    made = [
        Prediction(1, "m", -0.2, -1, -0.01),
        Prediction(2, "m", -0.2, -1, -0.01),
        Prediction(3, "m", 0.2, 1, 0.01),
        Prediction(4, "m", 0.2, 1, 0.01),
    ]

    # when it is graded
    g = grade(made, expected_sign=1)

    # then the link was right on all four, always saying up only on two
    assert (g.right, g.always_right, g.first) == (4, 2, "m")


# The markets the synthetic history moves; Europe's have none, so their links stay silent.
US_MARKETS = ("SPY / ES", "UST10Y / ZN", "DXY", "GC / XAU", "VIX")


def _store_consensus_history(con: duckdb.DuckDBPyConnection) -> None:
    # 156 monthly CPI releases, 2010 to 2022, with a consensus surprise; each market follows 85% of them
    # in its expected direction.
    rng = random.Random(3)
    months = [date(2010 + i // 12, i % 12 + 1, 1) for i in range(156)]
    releases = [
        FirstRelease(m, date(m.year + m.month // 12, m.month % 12 + 1, 14), 1.0) for m in months
    ]
    flows.store_releases(flows.CPI_FLOW, releases, con=con)
    for event in flows.stored_events(flows.CPI_FLOW, con=con):
        surprise = round(rng.gauss(0, 0.15), 2)
        con.execute(
            "INSERT INTO surprises VALUES (?, ?, ?, 0, 0, ?)",
            [event.event_id, CORE, expectations.NASDAQ_CONSENSUS, surprise],
        )
        way = 1 if rng.random() < 0.85 else -1
        for instrument in US_MARKETS:
            move = (flows.EXPECTED_SIGN[instrument] or 1) * way * 0.01 * surprise + rng.gauss(
                0, 0.0002
            )
            con.execute(
                "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
                "VALUES (?, ?, 'pct', ?)",
                [event.event_id, instrument, move],
            )


def test_predict_prints_each_link_s_record_and_verdict(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a CPI history whose markets follow 85% of consensus surprises
    _store_consensus_history(db.get_connection())

    # when the walk-forward is printed
    code = main(["predict", "--event", "cpi"])

    # then every link with a direction gets a row in both tables, and the yield holds
    out = capsys.readouterr().out.splitlines()
    out = out[: next(i for i, line in enumerate(out) if line.startswith("holds = "))]
    assert code == 0
    assert (
        out[0]
        == "core against Nasdaq's consensus: each release predicted only from the ones before it"
    )
    assert [line for line in out if line.startswith("walk-forward")] == [
        "walk-forward (all)",
        "walk-forward (without 2020-03 … 2021-04)",
    ]
    rows = [line for line in out if line.startswith("UST10Y / ZN")]
    assert len(rows) == 2 and all(row.endswith(" holds") for row in rows)
    predicted = [int(row.split()[5]) for row in rows]
    assert predicted[0] > predicted[1]
    assert sum(line.startswith(("SPY", "UST10Y", "DXY", "VIX")) for line in out) == 8
    assert not any(line.startswith("GC / XAU") for line in out)


def test_predict_asks_for_the_loads_it_needs(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given nothing stored

    # when the walk-forward is asked for
    code = main(["predict", "--event", "nfp"])

    # then it names the loads to run
    assert code == 1
    assert "load-surprises" in capsys.readouterr().err


def _next(
    monkeypatch: pytest.MonkeyPatch,
    upcoming: expectations.NextConsensus | None,
    at: time = time(9, 0),
    days_before: int = 0,
) -> None:
    # The next release, and the clock at ``at`` New York, ``days_before`` it (its day by default).
    monkeypatch.setattr(expectations, "next_consensus", lambda measure, today, cache_dir: upcoming)
    if upcoming is not None:
        now = datetime.combine(upcoming.day - timedelta(days=days_before), at, tzinfo=NEW_YORK)
        monkeypatch.setattr(cli, "_now", lambda: now)


def test_an_actual_predicts_each_open_link_s_close_and_a_closed_one_is_silent(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, the yield's moves in basis points, but VIX's all the same, so its link
    # cannot open; and a consensus of 0.2 on both calendars for the next release
    con = db.get_connection()
    _store_consensus_history(con)
    con.execute("UPDATE observations SET ret_1d = 0.001 WHERE instrument = 'VIX'")
    con.execute("UPDATE observations SET ret_1d = ret_1d * 10000 WHERE instrument = 'UST10Y / ZN'")
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in hot, at 0.3
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then the surprise is noticeable; stocks are called down, the yield and dollar up, each with
    # its record as counts and its band in its own unit, no percentage; VIX is silent
    assert code == 0
    assert capsys.readouterr().out.splitlines() == [
        "core on 2026-11-12: actual 0.3, Nasdaq's consensus 0.2, surprise +0.1",
        "SPY / ES     down   closes down today: right on 70 of 79 calls before, -0.11% to -0.08%",
        "UST10Y / ZN  up     closes up today: right on 70 of 79 calls before, +8.6 bp to +11.2 bp",
        "DXY          up     closes up today: right on 70 of 79 calls before, +0.08% to +0.11%",
        "VIX          —      silent: the link does not pass on the releases so far",
        "DAX          —      silent: the link does not pass on the releases so far",
        "SX5E         —      silent: the link does not pass on the releases so far",
        "EURUSD       —      silent: the link does not pass on the releases so far",
        "COMP         —      silent: the link does not pass on the releases so far",
        "UST5Y / ZF   —      silent: the link does not pass on the releases so far",
        "UKX          —      silent: the link does not pass on the releases so far",
        "SXXP         —      silent: the link does not pass on the releases so far",
        "record = the link's calls so far, walk-forward; band = where half its moves land; "
        "both graded by `fortuneteller predict --event cpi`",
        f"logged 11 rows to {settings.calls_path}",
    ]


def test_without_nasdaq_s_consensus_tradingview_s_forecast_is_taken_and_named(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, and a next release Nasdaq has no consensus for, TradingView 0.2
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), None, 0.2))

    # when the release comes in at 0.3
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then the surprise is against TradingView's forecast, named, and the rows are logged
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (
        "core on 2026-11-12: actual 0.3, TradingView's forecast (Nasdaq has none) 0.2, "
        "surprise +0.1"
    )
    assert out[-1] == f"logged 11 rows to {settings.calls_path}"


def _tradingview_reads(
    monkeypatch: pytest.MonkeyPatch, actuals: list[float | None], at: time = time(8, 30)
) -> list[float]:
    # TradingView's actual on successive reads (the last one repeated), a clock from ``at`` on the
    # release day that the waits advance, and the waits made.
    clock = [datetime.combine(date(2026, 11, 12), at, tzinfo=NEW_YORK)]
    waits: list[float] = []
    reads = iter(actuals)

    def read(measure: str, day: date, cache_dir: Path) -> float | None:
        return next(reads, actuals[-1])

    def wait(seconds: float) -> None:
        waits.append(seconds)
        clock[0] += timedelta(seconds=seconds)

    monkeypatch.setattr(expectations, "published_actual", read)
    monkeypatch.setattr(cli, "_now", lambda: clock[0])
    monkeypatch.setattr(cli, "_sleep", wait)
    return waits


def test_fetch_waits_for_tradingview_s_actual_and_calls_on_it(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, a consensus of 0.2, and TradingView's actual empty twice, then 0.3
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    waits = _tradingview_reads(monkeypatch, [None, None, 0.3])

    # when the release is fetched from 08:30
    code = main(["predict", "--event", "cpi", "--fetch"])

    # then it reads every 15 seconds, names where the actual came from, and calls and logs as typed
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert waits == [15, 15]
    assert out[:2] == [
        "actual 0.3 from TradingView at 08:30:30 New York",
        "core on 2026-11-12: actual 0.3, Nasdaq's consensus 0.2, surprise +0.1",
    ]
    assert out[-1] == f"logged 11 rows to {settings.calls_path}"
    assert [row.actual for row in study.read_calls(settings.calls_path)] == [0.3] * 11


def test_fetch_gives_up_half_an_hour_after_the_release(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and TradingView never showing the actual
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    waits = _tradingview_reads(monkeypatch, [None])

    # when the release is fetched from 08:30
    code = main(["predict", "--event", "cpi", "--fetch"])

    # then it stops at 09:00, says to type the actual, and logs nothing
    captured = capsys.readouterr()
    assert code == 1
    assert sum(waits) == 30 * 60
    assert "no actual for core on 2026-11-12 by 09:00 New York; type it with --actual" in (
        captured.err
    )
    assert not settings.calls_path.exists()


def test_fetch_before_the_release_refuses_without_reading(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, and the clock at 08:29 on the release day
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    waits = _tradingview_reads(monkeypatch, [0.3], at=time(8, 29))

    # when the release is fetched
    code = main(["predict", "--event", "cpi", "--fetch"])

    # then it refuses, naming the release time, and waits for nothing
    assert code == 1
    assert waits == []
    assert "--fetch reads core on 2026-11-12 from its release at 08:30" in capsys.readouterr().err


def _core_released_on(monkeypatch: pytest.MonkeyPatch, core_day: date) -> None:
    # Core CPI's next release on ``core_day``; every other measure's a month after it.
    def upcoming(measure: str, today: date, cache_dir: Path) -> expectations.NextConsensus:
        day = core_day if measure == "core" else core_day + timedelta(days=30)
        return expectations.NextConsensus(day, 0.2, 0.2)

    monkeypatch.setattr(expectations, "next_consensus", upcoming)


def test_live_fetches_and_logs_the_release_of_the_day(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, CPI released today and TradingView's actual empty once, then 0.3
    _store_consensus_history(db.get_connection())
    _core_released_on(monkeypatch, date(2026, 11, 12))
    _tradingview_reads(monkeypatch, [None, 0.3])

    # when the release-day job's command runs at 08:30
    code = main(["live"])

    # then CPI alone is fetched, called and logged, and the last line counts the rows not silent
    out = capsys.readouterr().out.splitlines()
    rows = study.read_calls(settings.calls_path)
    spoke = sum(row.outcome != study.SILENT for row in rows)
    assert code == 0
    assert out[:2] == [
        "live: cpi is released today",
        "actual 0.3 from TradingView at 08:30:15 New York",
    ]
    assert {row.flow for row in rows} == {"cpi"}
    assert spoke and out[-1] == f"live: {len(rows)} rows logged today, {spoke} not silent"


def test_live_on_a_day_without_a_release_does_nothing(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and no release before tomorrow
    _store_consensus_history(db.get_connection())
    _core_released_on(monkeypatch, date(2026, 11, 13))
    waits = _tradingview_reads(monkeypatch, [0.3])

    # when the release-day job's command runs
    code = main(["live"])

    # then it says so, reads no actual and logs nothing
    assert code == 0
    assert capsys.readouterr().out == "live: no release today (2026-11-12)\n"
    assert waits == []
    assert not settings.calls_path.exists()


def test_live_leaves_a_release_already_logged_alone(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given CPI released today and already logged by hand
    _store_consensus_history(db.get_connection())
    _core_released_on(monkeypatch, date(2026, 11, 12))
    waits = _tradingview_reads(monkeypatch, [0.3])
    at = datetime(2026, 11, 12, 13, 31, tzinfo=UTC)
    study.append_calls(
        settings.calls_path,
        [study.LoggedCall(at, "cpi", date(2026, 11, 12), 0.3, "VIX", study.SILENT)],
    )

    # when the release-day job's command runs again
    code = main(["live"])

    # then it reads nothing, logs nothing more, does not fail, and still sums up the day's rows
    assert code == 0
    assert capsys.readouterr().out == (
        f"live: cpi is already in {settings.calls_path}\nlive: 1 row logged today, all silent\n"
    )
    assert waits == []
    assert len(study.read_calls(settings.calls_path)) == 1


def test_live_before_the_release_time_waits_for_the_timer(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given CPI released today and the clock at 03:00 New York, a run the timer caught up at login
    _store_consensus_history(db.get_connection())
    _core_released_on(monkeypatch, date(2026, 11, 12))
    waits = _tradingview_reads(monkeypatch, [0.3], at=time(3, 0))

    # when the release-day job's command runs
    code = main(["live"])

    # then it reads nothing, logs nothing, and does not fail
    assert code == 0
    assert capsys.readouterr().out == "live: before 08:30 New York; the timer runs it then\n"
    assert waits == []
    assert not settings.calls_path.exists()


def test_live_fails_when_the_release_of_the_day_brings_no_actual(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, CPI released today and TradingView never showing the actual
    _store_consensus_history(db.get_connection())
    _core_released_on(monkeypatch, date(2026, 11, 12))
    _tradingview_reads(monkeypatch, [None])

    # when the release-day job's command runs
    code = main(["live"])

    # then it fails, so the job reports it, and logs nothing
    assert code == 1
    assert "type it with --actual" in capsys.readouterr().err
    assert not settings.calls_path.exists()


def test_live_fails_when_a_calendar_cannot_be_read(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a calendar that cannot be read
    def unreadable(measure: str, today: date, cache_dir: Path) -> None:
        raise CalendarError("TradingView's calendar answered 503")

    monkeypatch.setattr(expectations, "next_consensus", unreadable)
    _tradingview_reads(monkeypatch, [None])

    # when the release-day job's command runs
    code = main(["live"])

    # then it fails, naming the calendar's error, since a release today cannot be ruled out
    assert code == 1
    assert "live: cpi: TradingView's calendar answered 503" in capsys.readouterr().err


def test_a_small_surprise_predicts_nothing(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and a consensus of 0.2
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in at 0.25
    code = main(["predict", "--event", "cpi", "--actual", "0.25"])

    # then it says why there is no prediction
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[1:] == [
        "no prediction: the surprise is under 0.1pp",
        f"logged 11 rows to {settings.calls_path}",
    ]


@pytest.mark.parametrize(
    ("upcoming", "reason"),
    [
        (None, "no core release with a consensus from"),
        (
            expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.5),
            "the calendars disagree for core on 2026-11-12: Nasdaq 0.2, TradingView 0.5",
        ),
    ],
)
def test_without_a_consensus_to_trust_there_is_no_prediction(
    upcoming: expectations.NextConsensus | None,
    reason: str,
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the CPI history, and no next release, or calendars far apart
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, upcoming)

    # when an actual is typed in
    code = main(["predict", "--event", "cpi", "--actual", "0.6"])

    # then nothing is predicted, and the reason is given
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert reason in captured.err


def test_a_calendar_that_cannot_be_read_is_reported(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, and TradingView failing
    _store_consensus_history(db.get_connection())

    def fail(measure: str, today: date, cache_dir: Path) -> None:
        raise CalendarError("TradingView did not answer")

    monkeypatch.setattr(expectations, "next_consensus", fail)

    # when an actual is typed in
    code = main(["predict", "--event", "cpi", "--actual", "0.6"])

    # then the failure is reported
    assert code == 1
    assert "predict: TradingView did not answer" in capsys.readouterr().err


def test_predict_grades_each_link_s_stated_confidence(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a CPI history whose markets follow 85% of consensus surprises
    _store_consensus_history(db.get_connection())

    # when the walk-forward is printed
    code = main(["predict", "--event", "cpi"])

    # then after rung 2's tables come the confidence, calibration and size tables, with and without
    # COVID; every link, right on 85% and stating about that, is honest; and the rule is printed
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert [
        line for line in out if line.startswith(("confidence (", "calibration (", "hit rate"))
    ] == [
        "confidence (all)",
        "calibration (all)",
        "hit rate by surprise size, calls with a probability (all)",
        "confidence (without 2020-03 … 2021-04)",
        "calibration (without 2020-03 … 2021-04)",
        "hit rate by surprise size, calls with a probability (without 2020-03 … 2021-04)",
    ]
    start = out.index("confidence (all)")
    rows = out[start + 2 : start + 6]
    assert [row.split()[0] for row in rows] == ["SPY", "UST10Y", "DXY", "VIX"]
    assert all(row.endswith(" honest") for row in rows)
    start = out.index("confidence (without 2020-03 … 2021-04)")
    assert all(row.endswith(" honest") for row in out[start + 2 : start + 6])
    start = out.index("confidence verdict (honest only if honest with and without COVID)")
    assert out[start + 1 : start + 12] == [
        "SPY / ES     honest",
        "UST10Y / ZN  honest",
        "DXY          honest",
        "VIX          honest",
        "DAX          too few",
        "SX5E         too few",
        "EURUSD       too few",
        "COMP         too few",
        "UST5Y / ZF   too few",
        "UKX          too few",
        "SXXP         too few",
    ]
    assert out[start + 13].startswith("honest = on at least 30 calls with a probability")


def test_an_open_link_with_too_few_calls_so_far_calls_without_a_probability(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, but a probability asked for only after 1,000 earlier calls
    _store_consensus_history(db.get_connection())
    monkeypatch.setattr(study, "MIN_CALLS", 1000)
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in hot
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then each link calls its direction and says why there is no probability
    assert code == 0
    assert capsys.readouterr().out.splitlines()[1:] == [
        "SPY / ES     down   closes down today; too few calls so far",
        "UST10Y / ZN  up     closes up today; too few calls so far",
        "DXY          up     closes up today; too few calls so far",
        "VIX          up     closes up today; too few calls so far",
        "DAX          —      silent: the link does not pass on the releases so far",
        "SX5E         —      silent: the link does not pass on the releases so far",
        "EURUSD       —      silent: the link does not pass on the releases so far",
        "COMP         —      silent: the link does not pass on the releases so far",
        "UST5Y / ZF   —      silent: the link does not pass on the releases so far",
        "UKX          —      silent: the link does not pass on the releases so far",
        "SXXP         —      silent: the link does not pass on the releases so far",
        "record = the link's calls so far, walk-forward; band = where half its moves land; "
        "both graded by `fortuneteller predict --event cpi`",
        f"logged 11 rows to {settings.calls_path}",
    ]


def test_an_actual_logs_each_link_s_line_as_printed(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, the yield in basis points and VIX's link unable to open
    con = db.get_connection()
    _store_consensus_history(con)
    con.execute("UPDATE observations SET ret_1d = 0.001 WHERE instrument = 'VIX'")
    con.execute("UPDATE observations SET ret_1d = ret_1d * 10000 WHERE instrument = 'UST10Y / ZN'")
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in hot
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then the log holds one row per link with what was printed, and says so
    calls = study.read_calls(settings.calls_path)
    assert code == 0
    assert capsys.readouterr().out.splitlines()[-1] == f"logged 11 rows to {settings.calls_path}"
    assert [(c.flow, c.day, c.actual) for c in calls] == [("cpi", date(2026, 11, 12), 0.3)] * 11
    assert [(c.instrument, c.outcome, c.direction) for c in calls] == [
        ("SPY / ES", study.CALLED, -1),
        ("UST10Y / ZN", study.CALLED, 1),
        ("DXY", study.CALLED, 1),
        ("VIX", study.SILENT, None),
        ("DAX", study.SILENT, None),
        ("SX5E", study.SILENT, None),
        ("EURUSD", study.SILENT, None),
        ("COMP", study.SILENT, None),
        ("UST5Y / ZF", study.SILENT, None),
        ("UKX", study.SILENT, None),
        ("SXXP", study.SILENT, None),
    ]
    yield_call = calls[1]
    assert yield_call.probability is not None and round(yield_call.probability, 2) == 0.88
    assert yield_call.band is not None
    assert (round(yield_call.band[0], 1), round(yield_call.band[1], 1)) == (8.6, 11.2)
    assert calls[3].probability is None and calls[3].band is None
    assert all(c.logged_at == datetime(2026, 11, 12, 14, 0, tzinfo=UTC) for c in calls)


def test_a_small_surprise_logs_every_link_as_small(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and a consensus of 0.2
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in at 0.25
    main(["predict", "--event", "cpi", "--actual", "0.25"])

    # then each link with a direction is logged, with no call
    calls = study.read_calls(settings.calls_path)
    assert [(c.instrument, c.outcome, c.direction) for c in calls] == [
        ("SPY / ES", study.SMALL, None),
        ("UST10Y / ZN", study.SMALL, None),
        ("DXY", study.SMALL, None),
        ("VIX", study.SMALL, None),
        ("DAX", study.SMALL, None),
        ("SX5E", study.SMALL, None),
        ("EURUSD", study.SMALL, None),
        ("COMP", study.SMALL, None),
        ("UST5Y / ZF", study.SMALL, None),
        ("UKX", study.SMALL, None),
        ("SXXP", study.SMALL, None),
    ]


def test_a_call_with_too_few_calls_before_is_logged_with_its_direction(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, but a probability only after 1,000 earlier calls
    _store_consensus_history(db.get_connection())
    monkeypatch.setattr(study, "MIN_CALLS", 1000)
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))

    # when the release comes in hot
    main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then each link's call is logged without a probability or band
    calls = study.read_calls(settings.calls_path)
    assert [(c.outcome, c.direction) for c in calls] == [
        (study.TOO_FEW_CALLS, -1),
        (study.TOO_FEW_CALLS, 1),
        (study.TOO_FEW_CALLS, 1),
        (study.TOO_FEW_CALLS, 1),
        (study.SILENT, None),
        (study.SILENT, None),
        (study.SILENT, None),
        (study.SILENT, None),
        (study.SILENT, None),
        (study.SILENT, None),
        (study.SILENT, None),
    ]
    assert all(c.probability is None and c.band is None for c in calls)


def test_a_release_is_logged_once(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and a release already logged
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    main(["predict", "--event", "cpi", "--actual", "0.3"])
    before = settings.calls_path.read_text()
    capsys.readouterr()

    # when the same release is typed in again, with another actual
    code = main(["predict", "--event", "cpi", "--actual", "0.5"])

    # then it refuses before printing anything, and the log is unchanged
    assert code == 1
    refused = capsys.readouterr()
    assert "already in" in refused.err and refused.out == ""
    assert settings.calls_path.read_text() == before


def test_another_flow_logged_that_day_leaves_the_release_its_entry(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, and a jobs report already logged on CPI's day
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    when = datetime(2026, 11, 12, 13, 40, tzinfo=UTC)
    nfp = study.LoggedCall(when, "nfp", date(2026, 11, 12), 151.0, "DXY", study.SILENT)
    study.append_calls(settings.calls_path, [nfp])

    # when CPI's actual is typed in
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then CPI's rows are logged after the jobs report's
    calls = study.read_calls(settings.calls_path)
    assert code == 0
    assert [c.flow for c in calls] == ["nfp"] + ["cpi"] * 11


def test_the_log_reads_back_what_was_written(tmp_path: Path) -> None:
    # given a call with a probability and band, and a silent link
    when = datetime(2026, 11, 6, 13, 31, 5, tzinfo=UTC)
    calls = [
        study.LoggedCall(
            when, "nfp", date(2026, 11, 6), 151.0, "DXY", study.CALLED, 1, 0.64, (-0.0015, 0.0055)
        ),
        study.LoggedCall(when, "nfp", date(2026, 11, 6), 151.0, "SPY / ES", study.SILENT),
    ]

    # when written in two goes and read back
    path = tmp_path / "calls.csv"
    study.append_calls(path, calls[:1])
    study.append_calls(path, calls[1:])

    # then the rows come back as written, under one header
    assert study.read_calls(path) == calls
    assert path.read_text().count("logged_at") == 1


@pytest.mark.parametrize(
    ("at", "days_before"), [(time(9, 0), 1), (time(8, 29), 0)], ids=["day before", "too early"]
)
def test_a_what_if_before_the_release_prints_but_is_not_logged(
    at: time,
    days_before: int,
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given the CPI history, and a clock before the release
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2), at, days_before)

    # when an actual is tried out, twice
    main(["predict", "--event", "cpi", "--actual", "0.3"])
    code = main(["predict", "--event", "cpi", "--actual", "0.4"])

    # then both print their calls, nothing is logged, and the release keeps its entry
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[-1] == "not logged: a release is logged on its day from 08:30 New York"
    assert not settings.calls_path.exists()


def test_an_empty_or_unterminated_log_keeps_its_rows_apart(tmp_path: Path) -> None:
    # given an empty log, and a log whose last row lacks its line end
    when = datetime(2026, 11, 6, 13, 31, 5, tzinfo=UTC)
    call = study.LoggedCall(when, "nfp", date(2026, 11, 6), 151.0, "DXY", study.SILENT)
    empty, unterminated = tmp_path / "empty.csv", tmp_path / "unterminated.csv"
    empty.touch()
    study.append_calls(unterminated, [call])
    unterminated.write_text(unterminated.read_text().rstrip("\n"))

    # when a row is added to each
    study.append_calls(empty, [call])
    study.append_calls(unterminated, [call])

    # then each reads back whole
    assert study.read_calls(empty) == [call]
    assert study.read_calls(unterminated) == [call, call]


def test_an_unreadable_log_row_is_named(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and a log with a damaged row
    _store_consensus_history(db.get_connection())
    _next(monkeypatch, expectations.NextConsensus(date(2026, 11, 12), 0.2, 0.2))
    settings.calls_path.write_text(",".join(study.LOG_COLUMNS) + "\nnot a time,cpi\n")

    # when an actual is typed in
    code = main(["predict", "--event", "cpi", "--actual", "0.3"])

    # then it stops and names the line
    assert code == 1
    assert "line 2 cannot be read" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("row", "line", "reason"),
    [
        ("2026-11-06T13:31:05,nfp,2026-11-06,151.0,DXY,silent,,,,", 2, "has no zone"),
        ("2026-11-06T13:31:05+00:00,nfp,2026-11-06,151.0,DXY,called,,,,", 2, "unknown outcome"),
        ("2026-11-06T13:31:05+00:00,nfp,2026-11-06,151.0,DXY,call,UP,,,", 2, "unknown direction"),
        ("2026-11-06T13:31:05+00:00,nfp,2026-11-06,151.0,DXY,call,up,0.6,-0.1,", 2, "half a band"),
        ("\n2026-11-06T13:31:05+00:00,nfp,not a day,151.0,DXY,silent,,,,", 3, "not a day"),
    ],
    ids=["naive time", "outcome", "direction", "half a band", "after a blank line"],
)
def test_a_row_the_log_cannot_hold_is_refused_by_its_line(
    tmp_path: Path, row: str, line: int, reason: str
) -> None:
    # given a log with one row that step 2 could not grade
    path = tmp_path / "calls.csv"
    path.write_text(",".join(study.LOG_COLUMNS) + "\n" + row + "\n")

    # when it is read
    with pytest.raises(ValueError) as refused:
        study.read_calls(path)

    # then the row's line and the reason are named
    assert f"line {line} cannot be read" in str(refused.value)
    assert reason in str(refused.value)


def test_a_log_under_another_header_is_refused(tmp_path: Path) -> None:
    # given a log whose header lacks a column
    path = tmp_path / "calls.csv"
    path.write_text(",".join(study.LOG_COLUMNS[:-1]) + "\n")

    # when it is read
    with pytest.raises(ValueError) as refused:
        study.read_calls(path)

    # then its header is named
    assert "line 1 is not the log's header" in str(refused.value)


def _live_release(
    con: duckdb.DuckDBPyConnection,
    released: date,
    moves: dict[str, float] | None = None,
    surprise: float = 0.1,
) -> None:
    # A CPI release after the history, its first print 0.3 against a consensus of 0.2, and its moves.
    month = date(released.year, released.month, 1) - timedelta(days=1)
    flows.store_releases(
        flows.CPI_FLOW, [FirstRelease(month.replace(day=1), released, 0.3)], con=con
    )
    event = flows.stored_events(flows.CPI_FLOW, con=con)[-1]
    con.execute(
        "INSERT INTO surprises VALUES (?, ?, ?, 0.3, ?, ?)",
        [event.event_id, CORE, expectations.NASDAQ_CONSENSUS, 0.3 - surprise, surprise],
    )
    for instrument, move in (moves or {}).items():
        con.execute(
            "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
            "VALUES (?, ?, 'pct', ?)",
            [event.event_id, instrument, move],
        )


def _row(
    day: date,
    instrument: str,
    at: time = time(9, 0),
    actual: float = 0.3,
    outcome: str = study.CALLED,
    direction: int | None = 1,
    probability: float | None = 0.7,
) -> study.LoggedCall:
    when = datetime.combine(day, at, tzinfo=NEW_YORK)
    band = (0.001, 0.003) if probability is not None else None
    return study.LoggedCall(
        when, "cpi", day, actual, instrument, outcome, direction, probability, band
    )


def test_score_grades_the_calls_in_time_and_lists_the_void_missed_and_pending(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the CPI history and four live releases: one logged, with the dollar's row written after
    # its 15:00 close; one logged with a mistyped actual; one never logged; one not loaded yet
    con = db.get_connection()
    _store_consensus_history(con)
    first, mistyped, missed = date(2026, 10, 14), date(2026, 11, 12), date(2026, 12, 10)
    _live_release(con, first, {"SPY / ES": -0.004, "UST10Y / ZN": 5.0, "DXY": 0.002})
    _live_release(con, mistyped, {"SPY / ES": -0.004})
    _live_release(con, missed)
    study.append_calls(
        settings.calls_path,
        [
            _row(first, "SPY / ES", direction=-1),
            _row(first, "UST10Y / ZN", outcome=study.TOO_FEW_CALLS, probability=None),
            _row(first, "DXY", at=time(15, 20)),
            _row(first, "VIX", outcome=study.SILENT, direction=None, probability=None),
            _row(mistyped, "SPY / ES", actual=0.4, direction=-1),
            _row(date(2027, 1, 13), "SPY / ES", direction=-1),
        ],
    )

    # when the log is scored
    code = main(["score"])

    # then the two calls in time are graded, the late one and the mistyped release are void and
    # named, the unlogged release is missed, and the one not loaded waits
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[out.index("walk-forward (live)") + 2 :][:4] == [
        "SPY / ES     down      2026-09  1          1      100%      0.5000  100%             too few",
        "UST10Y / ZN  up        2026-09  1          1      100%      0.5000  100%             too few",
        "DXY          up        —        0          0      —         —       —                too few",
        "VIX          up        —        0          0      —         —       —                too few",
    ]
    assert out[out.index("void: 2") + 1 :][:2] == [
        "  cpi 2026-10-14 DXY: logged 15:20 New York, not from the release at 08:30 until its "
        "close at 15:00",
        "  cpi 2026-11-12: actual 0.4 is not FRED's first print 0.3",
    ]
    assert out[out.index("pending: 1") + 1] == "  cpi 2027-01-13: the release is not loaded"
    assert out[-2:] == [
        "missed: 1 releases since 2026-10-13 with no rows (claims since 2026-10-29)",
        "  cpi 2026-12-10",
    ]


def test_a_call_on_tradingview_s_forecast_is_logged_and_graded(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history, a release Nasdaq had no consensus for, called at 09:00 on TradingView's
    # 0.2, and later loaded with that surprise and its moves
    con = db.get_connection()
    _store_consensus_history(con)
    day = date(2026, 10, 14)
    _next(monkeypatch, expectations.NextConsensus(day, None, 0.2))
    assert main(["predict", "--event", "cpi", "--actual", "0.3"]) == 0
    _live_release(con, day, {"SPY / ES": -0.004, "UST10Y / ZN": 5.0, "DXY": 0.002, "VIX": 0.01})
    capsys.readouterr()

    # when the log is scored
    code = main(["score"])

    # then each link's call is graded, and none is void, pending or missed
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[out.index("walk-forward (live)") + 2 :][:4] == [
        "SPY / ES     down      2026-09  1          1      100%      0.5000  100%             too few",
        "UST10Y / ZN  up        2026-09  1          1      100%      0.5000  100%             too few",
        "DXY          up        2026-09  1          1      100%      0.5000  100%             too few",
        "VIX          up        2026-09  1          1      100%      0.5000  100%             too few",
    ]
    assert not any(line.startswith(("void:", "pending:")) for line in out)
    assert out[-1] == "missed: 0 releases since 2026-10-13 with no rows (claims since 2026-10-29)"


@pytest.mark.parametrize(
    ("at", "graded"), [(time(8, 30), True), (time(8, 29, 59), False), (time(14, 59), True)]
)
def test_a_call_counts_from_the_release_until_its_close(
    tmp_db: Path, at: time, graded: bool
) -> None:
    # given the CPI history and a live release whose dollar call was logged at ``at``
    con = db.get_connection()
    _store_consensus_history(con)
    day = date(2026, 10, 14)
    _live_release(con, day, {"DXY": 0.002})

    # when it is scored
    score = study.score_calls(flows.CPI_FLOW, [_row(day, "DXY", at=at)], con=con)

    # then it is graded only from 08:30 New York until the dollar's 15:00 close
    assert len(score.calls["DXY"]) == int(graded)
    assert len(score.void) == int(not graded)


def test_a_live_call_is_graded_with_its_stated_numbers_and_the_replay_s_drift(
    tmp_db: Path,
) -> None:
    # given the CPI history and a live release whose yield call stated 70% and a band
    con = db.get_connection()
    _store_consensus_history(con)
    day = date(2026, 10, 14)
    _live_release(con, day, {"UST10Y / ZN": 0.002}, surprise=0.15)

    # when it is scored
    score = study.score_calls(flows.CPI_FLOW, [_row(day, "UST10Y / ZN")], con=con)

    # then the call carries what was logged, the stored surprise and move, and the drift of the
    # noticeable releases before it
    rule = flows.CPI_FLOW.surprise_rule
    assert rule is not None
    earlier = con.execute(
        "SELECT o.ret_1d FROM surprises s JOIN observations o ON o.event_id = s.event_id "
        "WHERE o.instrument = 'UST10Y / ZN' AND s.event_id < ? AND abs(s.surprise) >= ?",
        [graded_event_id(con, day), rule.noticeable],
    ).fetchall()
    (graded,) = score.calls["UST10Y / ZN"]
    assert (graded.call.direction, graded.call.surprise, graded.call.move) == (1, 0.15, 0.002)
    assert (graded.probability, graded.band) == (0.7, (0.001, 0.003))
    assert graded.drift == (sum(m > 0 for (m,) in earlier) + 1) / (len(earlier) + 2)
    assert score.void == [] and score.pending == []


def graded_event_id(con: duckdb.DuckDBPyConnection, day: date) -> int:
    return next(
        e.event_id
        for e in flows.stored_events(flows.CPI_FLOW, con=con)
        if flows.release_date(e) == day
    )


def test_live_never_asks_for_a_release_after_its_run(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the CPI history and calendars that record each measure asked for
    _store_consensus_history(db.get_connection())
    asked: list[str] = []

    def upcoming(measure: str, today: date, cache_dir: Path) -> expectations.NextConsensus:
        asked.append(measure)
        return expectations.NextConsensus(today + timedelta(days=1), 0.2, 0.2)

    monkeypatch.setattr(expectations, "next_consensus", upcoming)
    _tradingview_reads(monkeypatch, [0.3])

    # when the release-day job's command runs
    code = main(["live"])

    # then it asks for every 08:30 US measure, claims among them, but neither euro-area one nor
    # ISM's
    assert code == 0
    assert "core" in asked
    assert set(sources.TRADINGVIEW_ROWS) & set(asked) == {sources.INITIAL_CLAIMS}
