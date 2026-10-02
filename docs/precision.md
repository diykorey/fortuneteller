# Precision

Every measurement in the MVP takes the simplest version that can still answer its question. This
document lists each of those choices: what we do now, the more precise way, what the precise way
would cost, and what would make it worth doing.

The rule for reading it: **a simplification here is not a bug.** It is a known limit, chosen on
purpose. It becomes work only when its trigger fires — usually when a result is close enough to the
line that the simplification could have decided it.

## Step 3 — the baseline for "ordinary days"

Step 3 asks whether the five instruments move more on CPI days than on ordinary days. The answer
depends on what "ordinary" means.

| | Option | Ordinary days are | Cost |
| --- | --- | --- | --- |
| **Now** | A. All other days | Every trading day that is not a CPI release day | None: the data is already stored |
| Better | B. Other releases removed | As A, minus jobs-report (NFP) and Fed-decision (FOMC) days | Two more release calendars to load and check |
| Better | C. Matched window | The 20 trading days around each release, without the release day | None in data; a different comparison per release |

**Why A is enough for now.** Jobs-report and Fed days are noisy, and A leaves them in the ordinary
pile. That raises the baseline, so the CPI effect A reports is **smaller than the true effect,
never larger**. If CPI days still stand out against it, they stand out. A can produce a false "no
effect", never a false "effect".

**What B fixes.** It compares CPI days with genuinely quiet days. That matters most for UST 10Y and
DXY, which also react strongly to jobs reports and Fed decisions. NFP falls on a Friday about one
week before CPI, so the two rarely share a day; FOMC days can. B is the natural first piece of
ladder rung 1 (more events), which loads those calendars anyway.

**What C fixes.** Markets have loud and quiet years: 2008 and 2022 move more on every day. A pools
all years into one baseline, so a release in a loud year is judged against a mostly quiet baseline.
C judges each release only against its own neighbourhood, which removes that. Step 3 partly covers
this by splitting the results by era.

**Trigger.** Do B or C if an instrument's step 3 result sits near the line between "moves" and
"doesn't" — then the baseline choice could be what decided it.

## Step 3 — the test for "moves"

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Decision rule | One ratio of medians and its permutation `p`; a fixed bar (1.10, 0.01) | A confidence interval on the ratio, so the output says how large the effect could plausibly be, not only whether it passed | An instrument comes out *unclear* |
| Coarse old yields | `^TNX` closes before 1990 are rounded to whole basis points, so many daily moves tie and the 1970–1989 UST ratio moves in coarse steps | A finer source for those years; FRED's `DGS10` is identical, so none free is known | The 1970–1989 UST era row matters to a conclusion |
| Loud and quiet years | All years pooled; eras shown as context | A model of each day's expected volatility (e.g. GARCH), so each CPI day is judged against how loud its own market was | Era ratios disagree with the verdict, e.g. *moves* overall but near 1.00 recently |

## Steps 1–2 — choices already built in

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Measuring window | Close-to-close: last close before the release to first close on or after it. The move includes everything else that happened that day. | Intraday: the price at 08:25 and 09:00 New York time, so only the release is in the window. Needs paid tick or minute data. | Step 4 finds a relationship but the scatter is too wide to use |
| Release time | 08:30 New York time for every release | The time each release was actually published; older ones may not all have been at 08:30 (not checked) | Intraday data arrives (the daily window doesn't depend on the time) |
| Release dates | From FRED. Checked against BLS from 1990; 1972–1989 unchecked | Every date checked against BLS's printed schedules | Any result that depends on the 1970s–80s |
| Gold | `GC=F`, Yahoo's continuous front-month futures; its price can jump on a roll day | Spot gold (XAU), or a series adjusted for the roll | A large gold move on a CPI day turns out to be a roll |
| S&P 500 | `^GSPC`, the index | `SPY` or `ES` itself, the instruments a user would trade | A user needs the traded instrument's number |
| UST 10Y | `^TNX`, the 10-year yield; a median 0.2 bp from FRED's DGS10 | `ZN` futures, the traded instrument | Same as above |
| Gap rule | A release is skipped if no close lies within 4 days on either side | Skip none: find each instrument's real trading calendar | Skips become more than a handful |

## Adding to this document

When a step chooses the simple way over a more precise one, add a row here in the same change, with
its trigger. When a trigger fires and the precise way is built, delete the row.
