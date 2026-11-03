import os
import subprocess
from datetime import UTC, date, datetime, time
from pathlib import Path

import duckdb
import pytest

from fortuneteller import db, flows, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import NEW_YORK, FirstRelease

DAY = date(2026, 11, 12)
BEFORE = datetime(2026, 11, 12, 13, 0, tzinfo=UTC)  # 08:00 New York
HEADER = "flow,instrument,direction\n"


def _git(repo: Path, *args: str, who: str = "player") -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": who,
        "GIT_AUTHOR_EMAIL": f"{who}@example.com",
        "GIT_COMMITTER_NAME": who,
        "GIT_COMMITTER_EMAIL": f"{who}@example.com",
    }
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=env
    ).stdout.strip()


def _cpi_release(
    con: duckdb.DuckDBPyConnection, released: date, moves: dict[str, float] | None = None
) -> None:
    flows.store_releases(flows.CPI_FLOW, [FirstRelease(date(2026, 10, 1), released, 0.3)], con=con)
    event = flows.stored_events(flows.CPI_FLOW, con=con)[-1]
    for instrument, move in (moves or {}).items():
        con.execute(
            "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) "
            "VALUES (?, ?, 'pct', ?)",
            [event.event_id, instrument, move],
        )


def _guess(
    instrument: str,
    direction: int = 1,
    day: date = DAY,
    flow: str = "cpi",
    path: str = "2026-11-12-alice.csv",
    sha: str = "a",
) -> study.Guess:
    return study.Guess(day, "alice", flow, instrument, direction, path, sha)


def test_a_guess_file_is_dated_by_the_commit_that_added_it_to_main(tmp_path: Path) -> None:
    # given a repository whose guesses arrive by a merge commit, from a side branch, and by a squash
    # commit on main; the merged file is later edited and then deleted
    repo = tmp_path / "repo"
    guesses = repo / "data" / "guesses"
    guesses.mkdir(parents=True)
    _git(tmp_path, "init", "-q", "-b", "main", str(repo))
    (guesses / ".gitkeep").write_text("")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "start", who="owner")
    _git(repo, "checkout", "-q", "-b", "alice")
    (guesses / "2026-11-12-alice.csv").write_text(HEADER + "cpi,DXY,up\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "guess")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "alice", "-m", "Merge pull request #1", who="GitHub")
    merge = _git(repo, "rev-parse", "HEAD")
    (guesses / "2026-11-12-bob.csv").write_text(HEADER + "cpi,VIX,down\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Squashed guess (#2)", who="GitHub")
    squash = _git(repo, "rev-parse", "HEAD")
    (guesses / "2026-11-12-alice.csv").write_text(HEADER + "cpi,DXY,down\n")
    _git(repo, "commit", "-q", "-am", "edit", who="owner")
    _git(repo, "rm", "-q", "data/guesses/2026-11-12-alice.csv")
    _git(repo, "commit", "-q", "-m", "delete", who="owner")

    # when the guess files are listed
    files = study.guess_files(guesses)

    # then each is found at the commit that added it to main, as it was then, and the deleted one
    # still counts
    assert files == [
        ("2026-11-12-alice.csv", merge, HEADER + "cpi,DXY,up\n"),
        ("2026-11-12-bob.csv", squash, HEADER + "cpi,VIX,down\n"),
    ]


def test_a_badly_named_or_written_file_voids_only_its_own_guesses() -> None:
    # given a good file, one with a capital in its handle and one with a wrong direction
    files = [
        ("2026-11-12-alice.csv", "a", HEADER + "cpi,DXY,up\n"),
        ("2026-11-12-Bob.csv", "b", HEADER + "cpi,DXY,up\n"),
        ("2026-11-12-carol.csv", "c", HEADER + "cpi,DXY,sideways\n"),
    ]

    # when they are read
    guesses, bad = study.read_guesses(files)

    # then the good one is read and the other two are named
    assert guesses == [_guess("DXY")]
    assert bad == [
        "2026-11-12-Bob.csv: void, its name is not <day>-<handle>.csv, lowercase",
        "2026-11-12-carol.csv: void, line 2: direction 'sideways'",
    ]


def test_each_guess_is_graded_voided_or_waits(tmp_db: Path) -> None:
    # given a CPI release on 11-12 with its moves, a later one on 12-10 not yet moved; guesses
    # merged before 08:30 except one, and one file that never went through a pull request
    con = db.get_connection()
    _cpi_release(con, DAY, {"DXY": 0.002, "VIX": 0.01})
    _cpi_release(con, date(2026, 12, 10))
    late = _guess("SPY / ES", sha="late")
    pushed = _guess("VIX", sha="pushed", path="2026-11-12-bob.csv")
    guesses = [
        _guess("DXY"),
        _guess("VIX", -1),
        _guess("DXY", -1),
        _guess("BTC"),
        _guess("SPY / ES", flow="posts"),
        late,
        pushed,
        _guess("SPY / ES", day=date(2026, 11, 13), path="2026-11-13-alice.csv"),
        _guess("SPY / ES", day=date(2026, 12, 10), path="2026-12-10-alice.csv"),
        _guess("SPY / ES", day=date(2027, 1, 13), path="2027-01-13-alice.csv"),
    ]
    times = {"a": BEFORE, "late": datetime(2026, 11, 12, 13, 30, tzinfo=UTC), "pushed": None}

    # when they are scored
    graded = study.score_guesses(guesses, times.__getitem__, con=con)

    # then each has its state and why
    assert [(g.state, g.reason) for g in graded] == [
        ("right", None),
        ("wrong", None),
        ("void", "repeats cpi DXY in its file"),
        ("void", "BTC is not one of cpi's links"),
        ("void", "posts is not a flow `live` calls"),
        ("void", "merged 2026-11-12 08:30 New York, not before 08:30 on 2026-11-12"),
        ("void", "not merged through a pull request"),
        ("void", "cpi had no release on 2026-11-13"),
        ("waiting", "its move is not loaded"),
        ("waiting", "the release is not loaded"),
    ]


def test_score_prints_each_guess_beside_the_machine_s_row(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a CPI release with its moves, the machine's rows (a too-few call on the yield, silent
    # on VIX, none on the dollar) and alice's guesses, one for a release not loaded yet
    con = db.get_connection()
    _cpi_release(con, DAY, {"DXY": 0.002, "VIX": 0.01, "UST10Y / ZN": 5.0})
    at = datetime.combine(DAY, time(9, 0), tzinfo=NEW_YORK)
    study.append_calls(
        settings.calls_path,
        [
            study.LoggedCall(at, "cpi", DAY, 0.3, "UST10Y / ZN", study.TOO_FEW_CALLS, 1),
            study.LoggedCall(at, "cpi", DAY, 0.3, "VIX", study.SILENT),
        ],
    )
    files = [
        ("2026-11-12-alice.csv", "a", HEADER + "cpi,DXY,up\ncpi,UST10Y / ZN,down\ncpi,VIX,up\n"),
        ("2027-01-13-alice.csv", "b", HEADER + "cpi,DXY,up\n"),
    ]
    monkeypatch.setattr(study, "guess_files", lambda directory: files)
    monkeypatch.setattr(study, "merged_at", lambda directory, sha: BEFORE)

    # when the log is scored
    code = main(["score"])

    # then the guesses block shows each guess, the machine's row and alice's count, and nothing
    # in it reads as pending
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    start = out.index("guesses: 4")
    assert out[start + 1 : start + 6] == [
        "  2026-11-12 alice cpi DXY up: right; machine: not logged",
        "  2026-11-12 alice cpi UST10Y / ZN down: wrong; machine: waiting",
        "  2026-11-12 alice cpi VIX up: right; machine: no call",
        "  2027-01-13 alice cpi DXY up: waiting, the release is not loaded; machine: not logged",
        "  alice: 2 of 3 right",
    ]
    assert not any(line.startswith("pending:") for line in out[start:])


def test_score_stops_when_github_cannot_be_asked(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a guess file, and GitHub not answering
    files = [("2026-11-12-alice.csv", "a", HEADER + "cpi,DXY,up\n")]
    monkeypatch.setattr(study, "guess_files", lambda directory: files)

    def fail(directory: Path, sha: str) -> None:
        raise subprocess.CalledProcessError(1, ["gh", "api"])

    monkeypatch.setattr(study, "merged_at", fail)

    # when the log is scored
    code = main(["score"])

    # then it stops with an error rather than voiding the guess
    assert code == 1
    assert "the guesses cannot be read" in capsys.readouterr().err
