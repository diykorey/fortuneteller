import math
import random
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import pytest

from fortuneteller import db, flows, sources, study
from fortuneteller.__main__ import _trigger_companies, main
from fortuneteller.sources import DailyClosingPrice
from fortuneteller.study import CANT_SAY, DOWN, SAME, TOO_FEW, UP, Base

START = date(2001, 1, 1)


def _days(n: int) -> list[date]:
    # n weekdays from START
    days, day = [], START
    while len(days) < n:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _closes(steps: list[float], start: float = 100.0) -> list[DailyClosingPrice]:
    # closes from start by each day's relative step
    price, closes = start, []
    for day, step in zip(_days(len(steps)), steps, strict=True):
        price *= 1 + step
        closes.append(DailyClosingPrice(day, price))
    return closes


def _gaussian(n: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(0, 0.01) for _ in range(n)]


def test_a_stock_that_moves_exactly_as_the_index_has_no_excess_move() -> None:
    # given an index, and a stock at twice its price on every day
    index = _closes(_gaussian(300, 1))
    stock = [DailyClosingPrice(c.day, 2 * c.price) for c in index]

    # when the excess moves are read over every span
    excess = {span: study.excess_spans(stock, index, c) for span, c in study.SPANS.items()}

    # then every span is there, and each excess move is zero
    assert all(len(spans) == 300 - c for (_, spans), c in zip(excess.items(), study.SPANS.values()))
    assert {round(s.move, 12) for spans in excess.values() for s in spans.values()} == {0.0}


def test_an_excess_move_is_the_stock_s_move_less_the_index_s_on_the_days_both_have() -> None:
    # given a stock up 5% and an index up 2% on the third day, and a day only the stock has
    index = _closes([0.0, 0.0, 0.02, 0.0])
    stock = _closes([0.0, 0.0, 0.05, 0.0])
    extra = DailyClosingPrice(index[1].day + timedelta(days=1), 999.0)
    stock = [*stock[:2], extra, *stock[2:]] if extra.day < stock[2].day else stock

    # when the day's excess move is read
    spans = study.excess_spans(stock, index, 1)

    # then it is 3%, keyed on the third day
    assert spans[index[2].day].move == pytest.approx(0.03)


def test_an_event_s_base_never_reads_a_close_after_its_close_before() -> None:
    # given a company's closes, and the same closes wild after an event's close before
    steps = _gaussian(800, 2)
    wild = steps[:601] + [0.2 * (-1) ** i for i in range(199)]
    index = _closes([0.0] * 800)
    calm, rough = _closes(steps), _closes(wild)
    r = 601

    # when the event's base is read from each
    bases = [
        study.event_base(study.excess_spans(closes, index, 5), closes, r)
        for closes in (calm, rough)
    ]

    # then they are the same base, and too short a history has none
    assert bases[0] is not None
    assert bases[0] == bases[1]
    assert study.event_base(study.excess_spans(calm, index, 5), calm, study.BASE_CLOSES - 1) is None


def test_ten_events_all_down_against_a_base_of_a_third_read_down() -> None:
    # given ten events all down, each against a base of a third each way
    third = Base(0.01, {UP: 1 / 3, SAME: 1 / 3, DOWN: 1 / 3})

    # when answered, and with nine
    ten = study.rates_answer([DOWN] * 10, [third] * 10)
    nine = study.rates_answer([DOWN] * 9, [third] * 9)

    # then ten read down at a chance of a half to the tenth, and nine are too few
    assert ten[0] == DOWN
    assert ten[1] == pytest.approx(0.5**10)
    assert nine[0] == TOO_FEW


def test_each_event_is_answered_against_its_own_base() -> None:
    # given twelve events that moved up, six at bases where up is rare and six where it is common
    rare = Base(0.01, {UP: 0.05, SAME: 0.5, DOWN: 0.45})
    common = Base(0.01, {UP: 0.45, SAME: 0.5, DOWN: 0.05})

    # when answered
    answer, chance, _ = study.rates_answer([UP] * 12, [rare] * 6 + [common] * 6)

    # then the chance is the product of their up shares
    assert answer == UP
    assert chance == pytest.approx(0.1**6 * 0.9**6)


def _company(seed: int, event: int, drop: float, n: int = 700) -> list[DailyClosingPrice]:
    steps = _gaussian(n, seed)
    steps[event] = drop
    return _closes(steps)


def test_companies_that_fall_on_their_event_day_read_down_on_the_day_only() -> None:
    # given twelve companies over a flat index, each 6% down on its own event day
    index = _closes([0.0] * 700)
    events, closes = [], {}
    for n in range(12):
        ticker, i = f"C{n}", 520 + 10 * n
        closes[ticker] = _company(n, i, -0.06)
        events.append((closes[ticker][i].day, ticker))

    # when the day is followed, and the day after it
    day = study.follow_scandals(events, closes, index, 1)
    after = study.follow_scandals(events, closes, index, 1, after=True)

    # then the day reads down on all twelve, and the day after has no answer
    assert day.counts == {UP: 0, SAME: 0, DOWN: 12}
    assert day.answer == DOWN
    assert after.answer in (CANT_SAY, SAME)


def test_a_company_with_no_closes_or_too_short_a_history_is_a_hole() -> None:
    # given one company with no closes, and one whose event comes before 504 closes
    index = _closes([0.0] * 700)
    young = _company(3, 100, -0.06)

    # when followed
    follow = study.follow_scandals(
        [(young[100].day, "YOUNG"), (index[600].day, "GONE")], {"YOUNG": young}, index, 1
    )

    # then both are holes, and nothing is answered
    assert follow.holes == 2
    assert follow.answer == TOO_FEW
    assert math.isnan(follow.chance)


def _seed(tmp_path: Path, rows: list[str]) -> Path:
    path = tmp_path / "ceo_scandals.csv"
    path.write_text("day,time,ticker,company,ceo,conduct,source\n" + "\n".join(rows) + "\n")
    return path


def test_a_word_out_on_a_sunday_or_after_the_close_reacts_at_the_next_close(
    tmp_path: Path,
) -> None:
    # given words out on a Sunday, after a close, at an unknown time and before a close
    path = _seed(
        tmp_path,
        [
            "2019-11-03,19:55,MCD,a,b,c,d",
            "2018-07-17,after close,TXN,a,b,c,d",
            "2006-04-24,unknown,MMS,a,b,c,d",
            "2012-04-10,before close,BBY,a,b,c,d",
        ],
    )

    # when the flow reads them
    events = flows.CEO_FLOW.load(path, datetime(2026, 11, 13, tzinfo=UTC)).events

    # then each reacts at the next close but the one before the close, and carries its ticker
    reacts = {e.detail: study.first_reaction_day(e, study.STOCK) for e in events}
    assert reacts == {
        "MCD": date(2019, 11, 4),
        "TXN": date(2018, 7, 18),
        "MMS": date(2006, 4, 25),
        "BBY": date(2012, 4, 10),
    }


def test_follows_for_ceo_scandals_prints_its_table(
    tmp_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given the index and two companies' closes, and an event at each
    index = _closes([0.0] * 700)
    con = db.get_connection()
    rows = [("SPY / ES", c) for c in index]
    for ticker, seed, i in (("AAA", 1, 600), ("BBB", 2, 610)):
        rows += [(ticker, c) for c in _company(seed, i, -0.06)]
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[i, c.day, c.price] for i, c in rows],
    )
    path = _seed(
        tmp_path, [f"{index[600].day},10:00,AAA,a,b,c,d", f"{index[610].day},10:00,BBB,a,b,c,d"]
    )
    flows.store_events(flows.CEO_FLOW.load(path, datetime(2026, 11, 13, tzinfo=UTC)).events)

    # when run
    code = main(["follows", "--event", "ceo"])

    # then it prints each span against the S&P 500
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == f"follows: 2 CEO scandals {index[600].day} … {index[610].day}: 2 scandals"
    assert out[2].startswith("scandal day    vs S&P 500     2   0    0    2      0/0  ")
    assert len(out) == 6


def test_a_company_yahoo_fails_on_is_reported_and_the_others_load(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given Yahoo answering for one company and failing for another
    def fetch(ticker: str) -> bytes:
        if ticker == "BAD":
            raise sources.YahooError("Yahoo returned HTTP 404 for BAD")
        return ticker.encode()

    monkeypatch.setattr(sources, "fetch_daily_bars", fetch)
    monkeypatch.setattr(
        sources, "parse_daily_bars", lambda _payload: [DailyClosingPrice(START, 10.0)]
    )

    # when both are loaded
    counts, failed = study.load_company_bars(["GOOD", "BAD"])

    # then the one loads under its ticker and the other is reported
    assert counts == {"GOOD": 1}
    assert failed == ["BAD: Yahoo returned HTTP 404 for BAD"]
    assert study.stored_closes("GOOD") == [DailyClosingPrice(START, 10.0)]


def test_a_trigger_file_may_name_a_company_read_for_ceo_alone() -> None:
    # given a file with a ticker column, holding a ceo row and a jobs report row
    files = [
        (
            "t.csv",
            "s",
            b"flow,day,kind,ticker\nceo,2026-11-08,scandal,NVDA\nnfp,2001-01-05,above,X\n",
        )
    ]

    # when read
    triggers, bad = study.read_triggers(files)

    # then the ceo row carries its ticker, the other none
    assert bad == []
    assert [(t.flow, t.ticker) for t in triggers] == [("ceo", "NVDA"), ("nfp", "")]


def _history() -> tuple[
    list[DailyClosingPrice], dict[str, list[DailyClosingPrice]], list[flows.EventInstance]
]:
    # a flat index, and twelve companies each 6% down the day after its event's reaction close
    index = _closes([0.0] * 700)
    companies, events = {}, []
    for n in range(12):
        ticker, i = f"C{n}", 520 + 10 * n
        companies[ticker] = _company(n, i + 1, -0.06)
        at = datetime.combine(index[i].day, time(10, 0), tzinfo=sources.NEW_YORK)
        events.append(flows.CEO_FLOW.event_instance(at, ticker))
    companies["NEW"] = _company(99, 661, -0.06)
    return index, companies, events


def _ceo_answer(
    trigger: study.Trigger, merged: datetime, companies: dict[str, list[DailyClosingPrice]]
) -> tuple[list[dict[str, str]], list[str]]:
    index, _, events = _history()
    return study.answer_triggers(
        [trigger],
        lambda _sha: merged,
        {"ceo": events},
        {"ceo": {}},
        {"SPY / ES": index},
        [],
        companies,
    )


def test_a_ceo_trigger_is_answered_from_the_scandals_before_it_and_graded_on_its_company() -> None:
    # given twelve scandals each followed by a fall the day after, and a new one at another
    # company, merged before its reaction close and falling the day after
    index, companies, _ = _history()
    day = index[660].day
    trigger = study.Trigger("t.csv", 2, "s", "ceo", day, study.SCANDAL, "NEW")
    merged = datetime.combine(day, time(12, 0), tzinfo=sources.NEW_YORK)

    # when answered
    rows, lines = _ceo_answer(trigger, merged, companies)

    # then the day after reads down from the twelve, and the company's own fall grades it right
    day_row = next(r for r in rows if r["span"] == "day")
    assert (day_row["market"], day_row["answer"], day_row["down"]) == ("NEW", DOWN, "12")
    assert (day_row["outcome"], day_row["result"]) == (DOWN, study.RIGHT)
    assert lines[1] == "  NEW vs S&P 500 day: down (0/0/12), down, right"
    assert len(rows) == 3


def test_a_ceo_trigger_late_unnamed_or_without_closes_counts_nowhere() -> None:
    # given a trigger merged after its reaction close, one with no ticker, one with no closes
    index, companies, _ = _history()
    day = index[660].day
    late = datetime.combine(day, time(16, 0), tzinfo=sources.NEW_YORK)
    early = datetime.combine(day, time(9, 0), tzinfo=sources.NEW_YORK)

    # when answered
    _, on_late = _ceo_answer(
        study.Trigger("t.csv", 2, "s", "ceo", day, "scandal", "NEW"), late, companies
    )
    _, unnamed = _ceo_answer(
        study.Trigger("t.csv", 2, "s", "ceo", day, "scandal"), early, companies
    )
    _, gone = _ceo_answer(
        study.Trigger("t.csv", 2, "s", "ceo", day, "scandal", "GONE"), early, companies
    )

    # then each says why, and none is logged
    assert on_late[0].startswith(f"t.csv:2 ceo {day} scandal NEW: late, merged {day} 16:00")
    assert unnamed == [
        f"t.csv:2 ceo {day} scandal: void, a ceo trigger names its company in a ticker column"
    ]
    assert gone == [f"t.csv:2 ceo {day} scandal GONE: waiting, GONE's closes are not loaded"]


def test_only_a_ceo_trigger_fetches_its_company(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given Yahoo watched, a jobs report trigger, and a ceo trigger naming a company
    asked: list[list[str]] = []

    def load(tickers: list[str], con: object = None) -> tuple[dict[str, int], list[str]]:
        asked.append(list(tickers))
        study.store_daily_bars(tickers[0], tickers[0], [DailyClosingPrice(START, 1.0)])
        return {tickers[0]: 1}, []

    monkeypatch.setattr(study, "load_company_bars", load)
    nfp = study.Trigger("t.csv", 2, "s", "nfp", START, "above")
    ceo = study.Trigger("t.csv", 3, "s", "ceo", START, "scandal", "NEW")
    con = db.get_connection()

    # when each is prepared
    alone = _trigger_companies([nfp], [], con)
    named = _trigger_companies([nfp, ceo], [], con)

    # then only the ceo trigger asks Yahoo, for its company alone
    assert (alone, asked) == ({}, [["NEW"]])
    assert named == {"NEW": [DailyClosingPrice(START, 1.0)]}
