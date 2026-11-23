"""Step 46, the loop's safety nets (docs/steps/loop-nets.md): a source asked again after a 5xx, a
timeout or a broken connection, and the watches replayed on the incidents' real rows and runs."""

import io
import json
import subprocess
import urllib.error
import urllib.request
from datetime import date
from email.message import Message
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import sources
from fortuneteller.sources import FredError, YahooError

DATA = Path(__file__).parent / "data"
# The runner's data/calls.csv after its live of 2026-11-19, run 44524466043's artifact, trimmed.
RUNNER_2026_11_19 = DATA / "runner_calls_2026-11-19.csv"
# main's data/calls.csv before and after PR #364 (merge 3077d54), the laptop's rows of 2026-11-19
# logged at 14:07 UTC, 37 minutes past their bar; trimmed.
MAIN_BEFORE_364 = DATA / "main_calls_before_pr364.csv"
MAIN_AFTER_364 = DATA / "main_calls_after_pr364.csv"
# The jobs workflow's runs from 2026-11-16 to 2026-11-20, as gh run list --json createdAt,event.
RUNS = DATA / "jobs_runs_2026-11-16_to_20.json"
KEY = "abcdef0123456789abcdef0123456789"


def _failure(url: str, code: int, body: bytes = b"") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, "failed", Message(), io.BytesIO(body))


def _serve(monkeypatch: pytest.MonkeyPatch, answers: list[int | BaseException]) -> list[str]:
    """urlopen answering each ask with the next answer, a status or a failure; the URLs asked."""
    asked: list[str] = []

    def answer(request: urllib.request.Request | str, timeout: float) -> io.BytesIO:
        url = request if isinstance(request, str) else request.full_url
        asked.append(url)
        reply = answers[len(asked) - 1]
        if isinstance(reply, BaseException):
            raise reply
        if reply != 200:
            raise _failure(url, reply, f"Bad request: {url}".encode())
        return io.BytesIO(b'{"observations": []}')

    monkeypatch.setattr(sources.urllib.request, "urlopen", answer)
    return asked


@pytest.fixture
def waits(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    slept: list[float] = []
    monkeypatch.setattr(sources, "sleep", slept.append)
    return slept


def test_a_fetch_answered_500_twice_returns_the_third_answer(
    monkeypatch: pytest.MonkeyPatch, waits: list[float], capsys: pytest.CaptureFixture[str]
) -> None:
    # given FRED answering 500, 500, then 200
    asked = _serve(monkeypatch, [500, 500, 200])

    # when a series is fetched
    body = sources.fetch_vintages(KEY, "PAYEMS")

    # then the third answer is returned, after waits of 30 and 90 seconds, each retry printed
    # without the key
    assert body == b'{"observations": []}'
    assert len(asked) == 3
    assert waits == [30, 90]
    printed = capsys.readouterr().err.splitlines()
    assert printed == [
        "retrying FRED after HTTP 500, in 30 s",
        "retrying FRED after HTTP 500, in 90 s",
    ]


def test_a_fetch_answered_500_three_times_raises_the_source_s_error(
    monkeypatch: pytest.MonkeyPatch, waits: list[float], capsys: pytest.CaptureFixture[str]
) -> None:
    # given FRED answering 500 to every ask, its body echoing the URL with the key
    asked = _serve(monkeypatch, [500, 500, 500])

    # when a series is fetched
    with pytest.raises(FredError) as caught:
        sources.fetch_vintages(KEY, "PAYEMS")

    # then it is asked three times and fails as today, with the key redacted everywhere
    assert len(asked) == 3
    assert waits == [30, 90]
    assert str(caught.value).startswith("FRED returned HTTP 500: Bad request: ")
    assert "<redacted>" in str(caught.value)
    assert KEY not in str(caught.value)
    assert KEY not in capsys.readouterr().err


@pytest.mark.parametrize("code", [403, 404])
def test_a_4xx_is_asked_once(
    code: int, monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    # given Yahoo refusing the ask
    asked = _serve(monkeypatch, [code, 200])

    # when / then the fetch fails at once with Yahoo's error, as today
    with pytest.raises(YahooError, match=rf"HTTP {code} for \^VIX"):
        sources.fetch_daily_bars("^VIX")
    assert len(asked) == 1
    assert waits == []


def test_a_timeout_and_a_broken_connection_are_asked_again(
    monkeypatch: pytest.MonkeyPatch, waits: list[float], capsys: pytest.CaptureFixture[str]
) -> None:
    # given a read that times out with the URL and key in its text, then a refused connection
    asked = _serve(
        monkeypatch,
        [
            TimeoutError(f"timed out fetching ?api_key={KEY}"),
            urllib.error.URLError(ConnectionRefusedError("refused")),
            200,
        ],
    )

    # when a series is fetched
    body = sources.fetch_vintages(KEY, "PAYEMS")

    # then the third answer is returned, each retry named by its failure's kind alone
    assert body == b'{"observations": []}'
    assert len(asked) == 3
    assert capsys.readouterr().err.splitlines() == [
        "retrying FRED after TimeoutError, in 30 s",
        "retrying FRED after ConnectionRefusedError, in 90 s",
    ]


def test_with_less_budget_left_than_the_next_wait_the_failure_raises_at_once(
    monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    # given a process that has already waited all but 29 seconds of its budget
    monkeypatch.setattr(sources, "_waited", sources.RETRY_BUDGET - 29)
    asked = _serve(monkeypatch, [503, 200])

    # when / then the 503 is raised as Yahoo's error without a wait
    with pytest.raises(YahooError, match="HTTP 503"):
        sources.fetch_daily_bars("^VIX")
    assert len(asked) == 1
    assert waits == []


def test_the_budget_is_the_process_s_across_fetches(
    monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    # given Yahoo failing every ask
    _serve(monkeypatch, [502] * 9)

    # when three fetches fail in turn
    for _ in range(3):
        with pytest.raises(YahooError):
            sources.fetch_daily_bars("^VIX")

    # then the third takes only the wait the 300 seconds still allow
    assert waits == [30, 90, 30, 90, 30]
    assert sum(waits) <= sources.RETRY_BUDGET


def test_unlogged_lists_the_runner_s_rows_main_lacked_before_pr_364(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given the runner's rows of 2026-11-19 and main before PR #364 merged the laptop's

    # when they are compared
    status = cli.main(["unlogged", "2026-11-19", str(RUNNER_2026_11_19), str(MAIN_BEFORE_364)])

    # then the five claims rows are printed
    assert status == 0
    assert capsys.readouterr().out.splitlines() == [
        "2026-11-19 claims: UST10Y / ZN",
        "2026-11-19 claims: DXY",
        "2026-11-19 claims: EURUSD",
        "2026-11-19 claims: UST5Y / ZF",
        "2026-11-19 claims: XLU",
    ]


def test_unlogged_prints_nothing_once_pr_364_is_merged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given main after PR #364, and a calls branch whose file git show could not write
    empty = tmp_path / "calls-gone.csv"
    empty.write_text("")

    # when the runner's rows are compared with both
    status = cli.main(
        ["unlogged", "2026-11-19", str(RUNNER_2026_11_19), str(empty), str(MAIN_AFTER_364)]
    )

    # then nothing is printed: the laptop's rows hold every (flow, market), logged at another time
    assert status == 0
    assert capsys.readouterr().out == ""


def test_unlogged_finds_the_rows_on_a_calls_branch(tmp_path: Path) -> None:
    # given main before PR #364 and the laptop's calls branch, which holds the day's rows
    branch = tmp_path / "calls-claims-2026-11-19.csv"
    branch.write_text(MAIN_AFTER_364.read_text())

    # when / then nothing is missing
    assert cli.unlogged(date(2026, 11, 19), RUNNER_2026_11_19, [MAIN_BEFORE_364, branch]) == []


def test_unstarted_evening_prints_the_evening_the_timer_did_not_ask(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given the real runs of the week, in which only the schedule ran on the night of 2026-11-17

    # when the evening of 2026-11-17 is checked
    status = cli.main(["unstarted", "--evening", "2026-11-17", str(RUNS)])

    # then it is printed as not started
    assert status == 0
    assert capsys.readouterr().out == (
        "the runner's evening of 2026-11-17 was not started: no workflow_dispatch run was created "
        "from 2026-11-17 22:00 to 2026-11-18 06:00 UTC\n"
    )


def test_unstarted_evening_prints_nothing_for_an_evening_asked(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given the same runs, with the timer's ask at 23:30 UTC on 2026-11-18

    # when the evening of 2026-11-18 is checked
    status = cli.main(["unstarted", "--evening", "2026-11-18", str(RUNS)])

    # then nothing is printed
    assert status == 0
    assert capsys.readouterr().out == ""


def test_unstarted_morning_prints_a_day_with_no_run(capsys: pytest.CaptureFixture[str]) -> None:
    # given the same runs, none started on demand on Monday 2026-11-16

    # when that morning is checked
    status = cli.main(["unstarted", "--morning", "2026-11-16", str(RUNS)])

    # then it is printed as not started
    assert status == 0
    assert capsys.readouterr().out == (
        "the runner's morning of 2026-11-16 was not started: no workflow_dispatch run was created "
        "from 2026-11-16 11:00 to 2026-11-16 17:00 UTC\n"
    )


@pytest.mark.parametrize("day", ["2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"])
def test_unstarted_morning_prints_nothing_for_each_morning_asked(day: str) -> None:
    # given the same runs, each weekday from 2026-11-17 with a run started on demand by 17:00 UTC
    runs = json.loads(RUNS.read_text())

    # when / then each morning is found started
    assert cli.unstarted(date.fromisoformat(day), runs, evening=False) is None


def test_the_release_day_script_parses() -> None:
    # given the laptop's script

    # when bash reads it without running it
    result = subprocess.run(
        ["bash", "-n", str(Path(__file__).parents[1] / "scripts" / "release-day.sh")],
        capture_output=True,
        text=True,
    )

    # then it parses
    assert result.returncode == 0, result.stderr
