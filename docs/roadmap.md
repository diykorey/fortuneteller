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
| 20 | **News into triggers**: a free news source read into step 18's triggers, by rules first and a model on this machine if rules fall short (starting from the unified prompt in docs/legacy/event-polarity-and-classifier-prompts.md). [Part 1](steps/ceo-scandals.md), a CEO's conduct in question, measured from a published dataset; part 1b, a CEO's conduct coming out with no departure (Nvidia's case), a kind by the owner's word, measured once a free list nobody picks is found; part 2, a pasted article read into a trigger, reading both kinds; part 3, a feed; tariff actions after | **Parked** until the 2027-01-31 gate ([why](decisions.md#2026-11-15-step-20-parked-until-the-gate-by-the-owner)). Taken 2026-11-13 by the owner, ahead of steps 17 and 18's grades ([why](decisions.md#2026-11-13-news-into-triggers-now-company-news-first-by-the-owner)). Part 1: the company falls against the S&P 500 on the day, 17 of 26; nothing holds walk-forward. Part 2: the word rules *don't read* (5 of 12 test positives, 6 of 99 negatives misread) |

### Phase 4: prove the loop, show the page, be seen

Opened 2026-11-14 ([why](decisions.md#2026-11-14-prove-the-loop-show-the-page-be-seen-then-widen)).
After a month live, the log holds one call; the page the target describes does not exist; nobody
outside the project sees it. So the next work closes that gap before widening. **No new flow or
kind starts until steps 21 to 23 are done**; step 20 is parked until the gate (*amended
2026-11-15*, [why](decisions.md#2026-11-15-step-20-parked-until-the-gate-by-the-owner)).
*Amended 2026-11-17, by the owner:* the pause is lifted; new kinds start now, in phase 5 below,
while steps 21 to 23 finish and the gate keeps its bars
([why](decisions.md#2026-11-17-widen-the-kinds-now-by-the-owner)). Each step gets its own spec, bars written first, read by a goldfish before
anything is built.

| # | Step | Where it stands |
| --- | --- | --- |
| 21 | **The loop off the laptop**: the release-day and evening jobs on GitHub Actions, first in a shadow run beside the laptop for two release days, every row compared. The spec says where the store lives on a runner that starts empty (rebuilt or cached). If a source refuses the runner (Nasdaq answered a different Python with HTTP 403 before), that is a result: the laptop stays and the reason is written down. Rung 6's popup stays on the laptop as a second channel; the page and step 23's post become the main one. When it passes, the 2026-11-10 decision to keep the laptop open is retired | **In progress**: [the spec](steps/loop-off-the-laptop.md). Step 1: every source answers the runner; the store cannot be rebuilt from empty. Step 2, the shadow beside the laptop: two counting days owed by 2026-12-18 ([status](status.md)) |
| 22 | **[Ask the fortune teller](steps/ask-the-fortune-teller.md)**: the page the target describes, with the reader picking the kind of event until step 20 reads it from the news. For each kind step 17 answers (Fed decisions, the jobs report, retail sales, CPI, jobless claims, ECB decisions) and step 20's *ceo*, every market and span: the answer, the counts and the base rate. *Can't say* is shown with what markets did anyway, never graded. Answers are computed ahead into a file the static scoreboard reads, the same numbers the follows command prints; no server | **Done** 2026-11-19 ([step 5](steps/ask-the-fortune-teller.md#step-5)): the published page answers every kind, none left out; exactly the three expected holds |
| 23 | **[Be seen, and count it](steps/be-seen.md)**: a free, privacy-light visitor counter on the page, and one channel, a weekly post: what the fortune teller said, and how it did. The spec names the counter and how it counts a unique visitor before the first post; the bar is the gate's | **In progress**: the counter live since 2026-11-17; the page's link preview since 2026-11-20; the first post next ([status](status.md)) |

**The gate, 2027-01-31.** Steps 21 to 23 are judged together against bars fixed now, each counted
from a named source:

- **The loop:** every release day of a flow the live command calls is logged on time and graded,
  none missed, for the four straight weeks before the gate. *On time* means logged within 15
  minutes of the release, before New York opens. Counted from the logged_at column of
  data/calls.csv against the release calendar, and the misses the score command lists.
- **The page:** live on GitHub Pages, answering every kind listed in step 22.
- **Readers:** at least 100 unique visitors in one week, by step 23's counter. *Amended 2026-11-15:* weeks run Monday to Sunday UTC, so the last, 2027-01-25 to 31, is
  read on 2027-02-01 ([step 23](steps/be-seen.md#the-rule-fixed-before-the-first-post)).

How many live calls are made is reported at the gate but is not a bar: it depends on how big the
surprises are, which no step controls. If any bar fails, the next change is a decisions entry that
says what the project does instead, before any new step starts. If all pass, the "Later" list
opens, prediction markets first: Kalshi's and Polymarket's free price history (Polymarket's from
2020), measured as markets readers bet in, then as a free expected value for an election (step 10).
They are the betting markets the project's first statement of intent named beside stocks and
crypto.

### Phase 5: the kinds the news brings

Opened 2026-11-17 by the owner ([why](decisions.md#2026-11-17-widen-the-kinds-now-by-the-owner)).
Each a dated history of past events, measured as step 17 measures a kind (what followed, over
spans, against the base rate, walk-forward), one kind per pull request, its spec and expected
outcome written first and read by a goldfish. A hot event of a measured kind is filed by hand as a
step 18 trigger; reading the news into kinds waits in the backlog below.

| # | Step | Where it stands |
| --- | --- | --- |
| 24 | **[OPEC+ decisions](steps/opec.md)**: output cuts and rises, against Brent (stored), gasoline and the indexes | **Done** 2026-11-17 ([results](steps/opec.md#results)): from the close before, energy stocks and gasoline move with the kind on the day and the week, and gasoline's day after *oil up* holds walk-forward (20 of 31); from the reaction close, about chance; the IMF's cut/hold/boost answers no cell on 89 meetings, most too few |
| 25 | **[Other central banks](steps/other-central-banks.md)**: the Bank of England's and the Bank of Japan's rate decisions, against the pound, the yen and their bonds, as the Fed and the ECB are | **Done** 2026-11-18: 187 BoE decisions from 2008 and 85 BoJ from 2016 with a kind; the pound, the yen and the Nikkei added, unsigned; BoE days move more, but no direction beyond chance and nothing holds walk-forward, as expected; the pound *can't say* after a BoE move |
| 26 | **War and military strikes**: the dated outbreaks and major strikes, against oil, gold, defence stocks and the indexes. *Amended 2026-11-18* ([why](decisions.md#2026-11-18-war-is-measured-as-icbs-violent-acts)): every international crisis a violent act set off, by ICB's list | **Done** 2026-11-18 ([results](steps/war.md#results)): 136 violent acts, 1970 to 2021; gold *up* after them over the day, the week and the month (23 of 37 up over the week), too few walk-forward; oil and defence stocks *can't say*; one answer above the chance bar from the close before |
| 27 | **Crypto shocks**: exchange collapses, hacks, ETF approvals and halvings, against bitcoin, ether and coin stocks. *Amended 2026-11-18:* hacks of $100 million or more from DefiLlama's list; collapses have no free dated list, ETF approvals and halvings are too few ([spec](steps/crypto.md#what-this-step-does-not-do)) | **Done** 2026-11-18 ([results](steps/crypto.md#results)): 44 hacks, 2014 to 2026; bitcoin, ether and Coinbase *can't say* on every span; one answer in all, within chance; as expected but for the week's counts |
| 28 | **Weather and climate**: hurricane landfalls, floods and droughts in crop-growing regions, each with one start day, against crops, fuel and insurers. *Amended 2026-11-18:* US hurricane landfalls from NOAA's HURDAT2, Allstate as the insurer; floods and droughts have no single start day in a free record ([spec](steps/weather.md#what-this-step-does-not-do)) | **Done** 2026-11-18 ([results](steps/weather.md#results)): 79 landfalls, 1970 to 2024; fuel, energy stocks, the crops and Allstate *can't say* but wheat *about the same* on the day from the reaction close; two answers in all, within chance |
| 29 | **[Ask about phase 5's kinds](steps/ask-phase-5.md)**: the page's *Ask the fortune teller* answers OPEC+, the BoE and the BoJ, violent acts, hacks and landfalls, as step 22 answers the first seven flows. Chosen 2026-11-19 by the owner | **Done** 2026-11-20: 12 kinds, 1,116 cells on the published page, each equal to `follows`; gasoline's day after *oil up* the one new hold, Brent's day grey as the kind ([results](steps/ask-phase-5.md#results)) |
| 30 | **[Floods](steps/floods.md)**: NOAA's billion-dollar US floods with a day, 39 from 1980 to 2024, against crops, fuel, insurers and the indexes. Chosen 2026-11-19 by the owner as floods and droughts; droughts left out, as they have no day | **Done** 2026-11-19 ([results](steps/floods.md#results)): nothing follows a flood; one answer a run, within chance; too few to hold |
| 31 | **[Earnings](steps/earnings.md)**: the Dow's members' quarterly EPS against the consensus, above, as expected or below, each company against the S&P 500. Chosen 2026-11-19 by the owner | **Done** 2026-11-19 ([results](steps/earnings.md#results)): 2,068 reports, 2008 to 2026; from the close before, a miss and an in-line report *down* on every span, a beat *up* over the week and month; a miss's day and week and an in-line report's day hold walk-forward; from the reaction close only a miss's day answers |
| 32 | **[Ask about earnings](steps/ask-earnings.md)**: the page's *Ask the fortune teller* answers a Dow company's report above, in line with or below the consensus, as step 31 measured it; every cell on the page carries the placebo's mark, *the period*, as `follows` prints it; the members' closes loaded every evening. Chosen 2026-11-19 | **Done** 2026-11-20: the published page answers the three earnings kinds, all 2,988 cells equal to `follows`, three period marks and seven holds, as expected ([results](steps/ask-earnings.md#results)) |
| 33 | **[The earnings kept current](steps/earnings-current.md)**: step 31's reports refreshed each Monday by hand, a pull request a week, the recent pages fetched again while Nasdaq fills them, to the gate. Chosen 2026-11-20 | **In progress**: step 1 done (the scripts); the first refresh, 2026-11-23, added Walmart's report of 2026-11-19, as expected, and changed no answer ([results](steps/earnings-current.md#results)); next, each Monday to the gate |
| 34 | **[A same-day source for earnings](steps/earnings-same-day.md)**: Yahoo's `earningsHistory` measured against Nasdaq, the same kind on at least 90% of 60 reports, and within 2 hours of the 8-K. Chosen 2026-11-20 by the owner | **In progress**: step 1, the same kind on 102 of 110 (92.7%), over the bar; the speed asked on the reports to 2027-01-31 |
| 35 | **[S&P 500 additions](steps/sp500-additions.md)**: each company S&P announced would join the S&P 500, 2007 to 2026, against the index, from the announcement. Chosen 2026-11-20 by the owner | **Done** 2026-11-20 ([results](steps/sp500-additions.md#results)): 143 kept; the day *up*, 85 of the 135 that moved, chance 0.0098, but it does not hold walk-forward (30 of 53); the week and the month *can't say* |
| 36 | **[Earnings beyond the Dow](steps/earnings-sp500.md)**: the S&P 500's members' reports from 2011, measured as step 31's, on a copy of the store. Chosen 2026-11-20 by the owner | **Done** 2026-11-20 ([results](steps/earnings-sp500.md#results)): 24,298 reports; a miss's day *down* and **holds**, 2,506 of 3,798 (66%); the miss's week (59.5%) and the in-line day do not hold, as they did on the Dow |
| 37 | **[Stock splits](steps/stock-splits.md)**: S&P 500 members' forward splits from 2011, each at its first public news, alone or with an earnings report, against the index. Chosen 2026-11-20 by the owner | **Done** 2026-11-20 ([results](steps/stock-splits.md#results)): 105 splits; one announced alone is followed by *up* on the day, and it **holds**, 33 of 51; in an earnings release *can't say* |
| 38 | **[A CEO's conduct, no departure](steps/ceo-conduct.md)**: step 20's part 1b, from S&P 500 members' 8-Ks found by the SEC's full-text search. Chosen 2026-11-20 by the owner | **Ended** 2026-11-20 at step 1 ([results](steps/ceo-conduct.md#results)): 24 members' 8-Ks, none a CEO who stayed; 0 kept, the kind stays parked |
| 39 | **[An exact meet](steps/exact-meet.md)**: an EPS equal to its forecast, which Nasdaq prints as `N/A`, read as *as expected* in both earnings seeds; Precision's trigger | **Done** 2026-11-20 ([results](steps/exact-meet.md#results)): 119 Dow and 1,685 S&P 500 reports added; the Dow's in-line day still holds, 229 of 368; its week now *the period* |
| 40 | **[Big moves and the news filed with them](steps/news-moves.md)**: S&P 500 members' days of a move three deviations or more against the index, from 2011, matched with the 8-K items filed that day, each against its share on every day; a hand-read sample of the big moves with no 8-K. Chosen 2026-11-21 by the owner | **Done** 2026-11-21 ([results](steps/news-moves.md#results)): 1.63% of 1.7 million member-days are big moves; a results 8-K makes one 19.6 times as likely, but 61.6% of big moves have no 8-K; of 40 read by hand, mostly the industry's or the economy's news (17) or nothing found (19); no item leans up or down |
| 41 | **[Hypotheses from an expert reader](steps/expert-hypotheses.md)**: a language model, as an economics and statistics expert, reads the records to 2019 and writes 40 testable rules (a kind, a condition before it, a market, a span, a direction); each tested once on 2020 onward by the usual bars, those that pass graded forward. Chosen 2026-11-21 by the owner | **Done** 2026-11-21 ([results](steps/expert-hypotheses.md#results)): 40 rules, all testable; 5 pass and 2 hold, every one a restatement of the record (2 by the OPEC kind's own definition); none of the 15 with a condition passed. The 4 passes that do not hold graded forward to the gate |
| 42 | **[Who a macro event hits: exposure scores](steps/exposure-scores.md)**: the Subscription LLM scores each S&P 500 member's 2019 10-K business text on signed rubrics (oil, rates, consumer spending), Karpathy's pattern with the safeguards; the scores tested on OPEC+, CPI, Fed and retail events from 2020, and against a sector baseline. Chosen 2026-11-21 by the owner | **Done**: 426 members scored, the second reading 100% within 2 points; only oil on OPEC+ *oil down* answers (15 of 18, day and week), within chance and near the kind, the industry sorting as well; nothing holds or beats its sector. Forward to the gate |
| 43 | **[Good or bad, read from the filing: 8-K severity](steps/filing-severity.md)**: the Subscription LLM scores 400 S&P 500 members' 8-Ks of 2020 to 2025 (items 2.05, 3.02, 5.02, 7.01, 8.01, no results) from −5 to +5 for shareholders; the score's sign tested against the shares' move on the index, day and week. Chosen 2026-11-21 by the owner, after step 42 | **Done**: 43 bad, 22 good of 400; after bad filings the shares trailed on 27 of 43 days (p 0.06), short of an answer; good no better than chance; nothing holds. Forward to the gate |
| 44 | **[A page a stranger reads](steps/readers.md)**: the first screen on what the page offers and the answers that hold; market names, the statistics in a closed *workings*; the Dow's reports of the next seven days with what followed each kind; the same in the weekly post. For step 23's readers. Chosen 2026-11-21 by the owner, after a first-visitor review | **In progress**: the spec |
| 45 | **[The S&P 500 on the page](steps/sp500-on-the-page.md)**: steps 35 to 37's groups (S&P 500 earnings, additions, splits) on *Ask*, measured once on a copy of the store and frozen with their day; the reports ahead every S&P 500 member's, under the earnings kinds' lines; the post names the five largest. Chosen 2026-11-21 by the owner | **In progress**: the spec |
| 46 | **[The loop's safety nets](steps/loop-nets.md)**: the runner's morning watches the laptop's rows and its own evening; the laptop's evening watches the runner's morning; each opens an issue for what the other missed. A source's HTTP 5xx or broken connection asked again twice, five minutes at most per run. Chosen 2026-11-21 by the owner | **In progress**: steps 1 and 2 built, the retry and the watches; next, two release days live |
| 47 | **[Fortuneteller predicts](steps/predicts.md)**: a page at `/predicts/` with one to five dated *if* cards from what holds (the largest S&P 500 report of each day ahead, a release whose link holds), each with its record as counts, rewritten each weekday; designed light and dark, at phone width. Asked for 2026-11-21 by the owner | **In progress**: built |
| 48 | **[Stated forecasts](steps/stated-forecasts.md)**: the predictions page says what will happen, from a market's own long run where it holds walk-forward over spans that do not overlap, and after news that has landed where its cell holds; each kept in `forecasts.csv` and graded. Asked for 2026-11-21 by the owner | **In progress**: 5 of 29 pairs hold, all *up* (the S&P 500 and the Nasdaq at a month and a year, home prices at a year); none for tomorrow |
| 49 | **[Our guesses](steps/our-guesses.md)**: the Subscription LLM guesses from the day's news, one market up or down over a week or a month, headed *Our guess*, kept before its span and scored apart; the page drops its *if* cards. Asked for 2026-11-22 by the owner | **In progress** |
| 50 | **[The guess ledger](steps/guess-ledger.md)**: up to 50 guesses an evening, each with end date, reasoning, tag and confidence; graded by the closes, reviewed by the model, learned from in monthly lessons; five at most on the front page (one per area since 2026-11-25, step 61), every one on a stats page. Asked for 2026-11-22 by the owner | **In progress** |
| 51 | **[The front page's guesses, approved](steps/front-staging.md)**: each evening the guesses the front page would show go into a pull request of their own, reworded or removed by the owner and published when it is merged; the ledger stays as it is. Asked for 2026-11-22 by the owner | **In progress** |
| 52 | **[Canada](steps/canada.md)**: the Bank of Canada's decisions and Canada's inflation against every market, the Canadian dollar and Toronto's stocks added. Asked for 2026-11-22 by the owner | **Done** 2026-11-23 ([results](steps/canada.md#results)): 153 BoC decisions and 189 lone inflation releases; nothing holds walk-forward; the BoC's 12 answers from the close before exceed chance plus 2, and the Canadian dollar strengthens on the day of a hike (13 of 19), too few to replay |
| 53 | **[China](steps/china.md)**: China's inflation and its other reports with forecasts against every market, the yuan and Shanghai's stocks added. Asked for 2026-11-22 by the owner | **Done** 2026-11-23 ([results](steps/china.md#results)): 116 inflation, 59 survey, 110 output and 127 trade releases alone; nothing holds walk-forward, every flow's answers below chance; the yuan weaker on the day exports miss (25 of 42), too few to replay |
| 54 | **[Switzerland](steps/switzerland.md)**: the Swiss National Bank's decisions and Swiss inflation against every market, the franc and Zurich's stocks added. Asked for 2026-11-22 by the owner | **Done** 2026-11-24 ([results](steps/switzerland.md#results)): 80 SNB decisions and 152 inflation releases alone; nothing holds walk-forward, both flows' answers below chance; the franc moves 1.9 times its usual size on the SNB's days alone, in no set direction |
| 55 | **[Guesses against the base rate](steps/guesses-vs-base-rate.md)**: every guess carries its market's base rate and the record is judged by how far guesses beat it; a *grounded guesser*, given the base rates and the forecasts that hold, runs each evening beside today's *news guesser* as the control, its prompt refined one numbered change at a time to the 2027-01-31 gate, then frozen and read against the control on 2027-04-30. Asked for 2026-11-23 by the owner | **In progress**: the spec |
| 56 | **[What the page claims, corrected](steps/honest-page.md)**: the business review's required fixes of 2026-11-24: a guess graded from its market's first close after it was made, hand-made guesses apart from both guessers' records, no single companies; a shown card stays until graded or is marked withdrawn; the long-run cards labelled *the usual way*, counts instead of tenths, guesses with a look of their own, day-after cells marked as reactions, a no-position line; the earnings seeds without the consensus figures. Chosen 2026-11-24 by the owner, before step 57 (the technical review's fixes) and step 58 (the publishing schedule) | **Done** 2026-11-24 ([results](steps/honest-page.md#results)): two expected outcomes wrong as first written: a guess made at a weekend started from that day, so ten base rates counted a weekday too many, fixed and recomputed; and the page drops a card at its end date, not at its grade, the rule amended to that; four points of the page still unclear to a reader; the earnings outputs byte for byte the same without the consensus figures; a reader with no financial training explained each card back |
| 57 | **[The technical review's required fixes](steps/technical-fixes.md)**: the cache keeps no error reply, a moved release leaves no copy, OPEC's cells judged only from the reaction close, a release alone by its reaction close, the jobs on their own checkout and store, the evening's model without `.env`, a bad guess dropped not fatal, a call logged once, bp moves rounded, the fallback forecast's unit checked, the evening's page merged apart from the triggers. Chosen 2026-11-24 by the owner, after step 56 and before step 58 (the publishing schedule) | **Done** 2026-11-25 ([results](steps/technical-fixes.md#results)): eleven fixes in #445 to #461; OPEC's one answer that held, gasoline's day after *oil up*, was counting the close that decides the kind and goes; R9's rounding moved the counts of 2,140 cells, not under 10, but no answer that holds; R4 changed no answer that holds |
| 58 | **[The publishing schedule](steps/publishing-schedule.md)**: each day's guesses drafted at 14:00 New York, a reminder at 16:00 if not approved, published at 18:00 as they stand, weekends too; the draft printed in full for the owner's approval. Chosen 2026-11-24 by the owner, after step 57 | **In progress**: built |
| 59 | **[Crypto's weekend closes](steps/crypto-weekends.md)**: bitcoin's and ether's Saturday and Sunday closes kept from Yahoo, which the price loader now drops for every market; a crypto guess made at a weekend graded from its next close. Chosen 2026-11-24 by the owner, after step 58 ([why](decisions.md#2026-11-24-bitcoins-and-ethers-weekend-closes-from-yahoo-after-step-58-by-the-owner)) | **In progress**: built |
| 60 | **Polymarket's busiest markets as a guide**: which kinds of events its busiest prediction markets ask about, read to choose the kinds phase 5 adds next; each chosen kind is then measured as any other, from free sources, and Polymarket's prices are never a forecast or a grade. Its terms on reuse and its reach from here are checked first. Chosen 2026-11-24 by the owner, after the 2027-01-31 gate | **Planned** |
| 61 | **[One front-page card per area](steps/front-by-area.md)**: the predictions page shows at most one card in each area (stocks, interest rates, currencies, energy, gold, food, crypto, homes), long-run forecasts and guesses alike, so an evening's guess in an empty area joins at once. Today the page holds five cards, and three long-run cards plus three guesses kept until graded fill it to 2026-12-04, two of them stocks. Chosen 2026-11-25 by the owner, after step 57 and before step 58 ([why](decisions.md#2026-11-25-one-front-page-card-per-area-after-step-57-by-the-owner)) | **Done** 2026-11-27 ([results](steps/front-by-area.md#results)): the page shows 8 cards, one per area, with no sideways scroll at 420 and 1,280 pixels; the first evening's proposal was the expected areas |
| 62 | **[Big moves, explained](steps/big-moves-explained.md)**: each weekday's big moves in the markets we track found from the closes, checked against our open calls and guesses, and their reason found in the news; the day's news scanned for big moves in markets we do not track. December 2026 read in January. Asked for 2026-11-26 by the owner ([why](decisions.md#2026-11-26-big-moves-explained-and-the-news-scanned-for-markets-we-miss-by-the-owner)) | **In progress**: built |
| 63 | **[The 2-year yield](steps/two-year-yield.md)**: the US 2-year Treasury yield from FRED's `DGS2`, signed as the 10-year, against every flow; a link on it that holds is called live. Chosen 2026-11-27 by the owner ([why](decisions.md#2026-11-27-new-sources-the-2-year-yield-first-then-us-releases-with-forecasts-by-the-owner)) | **Done** 2026-11-27 ([results](steps/two-year-yield.md#results)): up after a jobs report above the forecast (69 of 105 right walk-forward) and after ISM above it (36 of 49), both hold; the jobs report's called live; nothing on retail sales or CPI, against the expected outcome |

**Backlog:** news read into these kinds by a small model on this machine (Gemma 3 4B or Qwen 2.5
3B, or Inkling 2 Mini, a 26B model with about 5B active, *added 2026-11-21*), tested on a fresh labelled set: step 20's parked next try, widened to phase 5's kinds.

Later, not planned in detail, each chosen one at a time after the gate: free expected values
beside the consensus, the Cleveland Fed's PCE nowcast first (its CPI nowcast is step 4's baseline already, *corrected 2026-11-21*), then the
Philadelphia Fed survey's history for GDP ([free sources](free-sources.md), *added 2026-11-21*); new kinds of
events, each a dated history before a flow (droughts, once a free source dates them by day;
crypto's own news; OPEC+, floods and earnings were measured in steps 24, 30 and 31); a CEO's
conduct with no departure (step 20, part 1b); the page's words for the figures, once rung 3's rule allows a percentage; and what-if stories
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
