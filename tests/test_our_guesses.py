"""Step 49, our guesses (docs/steps/our-guesses.md): checked, kept once, graded apart."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller.sources import DailyClosingPrice

FRIDAY = date(2026, 11, 20)


def _answer(*guesses: dict[str, object]) -> str:
    return "Here are my guesses:\n" + json.dumps(list(guesses))


def _g(market: str = "BRN", span: str = "week", **extra: object) -> dict[str, object]:
    return {
        "market": market,
        "span": span,
        "direction": "down",
        "reason": "OPEC+ pumps more.",
    } | extra


def test_a_guess_outside_the_rules_is_dropped() -> None:
    # given guesses on a market not listed and over a quarter; then with a percent and 31 words
    answer = _answer(
        _g("AAPL"),
        _g(span="quarter"),
    )
    more = _answer(
        _g(reason="Oil falls 5% on the news."),
        _g(reason=" ".join(["word"] * 31)),
    )

    # when they are checked
    kept, dropped = cli.keep_guesses(answer, [], FRIDAY)
    kept_more, dropped_more = cli.keep_guesses(more, [], FRIDAY)

    # then none is kept and each says why
    assert kept == [] and kept_more == []
    assert dropped == [
        "AAPL week: a market not listed",
        "BRN quarter: a span not a week or a month",
    ]
    assert dropped_more == ["BRN week: a percent sign", "BRN week: a reason over 30 words"]


def test_a_guess_starts_after_its_evening_and_cannot_be_rewritten() -> None:
    # given a good guess kept on Friday
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)

    # when the same evening asks again, with the opposite direction
    again, dropped = cli.keep_guesses(_answer(_g(direction="up")), kept, FRIDAY)

    # then the first row is unchanged, its span starts on Monday, and no second row is kept
    assert again == kept and len(kept) == 1
    assert (kept[0]["first"], kept[0]["last"]) == ("2026-11-23", "2026-11-27")
    assert kept[0]["model"] == cli.GUESS_MODEL
    assert dropped == ["BRN week: one of the same market and span still open"]


def test_a_malformed_answer_keeps_nothing() -> None:
    # given an answer with no JSON list
    rows = [{"market": "BRN"}]

    # when it is checked
    kept, dropped = cli.keep_guesses("I could not read the news today.", rows, FRIDAY)

    # then the rows are as they were
    assert kept == rows and dropped == ["the answer held no JSON list"]


def test_a_failed_run_does_not_stop_the_evening(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given the model failing
    def fail(today: date) -> str:
        raise OSError("claude is not installed")

    monkeypatch.setattr(cli, "ask_for_guesses", fail)
    monkeypatch.setattr(cli.settings, "scoreboard_dir", tmp_path / "scoreboard")

    # when the evening asks for guesses
    code = cli.main(["guess"])

    # then it ends well and keeps no file
    assert code == 0 and not (tmp_path / "predicts" / "our-guesses.csv").exists()


def test_guesses_are_graded_in_their_own_tally() -> None:
    # given a kept down guess on oil for the week of Nov 23, and closes falling to the 27th
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    start = date(2026, 11, 19)
    closes = [DailyClosingPrice(start + timedelta(days=i), 80.0 - i) for i in range(10)]

    # when graded with the closes to the 26th, and to the 27th
    early = cli.grade_forecasts(kept, lambda m: [c for c in closes if c.day <= date(2026, 11, 26)])
    done = cli.grade_forecasts(kept, lambda m: [c for c in closes if c.day <= date(2026, 11, 27)])

    # then it is open, then came true, and counts only in the guesses' tally
    assert early[0]["grade"] == "" and done[0]["grade"] == "came true"
    assert cli.forecast_tally(done) == {"came_true": 1, "did_not": 0, "open": 0}


def test_the_nasdaq_is_not_guessed_while_the_s_and_p_500_s_week_is_open_nor_a_third() -> None:
    # given the S&P 500's week kept, then an answer of the Nasdaq's week, gold's month and a third
    kept, _ = cli.keep_guesses(_answer(_g("SPY / ES")), [], FRIDAY)
    answer = _answer(_g("COMP"), _g("GC / XAU", "month"), _g("BTC"))

    # when it is checked
    more, dropped = cli.keep_guesses(answer, kept, FRIDAY)

    # then gold is kept, the Nasdaq dropped as the S&P 500's twin, and bitcoin never read
    assert [r["market"] for r in more] == ["SPY / ES", "GC / XAU"]
    assert dropped == ["COMP week: one of the same market and span still open"]


def test_a_guess_is_graded_from_the_close_before_its_first_day() -> None:
    # given a down guess for Nov 23 to 27: Friday 100, Monday 90, the 27th 95
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    prices = {20: 100.0, 23: 90.0, 24: 91.0, 25: 92.0, 26: 94.0, 27: 95.0}
    closes = [DailyClosingPrice(date(2026, 11, d), p) for d, p in prices.items()]

    # when graded
    done = cli.grade_forecasts(kept, lambda m: closes)

    # then from Friday's 100 to 95 it came true (from Monday's 90 it would not have)
    assert done[0]["grade"] == "came true"
