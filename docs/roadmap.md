# Roadmap

> Why this plan has this shape — the target, the idea being tested, and the principles behind the
> ordering — is in the [Legend](legend.md). Unfamiliar acronym, ticker, or term? Every one is
> explained in the [Glossary](glossary.md).

## The goal

Given an event, say which instruments move, by how much, in which direction — with confidence that
means something. A warning product, not HFT: the latency budget is seconds to minutes.

*Amended 2026-10-23:* an entertainment tool with a realistic approach, not a financial one
([Legend](legend.md#the-target)). The bars stay; the surface widens.

*Amended 2026-11-04:* a reader of the news, told what follows for the markets behind what they pay
for, over spans from a day to a year ([Legend](legend.md#the-target)).

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

Decided 2026-10-07, after rung 1: sharpen the measurement before predicting, then predict, then
widen. Each new expected value is one expectation source and each new event one event flow
([Extending](extending.md)).

| # | Step | Why now |
| --- | --- | --- |
| 1 | **[A free forecast of each jobs report](steps/nfp-forecast.md)** — ADP and jobless claims, fitted on earlier reports only. **Done**: both links pass since 2014, against the forecast and the trend alike; the full history stays unclear | The yield's and the dollar's jobs-report links sit just under the bar against the trend; a real forecast is the known shortcut, and it is free |
| 1a | **[Country-aware events](steps/country-aware-events.md)** — a flow is its event type and origin country; trends and reports per flow; each market's own time zone. **Done** | Events are told apart by type alone, so a second country would mix with the US's; cheap now, before more depends on it |
| 2 | **[A free consensus, as context](steps/free-consensus.md)** — Nasdaq's published consensus for CPI and payrolls, 2008 to today, checked against TradingView's, judged beside the trend on the same reports. Chosen 2026-10-09 over paid data; paid consensus and intraday prices deferred, not dropped. **Done**: the jobs report's yield and dollar links pass, and more strongly; CPI's dollar passes against the consensus only | The expected value traders actually saw, for free; the jobs-report forecast showed a model is not the shortcut |
| 3 | **[Predict the next release](steps/rung-2-predict.md)** — rung 2 below: a walk-forward test of claim 3 on every signed link, then a prediction for a new release's actual. **Done**: the jobs-report dollar and yield hold (the yield barely beats drift); CPI's links are too few | Built on whichever links pass after steps 1–2 |
| 4 | **[More events](steps/step-4-more-events.md)** — retail sales, core PCE, GDP, each one event flow and each run up rungs 1–3; ECB decisions wait for step 4a. **Done** 2026-10-12: retail sales' yield holds walk-forward; core PCE and GDP give no calls | Widens what the measured core covers, and gives rung 3 more calls |
| 4a | **Cross-country effects** — part 1, [US releases and Europe's stocks](steps/cross-country.md), **done** 2026-10-21: Europe moves on Fed decisions and follows CPI's surprise more than New York, short of *tracks*. Part 2, [ECB decisions](steps/ecb-decisions.md), **done** 2026-10-22: they move the dollar, not Europe's stocks. Part 3, [euro-area inflation](steps/euro-inflation.md), **done** 2026-10-22: the flash moves New York, probably by another release that day, and nothing follows its surprise. The whole step: non-US markets with their country; moves and surprises in standard units; `effect_size_matrix` per (event type, origin country) × market; a report per affected country | One event has one surprise, but a different power in each country's markets; measuring that needs markets abroad, which come with more events |
| 4b | **[The US manufacturing survey (ISM)](steps/ism-manufacturing.md)** — one more US flow, from TradingView, chosen 2026-10-23. **Done** 2026-10-23: the yield and the dollar track its surprise, short of *holds* walk-forward; it explains part of New York's flash-day move | Part 3 of step 4a found New York moving on euro-area flash days and named ISM, released the same morning, as the likely cause, untested |

Decided 2026-10-23, after step 4b, with the target amended: the five monthly flows added since
step 4 gave no new call, nothing built reaches anyone but the laptop's popup, and the taxonomy's
other half (statements, shocks, news) is unmeasured. So: show what is measured, raise the call
count once, then widen events and markets, with every bar unchanged. A statement nobody scheduled
is never called before it happens: for news the product is a graded reaction record (*retired
2026-11-04*, below: an event that has happened is answered for the spans after it), and for a
scheduled statement a preview. Counts checked 2026-10-23 on the calendars already cached.

| # | Step | Why now |
| --- | --- | --- |
| 5 | **The scoreboard** — a static page the evening job writes from the calls log and the score: every call and its grade, every link's record, every event's verdicts for every market, and how many *moves* chance alone would give at these counts | Everything below is a table nobody sees without it. A static page is not a web service, so no graduation trigger fires |
| 6 | **[Jobless claims](steps/jobless-claims.md)** — the weekly US release (Thursday 08:30 New York, about 700 since 2013 with a forecast) as a flow with its surprise, called live by the morning job. **Measured** 2026-10-27: nothing moves on its lone days, the yield follows the surprise short of *tracks*, no call; live every Thursday from 2026-10-29. *Amended 2026-11-02* ([own years](steps/own-years-baseline.md#results)): six markets move on its lone days | The only event that beats the sample wall: about 50 calls a year against 12 for a monthly one |
| 7 | **[More outcomes](steps/more-outcomes.md)** — oil, EUR/USD, the Nasdaq, the 5-year yield, the FTSE 100, the STOXX 600, bitcoin, a defence and an energy ETF, each with its close and zone; "does it move?" only, unless a sign is written down first. **Measured** 2026-10-27: the 5-year yield the most responsive market, holding walk-forward on the jobs report, retail sales and ISM; the euro the dollar's mirror, holding on the jobs report; the Nasdaq moves on seven events (two from [own years](steps/own-years-baseline.md#results), 2026-11-02); Brent and energy on ISM days only, bitcoin and defence on none | Free on Yahoo with daily history; every verdict table gains rows, and oil and defence are the natural outcomes of step 10's shocks. More cells mean more *moves* by chance: the scoreboard says how many |
| 8 | **[Scheduled statements](steps/scheduled-statements.md)** — the Fed chair's and the ECB president's speeches and testimonies as two flows, "does it move?" only; the morning job previews a scheduled one with its record. *Amended 2026-10-29:* press conferences left out, each on its decision's day. **Measured** 2026-10-29: the Fed chair moves nothing; the ECB president's three *moves* (VIX, Brent, the Nasdaq) do not survive the era split, and the pooled baseline's trigger has fired. *Amended 2026-11-02* ([own years](steps/own-years-baseline.md#results)): the president moves the Euro Stoxx 50 and Brent. **Preview built** 2026-11-02 | The cached calendar holds 5,644 timed Fed and ECB statements since 2013, none with an expected value, so no surprise. Only the chair's and the president's are events: 1.7 statements a trading day would leave no ordinary day |
| 8a | **[Ordinary days from each flow's own years](steps/own-years-baseline.md)** — the raw move's ordinary days from each flow's first reaction day on each market, before the statements' preview. *Added 2026-10-29*. **Done** 2026-11-02: 60 of 192 cells changed, *moves* 52 → 54, no call; the Nasdaq moves on two flows instead of nine, lone claims days on six markets; the new trigger fires on the president's Brent | Step 8 fired precision's *loud and quiet years* trigger: the five flows from 2013–14 are judged against decades they have no days in, and the preview would announce what that tilt makes |
| 9 | **[Germany's calendar](steps/germany-calendar.md)** — ZEW and Ifo (10:00 and 11:00 Frankfurt) and the German flash CPI, the first European surprises with a forecast history. *Chosen 2026-11-02. Amended 2026-11-02:* ZEW lands at 11:00 and Ifo at 10:00; Ifo's history on TradingView starts in 2018; all three lesser flows, so every existing output stays. **Done** 2026-11-02: the surveys move nothing; the euro tracks the German flash CPI's surprise, short of *holds*, no call | A `DE` fetch of the same calendar. Whether Europe reacts to its own survey news, after the ECB and the flash showed it reacting mostly to the US |
| 10 | **Dated shocks** — elections (US, European Parliament, Germany, France, UK), tariff announcements, debt-ceiling deadlines and summits as hand-written dates in a seed CSV; "does it move?" and for how long (`ret_1w`). *Amended 2026-11-02:* four parts, one spec each; part 1, [elections](steps/elections.md), chosen first, the dates objective and decades long; *too few* under ten days a cell; "for how long" as a five-day ratio from `raw-move --week`, not `ret_1w`. *Amended 2026-11-02:* part 2, [tariff actions](steps/tariffs.md): the president's signed documents from the Federal Register since 2018, not hand-picked announcements. *Amended 2026-11-03:* part 3, [the debt limit](steps/debt-limit.md): the day Congress cleared each law that changed the limit since 1970, not deadlines, which have no date until they pass. *Amended 2026-11-03:* part 4, [summits](steps/summits.md): the G7's and the G20's annual leaders' summits, 70 days as one lesser flow dated by the last day. **Done** 2026-11-03: a US election moves American stocks for a day, and France's VIX; a tariff signing Europe's indices, on the day and over the week; Congress's final debt-limit vote both Treasury yields, on the day and over the week; a summit only the dollar, on the day, unconfirmed | The taxonomy's other half, measured honestly; the n is tiny by nature and the page says *too few* |
| 11 | **News as a feed** — GDELT, one narrow question first: the US president's statements on trade since 2015, against oil, stocks and the dollar, with the bar fixed before measuring. *Amended 2026-11-03:* part 1, [the president's trade posts](steps/presidential-posts.md): GDELT measured first cannot date them (its coverage follows the market, it names no speaker and has no trade topic), so the days come from the president's own archived tweets in his first term, compared inside that term; part 2, his second term, waits for a committed record of its posts. **Measured** 2026-11-03: no market moves on a tweet day or over the week; six are unclear. *Amended 2026-11-03:* [part 2](steps/presidential-posts-2.md), the second term's Truth Social posts, from a frozen snapshot of CNN's archive, the committed seed being the record. **Measured** 2026-11-03: no US market moves on a second-term post day; bitcoin alone, clustering not excluded. **Closed with no** by the rule written first: no US market moves on the president's trade posts; news in general is not measured | The only free news-event history with actors and tone, and noisy. Decides whether a feed is worth building on before any detection machinery (rung 7) |
| 12 | **[Beat the fortune teller](steps/beat-the-fortune-teller.md)** — a person's call logged before the release, graded beside the machine's on the same rules and shown on the scoreboard. *Added 2026-11-03* from the list below, after step 11 closed | The Legend's 2026-10-23 amendment: an entertainment tool that shows its record; being seen counts as progress. Needs no new data or model |
| 13 | **[The Fed statement's tone](steps/fed-statement-tone.md)** — each Fed statement's hawkish or dovish tone from a published word list (Apel and Blix Grimaldi, 2012), against the previous statement's, as the Fed flow's surprise; the verdict on holds. *Added 2026-11-03* from the list below. **Stopped** 2026-11-03 by its rule: the list reads 19 of 226 statements, one hold a link, untested | The Fed moves six of seven markets with no surprise test; its statements are free text, and a word list needs no paid model |
| 14 | **[The Fed statement's sentiment](steps/fed-statement-sentiment.md)** — step 13's question with Gardner, Scotti and Vega's dictionary built from the FOMC's own statements (FEDS 2021-074): topic keywords paired with the nearest modifier, against the previous statement, the verdict on holds. *Added 2026-11-03* by the owner after step 13 stopped. **Done** 2026-11-03: the dictionary reads every statement and passes the paper's checks; all four signed links *doesn't*, no call | Step 13's list could not read the Fed's phrasing; this one was built from it |
| 15 | **[The week ahead](steps/week-ahead.md)** — the scoreboard opens with each release `live` calls in the next seven days: the consensus, the threshold either side, and what each signed link will call, with its replay record; never a call before the number. *Added 2026-11-04* toward the owner's restated goal, a tool ordinary people can read. **Done** 2026-11-04: the jobs report's four links preview with *holds* records, CPI's with *too few* | Everything shown so far is the past; a reader cannot see what is coming or what a call hinges on. Needs no new data or model |
| 16 | **[The week ahead, without a call](steps/watch-ahead.md)** — the scheduled events `live` does not call (Fed and ECB decisions, their heads' statements, the euro-area, ISM and German releases) listed in the week ahead with how markets moved on such days before; no direction. *Added 2026-11-04* by the owner after step 15. **Done** 2026-11-04: the table lists ZEW, Ifo and the rest with their record, no direction | A reader can watch more than six US releases; the record already exists |

Decided 2026-11-04 by the owner, with the target amended ([Legend](legend.md#the-target)): a
reader of the news, told what follows for the markets behind what they pay for, over spans of a
day, a week, a month (21 closes), a quarter (63) and a year (252). Build on what exists first:
decisions, then a trigger standing in for the news, then the markets people feel, then real news.
Predicting is built before collecting. The goal covers many countries; steps 17–20 are the US's,
and each further country (the euro area and Germany first, their events already stored) follows
as its own parts once the US answers hold. Each step gets its own spec, bars written first.

| # | Step | Why now |
| --- | --- | --- |
| 17 | **What follows, over spans** ([part 1](steps/what-follows.md), Fed decisions over a day, a week and a month; [part 1b](steps/what-follows-jobs.md), the jobs report by kind, taken 2026-11-04 before part 2; [part 1c](steps/what-follows-retail.md), retail sales by kind; [part 1d](steps/what-follows-cpi.md), CPI by kind, from its headline; *amended 2026-11-04:* a release with a surprise is answered by its kind too, above, as expected or below, for the week and the month its links never measured) — for the flows whose direction no surprise gives (the thirteen with no surprise rule, and the Fed, whose sentiment rule calls nothing), the signed move after each past event over each span, against the base rate ([Legend](legend.md#the-target)), replayed walk-forward; *up*, *down*, *about the same* or *can't say*, with the counts, and how many *up* or *down* chance alone gives at these counts. A decision's kind is what was decided: cut, hold or hike, the Fed's from its stored target rate (`target_rates`, `is_hold`), the ECB's from the calendar's actual rate, which `parse_ecb_decisions` reads and drops today. Parts, one spec each: Fed decisions over a day, a week and a month first; then the quarter and the year, where spans overlap and a cut cycle is one episode, not eight events, with the test for that fixed in the spec; other US flows one at a time; the ECB's with the euro area, the first country after the US. **Part 1 measured** 2026-11-04: nothing holds walk-forward; four answers on all history against 4.3 by chance; VIX falls on the day of a hold, right on 51% walk-forward, short of 60%. **Part 1b measured** 2026-11-04: after a jobs report above the consensus the 10-year and 5-year yields rise on the day and hold walk-forward (67%, 65%); 13 answers on all history against 4.3 by chance. **Part 1c measured** 2026-11-04: retail sales by kind holds nothing; 5 answers against 4.3; after a release below the consensus both yields fall on the day, right on 56% and 51% walk-forward. **Part 1d measured** 2026-11-04: CPI by kind, from its headline, holds nothing; 6 answers against 4.3, all after a cooler print and all *can't say* without its shared days. *Amended 2026-11-11:* [part 1e](steps/what-follows-claims.md), jobless claims by kind, the only flow left whose every kind can reach 30 graded; claims triggers with it. **Part 1e measured** 2026-11-11: claims by kind holds nothing; 8 answers against 6.8 by chance, the yields leaning the expected way on the day, six of them *can't say* without the shared days. *Amended 2026-11-11:* [part 1f](steps/what-follows-ecb.md), the ECB's decisions by kind, from the deposit rate where the calendar lists it and the refinancing rate before; only a hold can hold; ECB triggers with it. **Part 1f measured** 2026-11-11: nothing answers, none of 225 cells against 6.8 by chance. *Amended 2026-11-12:* [part 2](steps/what-follows-long.md), the Fed's decisions over a quarter and a year, an answer standing only if it also holds counting each cut cycle, hike cycle and run of holds once | Today a direction comes only from a surprise; a signed move is stored only over a day (`ret_1d`), and the week is an unsigned five-close move computed for `raw-move --week`. Needs no new data: every price series is stored from its start |
| 18 | **A trigger arrives** ([part 1](steps/after-the-day.md), what follows from the next close, measured 2026-11-04: nothing holds on any flow, 20 answers against about 17 by chance; [part 2](steps/trigger-file.md), the file and the log; *amended 2026-11-04:* in two parts. Part 1 measures step 17's method on spans that start at the reaction close, the only move not seen when a trigger is merged; "step 17's figures" below means those. Part 2 is the file and the log: a trigger counts on a market only if merged before that market's reaction close, takes its event's time and kind from the store, and lists the events filed late or not at all) — a hand-written file of triggers (the flow, what was decided, the day) stands in for the news; each is dated by the merge of the pull request that adds it, as a guess is, and answered, once it has happened, with step 17's figures for every span starting after that. One row per trigger, market and span in a log of its own, graded from the stored closes when the span's last close is in; `data/calls.csv` and `score` stay as they are | Predicting apart from collecting, as the owner chose: the answer is tested and graded before any news is read. The file names the flow, so nothing matches news to flows until step 20 |
| 19 | **The markets people feel** ([part 1](steps/markets-people-feel.md); *amended 2026-11-04:* corn, wheat, soybeans, gasoline and natural gas through the funds that hold their futures, whose prices do not jump on a roll; utilities and homebuilders; all unsigned. Coffee, which has no fund, the breakeven and any sign wait for part 2. *Amended 2026-11-04:* part 2 is three, one set of markets each: [2a, coffee](steps/coffee.md), through its front month with the roll measured; [2b, the breakeven](steps/breakeven.md), from FRED; 2c, the signs, weighed against what `live` would call. *Amended 2026-11-05:* before 2c, [the scoreboard, faster](steps/scoreboard-faster.md): its rebuild takes 826 s against a 15-minute bar. *Amended 2026-11-05:* [2c](steps/signs.md) signs utilities and homebuilders only; the breakeven's sign waits for the evening grade to wait a day for FRED's close, the next step, since a call on it would stop the evening job for every market. *Amended 2026-11-09:* that step is [2d, the breakeven's sign](steps/breakeven-sign.md), +1 on inflation news only) — coffee, wheat, corn, soybeans, gasoline and natural gas futures, utilities and homebuilder stocks from Yahoo, and the 5-year expected inflation (breakeven) from FRED by `fetch_series`; each a row in `MVP_PRICE_SERIES` with its close, zone and unit and a sign in `with_more_outcomes`; the raw move and step 17's spans on the flows that exist. Each series checked for its start, frequency and roll days before measuring, and how futures rolls are treated written first | The reader's everyday things, through free daily markets. Mortgages need nothing new: they follow the 10-year and 5-year yields already stored |
| 20 | **News into triggers** — a free news source read into step 18's triggers, by rules first and a model on this machine if rules fall short (starting from the unified prompt in `docs/legacy/event-polarity-and-classifier-prompts.md`); first on one stored unscheduled kind, tariff actions, checked against the stored flow as its list of known events before any answer rests on it. Step 11 found GDELT unable to date one speaker's posts; this asks only for kinds of events and their days | What the owner asked for: the tool finds the event itself. Waits until step 17's replay passes and step 18 has graded day and week answers |

Later, not planned in detail, each chosen one at a time after step 18's results: new kinds of
events, each a dated history before a flow (OPEC decisions against Brent, already stored; floods
and droughts in crop-growing regions, with one start day each; earnings reports, with the single
companies' prices they need; crypto's own news); the page's words for the figures, once rung 3's
rule allows a percentage; what-if stories for what has no past, labelled as reasoning and kept
apart from graded records; and prediction-market prices as an election's expected value. (A
statement's direction read with a published word list became steps 13 and 14; a language model's
first use is step 20.)

## After the MVP — the feature ladder

In order. Each rung is worth building only because the one below it worked.

| # | Feature | Why it waits |
| --- | --- | --- |
| 1 | **[More events](steps/rung-1-more-events.md)** — NFP, Fed decisions. **Done** 2026-10-06; results in [MVP results](mvp-results.md#rung-1--more-events) | Same code, more rows. Widen only once one event type is measured. |
| 2 | **[Predict the next release](steps/rung-2-predict.md)**. **Done** 2026-10-12; results in [MVP results](mvp-results.md#predicting-the-next-release) | A prediction is only worth emitting once it comes from measured numbers. |
| 3 | **[Honest confidence](steps/rung-3-confidence.md)** — hit rate → probability, magnitude bands, silence on low-`n` cells. **Done** 2026-10-12; results in [MVP results](mvp-results.md#honest-confidence): the bands are honest, the probabilities not | "70%" must mean 70%. Needs enough measured history to calibrate against. |
| 4 | **[Keep score](steps/rung-4-keep-score.md)** — log predictions, grade them against outcomes. **Done** 2026-10-16: logged and graded on the first two live releases; every verdict "too few", as expected | You cannot grade predictions you are not yet making. |
| 5 | **[Live path](steps/rung-5-live-path.md)** — fetch the release when it lands, instead of by hand. **Done** 2026-10-16: the first fetched actual equals FRED's; unattended by [the release-day job](steps/release-day-job.md), installed 2026-10-15 | Automating a manual step that must first be worth automating. |
| 6 | **[Delivery](steps/rung-6-delivery.md)** — the warning actually reaches a person. Chosen 2026-10-21: a desktop popup on this laptop | Never deliver uncalibrated warnings; needs rung 3. *Amended 2026-10-20* ([the record, not a probability](steps/record-not-probability.md)): a warning carries the direction, its walk-forward record and its band, never a stated probability, until one proves honest by rung 3's rule. |
| 7 | **Unscheduled events** — detection, classification, entity linking, corroboration. *Amended 2026-10-23:* statements, shocks and news are measured as history first (steps 8, 10 and 11 above); live detection stays last. *Amended 2026-11-04:* step 20 reads news into triggers for kinds already measured, after a predictor exists; detection beyond those stays last | The hardest part of the system, and worthless without a working predictor behind it. |

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
