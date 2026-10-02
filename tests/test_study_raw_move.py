"""Raw move: every day's absolute move, and which of those days are CPI days."""

from datetime import date

import pytest

from fortuneteller.study import DailyClosingPrice, cpi_days, daily_moves


def _closes(*days_and_prices: tuple[date, float]) -> list[DailyClosingPrice]:
    return [DailyClosingPrice(day, price) for day, price in days_and_prices]


def test_each_day_gets_the_absolute_move_from_the_previous_close() -> None:
    # given three closes, up then down
    closes = _closes(
        (date(2022, 9, 12), 100.0), (date(2022, 9, 13), 110.0), (date(2022, 9, 14), 99.0)
    )

    # when the daily moves are computed in percent
    moves = daily_moves(closes, "pct")

    # then each day after the first has its move's size, keyed by its own date
    assert moves == {date(2022, 9, 13): pytest.approx(0.10), date(2022, 9, 14): pytest.approx(0.10)}


def test_yield_moves_are_in_basis_points() -> None:
    # given a 10-year yield falling from 4.20% to 4.05%
    closes = _closes((date(2022, 9, 12), 4.20), (date(2022, 9, 13), 4.05))

    # when the daily moves are computed in basis points
    moves = daily_moves(closes, "bps")

    # then the move is 15 bp
    assert moves == {date(2022, 9, 13): pytest.approx(15.0)}


def test_a_long_weekend_is_one_day_but_a_hole_in_the_data_is_not() -> None:
    # given Friday, the Tuesday after a long weekend, and then nothing until the next Monday
    closes = _closes(
        (date(2001, 9, 7), 100.0), (date(2001, 9, 11), 101.0), (date(2001, 9, 17), 95.0)
    )

    # when the daily moves are computed
    moves = daily_moves(closes, "pct")

    # then the four-day gap is a move, and the six-day gap is skipped
    assert list(moves) == [date(2001, 9, 11)]


def test_a_cpi_day_is_the_first_close_on_or_after_the_release() -> None:
    # given closes around a Tuesday release and a Sunday release
    closes = _closes(
        (date(2022, 9, 12), 1.0),
        (date(2022, 9, 13), 1.0),
        (date(1992, 12, 11), 1.0),
        (date(1992, 12, 14), 1.0),
    )
    closes.sort(key=lambda close: close.day)

    # when the CPI days are found
    days = cpi_days(closes, [date(2022, 9, 13), date(1992, 12, 13)])

    # then they are the release day itself and the Monday after the Sunday
    assert days == {date(2022, 9, 13), date(1992, 12, 14)}


def test_releases_step_2_skips_are_not_cpi_days() -> None:
    # given closes that start after one release and stop well before another
    closes = _closes((date(2000, 1, 3), 1.0), (date(2000, 1, 4), 1.0))

    # when the CPI days are found
    days = cpi_days(closes, [date(1999, 12, 14), date(2000, 2, 15)])

    # then neither release has one
    assert days == set()


def test_two_releases_paired_with_one_close_give_one_cpi_day() -> None:
    # given a Friday and a Monday close
    closes = _closes((date(2026, 1, 9), 1.0), (date(2026, 1, 12), 1.0))

    # when a Saturday and a Sunday release both pair with Monday
    days = cpi_days(closes, [date(2026, 1, 10), date(2026, 1, 11)])

    # then Monday counts once
    assert days == {date(2026, 1, 12)}
