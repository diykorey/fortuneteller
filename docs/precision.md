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
| Years inside the span | Ordinary days from the flow's first reaction day on each market ([own years](steps/own-years-baseline.md), built 2026-10-30), every year inside that span pooled | Ordinary days weighted to match each year's share of the flow's days, or a model of each day's expected volatility (e.g. GARCH) | A flow whose days bunch in its last years, with era ratios that disagree with its verdict |

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
