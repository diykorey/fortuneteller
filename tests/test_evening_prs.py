"""Step 57, R11 (docs/steps/technical-fixes.md): the evening's pages and the triggers' log go in
pull requests of their own, the pages' merged, so the evening's guesses never wait with the log.
Step 58 (docs/steps/publishing-schedule.md): the draft at 14:00 New York, the reminder at 16:00,
and the evening publishing the day's front pull request. The real script runs against a local
origin, with gh, uv, git push and notify-send stood in for."""

import os
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import NamedTuple

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "release-day.sh"
GIT = shutil.which("git") or "git"

GH = """#!/usr/bin/env bash
echo "gh $*" >> "$CALLS"
case "$1 $2" in
    "run list") echo "[]" ;;
    "pr list")
        case "$*" in
            *'startswith("calls-")'*) printf '%s' "${OPEN:-[]}" | jq -r "${@: -1}" ;;
            *createdAt*) printf '%s' "${FRONT_LIST:-}" ;;
            *"--head front-"*) printf '%s' "${REMIND:-}" ;;
            *front-*) printf '%s' "${FRONT_OPEN:-}" ;;
        esac ;;
    "pr view") echo "${OTHERS:-0}" ;;
esac
exit 0
"""

# Tonight's commands: the triggers' log and the pages both change, nothing is scored.
UV = """#!/usr/bin/env bash
dir=$3
case "$5" in
    triggers) echo "2026-11-23,a trigger,graded" >> "$dir/data/trigger-log.csv" ;;
    scoreboard) echo '{"written": "tonight"}' > "$dir/docs/scoreboard/data.json" ;;
    score) echo "nothing to score" ;;
    guess) echo "BTC,a guess" >> "$dir/docs/predicts/our-guesses.csv" ;;
    draft) printf 'stated,market\ntoday,BTC\n' > "$dir/docs/predicts/front-next.csv" ;;
esac
exit 0
"""

GIT_STUB = f"""#!/usr/bin/env bash
for a in "$@"; do
    if [ "$a" = push ]; then echo "git $*" >> "$CALLS"; exit 0; fi
done
exec {GIT} "$@"
"""


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        [GIT, "-C", str(cwd), *args], check=True, capture_output=True, text=True
    ).stdout


def _stub(folder: Path, name: str, body: str) -> None:
    path = folder / name
    path.write_text(body)
    path.chmod(0o755)


class Job(NamedTuple):
    origin: Path
    job: Path
    calls: Path
    env: dict[str, str]


def _job(tmp_path: Path) -> Job:
    """An origin with the pages, the log, the ledger and an unchanged score, a checkout of it,
    and gh, uv, git push, sleep and notify-send stood in for."""
    seed = tmp_path / "seed"
    for path, text in {
        "data/trigger-log.csv": "day,trigger,grade\n",
        "data/score.txt": "nothing to score\n",
        "docs/scoreboard/data.json": '{"written": "yesterday"}\n',
        "docs/predicts/front.csv": "stated,market\n",
        "docs/predicts/front-next.csv": "stated,market\n",
        "docs/predicts/our-guesses.csv": "market,statement\n",
    }.items():
        (seed / path).parent.mkdir(parents=True, exist_ok=True)
        (seed / path).write_text(text)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "job",
        "GIT_AUTHOR_EMAIL": "job@example.com",
        "GIT_COMMITTER_NAME": "job",
        "GIT_COMMITTER_EMAIL": "job@example.com",
    }
    subprocess.run([GIT, "init", "-q", "-b", "main", str(seed)], check=True)
    _git(seed, "add", ".")
    subprocess.run([GIT, "-C", str(seed), "commit", "-q", "-m", "seed"], check=True, env=env)
    origin = tmp_path / "origin.git"
    subprocess.run([GIT, "clone", "-q", "--bare", str(seed), str(origin)], check=True)
    checkout = tmp_path / "checkout"
    subprocess.run([GIT, "clone", "-q", str(origin), str(checkout)], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _stub(bin_dir, "gh", GH)
    _stub(bin_dir, "uv", UV)
    _stub(bin_dir, "git", GIT_STUB)
    _stub(bin_dir, "sleep", "#!/usr/bin/env bash\nexit 0\n")
    _stub(bin_dir, "notify-send", '#!/usr/bin/env bash\necho "notify $*" >> "$CALLS"\n')
    calls = tmp_path / "calls.txt"
    calls.touch()
    job = tmp_path / "job"
    env |= {
        "PATH": f"{bin_dir}:{env['PATH']}",
        "CALLS": str(calls),
        "FT_MAIN_CHECKOUT": str(checkout),
        "FT_JOB_TREE": str(job),
    }
    return Job(origin, job, calls, env)


def _run(job: Job, step: str, **extra: str) -> str:
    run = subprocess.run(
        ["bash", str(SCRIPT), step],
        env=job.env | extra,
        capture_output=True,
        text=True,
        timeout=120,
    )
    log = job.calls.read_text()
    assert run.returncode == 0, run.stdout + log
    return run.stdout + log


def _ago(hours: float) -> str:
    return (datetime.now(UTC) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_the_pages_are_merged_apart_from_the_triggers_log_and_no_front_is_proposed(
    tmp_path: Path,
) -> None:
    # given the job's origin and stand-ins, with no front pull request open
    job = _job(tmp_path)

    # when the evening runs
    log = _run(job, "score")

    # then the pages' pull request holds the pages alone and is merged, the triggers' holds the
    # log alone and is left for a person, and no guess is made or front pull request opened
    day = next(w for w in log.split() if w.startswith("scoreboard-")).removeprefix("scoreboard-")
    assert "--head scoreboard-" + day in log
    assert "--head triggers-" + day in log
    assert "--merge scoreboard-" + day in log
    assert "--merge triggers-" not in log
    pages = _git(job.job, "show", "--name-only", "--format=", "scoreboard-" + day).split()
    trigger = _git(job.job, "show", "--name-only", "--format=", "triggers-" + day).split()
    assert pages == ["docs/scoreboard/data.json"]
    assert trigger == ["data/trigger-log.csv"]
    assert "--head front-" not in log and "notify" not in log


@pytest.mark.parametrize(
    ("open_head", "held"), [("triggers-2026-11-24", False), ("score-2026-11-24", True)]
)
def test_only_an_open_score_or_pages_pull_request_holds_the_evening(
    tmp_path: Path, open_head: str, held: bool
) -> None:
    # given the job's origin and stand-ins, with one of the evening's pull requests left open
    job = _job(tmp_path)

    # when the evening runs
    log = _run(job, "score", OPEN=f'[{{"headRefName": "{open_head}"}}]')

    # then an open score holds it, and an open triggers' log, left for a person, does not
    assert ("waiting for " + open_head in log) is held
    assert ("--merge scoreboard-" in log) is not held


def test_the_draft_keeps_the_guesses_then_proposes_the_front_and_says_so(tmp_path: Path) -> None:
    # given the job's origin and stand-ins, with no front pull request open
    job = _job(tmp_path)

    # when the draft runs at 14:00
    log = _run(job, "draft")

    # then the ledger goes in a pull request merged on passing checks, the proposal in the day's
    # front pull request, never merged, and one notification is sent
    day = next(w for w in log.split() if w.startswith("guesses-")).removeprefix("guesses-")
    assert "--merge guesses-" + day in log
    guesses = _git(job.job, "show", "--name-only", "--format=", "guesses-" + day).split()
    assert guesses == ["docs/predicts/front-next.csv", "docs/predicts/our-guesses.csv"]
    front = _git(job.job, "show", f"front-{day}:docs/predicts/front.csv")
    assert front == "stated,market\ntoday,BTC\n"
    assert "--merge front-" not in log
    assert log.count("notify ") == 1


def test_the_draft_proposes_nothing_while_an_earlier_front_the_owner_changed_is_open(
    tmp_path: Path,
) -> None:
    # given an earlier front pull request on origin holding the job's commit and the owner's
    job = _job(tmp_path)
    owner = tmp_path / "owner"
    subprocess.run([GIT, "clone", "-q", str(job.origin), str(owner)], check=True)
    _git(owner, "switch", "-q", "-c", "front-2026-11-24")
    for words in ("job", "owner"):
        (owner / "docs/predicts/front.csv").write_text(f"stated,market\n{words},BRN\n")
        subprocess.run([GIT, "-C", str(owner), "commit", "-qam", words], check=True, env=job.env)
    _git(owner, "push", "-q", "origin", "front-2026-11-24")

    # when the draft runs
    log = _run(job, "draft", FRONT_OPEN="front-2026-11-24\n")

    # then it is left open and nothing new is proposed or announced
    assert "today proposes nothing" in log
    assert "pr close" not in log and "--head front-" not in log and "notify " not in log


@pytest.mark.parametrize(
    ("hours", "others", "published"),
    [(3.1, "0", True), (2.0, "0", False), (5.0, "1", False)],
)
def test_the_evening_publishes_a_front_three_hours_old_with_only_the_owner_s_commits(
    tmp_path: Path, hours: float, others: str, published: bool
) -> None:
    # given the day's front pull request opened some hours ago, with or without another account's
    # commit on it
    job = _job(tmp_path)
    listed = f"470 front-2026-11-25 {_ago(hours)}\n"

    # when the evening runs
    log = _run(job, "score", FRONT_LIST=listed, OTHERS=others)

    # then it is merged only when 3 hours old and with no other account's commit
    assert ("--merge front-2026-11-25" in log) is published


@pytest.mark.parametrize(("open_pr", "notified"), [("470\n", True), ("", False)])
def test_the_reminder_shows_only_an_open_front(
    tmp_path: Path, open_pr: str, notified: bool
) -> None:
    # given the day's front pull request open or not
    job = _job(tmp_path)

    # when the reminder runs at 16:00
    log = _run(job, "remind", REMIND=open_pr)

    # then a notification only while it is open, and no store or tree touched
    assert ("notify " in log) is notified
    assert not job.job.exists()


def test_the_job_runs_its_own_tree_s_script_at_origin_main(tmp_path: Path) -> None:
    # given an origin whose release-day script only says where it ran, and the job's worktree of
    # it left on an older commit
    seed = tmp_path / "seed"
    (seed / "scripts").mkdir(parents=True)
    script = seed / "scripts" / "release-day.sh"
    script.write_text('echo "old $*"\n')
    env = {**os.environ, "GIT_AUTHOR_NAME": "job", "GIT_AUTHOR_EMAIL": "job@example.com"}
    env |= {"GIT_COMMITTER_NAME": "job", "GIT_COMMITTER_EMAIL": "job@example.com"}
    subprocess.run([GIT, "init", "-q", "-b", "main", str(seed)], check=True)
    _git(seed, "add", ".")
    subprocess.run([GIT, "-C", str(seed), "commit", "-q", "-m", "old"], check=True, env=env)
    origin = tmp_path / "origin.git"
    subprocess.run([GIT, "clone", "-q", "--bare", str(seed), str(origin)], check=True)
    job = tmp_path / "job"
    subprocess.run([GIT, "clone", "-q", str(origin), str(job)], check=True)
    script.write_text('echo "tree $*"\n')
    subprocess.run([GIT, "-C", str(seed), "commit", "-qam", "new"], check=True, env=env)
    _git(seed, "push", "-q", str(origin), "main")

    # when the job starts
    run = subprocess.run(
        ["bash", str(SCRIPT.with_name("job-start.sh")), "score"],
        env=env | {"FT_JOB_TREE": str(job)},
        capture_output=True,
        text=True,
        timeout=60,
    )

    # then origin/main's script ran, from the job's tree, not the checkout's beside the starter
    assert run.stdout == "tree score\n", run.stderr
