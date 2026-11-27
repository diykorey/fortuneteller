# One front-page card per area

> Step 61 of the [Roadmap](../roadmap.md). The owner's choice of 2026-11-25 ("A"), after the
> question why the public predictions look the same from day to day
> ([why](../decisions.md#2026-11-25-one-front-page-card-per-area-after-step-57-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *front page*, *our guess*, *stated forecast*,
> *area*, *front pull request*, *staying card*.

## The goal

**In plain words:** each evening, a guess about a kind of market the page shows nothing on joins
the page, so the page covers every area there is a guess for, not the same few for weeks.

At the end: the front page shows one card per area, tested forecasts and our guesses alike, at
most eight, with no cap of five; each evening's proposal (`docs/predicts/front-next.csv`) adds a
guess in every area that has an open guess and no card.

## The way to reach it

The page shows five cards at most, twice over: the proposal leaves room for five
(`FRONT_MOST` in `front_proposal`), and the page itself keeps the first five
(`predicts.html`). The stated forecasts come first, one per area already
([stated forecasts](stated-forecasts.md)); since [step 56](honest-page.md) a guess shown stays
until it is graded. On 2026-11-25 the page states two (the S&P 500 over a month, US home prices
over a year) and keeps three guesses to 2026-12-04 and 2026-12-31 (bitcoin to the 4th, the yen
and Brent to the 31st): five, so none of the open guesses, on 30 markets (28 of them the news guesser's), can
join before 2026-12-04.

Both caps go. The rule already in the proposal becomes the only limit: one guess per area, none in
an area a stated forecast or a staying card holds (`one_per_area`, `AREAS`). With eight areas
(stocks, interest rates and inflation, currencies, energy, gold, food, crypto, homes) the page
holds eight cards at most. Two edges are fixed now: a staying card past its last day, shown no
more but not yet graded, no longer holds its area; a withdrawn card, still shown, does. The
proposal draws on the news guesser's guesses alone, as today; the grounded guesser's and
hand-made ones stay off the front page.

## The rule, fixed before anything is shown

This step measures nothing; it changes which cards the page shows. Written 2026-11-25, before
building.

- **Expected outcome:** on `main` at `28d0c5f` (its `front.csv`, `our-guesses.csv` and the two
  stated forecasts), for New York's day 2026-11-25, the proposal keeps the yen, bitcoin and Brent
  and adds one news guess each in food, interest rates and gold: coffee to 2027-03-31, the US
  5-year yield to 2026-12-11 and gold to 2026-12-21, the first in each area by the existing order.
  No area holds two cards; stocks and homes get no guess.
- **On screen:** the page written from those files shows eight cards, one per area, and has no
  horizontal scroll at 420 and 1280 pixels wide.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Each finding fixed in the spec or answered in the pull request |
| 2 | Both caps removed | `FRONT_MOST` and the page's `slice(0, 5)` gone; tests: with two stated forecasts and three staying cards, the proposal adds one guess in each other area that has one and none in an area held; a staying card past its last day frees its area, a withdrawn one does not; the files at `28d0c5f` give the expected outcome's six; the page test finds eight cards and no horizontal scroll at both widths |
| 3 | The docs amended with a date | Every line that says five cards says one per area instead: `front-staging.md`, `honest-page.md`, `predicts.md`, `our-guesses.md`, `stated-forecasts.md`, `guess-ledger.md`, and the glossary's *area*, *front page* and *front pull request*; *staying card* added |
| 4 | The first evening's proposal, and the page | The next `front-<day>` pull request printed in full for the owner; once merged, the published page shows one card per area and no horizontal scroll at both widths; Results here |

## How you know it is right

- **A wrong area map would show as two cards in one area:** the tests, the expected outcome and the
  published page all count areas, not cards.
- **A cap left behind would show as five:** the page test counts eight cards from files that give
  eight.
- **The ranking is not changed by accident:** the three added guesses are named above, from the
  existing order, before building.
- **Nothing tested changes:** `forecasts.csv` and the stated forecasts are the same before and
  after on the same files.

## What this step does not do

It does not add company-results forecasts or change the guesses' lean to *down* (both open in
the decision), change which guesses are made, show the grounded guesser's guesses on the front
page, or make a shown card leave before it is graded.

## Technical details

- **Code:** `__main__.py`, `front_proposal` (no `room`; a staying card past its last day leaves
  `taken`) and `front_guesses` (no `most`); `src/fortuneteller/predicts.html` (no `slice`); tests
  in `tests/test_our_guesses.py` and the page test beside the predicts page's.
- **Docs:** this spec; the dated amendments of step 3; the glossary; status; the changelog;
  roadmap row 61.

## Results

Read 2026-11-27.

**In plain words:** the predictions page now shows one card for each area, eight of them, and
fits a phone and a laptop without sideways scrolling.

- **Expected outcome: right.** On `main`'s files at `28d0c5f`, for New York's day 2026-11-25, the
  proposal is the six the rule names: the yen, bitcoin and Brent stay; coffee to 2027-03-31, the
  US 5-year yield to 2026-12-11 and gold to 2026-12-21 join; no area holds two, and stocks and
  homes get no guess (step 2's test, and `draft_front` on those files, #464).
- **On screen: right.** The published page, written by the evening of 2026-11-26 (#480, merged
  23:39 UTC), read in a browser at 420 and 1,280 pixels: 8 cards at both, one per area (stocks,
  homes, the yen, bitcoin, oil, interest rates, coffee, gold), the page 401 pixels wide in a
  416-pixel view and 1,261 in 1,276, so no horizontal scroll (`li.card` counted and
  `scrollWidth` read in the page).
- **Step 4.** The first evening's proposal, *The front page's guesses, 2026-11-25* (#471), was
  printed in full for the owner and merged as it stood by `fortuneteller approve --yes`. Its gold
  card is the guess of 2026-11-25 to 2026-12-04, not the expected outcome's gold to 2026-12-21:
  the draft of 2026-11-25 ran on that evening's ledger, whose new gold guess ranks first by the
  existing order; the expected outcome was fixed on the files at `28d0c5f`, before it.
- **Late by a day.** The page kept its five cards until 2026-11-27: the evening of 2026-11-26
  stopped before writing it while a triggers' pull request (#457) was open, fixed by #474.
