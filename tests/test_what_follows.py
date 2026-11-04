from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, flows, sources, stats, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import DailyClosingPrice
from fortuneteller.study import CANT_SAY, CUT, DOWN, HIKE, HOLD, SAME, TOO_FEW, UP

START = date(2001, 1, 1)


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


def _alternating(n: int) -> list[float]:
    return [0.01 if i % 2 == 0 else -0.01 for i in range(n)]


def _decision(day: date) -> flows.EventInstance:
    return flows.fomc_event_instance(sources.FomcDecision(day, True))


def test_a_decision_s_kind_is_read_from_the_target_rate_either_side() -> None:
    # given four decisions: the target unchanged, lower, higher, and one with no rate after
    days = [date(2019, 6, 19), date(2019, 7, 31), date(2022, 3, 16), date(2026, 10, 28)]
    rates = {
        date(2019, 6, 18): 2.5,
        date(2019, 6, 22): 2.5,
        date(2019, 7, 30): 2.5,
        date(2019, 8, 3): 2.25,
        date(2022, 3, 15): 0.25,
        date(2022, 3, 19): 0.5,
        date(2026, 10, 27): 4.0,
    }

    # when each is given its kind
    kinds = study.fed_kinds([_decision(day) for day in days], rates)

    # then a hold, a cut and a hike, and the last has none
    assert list(kinds.values()) == [HOLD, CUT, HIKE]
    assert len(kinds) == 3


def test_a_span_with_a_hole_is_skipped_and_a_decision_s_span_is_the_base_span() -> None:
    # given closes with a five-day gap after the tenth
    closes = _closes(_alternating(20))
    closes = closes[:10] + [
        DailyClosingPrice(c.day + timedelta(days=7), c.price) for c in closes[10:]
    ]

    # when the week spans are read
    spans = study.span_moves(closes, "pct", 5)

    # then the spans across the gap are skipped, and one keyed on the reaction close starts the
    # close before it
    assert closes[3].day in spans and closes[8].day not in spans
    assert spans[closes[11].day].start == closes[10].day
    assert spans[closes[11].day].end == closes[15].day


def test_a_decision_is_left_out_only_if_it_overlaps_the_last_one_kept() -> None:
    # given three month decisions, the second overlapping the first and the third only the
    # second, and a fourth starting on the last kept span's end close
    closes = _closes(_alternating(200))
    days = [c.day for c in closes]
    decisions = [(days[10], HOLD), (days[20], HOLD), (days[35], HOLD), (days[56], HOLD)]

    # when the month is followed
    follow = study.follow_market(decisions, closes, "pct", 21)[HOLD]

    # then the second is left out and the third and fourth counted
    assert follow.overlapped == 1
    assert sum(follow.counts.values()) == 3


def test_a_market_that_only_moves_more_after_decisions_has_no_direction() -> None:
    # given day moves of 1% either way, and twenty decisions on which it moves 2%, as often up as
    # down
    steps = _alternating(600)
    keys = list(range(100, 500, 20))
    for n, i in enumerate(keys):
        steps[i] = 0.02 if n % 2 == 0 else -0.02
    closes = _closes(steps)

    # when the day is followed
    follow = study.follow_market([(closes[i].day, HIKE) for i in keys], closes, "pct", 1)[HIKE]

    # then the answer is no direction
    assert follow.answer == CANT_SAY


def test_a_rise_after_each_decision_reads_up() -> None:
    # given closes alternating 1% either way, rising 3% more over each of 12 decisions' months
    steps = _alternating(1500)
    keys = list(range(200, 1400, 100))
    for i in keys:
        for k in range(i, i + 21):
            steps[k] += 0.03 / 21
    closes = _closes(steps)

    # when the month is followed
    follow = study.follow_market([(closes[i].day, CUT) for i in keys], closes, "pct", 21)[CUT]

    # then every decision's month went up, and the answer is up
    assert follow.counts == {UP: 12, SAME: 0, DOWN: 0}
    assert follow.answer == UP


def test_the_answer_needs_ten_events_and_a_chance_under_the_bar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given ten events all up, a same rate of a quarter, and up half of the base spans that moved
    counts = {UP: 10, SAME: 0, DOWN: 0}

    # when answered with ten, nine, and a bar equal to the chance
    ten = study.span_answer(counts, 0.25, 0.5)
    nine = study.span_answer({UP: 9, SAME: 0, DOWN: 0}, 0.25, 0.5)
    monkeypatch.setattr(study, "FOLLOW_P_BAR", ten[1])
    at_bar = study.span_answer(counts, 0.25, 0.5)

    # then up at 0.5^10, too few, and no answer at the bar itself
    assert ten == (UP, pytest.approx(0.5**10))
    assert nine[0] == TOO_FEW
    assert at_bar[0] == CANT_SAY


def test_the_walk_forward_answer_uses_nothing_after_the_decision() -> None:
    # given 12 month decisions on closes that rise after each
    steps = _alternating(900)
    keys = list(range(200, 800, 50))
    for i in keys:
        for k in range(i, i + 21):
            steps[k] += 0.03 / 21
    closes = _closes(steps)
    last = keys[-1]

    def answer(cl: list[DailyClosingPrice]) -> tuple[str, study.Base] | None:
        spans = study.span_moves(cl, "pct", 21)
        by_end = sorted(spans.items(), key=lambda item: item[1].end)
        return study.answer_before([cl[i].day for i in keys], len(keys) - 1, spans, by_end)

    # when every close from the last decision's reaction on is changed
    changed = closes[:last] + [DailyClosingPrice(c.day, c.price * 3) for c in closes[last:]]

    # then its answer, cut and rates are the same
    before, after = answer(closes), answer(changed)
    assert before is not None and before == after


def test_decisions_that_stand_for_their_period_are_marked_by_the_placebo() -> None:
    # given closes alternating 1% either way, but rising every day for one stretch, and twelve
    # decisions inside that stretch
    steps = _alternating(2400)
    for k in range(400, 760):
        steps[k] = 0.004
    closes = _closes(steps)
    keys = list(range(420, 720, 25))

    # when the week is followed
    follow = study.follow_market([(closes[i].day, HOLD) for i in keys], closes, "pct", 5)[HOLD]

    # then the answer is up, and the placebo says it is the period's
    assert follow.answer == UP
    assert follow.period


def test_the_chance_with_its_own_rates_is_the_binomial_when_they_are_equal() -> None:
    # given ten tries at 0.3
    # when 6 or more right is counted both ways
    # then the two agree
    assert stats.poisson_binomial_tail(6, [0.3] * 10) == pytest.approx(
        stats.binomial_tail(6, 10, 0.3)
    )


def test_follows_prints_the_table_and_needs_the_key(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given two Fed decisions, one market's closes, and FRED's target rate patched
    db.init_db()
    flows.store_fomc_decisions(
        [
            sources.FomcDecision(date(2001, 3, 20), True),
            sources.FomcDecision(date(2001, 5, 15), True),
        ]
    )
    closes = _closes(_alternating(300))
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    rates = {date(2001, 3, 19): 5.5, date(2001, 3, 23): 5.0, date(2001, 5, 14): 4.5}
    monkeypatch.setattr(flows, "target_rates", lambda api_key: list(rates.items()))
    monkeypatch.setattr(settings, "fred_api_key", None)

    # when run without a key, then with one
    without = main(["follows"])
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))
    code = main(["follows"])

    # then the first fails, and the second prints the header, a cut's day and the chance line
    out = capsys.readouterr().out.splitlines()
    assert (without, code) == (1, 0)
    assert out[0] == "follows: 2 Fed decisions 2001-03-20 … 2001-05-15: 1 cuts, 0 holds, 0 hikes"
    assert out[2].startswith("cut   day    SPY / ES       1   ")
    assert out[2].endswith("too few")
    assert out[-1] == "by chance: about 0.0 answers on all history, 0.0 holds walk-forward"
