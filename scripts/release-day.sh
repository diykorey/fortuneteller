#!/usr/bin/env bash
# The release-day job (docs/steps/release-day-job.md) and the evening score (docs/steps/
# evening-score.md), in a worktree of their own from origin/main: `live` logs the day's calls,
# `score` loads the day and grades them; a change goes to a pull request, a failure to an issue.
set -uo pipefail

repo=diykorey/fortuneteller
step=${1:?live or score}
main_checkout=${FT_MAIN_CHECKOUT:?the checkout whose database and cache the job reads}
job_tree=${FT_JOB_TREE:?the job's own worktree}
day=$(TZ=America/New_York date +%F)
out=$(mktemp)
# Everything goes to $out, the issue's body if the run fails; the journal gets it at the end.
exec 3>&1 >>"$out" 2>&1
trap 'cat "$out" >&3; rm -f "$out"' EXIT

case $step in
    live) title="Release-day job failed on $day" ;;
    score) title="Evening score failed on $day" ;;
    *) printf 'unknown step: %s\n' "$step"; exit 2 ;;
esac

report() {
    printf '%s: %s\n' "$title" "$1"
    gh issue create -R "$repo" --title "$title" --body-file "$out"
    exit 1
}

# One lock for both steps: the morning and the evening never hold the database at once.
exec 4>"$job_tree.lock"
flock 4 || report "flock $job_tree.lock"

git -C "$main_checkout" fetch -q origin || report "git fetch"
if [ ! -d "$job_tree" ]; then
    git -C "$main_checkout" worktree add -q --detach "$job_tree" origin/main ||
        report "git worktree add"
fi
git -C "$job_tree" switch -q --discard-changes --detach origin/main ||
    report "git switch in $job_tree"

export FT_DB_PATH="$main_checkout/data/fortuneteller.duckdb"
export FT_CACHE_DIR="$main_checkout/data/cache"

# Commits $1 on branch $2 and opens its pull request with body $3.
open_pr() {
    git -C "$job_tree" switch -q -c "$2" &&
        git -C "$job_tree" commit -q -m "$1" -- "$file" &&
        git -C "$job_tree" -c credential.helper= -c credential.helper='!gh auth git-credential' \
            push -q "https://github.com/$repo.git" "$2" &&
        gh pr create -R "$repo" --base main --head "$2" --title "$1" --body "$3" ||
        report "committing, pushing or opening the pull request for $2"
}

if [ "$step" = live ]; then
    file=data/calls.csv
    FT_CALLS_PATH="$job_tree/$file" uv run --directory "$job_tree" fortuneteller live
    live=$?
    if ! git -C "$job_tree" diff --quiet -- "$file"; then
        flows=$(git -C "$job_tree" diff -U0 -- "$file" | grep '^+[0-9]' | cut -d, -f2 |
            sort -u | paste -sd-)
        at=$(date -u +%H:%M:%SZ)
        open_pr "Log the live $flows call of $day" "calls-$flows-$day" \
            "Logged by the release-day job at $at; graded by \`score\` after the closes."
    fi
    [ "$live" -eq 0 ] || report "fortuneteller live exited $live"
    exit 0
fi

file=data/score.txt
waiting=$(gh pr list -R "$repo" --state open --json headRefName \
    --jq '.[].headRefName | select(startswith("calls-") or startswith("score-"))') ||
    report "gh pr list"
if [ -n "$waiting" ]; then
    printf 'score: waiting for %s to be merged\n' "$waiting"
    exit 0
fi
for command in load-releases load-prices load-surprises; do
    uv run --directory "$job_tree" fortuneteller "$command" ||
        report "fortuneteller $command exited $?"
done
# --directory runs it in $job_tree, so the relative calls path names no home directory.
FT_CALLS_PATH=data/calls.csv uv run --directory "$job_tree" fortuneteller score >"$job_tree/$file" ||
    report "fortuneteller score exited $?"
cat "$job_tree/$file"
if grep -q '^pending: ' "$job_tree/$file"; then
    echo "score: rows pending; nothing committed"
    exit 0
fi
if ! git -C "$job_tree" diff --quiet -- "$file"; then
    open_pr "Score the calls on $day" "score-$day" \
        "Graded by the evening score at $(date -u +%H:%M:%SZ), after the closes."
fi
