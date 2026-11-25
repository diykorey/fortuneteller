import math
import random
import re
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, flows, sources, stats, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import describe_follows, main
from fortuneteller.config import settings
from fortuneteller.models import Surprise
from fortuneteller.sources import DailyClosingPrice
from fortuneteller.study import (
    ABOVE,
    AS_EXPECTED,
    BELOW,
    CANT_SAY,
    CUT,
    DOWN,
    HIKE,
    HOLD,
    SAME,
    TOO_FEW,
    UP,
)

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
    # given five decisions: the target unchanged, lower, higher, one with no rate after and one
    # with none before
    days = [
        date(2019, 6, 19),
        date(2019, 7, 31),
        date(2022, 3, 16),
        date(2026, 10, 28),
        date(2023, 1, 4),
    ]
    rates = {
        date(2019, 6, 18): 2.5,
        date(2019, 6, 22): 2.5,
        date(2019, 7, 30): 2.5,
        date(2019, 8, 3): 2.25,
        date(2022, 3, 15): 0.25,
        date(2022, 3, 19): 0.5,
        date(2026, 10, 27): 4.0,
        date(2023, 1, 7): 4.5,
    }

    # when each is given its kind
    kinds = study.fed_kinds([_decision(day) for day in days], rates)

    # then a hold, a cut and a hike, and the last two have none
    assert list(kinds.values()) == [HOLD, CUT, HIKE]
    assert len(kinds) == 3


def test_a_span_with_a_hole_is_skipped_and_a_decision_s_span_is_the_base_span() -> None:
    # given closes with a five-day gap after the tenth
    closes = _closes(_alternating(20))
    shift = timedelta(days=5 - (closes[10].day - closes[9].day).days)
    closes = closes[:10] + [DailyClosingPrice(c.day + shift, c.price) for c in closes[10:]]
    assert (closes[10].day - closes[9].day).days == 5

    # when the week spans are read
    spans = study.span_moves(closes, "pct", 5)

    # then the spans across the gap are skipped, and one keyed on the reaction close starts the
    # close before it
    assert closes[3].day in spans and closes[8].day not in spans
    assert spans[closes[11].day].start == closes[10].day
    assert spans[closes[11].day].end == closes[15].day


def test_a_decision_is_left_out_only_if_it_overlaps_the_last_one_kept() -> None:
    # given month decisions: a cut overlapping a hold, a hold overlapping only the cut, a hold
    # starting on the last kept span's end close, and one after the last close
    closes = _closes(_alternating(200))
    days = [c.day for c in closes]
    decisions = [
        (days[10], HOLD),
        (days[20], CUT),
        (days[35], HOLD),
        (days[56], HOLD),
        (days[-1] + timedelta(days=1), HOLD),
    ]

    # when the month is followed
    follows = study.follow_market(decisions, closes, "pct", 21)

    # then the cut is left out for overlapping a hold, the third and fourth are counted, and the
    # one after the last close is neither counted nor a hole
    assert (follows[CUT].overlapped, follows[HOLD].overlapped) == (1, 0)
    assert sum(follows[HOLD].counts.values()) == 3
    assert follows[HOLD].holes == 0


def _gaussian(n: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(0, 0.01) for _ in range(n)]


def test_a_market_that_only_moves_more_after_decisions_has_no_direction() -> None:
    # given day moves of about 1% either way, and sixty decisions on which it moves 2.5%, up on 33
    steps = _gaussian(3000, 1)
    keys = list(range(100, 2900, 46))[:60]
    for n, i in enumerate(keys):
        steps[i] = 0.025 if n < 33 else -0.025
    closes = _closes(steps)

    # when the day is followed
    follow = study.follow_market([(closes[i].day, HIKE) for i in keys], closes, "pct", 1)[HIKE]

    # then there is no direction, though testing up on all sixty against up's base rate would say
    # up
    assert follow.base is not None
    assert stats.binomial_tail(33, 60, follow.base.rates[UP]) < study.FOLLOW_P_BAR
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

    # when every close from the last decision's reaction on is changed, unevenly
    changed = closes[:last] + [
        DailyClosingPrice(c.day, c.price * (1 + (k % 7) / 10)) for k, c in enumerate(closes[last:])
    ]

    # then its answer, cut and rates are the same, and the tenth decision, with nine before it,
    # has none
    before, after = answer(closes), answer(changed)
    assert before is not None and before == after
    spans = study.span_moves(closes, "pct", 21)
    by_end = sorted(spans.items(), key=lambda item: item[1].end)
    assert study.answer_before([closes[i].day for i in keys], 9, spans, by_end) is None


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


def test_decisions_whose_own_day_moves_are_not_the_period() -> None:
    # given day moves of about 1% either way, and a 2% rise on each of 70 decisions' days
    steps = _gaussian(3000, 2)
    keys = list(range(100, 2900, 40))[:70]
    for i in keys:
        steps[i] = 0.02
    closes = _closes(steps)

    # when the day is followed
    follow = study.follow_market([(closes[i].day, HOLD) for i in keys], closes, "pct", 1)[HOLD]

    # then the answer is up, and the placebo does not say it
    assert follow.answer == UP
    assert not follow.period


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

    # then the first fails, and the second prints the header of the decision with a kind, a cut's
    # day and the chance line
    out = capsys.readouterr().out.splitlines()
    assert (without, code) == (1, 0)
    assert out[0] == "follows: 1 Fed decisions 2001-03-20 … 2001-03-20: 1 cuts, 0 holds, 0 hikes"
    assert out[2].startswith("cut   day    SPY / ES       1   ")
    assert out[2].endswith("too few")
    assert out[-1] == "by chance: about 0.0 answers on all history, 0.0 holds walk-forward"


NFP = flows.flow_named("nfp")
RETAIL = flows.flow_named("retail")
CPI = flows.flow_named("cpi")
CLAIMS = flows.flow_named("claims")


def _report(day: date, flow: flows.EventFlow = NFP) -> flows.EventInstance:
    # a release of ``flow`` at 08:30 New York on ``day``
    at = datetime.combine(day, time(8, 30), tzinfo=sources.NEW_YORK)
    return _decision(day).model_copy(
        update={
            "event_id": flows.event_id(flow, day),
            "event_type": flow.event_type,
            "event_ts": at.astimezone(UTC).replace(tzinfo=None),
        }
    )


def _store_reports(
    surprises: list[tuple[date, str, float]],
    flow: flows.EventFlow = NFP,
    measure: str = "payrolls",
    values: Mapping[date, tuple[float, float]] | None = None,
) -> None:
    # each release with one surprise row: (day, baseline, surprise in the measure's unit)
    db.init_db()
    reports = {day: _report(day, flow) for day, _, _ in surprises}
    db.insert_models("event_instances", list(reports.values()))
    db.insert_models(
        "surprises",
        [
            Surprise(
                event_id=reports[day].event_id,
                measure=measure,
                baseline=baseline,
                actual_mom=(values or {}).get(day, (0.0, 0.0))[0],
                expected_mom=(values or {}).get(day, (0.0, 0.0))[1],
                surprise=surprise,
            )
            for day, baseline, surprise in surprises
        ],
    )


def test_a_report_s_kind_is_read_from_its_consensus_surprise(tmp_db: Path) -> None:
    # given reports 50k, 49.9k, -50k and -49.9k off the consensus, one with only a trend surprise
    # of 200k, and one whose consensus surprise is missing
    days = [
        date(2024, 1, 5),
        date(2024, 2, 2),
        date(2024, 3, 8),
        date(2024, 4, 5),
        date(2024, 5, 3),
        date(2024, 6, 7),
    ]
    _store_reports(
        [
            (days[0], "nasdaq_consensus", 50.0),
            (days[1], "nasdaq_consensus", 49.9),
            (days[2], "nasdaq_consensus", -50.0),
            (days[3], "nasdaq_consensus", -49.9),
            (days[4], "trend_12m", 200.0),
            (days[5], "nasdaq_consensus", 0.0),
        ]
    )
    db.get_connection().execute(
        "UPDATE surprises SET surprise = NULL WHERE event_id = ?", [flows.event_id(NFP, days[5])]
    )

    # when the kinds are read
    kinds = study.release_kinds(NFP)

    # then above, as expected, below, as expected, and the last two have none
    assert [kinds.get(flows.event_id(NFP, day)) for day in days] == [
        ABOVE,
        AS_EXPECTED,
        BELOW,
        AS_EXPECTED,
        None,
        None,
    ]


def test_a_release_that_moves_a_market_whatever_it_says_answers_for_every_kind() -> None:
    # given day moves of about 1% either way, and a 3% fall on every report's day, fifteen of each
    # kind
    steps = _gaussian(3000, 3)
    keys = list(range(100, 2900, 60))[:45]
    for i in keys:
        steps[i] = -0.03
    closes = _closes(steps)
    order = [ABOVE, AS_EXPECTED, BELOW]
    reports = [(closes[i].day, order[n % 3]) for n, i in enumerate(keys)]

    # when the day is followed
    follows = study.follow_market(reports, closes, "pct", 1, study.SURPRISE_KINDS)

    # then every kind answers down: the release's, not the kind's
    assert [follows[kind].answer for kind in order] == [DOWN, DOWN, DOWN]


def test_the_fed_table_is_unchanged() -> None:
    # given three made-up Fed decisions, a cut, a hold and a hike, on one market's closes
    closes = _closes(_alternating(300))
    events = [_decision(closes[i].day) for i in (20, 60, 100)]
    kinds = dict(zip((e.event_id for e in events), (CUT, HOLD, HIKE), strict=True))
    series = study.MVP_PRICE_SERIES["SPY / ES"]
    decisions = [(study.first_reaction_day(e, series), kinds[e.event_id]) for e in events]
    by_span = {
        span: study.follow_market(decisions, closes, series.unit, c)
        for span, c in study.SPANS.items()
    }
    cells = [
        (kind, span, "SPY / ES", by_span[span][kind])
        for kind in study.KINDS
        for span in study.SPANS
    ]

    # when the table is described
    lines = describe_follows(events, kinds, cells)

    # then its first lines are those printed before the release kinds were added
    assert lines[:3] == [
        "follows: 3 Fed decisions 2001-01-29 … 2001-05-21: 1 cuts, 1 holds, 1 hikes",
        "kind  span   market        n  up same down  out/hole  base up/same/down  answer          "
        "chance  placebo  walk-forward",
        "cut   day    SPY / ES       1   1    0    0      0/0  0.50/0.07/0.42     too few         "
        "—       -        0: 0 right, too few",
    ]


def test_follows_for_the_jobs_report_needs_no_key_but_its_surprises(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no FRED key, one market's closes, and three reports, then their surprises
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.insert_models("event_instances", [_report(day) for day in days])
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )

    # when run before the surprises are stored, then after
    before = main(["follows", "--event", "nfp"])
    err = capsys.readouterr().err
    db.get_connection().execute("DELETE FROM event_instances")
    _store_reports(
        [(days[0], "nasdaq_consensus", 60.0), (days[1], "nasdaq_consensus", 0.0)]
        + [(days[2], "nasdaq_consensus", -60.0)]
    )
    after = main(["follows", "--event", "nfp"])

    # then the first asks for the surprises, and the second prints the jobs reports' table
    out = capsys.readouterr().out.splitlines()
    assert (before, after) == (1, 0)
    assert "follows: no surprises for nfp yet; run `fortuneteller load-surprises` first" in err
    assert out[0] == (
        "follows: 3 jobs reports 2001-01-29 … 2001-05-21: 1 above, 1 as expected, 1 below"
    )
    assert out[1].startswith("kind        span   market")
    assert out[2].startswith("above       day    SPY / ES       1   ")


def test_a_retail_release_s_kind_is_read_at_its_own_threshold(tmp_db: Path) -> None:
    # given retail sales releases 0.3, 0.29, -0.3 and -0.29pp off the consensus
    days = [date(2024, 1, 17), date(2024, 2, 15), date(2024, 3, 14), date(2024, 4, 15)]
    _store_reports(
        [
            (days[0], "nasdaq_consensus", 0.3),
            (days[1], "nasdaq_consensus", 0.29),
            (days[2], "nasdaq_consensus", -0.3),
            (days[3], "nasdaq_consensus", -0.29),
        ],
        RETAIL,
        "retail_sales",
    )

    # when the kinds are read
    kinds = study.release_kinds(RETAIL)

    # then the 0.3pp line, not another flow's, separates them
    assert [kinds[flows.event_id(RETAIL, day)] for day in days] == [
        ABOVE,
        AS_EXPECTED,
        BELOW,
        AS_EXPECTED,
    ]


def test_follows_for_retail_sales_prints_its_table(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no FRED key, one market's closes, and three retail sales releases with surprises
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    _store_reports(
        [(days[0], "nasdaq_consensus", 0.4), (days[1], "nasdaq_consensus", 0.0)]
        + [(days[2], "nasdaq_consensus", -0.4)],
        RETAIL,
        "retail_sales",
    )

    # when run
    code = main(["follows", "--event", "retail"])

    # then it prints the retail sales releases' table
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (
        "follows: 3 retail sales releases 2001-01-29 … 2001-05-21: 1 above, 1 as expected, 1 below"
    )
    assert out[2].startswith("above       day    SPY / ES       1   ")


def test_a_cpi_release_s_kind_is_read_from_its_headline(tmp_db: Path) -> None:
    # given core CPI actuals against a 0.2 consensus, each stored with a surprise of 0, and one
    # with no surprise
    actuals = [0.281, 0.249, 0.151, 0.149, 0.25, 0.2499, 0.3]
    days = [date(2024, month, 12) for month in range(1, len(actuals) + 1)]
    values = dict(zip(days, [(actual, 0.2) for actual in actuals], strict=True))
    _store_reports([(day, "nasdaq_consensus", 0.0) for day in days], CPI, "core", values)
    db.get_connection().execute(
        "UPDATE surprises SET surprise = NULL WHERE event_id = ?", [flows.event_id(CPI, days[-1])]
    )

    # when the kinds are read
    kinds = study.release_kinds(CPI)

    # then each is read from its actual rounded half up to 0.1, and the last has none
    assert [kinds.get(flows.event_id(CPI, day)) for day in days] == [
        ABOVE,
        AS_EXPECTED,
        AS_EXPECTED,
        BELOW,
        ABOVE,
        AS_EXPECTED,
        None,
    ]


def test_the_headline_rounding_is_cpi_s_alone(tmp_db: Path) -> None:
    # given a retail sales release 0.46 against 0.2, 0.26 off unrounded and 0.3 off rounded
    day = date(2024, 1, 17)
    _store_reports([(day, "nasdaq_consensus", 0.26)], RETAIL, "retail_sales", {day: (0.46, 0.2)})

    # when its kind is read
    kinds = study.release_kinds(RETAIL)

    # then it is as expected at retail sales' 0.3 line
    assert kinds[flows.event_id(RETAIL, day)] == AS_EXPECTED


def test_follows_for_cpi_prints_its_table(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no FRED key, one market's closes, and three CPI releases at 0.281, 0.2 and 0.0 against
    # a 0.2 consensus
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    values = {days[0]: (0.281, 0.2), days[1]: (0.2, 0.2), days[2]: (0.0, 0.2)}
    _store_reports([(day, "nasdaq_consensus", 0.0) for day in days], CPI, "core", values)

    # when run
    code = main(["follows", "--event", "cpi"])

    # then it prints the CPI releases' table, the first release above from its headline
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert (
        out[0] == "follows: 3 CPI releases 2001-01-29 … 2001-05-21: 1 above, 1 as expected, 1 below"
    )
    assert out[2].startswith("above       day    SPY / ES       1   ")


def _rise_then_fall(n: int, keys: list[int]) -> list[DailyClosingPrice]:
    # closes alternating 1% either way, rising 3% on each key and falling 3% the close after
    steps = _alternating(n)
    for i in keys:
        steps[i], steps[i + 1] = 0.03, -0.03
    return _closes(steps)


def test_after_the_day_reads_the_close_after_the_reaction() -> None:
    # given 12 events whose day rises 3% and whose next day falls 3%
    keys = list(range(100, 1300, 100))
    closes = _rise_then_fall(1400, keys)
    decisions = [(closes[i].day, CUT) for i in keys]

    # when the day is followed from the close before, and from the reaction close
    on = study.follow_market(decisions, closes, "pct", 1)[CUT]
    after = study.follow_market(decisions, closes, "pct", 1, after=True)[CUT]

    # then the day itself is up, and the day after is down
    assert (on.answer, after.answer) == (UP, DOWN)
    assert after.counts == {UP: 0, SAME: 0, DOWN: 12}


def test_an_event_on_the_last_close_has_no_span_after_its_day_yet() -> None:
    # given closes and one event on the last of them
    closes = _closes(_alternating(100))

    # when the day after is followed
    follow = study.follow_market([(closes[-1].day, HOLD)], closes, "pct", 1, after=True)[HOLD]

    # then it is counted nowhere, not even as a hole
    assert sum(follow.counts.values()) == 0
    assert (follow.overlapped, follow.holes) == (0, 0)


def test_a_placebo_after_the_day_never_lands_on_another_event_s_day_after() -> None:
    # given day moves of about 0.1% either way, and a 3% rise on the close after each of 15 events,
    # ten closes apart
    steps = [s / 10 for s in _gaussian(400, 3)]
    keys = list(range(100, 250, 10))
    for i in keys:
        steps[i + 1] = 0.03
    closes = _closes(steps)

    # when the day after is followed
    follow = study.follow_market(
        [(closes[i].day, HOLD) for i in keys], closes, "pct", 1, after=True
    )[HOLD]

    # then it is up and not the period: a placebo ten closes away would be the next event's day
    # after, and is skipped
    assert follow.answer == UP
    assert not follow.period


def test_a_month_placebo_after_the_day_holds_no_reaction_close() -> None:
    # given closes alternating 0.1% either way, 12 events 101 closes apart whose day rises 5% and
    # whose next month rises 3% more
    steps = [s / 10 for s in _alternating(1500)]
    keys = list(range(100, 1300, 101))
    for i in keys:
        steps[i] = 0.05
        for k in range(i + 1, i + 22):
            steps[k] += 0.03 / 21
    closes = _closes(steps)

    # when the month after the day is followed
    follow = study.follow_market(
        [(closes[i].day, HOLD) for i in keys], closes, "pct", 21, after=True
    )[HOLD]

    # then it is up and not the period: a placebo 21 closes back would end on the reaction close
    # and read its 5% rise as up
    assert follow.answer == UP
    assert not follow.period


def test_the_walk_forward_answer_after_the_day_reads_nothing_after_the_reaction_close() -> None:
    # given 12 events whose next month rises, keyed on the close after each reaction
    steps = _alternating(900)
    keys = list(range(200, 800, 50))
    for i in keys:
        for k in range(i + 1, i + 22):
            steps[k] += 0.03 / 21
    closes = _closes(steps)
    last = keys[-1]

    def answer(cl: list[DailyClosingPrice]) -> tuple[str, study.Base] | None:
        spans = study.span_moves(cl, "pct", 21)
        by_end = sorted(spans.items(), key=lambda item: item[1].end)
        return study.answer_before([cl[i + 1].day for i in keys], len(keys) - 1, spans, by_end)

    # when every close after the last reaction close is changed, and then that close itself
    later = closes[: last + 1] + [
        DailyClosingPrice(c.day, c.price * (1 + (k % 7 + 1) / 10))
        for k, c in enumerate(closes[last + 1 :])
    ]
    itself = [*closes[:last], DailyClosingPrice(closes[last].day, closes[last].price * 1.5)]
    itself += closes[last + 1 :]

    # then the later closes change nothing, and the reaction close changes the base
    before = answer(closes)
    assert before is not None and before == answer(later)
    changed = answer(itself)
    assert changed is not None and changed[1] != before[1]


def test_follows_after_the_day_says_so_in_its_header(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no FRED key, one market's closes, and three retail sales releases with surprises
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    _store_reports(
        [(days[0], "nasdaq_consensus", 0.4), (days[1], "nasdaq_consensus", 0.0)]
        + [(days[2], "nasdaq_consensus", -0.4)],
        RETAIL,
        "retail_sales",
    )

    # when run with the flag
    code = main(["follows", "--event", "retail", "--after-the-day"])

    # then the header says the spans start at the reaction close
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (
        "follows: 3 retail sales releases 2001-01-29 … 2001-05-21: 1 above, 1 as expected, "
        "1 below, spans from the reaction close"
    )
    assert out[2].startswith("above       day    SPY / ES       1   ")


def test_follows_for_jobless_claims_prints_its_table_at_its_own_threshold(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given no FRED key, one market's closes, and claims reports 5k, 4k and -5k off the consensus
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    _store_reports(
        [(days[0], "nasdaq_consensus", 5.0), (days[1], "nasdaq_consensus", 4.0)]
        + [(days[2], "nasdaq_consensus", -5.0)],
        CLAIMS,
        sources.INITIAL_CLAIMS,
    )

    # when run
    code = main(["follows", "--event", "claims"])

    # then it prints the claims reports' table, the 5k line separating the kinds
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (
        "follows: 3 jobless claims reports 2001-01-29 … 2001-05-21: 1 above, 1 as expected, 1 below"
    )
    assert out[2].startswith("above       day    SPY / ES       1   ")


def _ecb(day: date) -> flows.EventInstance:
    # an ECB decision at 14:15 Frankfurt on ``day``
    return flows.ecb_event_instance(
        datetime.combine(day, time(14, 15), tzinfo=sources.FRANKFURT).astimezone(UTC)
    )


def test_an_ecb_decision_s_kind_is_its_rate_against_the_previous_decision_s() -> None:
    # given four decisions, the third with no rate
    days = [date(2024, 4, 11), date(2024, 6, 6), date(2024, 7, 18), date(2024, 9, 12)]
    rates = {days[0]: 4.0, days[1]: 3.75, days[3]: 3.75}

    # when their kinds are read
    kinds = study.ecb_kinds([_ecb(d) for d in reversed(days)], rates)

    # then the first has none, the second is a cut, the third none, and the fourth a hold against
    # the last decision with a rate
    assert kinds == {_ecb(days[1]).event_id: CUT, _ecb(days[3]).event_id: HOLD}


def test_follows_for_the_ecb_prints_its_table(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given three ECB decisions, one market's closes, and the calendar's rates patched
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    db.insert_models("event_instances", [_ecb(d) for d in days])
    rates = {days[0]: 1.0, days[1]: 1.25, days[2]: 1.25}
    monkeypatch.setattr(flows, "load_ecb_rates", lambda _cache_dir: rates)

    # when run
    code = main(["follows", "--event", "ecb"])

    # then it prints the ECB decisions' table, the first decision having no kind
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (f"follows: 2 ECB decisions {days[1]} … {days[2]}: 0 cuts, 1 holds, 1 hikes")


def test_cycles_join_cuts_across_holds_and_split_holds_at_any_move() -> None:
    # given a cut, a hold, a cut, a hike, a hike, a hold, a hold, and a cut
    kinds = [CUT, HOLD, CUT, HIKE, HIKE, HOLD, HOLD, CUT]

    # when the cycles are read
    cycles = study.fed_cycles(kinds)

    # then both first cuts are one cycle, both hikes one, each run of holds its own, and the last
    # cut, after a hike, a new cycle
    assert cycles == [0, 1, 0, 2, 2, 3, 3, 4]


def _rising_after(keys: list[int], c: int) -> list[DailyClosingPrice]:
    # closes alternating 1% either way, rising 3% more over the c closes from each key
    steps = _alternating(keys[-1] + c + 200)
    for i in keys:
        for k in range(i, i + c):
            steps[k] += 0.03 / c
    return _closes(steps)


def test_an_answer_from_too_few_cycles_does_not_stand() -> None:
    # given 12 cuts whose quarter rises, from three cycles of four
    keys = list(range(200, 200 + 12 * 400, 400))
    closes = _rising_after(keys, 63)
    decisions = [(closes[i].day, CUT) for i in keys]
    cycles = [i // 4 for i in range(12)]

    # when the quarter is followed with the cycles
    follow = study.follow_market(decisions, closes, "pct", 63, cycles=cycles)[CUT]

    # then the cell answers up, but counting each cycle once there are three: too few cycles
    assert follow.answer == UP
    assert follow.by_cycle == (3, study.TOO_FEW_CYCLES)


def test_an_answer_every_cycle_repeats_stands() -> None:
    # given 12 cuts whose quarter rises, each its own cycle
    keys = list(range(200, 200 + 12 * 400, 400))
    closes = _rising_after(keys, 63)
    decisions = [(closes[i].day, CUT) for i in keys]

    # when the quarter is followed with the cycles, and without
    with_cycles = study.follow_market(decisions, closes, "pct", 63, cycles=list(range(12)))[CUT]
    without = study.follow_market(decisions, closes, "pct", 63)[CUT]

    # then counting each cycle once gives the same answer, and nothing else changes
    assert with_cycles.by_cycle == (12, UP)
    assert without.by_cycle is None
    assert without == study.Follow(**{**with_cycles.__dict__, "by_cycle": None})


def test_a_held_cell_whose_cycles_do_not_repeat_it_does_not_hold() -> None:
    # given a cell that holds walk-forward, and its answer counting each cycle once
    held = study.Follow(
        {UP: 40, SAME: 0, DOWN: 0}, 0, 0, None, UP, 0.0, False, 30, 30, 0.0, study.HOLDS
    )
    base = study.base_of([0.01, -0.01, 0.0] * 10)
    assert base is not None
    flat = [study.Span(START, START, -0.01)] * 12

    # when its cycles answer down
    follow = study._by_cycle(study.replace(held, base=base), flat)

    # then the answer is one cycle's, and the cell does not hold
    assert follow.by_cycle == (12, study.ONE_CYCLE)
    assert follow.verdict == study.DOESNT_HOLD


def test_follows_long_is_the_fed_s_alone(tmp_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # given nothing stored

    # when the quarter and the year are asked for the jobs report
    code = main(["follows", "--long", "--event", "nfp"])

    # then it refuses
    assert code == 1
    assert "measured on the Fed's decisions only" in capsys.readouterr().err


def test_follows_long_prints_the_quarter_and_the_year_with_the_cycles(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given one Fed cut, one market's closes, and FRED's target rate patched
    db.init_db()
    flows.store_fomc_decisions([sources.FomcDecision(date(2001, 3, 20), True)])
    closes = _closes(_alternating(600))
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    rates = {date(2001, 3, 19): 5.5, date(2001, 3, 23): 5.0}
    monkeypatch.setattr(flows, "target_rates", lambda api_key: list(rates.items()))
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))

    # when the quarter and the year are followed
    code = main(["follows", "--long"])

    # then a row per kind and span, each with its cycle column
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert "cycles" in out[1]
    assert [line.split()[1] for line in out[2:-1]] == ["quarter", "year"] * 3
    assert out[2].startswith("cut   quarter  SPY / ES       1")
    assert "1: too few cycles" in out[2]


def test_a_base_keeps_how_many_moves_it_rests_on() -> None:
    # given nine moves
    moves = [0.01, -0.02, 0.0, 0.03, -0.01, 0.002, -0.004, 0.02, -0.03]

    # when their base is taken
    base = study.base_of(moves)

    # then it rests on nine
    assert base is not None
    assert base.n == 9


FOLLOWS_LINE = re.compile(
    r"^(?P<kind>above|as expected|below)\s+(?P<span>day|week|month)\s+(?P<market>.+?)\s+"
    r"(?P<n>\d+)\s+(?P<up>\d+)\s+(?P<same>\d+)\s+(?P<down>\d+)\s+\d+/\d+\s+"
    r"(?P<base>[\d.]+/[\d.]+/[\d.]+|—)\s+(?P<answer>up|down|about the same|can't say|too few)\s+"
    r"\S+\s+\S+\s+(?P<graded>\d+): (?P<right>\d+) right, (?P<verdict>.+)$"
)


def test_the_page_s_cells_are_the_lines_follows_prints(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given two markets' closes and 45 jobs reports, the surprises' signs alternating and the
    # markets rising on the day after a report above the consensus
    two = {k: study.MVP_PRICE_SERIES[k] for k in ("SPY / ES", "DXY")}
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", two)
    rng = random.Random(3)
    keys = list(range(30, 1380, 30))
    steps = [rng.gauss(0, 0.005) for _ in range(1400)]
    for j, k in enumerate(keys):
        steps[k] = 0.01 if j % 3 == 0 else rng.gauss(0, 0.005)
    closes = _closes(steps)
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in two for c in closes],
    )
    signs = (60.0, 0.0, -60.0)
    _store_reports([(closes[k].day, "nasdaq_consensus", signs[j % 3]) for j, k in enumerate(keys)])

    # when follows prints the jobs reports' table and the page's data is built
    assert main(["follows", "--event", "nfp"]) == 0
    printed = [FOLLOWS_LINE.match(line) for line in capsys.readouterr().out.splitlines()[2:-1]]
    ask = cli.ask_data(db.get_connection())

    # then every line has one cell on the page, equal field by field
    (nfp,) = [entry for entry in ask["ask"] if entry["name"] == "nfp"]
    cells = {(c["kind"], c["span"], c["market"]): c for c in nfp["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 3 * 3 * 2
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"], line["market"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        shares = [cell["base_up"], cell["base_same"], cell["base_down"]]
        assert "/".join(f"{s:.2f}" for s in shares) == line["base"]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert (cell["graded"], cell["right"]) == (int(line["graded"]), int(line["right"]))
        assert "%" not in str(cell["say"])
    assert [k["events"] for k in nfp["kinds"]] == [15, 15, 15]  # type: ignore[index]


def test_the_page_names_a_flow_it_cannot_compute_and_shows_the_others(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a Fed decision and three jobs reports with their surprises, and no FRED key
    monkeypatch.setattr(settings, "fred_api_key", None)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    _store_reports(
        [(day, "nasdaq_consensus", s) for day, s in zip(days, (60.0, 0.0, -60.0), strict=True)]
    )
    flows.store_fomc_decisions([sources.FomcDecision(closes[140].day, True)])
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )

    # when the page's data is built
    ask = cli.ask_data(db.get_connection())

    # then the Fed is left out with the reason, and the jobs reports are there
    left = {entry["name"]: entry["reason"] for entry in ask["ask_left_out"]}
    assert left["fomc"] == "FT_FRED_API_KEY is not set (see docs/accounts.md)"
    assert (
        left["retail"] == "no retail sales releases stored; run `fortuneteller load-releases` first"
    )
    assert [entry["name"] for entry in ask["ask"]] == ["nfp"]


def test_a_cell_s_sentence_gives_its_events_its_base_and_its_replay_apart() -> None:
    # given step 17's cell for the 10-year yield on the day after a jobs report above the consensus
    f = study.Follow(
        counts={UP: 47, SAME: 8, DOWN: 13},
        overlapped=0,
        holes=0,
        base=study.Base(0.01, {UP: 0.45, SAME: 0.33, DOWN: 0.22}, 9000),
        answer=UP,
        chance=0.00001,
        period=False,
        graded=57,
        right=38,
        walk_chance=0.001,
        verdict=study.HOLDS,
    )

    # when it is put in words
    say = cli.ask_say("nfp", ABOVE, "day", "UST10Y / ZN", f)

    # then the event counts, the base's counts and the replay are each named, with no percentage
    assert say == (
        "After a jobs report above the consensus, UST10Y / ZN on the day: up 47, about the same 8, "
        "down 13, of 68. On every day of its history: up 4050, about the same 2970, down 1980, of "
        "9000. Answer: up. Replayed, it held: right 38 of 57."
    )


def test_each_replay_verdict_and_too_few_events_have_words() -> None:
    # given a cell with five events, and the replay's three other states
    def cell(graded: int, right: int, verdict: str) -> study.Follow:
        return study.Follow(
            {UP: 3, SAME: 1, DOWN: 1},
            0,
            0,
            None,
            TOO_FEW,
            math.nan,
            False,
            graded,
            right,
            1.0,
            verdict,
        )

    # when each is put in words
    words = [
        cli.ask_say("fomc", CUT, "week", "DXY", cell(*args))
        for args in ((0, 0, TOO_FEW), (34, 17, study.DOESNT_HOLD), (6, 4, TOO_FEW))
    ]

    # then each says it plainly
    assert words[0] == (
        "After a Fed rate cut, DXY over the next week: up 3, about the same 1, down 1, of 5. "
        "Too few events to answer: 5, against the 10 it needs. Not replayed."
    )
    assert words[1].endswith("Replayed, it did not hold: right 17 of 34.")
    assert words[2].endswith("Too few replayed to judge: right 4 of 6.")


def _opec(day: date, kind: str) -> flows.EventInstance:
    # an OPEC announcement at 08:00 New York on ``day``, its kind in its detail as the seed has it
    at = datetime.combine(day, time(8, 0), tzinfo=sources.NEW_YORK)
    return flows.OPEC_FLOW.event_instance(at, kind)


def test_follows_for_opec_judges_the_spans_after_brent_s_close_and_prints_the_rest_unjudged(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given three OPEC announcements, two oil up and one oil down, and Brent and the S&P 500
    # falling 3% on each oil up day and rising on the oil down one, against the kind
    markets = ("SPY / ES", study.KIND_MARKET)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in markets})
    steps = _alternating(300)
    keys = {40: study.OIL_UP, 80: study.OIL_DOWN, 120: study.OIL_UP}
    for i, kind in keys.items():
        steps[i] = -0.03 if kind == study.OIL_UP else 0.03
    closes = _closes(steps)
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in markets for c in closes],
    )
    db.insert_models("event_instances", [_opec(closes[i].day, k) for i, k in keys.items()])
    first, last = closes[40].day, closes[120].day

    # when run, and from the reaction close
    day_code = main(["follows", "--event", "opec"])
    day_out = capsys.readouterr().out.splitlines()
    after_code = main(["follows", "--event", "opec", "--after-the-day"])
    after_out = capsys.readouterr().out.splitlines()

    # then the kinds are the seed's; the judged run is the same both ways and marks nothing; the
    # run from the close before follows it, every row marked, with no chance line
    assert day_code == after_code == 0
    assert day_out[0] == f"follows: 3 OPEC announcements {first} … {last}: 2 oil up, 1 oil down"
    gap = day_out.index("")
    judged = [line for line in day_out[:gap] if line.startswith("oil")]
    unjudged = [line for line in day_out[gap:] if line.startswith("oil")]
    assert judged == [line for line in after_out if line.startswith("oil")]
    assert not any(line.endswith("(not judged)") for line in judged)
    assert len(unjudged) == len(judged) and all(line.endswith("(not judged)") for line in unjudged)
    assert day_out[gap + 1] == "from the close before:"
    assert day_out[-1].startswith("not judged: ")


@pytest.mark.parametrize(
    ("market", "starts"),
    [
        (study.KIND_MARKET, 0),
        ("SPY / ES", 0),
        ("DAX", 1),
        ("GC / XAU", 1),
    ],
)
def test_an_opec_span_starts_at_the_first_close_at_or_after_brent_s_reaction_close(
    market: str, starts: int
) -> None:
    # given an announcement at 08:00 New York on a Wednesday, read by Brent's close at 14:30
    event = _opec(date(2026, 11, 18), study.OIL_UP)

    # when each market's start is found
    start = study.opec_start(event, study.MVP_PRICE_SERIES[market])

    # then Brent and the S&P 500 start that day, Europe's indices and gold the next
    assert start == date(2026, 11, 18) + timedelta(days=starts)


def test_a_market_closing_with_brent_starts_at_that_close() -> None:
    # given a market that closes at Brent's minute
    same = study.PriceSeries("X", "pct", study.KIND_SERIES.close, study.KIND_SERIES.zone)

    # when an announcement's start is found
    start = study.opec_start(_opec(date(2026, 11, 18), study.OIL_UP), same)

    # then it is that day's close
    assert start == date(2026, 11, 18)


def test_a_run_not_judged_has_no_chance_line() -> None:
    # given an answered cell
    answered = study.Follow(
        {UP: 40, SAME: 0, DOWN: 0}, 0, 0, None, UP, 0.0, False, 0, 0, 0.0, study.TOO_FEW
    )
    events = [_opec(date(2020, 4, 13), study.OIL_UP)]
    kinds = study.detail_kinds(events)
    cells = [(study.OIL_UP, "day", "SPY / ES", answered)]

    # when the table is described judged, and not
    judged = describe_follows(events, kinds, cells, study.OPEC_KINDS, "OPEC announcements")
    not_judged = describe_follows(
        events, kinds, cells, study.OPEC_KINDS, "OPEC announcements", judged=False
    )

    # then only the judged one counts it against chance
    assert judged[-1].startswith(f"by chance: about {3 * study.FOLLOW_P_BAR:.1f} answers")
    assert not_judged[-2].endswith("(not judged)")
    assert not_judged[-1].startswith("not judged: ")


def _boe(day: date, at: time = time(12, 0)) -> flows.EventInstance:
    # a BoE decision at ``at`` London on ``day``
    return flows.decision_instance(
        flows.BOE_FLOW, datetime.combine(day, at, tzinfo=sources.LONDON).astimezone(UTC)
    )


def test_a_boe_decision_s_kind_is_the_bank_s_change_and_2020_03_26_a_hold() -> None:
    # given the Bank's changes from the seed, and decisions on the days checked by hand
    days = [
        date(2008, 1, 10),
        date(2009, 3, 5),
        date(2016, 8, 4),
        date(2020, 3, 11),
        date(2020, 3, 19),
        date(2020, 3, 26),
        date(2022, 12, 15),
        date(2025, 12, 18),
    ]
    rates = {d: r for d, (_, r) in flows.boe_changes(settings.seed_dir).items()}

    # when their kinds are read
    kinds = study.boe_kinds([_boe(d) for d in reversed(days)], rates)

    # then the first has none, and each other is the Bank's: 2020-03-26 a hold
    assert [kinds.get(_boe(d).event_id) for d in days] == [
        None,
        CUT,
        CUT,
        CUT,
        CUT,
        HOLD,
        HIKE,
        CUT,
    ]


def test_the_first_bank_rate_change_is_against_the_rate_before_2008() -> None:
    # given the decision before it, and the cut of 2008-02-07 to 5.25% from 5.5%
    events = [_boe(date(2008, 1, 10)), _boe(date(2008, 2, 7))]

    # when their kinds are read
    kinds = study.boe_kinds(events, {date(2008, 2, 7): 5.25})

    # then it is a cut
    assert kinds == {events[1].event_id: CUT}


def test_follows_for_the_boe_prints_its_table(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given three BoE decisions, one market's closes, and the Bank's changes patched
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    db.insert_models("event_instances", [_boe(d) for d in days])
    monkeypatch.setattr(flows, "boe_changes", lambda _seed_dir: {days[1]: (time(12, 0), 6.0)})

    # when run
    code = main(["follows", "--event", "boe"])

    # then it prints the BoE decisions' table, the first decision having no kind
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (f"follows: 2 BoE decisions {days[1]} … {days[2]}: 0 cuts, 1 holds, 1 hikes")


def _boj(day: date) -> flows.EventInstance:
    # a BoJ decision at 12:00 Tokyo on ``day``
    return flows.decision_instance(
        flows.BOJ_FLOW, datetime.combine(day, time(12, 0), tzinfo=sources.TOKYO).astimezone(UTC)
    )


def test_follows_for_the_boj_reads_its_kinds_from_the_calendar_s_rates(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given three BoJ decisions, one market's closes, and the calendar's rates patched: a hold of
    # the yield-curve policy's start and the end of negative rates
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    db.insert_models("event_instances", [_boj(d) for d in days])
    rates = {
        datetime.combine(d, time(3, 0), tzinfo=UTC): r
        for d, r in zip(days, (-0.1, -0.1, 0.1), strict=True)
    }
    monkeypatch.setattr(flows, "load_boj_rates", lambda _cache_dir: rates)

    # when run
    code = main(["follows", "--event", "boj"])

    # then it prints the BoJ decisions' table, the first decision having no kind
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0] == (f"follows: 2 BoJ decisions {days[1]} … {days[2]}: 0 cuts, 1 holds, 1 hikes")


def test_a_violent_act_reacts_by_its_utc_day_on_each_market() -> None:
    # given the seed's act of 1990-08-02, a Thursday
    batch = flows.WAR_FLOW.load(settings.seed_dir / "war.csv", datetime(2026, 11, 18, tzinfo=UTC))
    event = next(e for e in batch.events if flows.release_date(e) == date(1990, 8, 2))

    # when its first reaction day is found on Tokyo's, New York's and the euro's close
    days = [
        study.first_reaction_day(event, study.MVP_PRICE_SERIES[m])
        for m in ("NKY", "SPY / ES", "EURUSD")
    ]

    # then it is at 04:00 UTC, on Tokyo's and New York's close that day and the euro's the next
    assert event.event_ts == datetime(1990, 8, 2, 4, 0)
    assert days == [date(1990, 8, 2), date(1990, 8, 2), date(1990, 8, 3)]


def test_a_landfall_reacts_by_its_utc_minute_on_each_market() -> None:
    # given the seed's landfall of Michael, Wednesday 2018-10-10 17:30 UTC
    batch = flows.WEATHER_FLOW.load(
        settings.seed_dir / "hurricanes.csv", datetime(2026, 11, 18, tzinfo=UTC)
    )
    michael = next(e for e in batch.events if flows.release_date(e) == date(2018, 10, 10))

    # when its first reaction day is found on New York's and Tokyo's close
    days = [
        study.first_reaction_day(michael, study.MVP_PRICE_SERIES[m]) for m in ("SPY / ES", "NKY")
    ]

    # then at 13:30 New York it reacts that day in New York and the next in Tokyo; read in New
    # York's time it would react a day late in New York
    assert michael.event_ts == datetime(2018, 10, 10, 17, 30)
    assert days == [date(2018, 10, 10), date(2018, 10, 11)]


OPEC_LINE = re.compile(
    r"^(?P<kind>oil up|oil down)\s+(?P<span>day|week|month)\s+(?P<market>.+?)\s+"
    r"(?P<n>\d+)\s+(?P<up>\d+)\s+(?P<same>\d+)\s+(?P<down>\d+)\s+\d+/\d+\s+"
    r"(?P<base>[\d.]+/[\d.]+/[\d.]+|—)\s+(?P<answer>up|down|about the same|can't say|too few)\s+"
    r"\S+\s+\S+\s+(?P<graded>\d+): (?P<right>\d+) right, (?P<verdict>.+?)(?:\s+\(the kind\))?$"
)


def test_the_page_s_opec_cells_are_follows_lines_with_their_own_kind_s_words(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given 44 OPEC announcements, the kinds alternating, Brent and the S&P 500 moving with them
    markets = ("SPY / ES", study.KIND_MARKET)
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in markets})
    rng = random.Random(5)
    keys = list(range(30, 1350, 30))
    steps = [rng.gauss(0, 0.005) for _ in range(1400)]
    kinds = {k: (study.OIL_UP if j % 2 == 0 else study.OIL_DOWN) for j, k in enumerate(keys)}
    for k, kind in kinds.items():
        steps[k] = 0.02 if kind == study.OIL_UP else -0.02
    closes = _closes(steps)
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in markets for c in closes],
    )
    db.insert_models("event_instances", [_opec(closes[k].day, kind) for k, kind in kinds.items()])

    # when follows prints OPEC's table and the page's data is built
    assert main(["follows", "--event", "opec"]) == 0
    out = capsys.readouterr().out.splitlines()
    lines = out[2 : out.index("") - 1]
    printed = [OPEC_LINE.match(line) for line in lines]
    ask = cli.ask_data(db.get_connection())

    # then every line is one cell, equal field by field, its sentence opening with its own kind's
    # words and saying its spans start when oil's price closed
    (opec,) = [entry for entry in ask["ask"] if entry["name"] == "opec"]
    cells = {(c["kind"], c["span"], c["market"]): c for c in opec["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 2 * 3 * 2
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"], line["market"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        shares = [cell["base_up"], cell["base_same"], cell["base_down"]]
        assert "/".join(f"{s:.2f}" for s in shares) == line["base"]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert (cell["graded"], cell["right"]) == (int(line["graded"]), int(line["right"]))
        assert str(cell["say"]).startswith(f"After {cli.ASK_DECISIONS['opec'][line['kind']]},")
        assert "%" not in str(cell["say"])
    assert all("counted from when oil's price closed" in str(c["say"]) for c in cells.values())
    assert [k["events"] for k in opec["kinds"]] == [22, 22]  # type: ignore[index]
    page = (Path(cli.__file__).parent / "scoreboard.html").read_text()
    assert "!c.period && c.answer" in page
    assert "c.verdict === 'holds' && !c.period" in page


def test_the_page_names_the_boj_when_its_rates_cannot_be_read_and_shows_the_boe(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given BoE and BoJ decisions with one market's closes, and TradingView failing for the BoJ
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    closes = _closes(_alternating(300))
    days = [closes[i].day for i in (20, 60, 100)]
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES ('SPY / ES', ?, ?, 'test')",
        [[c.day, c.price] for c in closes],
    )
    db.insert_models("event_instances", [_boe(d) for d in days] + [_boj(d) for d in days])
    monkeypatch.setattr(flows, "boe_changes", lambda _seed_dir: {days[1]: (time(12, 0), 6.0)})

    def failing(_cache_dir: Path) -> dict[datetime, float]:
        raise sources.CalendarError("TradingView answered 'error'")

    monkeypatch.setattr(flows, "load_boj_rates", failing)

    # when the page's data is built
    ask = cli.ask_data(db.get_connection())

    # then the BoJ is left out with the error, and the BoE is there
    left = {entry["name"]: entry["reason"] for entry in ask["ask_left_out"]}
    assert left["boj"] == (
        "the BoJ's rates could not be read from TradingView: TradingView answered 'error'"
    )
    assert "boe" in [entry["name"] for entry in ask["ask"]]


def test_a_flood_reacts_at_04_00_utc_of_its_begin_day() -> None:
    # given the seed's floods: the Upper Midwest's on Sunday 2024-06-16 and the Northeast's on
    # Tuesday 2023-07-11 is not one; a flood placed on that Tuesday
    batch = flows.FLOOD_FLOW.load(
        settings.seed_dir / "floods.csv", datetime(2026, 11, 19, tzinfo=UTC)
    )
    midwest = next(e for e in batch.events if flows.release_date(e) == date(2024, 6, 16))
    tuesday = flows.FLOOD_FLOW.event_instance(
        datetime(2023, 7, 11, 4, 0, tzinfo=UTC), "a flood on a Tuesday"
    )

    # when their first reaction days are found
    sunday = study.first_reaction_day(midwest, study.MVP_PRICE_SERIES["SPY / ES"])
    days = [
        study.first_reaction_day(tuesday, study.MVP_PRICE_SERIES[m])
        for m in ("SPY / ES", "NKY", "EURUSD")
    ]

    # then the Sunday flood reacts on Monday, and the Tuesday one that day in New York and Tokyo
    # and the next day on the euro, whose close is 00:00 London
    closes = [
        DailyClosingPrice(d, p) for d, p in ((date(2024, 6, 14), 100.0), (date(2024, 6, 17), 101.0))
    ]
    assert midwest.event_ts == datetime(2024, 6, 16, 4, 0)
    assert study.reaction_days(closes, [sunday]) == {date(2024, 6, 17)}
    assert days == [date(2023, 7, 11), date(2023, 7, 11), date(2023, 7, 12)]


def test_follows_for_floods_prints_one_kind() -> None:
    # given the flood flow
    flow = flows.flow_named("flood")

    # when its kind is read
    kinds = study.one_kind(
        flow, [flows.FLOOD_FLOW.event_instance(datetime(2024, 6, 16, 4, 0, tzinfo=UTC), "x")]
    )

    # then every flood is a flood, and the page leaves the floods out
    assert set(kinds.values()) == {study.FLOOD}
    assert cli.FOLLOWS_NOUNS["flood"] == "floods"


def test_an_earnings_report_reacts_by_its_8_k_s_minute_summer_and_winter() -> None:
    # given four reports at 8-K minutes either side of 16:00 New York, in summer and in winter
    stamps = [
        datetime(2026, 10, 28, 19, 55, tzinfo=UTC),
        datetime(2026, 10, 28, 20, 4, tzinfo=UTC),
        datetime(2025, 1, 29, 20, 55, tzinfo=UTC),
        datetime(2025, 1, 29, 21, 5, tzinfo=UTC),
    ]
    reports = [flows.EARNINGS_FLOW.event_instance(at, "MSFT above") for at in stamps]

    # when their first reaction days on a company's 16:00 New York close are found
    days = [study.first_reaction_day(e, study.STOCK) for e in reports]

    # then 15:55 New York reacts that day and 16:04 or 16:05 the next
    assert days == [date(2026, 10, 28), date(2026, 10, 29), date(2025, 1, 29), date(2025, 1, 30)]


def test_two_reports_on_one_day_are_two_events_in_the_order_of_their_minutes(
    tmp_db: Path, tmp_path: Path
) -> None:
    # given two members reporting on one day, the later ticker first in the morning
    seed = tmp_path / "earnings.csv"
    seed.write_text(
        "day,time,ticker,eps,forecast,surprise,kind\n"
        "2026-10-28,20:04,MSFT,4.89,4.71,3.82,above\n"
        "2026-10-28,11:00,V,3.10,3.11,-0.32,as expected\n"
    )

    # when they are loaded, stored and read back
    batch = flows.EARNINGS_FLOW.load(seed, datetime(2026, 11, 19, tzinfo=UTC))
    db.init_db()
    flows.store_events(batch.events)
    stored = flows.stored_events(flows.EARNINGS_FLOW)

    # then each is its own event, each giving its day back, read by minute, with its kind
    assert len({e.event_id for e in stored}) == 2
    assert {flows.event_date(e.event_id) for e in stored} == {date(2026, 10, 28)}
    assert [e.detail for e in stored] == ["V as expected", "MSFT above"]
    assert study.earnings_kinds(stored) == {
        stored[0].event_id: "as expected",
        stored[1].event_id: "above",
    }
    assert batch.report == ["loaded 2 earnings reports, 2026-10-28 … 2026-10-28"]


def test_a_base_grown_one_move_at_a_time_is_base_of_its_moves() -> None:
    # given moves with ties, zeros and both signs
    rng = random.Random(7)
    moves = [round(rng.gauss(0, 1), 1) for _ in range(400)] + [0.0] * 5

    # when the base is grown one move at a time
    so_far = study.BaseSoFar()
    grown = []
    for i, move in enumerate(moves):
        so_far.add(move)
        grown.append((so_far.base(), study.base_of(moves[: i + 1])))

    # then each base is base_of's, cut and shares exactly
    assert all(a == b for a, b in grown)
    assert grown[0] == (None, None)


def _boc(day: date, at: time = time(10, 0)) -> flows.EventInstance:
    # a Bank of Canada decision at ``at`` Toronto on ``day``
    return flows.decision_instance(
        flows.BOC_FLOW, datetime.combine(day, at, tzinfo=flows.TORONTO).astimezone(UTC)
    )


def test_a_boc_decision_s_kind_is_the_bank_s_change_2020_03_13_a_cut_and_2012_01_17_a_hold() -> (
    None
):
    # given the Bank's changes from the seed, and decisions on the days checked by hand
    days = [
        date(2008, 1, 22),
        date(2008, 10, 8),
        date(2012, 1, 17),
        date(2013, 12, 4),
        date(2020, 3, 13),
        date(2020, 3, 27),
        date(2022, 3, 2),
        date(2026, 10, 28),
    ]
    rates = {d: r for d, (_, r) in flows.boc_changes(settings.seed_dir).items()}

    # when their kinds are read
    kinds = study.boe_kinds([_boc(d) for d in reversed(days)], rates, study.BOC_RATE_BEFORE)

    # then the first has none, and each other is the Bank's: the emergency cuts of 2020 cuts and
    # the days the calendar gives no rate holds
    assert [kinds.get(_boc(d).event_id) for d in days] == [
        None,
        CUT,
        HOLD,
        HOLD,
        CUT,
        CUT,
        HIKE,
        HIKE,
    ]


def test_the_first_boc_change_is_against_the_rate_before_2008() -> None:
    # given the decision of 2007-12-04 and the cut of 2008-01-22 to 4% from 4.25%
    events = [_boc(date(2007, 12, 4)), _boc(date(2008, 1, 22))]

    # when their kinds are read against the target before 2008
    kinds = study.boe_kinds(events, {date(2008, 1, 22): 4.0}, study.BOC_RATE_BEFORE)

    # then it is a cut
    assert kinds == {events[1].event_id: CUT}


def _snb(day: date, at: time = time(9, 30)) -> flows.EventInstance:
    # an SNB decision at ``at`` Zurich on ``day``
    return flows.decision_instance(
        flows.SNB_FLOW, datetime.combine(day, at, tzinfo=sources.ZURICH).astimezone(UTC)
    )


def test_an_snb_decision_s_kind_is_the_bank_s_change_2015_01_15_a_cut_and_2015_03_19_a_hold() -> (
    None
):
    # given the Bank's changes from the seed, and decisions on the days checked by hand: the first
    # on the calendar, an unscheduled cut, the end of the minimum exchange rate, the hold the
    # calendar reads as a cut, the switch to the policy rate, the first hike and the last cut
    days = [
        date(2008, 3, 13),
        date(2011, 8, 3),
        date(2015, 1, 15),
        date(2015, 3, 19),
        date(2019, 6, 13),
        date(2022, 6, 16),
        date(2025, 6, 19),
    ]
    rates = {d: r for d, (_, r) in flows.snb_changes(settings.seed_dir).items()}

    # when their kinds are read
    kinds = study.boe_kinds([_snb(d) for d in reversed(days)], rates, study.SNB_RATE_BEFORE)

    # then the first has none, and each other is the Bank's
    assert [kinds.get(_snb(d).event_id) for d in days] == [None, CUT, CUT, HOLD, HOLD, HIKE, CUT]


BOC_LINE = re.compile(
    r"^(?P<kind>cut|hold|hike)\s+(?P<span>day|week|month)\s+(?P<market>.+?)\s+"
    r"(?P<n>\d+)\s+(?P<up>\d+)\s+(?P<same>\d+)\s+(?P<down>\d+)\s+\d+/\d+\s+"
    r"(?P<base>[\d.]+/[\d.]+/[\d.]+|—)\s+(?P<answer>up|down|about the same|can't say|too few)\s+"
    r"\S+\s+\S+\s+(?P<graded>\d+): (?P<right>\d+) right, (?P<verdict>.+)$"
)


@pytest.mark.parametrize(
    ("name", "label", "decision", "changes_of", "currency"),
    [
        ("boc", "BoC", _boc, "boc_changes", "USDCAD"),
        ("snb", "SNB", _snb, "snb_changes", "USDCHF"),
    ],
)
def test_follows_for_a_bank_prints_its_table_and_the_page_s_cells_are_its_lines(
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    label: str,
    decision: Callable[[date], flows.EventInstance],
    changes_of: str,
    currency: str,
) -> None:
    # given 44 decisions of the Bank of Canada or the SNB, the Bank's changes patched to make every
    # third a cut and every third a hike, and two markets' closes
    two = {k: study.MVP_PRICE_SERIES[k] for k in ("SPY / ES", currency)}
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", two)
    rng = random.Random(7)
    closes = _closes([rng.gauss(0, 0.005) for _ in range(1400)])
    keys = list(range(30, 1350, 30))
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in two for c in closes],
    )
    db.insert_models("event_instances", [decision(closes[k].day) for k in keys])
    changes, rate = {}, 4.0
    for j, k in enumerate(keys[1:]):
        if j % 3 != 1:
            rate += 0.25 if j % 3 == 0 else -0.25
            changes[closes[k].day] = (time(10, 0), rate)
    monkeypatch.setattr(flows, changes_of, lambda _seed_dir: changes)
    cuts = sum(1 for j in range(len(keys) - 1) if j % 3 == 2)
    holds = sum(1 for j in range(len(keys) - 1) if j % 3 == 1)
    hikes = len(keys) - 1 - cuts - holds

    # when follows prints the Bank's table and the page's data is built
    assert main(["follows", "--event", name]) == 0
    out = capsys.readouterr().out.splitlines()
    printed = [BOC_LINE.match(line) for line in out[2:-1]]
    ask = cli.ask_data(db.get_connection())

    # then the header counts the Bank's kinds after the first decision, and every line has one cell
    # on the page, equal field by field, its sentence opening with the Bank's own words
    first, last = closes[keys[1]].day, closes[keys[-1]].day
    assert out[0] == (
        f"follows: {len(keys) - 1} {label} decisions {first} … {last}: "
        f"{cuts} cuts, {holds} holds, {hikes} hikes"
    )
    (boc,) = [entry for entry in ask["ask"] if entry["name"] == name]
    cells = {(c["kind"], c["span"], c["market"]): c for c in boc["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 3 * 3 * 2
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"], line["market"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        shares = [cell["base_up"], cell["base_same"], cell["base_down"]]
        assert "/".join(f"{s:.2f}" for s in shares) == line["base"]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert (cell["graded"], cell["right"]) == (int(line["graded"]), int(line["right"]))
        assert str(cell["say"]).startswith(f"After {cli.ASK_DECISIONS[name][line['kind']]},")
        assert "%" not in str(cell["say"])
    assert [k["events"] for k in boc["kinds"]] == [cuts, holds, hikes]  # type: ignore[index]


CACPI = flows.CA_CPI_FLOW


def _store_cacpi(
    prints: Mapping[date, tuple[float, float]], flow: flows.TradingViewFlow = CACPI
) -> list[flows.EventInstance]:
    # a Canadian (or Swiss) CPI release at 08:30 Toronto (Zurich) on each day, with its actual and
    # TradingView's forecast, and its surprise row as `load-surprises` stores it
    db.init_db()
    events = [
        flow.event_instance(datetime.combine(day, time(8, 30), tzinfo=flow.zone), day)
        for day in prints
    ]
    db.insert_models("event_instances", events)
    db.insert_models(
        "surprises",
        [
            Surprise(
                event_id=e.event_id,
                measure=flow.measures[0],
                baseline="tradingview_forecast",
                actual_mom=actual,
                expected_mom=forecast,
                surprise=actual - forecast,
            )
            for e, (actual, forecast) in zip(events, prints.values(), strict=True)
        ],
    )
    return events


def test_a_canadian_cpi_release_on_a_us_release_s_close_is_left_out_of_its_kinds(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given three Canadian CPI releases, above, as expected and below, a US CPI release at the same
    # 08:30 New York as the first, and the S&P 500's and the Canadian dollar's closes
    markets = ("SPY / ES", "USDCAD")
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in markets})
    days = [date(2024, 1, 16), date(2024, 2, 20), date(2024, 3, 19)]
    events = _store_cacpi(dict(zip(days, [(3.4, 3.3), (2.9, 2.9), (2.8, 2.9)], strict=True)))
    db.insert_models("event_instances", [_report(days[0], CPI)])
    weekday_closes(markets, date(2024, 1, 1), date(2024, 4, 30))

    # when the kinds are read, all of them and the ones alone in some market
    every = study.release_kinds(CACPI)
    alone = study.lone_release_kinds(CACPI)

    # then the release sharing every market's close has its kind but is left out of the lone ones
    assert [every.get(e.event_id) for e in events] == [ABOVE, AS_EXPECTED, BELOW]
    assert [alone.get(e.event_id) for e in events] == [None, AS_EXPECTED, BELOW]


def test_a_swiss_cpi_release_on_a_us_jobs_report_s_close_is_left_out_of_its_kinds(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given three Swiss CPI releases, above, as expected and below, a US jobs report the day of the
    # first, which reaches the S&P 500 and the SMI at that day's close, and their closes
    markets = ("SPY / ES", "SMI")
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in markets})
    days = [date(2024, 3, 8), date(2024, 4, 4), date(2024, 5, 2)]
    prints = [(1.3, 1.2), (1.0, 1.0), (1.3, 1.4)]
    events = _store_cacpi(dict(zip(days, prints, strict=True)), flows.CH_CPI_FLOW)
    db.insert_models("event_instances", [_report(days[0], NFP)])
    weekday_closes(markets, date(2024, 3, 1), date(2024, 5, 31))

    # when the kinds are read, all of them and the ones alone in some market
    every = study.release_kinds(flows.CH_CPI_FLOW)
    alone = study.lone_release_kinds(flows.CH_CPI_FLOW)

    # then the shared day has its kind but is left out of the lone ones
    assert [every.get(e.event_id) for e in events] == [ABOVE, AS_EXPECTED, BELOW]
    assert [alone.get(e.event_id) for e in events] == [None, AS_EXPECTED, BELOW]


@pytest.mark.parametrize(
    ("flow", "currency", "noun"),
    [(CACPI, "USDCAD", "Canadian"), (flows.CH_CPI_FLOW, "USDCHF", "Swiss")],
    ids=["cacpi", "chcpi"],
)
def test_follows_for_a_lesser_cpi_leaves_out_a_shared_day_and_the_page_s_cells_are_its_lines(
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    flow: flows.TradingViewFlow,
    currency: str,
    noun: str,
) -> None:
    # given two markets' closes and 45 Canadian or Swiss CPI releases, above, as expected and
    # below in turn, the first sharing its day with a US retail sales release
    two = {k: study.MVP_PRICE_SERIES[k] for k in ("SPY / ES", currency)}
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", two)
    rng = random.Random(5)
    closes = _closes([rng.gauss(0, 0.005) for _ in range(1400)])
    keys = list(range(30, 1380, 30))
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in two for c in closes],
    )
    prints = ((2.3, 2.2), (2.2, 2.2), (2.2, 2.3))
    _store_cacpi({closes[k].day: prints[j % 3] for j, k in enumerate(keys)}, flow)
    db.insert_models("event_instances", [_report(closes[keys[0]].day, RETAIL)])

    # when follows prints the table and the page's data is built
    name = flow.cli_name
    assert main(["follows", "--event", name]) == 0
    out = capsys.readouterr().out.splitlines()
    printed = [FOLLOWS_LINE.match(line) for line in out[2:-1]]
    ask = cli.ask_data(db.get_connection())

    # then the header counts the 44 releases alone, the shared one an above left out, and every
    # line has one cell on the page, equal field by field
    first, last = closes[keys[1]].day, closes[keys[-1]].day
    assert out[0] == (
        f"follows: 44 {noun} CPI releases {first} … {last}: 14 above, 15 as expected, 15 below"
    )
    (cacpi,) = [entry for entry in ask["ask"] if entry["name"] == name]
    cells = {(c["kind"], c["span"], c["market"]): c for c in cacpi["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 3 * 3 * 2
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"], line["market"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        shares = [cell["base_up"], cell["base_same"], cell["base_down"]]
        assert "/".join(f"{s:.2f}" for s in shares) == line["base"]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert (cell["graded"], cell["right"]) == (int(line["graded"]), int(line["right"]))
        assert str(cell["say"]).startswith(f"After {cli.ask_kind(name, line['kind'])},")
        assert "%" not in str(cell["say"])
    assert [k["events"] for k in cacpi["kinds"]] == [14, 15, 15]  # type: ignore[index]


CNCPI = flows.CN_CPI_FLOW
CNPMI = flows.CN_PMI_FLOW
CNIP = flows.CN_IP_FLOW
CNTRADE = flows.CN_TRADE_FLOW


def _store_china(
    flow: flows.TradingViewFlow, prints: Mapping[date, tuple[float, float]], at: time = time(9, 30)
) -> list[flows.EventInstance]:
    # a release of one of China's flows at ``at`` Beijing on each day, with its actual and
    # TradingView's forecast, and its surprise row as `load-surprises` stores it
    db.init_db()
    events = [
        flow.event_instance(datetime.combine(day, at, tzinfo=sources.SHANGHAI), day)
        for day in prints
    ]
    db.insert_models("event_instances", events)
    db.insert_models(
        "surprises",
        [
            Surprise(
                event_id=e.event_id,
                measure=flow.measures[0],
                baseline="tradingview_forecast",
                actual_mom=actual,
                expected_mom=forecast,
                surprise=actual - forecast,
            )
            for e, (actual, forecast) in zip(events, prints.values(), strict=True)
        ],
    )
    return events


def test_a_chinese_cpi_release_shares_a_us_close_but_not_shanghai_s(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given four Chinese CPI releases at 09:30 Beijing: Wednesday 2024-01-10 with a US CPI release
    # at 08:30 New York that day, Saturday 2024-03-09 with a US jobs report the Monday after,
    # Friday 2024-02-09 and Sunday 2024-06-09 with nothing near; the S&P 500's and Shanghai's closes
    monkeypatch.setattr(
        study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in ("SPY / ES", "SHCOMP")}
    )
    days = [date(2024, 1, 10), date(2024, 3, 9), date(2024, 2, 9), date(2024, 6, 9)]
    prints = [(0.3, 0.2), (0.7, 0.4), (-0.8, -0.5), (0.3, 0.4)]
    events = _store_china(CNCPI, dict(zip(days, prints, strict=True)))
    db.insert_models("event_instances", [_report(days[0], CPI), _report(date(2024, 3, 11), NFP)])
    weekday_closes(("SPY / ES", "SHCOMP"), date(2024, 1, 1), date(2024, 6, 30))

    # when each market's shared releases and the kinds are read
    shared = study.shared_by_market(CNCPI)
    alone = study.lone_release_kinds(CNCPI)

    # then both reach the S&P 500 at the US release's close, but Shanghai's close comes before the
    # US releases, so there both are alone, and every release keeps its kind
    assert shared == {"SPY / ES": {events[0].event_id, events[1].event_id}, "SHCOMP": set()}
    assert [alone.get(e.event_id) for e in events] == [ABOVE, ABOVE, BELOW, BELOW]


def test_us_cpi_and_china_s_next_morning_share_shanghai_s_close_alone(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given US CPI at 08:30 New York on 2023-10-12 and China's at 09:30 Beijing on 2023-10-13,
    # and the S&P 500's and Shanghai's closes
    monkeypatch.setattr(
        study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in ("SPY / ES", "SHCOMP")}
    )
    (china,) = _store_china(CNCPI, {date(2023, 10, 13): (0.2, 0.2)})
    db.insert_models("event_instances", [_report(date(2023, 10, 12), CPI)])
    weekday_closes(("SPY / ES", "SHCOMP"), date(2023, 10, 2), date(2023, 10, 31))

    # when China's shared releases are read in each market
    shared = study.shared_by_market(CNCPI)

    # then both reach Shanghai at its 2023-10-13 close; the S&P 500 had US CPI the day before
    assert shared == {"SPY / ES": set(), "SHCOMP": {china.event_id}}


def test_two_releases_across_a_market_holiday_share_the_close_after_it(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given the S&P 500 closed on Monday 2024-01-15, a Canadian CPI release that Monday and a US
    # CPI release on the Tuesday
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", {"SPY / ES": study.MVP_PRICE_SERIES["SPY / ES"]})
    weekday_closes(("SPY / ES",), date(2024, 1, 1), date(2024, 1, 31))
    db.get_connection().execute("DELETE FROM daily_bars WHERE day = DATE '2024-01-15'")
    (canada,) = _store_cacpi({date(2024, 1, 15): (3.4, 3.3)})
    db.insert_models("event_instances", [_report(date(2024, 1, 16), CPI)])

    # when Canada's shared releases are read
    shared = study.shared_in(CACPI, "SPY / ES")

    # then both reach the market at Tuesday's close, so the Canadian release is shared
    assert shared == {canada.event_id}


def test_china_s_cpi_and_output_on_one_day_each_leave_that_day_out(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given Chinese CPI releases on Wednesday 2024-01-10 and Friday 2024-02-09, and output releases
    # at 10:00 Beijing on that Wednesday and on Monday 2024-03-18, and two markets' closes
    monkeypatch.setattr(
        study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in ("SPY / ES", "SHCOMP")}
    )
    weekday_closes(("SPY / ES", "SHCOMP"), date(2024, 1, 1), date(2024, 3, 29))
    cpi = _store_china(CNCPI, {date(2024, 1, 10): (0.3, 0.2), date(2024, 2, 9): (0.2, 0.2)})
    output = _store_china(
        CNIP, {date(2024, 1, 10): (5.3, 5.0), date(2024, 3, 18): (5.2, 5.0)}, time(10, 0)
    )

    # when each flow's kinds on its days alone are read
    cpi_alone = study.lone_release_kinds(CNCPI)
    output_alone = study.lone_release_kinds(CNIP)

    # then the shared Wednesday is in neither table; output is above from 0.3, as expected at 0.2
    assert [cpi_alone.get(e.event_id) for e in cpi] == [None, AS_EXPECTED]
    assert [output_alone.get(e.event_id) for e in output] == [None, AS_EXPECTED]
    assert study.release_kinds(CNIP)[output[0].event_id] == ABOVE


def test_a_chinese_survey_on_a_sunday_shares_the_us_survey_s_monday_close_in_us_markets(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, weekday_closes: Callable[..., None]
) -> None:
    # given Chinese surveys at 09:30 Beijing on Sunday 2024-03-31, with the US survey on Monday
    # 2024-04-01, on Sunday 2024-06-30 with nothing on its Monday, and on Wednesday 2024-01-31;
    # the S&P 500's and Shanghai's closes
    monkeypatch.setattr(
        study, "MVP_PRICE_SERIES", {m: study.MVP_PRICE_SERIES[m] for m in ("SPY / ES", "SHCOMP")}
    )
    days = [date(2024, 3, 31), date(2024, 6, 30), date(2024, 1, 31)]
    prints = [(50.8, 50.1), (49.5, 49.4), (49.1, 49.3)]
    events = _store_china(CNPMI, dict(zip(days, prints, strict=True)))
    db.insert_models("event_instances", [_report(date(2024, 4, 1), flows.flow_named("ism"))])
    weekday_closes(("SPY / ES", "SHCOMP"), date(2024, 1, 1), date(2024, 7, 31))

    # when each market's shared releases and the kinds are read
    shared = study.shared_by_market(CNPMI)
    every = study.release_kinds(CNPMI)

    # then the Sunday's survey shares Monday's close in the S&P 500 alone, as Shanghai closes
    # before the US survey; above from 0.2 points, as expected at 0.1
    assert shared == {"SPY / ES": {events[0].event_id}, "SHCOMP": set()}
    assert [every.get(e.event_id) for e in events] == [ABOVE, AS_EXPECTED, BELOW]


@pytest.mark.parametrize(
    ("flow", "noun", "prints"),
    [
        (CNCPI, "Chinese CPI releases", ((0.3, 0.2), (0.2, 0.2), (0.2, 0.3))),
        (CNPMI, "Chinese PMI releases", ((50.4, 50.2), (50.3, 50.2), (50.0, 50.2))),
        (CNIP, "Chinese output releases", ((5.3, 5.0), (5.2, 5.0), (4.7, 5.0))),
        (CNTRADE, "Chinese trade releases", ((8.3, 6.0), (8.2, 6.0), (3.7, 6.0))),
    ],
)
def test_follows_for_a_chinese_flow_prints_its_lone_releases_and_the_page_s_cells_are_its_lines(
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    flow: flows.TradingViewFlow,
    noun: str,
    prints: tuple[tuple[float, float], ...],
) -> None:
    # given Shanghai's and the yuan's closes and 45 releases of one of China's flows, above, as
    # expected and below in turn, the first on the day of a US retail sales release, which reaches
    # both markets a close later
    two = {k: study.MVP_PRICE_SERIES[k] for k in ("SHCOMP", "USDCNY")}
    monkeypatch.setattr(study, "MVP_PRICE_SERIES", two)
    rng = random.Random(7)
    closes = _closes([rng.gauss(0, 0.005) for _ in range(1400)])
    keys = list(range(30, 1380, 30))
    db.init_db()
    db.get_connection().executemany(
        "INSERT INTO daily_bars (instrument, day, close, source) VALUES (?, ?, ?, 'test')",
        [[m, c.day, c.price] for m in two for c in closes],
    )
    _store_china(flow, {closes[k].day: prints[j % 3] for j, k in enumerate(keys)})
    db.insert_models("event_instances", [_report(closes[keys[0]].day, RETAIL)])

    # when follows prints the table and the page's data is built
    assert main(["follows", "--event", flow.cli_name]) == 0
    out = capsys.readouterr().out.splitlines()
    printed = [FOLLOWS_LINE.match(line) for line in out[2:-1]]
    ask = cli.ask_data(db.get_connection())

    # then the header counts all 45, none sharing a close, and every line has one cell on the page
    first, last = closes[keys[0]].day, closes[keys[-1]].day
    assert out[0] == (f"follows: 45 {noun} {first} … {last}: 15 above, 15 as expected, 15 below")
    (entry,) = [entry for entry in ask["ask"] if entry["name"] == flow.cli_name]
    cells = {(c["kind"], c["span"], c["market"]): c for c in entry["cells"]}  # type: ignore[union-attr]
    assert len(printed) == len(cells) == 3 * 3 * 2
    for line in printed:
        assert line is not None
        cell = cells[(line["kind"], line["span"], line["market"])]
        assert [cell["up"], cell["same"], cell["down"]] == [
            int(line["up"]),
            int(line["same"]),
            int(line["down"]),
        ]
        assert (cell["answer"], cell["verdict"]) == (line["answer"], line["verdict"])
        assert str(cell["say"]).startswith(f"After {cli.ask_kind(flow.cli_name, line['kind'])},")
    assert [k["events"] for k in entry["kinds"]] == [15, 15, 15]  # type: ignore[index]
