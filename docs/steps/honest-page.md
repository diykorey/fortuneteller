# What the page claims, corrected

> Step 56 of the [Roadmap](../roadmap.md). The owner's choice of 2026-11-24 ("A then b then c"):
> the required fixes of the business review of 2026-11-24 first, as one step, then the technical
> fixes (step 57), then the publishing schedule (step 58). The review's table of required
> fixes is in this step's pull request; its eight required fixes are named below by what they fix. Where the
> review left a choice, the owner took the recommended one ("Option A", 2026-11-24) and stated
> that the maker holds no position. Terms are in the [Glossary](../glossary.md): *our guess*,
> *stated forecast*, *base rate*, *front page*, *the usual way*, *made*,
> *withdrawn*, *hand-made guess*.

## The goal

**In plain words:** the page says no more than its numbers show. A guess is graded only from a
price its writer could not have seen; a card once shown is not quietly taken back; the cards that
follow a market's normal drift say so; guesses look like hunches, not like tested cards; and the
public files take in no more of the data the project may not republish.

At the end: the eight fixes below are on `main` and on the published page, each checked as *How
you know it is right* says.

## The way to reach it

- **The baseline (look-ahead).** Today a guess is graded from the close before the first
  weekday after its evening ([the guess ledger](guess-ledger.md), *Graded by the closes alone*).
  Tokyo and Europe close hours before an 18:00 New York guess, and a Sunday guess starts from
  Friday's close, so the writer has seen what followed the price it is graded from. From now on
  each row carries `made`, the UTC time the guess was written, and its baseline is its market's
  first close after `made`, read with each market's close time and zone in
  `study.MVP_PRICE_SERIES`, as an event's reaction day is: a close at the very instant of `made`
  counts as seen. A row without `made` takes the time of the commit that first added it to the
  ledger, which is never earlier than it was written; *amended 2026-11-24*, step 1: written into
  the ledger by step 1, and a row still without one counts as made at 23:59 New York on its stated
  day. No ledger row is graded yet (the first ends
  2026-11-27), so every row takes the new baseline and no grade changes. Its base rate counts the
  weekdays from that close to its end date; a base rate already filled is recomputed (none was
  filled when step 1 was built). *Amended 2026-11-24, at step 5:* the evening job had filled them
  all, under the old rule, before step 1 was built; each was recomputed, as step 1's Results list.
- **Hand-made guesses apart (found while checking the review, 2026-11-24).** The two guesses added by hand that day carry
  `guesser` *news* and `prompt` *by-hand*, so they would count in the control guesser's record,
  its lessons and step 55's comparison. From now on a `by-hand` row counts in neither guesser's
  record, lessons or comparison; it stays in the ledger, on the stats page and eligible for the
  front page, and in the page's tally of guesses.
- **No single companies (advice rules).** `COIN` and `ALL` leave the markets a guess may name: 35 from
  37. The open Coinbase guess stays in the ledger and is graded as before.
- **Cards stay until graded (pruning).** A guess once on the front page stays there until it is
  graded, the evening after its end date's close is stored. The owner may still reword it, or
  withdraw it: a withdrawn card stays as long, marked *withdrawn on* its date, and is graded in the
  ledger as any other. Cards that stay take their places of the five first; the evening's new
  picks fill only what is left, so the page never shows more than five. The front page's own tally
  counts every guess it has shown, withdrawn ones among them: came true, did not, open.
  *Amended 2026-11-24, at step 5:* the page shows each card, like every card, until its end date;
  the evening's proposal keeps it in `front.csv` until it is graded. The same
  change finds why the evening proposal of 2026-11-23
  ([#434](https://github.com/diykorey/fortuneteller/pull/434), closed unmerged) dropped the
  approved words of 2026-11-22 although their locked fields matched, and fixes it.
- **The usual way (drift).** The long-run cards of [stated forecasts](stated-forecasts.md) are
  tested against a coin, so a market that usually rises passes. Their label becomes *The usual
  way* and their line says it is the market's normal direction over that stretch, not a forecast
  from news. Their rule, records and grades are unchanged.
- **Counts, not tenths.** "About 6 times in 10" is a rounded proportion, which [the
  Legend](../legend.md)'s *bare figures first* and [predicts](predicts.md)' "no percentage and no
  bar of a proportion" rule out. The line becomes the counts alone: "came true 29 of 34 times".
- **A guess looks like a hunch (mixing).** No green or orange badge on a guess: a grey one, with a
  💭 mark, on a card tinted the page's guess colour, all guesses after the tested cards.
- **Reactions, not forecasts (the day cells).** Wherever a cell of the day of the news reaches a
  reader (*Ask*, the link preview, the weekly LinkedIn post that `weekly-post` drafts), one line
  says: "Counted from the close before the news, so much of this move can come before you read the
  headline." The OPEC *oil up* to gasoline cell adds: "Oil's own move that day decides this kind,
  so this mostly repeats it." *Amended 2026-11-24, by the owner's approval of the printed words:*
  the line reads "A move on the day is counted from the close before the news, so much of it can
  come before you read the headline.", and the OPEC one "Oil's own move that day decides this kind
  of decision, so this mostly repeats it."
- **No conflicts (advice rules).** Beside the footer's name: "The maker holds no position in any market
  shown." The legal opinion is the owner's errand; the questions for it are listed in the pull
  request. *Amended 2026-11-24, after the plain-words check found "position" unclear, by the
  owner's approval:* "The maker has no money in any market shown."
- **The consensus figures (licence).** The earnings flows read only `day`, `time`, `ticker` and
  `kind`. The scripts still make each kind from the source's figures as they fetch them, and keep
  the figures in `data/cache/` (not committed), where a later check can read them. `eps`, `forecast` and `surprise` leave `data/seed/earnings.csv` and
  `data/seed/earnings_sp500.csv`, and the scripts that write them (`scripts/nasdaq_earnings.py`,
  `scripts/yahoo_earnings.py`) stop writing them to `data/seed/`. The git history is left as it is.

## The rule, fixed before anything is shown

This step measures nothing new: it changes how guesses are graded before any is graded, and what
the page says.

- **Expected outcome, written first:**
  - Every ledger row keeps its grade (none yet); each open row's baseline is its market's first
    close after `made`. The hand count: for every row in the ledger when step 1 is built, its
    `made` (from the commit that added it, for the rows before step 1), its market's close time
    and zone, and the baseline day, listed here by hand before the code runs and equal to the
    code's on every row.
  - Each recomputed base rate listed here, old beside new.
  - `fortuneteller excess` counts no `by-hand` row for either guesser.
  - A guess naming `COIN` or `ALL` is dropped with its reason.
  - Every stated forecast's record, grade and hold unchanged; only its label and line change.
  - The front page shows at most five cards on every evening, a card shown stays until graded.
  - After the columns leave the seeds (step 4), every `follows`, `raw-move`, scoreboard and *Ask*
    output of the three earnings flows (`earnings`, `earnings500`, `splits`) identical byte for byte
    to the same outputs after step 3. Step 3 changes words only: every number, cell and answer of
    *Ask* and the scoreboard identical before and after it.
  - The words shown read clearly to a reader with no financial training (the plain-words check) and
    are approved by the owner, printed in full in the console, before they are published.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The ledger: `made`, the baseline, `by-hand` rows apart, 35 markets | Tests: a Nikkei guess made Monday 18:00 New York starts from Tuesday's Tokyo close; a euro guess made Monday 18:00 New York (winter) from Tuesday's 00:00 London bar; one made Monday 19:30 New York from Wednesday's; a bitcoin guess made Sunday 15:00 New York from Monday's close (its weekend closes are not stored, 635 or 636 a weekday and none on Saturday or Sunday, read 2026-11-24); *amended 2026-11-24, before step 1 was built (425b312): written first as "from Monday 00:00 UTC", which is no close of bitcoin's;* a guess made at a close's very instant from the next; the same across the March change of clocks; a `by-hand` row in no guesser's record, lessons or comparison, and still on the stats page, the front page's picks and the tally; `COIN` dropped with its reason. The hand count equal to the code's |
| 2 | The front page: cards stay until graded, *withdrawn*, five at most, the front tally, the dropped words found and fixed | Tests: a shown guess missing from tomorrow's picks stays; with five staying, no new pick shows; a withdrawn one shows its date and is in the front tally; the inputs of 2026-11-23's proposal give back the approved words. The cause written here |
| 3 | The words: *the usual way*, counts, the guess card, reactions marked, the no-position line | Tests: no guess card carries the *up* or *down* badge class; no card says "in 10". The page seen in the browser at phone and desktop width, light and dark, nothing cut off or overlapping; a fresh reader with no financial training, as [predicts](predicts.md) has one, explains each card back correctly; the owner approves the words, printed in full in the console |
| 4 | The seeds without the consensus figures | The two seeds' columns are `day,time,ticker,kind`; the earnings outputs identical on a copy of the store |
| 5 | Results here, the roadmap row | Every bullet of the expected outcome marked right or wrong |

## How you know it is right

- **No guess can see its baseline:** step 1's tests place guesses just before and just after a
  close in Tokyo, London's 00:00 bar and bitcoin's 23:59 UTC close (*amended 2026-11-24, before
  step 1 was built (425b312), from "bitcoin's UTC day"*); each starts from the first close
  strictly after it was made.
- **Nothing measured changes:** steps 3 and 4 compare every output on a copy of the store, as the
  country steps do.
- **Nobody is surprised by the words:** the owner approves them before they are published.

## What this step does not do

The technical review's fixes (step 57), the publishing schedule (step 58), the review's
improvements (a luck baseline from random dates, bars against the base rate, correlated markets
counted as one group), the legal opinion, and rewriting the public history.

## Technical details

- **Code:** `__main__.py` (`keep_guesses`, `grade_guesses`, `grade_forecasts`, `with_base_rates`,
  `_mine`, `counted_guesses`, `front_rows`, the guesser's market list), `study.py` (the first close
  after a time), `predicts.html`, the two earnings scripts.
- **Data:** `docs/predicts/our-guesses.csv` (`made`), `docs/predicts/front.csv` (`withdrawn`), the
  two earnings seeds.
- **Docs:** this spec; dated amendments in [the guess ledger](guess-ledger.md), [front
  staging](front-staging.md), [stated forecasts](stated-forecasts.md),
  [predicts](predicts.md) and [guesses against the base rate](guesses-vs-base-rate.md);
  `docs/schema.md` if a stored column changes; the glossary; status; the changelog; roadmap row 56.

## Results

### Step 5: the expected outcome, marked

Each bullet of *The rule, fixed before anything is shown*, against what the steps found.

- **Every ledger row keeps its grade; each open row's baseline is its market's first close after
  `made`: wrong at step 1, right after step 5's fix.** None of the 35 rows is graded (the
  ledger's `grade` column, 2026-11-24), so no grade changed. Step 1's hand count was to equal the
  code's `guess_start` on every row, and it did not. For ten rows made on Sunday 2026-11-22,
  `guess_start` gave the Sunday itself, as their market's Sunday close (bitcoin's) or no Sunday
  close at all still lay ahead: `COMP`, `GC / XAU`, `VIX`, `SPY / ES`, `DXY`, `BTC`, `COIN`,
  `BRN`, `UGA`, `ITB`. `USDJPY`, past Sunday's 00:00 London bar, already got Monday. Grading was
  unaffected, but their base rates counted one weekday too many. Step 5 rolls a weekend start to
  Monday (`guess_start`; tests: a bitcoin guess made Sunday, and two S&P 500 guesses made Sunday
  and Friday after the close, each start Monday) and recomputes those ten. A holiday is not rolled:
  `NKY`'s start is Monday 2026-11-23, a holiday in Tokyo, and grading takes Tuesday's close. Its
  base rate counts weekdays, holidays among them, as every base rate does.
- **Each recomputed base rate listed, old beside new: right**, every row in the table below:
  before step 1 and after it from the ledger in git, after step 5 from `with_base_rates`, which
  `fortuneteller guess` runs to fill the ledger, on a copy of the store of 2026-11-24 01:25.
- **Step 1's tests:** `test_a_guess_starts_from_its_market_s_first_close_after_it_was_made`
  (Tokyo, London's bar in winter and after the March change of clocks, a close's very instant,
  bitcoin on Sunday, and from step 5 the S&P 500 on Sunday and on Friday evening),
  `test_a_weekend_bitcoin_guess_is_graded_from_monday_s_close`,
  `test_a_row_made_unknown_counts_as_made_late_on_its_stated_day` and
  `test_a_base_rate_counts_the_weekdays_from_the_guess_s_start`, all passing with `uv run pytest`.
  Each starts a guess from the first close strictly after it was made, so no guess sees its
  baseline. The guess made by hand on 2026-11-24 had none before step 1.
- **`fortuneteller excess` counts no `by-hand` row: right, by test only.**
  `test_a_hand_made_guess_is_in_no_guesser_s_record_but_still_shown` counts one graded news guess
  and leaves out the hand-made one. On the store, `fortuneteller excess` prints "0 counted" for
  both guessers, as no guess is graded yet.
- **A guess naming `COIN` or `ALL` is dropped with its reason: right.** The guesser's check list
  test drops both as "a single company", and `test_the_guesser_is_not_offered_a_single_company`
  finds 35 markets offered.
- **Every stated forecast's record, grade and hold unchanged: right.** Step 1 stopped grading
  guesses with `grade_forecasts` and left that function as it was. On two copies of the store of 2026-11-24 01:25,
  `fortuneteller scoreboard` was run with the code before step 3 (#440's merge) and after it
  (#441's). The page data `data.json`, the stated forecasts and *Ask* among it, is byte for byte
  the same, and the ledger it rewrites too. `fortuneteller weekly-post` differs by one line, the
  day-of-news note step 3 adds.
- **At most five cards on the front page every evening: right; a card shown staying until
  graded: wrong as the rule was written.** The proposal fills only what the staying cards leave of
  five (`test_with_five_cards_staying_no_new_guess_is_picked`). The page drops a card at its end
  date, a day or so before it is graded; only the proposal keeps it until graded. Step 2's Results
  said so, and the rule was amended at step 5 to what was built, rather than the page changed.
  With the fixed code, in a one-off script calling `front_proposal`, 2026-11-23's own
  inputs (the approved `front.csv` of 2026-11-22, #434's ledger and the three open tested
  forecasts) give back the three approved cards in the owner's words.
- **The earnings outputs identical after step 4: right**, as step 4's Results say.
- **The words read clearly and were approved before they were published: approved, and each card
  explained back; four points of the page still unclear.** The owner
  approved them on 2026-11-24. After the five fixes, a fresh reader with no financial training
  read the page and explained each of the five cards back correctly: what it says, by when, and
  how it will be checked. They named the two *usual way* cards as not forecasts from news, and the
  three guesses as hunches with no record. They also listed 19 points that confused them, most in
  the guesses' own reasons ("Brent", "the war", "bitcoin funds"). Four are about the page itself:
  - the first count says 3 *usual way* cards are open but only two are shown;
  - "ever shown here" beside "Guesses: 25" is unclear;
  - a guess *made Nov 22* compares with *November 23*;
  - the usual-way card starts on November 20 while the guesses start on November 23.
  The first was among step 3's five findings and is not fixed: the count includes a third stated
  forecast whose card is not shown. These are left to the owner, and none changes a number.

| Stated | Market | Guesser | Before step 1 | Step 1 | Step 5 |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | `COMP` | news | 0.4230 | 0.4230 | 0.4237 |
| 2026-11-22 | `GC / XAU` | news | 0.4334 | 0.4334 | 0.4362 |
| 2026-11-22 | `VIX` | news | 0.5406 | 0.5406 | 0.5359 |
| 2026-11-22 | `SPY / ES` | news | 0.7270 | 0.7270 | 0.7243 |
| 2026-11-22 | `DXY` | news | 0.4944 | 0.4944 | 0.4935 |
| 2026-11-22 | `USDJPY` | news | 0.4690 | 0.4662 | 0.4662 |
| 2026-11-22 | `NKY` | news | 0.4217 | 0.4254 | 0.4254 |
| 2026-11-22 | `BTC` | news | 0.4451 | 0.4451 | 0.4453 |
| 2026-11-22 | `COIN` | news | 0.5525 | 0.5525 | 0.5601 |
| 2026-11-22 | `BRN` | news | 0.4659 | 0.4659 | 0.4637 |
| 2026-11-22 | `UGA` | news | 0.4181 | 0.4181 | 0.4229 |
| 2026-11-22 | `ITB` | news | 0.4301 | 0.4301 | 0.4290 |
| 2026-11-23 | `ETH` | news | 0.5058 | 0.5058 | 0.5058 |
| 2026-11-23 | `EURUSD` | news | 0.5049 | 0.5041 | 0.5041 |
| 2026-11-23 | `GBPUSD` | news | 0.4901 | 0.4902 | 0.4902 |
| 2026-11-23 | `XLE` | news | 0.4190 | 0.4213 | 0.4213 |
| 2026-11-23 | `UNG` | news | 0.5799 | 0.5794 | 0.5794 |
| 2026-11-23 | `UST5Y / ZF` | news | 0.4924 | 0.4911 | 0.4911 |
| 2026-11-23 | `T5YIE` | news | 0.4657 | 0.4653 | 0.4653 |
| 2026-11-23 | `DAX` | news | 0.6401 | 0.6389 | 0.6389 |
| 2026-11-23 | `SHCOMP` | news | 0.5103 | 0.5094 | 0.5094 |
| 2026-11-23 | `USDCNY` | news | 0.5734 | 0.5716 | 0.5716 |
| 2026-11-23 | `USDCHF` | news | 0.5628 | 0.5624 | 0.5624 |
| 2026-11-23 | `KC` | news | 0.4929 | 0.4963 | 0.4963 |
| 2026-11-23 | `WEAT` | news | 0.5825 | 0.5887 | 0.5887 |
| 2026-11-23 | `UNG` | grounded | 0.6392 | 0.6362 | 0.6362 |
| 2026-11-23 | `ITB` | grounded | 0.4164 | 0.4147 | 0.4147 |
| 2026-11-23 | `VIX` | grounded | 0.5439 | 0.5422 | 0.5422 |
| 2026-11-23 | `BRN` | grounded | 0.4517 | 0.4520 | 0.4520 |
| 2026-11-23 | `XLU` | grounded | 0.3876 | 0.3878 | 0.3878 |
| 2026-11-23 | `T5YIE` | grounded | 0.4584 | 0.4597 | 0.4597 |
| 2026-11-23 | `USDJPY` | grounded | 0.4694 | 0.4731 | 0.4731 |
| 2026-11-23 | `GC / XAU` | grounded | 0.4377 | 0.4409 | 0.4409 |
| 2026-11-23 | `USDCAD` | grounded | 0.5110 | 0.5086 | 0.5086 |
| 2026-11-24 | `UST10Y / ZN` | hand-made | — | 0.4856 | 0.4856 |

### Step 4: the seeds without the consensus figures

Both seeds now hold `day,time,ticker,kind`: 2,212 rows in `earnings.csv` and 25,983 in
`earnings_sp500.csv`, the same rows as before without the three figures. No two rows were the
same on the four columns kept, so no row was merged. From now on `scripts/nasdaq_earnings.py seed`
writes the full rows to `data/cache/figures/`, which is not committed, under the seed's name.
`scripts/yahoo_earnings.py agree` reads Nasdaq's figures from there. The test that checks each
kind against its surprise reads the same files and is skipped where they are absent, as in CI.

On two copies of the store of 2026-11-24 01:25, the three earnings flows (`earnings`,
`earnings500`, `splits`) were loaded from `main`'s seeds into one copy and from this step's into
the other. Their events are the same: 2,212, 25,983 and 105, as each flow's load reports them
(the line `fortuneteller load-releases` prints, "loaded 2212 earnings reports"). Every output is byte for byte the
same on both copies: `follows` and `follows --after-the-day`, `raw-move` and `raw-move --week` for
each flow, and the scoreboard's `data.json` and page, *Ask* among them. The only line that
differs is the scoreboard's "written to", which names each copy's own folder.

### Step 3: the words

The long-run cards are labelled *The usual way*, and their badge and line say "Usually higher".
Their record is the counts alone ("Went this way in 402 of 666 past months", from the page data
`fortuneteller scoreboard` writes). A guess card is
labelled "💭 Our guess", with a grey badge on a pale card with a dashed border. A withdrawn card
says when it was taken back. The page counts the guesses it has ever shown. The footer says "The
maker has no money in any market shown." The day-of-news line is on the scoreboard's holds, on
*Ask*, in the weekly post and on the link preview; the OPEC note is on its cell.

Tests (`tests/test_predicts.py`, `tests/test_stated_forecasts.py`): no guess card has the *up*
or *down* class, no card says "in 10", and the footer and the withdrawn note are present. Every
number, cell and answer is the same before and after: only the words changed (*written before
the check; step 5's comparison on a copy of the store bears it out*).

The page was rendered in headless Chrome with the live data and the three cards, one of them
marked withdrawn. At 390 and 1280 pixels wide, in light and dark, nothing was cut off or
overlapping.

A fresh reader with no financial training read the drafted page. They found five problems:
"drift" was unclear; the usual-way cards looked like forecasts; "holds no position" was jargon;
the counts at the top did not match the cards; and the cards still named November 20 although
they are now graded from November 23. Each was fixed (*corrected at step 5:* but the
first count still includes a stated forecast whose card is not shown). The owner approved the words, printed in
full in the console, on 2026-11-24 ("A"). The three cards on the page now name November 23, and
Brent's card drops Friday's price of 92.57 dollars.

### Step 2: the cards that stay

The cause of #434: the evening job copied `front-next.csv` into `front.csv` after switching its
tree to a fresh `main`. The file is tracked, so the switch had put back `main`'s copy, committed
2026-11-22 18:32 before the owner reworded the cards; #434's `front.csv` is byte for byte that
copy. Tonight's proposal (in #433) was never read. When the evening's own pull request merges
first, as it does on an evening with no trigger, `main` holds tonight's copy and the bug hides.
The job now keeps tonight's file aside before the switch.

Tests (`tests/test_our_guesses.py`): a shown guess stays first in the owner's words when not
picked again; one deleted comes back withdrawn that evening; with five staying no new guess is
picked; a graded one leaves; `shown` is set once and the tally counts every shown guess. The
page shows each card to its end date, as before; the proposal keeps it to its grade (the rule
amended at step 5 to say so).

### Step 1: the baseline

The hand count, written 2026-11-24 before the code ran: each row's `made` (the commit that added
it), in its market's zone against its close, and the day its baseline close falls on. They equal the
code's `guess_start` on every row. *Corrected at step 5:* not on ten rows, step 5's Results.

| Rows | `made` (UTC) | Read against | Baseline close |
| --- | --- | --- | --- |
| `COMP`, `GC / XAU` | 2026-11-22 07:20:00 (735fd77) | Sunday in New York | Monday 2026-11-23 |
| `VIX`, `SPY / ES`, `DXY`, `COIN`, `BRN`, `UGA`, `ITB` | 2026-11-22 09:08:01 (3e0345c) | Sunday in New York | Monday 2026-11-23 |
| `USDJPY` | the same | after Sunday's 00:00 London bar | Monday 2026-11-23 |
| `BTC` | the same | before Sunday's 23:59 UTC close, which is not stored | Monday 2026-11-23 |
| `NKY` | the same | 18:08 Sunday in Tokyo; Monday is a holiday in Japan | Tuesday 2026-11-24 |
| `UST10Y / ZN` | 2026-11-24 00:02:59 (0adfa50) | 19:02 Monday in New York, after the close | Tuesday 2026-11-24 |
| The job's 21 of 2026-11-23 but `ETH` | 2026-11-23 23:25:41 (1ef7ff7, merged with #433) | after every close of Monday: New York, Europe, Tokyo, Shanghai, London's bar | Tuesday 2026-11-24 |
| `ETH` of 2026-11-23 | the same | before Monday's 23:59 UTC close | Monday 2026-11-23 |

Before, the twelve rows of 2026-11-22 started from Friday 2026-11-20's close; the job's of
2026-11-23 from Monday's, and the hand-made one of 2026-11-24 already from Tuesday's.
*Corrected 2026-11-24, at step 5:* this sentence first said the job's rows of 2026-11-23 had
started from Tuesday's; under the old rule, the close before the first weekday after the evening,
they started from Monday's, which is why their base rates move below. *Amended
2026-11-24:* #433, which held the job's 22 guesses of 2026-11-23, was merged by the owner's choice
after this table was first written, and the hand-made wheat row dropped for the job's own; the 22
rows of 2026-11-23 were counted by hand the same way before the code ran, and all 35 equal it.

The base rates had been filled by the evening job under the old rule, so each is recomputed (old,
new), unchanged where the span keeps its weekdays: `USDJPY` of 2026-11-22 0.4690, 0.4662; `NKY`
0.4217, 0.4254; and every row of 2026-11-23 but `ETH`, each by at most 0.0062: `EURUSD` 0.5049,
0.5041; `GBPUSD` 0.4901, 0.4902; `XLE` 0.4190, 0.4213; `UNG` 0.5799, 0.5794; `UST5Y / ZF`
0.4924, 0.4911; `T5YIE` 0.4657, 0.4653; `DAX` 0.6401, 0.6389; `SHCOMP` 0.5103, 0.5094; `USDCNY`
0.5734, 0.5716; `USDCHF` 0.5628, 0.5624; `KC` 0.4929, 0.4963; `WEAT` 0.5825, 0.5887; the grounded
guesser's `UNG` 0.6392, 0.6362; `ITB` 0.4164, 0.4147; `VIX` 0.5439, 0.5422; `BRN` 0.4517,
0.4520; `XLU` 0.3876, 0.3878; `T5YIE` 0.4584, 0.4597; `USDJPY` 0.4694, 0.4731; `GC / XAU` 0.4377,
0.4409; `USDCAD` 0.5110, 0.5086. The hand-made `UST10Y / ZN` gets its first, 0.4856. Read with
`fortuneteller guess`'s own `with_base_rates` on the store of 2026-11-24, its last close 2026-11-20.
