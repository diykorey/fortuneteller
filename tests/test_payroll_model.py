"""The jobs-report forecast: refitted before every report, on earlier reports only."""

import random
from collections.abc import Callable
from dataclasses import replace
from datetime import date

import pytest

from fortuneteller import expectations, flows
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
