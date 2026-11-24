"""Steps 49 and 50, our guesses and the guess ledger (docs/steps/our-guesses.md,
docs/steps/guess-ledger.md): checked, kept once, graded, reviewed, and learned from monthly."""

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import study
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
        (_g("COIN"), "a single company"),
        (_g("ALL"), "a single company"),
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


def test_a_guess_is_graded_from_the_first_close_after_it_was_made() -> None:
    # given a down Brent guess made Friday 18:00 New York for Nov 23 to 27: Friday 100 (settled
    # at 14:30, before it), Monday 90, the 27th 95
    made = datetime(2026, 11, 20, 23, 0, tzinfo=UTC)
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY, made=made)
    prices = {20: 100.0, 23: 90.0, 24: 91.0, 25: 92.0, 26: 94.0, 27: 95.0}
    closes = [DailyClosingPrice(date(2026, 11, d), p) for d, p in prices.items()]

    # when graded, with the closes to the 26th and to the 27th
    early = cli.grade_guesses(kept, lambda m: closes[:-1])
    done = cli.grade_guesses(kept, lambda m: closes)

    # then it is open, then did not come true from Monday's 90 (from Friday's 100, seen before it
    # was made, it would have)
    assert kept[0]["made"] == "2026-11-20T23:00:00+00:00"
    assert early[0]["grade"] == ""
    assert (done[0]["grade"], done[0]["move"]) == ("did not", "90 to 95")


@pytest.mark.parametrize(
    ("market", "made", "start"),
    [
        # Monday 18:00 New York is Tuesday 08:00 in Tokyo, before its 15:30 close
        ("NKY", datetime(2026, 11, 23, 23, 0, tzinfo=UTC), date(2026, 11, 24)),
        # Monday 18:00 New York is 23:00 London, before Tuesday's 00:00 bar
        ("EURUSD", datetime(2026, 11, 23, 23, 0, tzinfo=UTC), date(2026, 11, 24)),
        # Monday 19:30 New York is Tuesday 00:30 London, after Tuesday's bar
        ("EURUSD", datetime(2026, 11, 24, 0, 30, tzinfo=UTC), date(2026, 11, 25)),
        # Monday 19:30 New York after the US change of clocks is 23:30 London, still on GMT
        ("EURUSD", datetime(2027, 3, 15, 23, 30, tzinfo=UTC), date(2027, 3, 16)),
        # a guess made at the very instant of Tokyo's close has seen it
        ("NKY", datetime(2026, 11, 24, 6, 30, tzinfo=UTC), date(2026, 11, 25)),
        # Sunday 15:00 New York, before bitcoin's 23:59 UTC close, which is not stored: Monday's
        ("BTC", datetime(2026, 11, 22, 20, 0, tzinfo=UTC), date(2026, 11, 23)),
        # Sunday 02:20 New York, the S&P 500's next close is Monday's
        ("SPY / ES", datetime(2026, 11, 22, 7, 20, tzinfo=UTC), date(2026, 11, 23)),
        # Friday 18:00 New York, after the close: Monday's
        ("SPY / ES", datetime(2026, 11, 20, 23, 0, tzinfo=UTC), date(2026, 11, 23)),
    ],
)
def test_a_guess_starts_from_its_market_s_first_close_after_it_was_made(
    market: str, made: datetime, start: date
) -> None:
    # given a guess made at ``made``
    row = {"stated": "2026-11-23", "market": market, "made": made.isoformat()}

    # when its start is read
    # then it is the first day whose close in that market comes after it
    assert cli.guess_start(row) == start


def test_a_weekend_bitcoin_guess_is_graded_from_monday_s_close() -> None:
    # given an up bitcoin guess made Sunday, and bitcoin's closes stored on weekdays only
    made = datetime(2026, 11, 22, 20, 0, tzinfo=UTC)
    kept, _ = cli.keep_guesses(
        _answer(_g("BTC", direction="up")), [], date(2026, 11, 22), made=made
    )
    prices = {20: 100.0, 23: 80.0, 24: 81.0, 25: 82.0, 26: 83.0, 27: 90.0}
    closes = [DailyClosingPrice(date(2026, 11, d), p) for d, p in prices.items()]

    # when graded
    done = cli.grade_guesses(kept, lambda m: closes)

    # then from Monday's 80, not Friday's 100, which the weekend's fall had already left behind
    assert (done[0]["grade"], done[0]["move"]) == ("came true", "80 to 90")


def test_a_row_made_unknown_counts_as_made_late_on_its_stated_day() -> None:
    # given a Nikkei row with no time it was made, stated Monday
    row = {"stated": "2026-11-23", "market": "NKY", "made": ""}

    # when its start is read
    # then it is as if made at 23:59 New York, Tuesday 13:59 in Tokyo: Tuesday's close
    assert cli.guess_start(row) == date(2026, 11, 24)


def test_a_base_rate_counts_the_weekdays_from_the_guess_s_start() -> None:
    # given an S&P 500 guess made Monday 18:00 New York ending Friday, and rising closes before
    made = datetime(2026, 11, 23, 23, 0, tzinfo=UTC).isoformat()
    row = {"stated": "2026-11-23", "market": "SPY / ES", "direction": "up", "last": "2026-11-27"}
    closes = [
        DailyClosingPrice(date(2026, 1, 1) + timedelta(days=i), 100.0 + i) for i in range(200)
    ]

    # when its base rate is filled
    [filled] = cli.with_base_rates([row | {"made": made}], lambda m: closes)

    # then it is over spans of 3 weekdays, Tuesday's close to Friday's
    expected = study.base_rate(closes, date(2026, 11, 23), 3, "up")
    assert filled["base_rate"] == f"{expected:.4f}"


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
        {
            "market": "BTC",
            "tag": "momentum",
            "confidence": "high",
            "last": "2026-11-27",
            "grade": "",
        },
        {"market": "DXY", "tag": "jobs", "confidence": "low", "last": "2026-12-21", "grade": ""},
        {"market": "BRN", "tag": "other", "confidence": "high", "last": "2026-12-04", "grade": ""},
        {
            "market": "GC / XAU",
            "tag": "other",
            "confidence": "medium",
            "last": "2026-11-25",
            "grade": "",
        },
    ]

    # when three places are filled with jobs promoted
    shown = cli.front_guesses(rows, {"jobs"}, FRIDAY, 3)

    # then jobs first, then the two high ones, soonest first
    assert [(r["tag"], r["last"]) for r in shown] == [
        ("jobs", "2026-12-21"),
        ("momentum", "2026-11-27"),
        ("other", "2026-12-04"),
    ]


def test_the_proposal_takes_the_ledgers_words_and_keeps_the_approved_ones() -> None:
    # given two picked guesses, the first already approved with the owner's words
    kept, _ = cli.keep_guesses(_answer(_g(), _g("GC / XAU")), [], FRIDAY)
    approved = cli.front_rows(kept[:1], [])
    approved[0] |= {"statement": "Oil will be cheaper on Nov 27.", "why": "Owner's words."}

    # when the evening proposes them
    rows = cli.front_rows(kept, approved)

    # then the first keeps the owner's words and the second has the ledger's, in order
    assert [(r["market"], r["statement"], r["why"]) for r in rows] == [
        ("BRN", "Oil will be cheaper on Nov 27.", "Owner's words."),
        ("GC / XAU", "Brent oil will be lower on Nov 27 than on Nov 20.", REASONING),
    ]
    assert list(rows[0]) == list(cli.FRONT_FIELDS)


@pytest.mark.parametrize("field", ["stated", "market", "direction", "last", "source"])
def test_a_front_row_with_a_locked_field_changed_matches_no_guess(field: str) -> None:
    # given an approved row, and the same row with one locked field changed
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    row = cli.front_rows(kept, [])[0]
    changed = row | {field: "changed", "statement": "Reworded."}

    # when checked against the ledger
    bad = cli.unlocked([row | {"why": "Reworded."}, changed], kept)

    # then only the changed one is refused
    assert bad == [changed]


def test_the_repositorys_front_page_rewords_only_what_it_may() -> None:
    # given the repository's approved front page and its ledger
    folder = Path(__file__).parent.parent / "docs" / "predicts"
    ledger = [cli._ledger_row(r) for r in cli._read_rows(folder / "our-guesses.csv")]

    # when checked
    bad = cli.unlocked(cli._read_rows(folder / "front.csv"), ledger)

    # then every row is a guess of the ledger, with its market, direction, dates and link as made
    assert bad == []


def test_the_front_page_takes_one_guess_per_area_and_none_where_a_tested_one_is() -> None:
    # given open guesses on two stock markets, two currencies and oil, all high
    rows = [
        {"market": m, "tag": "other", "confidence": "high", "last": last, "grade": ""}
        for m, last in (
            ("VIX", "2026-11-25"),
            ("USDJPY", "2026-11-26"),
            ("DXY", "2026-11-27"),
            ("NKY", "2026-11-30"),
            ("BRN", "2026-12-01"),
        )
    ]

    # when four places are filled beside a tested forecast on stocks
    shown = cli.front_guesses(rows, set(), FRIDAY, 4, {"stocks"})

    # then one currency and oil, soonest first, and no stock market
    assert [r["market"] for r in shown] == ["USDJPY", "BRN"]


def test_every_market_the_guesser_may_name_has_an_area() -> None:
    # given the markets of the guesses and of the tested forecasts
    markets = set(cli.study.MVP_PRICE_SERIES) | {cli.HOME}

    # then each has one of the eight areas
    assert markets <= set(cli.AREAS) and len(set(cli.AREAS.values())) == 8


@pytest.mark.parametrize("markets", [("USDCNY", "SHCOMP"), ("USDCHF", "SMI")])
def test_a_country_s_currency_is_a_currency_and_its_index_a_stock_market(
    markets: tuple[str, str],
) -> None:
    # given a country's two markets: China's and Switzerland's (docs/steps/china.md, switzerland.md)

    # when their areas are read
    areas = [cli.AREAS[m] for m in markets]

    # then the currency is with the currencies and the index with the stocks
    assert areas == ["currencies", "stocks"]


def _closes(*prices: float) -> list[DailyClosingPrice]:
    start = date(2026, 1, 1)
    return [DailyClosingPrice(start + timedelta(days=i), p) for i, p in enumerate(prices)]


def test_the_base_rate_is_the_share_of_runs_that_went_its_way() -> None:
    # given five closes: runs of 1 close go up, up, down, up
    closes = _closes(10, 11, 12, 11, 13)

    # when the base rate is asked over runs of 1 close, before a day after them all
    up = study.base_rate(closes, date(2027, 1, 1), 1, "up")
    down = study.base_rate(closes, date(2027, 1, 1), 1, "down")

    # then 3 of 4 runs went up and 1 of 4 down
    assert (up, down) == (0.75, 0.25)


def test_an_unchanged_run_counts_against_both_directions() -> None:
    # given runs of 2 closes: 10 to 12 up, 11 to 11 unchanged
    closes = _closes(10, 11, 12, 11)

    # when the base rate is asked both ways
    up = study.base_rate(closes, date(2027, 1, 1), 2, "up")
    down = study.base_rate(closes, date(2027, 1, 1), 2, "down")

    # then the unchanged run counts as neither
    assert (up, down) == (0.5, 0.0)


def test_closes_on_or_after_the_evening_are_not_used() -> None:
    # given four closes, then a fall on and after the evening of Jan 4
    closes = _closes(10, 11, 12, 13, 5, 1)

    # when the base rate is asked for a guess made on Jan 5's evening
    rate = study.base_rate(closes, date(2026, 1, 5), 1, "up")

    # then only the runs among Jan 1 to 4 count
    assert rate == 1.0
    assert study.base_rate(closes[:1], date(2026, 1, 5), 1, "up") is None


def test_a_kept_guess_and_a_stored_one_get_their_base_rate() -> None:
    # given a down guess made Friday evening, graded from Monday Nov 23's close to Friday Nov 27's,
    # and a stored row without a base rate
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    stored = {**kept[0], "market": "GC / XAU", "base_rate": ""}
    del stored["base_rate"]
    prices = [100.0 + (i % 7) for i in range(40)]
    closes = [
        DailyClosingPrice(date(2026, 9, 1) + timedelta(days=i), p) for i, p in enumerate(prices)
    ]

    # when the base rates are filled
    rows = cli.with_base_rates([kept[0], stored], lambda m: closes)

    # then each is the share of 4-close runs before Friday that fell, and a set one is kept
    expected = study.base_rate(closes, FRIDAY, 4, "down")
    assert expected is not None
    assert [r["base_rate"] for r in rows] == [f"{expected:.4f}"] * 2
    assert (
        cli.with_base_rates([{**rows[0], "base_rate": "0.1"}], lambda m: [])[0]["base_rate"]
        == "0.1"
    )


RULE = "The reasoning names the guess's base rate"


def test_the_grounded_prompt_holds_the_record_and_the_news_prompt_does_not() -> None:
    # given an open news guess, the base rates and an open tested forecast
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    rates = "SPY / ES: week 56 in 100, year 74 in 100"
    forecasts = cli.open_forecasts(
        [
            {"kind": "long run", "market": "SPY / ES", "span": "month", "direction": "up"}
            | {"last": "2026-12-21", "event": "", "grade": ""},
            {"kind": "long run", "market": "COMP", "span": "week", "direction": "up"}
            | {"last": "2026-11-20", "event": "", "grade": "came true"},
        ]
    )

    # when both prompts are built
    news = cli.news_prompt(FRIDAY, kept, "be careful")
    grounded = cli.grounded_prompt(FRIDAY, kept, "be careful", rates, forecasts)

    # then the grounded one holds the table, the open forecast only and the rule; the news one
    # none of them and is the guess prompt as built before step 55
    assert rates in grounded and RULE in grounded
    assert "SPY / ES up over a month to 2026-12-21 (long run)" in grounded
    assert "COMP" not in forecasts
    assert rates not in news and RULE not in news and "Tested forecasts" not in news
    before = cli._prompt(
        "guess_prompt.txt",
        today=FRIDAY.isoformat(),
        markets=cli.market_list(),
        tags=", ".join(cli.GUESS_TAGS),
        most=str(cli.GUESS_MAX),
        open=f"BRN week down to 2026-11-27: {kept[0]['statement']}",
        lessons="be careful",
    )
    assert news == before


def test_each_guesser_sees_and_repeats_only_its_own_open_guesses() -> None:
    # given an open news guess on Brent to Nov 27
    news, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)

    # when the grounded guesser guesses the same, then guesses it again
    grounded, _ = cli.keep_guesses(_answer(_g()), news, FRIDAY, "0", "grounded", "grounded-1")
    again, dropped = cli.keep_guesses(
        _answer(_g()), grounded, FRIDAY, "0", "grounded", "grounded-1"
    )

    # then the first is kept with its guesser and version, the second refused
    assert [(r["guesser"], r["prompt"]) for r in grounded] == [
        ("news", "news-1"),
        ("grounded", "grounded-1"),
    ]
    assert len(again) == 2 and "repeats an open guess" in dropped[0]
    assert (
        "BRN"
        not in cli.grounded_prompt(FRIDAY, news, "", "", "")
        .split("Guesses still open:")[1]
        .split("Lessons")[0]
    )


def test_the_evening_asks_both_and_a_failed_grounded_call_keeps_the_news_guesses(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # given a model that answers the news prompt and fails the grounded one
    asked: list[str] = []

    def model(prompt: str, web: bool) -> str:
        asked.append("grounded" if RULE in prompt else "news")
        if RULE in prompt:
            raise OSError("the grounded session timed out")
        return _answer(_g(end="2026-11-30"))

    monkeypatch.setattr(cli, "_run_model", model)
    monkeypatch.setattr(cli, "_now", lambda: datetime(2026, 11, 20, 22, tzinfo=UTC))
    monkeypatch.setattr(cli.settings, "scoreboard_dir", tmp_path / "scoreboard")

    # when the evening runs
    code = cli.main(["guess"])

    # then both were asked, and the news guess is kept as the news guesser's
    rows = cli._read_rows(tmp_path / "predicts" / "our-guesses.csv")
    assert code == 0 and asked == ["news", "grounded"]
    assert [(r["market"], r["guesser"], r["prompt"]) for r in rows] == [("BRN", "news", "news-1")]


def test_a_stored_row_without_a_guesser_is_the_news_guessers() -> None:
    # given a ledger row from before step 55
    kept, _ = cli.keep_guesses(_answer(_g()), [], FRIDAY)
    old = {k: v for k, v in kept[0].items() if k not in ("guesser", "prompt")}

    # when it is read
    row = cli._ledger_row(old)

    # then it is the news guesser's first prompt
    assert (row["guesser"], row["prompt"]) == ("news", "news-1")
    assert cli.grounded_version() == "grounded-1"


def _row(market: str = "BRN", last: str = "2026-11-27", **extra: str) -> dict[str, str]:
    row = {
        "stated": "2026-11-20",
        "market": market,
        "horizon": "week",
        "direction": "up",
        "last": last,
        "tag": "momentum",
        "confidence": "low",
        "grade": "came true",
        "base_rate": "0.5",
        "guesser": "news",
        "prompt": "news-1",
    }
    return row | extra


def test_a_bet_is_counted_once_per_guesser_market_and_week() -> None:
    # given two Brent guesses ending in one week, the S&P 500 and the Nasdaq in one week, the
    # same Brent guess by the grounded guesser, and an open guess
    rows = [
        _row(),
        _row(last="2026-11-26", grade="did not"),
        _row("SPY / ES"),
        _row("COMP"),
        _row(guesser="grounded", prompt="grounded-1"),
        _row("GC / XAU", grade=""),
    ]

    # when the guesses are counted
    counted = cli.counted_guesses(rows)

    # then the first Brent, the S&P 500 and the grounded Brent count
    assert [(r["market"], r["guesser"], r["last"]) for r in counted] == [
        ("BRN", "news", "2026-11-27"),
        ("SPY / ES", "news", "2026-11-27"),
        ("BRN", "grounded", "2026-11-27"),
    ]


def _weeks(count: int, right: int, rate: str = "0.5") -> list[dict[str, str]]:
    first = date(2026, 1, 2)
    return [
        _row(
            last=(first + timedelta(weeks=i)).isoformat(),
            grade="came true" if i < right else "did not",
            base_rate=rate,
        )
        for i in range(count)
    ]


def test_a_guesser_beats_its_base_rate_only_with_enough_guesses_and_a_small_chance() -> None:
    # given 60 guesses at a base rate of one half: 60 right, 59 of 59 right, and 32 of 60 right
    # when each is judged
    many = cli.excess_record(_weeks(60, 60), "news")
    few = cli.excess_record(_weeks(59, 59), "news")
    near = cli.excess_record(_weeks(60, 32), "news")

    # then only the first beats it; the second has too few; the third is within chance
    assert many["verdict"] == "beats its base rate" and many["excess"] == 30
    assert few["verdict"] == "too few"
    assert near["verdict"] == "does not beat its base rate" and near["excess"] == 2


def test_a_version_is_judged_on_its_evenings_against_the_news_guesser() -> None:
    # given evenings where the grounded guesser beat, lost, tied, and one with a week guess open
    def evening(
        day: str, news: str, grounded: str, open_week: bool = False
    ) -> list[dict[str, str]]:
        rows = [
            _row(stated=day, grade=news),
            _row(stated=day, grade=grounded, guesser="grounded", prompt="grounded-2"),
        ]
        if open_week:
            rows.append(_row("GC / XAU", stated=day, grade=""))
        return rows

    rows = (
        evening("2026-12-01", "did not", "came true")
        + evening("2026-12-02", "came true", "did not")
        + evening("2026-12-03", "came true", "came true")
        + evening("2026-12-04", "did not", "came true", open_week=True)
        + [_row(stated="2026-12-05", guesser="grounded", prompt="grounded-1", grade="came true")]
    )

    # when version 2's evenings are tallied
    tally = cli.evenings_against(rows, version="grounded-2")

    # then one higher and one lower count; the tie, the open evening and version 1's are left out
    assert tally == {"higher": 1, "lower": 1}
    assert cli.version_verdict(tally) == "too few"
    assert cli.version_verdict({"higher": 8, "lower": 7}) == "keep"
    assert cli.version_verdict({"higher": 7, "lower": 8}) == "revert"
    assert cli.against_verdict({"higher": 21, "lower": 9})[0] == "grounded beats news"
    assert cli.against_verdict({"higher": 19, "lower": 10})[0] == "too few"


def test_the_grounded_lessons_are_given_each_tag_against_its_base_rates() -> None:
    # given two graded grounded guesses of one tag, each with a review
    rows = [
        _row(guesser="grounded", review="It held."),
        _row("GC / XAU", guesser="grounded", grade="did not", base_rate="0.6", review="Luck."),
    ]
    asked: list[str] = []

    # when the lessons are written with the tag record
    record = cli.tag_against_base(rows)
    cli.update_lessons("", rows, date(2026, 12, 1), lambda p: asked.append(p) or "Learn.", record)

    # then the record reads 1 of 2 against 1.1 expected, and the model was given it
    assert record == "- momentum: 1 of 2 came true, 1.1 expected from base rates"
    assert record in asked[0]


def test_a_hand_made_guess_is_in_no_guesser_s_record_but_still_shown() -> None:
    # given a graded news guess, and a graded hand-made one on another market
    rows = [_row(), _row("WEAT", prompt="by-hand")]

    # when counted, judged, read as the news guesser's own, and picked for the front page
    counted = cli.counted_guesses(rows)
    record = cli.excess_record(rows, "news")
    mine = cli._mine(rows, "news")
    open_rows = [r | {"grade": ""} for r in rows]
    picks = cli.front_guesses(open_rows, set(), date(2026, 11, 20), 5)

    # then only the news guess counts, yet both may reach the front page
    assert [r["market"] for r in counted] == ["BRN"]
    assert record["counted"] == 1
    assert [r["market"] for r in mine] == ["BRN"]
    assert sorted(r["market"] for r in picks) == ["BRN", "WEAT"]


def test_the_guesser_is_not_offered_a_single_company() -> None:
    # given the markets the guesser is shown
    listed = [line.split(":")[0] for line in cli.market_list().splitlines()]

    # then neither Coinbase nor Allstate is among them, and the other 35 are
    assert "COIN" not in listed and "ALL" not in listed
    assert len(listed) == len(study.MVP_PRICE_SERIES) - 2 == 35


TODAY = date(2026, 11, 25)


def _front(r: dict[str, str], **extra: str) -> dict[str, str]:
    return {f: r.get(f, "") for f in cli.FRONT_LOCKED} | {"statement": "Owner's words."} | extra


def test_a_shown_guess_stays_with_the_owner_s_words_though_not_picked_again() -> None:
    # given an open Brent guess shown on the front page in the owner's words, and a newer guess
    shown = _row(grade="", shown="2026-11-22")
    newer = _row("DXY", grade="", confidence="high")
    approved = [_front(shown)]

    # when tonight's proposal is made
    proposal = cli.front_proposal([], approved, [newer, shown], [shown, newer], set(), TODAY)

    # then Brent stays first, as the owner left it, and the newer guess fills the room
    assert [(r["market"], r["statement"]) for r in proposal] == [
        ("BRN", "Owner's words."),
        ("DXY", ""),
    ]


def test_a_shown_guess_the_owner_deleted_comes_back_withdrawn() -> None:
    # given an open guess shown earlier and no longer in front.csv
    shown = _row(grade="", shown="2026-11-22", statement="Ledger words.")

    # when tonight's proposal is made
    [row] = cli.front_proposal([], [], [], [shown], set(), TODAY)

    # then it is back, with the ledger's words, withdrawn tonight
    assert (row["market"], row["statement"], row["withdrawn"]) == (
        "BRN",
        "Ledger words.",
        "2026-11-25",
    )


def test_with_five_cards_staying_no_new_guess_is_picked() -> None:
    # given five shown open guesses in five areas, and a new one
    markets = ["BRN", "DXY", "SPY / ES", "GC / XAU", "BTC"]
    shown = [_row(m, grade="", shown="2026-11-22") for m in markets]
    new = _row("WEAT", grade="", confidence="high")

    # when tonight's proposal is made
    proposal = cli.front_proposal(
        [], [_front(r) for r in shown], [new], [*shown, new], set(), TODAY
    )

    # then the five stay and the new one waits
    assert [r["market"] for r in proposal] == markets


def test_a_graded_guess_leaves_the_front_page() -> None:
    # given a shown guess now graded
    done = _row(shown="2026-11-22")

    # when tonight's proposal is made
    # then it is gone
    assert cli.front_proposal([], [_front(done)], [], [done], set(), TODAY) == []


def test_the_front_tally_counts_every_guess_once_shown_withdrawn_ones_too() -> None:
    # given a ledger: one on the published front page tonight, one shown before, one never
    ledger = [
        _row(grade=""),
        _row("DXY", grade="did not", shown="2026-11-22"),
        _row("BTC", grade=""),
    ]

    # when the rows shown are marked
    marked = cli.mark_shown(ledger, [_front(ledger[0], withdrawn="2026-11-25")], TODAY)

    # then the first is marked tonight, the second keeps its date, the third is not shown
    assert [r["shown"] for r in marked] == ["2026-11-25", "2026-11-22", ""]
    assert cli.forecast_tally([r for r in marked if r["shown"]]) == {
        "came_true": 0,
        "did_not": 1,
        "open": 1,
    }
