# The publishing schedule

> Step 58 of the [Roadmap](../roadmap.md). The owner's choices of 2026-11-24: guesses drafted at
> 14:00 New York, a reminder at 16:00 if not approved, published at 18:00 as they stand, every
> day; the draft printed both by a `fortuneteller approve` command after a desktop notification
> and in the session when one is open
> ([why](../decisions.md#2026-11-24-the-jobs-share-the-store-polymarket-after-the-gate-the-draft-printed-both-ways-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *front page*, *front pull request*, *our guess*,
> *staying card*, *evening score*.

## The goal

**In plain words:** the day's guesses reach the page every day at the same hour, whether or not
the owner had time to look; the owner gets four hours to reword or remove them first, and two
reminders.

At the end: each day at 14:00 New York the job writes the day's guesses and opens the front pull
request, and the laptop shows a notification; `fortuneteller approve` prints every card in full
and merges on a yes; at 16:00, if it is still open, a second notification; at 18:00 the evening
run merges it as it stands. Today the guesses are written at 18:00 and wait for the owner without
end (on 2026-11-23 and 24 a day each).

## The way to reach it

- **One evening run, every day, not a second unit at 18:00.** The evening score already runs at
  18:00 in the job's tree, under the lock it shares with the morning, and switches that tree to
  `main`; a publishing unit beside it would race it. So the evening run publishes, at its end, and
  runs every day: on Saturday and Sunday it skips the loads, `score` and `triggers` (no close to
  grade) and still writes the pages and publishes.
- **Which command runs when:**

  | Hour, New York | Run | Does |
  | --- | --- | --- |
  | 14:00, daily | `release-day.sh draft` (new) | `guess` (both guessers, moved from the evening), then `fortuneteller draft` (new): `mark_shown` and the proposal from the stated forecasts on the published page; the front pull request opened as today; a notification |
  | 16:00, daily | `release-day.sh remind` (new) | a notification if the day's front pull request is open |
  | 18:00, daily | `release-day.sh score` | as today, without `guess` and without opening a front pull request; then the day's front pull request merged if its checks pass and the draft is old enough |

- **A late wake does not publish unseen.** The timers keep `Persistent=true`, so a laptop asleep
  at 14:00 runs the draft when it wakes, and one asleep at 18:00 runs the evening then. The
  evening merges a front pull request only when it was opened at least 3 hours before; a younger
  one waits for the next evening. The lock runs a draft and an evening that wake together one
  after the other.
- **The job merges what it drafted, as the owner left it.** A front pull request with the owner's
  commits is merged with them; one with a commit by anyone else, or with failing checks, is left
  open and named in the evening's output. This amends [front staging](front-staging.md)'s *the
  job never merges it*, with this date.
- **Weekend guesses count apart.** On Saturday and Sunday nearly every market's guess starts from
  Monday's close, as Friday evening's do (bitcoin's and ether's too, until step 59), so a weekend's
  guesses are not new tries. They are made, shown and graded, and left out of the per-evening
  record and of [step 55](guesses-vs-base-rate.md)'s comparison, which this amends with this
  date.
- **`approve` runs where the owner types it.** The main checkout's `.env` holds keys of other
  tools, and the settings refuse them (2026-11-25); the settings ignore keys they do not know.

## The rule, fixed before anything is shown

This step measures nothing; it changes when the guesses are written and who merges them. Written
2026-11-25, before building.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | `fortuneteller draft` and `release-day.sh draft` | Tests: the proposal from the page's stated forecasts equals the evening's on the same files; the script run against a scratch repository opens one front pull request and sends one notification, and with an open one the owner added to, opens none |
| 3 | `fortuneteller approve` | Tests: every card printed in full; *yes* merges, anything else leaves it open; no front pull request open says so. Run from the main checkout with its `.env` |
| 4 | The evening publishes, every day | Tests, against a scratch repository: a draft 3 hours old merged; one 2 hours old left; one with another's commit left; on a Saturday no load, `score` or `guess`, the pages written. Weekend rows left out of the per-evening record and step 55's comparison |
| 5 | The units | Draft and remind timers daily at 14:00 and 16:00 New York, the evening daily; installed and reloaded; the notifications seen when the timers ran the units, not from a shell |
| 6 | The first two days, Results here | A weekday and a weekend day read: the draft, the notifications, the merge at 18:00 or the owner's approval |

## How you know it is right

- **A merge the owner did not get time for would show in a test:** the 2-hour draft is left open.
- **A notification sent only from a shell would show at step 5:** it must come from the timer's run,
  whose environment differs.
- **The proposal moved to 14:00 must not change what it proposes:** step 2 compares it with the
  evening's on the same files.
- **Nothing graded changes:** the evening's `score` output on a weekday equals today's for the
  same calls.

## What this step does not do

It does not change which guesses are made or shown (step 61), move the jobs off the laptop
(step 21), or keep the crypto weekend closes (step 59).

## Technical details

- **Code:** `__main__.py` (`draft`, `approve`, the proposal taken out of `stated_forecasts`, the
  weekend rows in `guess_record` and `excess_record`); `config.py` (unknown keys ignored);
  `scripts/release-day.sh` (`draft`, `remind`, the evening's merge and weekend path);
  `scripts/systemd/` (two units and timers, the evening timer daily); the notification with
  `notify-send`, the unit given the session's bus.
- **Docs:** this spec; dated amendments in [front staging](front-staging.md),
  [evening score](evening-score.md) and [step 55](guesses-vs-base-rate.md); the glossary; status;
  the changelog; roadmap row 58.

## Results

Not yet measured.
