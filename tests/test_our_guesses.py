"""Steps 49 and 50, our guesses and the guess ledger (docs/steps/our-guesses.md,
docs/steps/guess-ledger.md): checked, kept once, graded, reviewed, and learned from monthly."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller.sources import DailyClosingPrice

FRIDAY = date(2026, 11, 20)
REASONING = (
    "OPEC+ members keep pumping above quota while demand slows into winter, so prices should drift"
    " lower; a surprise cut at the next meeting would prove this wrong."
)


def _answer(*guesses: dict[str, object]) -> str:
    return "Here are my guesses [from the news]:\n" + json.dumps(list(guesses))


def _g(market: str = "BRN", end: str = "2026-11-27", **extra: object) -> dict[str, object]:
    return {
        "market": market,
        "direction": "down",
        "end": end,
        "statement": "Brent oil will be lower on Nov 27 than on Nov 20.",
        "reasoning": REASONING,
        "tag": "oil supply",
        "confidence": "medium",
        "source": "https://example.com/opec",
    } | extra


@pytest.mark.parametrize(
    ("guess", "why"),
    [
        (_g("AAPL"), "a market not listed"),
        (_g(direction="flat"), "a direction not up or down"),
        (_g(end="2026-11-28"), "an end date not a weekday from the second after tonight to a year"),
        (_g(end="2026-11-23"), "an end date not a weekday from the second after tonight to a year"),
        (_g(end="2027-12-31"), "an end date not a weekday from the second after tonight to a year"),
        (_g(end="soon"), "no end date"),
        (_g(statement=" ".join(["word"] * 41)), "a statement missing or over 40 words"),
        (_g(reasoning="Oil falls."), "reasoning not 15 to 150 words"),
        (_g(reasoning=REASONING + " By 5% at least."), "a percent sign"),
        (_g(tag="vibes"), "a tag not listed"),
        (_g(confidence="certain"), "a confidence not low, medium or high"),
        (_g(source="http://example.com"), "no https link to its news"),
    ],
)
def test_each_check_refuses_its_case(guess: dict[str, object], why: str) -> None:
    # given one guess that breaks one rule
    # when it is checked
    kept, dropped = cli.keep_guesses(_answer(guess), [], FRIDAY)

    # then it is not kept, and the reason is given
    assert kept == [] and dropped == [f"{guess['market']} to {guess['end']}: {why}"]


def test_a_repeat_is_refused_and_a_guess_a_week_apart_is_kept() -> None:
    # given the S&P 500 guessed to Fri Nov 27
    kept, _ = cli.keep_guesses(_answer(_g("SPY / ES")), [], FRIDAY)

    # when the Nasdaq to Wed Dec 2, the S&P 500 to Fri Dec 4 and gold to Nov 27 are offered
    answer = _answer(_g("COMP", "2026-12-02"), _g("SPY / ES", "2026-12-04"), _g("GC / XAU"))
    more, dropped = cli.keep_guesses(answer, kept, FRIDAY)

    # then the Nasdaq is a repeat of its twin, the S&P 500 a week later and gold are kept
    assert [(r["market"], r["last"]) for r in more] == [
        ("SPY / ES", "2026-11-27"),
        ("SPY / ES", "2026-12-04"),
        ("GC / XAU", "2026-11-27"),
    ]
    assert dropped == ["COMP to 2026-12-02: repeats an open guess on SPY / ES ending 2026-11-27"]


def test_a_kept_guess_starts_after_its_evening_with_its_horizon_and_lessons() -> None:
    # given a good guess on Friday under lessons version 3
    kept, _ = cli.keep_guesses(_answer(_g(end="2026-12-21")), [], FRIDAY, "3")

    # then it starts Monday, is a month, and keeps its model and lessons version
    row = kept[0]
    assert (row["first"], row["last"], row["horizon"]) == ("2026-11-23", "2026-12-21", "month")
    assert (row["model"], row["lessons"], row["grade"]) == (cli.GUESS_MODEL, "3", "")


def test_no_more_than_fifty_are_read() -> None:
    # given 51 guesses, each on its own end date a week apart
    start = date(2026, 11, 27)
    guesses = [_g(end=(start + timedelta(weeks=i)).isoformat()) for i in range(51)]

    # when checked
    kept, _ = cli.keep_guesses(_answer(*guesses), [], FRIDAY)

    # then 50 are kept, the 51st not read
    assert len(kept) == 50


def test_a_malformed_answer_keeps_nothing() -> None:
    # given an answer with no JSON list
    rows = [{"market": "BRN"}]

    # when it is checked
    kept, dropped = cli.keep_guesses("I could not read the news today.", rows, FRIDAY)

    # then the rows are as they were
    assert kept == rows and dropped == ["the answer held no JSON list"]


def test_a_failed_run_keeps_the_rows_and_does_not_stop_the_evening(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given one kept guess, and the model failing
    folder = tmp_path / "predicts"
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    cli._write_rows(folder / "our-guesses.csv", cli.GUESS_FIELDS, kept)

    def fail(prompt: str, web: bool) -> str:
        raise OSError("claude is not installed")

    monkeypatch.setattr(cli, "_run_model", fail)
    monkeypatch.setattr(cli.settings, "scoreboard_dir", tmp_path / "scoreboard")

    # when the evening asks for guesses
    code = cli.main(["guess"])

    # then it ends well and the row is as it was
    assert code == 0
    assert cli._read_rows(folder / "our-guesses.csv") == kept


def test_a_guess_is_graded_from_the_close_before_its_first_day() -> None:
    # given a down guess for Nov 23 to 27: Friday 100, Monday 90, the 27th 95
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    prices = {20: 100.0, 23: 90.0, 24: 91.0, 25: 92.0, 26: 94.0, 27: 95.0}
    closes = [DailyClosingPrice(date(2026, 11, d), p) for d, p in prices.items()]

    # when graded, with the closes to the 26th and to the 27th
    early = cli.grade_guesses(kept, lambda m: closes[:-1])
    done = cli.grade_guesses(kept, lambda m: closes)

    # then it is open, then came true from Friday's 100 (from Monday's 90 it would not have)
    assert early[0]["grade"] == ""
    assert (done[0]["grade"], done[0]["move"]) == ("came true", "100 to 95")


def test_a_review_is_kept_on_a_graded_row_and_never_changes_its_grade() -> None:
    # given a graded row and an open one, and a model that calls both right
    kept, _ = cli.keep_guesses(_answer(_g(), _g("GC / XAU")), [], FRIDAY)
    kept[0] = kept[0] | {"grade": "did not", "move": "100 to 105"}
    answer = json.dumps([{"id": 0, "review": "It came true."}, {"id": 1, "review": "Also true."}])

    # when reviewed
    reviewed = cli.review_guesses(kept, lambda prompt: answer)

    # then only the graded row has its review, and its grade is unchanged
    assert (reviewed[0]["review"], reviewed[0]["grade"]) == ("It came true.", "did not")
    assert reviewed[1]["review"] == ""


def test_lessons_are_written_once_a_month_from_the_reviews_since_the_last() -> None:
    # given reviewed rows, and lessons at version 2 of October
    row = cli.keep_guesses(_answer(_g()), [], FRIDAY)[0][0]
    rows = [row | {"grade": "did not", "review": "The cut came early.", "last": "2026-11-27"}]
    text = "# Lessons\n\nWhat the guesser reads.\n\n## Version 2, 2026-10-01\n\n- Old lesson.\n"
    seen: list[str] = []

    def ask(prompt: str) -> str:
        seen.append(prompt)
        return "- Watch for early cuts."

    # when the first run of December asks, and then a second run that month
    december = cli.update_lessons(text, rows, date(2026, 12, 1), ask)
    again = cli.update_lessons(december, rows, date(2026, 12, 2), ask)

    # then version 3 is written, newest first, from the review, and not again that month
    assert cli.lessons_version(december) == (3, "2026-12-01")
    assert december.index("Version 3") < december.index("Version 2")
    assert "The cut came early." in seen[0] and len(seen) == 1
    assert again == december


def test_the_first_lessons_are_version_one() -> None:
    # given no lessons and one reviewed row
    row = cli.keep_guesses(_answer(_g()), [], FRIDAY)[0][0]
    rows = [row | {"grade": "came true", "review": "Right for its reasons."}]

    # when the month's first run asks
    text = cli.update_lessons("", rows, date(2026, 12, 1), lambda prompt: "- Keep it up.")

    # then it is version 1
    assert cli.lessons_version(text) == (1, "2026-12-01")


def _graded(stated: str, tag: str, right: int, wrong: int, open_: int = 0) -> list[dict[str, str]]:
    rows = []
    for grade, n in (("came true", right), ("did not", wrong), ("", open_)):
        rows += [{"stated": stated, "tag": tag, "grade": grade} for _ in range(n)]
    return rows


def test_an_evening_counts_once_right_only_if_more_than_half_came_true() -> None:
    # given three evenings of one tag: 11 and 9, 10 and 10, and 12 right with one still open
    rows = (
        _graded("2026-11-20", "jobs", 11, 9)
        + _graded("2026-11-23", "jobs", 10, 10)
        + _graded("2026-11-24", "jobs", 12, 0, 1)
    )

    # when its record is counted
    record = cli.guess_record(rows, "tag")

    # then two evenings are tries, the first right and the tie not; the open evening waits
    assert record == [
        {
            "tag": "jobs",
            "guesses": 40,
            "came_true": 21,
            "evenings": 2,
            "evenings_right": 1,
            "p": 0.75,
            "verdict": "too few",
        }
    ]


def test_the_front_page_prefers_a_promoted_tag_then_high_confidence_then_soonest() -> None:
    # given four open guesses
    rows = [
        {"tag": "momentum", "confidence": "high", "last": "2026-11-27", "grade": ""},
        {"tag": "jobs", "confidence": "low", "last": "2026-12-21", "grade": ""},
        {"tag": "other", "confidence": "high", "last": "2026-12-04", "grade": ""},
        {"tag": "other", "confidence": "medium", "last": "2026-11-25", "grade": ""},
    ]

    # when three places are filled with jobs promoted
    shown = cli.front_guesses(rows, {"jobs"}, FRIDAY, 3)

    # then jobs first, then the two high ones, soonest first
    assert [(r["tag"], r["last"]) for r in shown] == [
        ("jobs", "2026-12-21"),
        ("momentum", "2026-11-27"),
        ("other", "2026-12-04"),
    ]
