"""Step 58, the publishing schedule (docs/steps/publishing-schedule.md): the draft at 14:00 New
York, `approve`, and the weekend's guesses left out of every record."""

import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli

TODAY = date(2026, 11, 25)


def _row(stated: str, market: str = "BRN", **extra: str) -> dict[str, str]:
    row = {
        "stated": stated,
        "market": market,
        "horizon": "week",
        "direction": "up",
        "last": "2026-12-04",
        "tag": "momentum",
        "confidence": "low",
        "grade": "came true",
        "base_rate": "0.5",
        "guesser": "news",
        "prompt": "news-1",
    }
    return row | extra


def test_a_weekend_s_guesses_from_the_schedule_count_in_no_record() -> None:
    # given guesses graded on Sunday 2026-11-22, Friday 2026-11-27, Saturday 2026-11-28 and
    # Sunday 2026-11-29, on four markets with no weekend close, so none is counted twice in a week
    rows = [
        _row("2026-11-22", "BRN"),
        _row("2026-11-27", "GC / XAU"),
        _row("2026-11-28", "SPY / ES"),
        _row("2026-11-29", "KC"),
    ]

    # when the records are made
    record = cli.guess_record(rows, "tag")
    counted = cli.counted_guesses(rows)

    # then the Sunday before the schedule and the Friday count, the weekend of the schedule not
    assert record[0]["evenings"] == 2 and record[0]["guesses"] == 2
    assert [r["stated"] for r in counted] == ["2026-11-22", "2026-11-27"]
    assert cli.excess_record(rows, "news")["counted"] == 2


def test_a_weekend_evening_is_no_evening_of_the_guessers_comparison() -> None:
    # given both guessers graded on Saturday 2026-11-28 and on Monday 2026-11-30
    rows = [
        _row(day, m, guesser=g, grade=grade)
        for day in ("2026-11-28", "2026-11-30")
        for g, m, grade in (("news", "BRN", "did not"), ("grounded", "GC / XAU", "came true"))
    ]

    # when the evenings are compared
    tally = cli.evenings_against(rows)

    # then only Monday is an evening, the grounded guesser higher on it
    assert tally == {"higher": 1, "lower": 0}


def _page(tmp_path: Path, stated: list[dict[str, object]]) -> Path:
    data = {"written": "2026-11-24", "stated": stated, "tally": None}
    page = tmp_path / "index.html"
    template = (Path(cli.__file__).parent / "predicts.html").read_text()
    page.write_text(template.replace(cli.PREDICTS_DATA_MARK, json.dumps(data)))
    return page


def test_the_draft_reads_the_stated_forecasts_from_the_published_page(tmp_path: Path) -> None:
    # given a published page stating the S&P 500 and home prices, and no page at all
    page = _page(tmp_path, [{"market": "SPY / ES"}, {"market": cli.HOME}])

    # when their markets are read
    # then both are found in order, and none without a page
    assert cli.published_stated(page) == ["SPY / ES", cli.HOME]
    assert cli.published_stated(tmp_path / "missing.html") == []


def test_the_draft_proposes_what_the_evening_proposed_on_the_same_files(tmp_path: Path) -> None:
    # given a ledger with a shown Brent guess and open ones on gold, the yen and the S&P 500, the
    # front page holding Brent, and a published page stating the S&P 500
    folder = tmp_path / "predicts"
    folder.mkdir()
    ledger = [
        _row("2026-11-24", "BRN", grade="", shown="2026-11-24"),
        _row("2026-11-24", "GC / XAU", grade="", confidence="high"),
        _row("2026-11-24", "USDJPY", grade=""),
        _row("2026-11-24", "SPY / ES", grade=""),
    ]
    rows = [cli._ledger_row(r) for r in ledger]
    cli._write_rows(folder / "our-guesses.csv", cli.GUESS_FIELDS, rows)
    front = cli.front_rows(rows[:1], [])
    cli._write_rows(folder / "front.csv", cli.FRONT_FIELDS, front)
    _page(folder, [{"market": "SPY / ES"}])
    evening = cli.front_proposal(["SPY / ES"], front, rows, rows, set(), TODAY)

    # when the draft runs
    proposal = cli.draft_front(folder, cli.published_stated(folder / "index.html"), TODAY)

    # then it is the evening's proposal, written to front-next.csv: Brent stays, gold and the yen
    # join, the S&P 500 waits beside its stated forecast
    assert proposal == evening
    assert [r["market"] for r in proposal] == ["BRN", "GC / XAU", "USDJPY"]
    assert cli._read_rows(folder / "front-next.csv") == proposal


CARDS = (
    "stated,market,direction,last,statement,why,source,withdrawn\n"
    '2026-11-25,BRN,down,2026-12-04,"Oil, lower by Dec 4.",OPEC adds supply.,https://example.com/a,\n'
    "2026-11-25,KC,up,2027-03-31,Coffee up.,Frost.,https://example.com/b,2026-11-26\n"
)


class FakeGh:
    """``gh`` for ``approve``: one open front pull request, checks and merge as told."""

    def __init__(self, checks: int = 0, merge: int = 0, open_prs: bool = True) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.checks, self.merge, self.open_prs = checks, merge, open_prs

    def __call__(self, *args: str) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        out, code = "", 0
        if args[:2] == ("pr", "list"):
            prs = [{"number": 470, "headRefName": "front-2026-11-25", "headRefOid": "abc123"}]
            prs.append({"number": 469, "headRefName": "scoreboard-2026-11-25", "headRefOid": "d"})
            out = json.dumps(prs if self.open_prs else prs[1:])
        elif args[:2] == ("pr", "checks"):
            code = self.checks
        elif args[:2] == ("pr", "merge"):
            code = self.merge
        return subprocess.CompletedProcess(args, code, out, "")


def _approve(
    monkeypatch: pytest.MonkeyPatch, gh: FakeGh, said: str, ask: bool = True, merge: bool = False
) -> tuple[int, str]:
    monkeypatch.setattr(cli, "_gh", gh)
    monkeypatch.setattr(
        cli, "_gh_api", lambda path: subprocess.CompletedProcess([path], 0, CARDS, "")
    )
    shown: list[str] = []
    code = cli.approve(lambda: said, shown.append, ask, merge)
    return code, "\n".join(shown)


def test_approve_prints_every_card_in_full_and_merges_the_printed_commit_on_yes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # given an open front pull request with two cards, one withdrawn, its checks passed
    gh = FakeGh()

    # when the owner answers yes
    code, out = _approve(monkeypatch, gh, "yes")

    # then each card's market, direction, last day, words, reasoning, source and withdrawal are
    # printed, and the pull request merged at the commit printed
    assert code == 0
    for text in (
        "front-2026-11-25 (#470), 2 cards:",
        "Market: BRN",
        "Direction: down",
        "Last day: 2026-12-04",
        "Says: Oil, lower by Dec 4.",
        "Why: OPEC adds supply.",
        "Source: https://example.com/a",
        "Withdrawn: 2026-11-26",
    ):
        assert text in out
    merge = next(c for c in gh.calls if c[:2] == ("pr", "merge"))
    assert merge[2] == "470" and merge[-2:] == ("--match-head-commit", "abc123")


@pytest.mark.parametrize(
    ("said", "gh", "left"),
    [
        ("n", FakeGh(), "left open"),
        ("", FakeGh(), "left open"),
        ("yes", FakeGh(checks=8), "checks have not all passed"),
        ("yes", FakeGh(merge=1), "changed since it was printed"),
    ],
)
def test_approve_leaves_it_open_unless_yes_with_checks_passed_and_nothing_added(
    monkeypatch: pytest.MonkeyPatch, said: str, gh: FakeGh, left: str
) -> None:
    # given an open front pull request
    # when the owner answers, with its checks and the merge as given
    code, out = _approve(monkeypatch, gh, said)

    # then it says why, and a merge is tried only when asked for and refused by GitHub
    assert left in out
    assert (("pr", "merge") in [c[:2] for c in gh.calls]) == bool(gh.merge)


def test_approve_print_asks_nothing_and_merges_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    # given an open front pull request
    gh = FakeGh()

    # when printed for a session
    code, out = _approve(monkeypatch, gh, "yes", ask=False)

    # then the cards are printed and nothing is merged
    assert code == 0 and "Card 2" in out
    assert all(c[:2] != ("pr", "merge") for c in gh.calls)


def test_approve_says_when_no_front_pull_request_is_open(monkeypatch: pytest.MonkeyPatch) -> None:
    # given only the pages' pull request open
    # when approve runs
    code, out = _approve(monkeypatch, FakeGh(open_prs=False), "yes")

    # then it says so
    assert (code, out) == (0, "approve: no front pull request is open")
