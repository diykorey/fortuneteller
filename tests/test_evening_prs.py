"""Step 57, R11 (docs/steps/technical-fixes.md): the evening's pages and the triggers' log go in
pull requests of their own, the pages' merged, so the evening's guesses never wait with the log.
The real script runs against a local origin, with gh, uv and git push stood in for."""

import os
import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "release-day.sh"
GIT = shutil.which("git") or "git"

GH = """#!/usr/bin/env bash
echo "gh $*" >> "$CALLS"
case "$1 $2" in
    "run list") echo "[]" ;;
esac
exit 0
"""

# Tonight's commands: the triggers' log and the pages both change, nothing is scored.
UV = """#!/usr/bin/env bash
dir=$3
case "$5" in
    triggers) echo "2026-11-23,a trigger,graded" >> "$dir/data/trigger-log.csv" ;;
    scoreboard)
        echo '{"written": "tonight"}' > "$dir/docs/scoreboard/data.json"
        printf 'stated,market\ntonight,BTC\n' > "$dir/docs/predicts/front-next.csv" ;;
    score) echo "nothing to score" ;;
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


def test_the_pages_are_merged_apart_from_the_triggers_log_and_the_front_keeps_tonight_s(
    tmp_path: Path,
) -> None:
    # given an origin with the pages, the log and an unchanged score, a checkout of it, and
    # gh, uv, git push, sleep and notify-send stood in for
    seed = tmp_path / "seed"
    for path, text in {
        "data/trigger-log.csv": "day,trigger,grade\n",
        "data/score.txt": "nothing to score\n",
        "docs/scoreboard/data.json": '{"written": "yesterday"}\n',
        "docs/predicts/front.csv": "stated,market\n",
        "docs/predicts/front-next.csv": "stated,market\n",
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
    _stub(bin_dir, "notify-send", "#!/usr/bin/env bash\nexit 0\n")
    calls = tmp_path / "calls.txt"
    job = tmp_path / "job"

    # when the evening runs
    run = subprocess.run(
        ["bash", str(SCRIPT), "score"],
        env=env
        | {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "CALLS": str(calls),
            "FT_MAIN_CHECKOUT": str(checkout),
            "FT_JOB_TREE": str(job),
        },
        capture_output=True,
        text=True,
        timeout=120,
    )

    # then the pages' pull request holds the pages alone and is merged, the triggers' holds the
    # log alone and is left for a person, and the front's holds tonight's proposal
    log = calls.read_text()
    assert run.returncode == 0, run.stdout + log
    day = next(w for w in log.split() if w.startswith("scoreboard-")).removeprefix("scoreboard-")
    assert "--head scoreboard-" + day in log
    assert "--head triggers-" + day in log
    assert "--merge scoreboard-" + day in log
    assert "--merge triggers-" not in log
    pages = _git(job, "show", "--name-only", "--format=", "scoreboard-" + day).split()
    trigger = _git(job, "show", "--name-only", "--format=", "triggers-" + day).split()
    assert pages == ["docs/predicts/front-next.csv", "docs/scoreboard/data.json"]
    assert trigger == ["data/trigger-log.csv"]
<<<<<<< HEAD


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
=======
    assert "--head front-" + day in log
    front = _git(job, "show", f"front-{day}:docs/predicts/front.csv")
    assert front == "stated,market\ntonight,BTC\n"
>>>>>>> origin/main
