"""Raw move: do the instruments move more on CPI days than on all other days?"""

import random
from datetime import date, timedelta
from pathlib import Path
from statistics import median

import duckdb
import pytest

from fortuneteller import db
from fortuneteller.__main__ import describe_raw_moves, main
from fortuneteller.models import DailyBar
from fortuneteller.stats import median_not_drawn
from fortuneteller.sources import (
    CpiRelease,
    DailyClosingPrice,
)
from fortuneteller.study import (
    DOESNT_MOVE,
    MOVES,
    MVP_PRICE_SERIES,
    UNCLEAR,
    EraRatio,
    MoveComparison,
    RawMove,
    compare_moves,
    cpi_days,
    daily_moves,
    measure_raw_moves,
    move_verdict,
    store_cpi_releases,
)


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


def _sizes(count: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [rng.expovariate(1.0) for _ in range(count)]


def test_the_median_of_the_undrawn_moves_matches_a_plain_median() -> None:
    # given a sorted pool and many random draws from it
    pool = sorted(_sizes(41, seed=1))
    rng = random.Random(2)

    for _ in range(200):
        drawn = sorted(rng.sample(range(len(pool)), rng.randint(1, 40)))

        # when the median of the rest is read without building the rest
        result = median_not_drawn(pool, drawn)

        # then it equals the median of the rest built the slow way
        rest = [move for i, move in enumerate(pool) if i not in set(drawn)]
        assert result == median(rest)


def test_cpi_days_twice_as_large_are_a_move() -> None:
    # given ordinary days, and CPI days twice their size
    other = _sizes(2000, seed=1)
    cpi = [2 * move for move in _sizes(200, seed=2)]

    # when they are compared
    result = compare_moves(cpi, other)

    # then the ratio is about 2, no relabelling beats it, and the verdict is "moves"
    assert result.ratio == pytest.approx(2.0, rel=0.25)
    assert result.p == pytest.approx(1 / 10_001)
    assert result.verdict == MOVES
    assert result.cpi_days == 200


def test_cpi_days_like_any_other_day_are_not_a_move() -> None:
    # given CPI days drawn from the same distribution as the other days
    other = _sizes(2000, seed=1)
    cpi = _sizes(200, seed=3)

    # when they are compared
    result = compare_moves(cpi, other)

    # then nothing is found
    assert result.ratio == pytest.approx(1.0, abs=0.15)
    assert result.p > 0.01
    assert result.verdict != MOVES


def test_the_same_input_gives_the_same_p() -> None:
    # given one set of moves
    other = _sizes(2000, seed=1)
    cpi = [1.05 * move for move in _sizes(200, seed=4)]

    # when they are compared twice
    first, second = compare_moves(cpi, other), compare_moves(cpi, other)

    # then the results are identical
    assert first == second


@pytest.mark.parametrize(
    ("ratio", "p", "expected"),
    [
        (1.10, 0.009, MOVES),
        (1.30, 0.01, UNCLEAR),
        (1.09, 0.0001, UNCLEAR),
        (1.05, 0.2, DOESNT_MOVE),
    ],
)
def test_the_verdict_needs_both_size_and_significance(
    ratio: float, p: float, expected: str
) -> None:
    # given a ratio and a p-value
    # when the verdict is read
    result = move_verdict(ratio, p)

    # then "moves" needs both, "unclear" one, "doesn't" neither
    assert result == expected


def _synthetic_store(con: duckdb.DuckDBPyConnection) -> None:
    # 36 monthly releases in 2021-2023; prices move 0.5% a day, and 2% on each release day.
    releases = []
    for month in range(36):
        year, month_index = 2021 + month // 12, month % 12 + 1
        released = date(year, month_index, 12)
        while released.weekday() >= 5:
            released += timedelta(days=1)
        reference = date(year - 1, 12, 1) if month_index == 1 else date(year, month_index - 1, 1)
        releases.append(CpiRelease(reference, released, 300.0))
    store_cpi_releases(releases, con=con)
    release_days = {release.released for release in releases}
    rng = random.Random(5)
    day, price, closes = date(2020, 12, 1), 100.0, []
    while day < date(2024, 1, 31):
        if day.weekday() < 5:
            size = 0.02 if day in release_days else 0.005
            price *= 1 + rng.choice((-1, 1)) * size * rng.uniform(0.5, 1.5)
            closes.append(DailyBar(instrument="", day=day, close=price, source="s"))
        day += timedelta(days=1)
    for instrument in MVP_PRICE_SERIES:
        bars = [bar.model_copy(update={"instrument": instrument}) for bar in closes]
        db.insert_models("daily_bars", bars, con=con)


def test_release_days_that_move_more_are_found_for_every_instrument() -> None:
    # given 36 releases on which every instrument moves four times its usual size
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    _synthetic_store(con)

    # when the raw moves are measured
    results = measure_raw_moves(con=con)

    # then each instrument moves, and only the 2020-now era has CPI days
    assert list(results) == list(MVP_PRICE_SERIES)
    for raw in results.values():
        assert raw.overall.verdict == MOVES
        assert raw.overall.cpi_days == 36
        assert raw.eras["2020-now"].cpi_days == 36
        assert raw.eras["1970-1989"] == EraRatio(0, None)


def test_the_report_shows_each_unit_and_marks_eras_without_cpi_days() -> None:
    # given one price instrument and one yield, each with a CPI-free era
    comparison = MoveComparison(649, 0.0055, 0.0051, 1.078, 0.0123, DOESNT_MOVE)
    eras = {"1970-1989": EraRatio(0, None), "2020-now": EraRatio(79, 1.04)}
    results = {
        "SPY / ES": RawMove("pct", comparison, eras),
        "UST10Y / ZN": RawMove("bps", MoveComparison(648, 4.0, 3.0, 1.33, 0.0001, MOVES), eras),
    }

    # when the report is written
    lines = describe_raw_moves(results)

    # then percent and basis points read as such, and a CPI-free era is a dash
    assert "SPY / ES          649       0.55%         0.51%   1.08  0.0123  doesn't" in lines
    assert "UST10Y / ZN       648      4.0 bp        3.0 bp   1.33  0.0001  moves" in lines
    assert "SPY / ES     —            1.04 (79)" in lines


def test_raw_move_prints_a_verdict_per_instrument_and_the_rule(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given releases and prices stored
    _synthetic_store(db.get_connection())

    # when the command runs
    code = main(["raw-move"])

    # then every instrument has a verdict line, and the rule is printed with them
    out = capsys.readouterr().out
    assert code == 0
    assert sum(line.endswith(" moves") for line in out.splitlines()) == 5
    assert "moves = ratio >= 1.10 and p < 0.01" in out


@pytest.mark.parametrize(
    ("load", "missing"),
    [(False, "load-releases"), (True, "load-prices")],
)
def test_raw_move_names_the_load_to_run_first(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], load: bool, missing: str
) -> None:
    # given an empty store, or releases without prices
    if load:
        store_cpi_releases([CpiRelease(date(2022, 8, 1), date(2022, 9, 13), 296.171)])

    # when the command runs
    code = main(["raw-move"])

    # then it stops with one line naming the command to run first
    err = capsys.readouterr().err
    assert code == 1
    assert f"`fortuneteller {missing}` first" in err
