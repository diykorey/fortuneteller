import random
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, flows, sources, stats, study
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
    surprises: list[tuple[date, str, float]], flow: flows.EventFlow = NFP, measure: str = "payrolls"
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
                actual_mom=0.0,
                expected_mom=0.0,
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
