"""The jobs report's surprise: first-published payroll changes against their 12-month trend."""

from datetime import date
from pathlib import Path

import pytest

from fortuneteller import study
from fortuneteller.sources import NFP_SERIES_ID, FirstRelease, parse_vintages
from fortuneteller.study import NFP_EVENT_TYPE, PAYROLLS, MonthlyChange

DATA = Path(__file__).parent / "data"


def _vintages() -> dict[date, dict[date, float]]:
    return parse_vintages((DATA / "fred_nfp_new_and_revised.json").read_bytes(), NFP_SERIES_ID)


def test_a_change_is_measured_against_the_previous_month_as_revised_that_day() -> None:
    # given FRED's levels per release day for mid-2022 and late 2025
    vintages = _vintages()

    # when the first-published changes are taken
    changes = {
        c.reference_month: c
        for c in study.first_published_payroll_changes(vintages, date(2022, 7, 1))
    }

    # then August 2022 is +315k, the BLS headline, though July was first printed 107k higher
    assert changes[date(2022, 8, 1)] == MonthlyChange(date(2022, 8, 1), date(2022, 9, 2), 315.0)
    # and October and November 2025 both come from 2025-12-16, after the shutdown
    assert changes[date(2025, 10, 1)] == MonthlyChange(
        date(2025, 10, 1), date(2025, 12, 16), -105.0
    )
    assert changes[date(2025, 11, 1)] == MonthlyChange(date(2025, 11, 1), date(2025, 12, 16), 64.0)


def test_months_before_the_first_stored_release_are_left_out() -> None:
    # given the same vintages, and stored releases starting with August 2022
    vintages = _vintages()

    # when the changes are taken from August 2022
    changes = study.first_published_payroll_changes(vintages, date(2022, 8, 1))

    # then June and July 2022 are not among them
    assert min(c.reference_month for c in changes) == date(2022, 8, 1)


def test_the_trend_counts_only_months_published_before_the_release() -> None:
    # given a year of +100k months, then October +1000k published the same day as November
    changes = [
        MonthlyChange(date(2024 + (m + 9) // 12, (m + 9) % 12 + 1, 1), date(2024, 1, 1), 100.0)
        for m in range(12)
    ]
    changes = [
        MonthlyChange(
            c.reference_month, date(c.reference_month.year, c.reference_month.month, 28), c.change
        )
        for c in changes
    ]
    changes += [
        MonthlyChange(date(2025, 10, 1), date(2025, 12, 16), 1000.0),
        MonthlyChange(date(2025, 11, 1), date(2025, 12, 16), 64.0),
    ]

    # when the trends are computed
    trend = study.trend_expectations(changes)

    # then November's trend is the earlier months alone: nobody knew October before that day
    assert trend[date(2025, 11, 1)] == pytest.approx(100.0)


def test_a_month_published_with_a_later_one_is_skipped_and_any_other_gap_refused() -> None:
    # given a year of stored releases to September 2025, then November stored for 2025-12-16,
    # whose day also first published October
    year = [study.previous_month(date(2025, 10, 1))]
    while len(year) < 12:
        year.append(study.previous_month(year[-1]))
    trend = [MonthlyChange(m, _fifth_after(m), 100.0) for m in year]
    events = [
        study.to_event_instance(FirstRelease(c.reference_month, c.released, 1.0), NFP_EVENT_TYPE)
        for c in trend
    ]
    events.append(
        study.to_event_instance(
            FirstRelease(date(2025, 11, 1), date(2025, 12, 16), 159552.0), NFP_EVENT_TYPE
        )
    )
    carried = MonthlyChange(date(2025, 10, 1), date(2025, 12, 16), -105.0)
    stored = MonthlyChange(date(2025, 11, 1), date(2025, 12, 16), 64.0)
    lone = MonthlyChange(date(2025, 12, 1), date(2026, 1, 9), 50.0)

    # when the surprises are built
    rows = study.build_surprises(events, {PAYROLLS: [*trend, carried, stored]}, [])

    # then November gets its row and October none; a month published alone with nothing stored fails
    assert [(r.event_id, r.actual_mom) for r in rows] == [(2_2025_12_16, 64.0)]
    with pytest.raises(ValueError, match="payrolls 2025-12: no release stored"):
        study.build_surprises(events, {PAYROLLS: [*trend, lone]}, [])


def _fifth_after(month: date) -> date:
    return date(month.year + month.month // 12, month.month % 12 + 1, 5)


def test_a_stored_release_that_disagrees_with_the_revision_history_is_named() -> None:
    # given August 2022 stored as FRED first printed it, and September stored 1k off
    vintages = _vintages()
    events = [
        study.to_event_instance(
            FirstRelease(date(2022, 8, 1), date(2022, 9, 2), 152744.0), NFP_EVENT_TYPE
        ),
        study.to_event_instance(
            FirstRelease(date(2022, 9, 1), date(2022, 10, 7), 153019.0), NFP_EVENT_TYPE
        ),
    ]

    # when they are checked against the vintages
    missed = study.payroll_level_mismatches(vintages, events)

    # then only September is named
    assert missed == [date(2022, 9, 1)]
