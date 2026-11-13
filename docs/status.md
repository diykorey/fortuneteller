# Status

Where the work is and what comes next. Two rules keep it current:

- **Starting a task:** move it from *Next* to *In progress*, and write the task expected after it
  as the new *Next* — so there is always one step queued ahead.
- **Finishing a task:** move it to *Last completed* and add it to *Done*, in the same change.

## Last completed

Step 17, part 2: the Fed's decisions over a quarter and a year. Nothing holds and no answer stands
counting each cycle once; one answer of 150 cells against 2.0 by chance
([the spec](steps/what-follows-long.md#results)).

## In progress

Step 20, part 1: a CEO's conduct in question, the company against the S&P 500, from a published
dataset of CEO dismissals ([the spec](steps/ceo-scandals.md)), taken 2026-11-13 by the owner ahead
of step 18's grades. Step 1, the coded list, is done: 26 events, 2005 to 2023. Step 2, the closes and
`follows --event ceo`, is in this change; step 2b, the trigger with the company's ticker, and step 3,
the results and Nvidia's answer, are next.

Step 18, part 2, step 3: the first triggers graded ([the spec](steps/trigger-file.md)). The owner's
first, CPI of 2026-11-10 *as expected*, was filed that evening but merged 2026-11-11 10:33, after
every reaction close, and its kind was wrong: CPI's kind is read from the core print, 0.3 against
0.2, *above*, not from the headline. It is void and counts on no market. It waits for the next one.

Waiting: the scoreboard's first release day on the published page (step 3); release-day job step
3, evening score step 2 and rung 6 step 2: the first release the morning job logs, pops up and the
evening grades. The jobs report of 2026-11-06, the first with the euro and the 5-year yield called,
was missed: the laptop slept from that morning to 2026-11-09, so `live` never ran at the release.
A closed lid suspends it even on power; the owner keeps it open (decided 2026-11-10).
CPI on 2026-11-10 was logged 49 minutes late: Nasdaq answered the job's Python 3.14 with HTTP 403
(issues #277–279), and the rerun on 3.12 logged it (PR #280), every row silent or *too few*;
`EURUSD`, logged after its release, is void. The evening of 2026-11-10 found three closes not yet
on Yahoo and committed nothing; the next failed on FRED's HTTP 502 (#289), and its rerun on
2026-11-12 graded it (PR #290): of the three *too few* rows the dollar index and the 5-year yield
were right, the DAX wrong. Python is now pinned to 3.12.

Beat the fortune teller, step 3: the first live round, a release `live` calls guessed through a
merged pull request ([the spec](steps/beat-the-fortune-teller.md)). It waits for a release; CPI on
2026-11-10 is the next.

## Next

Step 20, part 1, step 3: the results, checked against the expected outcome, with Nvidia's answer for
2026-11-08; then step 2b, a `ceo` trigger with its company's ticker. Then part 2, a pasted article
read into a trigger.

## Done

| Date | What | Where |
| --- | --- | --- |
| 2026-11-14 | Docs: decisions.md, the choices that set direction, newest first, with why and where | PR #301 |
| 2026-11-14 | Docs: the entry points made true; docs/README.md the onboarding path; glossary adds link, step, part, rung | PR #300 |
| 2026-11-14 | News into triggers, part 1, step 2: `follows --event ceo`, each company against the S&P 500 on its own base; the companies' closes by `load-prices --companies` | PR #299 |
| 2026-11-13 | News into triggers, part 1, step 1: 26 CEO scandals coded from the dismissal dataset, each with its source | PR #298 |
| 2026-11-13 | News into triggers, part 1: spec, a CEO's conduct in question; step 20 taken now by the owner | PR #297 |
| 2026-11-12 | What follows, part 2, step 2: results — nothing holds over a quarter or a year; no answer stands by cycle | PR #295 |
| 2026-11-12 | What follows, part 2, step 1: `follows --long`, the quarter and the year with each cycle once | PR #294 |
| 2026-11-12 | What follows, part 2: spec, the Fed's decisions over a quarter and a year, each cycle once | PR #293 |
| 2026-11-12 | A trigger's row printed at the release, its kind read as the store reads it | PR #292 |
| 2026-11-12 | The breakeven's sign: on CPI it holds, 35 of 42, a new live call; a close published a day late waits and stops nothing | PR #275 |
| 2026-11-11 | What follows, part 1f, step 2: results — the ECB's decisions by kind answer nothing | PR #288 |
| 2026-11-11 | What follows, part 1f, step 1: `follows --event ecb`; ECB triggers | PR #287 |
| 2026-11-11 | What follows, part 1f: spec, the ECB's decisions by kind | PR #286 |
| 2026-11-11 | What follows, part 1e, step 2: results — claims by kind holds nothing; the yields' day answers lean on shared days | PR #285 |
| 2026-11-11 | What follows, part 1e, step 1: `follows --event claims`; claims triggers | PR #284 |
| 2026-11-11 | What follows, part 1e: spec, jobless claims by kind | PR #283 |
| 2026-11-11 | Python pinned to 3.12: Nasdaq refuses 3.14's requests | PR #282 |
| 2026-11-09 | The signs, step 2: results — no link holds, no new call | PR #271 |
| 2026-11-09 | The signs, step 1: `XLU` on every rule the yield has, `ITB` on CPI and core PCE; no new call | PR #270 |
| 2026-11-05 | The signs: spec, utilities and homebuilders; the breakeven's waits for the evening grade | PR #269 |
| 2026-11-05 | The scoreboard, faster, step 1: every output identical, the rebuild 270 s | PR #268 |
| 2026-11-05 | The scoreboard, faster: spec | PR #267 |
| 2026-11-05 | The claims' actual is FRED's first print; the evening job runs again | PR #266 |
| 2026-11-04 | The breakeven, step 2: results | PR #264 |
| 2026-11-04 | The breakeven, step 1: FRED's `T5YIE`, unsigned | PR #263 |
| 2026-11-04 | Coffee, step 2: results | PR #261 |
| 2026-11-04 | Coffee, step 1: `KC=F`, unsigned | PR #260 |
| 2026-11-04 | The markets people feel, part 1, step 2: results | PR #258 |
| 2026-11-04 | The markets people feel, part 1, step 1: seven markets, unsigned | PR #257 |
| 2026-11-04 | The markets people feel, part 1: spec | PR #256 |
| 2026-11-04 | A trigger arrives, part 2, step 2: the evening score answers and logs the triggers | PR #255 |
| 2026-11-04 | A trigger arrives, part 2, step 1: `triggers`, answered from the reaction close, logged and graded | PR #254 |
| 2026-11-04 | A trigger arrives, part 2: spec, the trigger file and its log | PR #253 |
| 2026-11-04 | A trigger arrives, part 1, step 2: results — nothing holds from the next close; what follows the reaction is mostly no direction | PR #252 |
| 2026-11-04 | A trigger arrives, part 1, step 1: `follows --after-the-day` | PR #251 |
| 2026-11-04 | A trigger arrives, part 1: spec, what follows from the next close | PR #250 |
| 2026-11-04 | What follows, part 1d, step 2: results — CPI by kind holds nothing; a cooler print's answers lean on shared days | PR #249 |
| 2026-11-04 | What follows, part 1d, step 1: `follows --event cpi`, kinds from the headline | PR #248 |
| 2026-11-04 | What follows, part 1d: spec, CPI by kind from its headline | PR #247 |
| 2026-11-04 | What follows, part 1c, step 2: results — retail sales by kind holds nothing; the yields fall after a release below | PR #246 |
| 2026-11-04 | What follows, part 1c, step 1: `follows --event retail` | PR #245 |
| 2026-11-04 | What follows, part 1c: spec, retail sales by kind | PR #244 |
| 2026-11-04 | What follows, part 1b, step 2: results — after a report above the consensus, both yields rise on the day and hold | PR #243 |
| 2026-11-04 | What follows, part 1b, step 1: `follows --event nfp` | PR #242 |
| 2026-11-04 | What follows, part 1b: spec, the jobs report by kind | PR #241 |
| 2026-11-04 | What follows, part 1, step 2: results — nothing holds; four answers near chance; VIX on hold days the nearest | PR #240 |
| 2026-11-04 | What follows, part 1, step 1: `follows` | PR #239 |
| 2026-11-04 | What follows, part 1: spec | PR #238 |
| 2026-11-04 | The target: many countries, the US first | PR #237 |
| 2026-11-04 | The target amended: news triggers, the markets people feel, spans from a day to a year; roadmap steps 17–20 | PR #236 |
| 2026-11-04 | The week ahead, without a call, step 1: the events not called, with their records | PR #235 |
| 2026-11-04 | The week ahead, without a call: spec | PR #234 |
| 2026-11-04 | The week ahead, step 1: the scoreboard previews the coming week's releases | PR #233 |
| 2026-11-04 | The week ahead: spec | PR #232 |
| 2026-11-03 | The Fed statement's sentiment, step 2: results — all four signed links *doesn't*, no call | PR #230 |
| 2026-11-03 | The Fed statement's sentiment, step 1: the paper's dictionary, five checks passed, the Fed's surprise rule | PR #229 |
| 2026-11-03 | The Fed statement's sentiment: spec | PR #228 |
| 2026-11-03 | The Fed statement's tone, step 1: the list reads 19 of 226 statements; stopped by its rule | PR #227 |
| 2026-11-03 | The Fed statement's tone: spec | PR #226 |
| 2026-11-03 | Beat the fortune teller, step 2: the scoreboard shows the guesses | PR #225 |
| 2026-11-03 | Beat the fortune teller, step 1: `score` grades guesses beside the machine's calls | PR #224 |
| 2026-11-03 | Beat the fortune teller: spec | PR #223 |
| 2026-11-03 | The president's trade posts, part 2, step 2: results — no US market moves on a post day; step 11 closes with no | PR #221 |
| 2026-11-03 | The president's trade posts, part 2, step 1: 220 second-term post days as one lesser flow, every existing entry identical | PR #220 |
| 2026-11-03 | The president's trade posts, part 2: spec | PR #219 |
| 2026-11-03 | The president's trade posts, step 2: results — nothing moves on a tweet day | PR #218 |
| 2026-11-03 | The president's trade posts, step 1: 179 tweet days stored as one lesser flow, every existing entry identical | PR #217 |
| 2026-11-03 | News as a feed, part 1, spec: the president's trade posts; GDELT cannot date them | PR #216 |
| 2026-11-03 | Summits, step 2: results — only the dollar moves on the day, unconfirmed; nothing over a week | PR #215 |
| 2026-11-03 | Summits, step 1: 70 summits stored as one lesser flow, every existing entry identical | PR #214 |
| 2026-11-03 | Dated shocks, part 4, spec: summits, the G7 and the G20 as one lesser flow | PR #213 |
| 2026-11-03 | The debt limit, step 2: results — both Treasury yields move on the day and over a week, no stock market does | PR #212 |
| 2026-11-03 | The debt limit, step 1: 73 days stored as one lesser flow, every existing entry identical | PR #211 |
| 2026-11-03 | Dated shocks, part 3, spec: the debt limit, dated by Congress's final vote | PR #210 |
| 2026-11-03 | Tariff actions, step 2: results — Europe's stocks move on a signing, New York's do not | PR #209 |
| 2026-11-03 | Tariff actions, step 1: 73 signing days stored as one lesser flow, every existing entry identical | PR #208 |
| 2026-11-02 | Dated shocks, part 2, spec: tariff actions from the Federal Register, signings since 2018 | PR #207 |
| 2026-11-02 | Elections, step 2: results — the US moves its stocks for a day, France VIX; nothing over a week | PR #206 |
| 2026-11-02 | Elections, step 1: five lesser flows from a hand-written seed file, *too few* under ten days, `raw-move --week`; every existing entry identical | PR #205 |
| 2026-11-02 | Dated shocks, part 1, spec: elections as five lesser flows, *too few* under ten days | PR #204 |
| 2026-11-02 | Germany's calendar, step 2: results — the surveys move nothing; the euro tracks the German flash CPI | PR #203 |
| 2026-11-02 | Germany's calendar, step 1: three lesser flows stored, every existing entry identical; *missed* only for flows called live | PR #202 |
| 2026-11-02 | Germany's calendar, spec: three lesser flows, the surveys' and the flash's signs fixed first | PR #201 |
| 2026-11-02 | Scheduled statements, step 3: the preview, popped up on a statement's morning | PR #200 |
| 2026-11-02 | Own years, step 2: results — 60 cells changed, the Nasdaq moves on two flows, lone claims days on six markets; no call changed | PR #199 |
| 2026-10-30 | Own years, step 1: ordinary days from each flow's first day; 59 cells changed, *moves* 52 → 54 | PR #198 |
| 2026-10-30 | The jobs wait three minutes for the network when caught up at a wake; two evenings lost to it | PR #196 |
| 2026-10-29 | Ordinary days from each flow's own years, spec: chosen before the statements' preview | PR #195 |
| 2026-10-29 | Scheduled statements, step 2: results — the Fed chair moves nothing; the president's three *moves* fail the era split | PR #194 |
| 2026-10-29 | Scheduled statements, step 1: the two lesser flows stored, every existing entry identical | PR #193 |
| 2026-10-29 | Scheduled statements, spec: two lesser flows, the chair's and the president's; the preview fixed first | PR #191 |
| 2026-10-28 | More outcomes, step 2: results — the 5-year yield the most responsive market, four new links hold, three live | PR #189 |
| 2026-10-28 | The scoreboard: GitHub Pages on, its address in the docs, the bare address redirected | PR #188 |
| 2026-10-28 | Jobless claims, step 3: the job merges a pull request whose rows are all silent | PR #187 |
| 2026-10-27 | More outcomes, step 1: the nine markets loaded, closes checked, signs by analogy; four new links hold, three of them live | PR #185 |
| 2026-10-27 | More outcomes, spec: nine markets, signs by analogy, the chance line counted | PR #184 |
| 2026-10-27 | Jobless claims, step 2: results — nothing moves on lone claims days; the yield follows the surprise, short of *tracks*; no call | PR #183 |
| 2026-10-26 | Jobless claims, step 1: the weekly flow, a lesser release, called live on Thursdays | PR #181 |
| 2026-10-26 | Jobless claims, spec | PR #180 |
| 2026-10-26 | The scoreboard, step 2: the evening job rewrites the page into the score pull request; a same-day run resets its branch | PR #179 |
| 2026-10-23 | The scoreboard, step 1: `fortuneteller scoreboard` writes the page's data and the page; the first page committed | PR #178 |
| 2026-10-23 | The scoreboard, spec | PR #177 |
| 2026-10-23 | The plan update: the target amended, roadmap steps 5–11, README status | PR #176 |
| 2026-10-23 | The US manufacturing survey (ISM), step 2: results — the yield and the dollar track it; no call | PR #175 |
| 2026-10-23 | The US manufacturing survey (ISM), step 1: the flow, shared with the flash | PR #174 |
| 2026-10-23 | The US manufacturing survey (ISM), spec | PR #173 |
| 2026-10-22 | Cross-country effects, part 3, step 2: results — the flash moves New York, not Europe; nothing follows its surprise | PR #171 |
| 2026-10-22 | Cross-country effects, part 3, step 1: the flash HICP flow; two GDP verdicts changed by shared days | PR #170 |
| 2026-10-22 | Cross-country effects, part 3, spec: euro-area inflation, the flash HICP and its surprise | PR #169 |
| 2026-10-22 | Cross-country effects, part 2, step 2: results — the ECB moves the dollar, not Europe's stocks | PR #168 |
| 2026-10-22 | Cross-country effects, part 2, step 1: the ECB flow | PR #167 |
| 2026-10-22 | Cross-country effects, part 2, spec: ECB decisions | PR #166 |
| 2026-10-21 | Cross-country effects, part 1, step 2: results — Europe follows CPI's surprise more than New York | PR #165 |
| 2026-10-21 | Cross-country effects, part 1, step 1: the DAX and Euro Stoxx 50 loaded | PR #163 |
| 2026-10-21 | Cross-country effects, part 1, spec: US releases against Europe's stocks | PR #162 |
| 2026-10-21 | Rung 6 step 1: the desktop popup; failure reports fixed (broken since #151) | PR #161 |
| 2026-10-21 | Rung 6 spec: delivery as a desktop popup | PR #160 |
| 2026-10-20 | The record, not a probability, step 2: the call line without a percentage | PR #159 |
| 2026-10-20 | The record, not a probability: spec; an honest probability passes rung 3 one time in five at 80 calls | PR #158 |
| 2026-10-20 | The evening score installed: the timer on, one check run clean | PR #157 |
| 2026-10-20 | The evening score step 1: `release-day.sh score`, its timer, one lock for both jobs | PR #156 |
| 2026-10-19 | The evening score spec: the day loaded and scored unattended | PR #155 |
| 2026-10-19 | Rungs 4 and 5 results: the first live calls graded, verdicts "too few"; both rungs done | PR #154 |
| 2026-10-16 | The release-day job catches up a start missed while the laptop was off | PR #153 |
| 2026-10-15 | The release-day job installed: the timer on, one check run clean | PR #152 |
| 2026-10-15 | Release-day job step 2: the script and its systemd timer | PR #151 |
| 2026-10-15 | The first release logged with `--fetch`: retail sales, 0.8 against 0.3 | PR #150 |
| 2026-10-15 | Release-day job step 1: `fortuneteller live` | PR #149 |
| 2026-10-14 | Release-day job spec: the call logged and its pull request opened unattended | PR #148 |
| 2026-10-14 | Rung 5 step 1: TradingView's CPI actual at most 8 s after 08:30, equal to the typed one | PR #147 |
| 2026-10-14 | The first live call: CPI 2026-10-14, core 0.3 against 0.2 | PR #146 |
| 2026-10-13 | Rung 5 step 2: `predict --fetch` reads the actual from TradingView | PR #145 |
| 2026-10-13 | Rung 5 spec: the live path, `predict --fetch` from TradingView | PR #144 |
| 2026-10-13 | Consensus fallback step 2: results — every verdict stands; retail's yield confidence too close to tell | PR #143 |
| 2026-10-13 | Consensus fallback step 1: TradingView's forecast where Nasdaq has no row | PR #142 |
| 2026-10-13 | Consensus fallback spec: TradingView's forecast where Nasdaq has none | PR #141 |
| 2026-10-13 | Rung 4 spec: the calls' pull request opens right after logging, before gold's close | PR #140 |
| 2026-10-13 | Rung 4 step 2: `score` grades the logged calls beside the replay | PR #139 |
| 2026-10-13 | Rung 4 step 1: `predict --actual` logs every link's line to `data/calls.csv` | PR #138 |
| 2026-10-13 | Rung 4 spec: keep score | PR #137 |
| 2026-10-12 | Step 4 step 3: results — retail sales' yield holds; core PCE and GDP no calls; step 4 complete | PR #136 |
| 2026-10-12 | Step 4 step 2: consensus surprises for the three; retail sales' yield tracks | PR #135 |
| 2026-10-12 | Step 4 step 1: retail sales, core PCE and GDP flows; GDP and retail sales move the yield and the dollar | PR #134 |
| 2026-10-12 | Step 4 spec: more events — retail sales, core PCE, GDP | PR #133 |
| 2026-10-12 | Rung 3 step 4: results — the bands are honest, the probabilities not; rung 3 complete | PR #132 |
| 2026-10-12 | Rung 3 step 3: `predict --actual` gives each call's probability and band | PR #131 |
| 2026-10-12 | Rung 3 step 2: `predict` grades each link's stated confidence | PR #130 |
| 2026-10-12 | Rung 3 step 1: `confident_calls`, a probability and a band per call | PR #129 |
| 2026-10-12 | Rung 3 spec: honest confidence — a probability and a band per call, graded | PR #128 |
| 2026-10-12 | Rung 2 step 4: results — jobs-report links hold, the dollar clearly; CPI too few; rung 2 complete | PR #127 |
| 2026-10-12 | Rung 2 step 3: `predict --actual`, the next release's call | PR #126 |
| 2026-10-12 | Rung 2 step 2: `predict`, each link's walk-forward record and verdict | PR #125 |
| 2026-10-12 | Rung 2 step 1: the walk-forward replay | PR #124 |
| 2026-10-12 | Rung 2 spec: predict the next release, tested walk-forward | PR #123 |
| 2026-10-09 | Free consensus step 3: results — jobs-report links pass, stronger; CPI's dollar passes against the consensus | PR #122 |
| 2026-10-09 | Free consensus step 2: Nasdaq's consensus as a source, judged beside the trend | PR #121 |
| 2026-10-09 | Free consensus: spec revised to Nasdaq; step 1, the calendars fetched and matched | PR #120 |
| 2026-10-09 | Data sources survey: ~250 free sources from FinceptTerminal graded; Nasdaq, TradingView and Forex Factory consensus compared | PR #119 |
| 2026-10-09 | Jobs-report forecast step 4: results — both links pass since 2014, against the trend too | PR #117 |
| 2026-10-09 | Jobs-report forecast step 3: the model beside the trend on the same reports | PR #116 |
| 2026-10-08 | Jobs-report forecast step 2: least squares and the payroll model | PR #115 |
| 2026-10-07 | Country-aware events step 2: trends and reports per flow, each market's zone — part 1 complete | PR #114 |
| 2026-10-07 | Country-aware events spec and step 1: flow identity by type and country | PR #113 |
| 2026-10-07 | Jobs-report forecast spec and step 1: ADP and claims inputs | PR #112 |
| 2026-10-06 | Event flows step 4: the recipe; a made-up flow and source plug in — refactor complete | PR #111 |
| 2026-10-06 | Event flows step 3: the CLI and measurement driven by the flows | PR #110 |
| 2026-10-06 | Event flows step 2: CPI, NFP and Fed as flows behind `EVENT_FLOWS` | PR #109 |
| 2026-10-06 | Event flows spec and step 1: expectation sources, validated surprises | PR #108 |
| 2026-10-06 | Rung 1.8: Results; rung 1 section in `mvp-results.md` — rung 1 complete | PR #107 |
| 2026-10-06 | Rung 1.7: NFP surprise; yield and dollar follow it but miss the hit-rate bar | PR #106 |
| 2026-10-06 | Rung 1.6: clean baseline; CPI and NFP verdicts hold, Fed's dollar just moves | PR #105 |
| 2026-10-06 | Rung 1.5: reaction close by event time; gold moves on Fed days (1.79) | PR #104 |
| 2026-10-05 | Rung 1.4: Fed decisions since 1994; S&P 500 and VIX move; gold's close precedes them | PR #103 |
| 2026-10-05 | Rung 1.3: every event's moves; `raw-move --event` — NFP moves all five | PR #102 |
| 2026-10-05 | Rung 1.2: NFP releases; dates checked against BLS since 1994 | PR #101 |
| 2026-10-05 | Rung 1.1: generic event keys; `surprises` | PR #100 |
| 2026-10-05 | Rung 1 spec: more events — NFP and Fed decisions | PR #99 |
| 2026-10-05 | Step 4.7: Results and `mvp-results.md` — step 4 and the MVP complete | PR #98 |
| 2026-10-05 | Step 4.6: `surprise` CLI — verdict and context tables | PR #97 |
| 2026-10-05 | Step 4.5: `track_surprises`; shared statistics in `stats.py` | PR #96 |
| 2026-10-05 | Step 4.4: `load-surprises` — 1,287 surprises stored | PR #95 |
| 2026-10-05 | Step 4.3: Cleveland Fed nowcast; expected value before each release | PR #94 |
| 2026-10-05 | Step 4.2: first-published m/m, core and headline, with the January fix | PR #92 |
| 2026-10-05 | `sources.py`: FRED and Yahoo requests and parsing moved out of `study.py` | PR #91 |
| 2026-10-05 | Step 4.1: `cpi_surprises` table and its schema doc | PR #90 |
| 2026-10-05 | `study.py` regrouped by step; no behaviour change | PR #89 |
| 2026-10-05 | `daily_bars` rebuilt per instrument; gold cross-checked, not replaced | PR #88 |
| 2026-10-05 | Step 4 spec: does the move follow the CPI surprise? | PR #87 |
| 2026-10-05 | Step 3.4: Results — step 3 complete; CPI moves UST 10Y, DXY, VIX | PR #86 |
| 2026-10-02 | Step 3.3: `raw-move` CLI — verdicts, eras, rule | PR #85 |
| 2026-10-02 | Step 3.2: `compare_moves` — ratio, permutation `p`, verdict | PR #84 |
| 2026-10-02 | Step 3.1: `daily_moves` and `cpi_days`; CPI-day moves match step 2 | PR #83 |
| 2026-10-02 | Step 3 spec: raw move on CPI days; precision doc | PR #82 |
| 2026-10-02 | Release dates checked against BLS; Nov 1992 corrected; weekend guard | PR #81 |
| 2026-09-29 | Step 2.5: `load-prices` CLI — step 2 complete | PR #80 |
| 2026-09-29 | Review hygiene: test isolation, empty key, naive `event_ts`, CI lockfile | PR #79 |
| 2026-09-29 | Review fixes: rebuild observations, loud failures, no provisional bars | PR #78 |
| 2026-09-28 | Step 2.4: build `observations` — 2,698 release-day moves | PR #77 |
| 2026-09-28 | Step 2.3: store the five instruments' closes; bulk `insert_models` | PR #76 |
| 2026-09-28 | Step 2.2: fetch and parse Yahoo daily closes | PR #75 |
| 2026-09-28 | Step 2.1: `daily_bars` table and its schema doc | PR #74 |
| 2026-09-25 | Scenarios doc: ten shock → aftershock episodes, numbers verified | PR #72 |
| 2026-09-25 | Step 2 spec: prices from Yahoo, `daily_bars`, observations | PR #73 |
| 2026-09-25 | Schema doc: every table, column and enum value explained | PR #71 |
| 2026-09-25 | Step 1.5: `load-releases` CLI — step 1 complete | PR #70 |
| 2026-09-25 | Step 1.4: store the CPI events idempotently | PR #69 |
| 2026-09-25 | Step 1.3: map each CPI release to an `EventInstance` | PR #68 |
| 2026-09-25 | Step 1.2: fetch and parse the CPI initial-release history from FRED | PR #67 |
| 2026-09-11 | Step 1 prep: FRED key in settings, accounts doc, API verified, UST 10Y added | PR #66 |
| 2026-09-11 | Docs entry point, legend, step 1 spec | PR #65 |
| 2026-09-11 | Docs rebuilt around the lean MVP; pre-reset corpus archived to `legacy/` | PR #64 |
| 2026-08-05 | `main` reset to M0; pre-reset work parked in `origin/main_05082026` | — |
| before 2026-08 | M0 data spine: models, DuckDB schema, seed CSVs, `init \| seed \| query-demo` CLI | M0-01…09 |

## MVP progress

| Step | State |
| --- | --- |
| 1 Releases | Done |
| 2 Prices | Done |
| 3 Raw move | Done — moves: UST 10Y, DXY, VIX; doesn't: S&P 500, gold |
| 4 Surprise | Done — tracks: UST 10Y; unclear: DXY; doesn't: VIX, S&P 500, gold |

## Rung 1 progress

| Event | Step 3 (moves?) | Step 4 (follows the surprise?) |
| --- | --- | --- |
| CPI (clean baseline) | moves: UST 10Y, DXY, VIX; doesn't: S&P 500, gold | as the MVP |
| NFP | moves: all five | unclear: UST 10Y, DXY, gold; doesn't: S&P 500, VIX. Since 2014: UST 10Y and DXY track, against the forecast and the trend alike |
| Fed | moves: S&P 500, gold, VIX; unclear: UST 10Y, DXY (moves, borderline, until own years) | none: no free expected value |
| Retail sales (step 4) | moves: UST 10Y; unclear: DXY (moves until own years) | against the consensus: UST 10Y tracks; DXY doesn't |
| Core PCE (step 4) | none; VIX unclear (moves until own years) | none track: too few noticeable surprises |
| GDP (step 4) | moves: UST 10Y, DXY | none track; DXY unclear |

## Known, not yet fixed

Found by the 2026-09-28 codebase review and deliberately left for later. This section stays until
each is fixed or dropped; it is not rewritten when a task finishes.

- Paths and `.env` resolve from the working directory, so running from elsewhere misses them.
- CPI release dates for 1972–1989, and NFP release dates before 1994, have not been checked against
  BLS. Later dates are checked; see step 1's spec and rung 1's.
- In 1990–2007 the 10-year yield and the dollar move more the day after a Fed decision than on the
  day; either their close then came before the statement, or the reaction ran on. See
  [Precision](precision.md), "Close times".
- Since 2008, 19 CPI releases share their day with retail sales, and 7 jobs reports with retail
  sales or core PCE; CPI's and the jobs report's tables keep those days. See
  [step 4](steps/step-4-more-events.md#shared-days).
