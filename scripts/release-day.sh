#!/usr/bin/env bash
# The release-day job (docs/steps/release-day-job.md): `fortuneteller live` in a worktree of its
# own, from origin/main; the rows it logs go to a pull request, and any failure to an issue.
set -uo pipefail

repo=diykorey/fortuneteller
main_checkout=${FT_MAIN_CHECKOUT:?the checkout whose database and cache the job reads}
job_tree=${FT_JOB_TREE:?the job's own worktree}
day=$(TZ=America/New_York date +%F)
out=$(mktemp)
# Everything goes to $out, the issue's body if the run fails; the journal gets it at the end.
exec 3>&1 >>"$out" 2>&1
trap 'cat "$out" >&3; rm -f "$out"' EXIT

report() {
    printf 'Release-day job failed: %s\n' "$1"
    gh issue create -R "$repo" --title "Release-day job failed on $day" --body-file "$out"
    exit 1
}

git -C "$main_checkout" fetch -q origin || report "git fetch"
if [ ! -d "$job_tree" ]; then
    git -C "$main_checkout" worktree add -q --detach "$job_tree" origin/main ||
        report "git worktree add"
fi
git -C "$job_tree" switch -q --detach origin/main || report "git switch in $job_tree"

FT_DB_PATH="$main_checkout/data/fortuneteller.duckdb" \
    FT_CACHE_DIR="$main_checkout/data/cache" \
    FT_CALLS_PATH="$job_tree/data/calls.csv" \
    uv run --directory "$job_tree" fortuneteller live
live=$?

if ! git -C "$job_tree" diff --quiet -- data/calls.csv; then
    flows=$(git -C "$job_tree" diff -U0 -- data/calls.csv | grep '^+[0-9]' | cut -d, -f2 |
        sort -u | paste -sd-)
    branch="calls-$flows-$day"
    git -C "$job_tree" switch -q -c "$branch" &&
        git -C "$job_tree" commit -q -m "Log the live $flows call of $day" -- data/calls.csv &&
        git -C "$job_tree" -c credential.helper= -c credential.helper='!gh auth git-credential' \
            push -q "https://github.com/$repo.git" "$branch" &&
        gh pr create -R "$repo" --base main --head "$branch" \
            --title "Log the live $flows call of $day" \
            --body "Logged by the release-day job at $(date -u +%H:%M:%SZ); graded by \`score\` after the closes." ||
        report "committing, pushing or opening the pull request for $branch"
fi
[ "$live" -eq 0 ] || report "fortuneteller live exited $live"
