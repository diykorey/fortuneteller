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
# FRED's key alone, for the Fed's group and home prices (docs/steps/stated-forecasts.md); the
# rest of .env stays out of the job's environment.
FT_FRED_API_KEY=$(sed -n 's/^FT_FRED_API_KEY=//p' "$main_checkout/.env" 2>/dev/null | head -1)
export FT_FRED_API_KEY

# Commits $files as $1 on branch $2 and opens its pull request with body $3. A run repeated on
# the same day, after a failed push or a morning catch-up, finds the branch the first run made:
# -C resets it rather than refusing it (the 2026-10-22 evening failed so, issue #172).
open_pr() {
    # shellcheck disable=SC2086
    git -C "$job_tree" switch -q -C "$2" &&
        git -C "$job_tree" add -- $files &&
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

# Waits for the checks on the pull request of branch $1; true when they all pass. Checks may not be
# reported yet on a pull request opened seconds ago, so it is asked three times.
checks_pass() {
    for _ in 1 2 3; do
        sleep 30
        if timeout 1200 gh pr checks -R "$repo" "$1" --watch --fail-fast --interval 30 >/dev/null; then
            return 0
        fi
    done
    return 1
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
            "$(grep -E ': actual |^.{12} (up|down|—) |^no prediction: |^trigger: ' "$out")
$kept"
    fi
    # A statement later today pops up on its own, also on a day with no call (scheduled-statements.md).
    previews=$(grep '^preview: ' "$out" | sed 's/^preview: //')
    [ -z "$previews" ] || popup "A statement today, $day" "$previews"
    [ "$live" -eq 0 ] || report "fortuneteller live exited $live"
    exit 0
fi

# The laptop's evening watches the runner's morning (docs/steps/loop-nets.md): no run started on
# demand from 11:00 to 17:00 UTC today opens an issue. Only an evening run on its own weekday,
# past 13:00 New York when that window has closed, checks; a catch-up after midnight carries the
# next day, whose morning may be ahead, and skips it. It never fails the evening.
watch_morning() {
    [ "$(TZ=America/New_York date +%u)" -le 5 ] && [ "$(TZ=America/New_York date +%H)" -ge 13 ] &&
        [ "$(TZ=America/New_York date +%F)" = "$day" ] || return 0
    local runs missing
    runs=$(mktemp)
    if gh run list -R "$repo" -w jobs.yml --json createdAt,event -L 50 >"$runs"; then
        missing=$(uv run --directory "$job_tree" fortuneteller unstarted --morning "$day" "$runs")
        if [ -n "$missing" ]; then
            printf '%s\n' "$missing"
            gh issue create -R "$repo" --title "The runner's morning was not started on $day" \
                --body "$missing" || echo "the issue could not be opened"
        fi
    else
        echo "gh run list failed; the runner's morning is not checked"
    fi
    rm -f "$runs"
}

file=data/score.txt
waiting=$(gh pr list -R "$repo" --state open --json headRefName \
    --jq '.[].headRefName | select(startswith("calls-") or startswith("score-") or startswith("triggers-") or startswith("scoreboard-"))') ||
    report "gh pr list"
if [ -n "$waiting" ]; then
    printf 'score: waiting for %s to be merged\n' "$waiting"
    watch_morning
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
    watch_morning
    exit 0
fi
# The owner's triggers (docs/steps/trigger-file.md) are answered and graded; their log goes into
# the score's pull request, or a pull request of its own when the score did not change.
uv run --directory "$job_tree" fortuneteller triggers || report "fortuneteller triggers exited $?"
log=data/trigger-log.csv
log_changed=$(git -C "$job_tree" status --porcelain -- "$log")
if ! git -C "$job_tree" diff --quiet -- "$file"; then
    # The scoreboard (docs/steps/scoreboard.md) is rewritten into the same pull request.
    uv run --directory "$job_tree" fortuneteller guess || true
    FT_CALLS_PATH=data/calls.csv uv run --directory "$job_tree" fortuneteller scoreboard ||
        report "fortuneteller scoreboard exited $?"
    files="$file docs/scoreboard docs/predicts"
    [ -z "$log_changed" ] || files="$files $log"
    open_pr "Score the calls on $day" "score-$day" \
        "Graded by the evening score at $(date -u +%H:%M:%SZ), after the closes."
    # Every row is graded (a pending row stops above), so the pull request is merged once its
    # checks pass (the owner, 2026-11-20, docs/decisions.md): the runner's evening then finds
    # nothing to wait on. A check that fails leaves it for a person.
    if checks_pass "score-$day"; then
        merge_pr "score-$day"
    else
        echo "score: checks did not pass; score-$day left open for review"
    fi
else
    # With nothing to score the page is still written (docs/steps/readers.md), so the Dow's
    # reports ahead on it stay current; it goes with the triggers' log when that changed.
    uv run --directory "$job_tree" fortuneteller guess || true
    FT_CALLS_PATH=data/calls.csv uv run --directory "$job_tree" fortuneteller scoreboard ||
        report "fortuneteller scoreboard exited $?"
    page_changed=$(git -C "$job_tree" status --porcelain -- docs/scoreboard docs/predicts)
    # The pages, the guess ledger among them, go in a pull request merged on passing checks; the
    # triggers' log in one of its own that waits for a person, so the evening's guesses never wait
    # with it (step 57, R11, docs/steps/technical-fixes.md; #433 held them on 2026-11-23).
    if [ -n "$page_changed" ]; then
        files="docs/scoreboard docs/predicts"
        open_pr "Write the page on $day" "scoreboard-$day" \
            "Written by the evening score at $(date -u +%H:%M:%SZ), with nothing to score."
        if checks_pass "scoreboard-$day"; then
            merge_pr "scoreboard-$day"
        else
            echo "score: checks did not pass; scoreboard-$day left open for review"
        fi
    fi
    if [ -n "$log_changed" ]; then
        git -C "$job_tree" switch -q --detach origin/main || report "git switch for the triggers"
        files=$log
        open_pr "Grade the triggers on $day" "triggers-$day" \
            "Answered and graded by the evening score at $(date -u +%H:%M:%SZ), after the closes."
    fi
fi

# The front page's guesses wait for the owner (docs/steps/front-staging.md): tonight's proposal,
# written into the evening's pull request as front-next.csv, goes from a fresh main into a pull
# request of its own that the job never merges. An earlier one is closed when it holds only the
# job's commit; one the owner or anyone else has added to is left open and tonight proposes nothing.
# Tonight's proposal is kept aside first: front-next.csv is tracked, so the switch to main puts back
# main's copy, which is an earlier evening's when tonight's pull request is not merged (2026-11-23,
# docs/steps/honest-page.md).
proposal=$(mktemp)
cp "$job_tree/docs/predicts/front-next.csv" "$proposal" 2>/dev/null
if git -C "$job_tree" fetch -q origin && git -C "$job_tree" switch -q --detach origin/main; then
    [ -s "$proposal" ] && cp "$proposal" "$job_tree/docs/predicts/front.csv"
    if ! git -C "$job_tree" diff --quiet -- docs/predicts/front.csv; then
        busy=
        for old in $(gh pr list -R "$repo" --state open --json headRefName \
            --jq '.[].headRefName | select(startswith("front-"))'); do
            if [ "$(git -C "$job_tree" rev-list --count "origin/main..origin/$old" 2>/dev/null)" = 1 ]; then
                gh pr close -R "$repo" --delete-branch "$old" || busy=1
            else
                busy=1
            fi
        done
        if [ -n "$busy" ]; then
            git -C "$job_tree" checkout -q -- docs/predicts/front.csv
            echo "front: an earlier front pull request was added to; tonight proposes nothing"
        else
            files=docs/predicts/front.csv
            open_pr "The front page's guesses, $day" "front-$day" \
                "Tonight's proposal for the front page's guesses. Reword \`statement\` or \`why\`, or delete a row; the other columns are locked. Merging publishes it; the job never merges it."
        fi
    fi
else
    report "fetching main for the front page's guesses"
fi
rm -f "$proposal"
watch_morning
