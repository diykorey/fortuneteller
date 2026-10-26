# Roadmap

> Why this plan has this shape — the target, the idea being tested, and the principles behind the
> ordering — is in the [Legend](legend.md). Unfamiliar acronym, ticker, or term? Every one is
> explained in the [Glossary](glossary.md).

## The goal

Given an event, say which instruments move, by how much, in which direction — with confidence that
means something. A warning product, not HFT: the latency budget is seconds to minutes.

*Amended 2026-10-23:* an entertainment tool with a realistic approach, not a financial one
([Legend](legend.md#the-target)). The bars stay; the surface widens.

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
is never called before it happens: for news the product is a graded reaction record, and for a
scheduled statement a preview. Counts checked 2026-10-23 on the calendars already cached.

| # | Step | Why now |
| --- | --- | --- |
| 5 | **The scoreboard** — a static page the evening job writes from the calls log and the score: every call and its grade, every link's record, every event's verdicts for every market, and how many *moves* chance alone would give at these counts | Everything below is a table nobody sees without it. A static page is not a web service, so no graduation trigger fires |
| 6 | **[Jobless claims](steps/jobless-claims.md)** — the weekly US release (Thursday 08:30 New York, about 700 since 2013 with a forecast) as a flow with its surprise, called live by the morning job | The only event that beats the sample wall: about 50 calls a year against 12 for a monthly one |
| 7 | **More outcomes** — oil, EUR/USD, the Nasdaq, the 5-year yield, the FTSE 100, the STOXX 600, bitcoin, a defence and an energy ETF, each with its close and zone; "does it move?" only, unless a sign is written down first | Free on Yahoo with daily history; every verdict table gains rows, and oil and defence are the natural outcomes of step 10's shocks. More cells mean more *moves* by chance: the scoreboard says how many |
| 8 | **Scheduled statements** — the Fed chair's and the ECB president's speeches, testimonies and press conferences as two flows, "does it move?" only; the morning job previews a scheduled one with its record | The cached calendar holds 5,644 timed Fed and ECB statements since 2013, none with an expected value, so no surprise. Only the chair's and the president's are events: 1.7 statements a trading day would leave no ordinary day |
| 9 | **Germany's calendar** — ZEW and Ifo (10:00 and 11:00 Frankfurt) and the German flash CPI, the first European surprises with a forecast history | A `DE` fetch of the same calendar. Whether Europe reacts to its own survey news, after the ECB and the flash showed it reacting mostly to the US |
| 10 | **Dated shocks** — elections (US, European Parliament, Germany, France, UK), tariff announcements, debt-ceiling deadlines and summits as hand-written dates in a seed CSV; "does it move?" and for how long (`ret_1w`) | The taxonomy's other half, measured honestly; the n is tiny by nature and the page says *too few* |
| 11 | **News as a feed** — GDELT, one narrow question first: the US president's statements on trade since 2015, against oil, stocks and the dollar, with the bar fixed before measuring | The only free news-event history with actors and tone, and noisy. Decides whether a feed is worth building on before any detection machinery (rung 7) |

Later, not planned in detail: a statement's text read for its direction (hawkish or dovish), the
first use of a language model, graded like a surprise; prediction-market prices as an election's
expected value; and "beat the fortune teller", a person's own call logged before the release and
graded beside the machine's.

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
| 7 | **Unscheduled events** — detection, classification, entity linking, corroboration. *Amended 2026-10-23:* statements, shocks and news are measured as history first (steps 8, 10 and 11 above); live detection stays last | The hardest part of the system, and worthless without a working predictor behind it. |

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
