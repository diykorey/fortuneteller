"""Step 62, big moves explained (docs/steps/big-moves-explained.md): each weekday's big moves in
our markets, checked against our open rows and explained from the news, and the news scanned for
big moves in markets we do not track."""

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import study
from fortuneteller.sources import DailyClosingPrice

FRIDAY = date(2026, 11, 27)
TEN_YEAR = "UST10Y / ZN"


def _weekdays(last: date, count: int) -> list[date]:
    days: list[date] = []
    day = last
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day -= timedelta(days=1)
    return sorted(days)


def _yields(last_move_bp: float, count: int = 506) -> list[DailyClosingPrice]:
    """Closes in percent, one basis point up and down by turns, then ``last_move_bp`` on Friday:
    the 504 moves before Friday's have a deviation of exactly 1 bp."""
    days = _weekdays(FRIDAY, count)
    prices = [2.0 + 0.01 * (i % 2) for i in range(count - 1)]
    prices.append(prices[-1] + last_move_bp / 100)
    return [DailyClosingPrice(d, p) for d, p in zip(days, prices, strict=True)]


@pytest.mark.parametrize(("move_bp", "big"), [(3.0, True), (-3.0, True), (2.99, False)])
def test_a_move_of_three_deviations_is_big_and_one_just_under_is_not(
    move_bp: float, big: bool
) -> None:
    # given a 10-year yield that moved one basis point a day, then move_bp on Friday
    closes = _yields(move_bp)

    # when the week's big moves are found
    found = cli.big_moves(TEN_YEAR, closes, "bps", [FRIDAY])

    # then three deviations either way is big, and 2.99 is not
    assert [(m.day, round(m.deviations, 6)) for m in found] == ([(FRIDAY, 3.0)] if big else [])


def test_a_market_without_504_moves_before_the_day_is_left_out() -> None:
    # given one close too few for 504 moves before Friday's
    closes = _yields(10.0, count=505)

    # when the week's big moves are found
    found = cli.big_moves(TEN_YEAR, closes, "bps", [FRIDAY])

    # then none is
    assert found == []


def _guess(direction: str, last: str) -> dict[str, str]:
    # made Friday 2026-11-20 at 18:00 New York: its first close is Monday the 23rd
    return {
        "stated": "2026-11-20",
        "made": "2026-11-20T23:00:00+00:00",
        "market": TEN_YEAR,
        "direction": direction,
        "last": last,
    }


UP_FRIDAY = cli.BigMove(FRIDAY, TEN_YEAR, 9.0, 4.5)


@pytest.mark.parametrize(
    ("guesses", "expected"),
    [
        ([_guess("up", "2026-11-27")], ("yes", "yes")),
        ([_guess("down", "2026-12-04")], ("yes", "no")),
        ([_guess("up", "2026-11-26")], ("no", "")),
        ([_guess("up", "2026-12-04"), _guess("down", "2026-12-04")], ("yes", "both")),
    ],
)
def test_a_guess_covers_the_move_only_while_its_span_holds_the_day(
    guesses: list[dict[str, str]], expected: tuple[str, str]
) -> None:
    # given guesses on the 10-year yield, and Friday's big move up

    # when its coverage is read
    covered = cli.coverage(UP_FRIDAY, [], [], guesses)

    # then a guess to Friday or later covers it, one ending Thursday does not, and both ways is both
    assert covered == expected


def test_a_call_with_no_direction_covers_nothing_and_a_forecast_s_span_does() -> None:
    # given a live call on Friday with no direction, and a stated forecast down to December
    call = study.LoggedCall(
        datetime(2026, 11, 27, 13, 40, tzinfo=UTC), "nfp", FRIDAY, 1.0, TEN_YEAR, ""
    )
    forecast = {
        "market": TEN_YEAR,
        "direction": "down",
        "first": "2026-11-23",
        "last": "2026-12-21",
    }

    # when the move's coverage is read with each
    by_call = cli.coverage(UP_FRIDAY, [call], [], [])
    by_forecast = cli.coverage(UP_FRIDAY, [call], [forecast], [])

    # then the call covers nothing, and the forecast covers it the wrong way
    assert by_call == ("no", "")
    assert by_forecast == ("yes", "no")


FLOWS = ["nfp", "cpi"]


def _reply(**item: str) -> str:
    return "Here is what I found:\n" + json.dumps([item])


@pytest.mark.parametrize(
    ("reply", "kind", "flow"),
    [
        (_reply(kind="unscheduled", reason="A hack.", link=""), "nothing found", ""),
        (
            _reply(kind="measured", flow="nfp", reason="Jobs beat.", link="https://x.test/a"),
            "measured",
            "nfp",
        ),
        (
            _reply(kind="measured", flow="tankan", reason="Tankan.", link="https://x.test/b"),
            "scheduled",
            "",
        ),
        (
            _reply(kind="scheduled", flow="cpi", reason="Results.", link="https://x.test/c"),
            "scheduled",
            "",
        ),
    ],
)
def test_a_reason_is_kept_only_with_a_link_and_measured_only_for_our_flows(
    reply: str, kind: str, flow: str
) -> None:
    # given the model's reply

    # when it is read
    read = cli.read_reason(reply, FLOWS)

    # then a reason with no link is nothing found, and a flow we do not measure is scheduled
    assert (read["kind"], read["flow"]) == (kind, flow)


def test_a_reply_of_no_known_kind_raises() -> None:
    # given a reply whose kind is none of the four

    # when it is read, then it raises, so the row stays not asked
    with pytest.raises(ValueError, match="known kind"):
        cli.read_reason(_reply(kind="maybe", reason="?", link="https://x.test"), FLOWS)


def test_the_scan_keeps_a_symbol_only_for_a_market_we_track() -> None:
    # given a scan naming copper with no symbol, gold with ours, and a symbol we do not have
    reply = json.dumps(
        [
            {"market": "copper", "symbol": "", "move": "a record high", "link": "https://x.test/1"},
            {"market": "gold", "symbol": "GC / XAU", "move": "down 3%", "link": "https://x.test/2"},
            {"market": "lithium", "symbol": "LIT", "move": "up 9%", "link": "https://x.test/3"},
            {"market": "tin", "symbol": "", "move": "up 5%", "link": ""},
        ]
    )

    # when it is read
    rows = cli.read_scan(reply, FRIDAY, study.MVP_PRICE_SERIES)

    # then gold keeps its symbol, lithium's is blanked, and the row with no link is dropped
    assert [(r["market"], r["symbol"]) for r in rows] == [
        ("copper", ""),
        ("gold", "GC / XAU"),
        ("lithium", ""),
    ]


def test_a_scan_that_finds_nothing_marks_the_day_scanned() -> None:
    # given an empty list from the scan

    # when it is read
    rows = cli.read_scan("[]", FRIDAY, study.MVP_PRICE_SERIES)

    # then one row with no market says the day was scanned
    assert [(r["day"], r.get("market", "")) for r in rows] == [("2026-11-27", "")]


def test_a_failed_reason_is_asked_again_the_next_evening_and_the_scan_is_not(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given the 10-year yield's big move on Friday stored, and a model that fails the reason once
    study.store_daily_bars(TEN_YEAR, "^TNX", _yields(9.0))
    monkeypatch.setattr(cli.settings, "calls_path", tmp_path / "data" / "calls.csv")
    monkeypatch.setattr(cli.settings, "scoreboard_dir", tmp_path / "docs" / "scoreboard")
    asked: list[str] = []
    answers = iter(
        [
            "I could not search.",
            _reply(kind="unscheduled", reason="A bond sale went badly.", link="https://x.test/r"),
        ]
    )

    def model(prompt: str, web: bool) -> str:
        asked.append("scan" if "any market" in prompt else "reason")
        return "[]" if asked[-1] == "scan" else next(answers)

    monkeypatch.setattr(cli, "_run_model", model)

    # when the evening runs twice
    first = cli.main(["big-moves"])
    rows_first = cli._read_rows(tmp_path / "data" / "big-moves.csv")
    second = cli.main(["big-moves"])
    rows = cli._read_rows(tmp_path / "data" / "big-moves.csv")

    # then the first leaves the reason blank, the second fills it, and the five days' scans run once
    assert (first, second) == (0, 0)
    assert [(r["day"], r["kind"], r["covered"]) for r in rows_first] == [("2026-11-27", "", "no")]
    assert [(r["kind"], r["reason"]) for r in rows] == [("unscheduled", "A bond sale went badly.")]
    assert asked.count("scan") == 5 and asked.count("reason") == 2
    news = cli._read_rows(tmp_path / "data" / "news-moves.csv")
    assert [r["day"] for r in news] == [d.isoformat() for d in _weekdays(FRIDAY, 5)]
