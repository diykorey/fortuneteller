"""Step 4's flows: retail sales, core PCE and GDP, each a change in one FRED level."""

import json
from datetime import date

import pytest

from fortuneteller import flows, sources
from fortuneteller.flows import GDP_FLOW, PCE_FLOW, RETAIL_FLOW, LevelFlow
from fortuneteller.sources import FirstRelease

# Real levels as FRED's revision history holds them: {reference month: {release day: level}}.
RETAIL_LEVELS = {
    "2026-05-01": {"2026-06-17": "763705", "2026-07-16": "766876", "2026-08-14": "766192"},
    "2026-06-01": {"2026-07-16": "768553", "2026-08-14": "768072"},
    "2026-07-01": {"2026-08-14": "763602"},
}
GDP_LEVELS = {
    "2026-01-01": {"2026-04-30": "24174.527", "2026-05-28": "24152.656", "2026-06-25": "24180.419"},
    "2026-04-01": {"2026-07-30": "24270.599"},
}


def _vintages_payload(series_id: str, levels: dict[str, dict[str, str]]) -> bytes:
    rows = [
        {"date": month} | {f"{series_id}_{day.replace('-', '')}": v for day, v in days.items()}
        for month, days in levels.items()
    ]
    return json.dumps({"count": len(rows), "observations": rows}).encode()


def _first_prints(levels: dict[str, dict[str, str]], skip: int) -> list[FirstRelease]:
    return [
        FirstRelease(
            date.fromisoformat(month), date.fromisoformat(min(days)), float(days[min(days)])
        )
        for month, days in list(levels.items())[skip:]
    ]


def _actuals(
    monkeypatch: pytest.MonkeyPatch,
    flow: LevelFlow,
    levels: dict[str, dict[str, str]],
    prints: list[FirstRelease],
) -> dict[str, float]:
    payload = _vintages_payload(flow.series_id, levels)
    monkeypatch.setattr(sources, "fetch_vintages", lambda _key, _series: payload)
    events = [flows.to_event_instance(release, flow) for release in prints]
    return {
        f"{actual.period:%Y-%m}": round(actual.value, 3)
        for actual in flow.actuals(events, "test-key")
    }


def test_retail_sales_change_is_against_the_previous_month_as_revised_that_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given May 2026 first printed at 763,705 and revised to 766,876 the day June came out
    prints = _first_prints(RETAIL_LEVELS, skip=1)

    # when the actuals are built
    actuals = _actuals(monkeypatch, RETAIL_FLOW, RETAIL_LEVELS, prints)

    # then each change is against the revised level, as Census printed it (+0.2% and -0.6%)
    assert actuals == {"2026-06": 0.219, "2026-07": -0.582}


def test_gdp_change_is_annualized_from_the_quarter_before(monkeypatch: pytest.MonkeyPatch) -> None:
    # given the first quarter of 2026 as it stood when the second's advance estimate came out
    prints = _first_prints(GDP_LEVELS, skip=1)

    # when the actual is built
    actuals = _actuals(monkeypatch, GDP_FLOW, GDP_LEVELS, prints)

    # then it is the annualized rate BEA printed: +1.5%
    assert actuals == {"2026-04": 1.5}


def test_a_stored_release_unlike_the_revision_history_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given June's stored first print differing from the level FRED's history holds for that day
    prints = _first_prints(RETAIL_LEVELS, skip=1)
    prints[0] = FirstRelease(prints[0].reference_month, prints[0].released, 768000.0)

    # when / then building the actuals fails, naming the month
    with pytest.raises(ValueError, match="retail_sales: .* 2026-06"):
        _actuals(monkeypatch, RETAIL_FLOW, RETAIL_LEVELS, prints)


def test_each_new_flow_has_its_own_event_type_and_command() -> None:
    # given the step 4 flows
    added = [RETAIL_FLOW, PCE_FLOW, GDP_FLOW]

    # when / then they are among the event flows, each its own type, code and name
    assert all(flow in flows.EVENT_FLOWS for flow in added)
    assert [flow.cli_name for flow in added] == ["retail", "pce", "gdp"]
    assert len({flow.event_type for flow in flows.EVENT_FLOWS}) == len(flows.EVENT_FLOWS)
