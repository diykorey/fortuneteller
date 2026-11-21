# Fortuneteller predicts

> Step 47 of the [Roadmap](../roadmap.md), for [step 23](be-seen.md)'s readers. Terms are in the
> [Glossary](../glossary.md): *holds*, *cell*, *the answers that hold*. Asked for 2026-11-21 by the
> owner: "a simple page with the text *Fortuneteller predicts:* and 1 to 5 predictions, updated
> daily, attractive and modern."

## The goal

**In plain words:** one short, good-looking page a stranger can read in five seconds. It shows one
to five things the fortune teller says about the days ahead, each with its record.

At the end `https://diykorey.github.io/fortuneteller/predicts/` shows *Fortuneteller predicts:*
and one to five cards. The evening job rewrites it each weekday with the scoreboard
([step 44](readers.md)).

## The way to reach it

- **A prediction is an *if*, never a call before the number.** The project calls only once the
  actual lands (CLAUDE.md), and gives counts, never a probability. So each card names an event
  ahead, its condition and what followed, with its record as counts and whose record it is:
  *Wed, Dec 2, Salesforce reports earnings. If it misses forecasts → its shares trail the S&P 500
  the next trading day. Right 2,506 of 3,798 past S&P 500 reports, replayed.* A report after the
  close is met on the next trading day, as step 31 measures *the day*; one before the open or at a
  time not given, *that day*. A card is not a *prediction* in the glossary's sense (a link's
  direction with its band); it is an *if* with a record.
- **Which cards, from the scoreboard's data alone:**
  1. each release in the week ahead (`ahead`) with a walk-forward link that holds and would call:
     its `above` direction is set, so it is not silent on a shared day. Of those links, the one
     with the most replayed releases (`predictions`), on its *above* side (a surprise above the
     threshold). Rung 2 found the jobs report's 10-year yield and dollar links hold;
  2. for each day of the S&P 500's reports ahead ([step 45](sp500-on-the-page.md)), the largest
     company by market value, with each earnings kind whose day cell holds;
  3. sorted by day and then time, at most ten dated (two weeks of them, so that a page not
     rewritten for days still has some ahead);
  4. then up to three undated answers that hold, in *Ask*'s order, each a different *kind*
     (`#ask/FLOW/KIND`) from every card before it.

  Every cell or link used holds as *the answers that hold* count it: not a kind cell, not read as
  the period. The page, in the reader's browser, drops a dated card whose New York day has
  passed. It shows the dated cards left, then the undated, five at most. A report on the day the
  page is read is still shown. With three undated cards written, the page never shows fewer than
  three.
- **The design:** one column, a gradient headline and a card per prediction.
  - Up and down are shown in green and orange.
  - Light and dark follow the reader's system. It reads at phone width.
  - It uses the system's fonts and no outside script but the counter (step 23's Umami tag).
  - No percentage and no bar of a proportion, since rung 3's rule allows none yet.
  - Whether it looks attractive is the owner's call when it is published, from a screenshot at
    both widths.

## The rule, fixed before measuring

- **Bars:**
  1. every card's link or cell holds on the scoreboard's data of the same evening;
  2. the page shows between one and five cards;
  3. no card's text holds a `%`;
  4. a headless-Chrome render at 420 and 1280 pixels wide has no horizontal scroll.
- **Expected outcome:**
  - on the page written the evening of 2026-11-30, five cards, all dated: the largest S&P 500
    report of each of the next days. The jobs report of 2026-12-04 is among them only if fewer
    than five report days come before it;
  - should every dated card pass before a rewrite, three undated cards.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `predictions` in `__main__.py`, written with the scoreboard to `docs/predicts/index.html` | Tests: a release whose link holds gives a card, and one whose link does not gives none. The largest company of a day is chosen. A kind not holding gives no card. Undated cards fill to three without repeating a shown kind. No card holds a `%` |
| 2 | The template `src/fortuneteller/predicts.html` | A pytest test in CI renders it in headless Chrome and finds the headline, one to five cards, and no horizontal scroll at both widths |
| 3 | Published | The page is live. Bar 1 is checked by running `predictions` on the published `data.json` and finding each card's link among *the answers that hold* or a holding `ahead` link; bars 2 to 4 on the page. The date and results are written here |

## How you know it is right

- **Not a kind or period cell:** a test stubs a kind cell and a period cell that both say
  *holds*, and finds no card from either.
- **Earnings counts:** an earnings card's record says *past S&P 500 reports*, not the company's
  own. A test reads it.
- **New York's day:** the browser's filter uses New York's date. A test renders the page and
  finds a card dated far ahead shown and one dated in the past dropped, with the undated cards
  making up the rest.

## What this step does not do

No new measurement, no call before an actual, no percentage, no change to the scoreboard page.

## Technical details

- `predictions(data)` reads `ahead`, `earnings_ahead`, `ask` and `market_names` from the dict
  `scoreboard_data` returns. The page embeds `{"written", "predictions"}` at
  `__PREDICTS_DATA__`, as `scoreboard` embeds `data.json` in its `index.html`.
- The evening job commits `docs/predicts` with `docs/scoreboard`. `written` changes each
  evening, so the page differs every weekday and is committed every weekday. That is the daily
  update asked for.
- The Umami tag uses the scoreboard's website ID, so step 23 counts the two pages' visitors
  together.
- Docs: this spec, the glossary (*predictions page*), status, the changelog and roadmap row 47.
