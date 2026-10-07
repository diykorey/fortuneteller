"""The jobs-report forecast's inputs: ADP's and the jobless claims' changes, as first published."""

from datetime import date
from pathlib import Path

import pytest

from fortuneteller import expectations, sources
from fortuneteller.expectations import MonthlyChange, adp_changes, claims_changes, survey_week
from fortuneteller.sources import parse_first_releases, parse_vintages

DATA = Path(__file__).parent / "data"
ADP_FIXTURES = {
    "NPPTTL": DATA / "fred_nppttl_new_and_revised.json",
    "ADPMNUSNERSA": DATA / "fred_adpmnusnersa_new_and_revised.json",
}
CLAIMS_FIXTURE = DATA / "fred_claims_initial_release.json"


def _adp() -> dict[date, MonthlyChange]:
    return adp_changes(
        {sid: parse_vintages(path.read_bytes(), sid) for sid, path in ADP_FIXTURES.items()}
    )


def test_adp_s_first_prints_match_its_releases_in_thousands() -> None:
    # given FRED's revision history of ADP, old method and new

    # when the first-published changes are taken
    adp = _adp()

    # then they are ADP's headlines: April 2020, May 2022, the relaunch in September 2022, Sep 2025
    assert adp[date(2020, 4, 1)].change == pytest.approx(-20236.067)
    assert adp[date(2022, 5, 1)].change == pytest.approx(128.225)
    assert adp[date(2022, 9, 1)] == MonthlyChange(date(2022, 9, 1), date(2022, 10, 5), 208.0)
    assert adp[date(2025, 9, 1)] == MonthlyChange(date(2025, 9, 1), date(2025, 10, 1), -32.0)


def test_history_adp_republished_later_is_not_a_first_print() -> None:
    # given June and July 2022, which ADP did not publish then and filled in on 2023-02-01
    adp = _adp()

    # when / then they have no first print: nobody had those numbers before the jobs reports
    assert [m for m in (date(2022, 6, 1), date(2022, 7, 1), date(2022, 8, 1)) if m in adp] == []


@pytest.mark.parametrize(
    ("month", "week"),
    [
        (date(2022, 8, 1), date(2022, 8, 13)),  # the 12th a Friday
        (date(2022, 2, 1), date(2022, 2, 12)),  # the 12th a Saturday: its own week's end
        (date(2022, 6, 1), date(2022, 6, 18)),  # the 12th a Sunday: the week starts that day
    ],
)
def test_the_survey_week_is_the_week_that_includes_the_12th(month: date, week: date) -> None:
    # given a month

    # when its survey week is found
    found = survey_week(month)

    # then it is the Saturday that ends the week containing the 12th
    assert found == week


def test_the_claims_change_is_between_survey_weeks_known_when_the_later_one_came_out() -> None:
    # given the first prints of the 4-week average of initial claims for July and August 2022
    weeks, _valueless = parse_first_releases(CLAIMS_FIXTURE.read_bytes(), "IC4WSA")

    # when the monthly changes are taken
    changes = claims_changes(weeks)

    # then August's runs from the week ending 07-16 to the one ending 08-13, known on 08-18
    by_week = {w.reference_month: w.value for w in weeks}
    expected = (by_week[date(2022, 8, 13)] - by_week[date(2022, 7, 16)]) / 1000
    assert changes == {
        date(2022, 8, 1): MonthlyChange(date(2022, 8, 1), date(2022, 8, 18), expected)
    }


def test_loading_reads_both_adp_series_and_the_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    # given FRED answering with the saved replies
    monkeypatch.setattr(sources, "fetch_vintages", lambda _key, sid: ADP_FIXTURES[sid].read_bytes())
    monkeypatch.setattr(
        sources, "fetch_first_releases", lambda _key, series_id: CLAIMS_FIXTURE.read_bytes()
    )

    # when the inputs are loaded
    adp, claims = expectations.load_model_inputs("key")

    # then both ADP methods and the claims are there
    assert {date(2020, 4, 1), date(2022, 9, 1)} <= set(adp)
    assert set(claims) == {date(2022, 8, 1)}
