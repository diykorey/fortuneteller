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
| Was | A. All other days | Every trading day that is not a CPI release day | None: the data is already stored |
| **Now** | B. Other releases removed | As A, minus every stored event's reaction day: jobs reports (NFP) and Fed decisions (FOMC) | Built in rung 1, sub-step 6. It moved no CPI verdict; every ratio rose by 0.02–0.08 |
| Better | C. Matched window | The 20 trading days around each release, without the release day | None in data; a different comparison per release |

**Why A was enough for the MVP.** Jobs-report and Fed days are noisy, and A leaves them in the ordinary
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
| Years inside the span | Ordinary days from the flow's first reaction day on each market ([own years](steps/own-years-baseline.md), built 2026-10-30), every year inside that span pooled | Ordinary days weighted to match each year's share of the flow's days, or a model of each day's expected volatility (e.g. GARCH) | A flow whose days bunch in its last years, with era ratios that disagree with its verdict. *Fired 2026-11-02* ([own years](steps/own-years-baseline.md#results)) on one cell, the ECB president's Brent: 1.28 overall, 1.09 since 2020, where 219 of its 332 days fall. Left for now: a lesser flow, no call; weighting when a lead flow's cell or a call fires it |

## Step 4 — the expected value and the surprise

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Computed baseline | Average of the previous 12 first-published core m/m: a plain trend | **A fitted forecasting model** (e.g. autoregressive, AR), which forecasts each month better and so leaves a truer surprise | Only `trend_12m` *tracks*, or the two baselines disagree |
| Market expectation | Cleveland Fed nowcast: a model, 2013 on. **For core it is almost exactly the 12-month trend** (median gap 0.003 pp, correlation 0.997, measured 2026-10-05): its information is oil and gasoline prices, which move headline, not core. So for core it is not an independent check on the trend; for headline it is (correlation 0.46) | Economists' survey consensus (Bloomberg, Reuters), what the market actually priced; paid | The nowcast result sits near the line, or a free consensus history turns up |
| Core before 1997 | No core verdict before 1997: FRED's first-release core starts then | Earlier first-published core from BLS's printed releases | A conclusion needs the 1970s–90s |
| Hit-rate cut-off | Surprises of at least 0.1 pp count; smaller ones are noise | A cut-off scaled to each era's typical surprise | Hit rate rests on fewer than 50 releases |

## Rung 1 — more events

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Fed surprise | None: the Fed gets step 3 only, because no free history of what the market expected exists | The change implied by Fed funds futures the day before each decision (the standard measure); paid | Fed decisions turn out to move markets in step 3 |
| Fed decision time | Each statement's time from a source; 2005 to mid-2006 assumed 14:15 (the minutes give none; 14:15 either side); 2007-08-10 and 2007-08-17 known only as "morning" | The exact minute for those | Only the side of each close matters, and all of them are on a known side |
| Close times | Each instrument's close in New York, measured on 2026-09 data (S&P 500 16:00, yield 15:00, dollar 15:00, gold 13:30, VIX 16:15), Europe's on 2026-10-15 to 20 and the nine more outcomes' on 2026-10-19 to 26, and assumed for all history | Each exchange's close time by era | In 1990–2007 the yield's and the dollar's next-day move beats their Fed-day move (0.97 vs 1.32, 0.84 vs 1.15): either their close came before 14:15 then, or the reaction runs into the next day. Daily data cannot tell which |
| NFP hit-rate cut-off | Surprises of at least 50k count | A cut-off scaled to each era's typical surprise | Hit rate rests on fewer than 50 releases |
| NFP expected value | The 12-month trend of first-published payroll changes, as for CPI | Economists' consensus (paid), or a model that uses the weekly jobless claims and the ADP report published before each release | The yield and the dollar rank-correlate at p 0.0001 but miss the 60% hit-rate bar (58%, 56%): a truer expected value may decide them |

## Step 8 — scheduled statements

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Whose statement | The calendar's title naming the holder in office that day (a term table in `flows`); another speaker, a press conference or a title naming nobody is left out | The Fed's and the ECB's own speech and testimony lists, which name the speaker | A statement the calendar titles without a name, or a new holder the table lacks |
| Statement time | The time the calendar lists, not checked; one a day, the earliest | The time the text was released, from the central bank's own page | A statement near a close, where the side of the close decides its day |

## Step 10 — dated shocks: elections

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Too few | A cell under ten event days has no verdict ([elections](steps/elections.md)); chosen, not derived | A minimum from the test's power: the fewest days at which a ratio of 1.5 reaches p < 0.01 | A cell at ten to fifteen days whose verdict decides a finding |
| Over a week | Five-day moves from the close before each day; an event's window against every window that starts on an ordinary day. Windows overlap, so neighbouring ordinary windows share four days and `p` is optimistic | Non-overlapping windows, or a block permutation | A week verdict at a `p` near 0.01 |
| Result time | The polls' close, written by hand; a result known later (a close race, a count overnight) still reacts the next day, and one known sooner from exit polls the same | The hour each result was called, from news archives | A vote whose result came more than a trading day after the polls closed |

## Step 10 — dated shocks: tariff actions

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Signing time | Every signing at 20:00 New York, after every market's close, reacting on each market's next close ([tariff actions](steps/tariffs.md)): the Federal Register gives the day, not the hour. A signing in the session (the 2025-04-09 pause, announced at 13:18) is measured a day late | The hour of each signing or announcement, from the White House's own record | A day the market moved on a signing it is measured after |
| The signing, not the announcement | The document's signing day; an announcement before it (steel, 2018-03-01, signed 2018-03-08), a post (2019-05-05, 2019-08-01) and USTR's own Section 301 lists are not events | A second, mechanical source for announcements, chosen before measuring | A results finding that hangs on a tariff day the signings miss |
| Clustered signings | 2025's signings sit days apart (2025-03-02, 03-03, 03-06), so their week windows overlap each other as well as the ordinary ones, on top of the overlap elections already note | One event per cluster, or a block permutation | A week verdict at a `p` near 0.01 |

## Step 10 — dated shocks: the debt limit

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Vote time | The final congressional vote's day and roll-call time since 2005; before it 20:00 New York on the day the Congressional Record gives ([the debt limit](steps/debt-limit.md)). A deal announced before the vote (2011-07-31, 2023-05-27) is not an event | Roll-call times before 2005, from the Congressional Record | A finding that hangs on a pre-2005 law whose vote came in market hours |
| Riders | A law whose limit change rides in a broader act (`vehicle` `rider`, 25 of 75) is measured with the rest of its act; a check repeats the test on `debt` laws alone | The broader act's own dates as a separate flow | A *moves* that the debt-only check does not keep |
| Clustered votes | Five stopgaps signed in October 1990, and runs in 1980 and 1987, sit days apart, so their week windows overlap each other | One event per cluster | A week verdict at a `p` near 0.01 |

## Step 10 — dated shocks: summits

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Summit time | No source gives the hour: 08:00 New York for a weekday last day in Europe or Asia, 20:00 for a weekend or a summit in the Americas ([summits](steps/summits.md)). A text issued before the last day is measured on the last day | Each communiqué's release hour, from the presidency's own record | A *moves* that the other-day check reverses |
| Shared weeks | Muskoka and Toronto (2010) are two events with one reaction day; a G7 and a G20 within a week of each other overlap their week windows | One event per pair | A week verdict at a `p` near 0.01 |

## Step 11 — news as a feed: the president's trade posts

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| The source | The president's own tweets, first term; GDELT is not used: its article counts follow the market, it names no speaker and has no trade topic ([the president's trade posts](steps/presidential-posts.md)) | GDELT's article search as a cross-check of when coverage started | A finding that hangs on coverage, not on the tweet |
| The keyword rule | `tariff`, `trade war` or `trade deal` in the tweet's own text, retweets and quotes out; catches deals with no tariff | A reading of each tweet's meaning, a language model's job (rung 7) | A *moves* the rate-naming check does not keep |
| First tweet only | A day is timed at its first matching tweet; a later one after the close is dropped (7 S&P 500 reaction days, 5%) | Every tweet's own reaction day | The dropped share above 10% |
| The term's end | Ordinary days end at 2021-01-08 (`ordinary_until`); week windows from 2021-01-05 reach past it | Week windows that end by the bound | A week verdict at a `p` near 0.01 |
| Part 2's source | A snapshot of CNN's Truth Social archive of 2026-11-03, md5-pinned, not committed; a fetch the same day rebuilt the seed with no difference; posts deleted before it are missing, where part 1 kept deleted tweets ([part 2](steps/presidential-posts-2.md)) | A committed or archived copy | A seed that a later fetch does not rebuild |
| Part 2's text-only rule | 4,923 posts in the window have no text once links are removed (images, videos, links) and are out, so an image-only announcement is missed | Reading the image's text | A *moves* that hangs on announcement days |
| Part 2's first post only | Later posts after the close add 8 S&P 500 reaction days (4%) | Every post's own reaction day | The dropped share above 10% |
| Part 2's week | Posts react on about 40% of closes, so 83% of the S&P 500's ordinary week windows hold one; the week is context, not graded; windows from 2026-10-27 reach past 2026-10-30 | A week test on a sparser flow | Never for this flow |

## Step 12 — beat the fortune teller

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| The witness | GitHub's `merged_at` for the pull request whose merge commit added the guess file, found along `main`'s first parents; a commit's own committer and date are not trusted | A signed, timestamped guess outside GitHub | A dispute over a guess's time |
| The owner's merge | Only the owner can merge, so a guess counts only if merged before 08:30 New York; the page lists guess pull requests not merged in time | Merging guess pull requests automatically before the release | A guess pull request left unmerged in time |
| Merge method | Merge commit or squash; with a rebase merge GitHub's merge commit is the pull request's last commit, so a guess counts only if that commit added the file | Matching any commit the pull request brought in | A rebased guess pull request |
| The handle | Chosen by the player, unchecked: one person can play under two | The pull request author's GitHub login | A handle whose record looks hedged |

## Steps 1–2 — choices already built in

| Choice | Now | More precise | Trigger |
| --- | --- | --- | --- |
| Measuring window | Close-to-close: last close before the release to first close on or after it. The move includes everything else that happened that day. | Intraday: the price at 08:25 and 09:00 New York time, so only the release is in the window. Needs paid tick or minute data. | Step 4 finds a relationship but the scatter is too wide to use |
| Release time | 08:30 New York time for every release | The time each release was actually published; older ones may not all have been at 08:30 (not checked) | Intraday data arrives (the daily window doesn't depend on the time) |
| Release dates | From FRED. Checked against BLS from 1990; 1972–1989 unchecked | Every date checked against BLS's printed schedules | Any result that depends on the 1970s–80s |
| Gold | `GC=F`, Yahoo's continuous front-month futures; its price can jump on a roll day | Keep `GC=F` and cross-check it against spot gold (XAU), as `^TNX` is checked against `DGS10`: where the two disagree on a CPI day, that move is a roll. Replacing `GC=F` would lose its history and add nothing the cross-check doesn't | A large gold move on a CPI day looks like a roll |
| Brent | `BZ=F`, Yahoo's continuous front-month futures at the 14:30 New York settlement; it can jump on a roll day as gold's does | Dated Brent, or the cross-check gold has | A large oil move on a release day looks like a roll |
| EUR/USD | `EURUSD=X`, whose daily close Yahoo takes at 00:00 London of the bar's own day (checked 2026-10-19 to 26 against 5-minute bars), so the first bar after a US release is the next London day's and the move spans 24 hours | A 17:00 New York close, from euro futures (`6E=F`) or paid FX data | A euro verdict that disagrees with the dollar index's |
| Bitcoin | `BTC-USD`'s UTC day; its weekend bars are dropped as every market's are, so a Monday move spans the weekend | Keep the weekend bars for the one market that trades through it | A Friday release whose bitcoin move matters |
| S&P 500 | `^GSPC`, the index | `SPY` or `ES` itself, the instruments a user would trade | A user needs the traded instrument's number |
| UST 10Y | `^TNX`, the 10-year yield; a median 0.2 bp from FRED's DGS10 | `ZN` futures, the traded instrument | Same as above |
| Gap rule | A release is skipped if no close lies within 4 days on either side | Skip none: find each instrument's real trading calendar | Skips become more than a handful |

## Adding to this document

When a step chooses the simple way over a more precise one, add a row here in the same change, with
its trigger. When a trigger fires and the precise way is built, delete the row.
