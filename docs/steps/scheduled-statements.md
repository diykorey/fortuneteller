# Scheduled statements

> Step 8 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-23 with the
> [plan update](../legend.md#the-target): the first events with no number, the first preview.
> Builds on [jobless claims](jobless-claims.md), whose *lesser* release it reuses. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** do markets move on the days the Fed chair or the ECB president speaks or
testifies, and can the fortune teller say so on the morning of the next one?

A statement has no forecast and no actual, so it has no surprise and no direction: only *does it
move?*. What it adds is a scheduled event that the morning job can announce, with that record,
before it happens.

## The events

- **Source:** TradingView's calendar, already cached a quarter at a time for the US and the euro
  area. A statement is a row titled `Fed …` or `ECB …` whose title holds *speech*, *speaks* or
  *testi…* in any case (the calendar also writes *Testymony*), at its own listed time. **One event
  a day,** the earliest: 246 Fed rows fall on 244 days, 483 ECB rows on 456.
- **Only the chair's and the president's.** The title names a person, and the row counts only if
  that person held the office on its date: Bernanke to 2014-01-31, Yellen to 2018-02-03, then
  Powell, then Warsh (the handover, about 2026-05-15, checked in step 1; the calendar has neither
  between 2026-03-30 and 2026-07-01); Draghi to 2019-10-31, then Lagarde.
  This drops Powell's 31 speeches as a governor and a 2013 row titled with his name. Other speakers
  are left out: 1.7 Fed or ECB statements a trading day, most of them noise beside the two voices
  the market waits for.
- **Press conferences are left out.** Each one falls on its decision's day, after the decision, and
  daily closes cannot separate the two; the Fed and ECB flows already measure that day.
- **Counted 2026-10-29 on the cache:** the Fed chair on 244 days (2013-02 to 2026-08, 176 of them
  with no other stored release); the ECB president on 456 days (2013-04 to 2026-09, 343 alone).
  Early years are thin (seven Fed days in 2013), and TradingView's history is all there is.
- **Two flows:** a new seed event type `Central-bank statement`, with origin `United States` for
  the Fed chair and `Euro area` for the ECB president.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** ratio ≥ 1.10 and p < 0.01, for all sixteen markets.
- **No surprise and no sign.** No expected value exists, so neither flow has a surprise rule. They
  have no walk-forward record and make no call.
- **Lesser, as claims.** A statement day is no other flow's shared or busy day, so every existing
  table, verdict and live call stays the same. Each flow's own table keeps only its lone days: no
  other stored release that day, except claims, the other lesser flow.
- **Chance, counted:** twelve flows × sixteen markets = 192 *does it move?* cells, 1.9 *moves* by
  chance; the surprise and walk-forward grids are unchanged.
- **The preview, decided now:** on a day with a statement still ahead at 08:30 New York, the morning
  job's popup names it, gives its time and the flow's markets that *move* with their ratios, or says
  that none does. It shows the record only, never a direction. About two in five of the president's
  statements are timed before 08:30 New York and get no preview; the chair's almost all do. If
  neither flow moves anything, the preview still runs: "no market has moved on the chair's 176 days"
  is a record too.
- **Expected outcome, written down first:** the Fed chair moves the 5-year and the 10-year yields
  and the dollar index (the two-day testimonies carry it), and no stock index; the ECB president
  moves nothing at the bar (most of her talks are not about rates), with the euro closest.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The seed row and the two lesser flows from the cached calendar; `load-releases` stores them; the scoreboard gains two rows~~ **done**; `load-releases` stores 245 Fed chair and 462 ECB president statements, every existing scoreboard entry identical on a copy of the store, the scoreboard in 527 s | A test's calendar quarter keeps a chair's speech and testimony, one event on a day with two, and drops a governor's speech and a press conference; `raw-move --event fedchair` prints sixteen verdicts; every existing output identical on a copy of the store; the scoreboard rebuilt within the evening job's twenty minutes (about 600 s expected, 502 s now) |
| 2 | ~~Results here and in [`mvp-results.md`](../mvp-results.md)~~ **done** | Both flows' verdicts for all sixteen markets, against the expected outcome |
| 3 | The preview: `live` prints a line for each statement later today, and the job pops it up, also on a day with no call | A test's calendar day with a 10:00 chair speech prints the line with the flow's movers read from the scoreboard's data; a speech at 03:00 prints nothing |

*Amended 2026-10-29, in step 1:* Warsh was sworn in on 2026-05-22, so Powell's last day as chair is
2026-05-21 and his 2026-05-31 speech a governor's. With the current quarter fetched and the euro
calendar read from 2013-01 as the US one is, the counts are 245 Fed chair days and 462 ECB
president days (2 and 27 days with two statements); the one ECB row left out is a 2013 speech
titled with Lagarde's name.

## Technical details

Two flow classes beside `EcbFlow`, `lesser = True`, `surprise_rule = None`, `cli_name` `fedchair`
and `ecbchief`, reading `fetch_tradingview_since` and a parser that matches each title to the term
table: one constant mapping names to their last day in office, not a resolver. `load-releases`
prints how many rows each flow drops for being out of term. The preview reads
`docs/scoreboard/data.json`, which the evening job rewrites, instead of rerunning the permutation
test at 08:30, and today's calendar quarter as `live` already fetches it. `docs/schema.md` gets the
event type and the two origins, `docs/precision.md` the title matching and TradingView's listed
time, `docs/glossary.md` *Statement flow* and *Preview*.

## Results

Measured 2026-10-29 (`raw-move --event fedchair` and `--event ecbchief` on a copy of the store
with every price loaded): each flow on its lone days, against every ordinary day of each market's
history, as fixed.

| Market | Fed chair: ratio, p, verdict | By era: 2008–19, 2020– | ECB president: ratio, p, verdict | By era: 2008–19, 2020– |
| --- | --- | --- | --- | --- |
| S&P 500 | 0.83, 0.96, doesn't | 0.75, 0.92 | 0.95, 0.75, doesn't | 0.65, 1.02 |
| 10-year yield | 1.15, 0.17, unclear | 0.87, 1.21 | 0.90, 0.99, doesn't | 0.74, 0.87 |
| Dollar index | 1.07, 0.25, doesn't | 0.99, 1.17 | 1.02, 0.40, doesn't | 0.85, 1.09 |
| Gold | 1.03, 0.40, doesn't | 0.95, 1.18 | 1.01, 0.46, doesn't | 0.72, 1.09 |
| VIX | 1.22, 0.015, unclear | 1.12, 1.09 | 1.24, 0.001, **moves** | 1.19, 1.08 |
| DAX | 0.90, 0.82, doesn't | 0.89, 1.08 | 0.95, 0.74, doesn't | 0.84, 1.19 |
| Euro Stoxx 50 | 0.84, 0.95, doesn't | 0.72, 1.12 | 1.10, 0.11, unclear | 0.90, 1.24 |
| Brent | 1.02, 0.41, doesn't | 0.98, 1.10 | 1.26, 0.002, **moves** | 1.26, 1.09 |
| EUR/USD | 0.98, 0.59, doesn't | 0.78, 1.25 | 0.95, 0.76, doesn't | 0.97, 1.13 |
| Nasdaq | 1.10, 0.16, unclear | 0.71, 1.02 | 1.27, 0.0002, **moves** | 0.71, 1.17 |
| 5-year yield | 1.05, 0.40, doesn't | 1.07, 1.17 | 0.90, 0.998, doesn't | 0.83, 0.97 |
| FTSE 100 | 0.78, 0.996, doesn't | 0.82, 0.99 | 0.90, 0.93, doesn't | 1.01, 1.15 |
| STOXX 600 | 0.98, 0.60, doesn't | 0.79, 1.05 | 1.00, 0.52, doesn't | 0.96, 0.99 |
| Bitcoin | 1.05, 0.32, doesn't | 0.88, 1.20 | 1.11, 0.13, unclear | 1.23, 1.02 |
| Defence ETF | 0.90, 0.87, doesn't | 0.77, 0.94 | 1.03, 0.35, doesn't | 0.69, 1.14 |
| Energy ETF | 0.96, 0.69, doesn't | 0.62, 1.27 | 1.01, 0.45, doesn't | 0.90, 1.01 |

176 Fed chair days and 339 ECB president days for the S&P 500, a few fewer where a market's
history is shorter or its holiday differs.

- **The Fed chair moves nothing.** No market reaches the bar; the 10-year yield and VIX are the
  nearest, at 1.15 and 1.22, neither under p 0.01.
- **The ECB president moves VIX, Brent and the Nasdaq, and nothing in Europe.** By the fixed rule
  these are three *moves*, where chance gives 0.16 in the flow's sixteen cells. They are not to be
  believed: within each era no market reaches 1.10 in both, and the Nasdaq's 1.27 overall is 0.71
  and 1.17 by era. The president's days are all from 2013 on and two thirds from 2020 on, while each
  market's ordinary days run back to 1971 for the Nasdaq and 1990 for VIX; a market louder now than
  in its past moves "more" on any recent day. Precision's *loud and quiet years* trigger, *moves*
  overall but near 1.00 by era, has fired.
- **Against the expected outcome:** both wrong. The chair moves no yield and no dollar at the bar
  (the 10-year at 1.15 is the closest); the president moves three markets, none of them the euro.

*Exploratory, chosen after the results above were seen, so not a verdict:* the same ratios with
ordinary days only from 2013 on. The Fed chair's yields and dollar rise to 1.16–1.23 (p 0.01–0.04,
*unclear*); the president's Nasdaq falls to 1.17 (p 0.02) and the Euro Stoxx 50 rises to *moves*
(1.24, p 0.001), with Brent still *moves* (1.29). Claims' lone days, seen the same way, would move
six markets instead of the Nasdaq alone. Every flow measured from 2013 (the ECB, the flash HICP,
ISM, claims, the statements) and every market with a long history carries the same tilt, in either
direction; the Nasdaq's *moves* on seven of ten events ([more outcomes](more-outcomes.md#results))
is probably part of it.

## What this does not do

No other speakers, no press conferences, no Bank of England or other central bank, no reading of
what was said (hawkish or dovish, the roadmap's *later*), no intraday window, no direction or call
from a statement.
