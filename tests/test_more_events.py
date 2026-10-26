"""Step 4's flows: retail sales, core PCE and GDP, each a change in one FRED level."""

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, expectations, flows, sources, study
import fortuneteller.__main__ as cli
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.flows import GDP_FLOW, PCE_FLOW, RETAIL_FLOW, LevelFlow
from fortuneteller.sources import NEW_YORK, FirstRelease

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
    identities = {(flow.event_type, flow.country) for flow in flows.EVENT_FLOWS}
    assert len(identities) == len(flows.EVENT_FLOWS)


def _store_with_surprise(
    con: duckdb.DuckDBPyConnection, flow: LevelFlow | flows.CpiFlow, measure: str, days: list[date]
) -> None:
    releases = [FirstRelease(day.replace(day=1) - timedelta(days=20), day, 1.0) for day in days]
    flows.store_releases(flow, releases, con=con)
    for i, event in enumerate(flows.stored_events(flow, con=con)):
        con.execute(
            "INSERT INTO surprises VALUES (?, ?, ?, 0, 0, ?)",
            [event.event_id, measure, expectations.NASDAQ_CONSENSUS, 0.5 + i],
        )
        for instrument in study.MVP_PRICE_SERIES:
            con.execute(
                "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
                "VALUES (?, ?, 'pct', ?)",
                [event.event_id, instrument, 0.1 + i],
            )


def test_a_new_flow_leaves_out_a_release_on_another_flow_s_day(tmp_db: Path) -> None:
    # given retail sales on 2024-03-12, the day CPI came out, and on 2024-04-15 alone
    con = db.get_connection()
    _store_with_surprise(con, flows.CPI_FLOW, sources.CORE, [date(2024, 3, 12)])
    _store_with_surprise(
        con, RETAIL_FLOW, sources.RETAIL_SALES, [date(2024, 3, 12), date(2024, 4, 15)]
    )

    # when each flow's surprises and moves are read
    retail = study.surprise_pairs(
        RETAIL_FLOW, [(sources.RETAIL_SALES, expectations.NASDAQ_CONSENSUS)], con=con
    )
    cpi = study.surprise_pairs(
        flows.CPI_FLOW, [(sources.CORE, expectations.NASDAQ_CONSENSUS)], con=con
    )

    # then retail sales keeps only its own day; CPI keeps the shared one
    assert retail[(sources.RETAIL_SALES, expectations.NASDAQ_CONSENSUS)]["DXY"] == ([1.5], [1.1])
    assert cpi[(sources.CORE, expectations.NASDAQ_CONSENSUS)]["DXY"] == ([0.5], [0.1])
    assert list(study.shared_days(RETAIL_FLOW, con=con).values()) == [date(2024, 3, 12)]


def test_surprise_lists_the_releases_left_out(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a retail sales release on a CPI day, and three alone
    con = db.get_connection()
    _store_with_surprise(con, flows.CPI_FLOW, sources.CORE, [date(2024, 3, 12)])
    alone = [date(2024, 4, 15), date(2024, 5, 15), date(2024, 6, 14)]
    _store_with_surprise(con, RETAIL_FLOW, sources.RETAIL_SALES, [date(2024, 3, 12), *alone])

    # when retail sales' report is printed
    code = main(["surprise", "--event", "retail"])

    # then it names the release left out
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[-2:] == [
        "left out: 1 RET releases on a day with another event's release",
        "2024-03-12",
    ]


def _tradingview_quarter(
    monkeypatch: pytest.MonkeyPatch, rows: list[tuple[str, date, str]]
) -> None:
    payload = json.dumps(
        {
            "status": "ok",
            "result": [
                {"title": title, "country": country, "date": f"{day}T12:30:00.000Z"}
                for title, day, country in rows
            ],
        }
    ).encode()
    monkeypatch.setattr(sources, "fetch_tradingview_quarter", lambda quarter, cache_dir: payload)


def test_another_flow_s_row_on_the_calendar_shares_the_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a day with retail sales, US core CPI, the Fed's decision and a UK row of CPI's name,
    # and the jobs report the day after
    day = date(2026, 11, 17)
    _tradingview_quarter(
        monkeypatch,
        [
            ("Retail Sales MoM", day, "US"),
            ("Core Inflation Rate MoM", day, "US"),
            ("Fed Interest Rate Decision", day, "US"),
            ("Core Inflation Rate MoM", day, "GB"),
            ("Non Farm Payrolls", day + timedelta(days=1), "US"),
        ],
    )

    # when retail sales asks who else is out that day
    others = expectations.other_releases([sources.RETAIL_SALES], day, tmp_path)

    # then the US CPI and the Fed are named, not retail sales itself, the UK or the next day
    assert others == ["Core Inflation Rate MoM", expectations.FED_DECISION_ROW]


def test_a_lesser_flow_s_row_shares_nobody_s_day_but_its_own_day_is_shared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a Thursday with retail sales and the claims report
    day = date(2026, 11, 19)
    _tradingview_quarter(
        monkeypatch, [("Retail Sales MoM", day, "US"), ("Initial Jobless Claims", day, "US")]
    )
    lesser = [sources.INITIAL_CLAIMS]

    # when each asks who else is out that day
    retail = expectations.other_releases([sources.RETAIL_SALES], day, tmp_path, lesser=lesser)
    claims = expectations.other_releases([sources.INITIAL_CLAIMS], day, tmp_path, lesser=lesser)

    # then retail sales has the day to itself, and claims shares it
    assert (retail, claims) == ([], ["Retail Sales MoM"])


@pytest.mark.parametrize(
    ("estimate", "expected"),
    [
        ("GDP Growth Rate QoQ Adv", ["GDP Growth Rate QoQ Adv"]),
        ("GDP Growth Rate QoQ 2nd Est", []),
        ("GDP Growth Rate QoQ Final", []),
    ],
)
def test_only_gdp_s_advance_estimate_shares_a_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, estimate: str, expected: list[str]
) -> None:
    # given a core PCE day that also holds one of GDP's three estimates
    day = date(2026, 11, 25)
    _tradingview_quarter(
        monkeypatch, [("Core PCE Price Index MoM", day, "US"), (estimate, day, "US")]
    )

    # when core PCE asks who else is out that day
    others = expectations.other_releases([sources.CORE_PCE], day, tmp_path)

    # then only the advance estimate, GDP's flow, shares it
    assert others == expected


def test_a_live_release_on_a_shared_day_logs_every_link_silent(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given retail sales' history, and its next release on a day CPI also comes out
    _store_with_surprise(
        db.get_connection(), RETAIL_FLOW, sources.RETAIL_SALES, [date(2024, 4, 15)]
    )
    day = date(2026, 11, 17)
    monkeypatch.setattr(
        expectations,
        "next_consensus",
        lambda measure, today, cache_dir: expectations.NextConsensus(day, 0.4, 0.4),
    )
    monkeypatch.setattr(cli, "_now", lambda: datetime.combine(day, time(9), tzinfo=NEW_YORK))
    _tradingview_quarter(
        monkeypatch, [("Retail Sales MoM", day, "US"), ("Core Inflation Rate MoM", day, "US")]
    )

    # when its actual is typed in, a big surprise
    code = main(["predict", "--event", "retail", "--actual", "1.4"])

    # then no call is made, and both of its links are logged silent
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[1] == "no prediction: 2026-11-17 also holds Core Inflation Rate MoM"
    calls = study.read_calls(settings.calls_path)
    assert [(c.flow, c.instrument, c.outcome) for c in calls] == [
        ("retail", "UST10Y / ZN", study.SILENT),
        ("retail", "DXY", study.SILENT),
    ]
