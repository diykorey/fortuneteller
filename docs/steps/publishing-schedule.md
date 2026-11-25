# The publishing schedule

> Step 58 of the [Roadmap](../roadmap.md). The owner's choices of 2026-11-24: guesses drafted at
> 14:00 New York, a reminder at 16:00 if not approved, published at 18:00 as they stand, every
> day; the draft printed both by a `fortuneteller approve` command after a desktop notification
> and in the session when one is open
> ([why](../decisions.md#2026-11-24-the-jobs-share-the-store-polymarket-after-the-gate-the-draft-printed-both-ways-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *front page*, *front pull request*, *our guess*,
> *made*, *shown*, *staying card*, *evening score*. Amendments below are dated 2026-11-25.

## The goal

**In plain words:** the day's guesses reach the page every day at the same hour, whether or not
the owner had time to look; the owner gets four hours to reword or remove them first, and a
reminder halfway.

At the end: each day at 14:00 New York the job writes the day's guesses and opens the front pull
request, and the laptop shows a notification; `fortuneteller approve` prints every card in full
and merges on a yes; at 16:00, if it is still open, a second notification; at 18:00 the evening
run merges it as it stands. Today the guesses are written at 18:00 and wait for the owner without
end: 2026-11-24's front pull request (#458) was published 7 hours after the job opened it, and
2026-11-23's (#434) never was, replaced by the next evening's.

## The way to reach it

- **One evening run, every day, not a second unit at 18:00.** The evening score already runs at
  18:00 in the job's tree, under the lock it shares with the morning, and switches that tree to
  `main`; a publishing unit beside it would race it. So the evening run publishes, at its end, and
  runs every day, whole: on Saturday and Sunday its loads find no new close and `score` no row to
  grade, and it writes the pages and publishes. Nothing in it depends on the day of the week but
  the morning's check, which already skips weekends.
- **Which command runs when:**

  | Hour, New York | Run | Does |
  | --- | --- | --- |
  | 14:00, daily | `release-day.sh draft` (new) | `guess` (both guessers, moved from the evening), then `fortuneteller draft` (new): marks the guesses found on the published page as *shown*, and proposes the front page's guesses beside the stated forecasts the published page carries (its embedded `stated`, written by last evening's run); the front pull request opened as today; a notification |
  | 16:00, daily | `release-day.sh remind` (new) | a notification if the day's front pull request is open |
  | 18:00, daily | `release-day.sh score` | as today, without `guess` and without opening a front pull request; then the day's front pull request merged under the rule below |

- **Guesses start one close earlier.** A guess starts from its market's first close after it is
  *made*. Made at 14:00, a guess on a market still open (US stocks, yields, the dollar) starts from
  that day's close, not the next day's as at 18:00; markets already closed (Tokyo, Europe) are
  unchanged. Its span and base rate are computed as before from that start. Both guessers move
  together, so step 55's comparison of the two is untouched; its refining period runs to
  2027-01-31 and the frozen period starts after, so the change falls inside refining.
- **Weekend guesses count apart.** A guess made on Saturday or Sunday at 14:00 starts from
  Monday's close on nearly every market (bitcoin and ether too, until step 59), so both days' are
  one start, not two tries. They are made, shown and graded, and left out of the record by
  evening (`guess_record`, an evening's guesses one try, [step 50](guess-ledger.md)) and of both
  of step 55's counts (`excess_record`, `counted_guesses`), which this amends.
- **The merge at 18:00.** The evening merges the day's front pull request when: it was opened at
  least 3 hours before (on time, 4); every commit on it is by the repository owner's account,
  under which both the job and the owner commit; and its checks pass, waited for as the score's
  pull request's are. Otherwise it stays open and is named in the evening's output. A draft too
  young waits for the next evening. The next 14:00 draft closes an earlier front pull request that
  holds only the job's commit, as today, and proposes afresh, so a draft never published is
  replaced, not lost: only shown guesses stay. This amends [front staging](front-staging.md)'s
  *the job never merges it*.
- **A late wake does not publish unseen.** The timers keep `Persistent=true`: a laptop asleep at
  14:00 drafts when it wakes, and the 3-hour rule keeps an evening that wakes with it from
  publishing at once; the lock runs the two one after the other.
- **Printed both ways.** `fortuneteller approve` prints each card in full (market, direction, the
  last day, the statement, the reasoning, the source, and *withdrawn* where set), then asks; *yes*
  merges exactly the commit printed, and only with its checks passed. `approve --print` prints
  without asking, for a session to show the owner and run `approve --yes` on the owner's word.
- **`approve` runs where the owner types it.** On 2026-11-25 a command run in the main checkout
  stopped before starting: the checkout's `.env` holds keys of other tools, and the settings
  refuse unknown keys. The settings are changed to ignore keys they do not know.

## The rule, fixed before anything is shown

This step measures nothing; it changes when the guesses are written and who merges them. Written
2026-11-25, before building.

- **Expected outcome:** on the first weekday and the first Saturday after the units are installed,
  a front pull request opened between 14:00 and 14:30 New York with a notification; a second
  notification at 16:00 only if it was still open; at 18:00 it merged as it stood, or merged
  earlier by `approve`; the page showing it by 18:30. On the weekday the score graded as before;
  on the Saturday no row graded and the pages written.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | `fortuneteller draft` and `release-day.sh draft` | Tests: on the same files, the proposal from the page's `stated` equals the one `scoreboard` made before this step; against a scratch repository the script opens one front pull request and sends one notification, and with an open one the owner added to, opens none |
| 3 | `fortuneteller approve` | Tests: every field above printed for each card; *yes* merges the printed commit; anything else, failing checks, or a commit added after printing leave it open; none open says so. Run from the main checkout with its `.env`: exit 0, the cards printed |
| 4 | The evening publishes, every day | Tests against a scratch repository: a draft 3 hours old merged; one 2 hours old left; one with another account's commit left. Tests: a Saturday's and a Sunday's guesses in no evening's try and in neither of step 55's counts; a Friday's still counted |
| 5 | The units | Draft and remind timers daily at 14:00 and 16:00 New York, the evening daily; installed and reloaded; each notification seen on the screen when its timer ran the unit, the times written in Results |
| 6 | Results here | The expected outcome marked right or wrong, day by day |

## How you know it is right

- **A merge the owner did not get time for would show in a test:** the 2-hour draft is left open.
- **A notification sent only from a shell would show at step 5:** it must come from the timer's
  run, whose environment differs.
- **The proposal moved to 14:00 must not change what it proposes:** step 2 compares it with the
  one made before this step on the same files.
- **Nothing graded changes:** the evening's `score` output on a weekday equals the one made before
  this step for the same calls.

## What this step does not do

It does not change which guesses are shown (step 61), move the jobs off the laptop (step 21), or
keep the crypto weekend closes (step 59).

## Technical details

- **Code:** `__main__.py` (`draft`, `approve`, the proposal taken out of `stated_forecasts`, the
  weekend rows in `guess_record`, `excess_record` and `counted_guesses`); `config.py` (unknown
  keys ignored); `scripts/release-day.sh` (`draft`, `remind`, the evening's merge);
  `scripts/systemd/` (two units and timers, the evening timer daily); the notification sent with
  `notify-send`, the unit given the desktop session's message bus address
  (`DBUS_SESSION_BUS_ADDRESS`), which a timer's run lacks.
- **Docs:** this spec; amendments in [front staging](front-staging.md),
  [evening score](evening-score.md), [step 50](guess-ledger.md) and
  [step 55](guesses-vs-base-rate.md); the glossary; status; the changelog; roadmap row 58.

## Results

Not yet measured.
