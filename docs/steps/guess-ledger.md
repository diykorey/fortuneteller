# The guess ledger

> Step 50 of the [Roadmap](../roadmap.md), widening [our guesses](our-guesses.md). Terms are in
> the [Glossary](../glossary.md): *our guess*, *Subscription LLM*, *holds*. Asked for 2026-11-22 by
> the owner: "we publish not more than 5; we predict up to 50 … all predictions must be
> reasonable … not repetitive … clearly stated. Each prediction should have reasoning that would
> help to analyze it after the end date … and based on reasoning analyze mistakes and improve
> future predictions."

## The goal

**In plain words:** each weekday evening the fortune teller makes up to 50 guesses, each a clear
sentence about one market, with an end date, its reasoning and the news behind it. When the end
date passes, the guess is graded by the closes, and the model reads its own reasoning against what
happened and writes what it got right or wrong. Once a month those reviews are turned into a new,
numbered version of the lessons the guesser reads. The front page shows five forecasts at most (one per area
since 2026-11-25, [step 61](front-by-area.md)); a stats page shows every guess, its grade and review, and the record by kind of reasoning.

At the end:

- `docs/predicts/our-guesses.csv` holds every guess with its grade and review;
- `docs/predicts/lessons.md` holds the lessons, each version dated and numbered;
- `docs/predicts/stats/index.html` holds the record.

## The way to reach it

- **Many guesses are not many proofs.** Guesses made on one evening from the same news mostly
  move together. So the stats page counts each guess, and also each evening once: the evening's
  guesses of one kind are one *try*, counted once all of them are graded, right if more than half
  came true (a tie is not). *Amended 2026-11-25* ([step 58](publishing-schedule.md)): a Saturday's or Sunday's guesses from
  2026-11-28, made by the daily draft and nearly all starting from Monday's close, are no try.
  *Amended 2026-11-25* ([step 59](crypto-weekends.md)): bitcoin's and ether's are, starting from
  their weekend close.
  A kind of reasoning is *promoted* by rung 2's bar on its tries: at
  least 30, right on at least 60%, one-sided binomial p below 0.01.
- **What makes a guess reasonable, checked before it is kept:**
  - one market of the 31 the store measures daily, by its exact code: `SPY / ES`, `UST10Y / ZN`,
    `DXY`, `GC / XAU`, `VIX`, `DAX`, `SX5E`, `BRN`, `EURUSD`, `COMP`, `UST5Y / ZF`, `UKX`, `SXXP`,
    `BTC`, `ITA`, `XLE`, `CORN`, `WEAT`, `SOYB`, `UGA`, `UNG`, `XLU`, `ITB`, `KC`, `T5YIE`,
    `GBPUSD`, `USDJPY`, `NKY`, `ETH`, `COIN`, `ALL` (`study.MVP_PRICE_SERIES`); *amended
    2026-11-22* ([Canada](canada.md), step 1): 33, with `USDCAD` and `TSX`; *amended 2026-11-23*
    ([China](china.md), step 1): 35, with `USDCNY` and `SHCOMP`; *amended 2026-11-23*
    ([Switzerland](switzerland.md), step 1): 37, with `USDCHF` and `SMI`; *amended 2026-11-24*
    ([step 56](honest-page.md), step 1): 35, without `COIN` and `ALL`, single companies, each
    dropped as *a single company*; Coinbase's open guess is graded as before; *amended
    2026-11-27* ([the 2-year yield](two-year-yield.md), step 1): 36, with `UST2Y / ZT`;
  - *up* or *down*;
  - an end date, a weekday, from the second weekday after the evening to a year ahead;
  - a statement of at most 40 words with no `%`;
  - reasoning of 15 to 150 words (words split on spaces, as every limit here). The prompt asks it
    to say what would prove the guess wrong; the check counts words only;
  - one tag from a fixed list;
  - a confidence of *low*, *medium* or *high*;
  - an `https` link to its news.
- **Not repetitive:** a guess is refused when an open one, or one kept earlier the same evening,
  names the same market, or its twin (the S&P 500 and the Nasdaq), with an end date less than 5
  weekdays from its own, whichever its direction. The model is shown the open guesses, so it can
  avoid them, and the check enforces it. This leaves room for many guesses a market, at end dates
  a week apart, so the 50 can be reached.
- **Horizon,** by weekdays to the end date, for the stats page: *week* (up to 5), *month* (up to
  21), *quarter* (up to 63), *year* (up to 261 weekdays, about 252 trading days). Step 49's
  rows keep their span as their horizon and their reason as their statement.
- **Graded by the closes alone:** from the close before the first weekday after the evening to
  the last close on or before the end date (so a holiday's end date takes the day before), once
  a close on or after the end date is stored, as step 49 grades. Its move is kept with the grade.
  *Amended 2026-11-24* ([step 56](honest-page.md), step 1, before any row was graded): from its
  market's first close after it was made (`made`), read with the market's close time and zone,
  so its writer has seen no close it is graded from; every row so far takes this baseline.
- **The review:** in the same `guess` run that grades a guess, before tonight's guesses, the model
  is given its statement, reasoning,
  grade and the market's move, and writes at most 80 words: which part of the reasoning held,
  which did not, and whether it was right for its reasons or by luck. The review never changes the
  grade.
- **Lessons, monthly:** on the first evening `guess` runs in a month with no version of that
  month, before that evening's guesses, the model reads every review of a guess ending since the
  last version and writes `lessons.md` version *N + 1* (version 1 when there is none), at most 400
  words, dated (*amended 2026-11-22:* only when there is at least one review to learn from; a
  month with none writes no version, as the first evening of 2026-11-22 did). That evening's
  guesses are made under it; each guess keeps its version, so the
  stats page compares versions.
- **The front page:** the tested forecasts (three at most), then guesses to make five (*Amended 2026-11-25* ([step 61](front-by-area.md)):
  one per area, no cap of five). It prefers
  a promoted tag, then confidence (*high*, then *medium*, then *low*; *amended 2026-11-22*, the
  rule had named only *high*), then the soonest end date.
  *Amended 2026-11-22, by the owner:* these guesses wait for approval in a pull request of their
  own before the front page shows them, worded as the owner approves
  ([step 51](front-staging.md)); the ledger is published as before.

## The rule, fixed before measuring

- **No bar decides what is kept,** beyond the checks above.
- **Promotion:** rung 2's bar on a tag's tries, as above.
- **The test of the whole ledger,** once 30 evenings have every guess graded: the evenings right
  (more than half came true) against a coin, one-sided binomial p below 0.01, which at 30 is 22.
  Beside it, with no verdict, how many of the same guesses a market that went up would have
  made right (*always up*).
- **Expected outcome:** 15 to 50 guesses kept on each evening of the first week; no tag promoted
  before 2027-02-28; the ledger no better than a coin at 30 evenings (10 to 20 right).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `guess`: grade the open guesses, review those graded, ask for up to 50 new ones with the open guesses and the lessons, check and keep them | Tests (the model stubbed): each word, market, date, tag, confidence and link check refuses its case; a guess on the same market or its twin ending less than 5 weekdays from an open one is refused, and one 5 weekdays apart is kept; a 51st is not read; a review is kept on the graded row only; a failed model call keeps the rows as they were |
| 2 | Lessons | Tests: the first run of a month writes version 1, or *N + 1*, dated, from the reviews since *N*; a second run that month does not |
| 3 | The stats page and the front page's guesses | Tests: an evening of 11 right and 9 wrong is one right try, 10 and 10 one wrong try, and an evening with a guess still open no try; the front page prefers a promoted tag, then high confidence, then the soonest end date, and fills to five |
| 4 | Published | The first evening's guesses, counted by tag, written in Results with the date |

## How you know it is right

- **A review cannot regrade:** a test gives a review that says the guess was right on a row graded
  *did not* and finds the grade unchanged.
- **Twenty guesses of one evening count once:** the test of step 3, with 11 and 9 and with 10 and
  10, tells *more than half* from *any* and from *all*.
- **Lessons do not peek:** a guess's lessons version is the latest written before its guesses,
  from reviews of guesses graded before that evening.

## What this step does not do

No market outside the 31 (33 from 2026-11-22, with `USDCAD` and `TSX`; 35 from 2026-11-23, with `USDCNY` and `SHCOMP`; 37 the same day, with `USDCHF` and `SMI`; 38 from 2026-11-27, with `UST2Y / ZT`). No size of move. No percentage. No change to the tested forecasts. No
more than five forecasts on the front page.

## Technical details

- **The runs:** `claude -p`, `--model claude-opus-5-5`, web search for the guesses, none for the
  reviews and the lessons; prompts in `src/fortuneteller/guess_prompt.txt`,
  `review_prompt.txt` and `lessons_prompt.txt`.
- **The file:** `docs/predicts/our-guesses.csv`, columns `stated, market, horizon, direction,
  first, last, statement, reasoning, tag, confidence, source, model, lessons, grade, move,
  review`; *amended 2026-11-23* ([step 55](guesses-vs-base-rate.md)): and `base_rate`, the share
  of the market's past runs of the guess's weekdays that went its way, four decimals, filled on
  the first `guess` run that sees the row. Then `guesser` (*news* or *grounded*) and `prompt`
  (*news-1*, or *grounded-N* from the first line of `grounded_prompt.txt`); a row without them is
  the news guesser's. The front page and this stats page read the news guesser's rows only, until
  step 55's step 3. Step 49's two rows are kept, read with an empty tag and reasoning.
  *Amended 2026-11-24* ([step 56](honest-page.md), step 1): then `made`, the UTC time the guess
  was written, to the second; the rows before it carry the time of the commit that first added
  them, and a row without one counts as made at 23:59 New York on its stated day. A row whose
  `prompt` is `by-hand` was written outside the job, approved by the owner: it is shown as any
  guess and counts in neither guesser's record, lessons or comparison.
- **Numbers in a reason** (*amended 2026-11-22*): the reasoning may quote a figure from the news;
  a share is written *14 in 100*, since a bare *14* lost its unit when the `%` was banned. The
  ban on a percentage stands for the forecast itself: no chance and no size is claimed.
- **Tags:** momentum, reversal, interest rates, inflation, jobs, earnings, oil supply, geopolitics,
  policy, sentiment, season, other.
- **Docs:** this spec, step 49's amendment (two guesses become up to 50, the front page's choice,
  the repeat rule), the glossary (*horizon*, *try*, *promoted*, *lessons*, and *Subscription LLM*
  for its two new uses, the review and the lessons), a decisions entry (the model reviews itself
  and rewrites its lessons), status, changelog, roadmap row 50.

## Results

**Step 4, published, 2026-11-22.** `fortuneteller guess`, run by hand on Sunday 2026-11-22, the
ledger's first evening, on a copy of the store (closes to 2026-11-20), with `claude-opus-5-5`.
With no review yet, no lessons were written (version 0, as amended above). It printed *10 kept,
0 dropped*: the model offered 10 and all passed the checks.

**Expected 15 to 50 on each evening of the first week: not met on this one (10).** The prompt
asks the model to skip a market where the news gives it no real reason; whether that is why it
offered 10 is not shown by these numbers. The weekday evenings from 2026-11-23 add to the count.

The 10, counted from `docs/predicts/our-guesses.csv` (which also holds step 49's 2 rows):

| Tag | Guesses | Confidence |
| --- | --- | --- |
| interest rates | 4 (the dollar index, the yen, the Nikkei, homebuilders) | 1 medium, 3 low |
| oil supply | 2 (Brent, gasoline) | low |
| momentum | 2 (bitcoin, Coinbase) | low |
| reversal | 2 (the fear gauge, the S&P 500 over a year) | 1 medium, 1 low |

Horizons of the 10: 3 months, 6 quarters, 1 year. `docs/predicts/index.html`, written by
`stated_forecasts` (what `fortuneteller scoreboard` calls), shows the three tested forecasts and,
by the amended rule, the two of medium confidence (none is high, none promoted), soonest first:
the yen to 2026-12-31 and the fear gauge to 2027-01-15. `docs/predicts/stats/index.html`,
written the same way, lists all 12 rows, all open.
