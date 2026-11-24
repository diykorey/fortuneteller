#!/usr/bin/env bash
# Starts the release-day job (docs/steps/release-day-job.md) from its own worktree's script at
# origin/main, never from the development checkout, whatever branch or edit that holds (step 57,
# R5, docs/steps/technical-fixes.md). The script is copied out under the job's lock first: the job
# switches its worktree while it runs, and bash reads a script as it goes.
set -u
tree=${FT_JOB_TREE:?the worktree the job works in}
script=$(mktemp)
flock "$tree.lock" bash -c '
    git -C "$1" fetch -q origin && git -C "$1" switch -q --discard-changes --detach origin/main
    cp "$1/scripts/release-day.sh" "$2"' _ "$tree" "$script" 2>/dev/null ||
    cp "$(dirname "$0")/release-day.sh" "$script"
bash "$script" "$@"
status=$?
rm -f "$script"
exit "$status"
