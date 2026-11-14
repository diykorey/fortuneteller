# Roadmap

> Why this plan has this shape — the target, the idea being tested, and the principles behind the
> ordering — is in the [Legend](legend.md). Unfamiliar acronym, ticker, or term? Every one is
> explained in the [Glossary](glossary.md).

## The goal

A reader sees a headline and is told what followed every past event of its kind, for the markets
behind what they pay for, over spans from a day to a year, with the record beside each answer. An
entertainment tool with a realistic approach, not financial advice
([Legend](legend.md#the-target)). It began as a warning product for traders; how the goal moved is
in [Decisions](decisions.md).

## The MVP — "does the edge exist?"

The MVP answers one question with real data: **when CPI comes in different from what was expected,
do liquid instruments move in a measurable, repeatable way?**

It is not a predictor and not a product. It is a table of measured numbers with an honest `n` next
to each one. **"No edge" is a valid result** — finding that out in four steps is the whole point.

**Scope:** one event type (CPI) × five instruments — SPY, UST 10Y, DXY, Gold, VIX. Nothing else,
until this works.

**Done when:** for each of those five cells you can read a measured effect size (move per unit of
surprise), a hit rate, and `n` — and say honestly whether an edge is there.

### The four steps

Each step ends with something you can run that prints a real number. No step builds machinery for a
step that has not happened yet. The sample outputs below are illustrative shapes, not targets.

| # | Step | What it prints | Done when |
| --- | --- | --- | --- |
| 1 | **[Releases](steps/step-1-releases.md)** — CPI release dates and actuals from FRED into `event_instances` | `loaded N CPI releases, <first> … <last>` | The table holds real releases |
| 2 | **[Prices](steps/step-2-prices.md)** — daily bars for the five instruments; the return around each release into `observations` | `5 instruments × N releases = M observations` | Real returns joined to real events |
| 3 | **[Raw move](steps/step-3-raw-move.md)** — do these instruments move abnormally on CPI days versus ordinary days? | Typical release-day move vs baseline, per instrument | You know whether the event matters at all |
| 4 | **[Surprise](steps/step-4-surprise.md)** — add expected-vs-actual; relate the move to the surprise | Move per surprise unit, hit rate, `n`, per cell | **MVP complete** |

### Why this order

The previous attempt predicted from placeholder numbers first and measured afterwards. That built
machinery before touching real data, and produced output that looked like a product while meaning
nothing. Measuring first means the first thing that exists is a fact, and every feature after it
stands on real numbers. See the reset note in [CLAUDE.md](../CLAUDE.md).

### What the MVP deliberately does not have

No live data path, no scheduler, no delivery, no detection, no confidence calibration, no second
event type, no web anything. Each is on the ladder below and earns its turn.

### The open decision inside step 4

Surprise needs an expected value to subtract, and **free historical consensus is the scarcest data
in this project**. The choice is deliberately deferred to step 4, when steps 1–2 have made it cheap
to test:

- **Market consensus** — what forecasters actually predicted. The authentic definition, and the
  hardest to obtain free.
- **Computed baseline** — an expected value modelled from past prints. Always available from FRED
  alone, but it measures surprise-vs-trend rather than surprise-vs-market.

If consensus proves unobtainable, step 4 falls back to the computed baseline **and says so in its
output**. The claim shrinks; it does not get quietly overstated.

## Next steps, in order

Four phases, each opened by a decision that says why ([Decisions](decisions.md)). A row says what
the step is and where it stands; its spec holds the bars, the method and the full results.

### Phase 1: sharpen the measurement, then predict, then widen

Opened 2026-10-07, after rung 1 ([why](decisions.md#2026-10-07-sharpen-the-measurement-then-predict-then-widen)).
Each new expected value is one expectation source and each new event one event flow
([Extending](extending.md)).

| # | Step | Where it stands |
| --- | --- | --- |
| 1 | **[A free forecast of each jobs report](steps/nfp-forecast.md)**: ADP and jobless claims, fitted on earlier reports only | **Done.** The yield's and the dollar's links pass since 2014, against the forecast and the trend alike; the full history stays unclear |
| 1a | **[Country-aware events](steps/country-aware-events.md)**: a flow is its event type and origin country; each market's own time zone | **Done** |
| 2 | **[A free consensus, as context](steps/free-consensus.md)**: Nasdaq's published consensus for CPI and payrolls, 2008 on, checked against TradingView's | **Done.** The jobs report's yield and dollar links pass, more strongly; CPI's dollar passes against the consensus only |
| 3 | **[Predict the next release](steps/rung-2-predict.md)** (rung 2): a walk-forward test of every signed link | **Done.** The jobs report's dollar and yield hold (the yield barely beats drift); CPI's links are too few |
| 4 | **[More events](steps/step-4-more-events.md)**: retail sales, core PCE, GDP | **Done** 2026-10-12. Retail sales' yield holds walk-forward; core PCE and GDP give no calls |
| 4a | **Cross-country effects**, in three parts: [US releases and Europe's stocks](steps/cross-country.md), [ECB decisions](steps/ecb-decisions.md), [euro-area inflation](steps/euro-inflation.md) | **Done** 2026-10-22. Europe moves on Fed decisions and follows CPI's surprise more than New York, short of *tracks*; ECB decisions move the dollar, not Europe's stocks; nothing follows the euro-area flash's surprise |
| 4b | **[The US manufacturing survey (ISM)](steps/ism-manufacturing.md)** | **Done** 2026-10-23. The yield and the dollar track its surprise, short of *holds*; it explains part of New York's flash-day move |

### Phase 2: show what is measured, then widen

Opened 2026-10-23, with the target amended
([why](decisions.md#2026-10-23-an-entertainment-tool-with-a-realistic-approach)): show what is
measured, raise the call count once, then widen events and markets, every bar unchanged.

| # | Step | Where it stands |
| --- | --- | --- |
| 5 | **[The scoreboard](steps/scoreboard.md)**: a static page the evening job writes: every call and its grade, every link's record, every event's verdicts, and how many *moves* chance alone would give | **Done.** Served by GitHub Pages since 2026-10-27 |
| 6 | **[Jobless claims](steps/jobless-claims.md)**: the weekly US release, about 50 calls a year against 12 for a monthly one | **Done** 2026-10-27. The yield follows the surprise, short of *tracks*; no call. With each flow's own years (step 8a), six markets move on its lone days. Called live every Thursday from 2026-10-29 |
| 7 | **[More outcomes](steps/more-outcomes.md)**: oil, EUR/USD, the Nasdaq, the 5-year yield, the FTSE 100, the STOXX 600, bitcoin, a defence and an energy ETF | **Done** 2026-10-27. The 5-year yield is the most responsive market, holding walk-forward on the jobs report, retail sales and ISM; the euro mirrors the dollar, holding on the jobs report; bitcoin and defence move on none |
| 8 | **[Scheduled statements](steps/scheduled-statements.md)**: the Fed chair's and the ECB president's speeches and testimonies, "does it move?" only, previewed by the morning job | **Done** 2026-11-02. The Fed chair moves nothing; with own years, the ECB president moves the Euro Stoxx 50 and Brent. The preview is built |
| 8a | **[Ordinary days from each flow's own years](steps/own-years-baseline.md)** | **Done** 2026-11-02. 60 of 192 cells changed, *moves* 52 → 54, no call |
| 9 | **[Germany's calendar](steps/germany-calendar.md)**: ZEW, Ifo and the German flash CPI | **Done** 2026-11-02. The surveys move nothing; the euro tracks the flash CPI's surprise, short of *holds*; no call |
| 10 | **Dated shocks**, in four parts: [elections](steps/elections.md), [tariff actions](steps/tariffs.md), [the debt limit](steps/debt-limit.md), [summits](steps/summits.md) | **Done** 2026-11-03. A US election moves American stocks for a day; a tariff signing, Europe's indices on the day and over the week; Congress's final debt-limit vote, both Treasury yields; a summit, only the dollar on the day, unconfirmed |
| 11 | **News as a feed**: the US president's trade posts, [first term](steps/presidential-posts.md) and [second](steps/presidential-posts-2.md) | **Closed with no** 2026-11-03, by the rule written first: no US market moves on them. News in general is not measured |
| 12 | **[Beat the fortune teller](steps/beat-the-fortune-teller.md)**: a person's call logged before the release, graded beside the machine's | **Built.** The first live round waits for a release ([status](status.md)) |
| 13 | **[The Fed statement's tone](steps/fed-statement-tone.md)**, from a published word list | **Stopped** 2026-11-03 by its rule: the list reads 19 of 226 statements |
| 14 | **[The Fed statement's sentiment](steps/fed-statement-sentiment.md)**, from a dictionary built on the FOMC's own statements | **Done** 2026-11-03. It reads every statement; all four signed links *doesn't*; no call |
| 15 | **[The week ahead](steps/week-ahead.md)**: each release live calls in the next seven days, with its consensus, the thresholds and the replay record; never a call before the number | **Done** 2026-11-04 |
| 16 | **[The week ahead, without a call](steps/watch-ahead.md)**: the scheduled events live does not call, with how markets moved on such days before | **Done** 2026-11-04 |

### Phase 3: a headline, answered with what follows

Opened 2026-11-04 by the owner ([why](decisions.md#2026-11-04-a-headline-answered-with-what-followed-by-the-owner)):
a reader of the news, told what follows for the markets behind what they pay for, over a day, a
week, a month (21 closes), a quarter (63) and a year (252). Build on what exists first: decisions,
then a trigger standing in for the news, then the markets people feel, then real news. Steps 17 to
20 start with the US; each further country (the euro area and Germany first, their events already
stored; ECB decisions are step 17's part 1f) follows as its own parts once the US answers hold. Each step gets its own spec, bars
written first.

| # | Step | Where it stands |
| --- | --- | --- |
| 17 | **What follows, over spans**: after each kind of past event, the signed move over each span against the base rate, replayed walk-forward; *up*, *down*, *about the same* or *can't say*, with the counts. Parts: [1, Fed decisions](steps/what-follows.md); [1b, the jobs report](steps/what-follows-jobs.md); [1c, retail sales](steps/what-follows-retail.md); [1d, CPI](steps/what-follows-cpi.md); [1e, jobless claims](steps/what-follows-claims.md); [1f, ECB decisions](steps/what-follows-ecb.md); [2, the Fed over a quarter and a year](steps/what-follows-long.md) | **Done** 2026-11-12. One answer holds walk-forward: after a jobs report above the consensus, both yields rise on the day, right on 38 and 37 of 57. Every other part holds nothing |
| 18 | **A trigger arrives**: [part 1](steps/after-the-day.md), what follows from the next close; [part 2](steps/trigger-file.md), a hand-written file of triggers, each dated by the merge of its pull request, answered with part 1's figures, logged and graded | Part 1 **done** 2026-11-04: nothing holds on any flow. Part 2 **built**; its first triggers wait to be graded ([status](status.md)) |
| 19 | **The markets people feel**: [part 1](steps/markets-people-feel.md), corn, wheat, soybeans, gasoline and natural gas through their funds, utilities and homebuilders; [2a, coffee](steps/coffee.md); [2b, the breakeven](steps/breakeven.md); [the scoreboard, faster](steps/scoreboard-faster.md); [2c, the signs](steps/signs.md); [2d, the breakeven's sign](steps/breakeven-sign.md). Mortgages need nothing new: they follow the yields already stored | **Done** 2026-11-12. The breakeven holds on CPI, 35 of 42, the first market people feel with a call; utilities' and homebuilders' signs hold nothing |
| 20 | **News into triggers**: a free news source read into step 18's triggers, by rules first and a model on this machine if rules fall short (starting from the unified prompt in docs/legacy/event-polarity-and-classifier-prompts.md). [Part 1](steps/ceo-scandals.md), a CEO's conduct in question, measured from a published dataset; part 1b, a CEO's conduct coming out with no departure (Nvidia's case), a kind by the owner's word, measured once a free list nobody picks is found; part 2, a pasted article read into a trigger, reading both kinds; part 3, a feed; tariff actions after | **In progress.** Taken 2026-11-13 by the owner, ahead of steps 17 and 18's grades ([why](decisions.md#2026-11-13-news-into-triggers-now-company-news-first-by-the-owner)). Part 1: the company falls against the S&P 500 on the day, 17 of 26; nothing holds walk-forward |

### Phase 4: prove the loop, show the page, be seen

Opened 2026-11-14 ([why](decisions.md#2026-11-14-prove-the-loop-show-the-page-be-seen-then-widen)).
After a month live, the log holds one call; the page the target describes does not exist; nobody
outside the project sees it. So the next work closes that gap before widening. **No new flow or
kind starts until steps 21 to 23 are done**, except step 20's part 2, already in progress; part 1b
waits for the gate. Each step gets its own spec, bars written first, read by a goldfish before
anything is built.

| # | Step | Where it stands |
| --- | --- | --- |
| 21 | **The loop off the laptop**: the release-day and evening jobs on GitHub Actions, first in a shadow run beside the laptop for two release days, every row compared. The spec says where the store lives on a runner that starts empty (rebuilt or cached). If a source refuses the runner (Nasdaq answered a different Python with HTTP 403 before), that is a result: the laptop stays and the reason is written down. Rung 6's popup stays on the laptop as a second channel; the page and step 23's post become the main one. When it passes, the 2026-11-10 decision to keep the laptop open is retired | **Planned**, next |
| 22 | **Ask the fortune teller**: the page the target describes, with the reader picking the kind of event until step 20 reads it from the news. For each kind step 17 answers (Fed decisions, the jobs report, retail sales, CPI, jobless claims, ECB decisions) and step 20's *ceo*, every market and span: the answer, the counts and the base rate. *Can't say* is shown with what markets did anyway, never graded. Answers are computed ahead into a file the static scoreboard reads, the same numbers the follows command prints; no server | **Planned** |
| 23 | **Be seen, and count it**: a free, privacy-light visitor counter on the page, and one channel, a weekly post: what the fortune teller said, and how it did. The spec names the counter and how it counts a unique visitor before the first post; the bar is the gate's | **Planned** |

**The gate, 2027-01-31.** Steps 21 to 23 are judged together against bars fixed now, each counted
from a named source:

- **The loop:** every release day of a flow the live command calls is logged on time and graded,
  none missed, for the four straight weeks before the gate. *On time* means logged within 15
  minutes of the release, before New York opens. Counted from the logged_at column of
  data/calls.csv against the release calendar, and the misses the score command lists.
- **The page:** live on GitHub Pages, answering every kind listed in step 22.
- **Readers:** at least 100 unique visitors in one week, by step 23's counter.

How many live calls are made is reported at the gate but is not a bar: it depends on how big the
surprises are, which no step controls. If any bar fails, the next change is a decisions entry that
says what the project does instead, before any new step starts. If all pass, the "Later" list
opens, prediction markets first: Kalshi's and Polymarket's free price history (Polymarket's from
2020), measured as markets readers bet in, then as a free expected value for an election (step 10).
They are the betting markets the project's first statement of intent named beside stocks and
crypto.

Later, not planned in detail, each chosen one at a time after the gate: new kinds of
events, each a dated history before a flow (OPEC decisions against Brent, already stored; floods
and droughts in crop-growing regions, with one start day each; earnings reports, with the single
companies' prices they need; crypto's own news); a CEO's conduct with no departure (step 20, part
1b); the page's words for the figures, once rung 3's rule allows a percentage; and what-if stories
for what has no past, labelled as reasoning and kept apart from graded records.

## After the MVP — the feature ladder

In order. Each rung is worth building only because the one below it worked.

| # | Feature | Why it waits |
| --- | --- | --- |
| 1 | **[More events](steps/rung-1-more-events.md)** — NFP, Fed decisions. **Done** 2026-10-06; results in [MVP results](mvp-results.md#rung-1--more-events) | Same code, more rows. Widen only once one event type is measured. |
| 2 | **[Predict the next release](steps/rung-2-predict.md)**. **Done** 2026-10-12; results in [MVP results](mvp-results.md#predicting-the-next-release) | A prediction is only worth emitting once it comes from measured numbers. |
| 3 | **[Honest confidence](steps/rung-3-confidence.md)** — hit rate → probability, magnitude bands, silence on low-`n` cells. **Done** 2026-10-12; results in [MVP results](mvp-results.md#honest-confidence): the bands are honest, the probabilities not | "70%" must mean 70%. Needs enough measured history to calibrate against. |
| 4 | **[Keep score](steps/rung-4-keep-score.md)** — log predictions, grade them against outcomes. **Done** 2026-10-16: logged and graded on the first two live releases; every verdict "too few", as expected | You cannot grade predictions you are not yet making. |
| 5 | **[Live path](steps/rung-5-live-path.md)** — fetch the release when it lands, instead of by hand. **Done** 2026-10-16: the first fetched actual equals FRED's; unattended by [the release-day job](steps/release-day-job.md), installed 2026-10-15 | Automating a manual step that must first be worth automating. |
| 6 | **[Delivery](steps/rung-6-delivery.md)**: the warning actually reaches a person, as a desktop popup on this laptop. **Built**; the first release it pops up unattended is awaited ([status](status.md)) | Never deliver uncalibrated warnings. A warning carries the direction, its walk-forward record and its band, never a stated probability, until one proves honest by rung 3's rule ([the record, not a probability](steps/record-not-probability.md)). |
| 7 | **Unscheduled events**: detection, classification, entity linking, corroboration. Statements, shocks and news are measured as history first (steps 8, 10 and 11); step 20 reads news into triggers only for kinds already measured; detection beyond those stays last | The hardest part of the system, and worthless without a working predictor behind it. |

Beyond the ladder, and deliberately not planned in detail: regime conditioning, productization
beyond the scoreboard, and operations. They get planned when rung 7 is in sight.

## The rules this roadmap is built on

From the [reset note in CLAUDE.md](../CLAUDE.md), because they are what keeps steps small:

1. No new package until a second caller needs it.
2. No indirection for a single case.
3. A plan doc must be shorter than the code it specifies.

## Graduation triggers

Build the heavier thing only when its trigger actually fires. None has.

| Move | Trigger |
| --- | --- |
| DuckDB → Postgres | Concurrent writers, or a live serving API |
| Script → web service | Something external must call it |
| Polling → streaming bus | Feed volume outgrows simple polling |

## Status

Last completed task and the next one: **[status.md](status.md)**.

Historical planning documents, including the superseded M0–M7 milestone scheme, are kept in
[legacy/](legacy/README.md).
