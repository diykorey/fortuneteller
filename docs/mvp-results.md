# MVP results

> The MVP's outcome in plain words. The detail, the numbers and how they were checked are in the
> step documents: [1 Releases](steps/step-1-releases.md), [2 Prices](steps/step-2-prices.md),
> [3 Raw move](steps/step-3-raw-move.md), [4 Surprise](steps/step-4-surprise.md). Terms are in
> the [Glossary](glossary.md). Measured on data loaded 2026-10-05; the rung 1 section on
> 2026-10-06, with [its own document](steps/rung-1-more-events.md).

## What we set out to prove

FortuneTeller is meant to warn which markets will move, and how, when an event happens. That only
works if three things are true, in this order (see the [Legend](legend.md)):

1. **The event moves markets at all.**
2. **The size of the move follows the size of the surprise:** how far the number landed from what
   was expected.
3. **That relationship holds for the next event**, not only for past ones.

The MVP tested the first two, on one event and five markets, before building anything that
predicts: every US CPI release since 1972, and the S&P 500, the 10-year Treasury yield, the dollar
index, gold and the VIX, from free data only.

## What we found

**1. CPI moves three of the five markets. True for three.**
On a CPI day the 10-year yield moves 25% more than on an ordinary day, VIX 19% more and the dollar
16% more, and chance alone would rarely give that. The S&P 500 and gold move no more than usual.

**2. The move follows the surprise for the 10-year yield, weakly. True for one.**
When core CPI comes in hotter than its recent trend, the 10-year yield rises that day, by about
1 bp for every 0.1 percentage point of surprise, and it goes the expected way about 62% of the
time. The link is real but weak: the surprise explains only a small part of the day's move. For
the dollar the evidence is mixed (a real link, but the direction is right only about half the
time). For VIX, the S&P 500 and gold, the move does not follow the surprise by the rule we fixed
in advance.

**3. Whether it holds for the next release: not tested yet.** That needs predictions made before
releases and graded after them: rungs 2–4 of the [roadmap](roadmap.md).

| Market | Moves more on CPI days? | Move follows the surprise? |
| --- | --- | --- |
| 10-year yield | Yes | **Yes, weakly** |
| Dollar index | Yes | Unclear |
| VIX | Yes | No |
| S&P 500 | No | No |
| Gold | No | No |

## What it means

**The project's bet holds in one place, and only weakly so far.** CPI matters to three markets,
and for the 10-year yield the size of the surprise says something about the move. That is a
signal. It is not yet a product: a direction that is right 62% of the time is wrong 38% of the
time, and a warning built on it today would mostly be noise with a confident face, which is the
failure the project exists to avoid.

**The weakness may be in the measurement as much as in the market.** Two shortcuts, listed in
[Precision](precision.md), probably hide part of the effect:

- **The window is a whole day.** A move from yesterday's close to today's close carries every other
  piece of news that day. Prices from just before and after 08:30 would isolate the release.
- **"Expected" is a trend, not the market's forecast.** There is no free history of what
  economists expected for core CPI; the free model forecast (the Cleveland Fed's) turned out to be
  almost the same as the trend. A surprise against the real forecast would be cleaner.

On the 155 releases since 2013 the 10-year yield's link is stronger (right 71% of the time), but
that rests on 49 releases and was not a planned test, so it is a lead, not a result.

**What it does not mean.** Nothing here predicts a future release, and nothing should be used to
trade or to warn. The numbers describe the past.

## Rung 1 — more events

Measured 2026-10-06. Detail and checks in [rung 1](steps/rung-1-more-events.md).

The same steps ran on two more events: the monthly jobs report (NFP, 1955 on) and the Fed's rate
decisions (1994 on, including 14 unscheduled ones). Two fixes came with them:

- **A cleaner baseline.** "Ordinary days" now leave out every CPI, jobs-report and Fed day.
- **The right close for each market.** A move starts at the last close before the event. Gold
  settles at 13:30, before the Fed's 14:00 statement, so on Fed days it reacts the next day.

**1. Do the events move markets? Yes, all three; the jobs report most.**

| Market | CPI | Jobs report | Fed decision |
| --- | --- | --- | --- |
| 10-year yield | Yes (+33%) | **Yes (+67%)** | Unclear (+23%) |
| Dollar index | Yes (+18%) | Yes (+25%) | Yes, borderline (+22%); unclear (+18%) from [own years](#own-years) |
| VIX | Yes (+22%) | Yes (+31%) | Yes (+25%) |
| S&P 500 | No | Yes (+19%) | Yes (+30%) |
| Gold | No | Yes (+27%) | **Yes (+81%)** |

The percentages say how much bigger the median move is than on an ordinary day. CPI's answers did
not change with the cleaner baseline; its numbers rose a little.

**2. Does the move follow the jobs-report surprise? Clearly related, but not reliable enough.**
When payrolls beat their 12-month trend, the 10-year yield and the dollar tend to rise. The link
is far beyond chance (p 0.0001 over about 670 reports) and stronger than CPI's. But the direction
is right only 58% (yield) and 56% (dollar) of the time, under the 60% bar fixed in advance, so
neither passes. The other three markets have no agreed direction for good jobs news, and do not
pass either. The Fed gets no surprise test: there is no free record of what the market expected.

| Market | CPI surprise | Jobs-report surprise |
| --- | --- | --- |
| 10-year yield | **Yes, weakly** (right 62%) | Unclear (right 58%) |
| Dollar index | Unclear (right 53%) | Unclear (right 56%) |
| VIX, S&P 500 | No | No |
| Gold | No | Unclear (no agreed direction) |

**What it means.** The method works beyond CPI: the jobs report and the Fed move markets clearly,
and every check on the data held. The surprise link is still the weak point. For the jobs report
it is real but misses the bar, which again points at the measurement rather than the market: the
"expected" value is a trend, not the forecast economists published.

## A free forecast of each jobs report

Measured 2026-10-09. Detail in [nfp-forecast](steps/nfp-forecast.md#results).

Rung 1's jobs-report links sat just under the bar, against a 12-month trend. A model forecast each
report from what was published before it (ADP's report, weekly jobless claims and the trend),
refitted before every report on earlier reports only: 148 reports, 2014 on.

**Against the forecast, the 10-year yield and the dollar pass**, with and without COVID: the yield
right 66% of the time (63% without COVID), the dollar 65% (68%), both p ≤ 0.0003. **But the trend
passes too on the same reports** (yield 64% / 60%, dollar 63% / 66%). The forecast is only a little
sharper: its typical miss is 77k jobs against the trend's 80k outside COVID.

**What it means.** The jobs-report link is reliable since 2014 whichever expected value is used;
what kept it under the bar over the full history is the earlier decades, not the trend. The
official verdict, over 681 reports since 1956, stays unclear. A better free forecast was not the
shortcut; whether the market's own view, the paid consensus, would add more is the next question.

## A free consensus

Measured 2026-10-09. Detail in [free consensus](steps/free-consensus.md#results).

The consensus published before each release (Nasdaq's calendar, checked against TradingView's)
replaced our trend and model as the expected value, as context beside the official verdicts:
220 CPI releases and 222 jobs reports since 2008.

**The jobs report's links pass against the consensus, and are clearly stronger.** The 10-year
yield follows the payroll surprise 67% of the time against the consensus (69% without COVID),
against 63% (60%) for the trend; the dollar 68% (69%) against 61% (63%). The correlation for the
yield rises from 0.26 to 0.39, and the yield moves about three times as much per 50k of surprise.

**For CPI, the consensus adds the dollar.** The yield tracks against the trend, the nowcast and the
consensus alike. The dollar, unclear against the trend and nowcast (53–56%), tracks against the
consensus (62–70%), though its correlation is unchanged.

**What it means.** The expected value was what held the jobs-report link under the bar: a model of
our own did not fix it, the market's own consensus does. Three links now pass against a free,
live expected value: the yield and the dollar on jobs reports, the yield on CPI (and the dollar on
CPI against the consensus only). That is what a first prediction (rung 2) can be built on.

## Predicting the next release

Measured 2026-10-12. Detail in [rung 2](steps/rung-2-predict.md#results).

Every link with an expected direction was replayed release by release, each predicting only once
it passed the test on the releases before it, and graded on that day's move.

**Both jobs-report links hold.** The yield was right on 65 of 100 calls (67% without COVID), the
dollar on 55 of 81 (68%; 69%), both p < 0.01. But always calling the yield up would have been right
61% of the time: its edge over drift is not significant. The dollar's is (68% against 47%).

**CPI's links are too few to judge.** They pass on the whole history, but open only in 2024 (dollar,
8 calls) and 2026 (yield, 1); stocks and VIX never open.

**What it means.** Claim 3 is shown for one link beyond doubt: the dollar on a jobs-report surprise.
`predict --actual` gives that call for the next release from its typed-in actual and the published
consensus.

## Honest confidence

Measured 2026-10-12. Detail in [rung 3](steps/rung-3-confidence.md#results).

Each jobs-report call from its link's 21st on was given a probability (the link's record on its
earlier calls) and a 50% band for the move, from earlier releases only, and both were graded.

**The probabilities are not honest.** Both links state about 68% and are right 61% (yield) and 64%
(dollar) of the time. Neither beats a coin or the drift by more than chance; the yield is worse
than the drift, and the dollar's calls stated at 70% or more were right on 6 of 14. Without COVID,
both are too close to tell.

**The bands are.** About half of each link's moves land inside its band. They are wide and cross
zero: on a 100k surprise, the dollar's runs from about −0.15% to +0.55%.

**What it means.** The dollar's direction on a jobs report is worth calling (rung 2); how sure to be
of it is not yet measurable from about 60 graded calls. `predict --actual` prints the record and the
band with that verdict beside them, rather than a number to trust. Since 2026-10-20 the record is
printed as counts, without the percentage or the verdict ([the record, not a
probability](steps/record-not-probability.md)).

## More events: retail sales, core PCE, GDP

Measured 2026-10-12. Detail in [step 4](steps/step-4-more-events.md#results).

Three US releases added, each against Nasdaq's consensus, with days shared with another release
left out (about 15% of retail sales').

**Retail sales adds a second link worth calling: the 10-year yield.** It follows the surprise (right
67%), and holds walk-forward: 50 of 78 calls right from 2011, where always calling it up would have
been right 44% of the time. Without COVID it misses the bar narrowly (p 0.014). Its stated
confidence is not honest: a coin's Brier score, on 58 calls.

**Core PCE and GDP move markets but cannot be predicted.** Core PCE's consensus is nearly always right
(19 surprises of 0.1pp in 207); GDP has too few releases. Neither link ever opens.

**What it means.** Calls worth making: the dollar on a jobs report, the yield on retail sales. More
events added links, not calls to existing links, so honest probabilities still wait for more history
or a log of live calls.

## A fallback consensus

Measured 2026-10-13. Detail in [consensus fallback](steps/consensus-fallback.md#results).

Nasdaq's calendar had no CPI row the day before the first live CPI release. Where Nasdaq has no
row, TradingView's forecast is now taken, in the replay and live; on 828 releases both list, the call
never turns around. The fallback adds 14 past releases (retail sales 7, core PCE 6, GDP 1). Every
walk-forward and surprise verdict stands; retail sales' yield still holds (51 of 79). Its stated
confidence moves from "not honest" to "too close to tell", by one call across a coin's Brier score.

## Live calls

Graded 2026-10-16. Detail in [rung 4](steps/rung-4-keep-score.md#results) and
[rung 5](steps/rung-5-live-path.md#results).

The first two live releases were logged before their closes and graded: core CPI on 2026-10-14
(typed) and retail sales on 2026-10-15 (fetched from TradingView, equal to FRED's first print).
Three calls were graded: CPI's dollar right; CPI's yield wrong; retail sales' yield, called up at
64%, wrong, 10.1 bp down and outside its band. Every live verdict reads "too few", as expected for
years. Calls are now logged unattended each release morning by
[the release-day job](steps/release-day-job.md).

## Cross-country effects: Europe's stocks

Measured 2026-10-21. Detail in [cross-country effects](steps/cross-country.md#results).

The DAX and Euro Stoxx 50 move on Fed decisions (more than the S&P 500), the Euro Stoxx 50 on
jobs reports; neither on CPI, retail sales or GDP days. Both follow CPI's surprise more closely than
the S&P 500 (rank correlation 0.18 against 0.13; against the consensus 0.17 against 0.02), with a
larger move per point, but neither reaches *tracks*. The DAX's CPI link is open walk-forward, so
live CPI releases now log a DAX call.

## Cross-country effects: ECB decisions

Measured 2026-10-22. Detail in [ECB decisions](steps/ecb-decisions.md#results).

115 ECB decisions since 2013 move the dollar index (ratio 1.41) and no other market: not the DAX
or Euro Stoxx 50, not the S&P 500, the yield or gold; VIX is unclear. The Fed moves six of seven.
Taking ECB days out of the ordinary days changed no US verdict.

## Cross-country effects: euro-area inflation

Measured 2026-10-22. Detail in [euro-area inflation](steps/euro-inflation.md#results).

143 flash HICP estimates since 2014 move the S&P 500 (ratio 1.41) and VIX (1.44), not Europe's
stocks, the yield or the dollar; on flash days with no other release the two fall short of the bar,
so the move is probably another US release that day. Against TradingView's forecast nothing follows
the core surprise; the DAX comes nearest (unclear). No call. Flash days, shared with US releases,
changed two GDP verdicts: the dollar index against the surprise to *doesn't*, VIX on release days to
unclear.

## The US manufacturing survey (ISM)

Measured 2026-10-23. Detail in [the ISM survey](steps/ism-manufacturing.md#results).

163 ISM releases since 2013 move the yield (ratio 1.47) and the DAX (1.37); the yield and the dollar
index track its surprise against TradingView's forecast (rank corr 0.33 and 0.26, both 67% of
noticeable surprises). Walk-forward the yield is right on 31 of 49, short of *holds*: no call. On
flash days without ISM, New York's move shrinks (S&P 500 1.40 to 1.25) but does not vanish. With
ISM days out of ordinary days, CPI's S&P 500 and GDP's gold turn unclear on release days, and the
flash's Euro Stoxx 50 against its surprise; every call is unchanged.

## Jobless claims

Measured 2026-10-27. Detail in [jobless claims](steps/jobless-claims.md#results).

706 weekly reports since 2013, 450 of them on a day with no other stored release: on those days no
market moves more than on an ordinary one (gold nearest, ratio 1.10, p 0.06). The yield follows the
surprise against Nasdaq's consensus the expected way, more claims a lower yield, but faintly (rank
corr 0.14 on 448 days, right on 56% of the 307 noticeable surprises), short of *tracks*; the dollar
index less so. No link opens walk-forward, so no call: the morning job logs silent rows every
Thursday from 2026-10-29 until one does. By the lesser-release rule nothing else changed, and taking
claims days out of ordinary days would move CPI's and the jobs report's yield ratios by under 0.001.

## More outcomes

Measured 2026-10-27. Detail in [more outcomes](steps/more-outcomes.md#results).

Nine markets beside the seven, under the same bars. The 5-year yield is the most responsive market
of the sixteen: it moves 90% more on jobs-report days, tracks CPI, retail sales and ISM, and holds
walk-forward on the jobs report (71 of 101), retail sales (49 of 74) and ISM (34 of 50). The euro
mirrors the dollar index and holds on the jobs report too (56 of 81). The Nasdaq moves on seven of
ten events, the S&P 500 on two, lone claims days among them. London and the STOXX 600 move on Fed
and jobs-report days as Frankfurt does, and not on the ECB's. Brent and the energy ETF move on ISM
days only; the defence ETF on none; bitcoin on none, and less than on ordinary days. 23 of the
nine's 90 release-day cells say *moves* where chance would give one. Four new links hold, three of
them called live from 6 November. (*Amended 2026-11-02*, [own years](#own-years): the Nasdaq now
moves on two events, the S&P 500 on four; London on the ECB's, ISM's and lone claims days too.)

## Scheduled statements

Measured 2026-10-29. Detail in [scheduled statements](steps/scheduled-statements.md#results).

The Fed chair's speeches and testimonies move no market on the 176 days the chair speaks alone; the
10-year yield and VIX come nearest. The ECB president's 339 lone days move VIX, Brent and the Nasdaq
by the fixed rule, and nothing in Europe; three *moves* in sixteen cells where chance gives 0.16,
and none survives the era split. The president's days start in 2013, and markets louder now than in
their past look as if they move on any recent day. The baseline that pools every year, chosen at
step 3, has met its trigger: an exploratory look with ordinary days from 2013 on moves the Euro
Stoxx 50 instead of the Nasdaq on the president's days, and six markets instead of one on lone
claims days. (*Amended 2026-11-02*, [own years](#own-years): built as the rule, those are now the
verdicts.)

## Own years

Measured 2026-11-02. Detail in [own years](steps/own-years-baseline.md#results).

Each flow's days are now compared with ordinary days from its own years, not every year of a
market's history. 60 of 192 cells changed verdict; *moves* went from 52 to 54, and no call changed.
The Nasdaq was the tilt: it moved on nine flows, now on two, the jobs report and ISM. ISM moves
twelve of sixteen markets. Lone claims days, where nothing moved, move six: the dollar, the euro,
the 5-year yield, gold, the DAX and the FTSE 100. The Fed's dollar, retail sales' dollar and core
PCE's VIX fall to *unclear*; the ECB adds the FTSE 100, and the euro-area flash keeps the S&P 500 but
loses VIX and the Nasdaq. The expected outcome was right on the Nasdaq and the jobs report, wrong on
how few cells the older flows would change and on the flash's S&P 500. One cell, the ECB president's
Brent, still *moves* on days bunched since 2020 where its ratio is 1.09: precision's new trigger.

## Germany's calendar

Measured 2026-11-02. Detail in [Germany's calendar](steps/germany-calendar.md#results).

Three German releases as lesser flows, each on its lone days: ZEW's analysts (113), Ifo's firms
(97) and the national flash CPI (85). The two surveys move no market and no market follows their
surprise. The flash CPI moves the dollar index (1.35), though only before 2020, and the euro tracks
its surprise: a hotter German print than forecast lifts the euro on 65% of noticeable surprises,
p 0.001. That is the first European surprise a market follows; the euro-area flash a few days later
has none. Walk-forward the euro's link opens in 2022-11 and is right on 12 of 19, too few; no call.
The expected outcome was right on the surveys and wrong on the flash.

## Elections

Measured 2026-11-02. Detail in [Elections](steps/elections.md#results).

National votes as five lesser flows, each on its lone reaction days: the US (26), the UK (7),
Germany (15), France's presidential rounds (18) and the European Parliament (9). A US election
moves the S&P 500 (2.24, p 0.0002) and the Nasdaq (2.01) the next day, about four times an
ordinary day since 2008; a week later the excess has faded to *unclear*. France's rounds move VIX
(2.23, p 0.004), still inside the bar against ordinary Mondays, and no stock market. Germany's
votes move nothing. The UK's and the European Parliament's cells are all *too few*, under ten
days. Over a week nothing reaches the bar. No call: an election has no surprise. The expected
outcome was right on the S&P 500, the UK and the week, and wrong on the US's VIX (*unclear*) and
on France.

## Tariff actions

Measured 2026-11-03. Detail in [Tariff actions](steps/tariffs.md#results).

The US president's signed tariff documents since 2018, from the Federal Register: 73 signing days,
44 of them alone on their reaction day. On the next close Europe's stocks move: the DAX (1.64, p
0.004) and the Euro Stoxx 50 (1.62). Over the week the DAX (1.58) and the STOXX 600 (1.52) do. No
US market moves on the next close. Europe closes before New York's afternoon, so a signing then
reaches New York's close the same day and Europe's only the next; on the signing day itself (a one-off
check, [detail](steps/tariffs.md#results)) the S&P 500 is 1.22, short of the bar, and the measure cannot tell the two apart. The expected outcome was wrong on
the day and over the week; its era split and its dilution were not testable. No call: a signing has
no surprise.

## The debt limit

Measured 2026-11-03. Detail in [The debt limit](steps/debt-limit.md#results).

The 75 laws that changed the US debt limit since 1970, dated by Congress's final vote: 73 days,
60 of them alone on the S&P 500's reaction day. On the next close the 10-year and 5-year Treasury
yields move about twice an ordinary day (1.97 and 1.94, p 0.0002), and over the week still about
1.5 times. No stock market moves, on the day or over the week. The yields' move holds on the laws
about the debt alone, has no match at the bar in the session before, and is not month ends. The expected
outcome, no market moving, was wrong for both yields. The 2008, 2011 and 2023 standoffs share
their day with a jobs report or core PCE and are not counted. No call: a vote has no surprise.

## Summits

Measured 2026-11-03. Detail in [Summits](steps/summits.md#results).

The 70 annual G7 and G20 leaders' summits since 1975, each at its last day: 51 of them alone on
the S&P 500's reaction day. On the day only the dollar index clears the bar (1.68, p 0.001), one
cell of 16 where chance gives 0.16; the euro does not follow (1.16) and the G7 alone falls short
(1.49, p 0.03). Over a week nothing moves. The expected outcome, nothing moving, was wrong for the
dollar alone. No call: a summit has no surprise.

## The president's trade posts

Measured 2026-11-03. Detail in [the president's trade posts](steps/presidential-posts.md#results).

GDELT, measured first, cannot date a statement: its article counts follow the market, it names no
speaker and has no trade topic. The president's own first-term tweets about tariffs or trade
can: 179 tweet days, 146 reaction days on the S&P 500, 103 of them lone, compared with ordinary
days of the same term. No market *moves*, on the next close or over the week; six are *unclear*,
the lowest p the 5-year yield's 0.07. On US stocks and VIX the day before each reaction day is
louder than the reaction day (the S&P 500 1.47, p 0.09), a check and not a verdict; on 9 of 16
markets it is quieter. Against the expected outcome: met on seven cells, near on eight, missed on
one (the Nasdaq); over a week met. No call.

**The second term** ([part 2](steps/presidential-posts-2.md#results)): 220 Truth Social post days
from a frozen snapshot of CNN's archive, 122 lone on the S&P 500, compared with ordinary days of
2025-01-22 to 2026-10-30. No US market *moves* on the day: the S&P 500 0.86, the Nasdaq 0.87, VIX
0.98; outside the session they stay under 1.10 (0.85, 0.86, 1.03). Bitcoin *moves* (1.33, p 0.009),
one hit where 0.16 are expected by chance, with its day before at 1.10, so clustering is not
excluded. Against the expected outcome: met on four cells, near on eight, missed on four (the three
US markets and bitcoin). Over a week, context only and not graded, gold and energy *move*; 80–83% of
ordinary week windows hold a post reaction day, so a week result is weak evidence. A median test
does not rule out a few large post days; no *moves* is not no effect. **By the rule written first,
step 11 closes with no:** the president's topic-matched text posts give no US market a *moves* on
the day. That measures those posts, not news in general. No call.

## The Fed statement's tone

Measured 2026-11-03. Detail in [the Fed statement's tone](steps/fed-statement-tone.md#results).

Each Fed statement since 2000 was scored with a published hawkish/dovish word list (Apel and Blix
Grimaldi, 2012): adjective–noun phrases such as "higher inflation" or "slower growth". The list
finds a phrase in 19 of the 226 statements. The Fed writes the noun first ("inflation remains
elevated") or with words the list does not have ("subdued inflation", "economic growth"). So no
signed link reaches the 40 holds the test needs; each has one. **By the rule written first, the
step stops before any move is read:** the Fed flow gets no surprise, and the question is
untested, not answered no. No call.

## The Fed statement's sentiment

Measured 2026-11-03. Detail in [the Fed statement's sentiment](steps/fed-statement-sentiment.md#results).

The same question as the tone, with a dictionary built from the FOMC's own statements (Gardner,
Scotti and Vega, 2021): topic words such as "unemployment" or "inflation" paired with the nearest
word saying which way they went. It reads all 226 statements since 2000 and passes five checks
against the paper, among them 2008-12-16 low and 2018-09-26 high. **But no signed market passes
the test: all four are *doesn't*** on the 113 holds alone on their day. The yields lean the
expected way short of the bar (the 10-year closest, p 0.15); the euro leans the other way. As written first, no link tracks; no call. The Fed's scoreboard entry now shows these
verdicts.

## What follows a Fed decision

Measured 2026-11-04. Detail in [what follows](steps/what-follows.md#results).

The first answers by kind of event over spans: after each of 276 Fed decisions since 1994, read
from the target rate as 40 cuts, 184 holds and 52 hikes, what each of sixteen markets did over a
day, a week and a month against its own spans of that length. **Nothing holds walk-forward.** Cuts
and hikes are too few to grade, as written first. On all history four cells answer, against about
4.3 by chance: gold up a month after a cut, VIX down the day of a hold, the S&P 500 up a month
after a hold, bitcoin down a month after a hike; the placebo marks none as the period. **The
nearest is VIX on the day of a hold**: down on 93 of 184, and walk-forward right on 83 of 162
(51%) against its base rate of about a third, a chance of 0.00001; it misses only the 60% bar. No
answer; nothing for step 18 to show yet.

## What follows a jobs report

Measured 2026-11-04. Detail in [what follows a jobs report](steps/what-follows-jobs.md#results).

Part 1's method on 222 jobs reports since 2008, each *above*, *as expected* or *below* the
consensus by 50k. **After a report above the consensus, the 10-year and 5-year Treasury yields
rise on the day, and hold walk-forward**: right on 38 and 37 of 57 graded (67%, 65%). The first
answers by kind that pass every bar. On all history 13 answers against 4.3 by chance; the yields'
rise stays over the week, untested walk-forward; nothing answers over the month. VIX falls on a
report's day whatever it says, the release's doing, not the kind's.

## What follows a retail sales release

Measured 2026-11-04. Detail in [what follows a retail sales release](steps/what-follows-retail.md#results).

Part 1b's method on 222 retail sales releases since 2008, each *above*, *as expected* or *below*
the consensus by 0.3pp. **Nothing holds walk-forward.** On all history there are 5 answers,
against 4.3 by chance:
- after *below*, both yields fall on the day; walk-forward they are right on 56% and 51%, short of
  60%;
- after *above*, Europe's stock indices rise and EUR/USD falls on the day.

The yields' rise after *above*, the link step 4 calls, leans up but does not answer by kind.
Nothing answers over the week or the month.

## What comes next

Chosen 2026-10-13: keep score ([rung 4](steps/rung-4-keep-score.md)), done above with the live path
([rung 5](steps/rung-5-live-path.md)). Chosen 2026-10-19: [the evening score](steps/evening-score.md),
grading the live calls unattended. Chosen 2026-10-20: [the record, not a
probability](steps/record-not-probability.md), the call printed without a percentage no test can
check yet. Chosen 2026-10-21: [delivery](steps/rung-6-delivery.md) (rung 6), each call
as a desktop popup. Chosen 2026-10-21: [cross-country effects, part 1](steps/cross-country.md),
US releases against Europe's stocks. Chosen 2026-10-22: [ECB decisions](steps/ecb-decisions.md),
the first event from outside the US, and [euro-area inflation](steps/euro-inflation.md), the first
with a surprise. Chosen 2026-10-23: [the ISM survey](steps/ism-manufacturing.md), tested as the
flash day's other release. Decided 2026-10-23: the target is an entertainment tool with a realistic
approach ([Legend](legend.md#the-target)), and the plan widens what is shown while every bar stays:
the [roadmap](roadmap.md#next-steps-in-order)'s steps 5–11, the scoreboard first. Chosen
2026-10-26: [jobless claims](steps/jobless-claims.md), the one event that beats the sample wall.
Chosen 2026-10-27: [more outcomes](steps/more-outcomes.md), nine markets beside the seven. The
options as they stood:

| Option | What it is | Cost | What it would tell us |
| --- | --- | --- | --- |
| ~~**More events**~~ (roadmap rung 1) | ~~Add the jobs report (NFP) and Fed decisions~~ **done**, above | — | — |
| **Sharper measurement** | Economists' consensus forecasts for CPI and payrolls, and intraday prices around the release | Paid data | Whether the yield's and the dollar's jobs-report link passes the bar against a real forecast; for CPI, whether the weak link is the market or our daily window. *Deferred 2026-10-23:* it serves a trading use, not the amended target |
| ~~**A better free forecast**~~ | ~~A model of each jobs report from what is published before it (weekly jobless claims, the ADP report)~~ **done**, above: both links pass since 2014, but against the trend too | — | — |
| ~~**Predict the next release**~~ (rung 2) | ~~Forecast each link's direction, graded walk-forward~~ **done**, above: the jobs-report dollar holds clearly, the yield on drift, CPI too few | — | — |
| ~~**Honest confidence**~~ (rung 3) | ~~A probability and a band per call, graded~~ **done**, above: the bands are honest, the probabilities not | — | — |
| ~~**More events**~~ (roadmap step 4) | ~~Retail sales, core PCE, GDP~~ **done**, above: retail sales' yield holds; core PCE and GDP give no calls | — | — |
| ~~**Cross-country effects**~~ (roadmap step 4a) | ~~ECB decisions and euro-area releases, with markets abroad~~ **done** in three parts, above: Europe follows US news more than its own; Germany's calendar is step 9 | — | — |
| **Widen what is shown** (roadmap steps 5–11) | The scoreboard, jobless claims, more outcomes, scheduled statements, Germany's calendar, dated shocks, news as a feed | Free sources, more work | Chosen 2026-10-23: whether the fortunes reach anyone, and what the taxonomy's other half does to markets |
| ~~**Keep score**~~ (rung 4) | ~~Log each live call and grade it later~~ **done**, above: logged and graded, unattended from 2026-10-16; verdicts "too few" | — | — |

Rung 1 strengthened the case for better expected values before predicting: two links (the yield
and the dollar on jobs reports) are clearly real but sit just under the bar, and the expected value
is the known shortcut.
