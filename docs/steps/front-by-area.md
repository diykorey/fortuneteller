# One front-page card per area

> Step 61 of the [Roadmap](../roadmap.md). The owner's choice of 2026-11-25 ("A"), after the
> question why the public predictions look the same from day to day
> ([why](../decisions.md#2026-11-25-one-front-page-card-per-area-after-step-57-by-the-owner)).
> Terms are in the [Glossary](../glossary.md): *front page*, *our guess*, *stated forecast*,
> *area*, *front pull request*.

## The goal

**In plain words:** each evening, a guess about a kind of market the page shows nothing on joins
the page, so the page covers every area there is a guess for, not the same three for weeks.

At the end: the front page's guesses are one per area not already on it, with no cap of five; an
evening's proposal (`docs/predicts/front-next.csv`) adds a guess in every area that has an open
guess and no card.

## The way to reach it

The page holds at most five cards ([front staging](front-staging.md)). The tested forecasts take
their room first, and since [step 56](honest-page.md) a guess shown stays until it is graded. On
2026-11-25 three long-run forecasts (the S&P 500 and the Nasdaq over a month, US home prices over
a year) and three guesses kept to 2026-12-04 and 2026-12-31 (the yen, bitcoin, Brent) fill it:
`front_proposal` has no room, so none of the evening's guesses, across 30 markets, can join
before 2026-12-04.

The cap goes; the rule that is already there, one guess per area and none in an area a tested
forecast or a staying card holds (`one_per_area`, `AREAS`), stays and becomes the only limit. The
eight areas (stocks, interest rates and inflation, currencies, energy, gold, food, crypto, homes)
bound the page at eight guesses beside the tested forecasts. The tested forecasts, which ones are
stated and how a card stays, do not change.

## The rule, fixed before anything is shown

This step measures nothing; it changes which guesses the page proposes. Written 2026-11-25,
before building.

- **Expected outcome:** on `main`'s files of 2026-11-25 (`front.csv`, `our-guesses.csv`, the
  three stated forecasts), the proposal keeps the yen, bitcoin and Brent and adds one guess each
  in food, interest rates and gold: coffee to 2027-03-31, the US 5-year yield to 2026-12-11 and
  gold to 2026-12-21, the open news guesses the existing order ranks first in each area. No area
  holds two guesses; stocks and homes get none, as the tested forecasts hold them.
- **On screen:** the published page at phone and desktop widths, with nine cards, reads in one
  column without overflow.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, reviewed by the goldfish | Its findings fixed or answered in the pull request |
| 2 | The cap removed | `FRONT_MOST` gone; a test: with three tested forecasts in two areas and three staying cards, the proposal adds one guess in each other area that has one, none in an area already held; the 2026-11-25 files give the expected outcome's six |
| 3 | The docs amended with a date | `front-staging.md`, `honest-page.md`, `predicts.md`, `our-guesses.md` and the glossary's *front page* and *front pull request* say one per area, not five |
| 4 | The first evening's proposal read, and the page | The next `front-<day>` pull request printed in full for the owner; once merged, the published page checked at both widths; Results here |

## How you know it is right

- **A wrong area map would show as two cards in one area:** the test and the expected outcome both
  count areas, not cards.
- **The ranking is not changed by accident:** the three added guesses are the ones the existing
  order (a promoted tag, then confidence, then the soonest end date) puts first in their area,
  named before building.
- **Nothing tested changes:** `forecasts.csv` and the stated forecasts are the same before and
  after on the same files.

## What this step does not do

It does not add company-results forecasts or change the guesses' lean to *down* (both open in
the decision), change which guesses are made, or make a shown card leave before it is graded.

## Technical details

- **Code:** `__main__.py`, `front_proposal` (the `room` from `FRONT_MOST` goes; `front_guesses`
  takes no `most`) and its test in `tests/test_front_staging.py` or beside it.
- **Docs:** this spec; dated amendments in the four step specs named in step 3; the glossary;
  status; the changelog; roadmap row 61.

## Results

Not yet measured.
