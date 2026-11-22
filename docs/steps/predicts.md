# Fortuneteller predicts

> Step 47 of the [Roadmap](../roadmap.md), for [step 23](be-seen.md)'s readers. Terms are in the
> [Glossary](../glossary.md): *holds*, *cell*, *the answers that hold*. Asked for 2026-11-21 by the
> owner: "a simple page with the text *Fortuneteller predicts:* and 1 to 5 predictions, updated
> daily, attractive and modern."

## The goal

**In plain words:** one short, good-looking page a stranger can read in five seconds. It shows one
to five things the fortune teller says about the days ahead, each with its record.

At the end `https://diykorey.github.io/fortuneteller/predicts/` shows *Fortuneteller predicts:*
and one to five cards (none to five since 2026-11-22, below). The evening job rewrites it each weekday with the scoreboard
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

- **In plain words** (*amended 2026-11-21*, asked by the owner before publishing: "obviously
  clear for a random person without financial education"). A reader with no financial training
  (a fresh subagent) read the rendered cards, and its findings set the wording:
  - no code and no term unexplained: *the interest the US government pays to borrow money for 10
    years*, not *US Treasury 10Y*; *announces its profit for the last three months*, not
    *reports earnings*; market hours given in New York time;
  - a move against the S&P 500 says what it means: *its stock falls behind the average big US
    stock: it may fall, or rise less*;
  - the record says whose it is and both sides, as counts: *Across 3,798 profit announcements by
    many big US companies (not just Dell), this held 2,506 times and failed 1,292 times*;
  - an earnings card says that no rule passed for a profit that matches or beats the predictions;
  - the intro opens with *These are not forecasts that something will happen*, says the page
    gives which way and not by how much, and carries *for fun, not financial advice*.

- **Forecasts only** (*amended 2026-11-22, by the owner*: "we need to state without any if
  then; if we cannot forecast better, do not do it at all"). The *if* cards are gone: the page
  shows [stated forecasts](stated-forecasts.md) and [our guesses](our-guesses.md) only. Bar 2
  becomes none to five cards; a page with none says *Nothing passed our tests today*.
- **Bright cards** (*amended 2026-11-22, by the owner*, option A of five mock-ups: bright cards,
  a scoreboard list, colour tiles, a newspaper, a swipe deck). A white page with 18px text and
  strong contrast, kept in dark mode. Each card shows an icon and a short name for its market, a
  green *▲ Up by* or orange *▼ Down by* its end date, the sentence, the days left, its record (or
  *No record yet* for a guess) and one line of why; a guess's full reasoning is folded under
  *Full reasoning*. The explanation is folded under *How it works*, and the two tallies are
  badges. The stats page takes the same colours. The bars are unchanged; the render tests check
  the same five cards at phone and desktop widths, with no sideways scroll.
- **The front door** (*amended 2026-11-22, by the owner*): the site's bare address,
  `docs/index.html`, sends readers here instead of to the scoreboard, which this page links to as
  *Every number behind the tested forecasts*; the scoreboard is restyled to match as its own change.

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
| 2 | The template `src/fortuneteller/predicts.html` | A pytest test in CI renders it in headless Chrome and finds the headline, one to five cards (none to five since 2026-11-22), and no horizontal scroll at both widths |
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
