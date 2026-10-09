"""The jobs-report forecast: refitted before every report on earlier reports only, and judged
beside the trend on the same reports."""

import random
from collections.abc import Callable
from dataclasses import replace
from datetime import date

import duckdb
import pytest

from fortuneteller import db, expectations, flows, study
from fortuneteller.__main__ import describe_side_by_side
from fortuneteller.expectations import (
    Actual,
    Expectation,
    MonthlyChange,
    PayrollModel,
    build_surprises,
    previous_month,
)
from fortuneteller.models import EventInstance
from fortuneteller.sources import PAYROLLS, FirstRelease
from fortuneteller.study import SurpriseTracking


def _planted(adp: float, claims: float, trend: float) -> float:
    return 20 + 0.5 * adp - 2 * claims + 0.3 * trend


class History:
    """Monthly jobs reports with their ADP and claims inputs, released in order: claims on the
    20th, ADP on the 4th of the next month, the report on the 6th."""

    def __init__(
        self, start: date, months: int, payrolls: Callable[[date, float, float, float], float]
    ) -> None:
        rng = random.Random(7)
        self.events: list[EventInstance] = []
        self.actuals: list[Actual] = []
        self.adp: dict[date, MonthlyChange] = {}
        self.claims: dict[date, MonthlyChange] = {}
        month, values = start, []
        for _ in range(months):
            following = date(month.year + month.month // 12, month.month % 12 + 1, 1)
            adp, claims = rng.uniform(-300, 300), rng.uniform(-50, 50)
            trend = sum(values[-12:]) / 12 if len(values) >= 12 else None
            value = (
                payrolls(month, adp, claims, trend) if trend is not None else rng.uniform(0, 300)
            )
            event = flows.to_event_instance(
                FirstRelease(month, following.replace(day=6), 1.0), flows.NFP_FLOW
            )
            self.events.append(event)
            self.actuals.append(Actual(event.event_id, PAYROLLS, month, value, "thousands"))
            self.adp[month] = MonthlyChange(month, following.replace(day=4), adp)
            self.claims[month] = MonthlyChange(month, month.replace(day=20), claims)
            values.append(value)
            month = following

    def forecasts(self, monkeypatch: pytest.MonkeyPatch) -> dict[date, Expectation]:
        monkeypatch.setattr(expectations, "load_model_inputs", lambda key: (self.adp, self.claims))
        months = {a.event_id: a.period for a in self.actuals}
        found = PayrollModel().expectations(self.events, self.actuals, "key")
        return {months[e.event_id]: e for e in found}


def _exact(month: date, adp: float, claims: float, trend: float) -> float:
    return _planted(adp, claims, trend)


def test_a_planted_relationship_is_recovered_once_36_reports_are_behind(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given six years of reports that follow the planted formula from their 13th month on
    history = History(date(2010, 1, 1), 72, _exact)

    # when the model forecasts them
    forecasts = history.forecasts(monkeypatch)

    # then the first forecast waits for 12 months of trend and 36 fitted reports, and each is exact
    assert min(forecasts) == date(2014, 1, 1)
    assert len(forecasts) == 24
    actual = {a.period: a.value for a in history.actuals}
    for month, forecast in forecasts.items():
        assert forecast.value == pytest.approx(actual[month], abs=1e-6)
        assert forecast.measure == PAYROLLS
        assert forecast.source == expectations.PAYROLL_MODEL


def test_covid_months_are_forecast_but_not_fitted_on(monkeypatch: pytest.MonkeyPatch) -> None:
    # given the planted formula throughout, except March 2020 – April 2021, 20 million jobs off
    def covid(month: date, adp: float, claims: float, trend: float) -> float:
        hit = date(2020, 3, 1) <= month <= date(2021, 4, 1)
        return _planted(adp, claims, trend) - (20_000 if hit else 0)

    history = History(date(2015, 1, 1), 96, covid)

    # when the model forecasts them
    forecasts = history.forecasts(monkeypatch)

    # then the COVID months get a forecast, and every later one is still exact
    actual = {a.period: a.value for a in history.actuals}
    assert date(2020, 4, 1) in forecasts
    later = [month for month in forecasts if month > date(2021, 4, 1)]
    assert len(later) == 20
    for month in later:
        assert forecasts[month].value == pytest.approx(actual[month], abs=1e-6)


def _noisy(month: date, adp: float, claims: float, trend: float) -> float:
    return _planted(adp, claims, trend) + random.Random(month.toordinal()).gauss(0, 40)


def test_nothing_published_at_or_after_a_report_changes_its_forecast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given noisy reports, and the same history with every number from report 60 on changed
    history = History(date(2010, 1, 1), 72, _noisy)
    target = history.events[60]
    released = flows.release_date(target)
    original = history.forecasts(monkeypatch)
    history.actuals = [
        replace(a, value=a.value * 3 + 100) if e.event_ts >= target.event_ts else a
        for a, e in zip(history.actuals, history.events, strict=True)
    ]
    for inputs in (history.adp, history.claims):
        for month, change in inputs.items():
            if change.released >= released:
                inputs[month] = replace(change, change=change.change - 77)

    # when the model forecasts again
    changed = history.forecasts(monkeypatch)

    # then the target's forecast is the same, and it was known before the report
    month = expectations.event_month(target)
    assert changed[month] == original[month]
    assert changed[month].known_at < target.event_ts
    assert changed[previous_month(month)] == original[previous_month(month)]


def test_the_shared_check_accepts_the_model_and_refuses_a_late_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given noisy reports whose forecasts all pass the shared check
    history = History(date(2010, 1, 1), 72, _noisy)
    forecasts = history.forecasts(monkeypatch)
    rows = build_surprises(
        history.events, history.actuals, list(forecasts.values()), [flows.NFP_EVENT_TYPE]
    )
    assert len(rows) == 24

    # when ADP for one month is dated the day of its report instead of two days before
    late = date(2015, 3, 1)
    history.adp[late] = replace(history.adp[late], released=date(2015, 4, 6))
    forecasts = history.forecasts(monkeypatch)

    # then that forecast is refused by the shared check
    with pytest.raises(ValueError, match="not before the event"):
        build_surprises(
            history.events, history.actuals, list(forecasts.values()), [flows.NFP_EVENT_TYPE]
        )


def _side_by_side_store() -> duckdb.DuckDBPyConnection:
    # 30 jobs reports, July 2019 – December 2021: the trend has all, the model the last 20.
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    months = [date(2019 + (6 + i) // 12, (6 + i) % 12 + 1, 1) for i in range(30)]
    flows.store_releases(
        flows.NFP_FLOW,
        [FirstRelease(m, date(m.year + m.month // 12, m.month % 12 + 1, 6), 1.0) for m in months],
        con=con,
    )
    rng = random.Random(4)
    for i, event in enumerate(flows.stored_events(flows.NFP_FLOW, con=con)):
        baselines = [expectations.TREND_12M] + ([expectations.PAYROLL_MODEL] if i >= 10 else [])
        for baseline in baselines:
            con.execute(
                "INSERT INTO surprises VALUES (?, ?, ?, 0, 0, ?)",
                [event.event_id, PAYROLLS, baseline, rng.gauss(0, 100)],
            )
        for instrument in study.MVP_PRICE_SERIES:
            con.execute(
                "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
                "VALUES (?, ?, 'pct', ?)",
                [event.event_id, instrument, rng.gauss(0, 1)],
            )
    return con


def test_compared_baselines_are_judged_on_the_same_reports() -> None:
    # given the trend on 30 reports and the model on the last 20
    con = _side_by_side_store()

    # when they are put side by side, with and without COVID's months
    everything = study.side_by_side(flows.NFP_FLOW, con=con)
    without = study.side_by_side(flows.NFP_FLOW, expectations.COVID_MONTHS, con=con)

    # then both are judged on the model's 20, then on its 8 outside March 2020 – April 2021
    for results, n in ((everything, 20), (without, 8)):
        for baseline in (expectations.TREND_12M, expectations.PAYROLL_MODEL):
            assert {t.n for t in results[baseline].values()} == {n}
            assert results[baseline]["UST10Y / ZN"].verdict is not None
    official = study.track_surprises(flows.NFP_FLOW, con=con)
    assert official[(PAYROLLS, expectations.TREND_12M)]["UST10Y / ZN"].n == 30


def test_the_side_by_side_table_names_both_baselines_and_its_scope() -> None:
    # given one instrument's rows for the trend and the model
    trend = SurpriseTracking(134, 0.2, 0.001, 0.58, 80, 1.5, "unclear")
    model = SurpriseTracking(134, 0.3, 0.0001, 0.62, 70, 2.0, "tracks")
    results = {
        expectations.TREND_12M: {i: trend for i in study.MVP_PRICE_SERIES},
        expectations.PAYROLL_MODEL: {i: model for i in study.MVP_PRICE_SERIES},
    }

    # when it is written
    lines = describe_side_by_side(results, flows.NFP_SURPRISE_RULE, "all")

    # then it says what it compares and that it is not the official verdict, a row per baseline
    assert lines[1] == (
        "payrolls against the 12-month trend and the payroll model, on the same reports (all); "
        "not the official verdict"
    )
    assert lines[2].startswith("instrument   baseline       n    rank corr")
    assert lines[5] == (
        "UST10Y / ZN  trend_12m      134  0.20       0.0010  58% (80)      1.5 bp     unclear"
    )
    assert lines[6] == (
        "UST10Y / ZN  payroll_model  134  0.30       0.0001  62% (70)      2.0 bp     tracks"
    )
