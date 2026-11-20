import csv
import dataclasses
import math
import re
import random
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import pytest

from fortuneteller import db, flows, sources, stats, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import _trigger_companies, main
from fortuneteller.config import settings
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


def test_the_page_s_ceo_cells_have_no_base_count_and_say_why(tmp_db: Path, tmp_path: Path) -> None:
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

    # when the page's data is built
    ask = cli.ask_data(con)

    # then the CEO flow has a cell per span against the S&P 500, each with no base count, saying so
    (ceo,) = [entry for entry in ask["ask"] if entry["name"] == "ceo"]
    cells = ceo["cells"]
    assert [(c["span"], c["market"]) for c in cells] == [  # type: ignore[union-attr]
        ("day", "vs S&P 500"),
        ("week", "vs S&P 500"),
        ("month", "vs S&P 500"),
    ]
    assert all(c["base_n"] is None for c in cells)  # type: ignore[union-attr]
    assert cells[0]["say"].startswith(  # type: ignore[index]
        "After a CEO's conduct in question, the company against the S&P 500 on the day: "
        "up 0, about the same 0, down 2, of 2."
    )
    assert "no single count" in cells[0]["say"]  # type: ignore[index]


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
    assert gone == [f"t.csv:2 ceo {day} scandal GONE: void, no closes for GONE, so no answer"]


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


def test_a_ceo_trigger_answers_without_a_scandal_whose_company_has_no_closes() -> None:
    # given the twelve scandals, one of whose companies has no closes loaded
    index, companies, _ = _history()
    del companies["C3"]
    day = index[660].day
    trigger = study.Trigger("t.csv", 2, "s", "ceo", day, study.SCANDAL, "NEW")

    # when answered
    rows, lines = _ceo_answer(
        trigger, datetime.combine(day, time(12, 0), tzinfo=sources.NEW_YORK), companies
    )

    # then it answers at once from the other eleven and says which was left out
    day_row = next(r for r in rows if r["span"] == "day")
    assert (day_row["answer"], day_row["down"]) == (DOWN, "11")
    assert lines[1] == "  answered without C3: no closes"


def test_a_departure_over_the_ceo_s_own_conduct_reads_as_ceo() -> None:
    # given
    text = (
        "March 7, 2005: 12:48 PM EST. Boeing (NYSE: BA) said its chief executive, Harry "
        "Stonecipher, resigned after the board found an improper relationship with a female "
        "executive."
    )

    # when
    reading = study.read_article(text)

    # then
    assert reading == study.Reading("ceo", date(2005, 3, 7), time(12, 48), "BA")


def test_conduct_coming_out_while_the_ceo_stays_is_the_second_kind() -> None:
    # given
    text = (
        "The board said on Nov. 8, 2026 that it has hired outside counsel to look into "
        "allegations of sexual harassment against the chief executive, who denies them."
    )

    # when
    reading = study.read_article(text)

    # then
    assert reading is not None and reading.kind == study.CONDUCT_NO_DEPARTURE


def test_a_fraud_departure_and_a_retirement_are_not_a_measured_kind() -> None:
    # given
    fraud = (
        "The chief executive resigned on May 1, 2004 as regulators widened an inquiry into the "
        "company's accounting and restated three years of revenue."
    )
    retirement = (
        "After 30 years, the chief executive will retire at the end of the year, the company "
        "said on June 2, 2015, and the board has begun a search for a successor."
    )

    # when
    readings = [study.read_article(fraud), study.read_article(retirement)]

    # then
    assert readings == [None, None]


def test_a_ticker_is_read_from_its_exchange() -> None:
    # given
    texts = [
        "The chief executive resigned over personal conduct, said Boeing (NYSE: BA).",
        "Nvidia (Nasdaq: NVDA) said its CEO stays while a misconduct claim is looked into.",
        "The CEO resigned over personal conduct.",
    ]

    # when
    tickers = [r.ticker for r in map(study.read_article, texts) if r is not None]

    # then
    assert tickers == ["BA", "NVDA", ""]


def test_a_word_out_after_the_close_or_on_a_weekend_moves_to_the_next_trading_day() -> None:
    # given
    days = [date(2026, 11, 6), date(2026, 11, 9), date(2026, 11, 10)]
    after_close = study.Reading("ceo", date(2026, 11, 9), time(16, 5), "")
    before_close = study.Reading("ceo", date(2026, 11, 9), time(15, 59), "")
    sunday = study.Reading("ceo", date(2026, 11, 8), None, "")

    # when
    filed = [study.article_day(r, days) for r in (after_close, before_close, sunday)]

    # then
    assert filed == [date(2026, 11, 10), date(2026, 11, 9), date(2026, 11, 9)]


def test_a_text_dated_in_pacific_time_is_read_in_new_york() -> None:
    # given
    text = "Dec. 5, 2018 2:36 p.m. PT. The CEO resigned after allegations of misconduct."

    # when
    reading = study.read_article(text)

    # then
    assert reading is not None and (reading.day, reading.at) == (date(2018, 12, 5), time(17, 36))


def test_personal_reasons_or_an_inquiry_into_the_company_is_neither_kind() -> None:
    # given
    personal_reasons = "The chief executive resigned on March 2, 2010 for personal reasons."
    inquiry = (
        "Regulators opened an inquiry into the company's sales practices on May 4, 2016; "
        "the chief executive said the company would cooperate fully."
    )

    # when
    readings = [study.read_article(personal_reasons), study.read_article(inquiry)]

    # then
    assert readings == [None, None]


def test_calls_to_step_down_or_a_refusal_to_resign_are_not_a_departure() -> None:
    # given
    called = (
        "Shareholders called for the chief executive to step down after allegations of "
        "misconduct; the board backed him."
    )
    refused = (
        "The CEO said he has no plans to resign while the board reviews claims of an "
        "inappropriate relationship."
    )
    left = (
        "The chief executive resigned after an inquiry into an inappropriate relationship; "
        "investors had called for him to step down weeks earlier."
    )

    # when
    kinds = [r.kind if r else None for r in map(study.read_article, (called, refused, left))]

    # then
    assert kinds == [study.CONDUCT_NO_DEPARTURE, study.CONDUCT_NO_DEPARTURE, "ceo"]


def test_read_article_prints_the_second_kind_with_its_ticker_or_not_a_measured_kind(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given
    stays = tmp_path / "stays.txt"
    stays.write_text(
        "Nvidia (Nasdaq: NVDA) said on Nov. 8, 2026 that its board will investigate the chief "
        "executive's admitted affair; he remains in his role."
    )
    other = tmp_path / "other.txt"
    other.write_text("The chief executive retired on June 2, 2015 after 30 years.")

    # when
    codes = [main(["read-article", str(stays)]), main(["read-article", str(other)])]

    # then
    assert codes == [0, 0]
    assert capsys.readouterr().out.splitlines() == [
        "a CEO's conduct, no departure: not measured yet (NVDA)",
        "not a measured kind",
    ]


def test_rates_so_far_answers_each_prefix_as_its_lists_would() -> None:
    # given forty events in random order, one at a base where nothing moves (an unsigned share)
    rng = random.Random(7)
    bases = [
        Base(0.01, {UP: u, SAME: 1 - u - d, DOWN: d})
        for u, d in ((rng.uniform(0.1, 0.5), rng.uniform(0.1, 0.4)) for _ in range(40))
    ]
    bases[30] = Base(0.01, {UP: 0.0, SAME: 1.0, DOWN: 0.0})
    outcomes = [rng.choice((UP, SAME, DOWN, DOWN)) for _ in range(40)]
    outcomes[30] = DOWN
    so_far = study.RatesSoFar()

    for n, (outcome, base) in enumerate(zip(outcomes, bases, strict=True), start=1):
        # when each event is added to the ones before it
        so_far.add(outcome, base)
        answer, chance, counts = so_far.answer()

        # then the answer is the one built from the first n events' own lists
        said, kept = outcomes[:n], bases[:n]
        assert counts == {o: said.count(o) for o in (UP, SAME, DOWN)}
        if n < study.MIN_EVENT_DAYS:
            assert answer == TOO_FEW
            continue
        chances = {SAME: stats.poisson_binomial_tail(counts[SAME], [b.rates[SAME] for b in kept])}
        shares = [b.up_share for o, b in zip(said, kept, strict=True) if o != SAME]
        if not any(math.isnan(s) for s in shares):
            chances[UP] = stats.poisson_binomial_tail(counts[UP], shares)
            chances[DOWN] = stats.poisson_binomial_tail(counts[DOWN], [1 - s for s in shares])
        assert chance == min(chances.values())
        assert (UP in chances) == (n <= 30)


EARNINGS_LINE = re.compile(
    r"^(?P<kind>above|as expected|below)\s+(?P<span>day|week|month)\s+vs S&P 500\s+"
    r"(?P<n>\d+)\s+(?P<up>\d+)\s+(?P<same>\d+)\s+(?P<down>\d+)\s+\d+/\d+\s+"
    r"(?P<base>[\d.]+/[\d.]+/[\d.]+)\s+(?P<answer>up|down|about the same|can't say|too few)\s+"
    r"\S+\s+(?P<placebo>period|-)\s+(?P<graded>\d+): (?P<right>\d+) right, (?P<verdict>.+)$"
)


def test_the_page_s_earnings_cells_are_follows_lines_with_their_kinds_words(
    tmp_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a flat index and 36 companies, twelve of each kind, each 6% up or down on its report
    index = _closes([0.0] * 700)
    con = db.get_connection()
    rows = [("SPY / ES", c) for c in index]
    reports = ["day,time,ticker,eps,forecast,surprise,kind"]
    for n in range(36):
        kind = (study.ABOVE, study.AS_EXPECTED, study.BELOW)[n % 3]
        ticker, i = f"C{n}", 520 + 4 * n
        rows += [(ticker, c) for c in _company(n, i, 0.06 if kind == study.ABOVE else -0.06)]
        reports.append(f"{index[i].day},14:00,{ticker},1,1,0,{kind}")
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[i, c.day, c.price] for i, c in rows],
    )
    seed = tmp_path / "earnings.csv"
    seed.write_text("\n".join(reports) + "\n")
    flows.store_events(flows.EARNINGS_FLOW.load(seed, datetime(2026, 11, 19, tzinfo=UTC)).events)

    # when follows prints the earnings and the page's data is built
    assert main(["follows", "--event", "earnings"]) == 0
    printed = [EARNINGS_LINE.match(line) for line in capsys.readouterr().out.splitlines()[2:-1]]
    ask = cli.ask_data(con)

    # then every line is one cell, equal field by field, with its own kind's words and no "%"
    (earnings,) = [entry for entry in ask["ask"] if entry["name"] == "earnings"]
    cells = {(c["kind"], c["span"]): c for c in earnings["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 9
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        shares = [cell["base_up"], cell["base_same"], cell["base_down"]]
        assert "/".join(f"{s:.2f}" for s in shares) == line["base"]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert (cell["graded"], cell["right"]) == (int(line["graded"]), int(line["right"]))
        assert cell["period"] == (line["placebo"] == "period")
        assert str(cell["say"]).startswith(
            f"After {cli.ASK_DECISIONS['earnings'][line['kind']]}, the company against the S&P 500"
        )
        assert "%" not in str(cell["say"])
    assert [k["events"] for k in earnings["kinds"]] == [12, 12, 12]  # type: ignore[index]
    assert cells[(study.BELOW, "day")]["answer"] == study.DOWN


def test_a_cell_the_placebo_marks_says_so_and_is_left_uncoloured() -> None:
    # given one answer the placebo gives too, and the same answer it does not
    base = Base(0.01, {UP: 1 / 3, SAME: 1 / 3, DOWN: 1 / 3}, n=500)
    clean = study.Follow(
        {UP: 12, SAME: 0, DOWN: 0}, 0, 0, base, UP, 0.0001, False, 40, 30, 0.001, "holds"
    )
    marked = dataclasses.replace(clean, period=True)
    names = {study.EXCESS_MARKET: "the company against the S&P 500"}

    # when each is made a page cell
    cells = [
        cli.ask_cell("earnings", study.ABOVE, "day", study.EXCESS_MARKET, f, names)
        for f in (clean, marked)
    ]

    jobs = cli.ask_cell("nfp", study.ABOVE, "day", "EURUSD", marked, names)

    # then only the marked one carries the mark and its words, a jobs report's with the weekday,
    # and the page leaves it uncoloured
    assert [c["period"] for c in cells] == [False, True]
    assert str(cells[1]["say"]).endswith(cli.PERIOD_WORDS)
    assert cli.PERIOD_WORDS not in str(cells[0]["say"])
    assert str(jobs["say"]).endswith(cli.WEEKDAY_PERIOD_WORDS)
    page = (Path(cli.__file__).parent / "scoreboard.html").read_text()
    assert "!c.kind_cell && !c.period && c.answer" in page
    assert "c.verdict === 'holds' && !c.kind_cell && !c.period" in page


def test_load_prices_loads_the_companies_and_a_failing_one_does_not_fail_it(
    tmp_db: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given the markets loaded and Yahoo failing for one company alone
    asked: list[str] = []
    monkeypatch.setattr(cli, "company_tickers", lambda: ["AAA", "BAD"])
    monkeypatch.setattr(cli, "_fred_key", lambda _command: "key")
    monkeypatch.setattr(study, "load_daily_bars", lambda _key, con=None: None)
    monkeypatch.setattr(study, "store_observations", lambda con=None: {})

    def load(tickers: list[str], con: object = None) -> tuple[dict[str, int], list[str]]:
        asked.extend(tickers)
        return {"AAA": 700}, ["BAD: Yahoo returned HTTP 404 for BAD"]

    monkeypatch.setattr(study, "load_company_bars", load)
    store = db.get_connection()
    db.init_db(con=store)
    db.insert_models("event_instances", [])
    monkeypatch.setattr(db, "count_rows", lambda _table, con=None: 1)

    # when load-prices runs, and load-prices --companies
    full = main(["load-prices"])
    full_out = capsys.readouterr()
    alone = main(["load-prices", "--companies"])

    # then both ask for every company; the full load exits 0 and the companies' alone 1
    assert asked == ["AAA", "BAD", "AAA", "BAD"]
    assert (full, alone) == (0, 1)
    assert "1 of 2 companies loaded" in full_out.out
    assert "HTTP 404 for BAD" in full_out.err


ADDITIONS_LINE = re.compile(EARNINGS_LINE.pattern.replace("above|as expected|below", "added"))


def test_s_p_500_additions_load_one_event_each_and_follows_prints_one_kind(
    tmp_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a flat index and twelve companies each added 6% up on its announcement, two a day
    index = _closes([0.0] * 700)
    con = db.get_connection()
    rows = [("SPY / ES", c) for c in index]
    additions = ["day,time,ticker,kind,effective"]
    for n in range(12):
        ticker, i = f"C{n}", 520 + 8 * (n // 2)
        rows += [(ticker, c) for c in _company(n, i, 0.06)]
        additions.append(f"{index[i].day},14:00,{ticker},added,{index[i + 3].day}")
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[i, c.day, c.price] for i, c in rows],
    )
    seed = tmp_path / "sp500_additions.csv"
    seed.write_text("\n".join(additions) + "\n")

    # when the seed is loaded and follows prints the additions, and the page's data is built
    batch = flows.ADDITIONS_FLOW.load(seed, datetime(2026, 11, 19, tzinfo=UTC))
    flows.store_events(batch.events)
    assert main(["follows", "--event", "additions"]) == 0
    printed = [ADDITIONS_LINE.match(line) for line in capsys.readouterr().out.splitlines()[2:-1]]
    ask = cli.ask_data(con)

    # then one event an addition, two sharing a day; three spans of the one kind, the day up;
    # and not on the page's ask yet
    assert len(batch.events) == len({e.event_id for e in batch.events}) == 12
    assert [m["span"] for m in printed if m] == ["day", "week", "month"]
    assert {m["kind"] for m in printed if m} == {study.ADDED}
    assert printed[0] is not None and printed[0]["answer"] == "up"
    assert "additions" not in [entry["name"] for entry in ask["ask"]]


def test_the_companies_loaded_each_evening_include_the_s_p_500_additions() -> None:
    # given the three company seeds
    with (settings.seed_dir / "sp500_additions.csv").open(newline="") as handle:
        added = {row["ticker"] for row in csv.DictReader(handle)}

    # when the evening's companies are listed
    tickers = cli.company_tickers()

    # then every addition's company is among them, once
    assert added <= set(tickers)
    assert len(tickers) == len(set(tickers))


def test_s_p_500_earnings_load_one_event_a_report_and_follows_prints_the_misses(
    tmp_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a flat index and twelve companies, each reporting a miss and falling 6%
    index = _closes([0.0] * 700)
    con = db.get_connection()
    rows = [("SPY / ES", c) for c in index]
    reports = ["day,time,ticker,eps,forecast,surprise,kind"]
    for n in range(12):
        ticker, i = f"C{n}", 520 + 8 * (n // 2)
        rows += [(ticker, c) for c in _company(n, i, -0.06)]
        reports.append(f"{index[i].day},14:00,{ticker},0.90,1.00,-10.0,below")
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[i, c.day, c.price] for i, c in rows],
    )
    seed = tmp_path / "earnings_sp500.csv"
    seed.write_text("\n".join(reports) + "\n")

    # when the seed is loaded and follows prints the S&P 500's earnings, and the page's data is built
    batch = flows.EARNINGS_500_FLOW.load(seed, datetime(2026, 11, 19, tzinfo=UTC))
    flows.store_events(batch.events)
    assert main(["follows", "--event", "earnings500"]) == 0
    printed = [EARNINGS_LINE.match(line) for line in capsys.readouterr().out.splitlines()]
    ask = cli.ask_data(con)

    # then one event a report; the misses' three spans, the day down; and not on the page's ask
    cells = [m for m in printed if m]
    assert len(batch.events) == len({e.event_id for e in batch.events}) == 12
    assert [(m["kind"], m["span"]) for m in cells] == [
        ("below", "day"),
        ("below", "week"),
        ("below", "month"),
    ]
    day_below = [m for m in cells if m["kind"] == "below" and m["span"] == "day"]
    assert day_below[0]["answer"] == "down"
    assert "earnings500" not in [entry["name"] for entry in ask["ask"]]


def test_load_prices_with_a_seed_loads_that_seed_s_companies_and_the_evening_s_are_unchanged(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a seed of three reports by two companies
    seed = tmp_path / "reports.csv"
    seed.write_text(
        "day,time,ticker,kind\n2020-01-02,14:00,AAA,below\n2020-04-02,14:00,BBB,above\n"
        "2020-07-02,14:00,AAA,above\n"
    )
    asked: list[str] = []

    def load(tickers: list[str], con: object = None) -> tuple[dict[str, int], list[str]]:
        asked.extend(tickers)
        return dict.fromkeys(tickers, 700), []

    monkeypatch.setattr(study, "load_company_bars", load)
    db.init_db(con=db.get_connection())

    # when load-prices --companies --seed runs, and the evening's companies are listed
    code = main(["load-prices", "--companies", "--seed", str(seed)])
    evening = cli.company_tickers()

    # then the seed's two companies are asked, once each, and the evening's list does not read
    # the S&P 500's earnings
    with (settings.seed_dir / "earnings_sp500.csv").open(newline="") as handle:
        sp500 = {row["ticker"] for row in csv.DictReader(handle)}
    seeds = (flows.CEO_FLOW, flows.EARNINGS_FLOW, flows.ADDITIONS_FLOW)
    named: set[str] = set()
    for name in (flow.seed_file for flow in seeds):
        with (settings.seed_dir / name).open(newline="") as handle:
            named |= {row["ticker"] for row in csv.DictReader(handle) if row.get("ticker")}
    assert (code, asked) == (0, ["AAA", "BBB"])
    assert set(evening) <= named
    assert not sp500 <= set(evening)
    with (settings.seed_dir / flows.SPLITS_FLOW.seed_file).open(newline="") as handle:
        split = {row["ticker"] for row in csv.DictReader(handle)}
    assert not split <= set(evening)


def test_stock_splits_load_one_event_a_split_and_follows_prints_the_two_kinds(
    tmp_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a flat index and twelve companies, each announcing a split and rising 6%, six alone
    index = _closes([0.0] * 700)
    con = db.get_connection()
    rows = [("SPY / ES", c) for c in index]
    splits = ["day,time,ticker,ratio,split_day,kind,accession"]
    for n in range(12):
        ticker, i = f"C{n}", 520 + 8 * (n // 2)
        rows += [(ticker, c) for c in _company(n, i, 0.06)]
        kind = "alone" if n % 2 else "with a report"
        splits.append(f"{index[i].day},14:00,{ticker},2-for-1,{index[i + 20].day},{kind},x")
    con.executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[i, c.day, c.price] for i, c in rows],
    )
    seed = tmp_path / "stock_splits.csv"
    seed.write_text("\n".join(splits) + "\n")

    # when the seed is loaded and follows prints the splits, and the page's data is built
    batch = flows.SPLITS_FLOW.load(seed, datetime(2026, 11, 19, tzinfo=UTC))
    flows.store_events(batch.events)
    assert main(["follows", "--event", "splits"]) == 0
    pattern = re.compile(
        EARNINGS_LINE.pattern.replace("above|as expected|below", "alone|with a report")
    )
    printed = [pattern.match(line) for line in capsys.readouterr().out.splitlines()]
    ask = cli.ask_data(con)

    # then one event a split; the two kinds' three spans each, in their order; not on the ask
    cells = [m for m in printed if m]
    assert len(batch.events) == len({e.event_id for e in batch.events}) == 12
    assert [(m["kind"], m["span"]) for m in cells] == [
        (kind, span) for kind in study.SPLIT_KINDS for span in ("day", "week", "month")
    ]
    assert "splits" not in [entry["name"] for entry in ask["ask"]]
