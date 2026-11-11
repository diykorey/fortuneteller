from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import pytest

from fortuneteller import db, flows, sources, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.models import Surprise
from fortuneteller.sources import DailyClosingPrice
from fortuneteller.study import ABOVE, BELOW, CUT, HOLD, HOLE, LEFT_OUT, TOO_FEW

START = date(2001, 1, 1)
NFP = flows.flow_named("nfp")
SPY = "SPY / ES"
GOLD = "GC / XAU"
HEADER = b"flow,day,kind\n"


def _days(n: int) -> list[date]:
    # n weekdays from START
    days, day = [], START
    while len(days) < n:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _closes(steps: list[float]) -> list[DailyClosingPrice]:
    # closes from 100 by each day's relative step
    price, closes = 100.0, []
    for day, step in zip(_days(len(steps)), steps, strict=True):
        price *= 1 + step
        closes.append(DailyClosingPrice(day, price))
    return closes


def _wavy(n: int) -> list[float]:
    # day steps that differ in size and sign, so every span length has moves of each kind
    return [0.01 * ((i * 7) % 5 - 2) / 2 + 0.003 * ((i * 3) % 4 - 1.5) for i in range(n)]


def _report(day: date) -> flows.EventInstance:
    # a jobs report at 08:30 New York on ``day``
    at = datetime.combine(day, time(8, 30), tzinfo=sources.NEW_YORK)
    decision = flows.fomc_event_instance(sources.FomcDecision(day, True))
    return decision.model_copy(
        update={
            "event_id": flows.event_id(NFP, day),
            "event_type": NFP.event_type,
            "event_ts": at.astimezone(UTC).replace(tzinfo=None),
        }
    )


def _trigger(
    day: date, kind: str = ABOVE, flow: str = "nfp", line: int = 2, sha: str = "a"
) -> study.Trigger:
    return study.Trigger("2001.csv", line, sha, flow, day, kind)


@pytest.fixture
def one_market(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {SPY: study.MVP_PRICE_SERIES[SPY]})


def _answer(
    triggers: list[study.Trigger],
    reports: list[flows.EventInstance],
    kinds: dict[int, str],
    closes: list[DailyClosingPrice],
    merged: datetime | None,
    log: list[dict[str, str]] | None = None,
    flow: str = "nfp",
) -> tuple[list[dict[str, str]], list[str]]:
    markets = {m: closes for m in study.MVP_PRICE_SERIES}
    return study.answer_triggers(
        triggers, lambda sha: merged, {flow: reports}, {flow: kinds}, markets, log or []
    )


def test_a_trigger_counts_on_a_market_only_if_merged_before_its_reaction_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given a Fed cut at 14:00 New York, the S&P 500 closing at 16:00 that day and gold at 13:30,
    # so gold reacts the next day
    monkeypatch.setattr(
        study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in (SPY, GOLD)}
    )
    closes = _closes(_wavy(300))
    day = closes[200].day
    cut = flows.fomc_event_instance(sources.FomcDecision(day, True))
    close = datetime.combine(day, time(16, 0), tzinfo=sources.NEW_YORK)

    # when merged a minute before the S&P 500's close, and at it
    early = _answer(
        [_trigger(day, CUT, "fomc")],
        [cut],
        {cut.event_id: CUT},
        closes,
        close - timedelta(minutes=1),
        flow="fomc",
    )
    late = _answer(
        [_trigger(day, CUT, "fomc")], [cut], {cut.event_id: CUT}, closes, close, flow="fomc"
    )

    # then the first is answered on both, the second late on the S&P 500 and answered on gold
    assert {r["market"] for r in early[0]} == {SPY, GOLD}
    assert {r["market"] for r in late[0]} == {GOLD}
    assert any(line.startswith(f"  {SPY}: late") for line in late[1])


def test_a_trigger_s_kind_and_day_must_match_the_store(one_market: None) -> None:
    # given a report above the consensus, one whose kind is not stored, and a later report
    closes = _closes(_wavy(300))
    days = [closes[i].day for i in (100, 120, 140)]
    reports = [_report(d) for d in days]
    kinds = {reports[0].event_id: ABOVE, reports[2].event_id: BELOW}
    merged = datetime.combine(days[0], time(9, 0), tzinfo=sources.NEW_YORK)

    # when filed as below, with the second's kind missing, a day with no report, and a repeat
    triggers = [
        _trigger(days[0], BELOW, line=2),
        _trigger(days[1], ABOVE, line=3),
        _trigger(days[0] + timedelta(days=1), ABOVE, line=4),
        _trigger(days[2], BELOW, line=5),
        _trigger(days[2], BELOW, line=6, sha="later"),
    ]
    times = {"a": merged, "later": merged + timedelta(minutes=5)}
    rows, lines = study.answer_triggers(
        triggers, times.get, {"nfp": reports}, {"nfp": kinds}, {SPY: closes}, []
    )

    # then each is void or waiting with its reason, and only the last report is answered
    assert f"2001.csv:2 nfp {days[0]} below: void, the stored kind is above, not below" in lines
    assert f"2001.csv:3 nfp {days[1]} above: waiting, its kind is not stored" in lines
    assert any(
        line.endswith(f"void, nfp had no event on {days[0] + timedelta(days=1)}") for line in lines
    )
    assert f"2001.csv:6 nfp {days[2]} below: void, repeats nfp {days[2]}, filed earlier" in lines
    assert {r["line"] for r in rows} == {"5"}


def test_a_trigger_is_answered_as_part_1_replays_its_event(one_market: None) -> None:
    # given 40 reports 15 closes apart, above and below in turn, and the month after each
    closes = _closes(_wavy(900))
    keys = list(range(100, 700, 15))
    reports = [_report(closes[i].day) for i in keys]
    kinds = {r.event_id: ABOVE if n % 2 == 0 else BELOW for n, r in enumerate(reports)}
    triggers = [
        _trigger(r.event_id and closes[i].day, kinds[r.event_id], line=n + 2)
        for n, (i, r) in enumerate(zip(keys, reports, strict=True))
    ]

    # when every report is filed in time
    rows, _ = _answer(triggers, reports, kinds, closes, datetime(2000, 1, 1, tzinfo=UTC))

    # then each answer is part 1's walk-forward answer at that report, or left out where it is
    series = study.MVP_PRICE_SERIES[SPY]
    decisions = [(study.first_reaction_day(r, series), kinds[r.event_id]) for r in reports]
    for span, c in study.SPANS.items():
        spans = study.span_moves(closes, "pct", c)
        by_end = sorted(spans.items(), key=lambda item: item[1].end)
        walk, _ = study.kept_keys(decisions, closes, spans, c, after=True)
        for kind in (ABOVE, BELOW):
            kept = [
                i + 1
                for i, (d, k), w in zip(keys, decisions, walk, strict=True)
                if k == kind and w.status == study.KEPT
            ]
            kept_days = [closes[i].day for i in kept]
            for n, (i, (_, k), w) in enumerate(zip(keys, decisions, walk, strict=True)):
                if k != kind:
                    continue
                row = next(r for r in rows if r["line"] == str(n + 2) and r["span"] == span)
                if w.status == LEFT_OUT:
                    assert row["answer"] == LEFT_OUT
                    continue
                then = study.answer_before(kept_days, kept.index(i + 1), spans, by_end)
                assert row["answer"] == (TOO_FEW if then is None else then[0])
    assert any(r["answer"] == LEFT_OUT for r in rows if r["span"] == "month")


def test_a_month_still_open_before_the_trigger_leaves_it_out_as_the_replay_will(
    one_market: None,
) -> None:
    # given 14 reports 25 closes apart and a last one 10 closes after them, the closes ending at
    # its reaction close, so the month before it is still open
    steps = _wavy(600)
    keys = [*range(50, 400, 25), 385]
    closes = _closes(steps)
    reports = [_report(closes[i].day) for i in keys]
    kinds = dict.fromkeys((r.event_id for r in reports), ABOVE)
    last = _trigger(closes[keys[-1]].day, line=2)

    # when it is answered with the closes to its reaction close, and with them all
    now, _ = _answer(
        [last], reports, kinds, closes[: keys[-1] + 1], datetime(2000, 1, 1, tzinfo=UTC)
    )
    later, _ = _answer([last], reports, kinds, closes, datetime(2000, 1, 1, tzinfo=UTC))

    # then the month is left out both times, and the day is answered the same both times
    month = [r["answer"] for rows in (now, later) for r in rows if r["span"] == "month"]
    day = [r["answer"] for rows in (now, later) for r in rows if r["span"] == "day"]
    assert month == [LEFT_OUT, LEFT_OUT]
    assert day[0] == day[1] != LEFT_OUT


def test_the_log_is_filled_once_and_never_changed(one_market: None) -> None:
    # given 14 reports, the last filed, and the closes to its reaction close only
    closes = _closes(_wavy(600))
    keys = list(range(50, 400, 25))
    reports = [_report(closes[i].day) for i in keys]
    kinds = dict.fromkeys((r.event_id for r in reports), ABOVE)
    trigger = _trigger(closes[keys[-1]].day)
    merged = datetime(2000, 1, 1, tzinfo=UTC)
    first, _ = _answer([trigger], reports, kinds, closes[: keys[-1] + 1], merged)

    # when run again with every later close in, then with the later closes revised
    second, _ = _answer([trigger], reports, kinds, closes, merged, first)
    revised = closes[: keys[-1] + 1] + [
        DailyClosingPrice(c.day, c.price * (1 + (k % 5 + 1) / 10))
        for k, c in enumerate(closes[keys[-1] + 1 :])
    ]
    third, _ = _answer([trigger], reports, kinds, revised, merged, second)
    fresh, _ = _answer([trigger], reports, kinds, revised, merged)

    # then the first run has answers and no outcome, the second only fills the outcome, the third
    # changes nothing, and the answers never read a close after the reaction
    assert [r["outcome"] for r in first] == ["", "", ""]
    assert all(r["outcome"] for r in second if r["cut"])
    for a, b in zip(first, second, strict=True):
        assert {k: v for k, v in a.items() if k not in ("outcome", "result")} == {
            k: v for k, v in b.items() if k not in ("outcome", "result")
        }
    assert third == second
    assert [r["answer"] for r in fresh] == [r["answer"] for r in first]


def test_a_span_with_a_hole_is_logged_as_one_and_not_graded(one_market: None) -> None:
    # given 14 reports, and a two-week gap in the closes three closes after the last
    closes = _closes(_wavy(600))
    keys = list(range(50, 400, 25))
    reports = [_report(closes[i].day) for i in keys]
    kinds = dict.fromkeys((r.event_id for r in reports), ABOVE)
    gap = keys[-1] + 3
    holed = closes[:gap] + [
        DailyClosingPrice(c.day + timedelta(days=14), c.price) for c in closes[gap:]
    ]
    trigger = _trigger(closes[keys[-1]].day)
    merged = datetime(2000, 1, 1, tzinfo=UTC)

    # when answered while its spans are open, then with every close in, and fresh
    first, _ = _answer([trigger], reports, kinds, holed[: keys[-1] + 1], merged)
    then, _ = _answer([trigger], reports, kinds, holed, merged, first)
    fresh, _ = _answer([trigger], reports, kinds, holed, merged)

    # then the day is graded, and the week and the month are holes with no result, both ways
    for rows in (then, fresh):
        by_span = {r["span"]: r for r in rows}
        assert by_span["day"]["outcome"] in ("up", "about the same", "down")
        for span in ("week", "month"):
            assert by_span[span]["cut"]
            assert (by_span[span]["outcome"], by_span[span]["result"]) == (HOLE, "")


def test_a_trigger_waiting_for_its_close_files_nothing(one_market: None) -> None:
    # given three reports and the closes ending before the first
    closes = _closes(_wavy(300))
    days = [closes[i].day for i in (100, 120, 140)]
    reports = [_report(d) for d in days]
    kinds = dict.fromkeys((r.event_id for r in reports), ABOVE)

    # when the first is filed
    rows, lines = _answer(
        [_trigger(days[0])], reports, kinds, closes[:90], datetime(2000, 1, 1, tzinfo=UTC)
    )

    # then it waits, logs nothing, and lists nothing as not filed
    assert rows == []
    assert not any(line.startswith("not filed") for line in lines)


def test_the_events_not_filed_are_listed(one_market: None) -> None:
    # given three reports, the second filed, the first and last not
    closes = _closes(_wavy(300))
    days = [closes[i].day for i in (100, 120, 140)]
    reports = [_report(d) for d in days]
    kinds = dict.fromkeys((r.event_id for r in reports), ABOVE)

    # when answered
    _, lines = _answer(
        [_trigger(days[1])], reports, kinds, closes, datetime(2000, 1, 1, tzinfo=UTC)
    )

    # then only the one after the first filed is listed
    assert [line for line in lines if line.startswith("not filed")] == [f"not filed: nfp {days[2]}"]


def test_a_file_with_another_header_voids_its_own_rows_only() -> None:
    # given two files, one with a wrong header
    files = [
        ("a.csv", "x", b"flow,day\nnfp,2001-01-05\n"),
        ("b.csv", "y", HEADER + b"nfp,2001-01-05,above\n"),
    ]

    # when read
    triggers, bad = study.read_triggers(files)

    # then the good file's trigger is read, and the bad file named
    assert triggers == [study.Trigger("b.csv", 2, "y", "nfp", date(2001, 1, 5), ABOVE)]
    assert bad == ["a.csv: void, its header is not flow,day,kind"]


def test_triggers_with_none_filed_says_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no trigger directory
    monkeypatch.setattr(settings, "triggers_dir", tmp_path / "triggers")
    monkeypatch.setattr(settings, "trigger_log_path", tmp_path / "trigger-log.csv")
    monkeypatch.setattr(settings, "db_path", tmp_path / "test_triggers.duckdb")

    # when run
    code = main(["triggers"])

    # then it says none are filed and writes no log
    assert code == 0
    assert capsys.readouterr().out == "triggers: none filed\n"
    assert not (tmp_path / "trigger-log.csv").exists()


def test_triggers_prints_and_logs_a_trigger_s_answers(
    tmp_db: Path,
    tmp_path: Path,
    one_market: None,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given one market's closes, 12 jobs reports above the consensus, and a file filing the last
    closes = _closes(_wavy(600))
    keys = list(range(50, 350, 25))
    reports = [_report(closes[i].day) for i in keys]
    con = db.get_connection()
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    db.insert_models("event_instances", reports)
    db.insert_models(
        "surprises",
        [
            Surprise(
                event_id=r.event_id,
                measure="payrolls",
                baseline="nasdaq_consensus",
                actual_mom=0.0,
                expected_mom=0.0,
                surprise=60.0,
            )
            for r in reports
        ],
    )
    day = closes[keys[-1]].day
    file = HEADER + f"nfp,{day},above\n".encode()
    monkeypatch.setattr(study, "guess_files", lambda directory: [("first.csv", "a", file)])
    monkeypatch.setattr(study, "merged_at", lambda directory, sha: datetime(2000, 1, 1, tzinfo=UTC))
    log = tmp_path / "trigger-log.csv"
    monkeypatch.setattr(settings, "trigger_log_path", log)

    # when run
    code = main(["triggers"])

    # then it prints the trigger and its three spans, and logs them
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == f"first.csv:2 nfp {day} above, merged 1999-12-31 19:00 New York"
    assert [line.split(":")[0] for line in out[1:4]] == [
        "  SPY / ES day",
        "  SPY / ES week",
        "  SPY / ES month",
    ]
    assert log.read_text().splitlines()[0] == ",".join(study.TRIGGER_LOG_COLUMNS)
    assert len(log.read_text().splitlines()) == 4


def test_a_claims_trigger_is_answered_not_refused(one_market: None) -> None:
    # given a claims report below the consensus at 08:30 New York
    claims = flows.flow_named("claims")
    closes = _closes(_wavy(300))
    day = closes[200].day
    report = _report(day).model_copy(
        update={"event_id": flows.event_id(claims, day), "event_type": claims.event_type}
    )
    merged = datetime.combine(day, time(9, 0), tzinfo=sources.NEW_YORK)

    # when filed as below before the close
    rows, lines = _answer(
        [_trigger(day, BELOW, "claims")],
        [report],
        {report.event_id: BELOW},
        closes,
        merged,
        flow="claims",
    )

    # then it is answered on the market, not refused for its flow
    assert {r["market"] for r in rows} == {SPY}
    assert not any("is not one of" in line for line in lines)


def test_an_ecb_trigger_is_answered_not_refused(one_market: None) -> None:
    # given an ECB hold at 14:15 Frankfurt
    closes = _closes(_wavy(300))
    day = closes[200].day
    hold = flows.ecb_event_instance(
        datetime.combine(day, time(14, 15), tzinfo=sources.FRANKFURT).astimezone(UTC)
    )
    merged = datetime.combine(day, time(14, 30), tzinfo=sources.FRANKFURT)

    # when filed as a hold before the close
    rows, lines = _answer(
        [_trigger(day, HOLD, "ecb")], [hold], {hold.event_id: HOLD}, closes, merged, flow="ecb"
    )

    # then it is answered on the market, not refused for its flow
    assert {r["market"] for r in rows} == {SPY}
    assert not any("is not one of" in line for line in lines)
