"""M1-03 tests — the conditional-direction resolver.

Exercises the CPI core slice against the seeded ``surprise_response`` mapping: hot → base
direction, cool → inverse, in-line / no-mapping → mixed, and the regime flip on regime-sensitive
cells.
"""

from __future__ import annotations

import duckdb

from fortuneteller.predict.direction import resolve_direction

CPI = "CPI / inflation surprise"


def _resolve(con: duckdb.DuckDBPyConnection, instrument: str, sign: str, regime: str | None) -> str:
    return str(resolve_direction(CPI, instrument, sign, regime, con=con))


def test_hot_cpi_resolves_to_base_directions(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given a hot (above-consensus) CPI print in a neutral regime
    # when each core cell is resolved
    # then it takes the seeded hot_direction
    assert _resolve(seeded_con, "SPY / ES", "above", "on-hold") == "down"
    assert _resolve(seeded_con, "DXY", "above", "on-hold") == "up"
    assert _resolve(seeded_con, "GC / XAU", "above", "on-hold") == "down"
    assert _resolve(seeded_con, "BUND / FGBL", "above", "on-hold") == "down"
    assert _resolve(seeded_con, "VIX", "above", "on-hold") == "up"


def test_cool_cpi_resolves_to_the_inverses(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given a cool (below-consensus) CPI print in a neutral regime
    # when each core cell is resolved
    # then it takes the inverse of the hot_direction
    assert _resolve(seeded_con, "SPY / ES", "below", "on-hold") == "up"
    assert _resolve(seeded_con, "DXY", "below", "on-hold") == "down"
    assert _resolve(seeded_con, "GC / XAU", "below", "on-hold") == "up"
    assert _resolve(seeded_con, "BUND / FGBL", "below", "on-hold") == "up"
    assert _resolve(seeded_con, "VIX", "below", "on-hold") == "down"


def test_in_line_and_unknown_resolve_to_mixed(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given an in-line / unknown surprise
    # when resolved
    # then there is no edge, so the direction is mixed (never invented)
    assert _resolve(seeded_con, "SPY / ES", "unknown", "on-hold") == "mixed"


def test_missing_mapping_resolves_to_mixed(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given an instrument with no surprise_response cell for CPI
    # when resolved
    # then it degrades to mixed rather than raising or inventing
    assert _resolve(seeded_con, "NVDA", "above", "on-hold") == "mixed"


def test_regime_flip_makes_good_news_bad_news(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given a cool (benign) CPI print in a rate-cut-hungry regime
    # when a regime-sensitive cell is resolved
    # then "good news is bad news" flips it back to risk-off (SPY down, DXY up)
    assert _resolve(seeded_con, "SPY / ES", "below", "easing-hungry") == "down"
    assert _resolve(seeded_con, "DXY", "below", "easing-hungry") == "up"
    # and a non-regime-sensitive cell is untouched by the regime
    assert _resolve(seeded_con, "GC / XAU", "below", "easing-hungry") == "up"


def test_resolution_is_deterministic(seeded_con: duckdb.DuckDBPyConnection) -> None:
    # given identical inputs
    # when resolved twice
    # then the result is identical
    first = resolve_direction(CPI, "SPY / ES", "above", "on-hold", con=seeded_con)
    second = resolve_direction(CPI, "SPY / ES", "above", "on-hold", con=seeded_con)
    assert first is second
