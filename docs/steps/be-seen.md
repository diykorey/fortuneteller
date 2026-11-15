# Be seen, and count it

> Step 23 of the [Roadmap](../roadmap.md#phase-4-prove-the-loop-show-the-page-be-seen), the last of
> phase 4. Terms are in the [Glossary](../glossary.md): *unique visitor*, *Umami*, *seen*, and
> *the gate* (the 2027-01-31 check, not the calibration gate).

## The goal

**In plain words:** people outside the project see the fortune teller, and how many is counted the
same way every week.

At the end, the [scoreboard page](scoreboard.md) carries a cookie-free visitor counter, and each
week a short post on the owner's LinkedIn profile says what the fortune teller said that week and
how it did, with a link to the page. Each week's count of unique visitors is written in
`docs/steps/be-seen-weeks.csv`. The gate reads its *readers* bar from that file: at least 100
unique visitors in one week. Both choices are the owner's (2026-11-15): Umami Cloud for the
counter, LinkedIn for the channel.

## The way to reach it

- **The counter: Umami Cloud's free tier.** Its script, one tag in the page's template
  (`src/fortuneteller/scoreboard.html`), sets no cookie (Umami's documentation; the check below
  looks). Umami counts a *unique visitor* as one hash of the site, the visitor's address and
  browser, and a salt it changes each month: one person on one browser is one visitor within a
  calendar month. The tag sets `data-do-not-track="true"`, so a browser that asks not to be
  tracked is not counted, and `data-domains="diykorey.github.io"`, so a copy of the page opened
  elsewhere is not counted. The owner's browsers are left out by Umami's *disabled flag*: the
  browser storage key `umami.disabled` set to `1`, once per browser; a private window or cleared
  site data loses it, and such a visit by the owner is counted, a small overcount said plainly.
- **The week:** Monday 00:00 to Sunday 23:59 UTC, the same for the count and the post.
- **The count: read from Umami's API, not the dashboard.** `fortuneteller weekly-post` asks
  Umami's API for the week's distinct visitors over exactly that range in UTC, so a dashboard set
  to another time zone, or a week added up from its days, cannot enter the file. A week that
  crosses the first of a month spans two salts, and a returning visitor would count twice in it;
  such a week is asked as its two parts, and its count is the larger part.
- **The post: drafted from the data, published by the owner.** `weekly-post` prints a draft for
  the last full week: each live call in `data/calls.csv` logged that week (by `logged_at`), its
  direction and market, and its grade, *right*, *wrong* or *pending*; the record of graded calls
  so far, right and wrong in counts, as `score` counts them; and the page's link. Triggers
  (`data/trigger-log.csv`) are not calls and are not in it. A week with no call says *no call this
  week*. It ends *an entertainment tool, not advice*. The owner may reword it and publishes it;
  the numbers stay.
- **The obstacle: reach, not the counter.** The owner's network is the first audience, and a
  weekly post about one call or none is easy to scroll past. The page must answer the reader's
  question (step 22's ask section) by the first post, so a visitor finds something. The count is
  what it is: no paid promotion, no bought followers, no asking colleagues to click.

## The rule, fixed before the first post

- **The window:** every week from the one the counter is first published in to the week of
  2027-01-25 to 2027-01-31. That last week is read on Monday 2027-02-01, so the *readers* bar is
  judged that day, a day after the gate's other two bars; the gate's date is left as it is.
- **The bar is the gate's:** at least 100 unique visitors, as the weeks file has them, in one week
  of the window. Met: *seen*. Not met: *not seen*, with the best week's count. No post by
  2027-01-01 still leaves the counter counting; the verdict says how many posts were made.
- **Counted, not barred:** each week's visitors, whether a post went out, and its reactions as
  LinkedIn shows them on the Monday the row is written.
- **Expected outcome, written first:** *not seen*. A guess from a network of a few hundred, a few
  in a hundred clicking a link: the best week 30 to 50 unique visitors, the week of the first
  post; then 10 to 20 a week. A weekly post of mostly silent rows gives little reason to come back.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The counter: the owner creates the Umami Cloud site, gives its website ID (public) and an API key (a secret, kept in `.env` as `FT_UMAMI_API_KEY`); the tag goes into the template | A test finds one Umami tag in the written page, with the ID, `data-do-not-track` and `data-domains`. The published page, opened from a browser without the flag, is one visitor by the API for that hour; opened again with the flag, still one. The date is written here |
| 2 | `fortuneteller weekly-post` | Tests: a week with a graded call prints it as *right* or *wrong*; a pending call says *pending*; a week with none says *no call this week*; the record equals `score`'s right and wrong counts; a week across a month's first is asked in two parts and the larger kept; the last line is the disclaimer |
| 3 | The first post, after step 22's page is published | Its date and address are in the weeks file's row for its week, written the next Monday with the count |
| 4 | Every Monday to 2027-02-01: the week's row, and the next post | A row for each week of the window; on 2027-02-01, the verdict here against the bar |

## How you know it is right

- The page written by `fortuneteller scoreboard` has the tag exactly once; the page opened from a
  file on disk is not counted (step 1's look, from the API).
- A visit from a flagged browser does not move the count (step 1's look).
- A draft for a week whose only call was graded *wrong* says *wrong*, not a softer word.
- A week whose visitors arrive on different days but are the same browser counts once: the API's
  distinct count, not the sum of the days, which a test with a stubbed API reply checks.
- The page shows no cookie banner because none is set: the published page's cookies, read in a
  browser after a visit, are none from Umami.

## What this step does not do

No paid promotion, no second channel, no cookies or sign-in on the page, no automatic posting: the
owner publishes each post. The counter counts visits to the scoreboard page only, not the
repository.

## Technical details

- **Tag:** `<script defer src="https://cloud.umami.is/script.js" data-website-id="ID"
  data-do-not-track="true" data-domains="diykorey.github.io"></script>` in the template's head;
  the ID in the template, one place, since the page has one site.
- **API:** Umami Cloud's website stats for `startAt` and `endAt` in milliseconds UTC, with the key
  in the `x-umami-api-key` header; the reply's visitors. No key: the draft prints and the count
  line says *no API key*.
- **Command:** `weekly-post` in `__main__.py`, reading `study.read_calls`; it writes nothing. The
  owner or the session adds the week's row to the weeks file. Tests in `tests/test_scoreboard.py`.
- **File:** `docs/steps/be-seen-weeks.csv`: `week_start, unique_visitors, crosses_month, posted,
  post_date, post_url, reactions`.
- **Docs:** this spec; the glossary (*unique visitor*, *Umami*, *disabled flag*, *seen*); the
  [scoreboard spec](scoreboard.md)'s "no per-visitor state", amended to say the page keeps none
  itself and Umami counts visits; `docs/status.md`, the changelog and roadmap row 23.
