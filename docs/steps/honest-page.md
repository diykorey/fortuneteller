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
  filled when step 1 was built).
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
  counts every guess it has shown, withdrawn ones among them: came true, did not, open. The same
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
  so this mostly repeats it."
- **No conflicts (advice rules).** Beside the footer's name: "The maker holds no position in any market
  shown." The legal opinion is the owner's errand; the questions for it are listed in the pull
  request.
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
| 1 | The ledger: `made`, the baseline, `by-hand` rows apart, 35 markets | Tests: a Nikkei guess made Monday 18:00 New York starts from Tuesday's Tokyo close; a euro guess made Monday 18:00 New York (winter) from Tuesday's 00:00 London bar; one made Monday 19:30 New York from Wednesday's; a bitcoin guess made Sunday 15:00 New York from Monday's close (its weekend closes are not stored, 635 or 636 a weekday and none on Saturday or Sunday, read 2026-11-24); a guess made at a close's very instant from the next; the same across the March change of clocks; a `by-hand` row in no guesser's record, lessons or comparison, and still on the stats page, the front page's picks and the tally; `COIN` dropped with its reason. The hand count equal to the code's |
| 2 | The front page: cards stay until graded, *withdrawn*, five at most, the front tally, the dropped words found and fixed | Tests: a shown guess missing from tomorrow's picks stays; with five staying, no new pick shows; a withdrawn one shows its date and is in the front tally; the inputs of 2026-11-23's proposal give back the approved words. The cause written here |
| 3 | The words: *the usual way*, counts, the guess card, reactions marked, the no-position line | Tests: no guess card carries the *up* or *down* badge class; no card says "in 10". The page seen in the browser at phone and desktop width, light and dark, nothing cut off or overlapping; a fresh reader with no financial training, as [predicts](predicts.md) has one, explains each card back correctly; the owner approves the words, printed in full in the console |
| 4 | The seeds without the consensus figures | The two seeds' columns are `day,time,ticker,kind`; the earnings outputs identical on a copy of the store |
| 5 | Results here, the roadmap row | Every bullet of the expected outcome marked right or wrong |

## How you know it is right

- **No guess can see its baseline:** step 1's tests place guesses just before and just after a
  close in Tokyo, London's 00:00 bar and bitcoin's 23:59 UTC close; each starts from the first close
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

### Step 1: the baseline

The hand count, written 2026-11-24 before the code ran: each row's `made` (the commit that added
it), in its market's zone against its close, and the day its baseline close falls on. They equal the
code's `guess_start` on every row.

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
2026-11-23 and the hand-made one of 2026-11-24 already started from Tuesday's. *Amended
2026-11-24:* #433, which held the job's 22 guesses of 2026-11-23, was merged by the owner's choice
after this table was first written, and the hand-made wheat row dropped for the job's own; the 21
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
