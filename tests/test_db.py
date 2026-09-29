"""Tests for the M0-05 database helper (db.py)."""

from datetime import date
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db
from fortuneteller.config import settings
from fortuneteller.models import DailyBar, EffectSizeSeed, Instrument

EXPECTED_TABLES = {
    "event_types",
    "instruments",
    "effect_size_seed",
    "news_sources",
    "countries",
    "event_instances",
    "observations",
    "effect_size_matrix",
    "daily_bars",
}


def _seeded_connection() -> duckdb.DuckDBPyConnection:
    # given a fresh in-memory store with the schema applied
    con = duckdb.connect(":memory:")
    db.init_db(con=con)
    return con


def test_init_db_creates_file_and_tables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # given a temp DB path (test_ prefix marks it as a throwaway artifact)
    db_path = tmp_path / "test_fortuneteller.duckdb"
    monkeypatch.setattr(settings, "db_path", db_path)
    # when init_db runs against the default (now temp) path
    db.init_db()
    # then the file exists and holds all nine tables
    assert db_path.exists()
    con = duckdb.connect(str(db_path))
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert tables == EXPECTED_TABLES


def test_get_instrument_roundtrips() -> None:
    # given a known Instrument inserted into a seeded store
    con = _seeded_connection()
    instrument = Instrument(
        symbol="SPY / ES", name="S&P 500", asset_class="equity_index", region="us"
    )
    db.insert_models("instruments", [instrument], con=con)
    # when it is read back by symbol
    fetched = db.get_instrument("SPY / ES", con=con)
    # then an equal model comes back
    assert fetched == instrument


def test_get_instrument_missing_returns_none() -> None:
    # given a seeded but empty instruments table
    con = _seeded_connection()
    # when an unknown symbol is queried
    # then None is returned
    assert db.get_instrument("DOES / NOT EXIST", con=con) is None


def test_get_effect_size_roundtrips() -> None:
    # given a known effect-size seed row inserted into a seeded store
    con = _seeded_connection()
    seed = EffectSizeSeed(
        event_type="CPI / inflation surprise",
        instrument="SPY / ES",
        direction="conditional",
        typical_magnitude="0.5-1.5%",
        reaction_half_life="minutes_hours",
        direction_confidence="high",
        surprise_dependent="yes",
    )
    db.insert_models("effect_size_seed", [seed], con=con)
    # when it is read back by its composite key
    fetched = db.get_effect_size("CPI / inflation surprise", "SPY / ES", con=con)
    # then an equal model comes back
    assert fetched == seed


def test_get_effect_size_missing_returns_none() -> None:
    # given a seeded but empty effect_size_seed table
    con = _seeded_connection()
    # when an unknown pair is queried
    # then None is returned
    assert db.get_effect_size("nope", "nope", con=con) is None


def test_insert_models_returns_count_and_count_rows_agree() -> None:
    # given two instruments
    con = _seeded_connection()
    rows = [
        Instrument(symbol="SPY / ES", name="S&P 500", asset_class="equity_index", region="us"),
        Instrument(symbol="VIX", name="Volatility", asset_class="volatility", region="us"),
    ]
    # when they are inserted
    inserted = db.insert_models("instruments", rows, con=con)
    # then the returned count and count_rows both report two
    assert inserted == 2
    assert db.count_rows("instruments", con=con) == 2


def test_insert_models_empty_is_noop() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when an empty sequence is inserted
    # then it writes nothing and reports zero
    assert db.insert_models("instruments", [], con=con) == 0
    assert db.count_rows("instruments", con=con) == 0


def test_unknown_table_is_rejected() -> None:
    # given a seeded store
    con = _seeded_connection()
    # when an unknown table name is used
    # then it raises rather than building SQL
    with pytest.raises(ValueError):
        db.count_rows("instruments; DROP TABLE instruments", con=con)
    with pytest.raises(ValueError):
        db.insert_models("not_a_table", [], con=con)


def test_insert_models_keeps_a_value_that_first_appears_late() -> None:
    # given 150 instruments whose optional notes are empty except on the last one
    con = _seeded_connection()
    rows = [
        Instrument(symbol=f"I{i}", name=f"Instrument {i}", asset_class="fx", region="us")
        for i in range(149)
    ]
    rows.append(
        Instrument(symbol="LAST", name="Last", asset_class="fx", region="us", notes="filled late")
    )
    # when they are inserted in one call
    db.insert_models("instruments", rows, con=con)
    # then the late value is stored, not lost to a column type guessed from the first rows
    assert db.get_instrument("LAST", con=con) == rows[-1]


def test_insert_models_rejects_a_key_repeated_within_one_call() -> None:
    # given two closes for the same instrument on the same day
    con = _seeded_connection()
    rows = [
        DailyBar(instrument="VIX", day=date(2022, 9, 13), close=close, source="yahoo:^VIX")
        for close in (27.27, 99.0)
    ]
    # when they are written in one call
    # then the call fails loudly instead of silently keeping one of them
    with pytest.raises(ValueError, match="repeat a key"):
        db.insert_models("daily_bars", rows, con=con, replace=True)
    assert db.count_rows("daily_bars", con=con) == 0


def test_insert_models_replace_overwrites_an_existing_row() -> None:
    # given a stored close
    con = _seeded_connection()
    day = date(2022, 9, 13)
    db.insert_models(
        "daily_bars", [DailyBar(instrument="VIX", day=day, close=1.0, source="s")], con=con
    )
    # when a new value for the same key is written with replace=True
    db.insert_models(
        "daily_bars",
        [DailyBar(instrument="VIX", day=day, close=27.27, source="s")],
        con=con,
        replace=True,
    )
    # then the row holds the new value and is not duplicated
    assert con.execute("SELECT close FROM daily_bars").fetchall() == [(27.27,)]


def test_insert_models_without_replace_rejects_an_existing_key() -> None:
    # given a stored close
    con = _seeded_connection()
    day = date(2022, 9, 13)
    db.insert_models(
        "daily_bars", [DailyBar(instrument="VIX", day=day, close=1.0, source="s")], con=con
    )
    # when a row with the same key is written without replace
    # then the database refuses it and the stored value is untouched
    with pytest.raises(duckdb.ConstraintException):
        db.insert_models(
            "daily_bars", [DailyBar(instrument="VIX", day=day, close=27.27, source="s")], con=con
        )
    assert con.execute("SELECT close FROM daily_bars").fetchall() == [(1.0,)]


def test_replace_rows_leaves_the_table_untouched_when_the_insert_fails() -> None:
    # given a stored close
    con = _seeded_connection()
    day = date(2022, 9, 13)
    db.insert_models(
        "daily_bars", [DailyBar(instrument="VIX", day=day, close=27.27, source="s")], con=con
    )
    # when a rebuild deletes it and then fails on a repeated key
    rows = [DailyBar(instrument="VIX", day=day, close=c, source="s") for c in (1.0, 2.0)]
    with pytest.raises(ValueError, match="repeat a key"):
        db.replace_rows("daily_bars", rows, "instrument = ?", ["VIX"], con=con)
    # then the delete is rolled back with it, so the old row is still there
    assert con.execute("SELECT close FROM daily_bars").fetchall() == [(27.27,)]


def test_replace_rows_swaps_the_matching_rows_only() -> None:
    # given closes for two instruments
    con = _seeded_connection()
    day = date(2022, 9, 13)
    db.insert_models(
        "daily_bars",
        [DailyBar(instrument=s, day=day, close=1.0, source="s") for s in ("VIX", "DXY")],
        con=con,
    )
    # when VIX's rows are replaced by an empty rebuild
    db.replace_rows("daily_bars", [], "instrument = ?", ["VIX"], con=con)
    # then VIX is gone and DXY is untouched
    assert con.execute("SELECT instrument FROM daily_bars").fetchall() == [("DXY",)]
