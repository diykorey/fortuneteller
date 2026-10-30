#!/usr/bin/env bash
# The release-day job (docs/steps/release-day-job.md) and the evening score (docs/steps/
# evening-score.md), in a worktree of their own from origin/main: `live` logs the day's calls,
# `score` loads the day and grades them; a change goes to a pull request, a failure to an issue.
set -uo pipefail

repo=diykorey/fortuneteller
step=${1:-live}
main_checkout=${FT_MAIN_CHECKOUT:?the checkout whose database and cache the job reads}
job_tree=${FT_JOB_TREE:?the worktree the job works in}
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

# A desktop popup (docs/steps/rung-6-delivery.md); one that fails never fails the run.
popup() {
    notify-send -u critical -a FortuneTeller "$1" "$2" || true
}

report() {
    printf '%s: %s\n' "$title" "$1"
    popup "$title" "$1"
    gh issue create -R "$repo" --title "$title" --body-file "$out"
    exit 1
}

# One lock for both steps: the morning and the evening never hold the database at once.
exec 4>"$job_tree.lock"
flock 4 || report "flock $job_tree.lock"

# A run the timer catches up as the laptop wakes can start before the network is back (#190, and a
# 2026-10-30 run that could not even open its issue), so the fetch is tried for three minutes.
fetched=
for _ in $(seq 12); do
    if git -C "$main_checkout" fetch -q origin; then
        fetched=1
        break
    fi
    sleep 15
done
[ -n "$fetched" ] || report "git fetch"
if [ ! -d "$job_tree" ]; then
    git -C "$main_checkout" worktree add -q --detach "$job_tree" origin/main ||
        report "git worktree add"
fi
git -C "$job_tree" switch -q --discard-changes --detach origin/main ||
    report "git switch in $job_tree"

export FT_DB_PATH="$main_checkout/data/fortuneteller.duckdb"
export FT_CACHE_DIR="$main_checkout/data/cache"

# Commits $files as $1 on branch $2 and opens its pull request with body $3. A run repeated on
# the same day, after a failed push or a morning catch-up, finds the branch the first run made:
# -C resets it rather than refusing it (the 2026-10-22 evening failed so, issue #172).
open_pr() {
    # shellcheck disable=SC2086
    git -C "$job_tree" switch -q -C "$2" &&
        git -C "$job_tree" commit -q -m "$1" -- $files &&
        git -C "$job_tree" -c credential.helper= -c credential.helper='!gh auth git-credential' \
            push -q "https://github.com/$repo.git" "$2" &&
        gh pr create -R "$repo" --base main --head "$2" --title "$1" --body "$3" ||
        report "committing, pushing or opening the pull request for $2"
}

# Merges the pull request of branch $1 as a merge commit and deletes the branch. GitHub may still
# be working out whether a pull request opened seconds ago can be merged, so it is asked three times.
merge_pr() {
    merged=
    for _ in 1 2 3; do
        if gh pr merge -R "$repo" --merge "$1"; then
            merged=1
            break
        fi
        sleep 20
    done
    [ -n "$merged" ] || report "merging the pull request for $1"
    git -C "$job_tree" -c credential.helper= -c credential.helper='!gh auth git-credential' \
        push -q "https://github.com/$repo.git" --delete "$1" || echo "the branch $1 stays on GitHub"
}

if [ "$step" = live ]; then
    file=data/calls.csv
    files=$file
    FT_CALLS_PATH="$job_tree/$file" uv run --directory "$job_tree" fortuneteller live
    live=$?
    if ! git -C "$job_tree" diff --quiet -- "$file"; then
        flows=$(git -C "$job_tree" diff -U0 -- "$file" | grep '^+[0-9]' | cut -d, -f2 |
            sort -u | paste -sd-)
        at=$(date -u +%H:%M:%SZ)
        open_pr "Log the live $flows call of $day" "calls-$flows-$day" \
            "Logged by the release-day job at $at; graded by \`score\` after the closes."
        # Rows that are all silent claim nothing, so their pull request is merged here (decided
        # 2026-10-28, docs/steps/jobless-claims.md); a call, or a run that failed, waits for a person.
        if [ "$live" -eq 0 ] && grep -Eq 'rows? logged today, all silent$' "$out"; then
            merge_pr "calls-$flows-$day"
            kept="merged: every row silent"
        else
            kept="open for review"
        fi
        popup "Log the live $flows call of $day" \
            "$(grep -E ': actual |^.{12} (up|down|—) |^no prediction: ' "$out")
$kept"
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
    # The scoreboard (docs/steps/scoreboard.md) is rewritten into the same pull request.
    FT_CALLS_PATH=data/calls.csv uv run --directory "$job_tree" fortuneteller scoreboard ||
        report "fortuneteller scoreboard exited $?"
    files="$file docs/scoreboard"
    open_pr "Score the calls on $day" "score-$day" \
        "Graded by the evening score at $(date -u +%H:%M:%SZ), after the closes."
fi
