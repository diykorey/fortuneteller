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
| 1 | The seed row and the two lesser flows from the cached calendar; `load-releases` stores them; the scoreboard gains two rows | A test's calendar quarter keeps a chair's speech and testimony, one event on a day with two, and drops a governor's speech and a press conference; `raw-move --event fedchair` prints sixteen verdicts; every existing output identical on a copy of the store; the scoreboard rebuilt within the evening job's twenty minutes (about 600 s expected, 502 s now) |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | Both flows' verdicts for all sixteen markets, against the expected outcome |
| 3 | The preview: `live` prints a line for each statement later today, and the job pops it up, also on a day with no call | A test's calendar day with a 10:00 chair speech prints the line with the flow's movers read from the scoreboard's data; a speech at 03:00 prints nothing |

## Technical details

Two flow classes beside `EcbFlow`, `lesser = True`, `surprise_rule = None`, `cli_name` `fedchair`
and `ecbchief`, reading `fetch_tradingview_since` and a parser that matches each title to the term
table: one constant mapping names to their last day in office, not a resolver. `load-releases`
prints how many rows each flow drops for being out of term. The preview reads
`docs/scoreboard/data.json`, which the evening job rewrites, instead of rerunning the permutation
test at 08:30, and today's calendar quarter as `live` already fetches it. `docs/schema.md` gets the
event type and the two origins, `docs/precision.md` the title matching and TradingView's listed
time, `docs/glossary.md` *Statement flow* and *Preview*.

## What this does not do

No other speakers, no press conferences, no Bank of England or other central bank, no reading of
what was said (hawkish or dovish, the roadmap's *later*), no intraday window, no direction or call
from a statement.
