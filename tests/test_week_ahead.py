from datetime import date, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import db, expectations, flows, sources, study
from fortuneteller.expectations import NextConsensus
from fortuneteller.study import ConfidentCall, Prediction

TODAY = date(2026, 11, 4)


def _consensus(days: dict[str, NextConsensus], asked: list[str]):
    def next_consensus(measure: str, today: date, cache_dir: Path) -> NextConsensus | None:
        asked.append(measure)
        found = days.get(measure)
        return found if found is not None and found.day >= today else None

    return next_consensus


def _replay(right: int, wrong: int, calling: int | None):
    """A replay of ``right`` and ``wrong`` up-calls, then the next release's call when
    ``calling`` is a direction."""
    made = [
        ConfidentCall(
            Prediction(i, "2020-01", 1.0, 1, 1.0 if i < right else -1.0), None, None, None
        )
        for i in range(right + wrong)
    ]
    if calling is not None:
        made.append(
            ConfidentCall(
                Prediction(study.NEXT_RELEASE, "next", 1.0, calling, 0.0), None, None, None
            )
        )
    return made


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    asked: list[str] = []
    days = {
        "payrolls": NextConsensus(TODAY + timedelta(days=2), 63.0, 65.0),
        "core": NextConsensus(TODAY + timedelta(days=8), None, 0.2),
        "initial_claims": NextConsensus(TODAY, 197.0, 196.0),
        "retail_sales": NextConsensus(TODAY + timedelta(days=7), None, 0.4),
    }
    monkeypatch.setattr(expectations, "next_consensus", _consensus(days, asked))
    monkeypatch.setattr(expectations, "other_releases", lambda *args, **kwargs: [])
    replays = {
        "UST10Y / ZN": _replay(20, 10, 1),
        "DXY": _replay(2, 1, None),
    }
    monkeypatch.setattr(
        study, "confident_links", lambda flow, baseline, con, next_surprise: replays
    )
    return asked


def test_the_week_ahead_lists_the_called_releases_of_the_next_seven_days(
    tmp_db: Path, stubs: list[str]
) -> None:
    # given the jobs report in two days, retail sales in seven, CPI in eight and claims today

    # when the week ahead is read
    ahead = cli.week_ahead(db.get_connection(), TODAY, Path("cache"))

    # then the jobs report and retail sales are listed, oldest first, and only flows `live` calls
    # are asked
    assert [(r["event"], r["day"]) for r in ahead] == [
        ("nfp", "2026-11-06"),
        ("retail", "2026-11-11"),
    ]
    called = {f.surprise_rule.combinations[0][0] for f in flows.EVENT_FLOWS if flows.called_live(f)}  # type: ignore[union-attr]
    assert set(stubs) == called


def test_each_release_shows_its_thresholds_and_each_link_s_rule_and_record(
    tmp_db: Path, stubs: list[str]
) -> None:
    # given the jobs report with Nasdaq's consensus and retail sales with TradingView's only

    # when the week ahead is read
    nfp, retail = cli.week_ahead(db.get_connection(), TODAY, Path("cache"))

    # then the threshold is the consensus either side of noticeable, Nasdaq's first, an open link
    # calls opposite ways either side with its record, and a closed one is silent with its own
    assert (nfp["consensus"], nfp["consensus_from"], nfp["below"], nfp["above"]) == (
        63.0,
        "Nasdaq",
        13.0,
        113.0,
    )
    assert (retail["consensus"], retail["consensus_from"]) == (0.4, "TradingView")
    assert nfp["links"] == {
        "UST10Y / ZN": {
            "above": "up",
            "below": "down",
            "right": 20,
            "predictions": 30,
            "always_right": 20,
            "verdict": study.grade([c.call for c in _replay(20, 10, None)], 1).verdict,
        },
        "DXY": {
            "above": None,
            "below": None,
            "right": 2,
            "predictions": 3,
            "always_right": 2,
            "verdict": study.TOO_FEW,
        },
    }


def test_a_release_sharing_its_day_is_silent_on_every_link(
    tmp_db: Path, stubs: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given claims, a flow whose rule leaves shared days out, on a day the jobs report shares
    claims = NextConsensus(TODAY + timedelta(days=2), 197.0, 196.0)
    monkeypatch.setattr(expectations, "next_consensus", _consensus({"initial_claims": claims}, []))
    monkeypatch.setattr(
        expectations, "other_releases", lambda *args, **kwargs: ["Non Farm Payrolls"]
    )

    # when the week ahead is read
    (release,) = cli.week_ahead(db.get_connection(), TODAY, Path("cache"))

    # then every link is silent and the other release is named
    assert release["event"] == "claims"
    assert release["shared"] == ["Non Farm Payrolls"]
    links = release["links"]
    assert isinstance(links, dict)
    assert all(link["above"] is None and link["below"] is None for link in links.values())


def test_a_calendar_that_cannot_be_read_leaves_the_week_ahead_empty(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a calendar that fails, and a scoreboard built from what is stored
    def broken(con: object, today: date, cache_dir: Path) -> list[dict[str, object]]:
        raise sources.CalendarError("TradingView is down")

    monkeypatch.setattr(cli, "week_ahead", broken)
    seen: dict[str, object] = {}

    def data(*args: object, ahead: object = "unset") -> dict[str, object]:
        seen["ahead"] = ahead
        raise ValueError("stop here")

    monkeypatch.setattr(
        cli, "scoreboard_data", lambda rows, con, today, graded, bad, ahead: data(ahead=ahead)
    )
    monkeypatch.setattr(cli, "_read_guesses", lambda con: ([], []))
    monkeypatch.setattr(db, "count_rows", lambda table, con=None: 1)

    # when the scoreboard is written
    cli.main(["scoreboard"])

    # then the error is printed and the page gets no week ahead
    assert "the week ahead: TradingView is down" in capsys.readouterr().err
    assert seen["ahead"] is None
