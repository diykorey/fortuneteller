# Decisions

The choices that set the project's direction, newest first, each with why and where it is written
out in full. Read this before reopening a question: if it is here, it was settled on purpose, and
changing it takes a new entry, not a quiet edit.

What belongs here: a choice of target, method, scope, order or way of working that later work must
respect. What does not: the bars and rules inside one step, which live in that step's spec and are
amended there with a date.

Each entry: **what** was decided, **why**, what it **retires**, and **where** the detail is. *By the
owner* marks a choice the owner made over another on the table.

## 2026-11-27: New sources: the 2-year yield first, then US releases with forecasts, by the owner

- **What:** the next sources are the US 2-year Treasury yield (FRED's `DGS2`) as a new market
  (step 63), then the US releases TradingView lists with forecasts that we lack: producer prices,
  Michigan sentiment, job openings, housing starts and durable goods.
- **Why:** every link that holds compares a release with its forecast and reads a short-term
  interest rate or a currency. Kinds with no expected figure (steps 26 to 30), and the new
  countries (steps 52 to 54), found nothing that holds. The 2-year is the market most sensitive
  to US releases, and the TradingView flows already read releases of this shape. Chosen over EIA's
  weekly oil and gas stocks, USDA's crop reports, and the Asian indexes, silver and copper the news
  scan found, which stay candidates.
- **Retires:** nothing. GDELT stays out ([Precision](precision.md)); Treasury auctions have no
  free expected yield; Polymarket (step 60) stays after the 2027-01-31 gate.
- **Where:** [The 2-year yield](steps/two-year-yield.md); [Roadmap](roadmap.md), step 63.

## 2026-11-26: Big moves explained, and the news scanned for markets we miss, by the owner

- **What:** each weekday the evening finds the big moves in the markets we track from the stored
  closes, checks each against our open calls and guesses, and asks the Subscription LLM for its
  reason; it also scans the day's news for big moves in markets we do not track. Built as step 62;
  a month of it is read in January 2027.
- **Why:** the owner asked to learn from the moves we did not see coming. Starting from our own
  closes catches every move in what we track, reported or not; the news is read only where the
  closes cannot see. Chosen over reading each country's papers first, which is costlier and
  reports what readers care about, and over the closes alone, which miss the markets we lack.
- **Retires:** nothing; Polymarket (step 60) stays after the 2027-01-31 gate.
- **Where:** [Big moves, explained](steps/big-moves-explained.md); [Roadmap](roadmap.md), step 62.

## 2026-11-25: One front-page card per area, after step 57, by the owner

- **What:** the predictions page holds at most one card per area, long-run forecasts and guesses
  alike, with room for every area; built as step 61, right after step 57 and before step 58.
- **Why:** the page looked the same from day to day. Its cap of five was full: three long-run
  cards (the S&P 500 and the Nasdaq, both stocks, and home prices) and three guesses kept until
  graded, so none of the evening's guesses could join before 2026-12-04, though they span 30
  markets. Chosen over measured company-results forecasts and over fixing the guesses' lean to
  *down* (40 of 52), both left open.
- **Retires:** the front page's cap of five.
- **Where:** [Roadmap](roadmap.md), step 61.

## 2026-11-24: The jobs share the store; Polymarket after the gate; the draft printed both ways, by the owner

- **What:** three choices. The release-day and evening jobs keep the one store the sessions use,
  each command waiting up to 30 minutes for a held store, then stopping with one line (step 57's
  R5). Polymarket's busiest markets are read, after the 2027-01-31 gate, to choose which kinds of
  events to add next (step 60). Step 58's draft is printed both by a `fortuneteller approve`
  command after a desktop notification and, when a session is open, in the session.
- **Why:** a store of the job's own would go stale on the S&P 500 companies' prices and on every
  load done by hand; Polymarket's questions say what people care about, but few match a market's
  move over a span and its history is short; the command works with no session open, the session
  is where the owner already approves drafts.
- **Retires:** R5's own store and cache under `~/.local/share/fortuneteller/`; the open question
  on step 58's roadmap row.
- **Where:** [Step 57](steps/technical-fixes.md), R5; [Roadmap](roadmap.md), steps 58 and 60.

## 2026-11-24: Nasdaq's cached refusals asked again, after step 57, by the owner

- **What:** the 324 Nasdaq calendar days cached as "Error while calling vendor" are deleted and
  asked again once (about 22 minutes at Nasdaq's pace), as a small change after step 57; every
  output is compared before and after, and each expected value recovered is listed.
- **Why:** step 57's R1 found them read since as days without releases; R1 keeps no new refusal
  but left these, so that nothing measured changed within step 57.
- **Retires:** [Precision](precision.md)'s *Now* for them, once done.
- **Where:** [Status](status.md); [Precision](precision.md), *Nasdaq's refusals kept before step
  57*, which reaches `main` with R1 (#451).

## 2026-11-24: Bitcoin's and ether's weekend closes, from Yahoo, after step 58, by the owner

- **What:** the price loader keeps Saturday's and Sunday's closes for bitcoin and ether, which
  Yahoo already sends and the loader drops for every market; a small step 59, after the publishing
  schedule. No new crypto source (Binance, Coinbase, CoinDesk).
- **Why:** a crypto guess made at a weekend is graded from Monday's close, and a weekend's news
  reaches crypto's price before any stored close. The prices are already free from Yahoo; Binance
  refuses US addresses, where the runner of step 21 works, and CoinDesk is news, whose reading
  (step 20) is parked until the 2027-01-31 gate.
- **Retires:** nothing.
- **Where:** [Roadmap](roadmap.md), row 59.

## 2026-11-24: Correct what the page claims before widening, by the owner

- **What:** the required fixes of two outside reviews of 2026-11-24 come before any new flow: the
  business review's eight first, as [step 56](steps/honest-page.md); then the technical review's,
  step 57, one pull request each; then the publishing schedule, step 58. Within step 56, by the
  owner: the page shows counts, not tenths; the consensus figures leave the public seeds and the
  history stays; the maker has no money in any market shown; guesses name no single company;
  guesses stay on the front page with a look of their own.
- **Why:** the reviews found that the page claims more than its numbers: guesses graded from a
  price their writer had already seen past, long-run drift labelled a tested forecast, a guess
  card that looks like a tested one, and a rule against tenths broken. Every evening adds up to 50
  more guesses under the old baseline, so that fix comes first.
- **Retires:** a guess's baseline as the close before the first weekday after its evening; the
  *Tested on the past* label on long-run cards; "about N times in 10".
- **Where:** [what the page claims, corrected](steps/honest-page.md), step 56.

## 2026-11-23: Guesses are judged against the base rate, with a control guesser, by the owner

- **What:** a guess counts as skill only by how far guesses beat their markets' base rates (the
  *excess*), not by how many came true. A *grounded guesser*, given the base rates and the
  forecasts that hold, runs each evening beside today's *news guesser*, which stays unchanged as
  the control; the grounded prompt is refined one numbered change at a time, each judged against
  the control.
- **Why:** the owner's aim is guesses that come true more often than the base rate. Of three ways
  (score only; give the guesser the record; the same with a control) the owner chose the control:
  run side by side, the same market moves hit both guessers, so the difference is the prompt's,
  where one after the other a calm month against a falling one would decide it. Steps 41 to 43
  showed the model finds no rule the record lacks, so here it is given the record instead.
- **Retires:** nothing; the guess ledger's count of guesses that came true stays beside the excess.
- **Where:** [guesses against the base rate](steps/guesses-vs-base-rate.md), step 55.

## 2026-11-23: Readers follow on LinkedIn, no sign-up on the site, by the owner

- **What:** a reader who wants the results follows the owner on LinkedIn, where the Monday post
  gives them; the site gets no email list, feed or sign-up. The first post tells a story (the
  laptop that slept through the jobs report, the patterns that failed, the one that held) and
  asks readers to follow.
- **Why:** of three options (follow on LinkedIn, an email list, an RSS feed) the owner chose the
  one with nothing to build; step 23 already makes the profile the channel.
- **Retires:** nothing.
- **Where:** [be seen](steps/be-seen.md), step 23.

## 2026-11-23: The runner may open issues

- **What:** the runner's morning opens an issue when the laptop has not logged the day's calls by
  08:45 New York, or when its own evening was never started; the laptop's evening opens one when
  the runner's morning was never started. A source's 5xx is asked again twice before it fails.
- **Why:** a machine that sleeps or a timer that never asks cannot report itself: the jobs report
  of 2026-11-06 and the evening of 2026-11-17 went unseen, and one HTTP 500 lost 2026-11-19's
  evening. The gate needs four straight weeks of release days, none missed.
- **Retires:** step 21's "a shadow run opens no pull request and no issue", for these two issues.
- **Where:** [the loop's safety nets](steps/loop-nets.md), step 46.

## 2026-11-22: Canada, China and Switzerland, by the owner

- **What:** three countries' news and markets, one step each: Canada (step 52), China (53),
  Switzerland (54), each built as step 25 built the Bank of England and the Bank of Japan. Step 46,
  the loop's safety nets, keeps its date (before 2026-11-25) and goes before step 53.
- **Why:** the owner asked for areas with no tested forecast to be tested on news, and for one more
  country, then chose three after a count of each candidate's releases with forecasts on
  TradingView's calendar (2008 to 2026): Canada its inflation (225 releases), jobs and retail
  sales, and the Bank's 152 decisions; China its inflation, trade and factory reports, its loan
  rate only from 2019; Switzerland its inflation and the SNB's 76 decisions. The ECB, the BoE and
  the BoJ gave *can't say* on their own currencies, so tested forecasts in currencies are not
  expected; the new markets are open to the guesser at once.
- **Where:** [Canada](steps/canada.md); China's and Switzerland's specs follow.

## 2026-11-22: One card per area on the front page, by the owner

- **What:** the front page shows one card per area of markets (eight: stocks, interest rates and
  inflation, currencies, energy, gold, food, crypto, homes), tested forecasts first.
- **Why:** the owner saw three of five cards on the stock market and asked for more areas. The
  guesses already spanned many; the page's choice did not. Of three ways (one per area, at most
  two on stocks, one per area with the guesser asked to cover every area) they chose the first.
- **Where:** [Fortuneteller predicts](steps/predicts.md), amended 2026-11-22.

## 2026-11-22: The site opens on the predictions page, by the owner

- **What:** the site's bare address sends readers to the predictions page, not the scoreboard;
  the scoreboard follows in the bright cards' design.
- **Why:** the owner asked whether the old design was still there. It was the first page readers
  saw, since the bare address went to the scoreboard. Of three ways put to them (open on the
  predictions page and restyle the scoreboard, open on the predictions page only, leave both)
  they chose the first.
- **Where:** [Fortuneteller predicts](steps/predicts.md), amended 2026-11-22.

## 2026-11-22: The front page's guesses approved by the owner, by the owner

- **What:** the guesses the front page shows wait in a pull request of their own each evening,
  where the owner rewords, removes or approves them; merging it publishes them. The ledger of every
  guess is still published the evening it is made, unreviewed. Only the words may change: the
  market, direction, dates and link are locked by a test.
- **Why:** the owner asked to "adjust prediction wording … staging to discuss and approve wording
  before publishing public those 5 only". Of four ways put to them (a pull request each evening,
  a private page with approve buttons, a hidden preview changed through chat, a second model pass
  with no person) they chose the pull request: it works from a phone, keeps every change in
  history and needs nothing new hosted. The ledger stays unreviewed because its timestamp is what
  shows a guess came before its span.
- **Where:** [the front page's guesses, approved](steps/front-staging.md), step 51.

## 2026-11-22: The page as bright cards, by the owner

- **What:** the predictions page is restyled as bright white cards: a market icon and short name,
  a green or orange *Up by* or *Down by* its end date, the days left, and one line of why, with
  the explanation folded away. The stats page matches.
- **Why:** the owner asked for "bright easy to read page adapt for desktop and mobile phones".
  Of five mock-ups shown with that evening's forecasts (bright cards, a scoreboard list, colour
  tiles, a newspaper, a swipe deck) the owner chose the bright cards. They read best for someone
  with no financial education and look the same on a phone and a desktop.
- **Where:** [Fortuneteller predicts](steps/predicts.md), amended 2026-11-22.

## 2026-11-22: Up to 50 guesses an evening, reviewed and learned from, by the owner

- **What:** the guesser makes up to 50 guesses an evening, each with an end date, reasoning, a tag
  and a confidence. Each is graded by the closes, then reviewed by the model against its own
  reasoning, and the reviews become numbered monthly lessons the guesser reads. The front page
  still shows five forecasts at most; a stats page shows every guess.
- **Why:** the owner asked for "as much as possible reasonable predictions with full explanation"
  graded so "we would be able to improve ourselves with the time". Of three options (up to 8 a
  day with a monthly review; no limit; two a day and a stats page) the owner chose a variant of
  the first with up to 50, each checked as reasonable, clear and not repetitive.
- **Kept honest by:** an evening's guesses of a kind count as one try, so many guesses do not
  pass for many proofs; a review never changes a grade; lessons change once a month and are
  versioned, so versions are compared.
- **Where:** [The guess ledger](steps/guess-ledger.md).

## 2026-11-22: No if cards; our guesses beside the record, by the owner

- **What:** the predictions page drops its *if* cards and shows only forecasts: the tested ones
  of step 48, and *our guesses*, the Subscription LLM's guesses from the day's news, each headed
  as a guess, kept before its span starts and scored apart.
- **Why:** the owner found the *if* cards poor ("we need state without any if then") and said a
  fortune teller may guess without a past where it makes sense. Of three options put to them
  (labelled guesses with their own tally; one list; no guesses yet) they chose the first.
- **Retires:** the Legend's *never a model's opinion* and *what has no past is never shown beside
  a record*, and CLAUDE.md's *never before it*, for *our guess* cards only; each is amended with
  this date. Step 47's *if* cards.
- **Where:** [Our guesses](steps/our-guesses.md), [Fortuneteller predicts](steps/predicts.md).

## 2026-11-21: The page states forecasts, by the owner

- **What:** the predictions page says what will happen, not only what follows an *if*: a
  market's own direction over a span where that direction, tested walk-forward over spans that do
  not overlap, holds by rung 2's bar; and, once news has landed, what follows it where its cell
  holds. Every stated forecast is kept in `docs/predicts/forecasts.csv` and graded when its span
  ends; the page shows the tally.
- **Why:** the owner asked for statements like "next year the cost of real estate will grow".
  Of three options put to them (both kinds; the long run only; daily calls with no tested
  record), they chose both; daily calls were not recommended, and step 48 found no market's
  next day holds.
- **Retires:** step 47's rule that every card is an *if*. It keeps: no event called before it
  happens (CLAUDE.md), no percentage, only what holds is shown.
- **Where:** [Stated forecasts](steps/stated-forecasts.md).

## 2026-11-21: The postponed list worked through, the page first, by the owner

- **What:** with nothing to build before Monday, the owner asked what had been postponed. Of the
  items not parked by an earlier decision, the owner chose this order:
  1. step 45, the S&P 500's measured groups on the page and its reports ahead;
  2. step 46, the loop's safety nets;
  3. the `.env` and paths fix from *Known, not yet fixed*, as a small change alongside.

  Everything parked until the gate stays parked.
- **Why:** step 44's reports ahead held two Dow reports before January. The S&P 500 holds the
  strongest link measured (a miss's day, 2,506 of 3,798) and dozens of reports a week. The loop is
  the gate's first bar.
- **Retires:** nothing.
- **Where:** [step 45](steps/sp500-on-the-page.md); [roadmap](roadmap.md) row 45.

## 2026-11-21: Improve for readers before widening, by the owner

- **What:** asked whether to widen or improve, the owner chose to improve, readers first, with the
  Dow's reports called ahead from the links that already hold: step 44, [a page a stranger
  reads](steps/readers.md). New sources and kinds stay after the gate.
- **Why:** the page had one visitor, the owner's, by 2026-11-21; a first-visitor review found its
  first screen jargon and *can't say*, and its week ahead silent. The gate's readers bar is the
  one no step had worked on, and widening adds *can't say* cells, not readers.
- **Retires:** nothing.
- **Where:** [step 44](steps/readers.md); [roadmap](roadmap.md) row 44.
## 2026-11-21: Free sources surveyed, two expected values queued after the gate, by the owner

- **What:** at the owner's ask, a survey of free sources of US economic statistics and of the
  research on how markets meet releases, kept as [free sources](free-sources.md). No free
  consensus with history was found; the Federal Reserve banks' free forecasts are the nearest.
  The owner chose to keep the survey and plan after the gate: the Cleveland Fed's inflation
  nowcast as a second expected value for PCE first (*corrected the same day:* its CPI nowcast has
  been step 4's baseline since 2026-10-05; only its PCE series is unused), then the Philadelphia Fed survey's
  history for GDP, on the roadmap's *Later* list.
- **Why:** the expected value is the part of a surprise the project cannot get free with history;
  the gate (2027-01-31) holds new work until it is passed.
  The same day the owner added Thinking Machines' Inkling 2 Mini (Apache 2.0, 26.4B with
  about 5B active, released 2026-11-20) to the backlog's local models, beside Gemma 3 4B and
  Qwen 2.5 3B; its card reports no classification or news benchmark, and on this machine (no
  GPU, 30 GB) it runs on the CPU, so the labelled set decides.
- **Retires:** nothing.
- **Where:** [free sources](free-sources.md); [roadmap](roadmap.md), *Later* and *Backlog*.

## 2026-11-21: Scores read from filings, tested against moves, by the owner

- **What:** after reading Andrej Karpathy's US job market visualizer (https://karpathy.ai/jobs/:
  BLS pages scored by a model against an anchored rubric, a score and a reason each, drawn as a
  treemap, untested), the owner chose to take its pattern in two steps, exposure first:
  1. **Step 42, exposure scores:** the Subscription LLM scores each S&P 500 member's 10-K business
     description on signed, anchored rubrics (oil, rates, consumer spending); the scores are then
     tested against the members' moves on the OPEC+, CPI, Fed and retail events, by the usual bars,
     and against a sector baseline.
  2. **Step 43, filing severity:** the same pattern on 8-K text ("how bad for shareholders, −5 to
     +5"), to give step 40's filing kinds (restructuring costs, share sales) the direction their
     item codes lack, so they can become flows.
  3. **Later, the treemap** for the page and the weekly post: members sized by value, coloured by
     what followed an event, once a scored cell answers.
- **Why:** step 40 found most big moves come with an industry's or the economy's news, and the
  project cannot say which companies such news hits. Karpathy's version is untested; this one adds
  the safeguards: the model blind to prices and to anything after the text, a second reading with
  a bar, scores as inputs never answers, and the cost (about 1,500 scores) carried by the
  Subscription LLM now, an API paid by tokens later, as his runs through OpenRouter.
- **Retires:** nothing.
- **Where:** [step 42](steps/exposure-scores.md); [step 43](steps/filing-severity.md).
- **Amended 2026-11-21, by the owner:** after step 42's results (the scores sorted nothing the
  industry did not), the owner chose to go ahead with step 43 over pausing the line or dropping
  it: a filing's direction is a different question from a company's exposure.
## 2026-11-21: A model proposes, the records decide, by the owner

- **What:** asked in turn whether the project pays for any service or model, whether a language
  model will forecast, how one would change the whole, and how the forecasting works, the owner
  then chose a flow where a language model plays an economics and statistics expert: it reads the
  records to 2019 and writes rules richer than one kind against one market (a condition before
  the event, a chain to another market); each rule is tested once on 2020 onward by the bars every
  answer meets, and those that pass are graded forward. For now the model runs through the
  owner's subscription, by hand in one session; a model called through an API, paid by tokens, is
  to be considered later. The answers given on the way stand as written:
  1. The code calls no paid service and no model: Yahoo, Nasdaq, the SEC and FRED (a free key)
     for data; GitHub Actions, cron-job.org and Umami's free tier to run and count.
  2. The forecast stays arithmetic on history (2026-11-04): a model may read the news into a kind
     (step 20's part 2, after the gate, on this machine) and may propose rules; it never answers.
  3. A model as the forecaster is declined again: the past cannot test it (it has read the
     outcomes), and its answer has no counts. It could be tried only as a challenger, its calls
     logged before the reaction and graded beside the record's.
- **Why:** the single-kind answers miss what readers ask; a model reads many records quickly, and
  the bars, a test period it did not see and the forward grading keep its rules honest. A rule
  chosen from many fits the past by luck, so the chance line counts every rule written.
- **Retires:** nothing; 2026-11-04 is refined: a model may now propose rules, not only read news.
- **Where:** [step 41](steps/expert-hypotheses.md).

## 2026-11-21: Big moves against the news filed with them, by the owner

- **What:** step 40 starts from the moves, not the news: the S&P 500 members' days of a move
  three deviations or more against the index, from 2011, matched with the 8-Ks filed that day,
  item by item, each against its share on every day; and a hand-read sample of the big moves no
  8-K explains. Asked how to see which news moves prices, the owner chose this over news sites
  read after each move.
- **Why:** the 8-K items are free, dated to the minute and the same on every rerun; news sites
  are paid or refuse scripts. Reading news only after big moves always finds a reason, so every
  item is also counted on the days that did not move.
- **Retires:** nothing. It is a census, not a flow: a kind it finds is measured by a step of its
  own.
- **Where:** [step 40](steps/news-moves.md).

## 2026-11-20: Four more kinds, by the owner

- **What:** asked which kind phase 5 measures next, the owner answered all four offered: S&P 500
  additions (step 35), earnings beyond the Dow, stock splits, and a CEO's conduct with no
  departure; one step each, in that order.
- **Why:** phase 5 goes on (the answers above); the four were the candidates with a free dated
  record or a known gap.
- **Retires:** nothing.
- **Where:** [roadmap](roadmap.md), [step 35](steps/sp500-additions.md).

## 2026-11-20: The owner's answers to the zoom-out

- **What:** four answers, given the same day.
  1. **Phase 5 goes on:** new kinds keep coming, one a pull request, before the gate; the zoom-out's
     freeze is declined.
  2. **The evening's score merges itself:** a score pull request, opened only when every row is
     graded, is merged by `scripts/release-day.sh` once its checks pass; a failed check leaves it
     for a person. The runner's evening (step 21) then finds nothing to wait on.
  3. **A free same-day source for earnings** is looked for, as a step of its own: Nasdaq's
     calendar fills too late for a live call ([step 33](steps/earnings-current.md)).
  4. **The out/hole column stays as it is:** an event outside a market's closes counts in
     neither; the [Glossary](glossary.md) says so.
- **Why:** 1, the owner's choice of 2026-11-17 stands; 2, a person merging before 01:30 Kyiv every
  night is the flaw the shadow found on 2026-11-18; 3 and 4, as asked.
- **Retires:** a person reviewing each score pull request before it merges.
- **Where:** `scripts/release-day.sh`, [step 21](steps/loop-off-the-laptop.md), the Glossary.

## 2026-11-20: The earnings are kept current, by hand, weekly

- **What:** step 33 refreshes step 31's reports each Monday in a pull request, until the gate.
- **Why:** the page's most-held answers (step 32) stop at 2026-11-18 otherwise, and a post quoting
  them grows stale. Nasdaq fills a report's EPS days late, so no evening fetch or live call.
- **Retires:** nothing.
- **Where:** [step 33](steps/earnings-current.md).

## 2026-11-20: The first monthly zoom-out

- **What:** a goldfish, given only the Legend, the roadmap, status and these decisions, zoomed out
  over the plan, as the [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish)
  asks once a month. Its findings, most serious first:
  1. Phase 5 repeats what phase 4 was opened to stop: nine steps in four days, most *can't say*
     or within chance, while no post has gone out and the readers bar has no count.
  2. The loop bar has no release day yet logged clean on both the laptop and the runner; the
     shadow owes two counting days by 2026-12-18, before the gate's four weeks begin.
  3. 2026-11-19 may be a second shadow failure, which the 2026-11-17 entry sends here before a
     third try; status puts the lost day down to the laptop's FRED failure.
  4. The Bank of England and the Bank of Japan (step 25) went before the euro area, against the
     Legend's "one country at a time once the US answers hold".
  5. Smaller: roadmap rows 21 and 23 and the Later list were behind status; status' *Next*
     repeated step 23's own next part; three items have waited for a release day since before
     2026-11-06 without saying which release ends the wait.
  It would cut: phase 5 until the gate; step 21 to the evening job, or the morning kept on the
  laptop; the popup and *beat the fortune teller* until there are readers.
- **Why:** recorded as found. Finding 5 is fixed in the same change. Findings 1, 2 and 4 would
  reverse the owner's choices of 2026-11-17 (widen the kinds now; the outside timer), so they wait
  for the owner. Finding 3 goes to step 21's spec. What phase 5 did gain: steps 31 and 32 put three
  links that hold on the page, the most of any kind.
- **Retires:** nothing.
- **Where:** [roadmap](roadmap.md), [status](status.md), [step 21](steps/loop-off-the-laptop.md).

## 2026-11-19: Earnings go on the page, and the page shows the placebo's mark

- **What:** step 32 adds step 31's three earnings kinds to the page's *Ask the fortune teller*,
  and gives every cell on the page the placebo's mark, which step 22 left off.
- **Why:** the earnings are the kind the news brings most and three of their links hold
  walk-forward, more than any kind on the page; it was kept off only by its 11-minute run, which
  PR #367 brought to a minute. Step 31 found a beat's day *up* that the placebo reads as the
  period; the page would show it as the beat's answer, and so it may already show other cells.
- **Retires:** the earnings skip in `ask_data`; step 22's page without the placebo.
- **Where:** [the spec](steps/ask-earnings.md).

## 2026-11-19: Earnings, the Dow's members, one event per report, by the owner

- **What:** step 31 measures earnings reports: the Dow's members on each report's day, Nasdaq's
  calendar for the EPS and its consensus, the SEC's 8-K for the minute. An event's id gains the
  report's place in its day, so a flow can hold several events on one day.
- **Why:** the kind the news brings most; a dated membership list picks the companies without
  hindsight, where today's market caps would choose the survivors.
- **Retires:** one event per flow per day.
- **Where:** [the spec](steps/earnings.md).

## 2026-11-19: Floods from NOAA's billion-dollar list; droughts left out

- **What:** step 30 measures the US floods of NOAA's Billion-Dollar Disasters list (1980 to
  2024) that have a day, 39 of its 45, the owner's "floods and droughts", as history only, with
  no crop-region filter.
- **Why:** the list is free and nobody here picks it. Its 32 droughts, and six of its floods, begin on the first of
  a month and last a month or more: a season, not a day the news knew; a call is made from the actual once it lands. A
  region filter would be read from the names by hand. A flood's cost is known weeks later, so no
  trigger.
- **Retires:** droughts as a kind, until a dated source is found; roadmap row 28's "floods and
  droughts in crop-growing regions" as a later step.
- **Where:** [the spec](steps/floods.md).

## 2026-11-19: Phase 5's kinds go on the page, by the owner

- **What:** step 29 adds the six flows of steps 24 to 28 to the page's *Ask the fortune teller*,
  before any new kind or reading the news into them.
- **Why:** they are measured and the page is the gate's second bar; a reader who brings an OPEC+
  or hurricane headline should find its kind. Small, and it shows only numbers already graded.
- **Retires:** the skip in `ask_data` that kept steps 24 to 28 off the page.
- **Where:** [the spec](steps/ask-phase-5.md).

## 2026-11-18: War is measured as ICB's violent acts

- **What:** step 26's *war and military strikes* is every international crisis since 1970 that
  the International Crisis Behavior project codes as set off by a violent act: 136 days, 1970 to
  2021, one kind.
- **Why:** a free list nobody here picks, with a day for each. A crisis's trigger is often words
  weeks before the shooting, and a crisis's violence is known only once it has run its course; the
  violent act is the day a trigger would be filed, known that day.
- **Retires:** nothing. Wars after 2021 wait for ICB's next version.
- **Where:** [war](steps/war.md).
## 2026-11-17: The runner is started by an outside timer (by the owner)

- **What:** the release-day job and the evening score on GitHub's runner are started by two jobs at
  cron-job.org, a free service, asking GitHub's API to run the workflow at 07:30 and 18:30 New
  York on weekdays. The ask carries the owner's fine-grained token for this repository only,
  allowed *Actions: read and write*, kept at that service alone, expiring 2027-03-31 (renewed
  before then, or the loop stops). The workflow's own schedule is removed.
- **Why:** GitHub started the scheduled runs 5 h 41 min to 9 h 56 min late on 2026-11-16 and had
  not started the morning of retail sales, 2026-11-17, by 15:13 UTC, so the shadow failed *on
  time*; runs asked for start within seconds. The owner chose to run the shadow again with the new
  start rather than keep the laptop; a second fail comes back here before a third try. Of the
  three ways weighed, the laptop starting the runner keeps the laptop awake, and fixing the
  laptop's sleep keeps the job on it; an outside timer frees both.
- **Retires:** step 21's 2026-11-14 rule that a run goes on by the time it was scheduled for.
  The token at a third party can start, cancel, re-run and delete this repository's workflow runs;
  it cannot read or change the code or the secrets.
- **Where:** [step 21](steps/loop-off-the-laptop.md), its amendments and results of 2026-11-17.

## 2026-11-17: Widen the kinds now (by the owner)

- **What:** phase 4's pause on new kinds is lifted. Phase 5 adds, one per pull request: OPEC+
  decisions, other central banks (the Bank of England, the Bank of Japan), war and military
  strikes, crypto shocks, and weather and climate events. A hot event of a measured kind is filed
  by hand as a trigger; reading the news into kinds by a small local model goes to the backlog.
- **Why:** the owner wants the fortune teller to answer the news people talk about, and a kind can
  only be answered once its past is measured. Each kind is a dated list on the building block the
  tariff, election, summit and CEO kinds already use, so each costs a list and a spec.
- **Retires:** phase 4's "no new flow or kind starts until steps 21 to 23 are done". The gate on
  2027-01-31 keeps its three bars; steps 21 to 23 finish beside the new kinds.
- **Where:** [roadmap phase 5](roadmap.md#phase-5-the-kinds-the-news-brings).

## 2026-11-17: The visitor count is read through Umami's share link (by the owner)

- **What:** step 23's weekly count stays on Umami Cloud's free plan and is read through the site's
  public share link, not a paid API key. If the link stops answering, the week is read from the
  dashboard by hand.
- **Why:** the free plan has no API key, and the owner pays nothing before there are customers.
  The share link gave the exact Monday-to-Sunday UTC count on 2026-11-17, and its token is listed
  in Umami's own API description. The owner chose it over GoatCounter (a free API, but a switch of
  counter and its own count of a visitor) and over reading the dashboard every week.
- **Retires:** the spec's `FT_UMAMI_API_KEY`.
- **Where:** [be seen](steps/be-seen.md#the-way-to-reach-it).

## 2026-11-15: Step 20 parked until the gate (by the owner)

- **What:** step 20 stops where it stands until the 2027-01-31 gate: part 1 measured, part 2's
  word rules *doesn't read*, `read-article` kept but not trusted. Part 1b, part 2's next try and
  part 3 wait. The work goes to steps 21 to 23. A `ceo` trigger is still filed by hand from part 1.
- **Why:** the rules read 5 of 12 test positives and misread 6 of 99 other departures, and Nvidia's
  article read as *not a measured kind*. The next try, a small model on this machine (Gemma 3 4B or
  Qwen 2.5 3B, on the CPU), with a fresh test set from part 1's conduct departures left out for
  their prices, is a new method that phase 4 says waits for the gate. The owner chose this over
  the model now and over pasting alone.
- **Retires:** phase 4's exception for step 20's part 2; and its spec's line that a *doesn't read*
  is answered before part 3, which this entry answers.
- **Where:** [part 2's results](steps/article-to-trigger.md#results),
  [roadmap step 20](roadmap.md#next-steps-in-order).

## 2026-11-14: The store travels encrypted (by the owner)

- **What:** on GitHub's runners, the store and the source cache travel between runs as one
  gpg-encrypted file, a release asset, under the secret `FT_STORE_KEY`; never as a cache or a
  plain artifact, and never rebuilt from empty. The owner set `FT_FRED_API_KEY` and
  `FT_STORE_KEY` as repository secrets.
- **Why:** step 21's first run showed the store cannot be rebuilt: TradingView rewrote 2025's
  shutdown weeks of claims and rate-limits a runner asking for every quarter. And an artifact of a
  public repository can be downloaded by anyone signed in, which would republish Nasdaq's and
  TradingView's replies.
- **Retires:** step 21's `actions/cache` and 90-day artifact for the store.
- **Where:** [step 21](steps/loop-off-the-laptop.md#results).

## 2026-11-14: Prove the loop, show the page, be seen; then widen

- **What:** roadmap phase 4. Steps 21 to 23 come first: the jobs off the laptop, the page where a
  reader picks a kind of event and sees what followed, and a counted audience. No new flow or kind
  starts before them, except step 20's part 2, already in progress. A gate on 2027-01-31 judges
  them together: four straight weeks of release days logged on time and graded, none missed; the
  page live for every kind step 17 and step 20 answer; at least 100 unique visitors in one week. A
  miss is answered with a new entry here before any new step. The number of live calls is reported,
  not a bar. Prediction markets lead the Later list once the gate passes. Once a month a goldfish
  zooms out over the whole plan.
- **Why:** a review of every document on 2026-11-14 found the measurement sound and the product
  unseen. After a month live, data/calls.csv held 47 rows and one call (retail sales, 2026-10-15,
  wrong); two of the last release days were missed or late; the page the target describes did not
  exist; 20 roadmap steps had widened what is measured while almost every new kind answered
  *can't say*. Being seen was named as progress on 2026-10-23 and never measured. A goldfish read
  of the first draft dropped a bar of 10 live calls, which the work cannot control.
- **Retires:** "chosen one at a time after step 18's results" for the Later list; it now waits on
  the gate. Part 1b of step 20 waits for the gate too.
- **Where:** [roadmap phase 4](roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen),
  [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish).

## 2026-11-14: A CEO's conduct without a departure is a kind too (by the owner)

- **What:** step 20 keeps two company kinds: a CEO leaving over their own conduct (`ceo`, part 1)
  and a CEO's conduct coming out while they stay (Nvidia, 2026-11-08). Part 2's reader tells them
  apart; the second gets no trigger and no answer until it has its own measured history (part 1b).
- **Why:** the news the owner pastes is mostly the second kind: a board investigates and the CEO
  stays. Part 1's dataset holds departures only, so it cannot answer for it.
- **Retires:** part 2's reading of Nvidia as *not a measured kind*.
- **Where:** [part 2](steps/article-to-trigger.md), [roadmap step 20](roadmap.md#next-steps-in-order).

## 2026-11-14: Every spec is read twice by a fresh reviewer

- **What:** each step's spec gets a goldfish review before anything is measured, and another when
  its results are in. The goldfish sees only the spec, the documents it links, the Legend and the
  Glossary; the author fixes each finding or says why it stands. The template gains two sections
  practice had already added: the rule fixed before measuring, and the results. Specs are named
  for their subject.
- **Why:** the author of a spec carries the conversation that led to it and can no longer see what
  the page leaves out; bars written first protect the result only if a stranger can read them.
- **Retires:** the step-N file naming for steps after the MVP, and step 1 as the worked example.
- **Where:** [Legend](legend.md#how-a-step-is-reviewed-the-elephant-and-the-goldfish).

## 2026-11-14: Docs have one way in, and decisions one home

- **What:** a newcomer, human or agent, starts at [docs/README.md](README.md). Choices that set
  direction are recorded here, newest first; the notes inside specs stay where they are. Each fact
  has one home: the roadmap carries one line per step, its spec the bars and the results,
  [status](status.md) only the task in hand, and the [changelog](changelog.md) every finished task.
- **Why:** the documents had grown by appending. A reader had to work through the history to learn
  what was true today, and 91 notes of what was decided or chosen were spread over 43 files.
- **Retires:** the root README's pre-reset design summary, the frozen "Current state" in
  docs/README.md, the results and amendments inside roadmap rows, and the done table in status.
- **Where:** [docs/README.md](README.md), [CLAUDE.md](../CLAUDE.md).

## 2026-11-13: News into triggers now, company news first (by the owner)

- **What:** roadmap step 20 is taken ahead of step 18's grades and step 17's replay. Its first kind
  is a CEO's conduct in question, the company against the S&P 500, from a published dataset of CEO
  dismissals rather than a hand-picked list.
- **Why:** the Nvidia CEO scandal of 2026-11-08 is the kind of headline the tool exists to answer.
- **Where:** [roadmap step 20](roadmap.md#next-steps-in-order), [the spec](steps/ceo-scandals.md).

## 2026-11-11: Python pinned to 3.12

- **What:** the project runs on Python 3.12 only.
- **Why:** Nasdaq's calendar answered the release-day job's Python 3.14 with HTTP 403, and CPI on
  2026-11-10 was logged 49 minutes late (issues #277 to #279).
- **Where:** PR #282, .python-version.

## 2026-11-10: The laptop stays open (by the owner)

- **What:** the laptop that runs the release-day and evening jobs is kept open on release days.
- **Why:** a closed lid suspends it even on power; the jobs report of 2026-11-06 was missed that way.
- **Where:** this entry is the record; it was first noted in status on 2026-11-10.

## 2026-11-04: A headline, answered with what followed (by the owner)

- **What:** the tool finds the event in the news, names its kind, and answers with what followed
  every past event of that kind, for the markets behind what people pay for, over a day, a week, a
  month, a quarter and a year. Each span answers up, down, about the same or can't say, against the
  base rate. The answer is arithmetic on history, never a model's opinion; a model may only read
  the news into a trigger, and runs on this machine. Predicting is built before collecting. The US
  first, then one country at a time.
- **Why:** the reader of the news wonders what comes next; a graded record of past reactions is
  what can answer honestly. The owner first proposed a model's guess, then chose arithmetic.
- **Retires:** "for news the product is a graded reaction record" from 2026-10-23.
- **Where:** [Legend](legend.md#the-target), [roadmap steps 17 to 20](roadmap.md#next-steps-in-order).

## 2026-11-03: News in general is not measured

- **What:** roadmap step 11 closed with no, by the rule written first: no US market moves on the
  president's trade posts. Live detection (rung 7) waits for another reason.
- **Where:** [part 1](steps/presidential-posts.md), [part 2](steps/presidential-posts-2.md).

## 2026-11-03: A statement's tone from a published word list, not a model (by the owner)

- **What:** the Fed statement's direction is read with published dictionaries (steps 13 and 14),
  not a language model.
- **Why:** free, fixed in advance, and checkable.
- **Where:** [step 13](steps/fed-statement-tone.md), [step 14](steps/fed-statement-sentiment.md).

## 2026-10-28: The release-day job merges an all-silent pull request

- **What:** when every row of the day is silent and the run exited cleanly, the job merges its own
  pull request. A call, or anything unusual, stays open for a person.
- **Why:** a silent row claims nothing, and jobless claims bring one every Thursday.
- **Retires:** the job's "it opens, never merges", for silent days only.
- **Where:** [jobless claims](steps/jobless-claims.md), [the release-day job](steps/release-day-job.md).

## 2026-10-23: An entertainment tool with a realistic approach

- **What:** a fortune teller who shows their record, never advice. The bars stay where they were
  fixed; what counts as progress widens to more kinds of events and markets, a steadier cadence,
  and being seen. So: show what is measured (the scoreboard), raise the call count, then widen.
  A statement nobody scheduled is never called before it happens.
- **Why:** the five monthly flows added since step 4 gave no new call, nothing reached anyone but
  the laptop's popup, and half the taxonomy (statements, shocks, news) was unmeasured.
- **Retires:** paid consensus and intraday prices, deferred: they serve a trading use.
- **Where:** [Legend](legend.md#the-target), [roadmap steps 5 to 16](roadmap.md#next-steps-in-order).

## 2026-10-21: Delivery is a desktop popup on this laptop

- **What:** rung 6 delivers each call as a popup on one laptop.
- **Where:** [rung 6](steps/rung-6-delivery.md). The scoreboard page later became the first
  delivery to anyone else.

## 2026-10-20: The record, not a probability

- **What:** a call prints its direction, its walk-forward record as counts and its band, never a
  percentage, until a probability proves honest by rung 3's rule.
- **Why:** rung 3's probabilities were not honest (stated 68%, right 61 to 65%), and on today's
  history no method can pass the test.
- **Where:** [the spec](steps/record-not-probability.md).

## 2026-10-14: The release-day job runs unattended

- **What:** on a release day the call is made, logged and opened as a pull request with no one at
  the keyboard.
- **Where:** [the release-day job](steps/release-day-job.md), answering [rung 5](steps/rung-5-live-path.md).

## 2026-10-13: TradingView's forecast where Nasdaq has none

- **What:** when Nasdaq's calendar has no row, the free consensus falls back to TradingView's.
- **Why:** the day before the first live CPI release, Nasdaq listed no CPI row.
- **Where:** [the spec](steps/consensus-fallback.md).

## 2026-10-09: Free consensus only (by the owner)

- **What:** the expected value is Nasdaq's free published consensus, checked against TradingView's,
  shown beside the trend. Paid consensus and intraday prices are deferred, not dropped.
- **Where:** [the spec](steps/free-consensus.md), [Data sources](data-sources.md#which-free-consensus-is-best).

## 2026-10-07: Sharpen the measurement, then predict, then widen

- **What:** the order of roadmap steps 1 to 4b, after rung 1.
- **Why:** two jobs-report links were clearly real but sat just under the bar, and a better
  expected value was the known, free shortcut.
- **Where:** [roadmap](roadmap.md#next-steps-in-order).

## 2026-10-05: How a CPI surprise is read

- **What:** core CPI against its 12-month trend decides the verdict; the nowcast and headline CPI
  are context. A link's expected direction is fixed in advance, never learned from the data.
- **Where:** [MVP step 4](steps/step-4-surprise.md), its decisions table.

## 2026-09-11: The documents rewritten

- **What:** the current set (legend, roadmap, status, step specs, glossary) replaced the pre-reset
  corpus, which moved to [legacy/](legacy/README.md) as reference, not instructions.
- **Why:** the old corpus described code that did not exist.

## 2026-08-05: The reset

- **What:** main was reset to the M0 data spine, discarding a built replay harness and prediction
  core. Three rules followed: no new package until a second caller needs it; no indirection for a
  single case; a plan doc shorter than the code it specifies. Measure before predicting.
- **Why:** it was over-engineered for the stage, and emitted confident output from placeholder
  values.
- **Retires:** the M0 to M7 milestone scheme.
- **Where:** [CLAUDE.md](../CLAUDE.md); the discarded work is on the main_05082026 branch.
