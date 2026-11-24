# Changelog

Every finished task, newest first, one line each, with the pull request that landed it. Add a row
in the same change that finishes a task ([status](status.md) says how). For why a direction was
taken, see [Decisions](decisions.md); for what a step found, its spec's Results.

| Date | What | Where |
| --- | --- | --- |
| 2026-11-24 | Step 57, R5's store, as the owner chose: the jobs keep the shared store; each job command waits up to 30 minutes for a store another process holds, then stops with one line naming it, as any command does at once outside the jobs. Polymarket's busiest markets added as step 60, after the gate; step 58's draft printed both by a command and in the session | [#456](https://github.com/diykorey/fortuneteller/pull/456) |
| 2026-11-24 | Step 57, R3: OPEC's cells are judged only from each market's first close at or after Brent's reaction close, in `follows`, *Ask*, the walk-forward and a live trigger's answer; the run from the close before prints marked *not judged*, and the kind cell retires. Gasoline's day after *oil up*, OPEC's one answer that held, no longer does; no other flow changes | [#455](https://github.com/diykorey/fortuneteller/pull/455) |
| 2026-11-24 | Step 57, R10: TradingView's forecast, where it fills in for Nasdaq's, is refused and named when over 20 times the actual or under a twentieth of it; on a copy of the store none of the 330 it fills in (all jobless claims) is refused | [#454](https://github.com/diykorey/fortuneteller/pull/454) |
| 2026-11-24 | Step 57, R8: the call log is appended under a lock on it, after reading it again, and a call whose flow, day and market it holds is left out; `score` keeps one row per day and market, the earliest logged. The log holds no duplicate, so no score changes | [#453](https://github.com/diykorey/fortuneteller/pull/453) |
| 2026-11-24 | Step 57, R2: `load-releases` removes an event whose date was corrected (a new one of its flow given within 7 days), with its observations and surprises; one a source stops listing is kept. On a copy of the store none was removed; TradingView's current quarter was found to list no speeches | [#452](https://github.com/diykorey/fortuneteller/pull/452) |
| 2026-11-24 | Step 57, R1: a reply is cached only once it is sound (TradingView's `ok`, a Nasdaq day's data or its "No record found", a Fed page not empty), written beside its place and moved in; the 324 Nasdaq vendor errors already cached are left and listed in Precision | [#451](https://github.com/diykorey/fortuneteller/pull/451) |
| 2026-11-24 | Step 57, R5, part 1: the jobs start `scripts/job-start.sh`, which runs `release-day.sh` from the job's own worktree at `origin/main`, copied out under the job's lock, never the development checkout's; the store's part waits for the owner | [#450](https://github.com/diykorey/fortuneteller/pull/450) |
| 2026-11-24 | Sources by country surveyed: official release calendars, data and news feeds for the US, the euro area, Germany, France, the UK, Switzerland, Japan, China and Canada, each fetched; no republishable free consensus found; GDELT the one multi-country news source whose terms allow reuse | [#447](https://github.com/diykorey/fortuneteller/pull/447) |
| 2026-11-24 | Step 57, R11 corrected: on an evening with the log changed, the switch to main for the triggers put back main's `front-next.csv` before tonight's was kept aside, so the front pull request proposed nothing (2026-11-23's fault, brought back by #446); tonight's is now kept before the switch, and the test checks the front pull request | [#449](https://github.com/diykorey/fortuneteller/pull/449) |
| 2026-11-24 | Step 57, R6: the evening unit loads no `.env`; the model `guess` starts gets web search alone (none for the review), none of the user's settings, hooks or servers, `PATH` and `HOME` alone, and an empty folder | [#448](https://github.com/diykorey/fortuneteller/pull/448) |
| 2026-11-24 | Step 57, R11: on an evening with nothing scored, the pages and the guess ledger go in a pull request merged on passing checks, the triggers' log in one of its own; the script tested end to end against a local origin with `gh`, `uv` and `git push` stood in | [#446](https://github.com/diykorey/fortuneteller/pull/446) |
| 2026-11-24 | Step 57, R7: a guess with a field not text (a list, a number) is dropped with its reason, and a `TypeError` keeps the evening's rows, so one bad answer no longer loses the evening's grades and guesses | [#445](https://github.com/diykorey/fortuneteller/pull/445) |
| 2026-11-24 | Step 57: the technical review's required fixes, the spec | [#444](https://github.com/diykorey/fortuneteller/pull/444) |
| 2026-11-24 | Step 56, step 5: the results; two outcomes wrong as first written: a guess made at a weekend now starts Monday, ten base rates recomputed by a weekday, and a card leaves the page at its end date, not its grade; step 3's page data byte for byte the same; a reader with no financial training explained each card back | [#443](https://github.com/diykorey/fortuneteller/pull/443) |
| 2026-11-24 | Step 56, step 4: the earnings seeds without Nasdaq's EPS, forecast and surprise, kept in the local cache; every earnings output and the scoreboard byte for byte the same | [#442](https://github.com/diykorey/fortuneteller/pull/442) |
| 2026-11-24 | Step 56, step 3: the page's words, approved by the owner: *the usual way*, counts instead of tenths, the guess card's own look, the day-of-news note, "The maker has no money in any market shown"; the three cards name November 23 | [#441](https://github.com/diykorey/fortuneteller/pull/441) |
| 2026-11-24 | Step 56, step 2: a shown card stays until graded or is marked withdrawn; the front page's own tally; #434's lost words traced to a stale copy and fixed | [#440](https://github.com/diykorey/fortuneteller/pull/440) |
| 2026-11-24 | Step 56, step 1: each guess graded from its market's first close after it was made; hand-made guesses in no guesser's record; no single companies | [#439](https://github.com/diykorey/fortuneteller/pull/439) |
| 2026-11-24 | Step 56: what the page claims, corrected, the spec | [#438](https://github.com/diykorey/fortuneteller/pull/438) |
| 2026-11-24 | Step 54, step 4: Switzerland's results; nothing holds walk-forward, the SNB's and inflation's answers below chance in both runs, the franc and the SMI *can't say* on the day after every kind judged; the franc's moves 1.88 times usual on the SNB's days alone | [#436](https://github.com/diykorey/fortuneteller/pull/436) |
| 2026-11-24 | Step 54, step 3: Switzerland's CPI as the lesser flow `chcpi`, `follows`, triggers and the page's *Ask*; from 0.1pp against TradingView's forecast; the expected 152 releases alone, every other flow unchanged | [#435](https://github.com/diykorey/fortuneteller/pull/435) |
| 2026-11-23 | Step 54, step 2: the SNB's flow, `follows --event snb`, `snb` triggers and the page's *Ask*; kinds from the Bank's history, the six unscheduled cuts added, 2015-01-15 a cut and 2015-03-19 a hold; the expected 80 decisions, every other flow unchanged | [#432](https://github.com/diykorey/fortuneteller/pull/432) |
| 2026-11-23 | Step 54, step 1: the franc and the SMI as markets, unsigned, the SMI's close checked against SIX's; `snb-changes.csv`, the SNB's 19 changes since 2008, every month equal to its monthly series, the unscheduled moves' hours from news reports (amended, the releases giving none); Switzerland in `countries.csv`; every existing `raw-move`, `follows`, scoreboard and *Ask* row unchanged | [#431](https://github.com/diykorey/fortuneteller/pull/431) |
| 2026-11-23 | Step 53, step 5: China's results; nothing holds walk-forward, each flow's answers below chance in both runs, Shanghai's stocks *can't say* after every report, the yuan weaker on the day exports miss from the close before (25 of 42), too few to replay; step 3's count of output's answers corrected | [#429](https://github.com/diykorey/fortuneteller/pull/429) |
| 2026-11-23 | Step 53, step 4: China's exports as `cntrade` (from 2.3pp), a lesser flow with `follows`, triggers and the page's *Ask*, and `Trade data` in `event_types.csv`; its kind the exports', not the imports'; 127 releases alone and inflation's 116, each header the one written before step 1; every other flow unchanged | [#428](https://github.com/diykorey/fortuneteller/pull/428) |
| 2026-11-23 | Step 53, step 3: China's NBS factory survey as `cnpmi` (from 0.2 points) and its industrial production as `cnip` (from 0.3pp), lesser flows with `follows`, triggers and the page's *Ask*; each kind its named report's, not its companion's; the survey's expected header amended before its table was read, the hand count having left out the euro area's flash inflation; 59 and 110 releases alone, inflation's 132; every other flow unchanged | [#427](https://github.com/diykorey/fortuneteller/pull/427) |
| 2026-11-23 | Step 53, step 2: China's CPI as the lesser flow `cncpi`, `follows --event cncpi`, `cncpi` triggers and the page's *Ask*; its kind the CPI against TradingView's forecast from 0.1, not the PPI of the same minute; its days alone read on the weekday it reacts on; 148 releases alone, every other flow unchanged | [#425](https://github.com/diykorey/fortuneteller/pull/425) |
| 2026-11-23 | Step 53, step 1: the yuan and the Shanghai Composite as markets, unsigned; the yuan from FRED's noon New York rate (`DEXCHUS`), kept from the peg's end, 2010-06-21, after Yahoo's `CNY=X` proved to stamp the day before's; Shanghai's close checked against the exchange's; every existing `raw-move`, `follows` and scoreboard row unchanged | [#424](https://github.com/diykorey/fortuneteller/pull/424) |
| 2026-11-23 | Step 46, steps 1 and 2: every source asked again after a 5xx, a timeout or a broken connection, at 30 and 90 s, 300 s a process at most, a 4xx never; `unlogged` and `unstarted`, run by the runner's morning and the laptop's evening, each opening an issue for what was missed; the incidents of 2026-11-17 and 2026-11-19 replayed on their real rows and runs | [#418](https://github.com/diykorey/fortuneteller/pull/418) |
| 2026-11-23 | Step 52, step 4: Canada's results; nothing holds walk-forward, the BoC's answers from the close before above chance plus 2, the Canadian dollar stronger on the day of a hike, too few to replay; Toronto's long run not measured | [#417](https://github.com/diykorey/fortuneteller/pull/417) |
| 2026-11-23 | Step 33, step 2: the first earnings refresh, LAST 2026-11-20; one new report, Walmart's of 2026-11-19, *as expected*; no line removed, the hand check against Yahoo passed, every stored id equals the seed's, no answer or verdict changed | [#416](https://github.com/diykorey/fortuneteller/pull/416) |
| 2026-11-23 | Step 23: the first week's row, 2026-11-16 to 2026-11-22: 8 unique visitors, no post | [#415](https://github.com/diykorey/fortuneteller/pull/415) |
| 2026-11-22 | Step 52, step 3: Canada's CPI as the lesser flow `cacpi`, `follows --event cacpi`, `cacpi` triggers and the page's *Ask*; its kind the actual less TradingView's forecast, from 0.1; its table on its 189 days alone; every other flow unchanged | [#414](https://github.com/diykorey/fortuneteller/pull/414) |
| 2026-11-22 | Step 52, step 2: the Bank of Canada's flow, `follows --event boc`, `boc` triggers and the page's *Ask*; kinds from the Bank's changes, 2008-10-08 added, 2020-03-13 a cut and the rateless days of 2012 and 2013 holds; the expected 153 decisions, every other flow unchanged | [#413](https://github.com/diykorey/fortuneteller/pull/413) |
| 2026-11-22 | Step 52, step 1: the Canadian dollar and Toronto's S&P/TSX as markets, unsigned; the Bank of Canada's target rate changes since 2008 as a seed; every existing row unchanged | [#412](https://github.com/diykorey/fortuneteller/pull/412) |
| 2026-11-22 | One card per area on the front page (eight areas); the date badge wraps on a narrow phone, checked at 300 pixels | [#410](https://github.com/diykorey/fortuneteller/pull/410) |
| 2026-11-22 | The scoreboard in the bright cards' design, with a link back to the predictions page; only the styles changed | [#409](https://github.com/diykorey/fortuneteller/pull/409) |
| 2026-11-22 | The site's bare address opens the predictions page instead of the scoreboard | [#408](https://github.com/diykorey/fortuneteller/pull/408) |
| 2026-11-22 | Step 51: the front page's guesses wait for the owner; each evening's proposal goes into a pull request of its own, reworded or removed and published when merged; the market, direction, dates and link are locked by a test; the page reads `front.csv` | [#407](https://github.com/diykorey/fortuneteller/pull/407) |
| 2026-11-22 | The predictions page as bright cards (option A of five): market icons, a big Up or Down by its date, days left, one line of why; the stats page matches | [#406](https://github.com/diykorey/fortuneteller/pull/406) |
| 2026-11-22 | Step 50: the guess ledger; up to 50 guesses an evening with end date, reasoning, tag and confidence, graded by the closes, reviewed by the model, learned from in monthly numbered lessons; a stats page of every guess; the first evening kept 10 | [#405](https://github.com/diykorey/fortuneteller/pull/405) |
| 2026-11-22 | Step 49: our guesses; the predictions page drops its *if* cards and shows the three tested forecasts, then the Subscription LLM's guesses from the day's news, headed *Our guess*, linked to their news, kept before their span and scored apart; the first two: tech stocks down over the week, gold down over the month | [#404](https://github.com/diykorey/fortuneteller/pull/404) |
| 2026-11-21 | Step 48: stated forecasts on the predictions page; 5 of 29 long-run pairs hold walk-forward, all *up* (the S&P 500 and the Nasdaq at a month and a year, US home prices at a year), none for tomorrow; three stated and kept in `forecasts.csv`, graded when their span ends; no after-news forecast qualifies yet | [#403](https://github.com/diykorey/fortuneteller/pull/403) |
| 2026-11-21 | Step 47's cards in plain words for a reader without financial training: no codes, *falls behind the average big US stock*, the record as held and failed counts across many companies, *not forecasts* first | [#402](https://github.com/diykorey/fortuneteller/pull/402) |
| 2026-11-21 | Steps 45 and 47 published: the S&P 500's frozen groups on *Ask* (the answers that hold go from 7 to 9) and its reports ahead; the page *Fortuneteller predicts* at `/predicts/` | [#401](https://github.com/diykorey/fortuneteller/pull/401) |
| 2026-11-21 | Free sources of US economic statistics surveyed; the Cleveland Fed nowcast and the Philadelphia Fed survey queued after the gate; Inkling 2 Mini added to the backlog's local models | [#399](https://github.com/diykorey/fortuneteller/pull/399) |
| 2026-11-21 | Step 43: good or bad, read from the filing; the Subscription LLM scored 400 S&P 500 members' 8-Ks of 2020 to 2025 for shareholders; the score's sign did not say which way the shares moved (bad 27 of 43, p 0.06); nothing answers or holds | [#397](https://github.com/diykorey/fortuneteller/pull/397) |
| 2026-11-21 | Step 42: who a macro event hits, exposure scores; the Subscription LLM scored 426 S&P 500 members' 2019 10-Ks on oil, rates and consumer spending; only oil on OPEC+ *oil down* answers, within chance and near the kind, and no score beats its industry | [#396](https://github.com/diykorey/fortuneteller/pull/396) |
| 2026-11-21 | Step 41: hypotheses from an expert reader; 40 rules from the record to 2019, tested on 2020 onward: 5 pass, 2 hold, all restatements; no condition added | PR #395 |
| 2026-11-21 | Step 40: big moves and the news filed with them; the 8-K items against S&P 500 members' big moves, and 40 unfiled big moves read by hand | PR #394 |
| 2026-11-20 | Step 39: an exact meet (Nasdaq's `N/A`) read as *as expected*; 119 Dow and 1,685 S&P 500 reports added | PR #392 |
| 2026-11-20 | Step 38 ended at step 1: no CEO who stayed in the members' 8-Ks; the kind stays parked | PR #391 |
| 2026-11-20 | Step 37 results: a split announced alone, *up* on the day and holding (33 of 51); in an earnings release *can't say* | PR #390 |
| 2026-11-20 | Step 37, steps 1 and 2: 105 S&P 500 members' forward splits from 2011, dated by their first public news (24 by hand), and the `splits` flow; the spec goldfish-reviewed; the Results to follow | PR #389 |
| 2026-11-20 | Step 36: earnings beyond the Dow, 24,298 S&P 500 members' reports from 2011; a miss's day *down* and holding (2,506 of 3,798); the spec goldfish-reviewed | PR #388 |
| 2026-11-20 | Step 35: S&P 500 additions, 191 from 2007, 143 kept; the day *up* (85 of 135 that moved) but not holding walk-forward; the spec goldfish-reviewed | PR #387 |
| 2026-11-20 | Step 34, step 2 set up: two members' reports to 2026-12-31, so the speed's window runs to the gate; the asks from the crontab | PR #386 |
| 2026-11-20 | Step 34, step 1: Yahoo's earnings kind is Nasdaq's on 102 of 110 reports (92.7%); its EPS differs on 20 | PR #385 |
| 2026-11-20 | Step 34 spec: a same-day source for earnings, Yahoo measured against Nasdaq before any call | PR #384 |
| 2026-11-20 | The owner's answers to the zoom-out: phase 5 goes on; the evening's score pull request merges itself once its checks pass; a same-day earnings source to be looked for; the out/hole column documented | PR #383 |
| 2026-11-20 | The walk-forward's base grown one move at a time: the scoreboard's CPU time 7m41s → 5m08s, its output byte for byte the same | PR #382 |
| 2026-11-20 | Step 33, step 1: step 31's scripts take the last day and fetch the recent pages again; the spec, goldfish-reviewed | PR #381 |
| 2026-11-20 | Step 23: the page asks first, before the week ahead, and `#ask/FLOW/KIND` links open on a kind | PR #380 |
| 2026-11-20 | The first monthly zoom-out: findings in Decisions; roadmap rows 21 and 23, the Later list and status' *Next* brought up to date | PR #379 |
| 2026-11-20 | Step 32 results: the published page answers the three earnings kinds; all 2,988 cells of 15 flows equal `follows`, three period marks, seven holds; the expected outcome right on every count | PR #376 |
| 2026-11-20 | Step 23: the page carries a link preview (description, Open Graph tags, a 1200 by 627 card quoting a miss's day), so a post's link shows more than an address | PR #377 |
| 2026-11-20 | Step 29 results: the published page answers the 12 kinds of OPEC+, the BoE, the BoJ, violent acts, hacks, landfalls and floods, 1,116 cells each equal to `follows`; the expected outcome right; seven holds on the page with step 32's earnings | PR #375 |
| 2026-11-19 | Step 32, step 1: the page's ask answers the earnings (9 cells, three holds), every cell carries the placebo's mark (3 marked), `load-prices` loads the companies' closes | PR #370 |
| 2026-11-19 | Step 31 results: from the close before, a Dow member's shares fall behind the S&P 500 after a miss or an in-line report and run ahead over the week and month after a beat; a miss's day and week and an in-line report's day hold walk-forward; the expected outcome wrong on six counts, the in-line reports above all | PR #368 |
| 2026-11-19 | `follows`' walk-forward over a company's reports builds each chance one event at a time: `follows --event earnings` 11 min 16 s → 59 s, every output byte-identical (both runs of the earnings and the CEO flow compared) | PR #367 |
| 2026-11-19 | Step 30 results: nothing follows a flood; 39 floods, one answer a run, within chance; the expected outcome right | PR #360 |
| 2026-11-19 | Step 22, step 5: the published page answers every kind, none left out, with exactly the three expected holds; step 22 done | PR #355 |
| 2026-11-18 | Step 28 results: fuel, energy stocks, corn, soybeans and Allstate *can't say* after a hurricane landfall; wheat *about the same* on the day from the reaction close, the one miss of the expected outcome; two answers in all, within chance | PR #354 |
| 2026-11-18 | Step 28, step 2: the `weather` flow (code 32, lesser), `follows --event weather` and `weather` triggers; header as expected | PR #352 |
| 2026-11-18 | Step 28, step 1: Allstate as a market, unsigned; HURDAT2's 79 first US hurricane landfalls since 1970 as the seed | PR #351 |
| 2026-11-18 | Spec: step 28, what follows a hurricane's first US landfall (NOAA's HURDAT2, 79 storms 1970 to 2024), Allstate added as a market; roadmap row 28 amended to landfalls | PR #350 |
| 2026-11-18 | Step 27 results: bitcoin, ether and Coinbase *can't say* after a crypto hack on every span; one answer in all, within chance; the expected outcome held but for the week's counts | PR #349 |
| 2026-11-18 | Step 27, step 2: the `crypto` flow (code 31, lesser), `follows --event crypto` and `crypto` triggers; header as expected | PR #348 |
| 2026-11-18 | Step 27, step 1: ether and Coinbase as markets, unsigned; DefiLlama's 44 hacks of $100 million or more as the seed; a market with no days in a flow's span gets a *too few* row | PR #347 |
| 2026-11-18 | Fix: the World row's note quoted in `countries.csv`; its comma broke the seed load and CI since #343 | PR #346 |
| 2026-11-18 | Spec: step 27, what follows a crypto hack of $100 million or more (DefiLlama's list, 44 hacks 2014 to 2026), ether and Coinbase added as markets; roadmap row 27 amended to hacks | PR #345 |
| 2026-11-18 | Step 26 results: gold up after a violent act on the day, the week and the month, too few walk-forward; oil and defence stocks *can't say*; the expected outcome wrong on gold, on the chance bar from the close before and on other flows' chance lines | PR #344 |
| 2026-11-18 | Step 26, steps 1 and 2: the violent acts' seed from ICB, the `war` flow, `follows --event war` and `war` triggers; the expected 136, every other flow unchanged | PR #343 |
| 2026-11-18 | Step 26 spec: what follows a violent act that sets off a crisis, 136 days from ICB's list, the expected outcome written first | PR #342 |
| 2026-11-18 | Step 25 results: BoE and BoJ decisions answer no more cells than chance, nothing holds walk-forward, the pound *can't say* after a BoE move; the expected outcome right on every count | PR #341 |
| 2026-11-18 | Step 25, step 3: the BoJ's flow, `follows --event boj` and `boj` triggers; kinds from the calendar's rates; the expected 85 decisions, every other flow unchanged | PR #340 |
| 2026-11-17 | Step 25, step 2: the BoE's flow, `follows --event boe` and `boe` triggers; kinds from the Bank's Bank Rate changes, 2020-03-26 a hold; the expected 187 decisions, every other flow unchanged | PR #338 |
| 2026-11-17 | Step 25, step 1: the pound, the yen and the Nikkei 225 as markets, unsigned; the Bank of England's Bank Rate changes since 2008 as a seed; every existing row unchanged | PR #337 |
| 2026-11-17 | Spec: step 25, what follows a Bank of England or a Bank of Japan decision (TradingView's calendar, the Bank's own Bank Rate history; the pound, the yen and the Nikkei added) | PR #336 |
| 2026-11-17 | Step 24, step 3: OPEC's results: energy stocks and gasoline move with the kind; gasoline's day after *oil up* holds; from the reaction close, about chance | PR #335 |
| 2026-11-17 | Step 24, step 2: `follows --event opec` (kinds from the seed, Brent's day marked), the `opec` trigger (a live one's kind from Brent's reaction day), the IMF check's file and script | PR #334 |
| 2026-11-17 | Step 21, step 2: the first shadow day fails *on time* (GitHub's schedule hours late); the runs started by an outside timer, by the owner; the workflow's schedule removed | PR #333 |
| 2026-11-17 | Step 24, step 1: the seed of Känzig's 169 OPEC announcements and the flow; the live kind agrees with the surprise on 72 of 80 days since 2007 | PR #332 |
| 2026-11-17 | Spec: step 24, what follows an OPEC+ decision (Känzig's 169 announcements by the sign of their oil supply surprise) | PR #330 |
| 2026-11-17 | Phase 5 opened by the owner: OPEC+, other central banks, war, crypto shocks, weather, one kind per PR; phase 4's pause lifted; the news model to the backlog | PR #329 |
| 2026-11-17 | Step 23, step 1: the counter live on the page and checked (a private visit counted once; the owner's flagged browser, a copy on disk and cookies: none); the share link kept whole, by the owner | PR #328 |
| 2026-11-17 | Step 23, step 1: Umami's tag on the page; the week's visitors read through the site's share link, the free plan having no API key (by the owner) | PR #326 |
| 2026-11-15 | Step 23, step 2: `weekly-post` drafts the week's post from the live calls, and reads the week's visitors from Umami's API | PR #325 |
| 2026-11-15 | Spec: step 23, be seen and count it (Umami Cloud and LinkedIn, by the owner) | PR #324 |
| 2026-11-15 | Step 20 parked until the 2027-01-31 gate, by the owner; the work goes to steps 21 to 23 | PR #323 |
| 2026-11-15 | Step 20, part 2, step 3: the test texts read once, *doesn't read* (5 of 12 positives, 6 of 99 negatives misread); `read-article`; Nvidia read as not a measured kind | PR #322 |
| 2026-11-15 | Step 20, part 2, step 2: the rules for reading an article, written on the dev texts and frozen; dev 9 of 12 positives read, 0 of 103 negatives | PR #321 |
| 2026-11-15 | Step 20, part 2, step 1: the dev and test sets listed; the dev texts fetched, from the page or the Wayback Machine, 12 of 13 positives with a text | PR #320 |
| 2026-11-14 | Step 22, steps 1 to 4: the page asks about each kind of event, from the same cells follows prints | PR #317 |
| 2026-11-14 | Step 21, step 2 begun: the shadow workflow on GitHub's schedule, the store seeded encrypted from the laptop | PR #316 |
| 2026-11-14 | Spec: step 22, ask the fortune teller | PR #315 |
| 2026-11-14 | Step 21, step 1: every source answers the runner, Nasdaq too; the rebuild from empty fails on TradingView's rewritten 2025 claims, so the store travels encrypted | PR #314 |
| 2026-11-14 | Step 21 spec: the jobs on GitHub Actions, a run from empty against every source, then a shadow run beside the laptop | PR #311 |
| 2026-11-14 | Roadmap phase 4: the loop off the laptop, the ask page, a counted audience; a gate on 2027-01-31; monthly zoom-out | PR #310 |
| 2026-11-14 | News into triggers, part 2: spec, a pasted article read into a trigger by rules, tested on part 1's dataset | PR #307 |
| 2026-11-14 | A `ceo` trigger no longer waits on closes: no closes for its company is no answer; a scandal without closes is left out and named | PR #309 |
| 2026-11-14 | News into triggers, part 1, step 2b: a `ceo` trigger names its company, answered from the scandals before it and graded on that company | PR #306 |
| 2026-11-14 | News into triggers, part 1, step 3: results — the company falls against the S&P 500 on the day, 17 of 26; no direction from the reaction close; Nvidia's day beside them | PR #305 |
| 2026-11-14 | Docs: fixes from two goldfish reads, onboarding and results review; verdict words in the glossary | PR #304 |
| 2026-11-14 | Docs: the goldfish review before measuring and after results; the step template matches practice | PR #303 |
| 2026-11-14 | Docs: the roadmap one line per step, status back to its three sections, this changelog split out | PR #302 |
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
