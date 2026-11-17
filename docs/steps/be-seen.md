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
  such a week is asked as its two parts, and its count is the larger part. The larger part is a
  floor, not the week's true count: a week of 100 split 60 and 40 is written as 60.
  *Amended 2026-11-17, by the owner:* Umami Cloud's free plan has no API key, and the owner pays
  nothing before there are customers. The API is read through the site's *share link* instead:
  the link's public code gives the site and a signed token, and the same stats are asked with it.
  The token is one of the ways in that Umami's own API description lists, but its free use is not
  promised; if it stops answering, the week is read from the dashboard, set to UTC, over a custom
  range, and the row says so. The share link makes the site's dashboard public, each visit
  included: its time, city, browser, system, screen and language, no name or address. On a page
  this small such a row can point to one reader; the owner judged it not private data and keeps
  the link whole (2026-11-17).
- **The post: drafted from the data, published by the owner.** `weekly-post` prints a draft for
  the last full week: each live call in `data/calls.csv` logged that week (by `logged_at`), its
  direction and market, and its grade, *right*, *wrong* or *pending*; the record of graded calls
  so far, right and wrong in counts; and the page's link. *Amended 2026-11-15, in step 2:* a call
  is a row whose outcome is `call`, as the scoreboard shows it; a row leaning *too few* is not
  one. Each is graded as `score` and the scoreboard grade it. The releases of the week are named
  too, so a week with only silent rows still says what came out. Triggers
  (`data/trigger-log.csv`) are not calls and are not in it. A week with no call says *no call this
  week*. It ends *an entertainment tool, not advice*. The owner may reword it and publishes it;
  the numbers stay.
- **The obstacle: reach, not the counter.** The owner's network is the first audience, and a
  weekly post about one call or none is easy to scroll past. The page must answer the reader's
  question (step 22's ask section) by the first post, so a visitor finds something. The count is
  what it is: no paid promotion, no bought followers, no asking colleagues to click.

## The rule, fixed before the first post

- **The window:** every week from the one the counter is first published in to the week of
  2027-01-25 to 2027-01-31. *Amended 2026-11-17:* the first week counts even if the counter went
  up mid-week, since a part week can only count fewer; its row names the day it went up. That last week is read on Monday 2027-02-01, so the *readers* bar is
  judged that day, a day after the gate's other two bars; the gate's date is left as it is.
- **The bar is the gate's:** at least 100 unique visitors, as the weeks file has them, in one week
  of the window. Met: *seen*. Not met: *not seen*, with the best week's count. No post by
  2027-01-01 still leaves the counter counting; the verdict says how many posts were made.
- **Counted, not barred:** each week's visitors, whether a post went out, and its reactions as
  LinkedIn shows them on the Monday the row is written. *Amended 2026-11-17:* reactions are the
  one count LinkedIn shows beside the post's reaction icons; comments and reposts are not in it.
- **Expected outcome, written first:** *not seen*. A guess from a network of a few hundred, a few
  in a hundred clicking a link: the best week 30 to 50 unique visitors, the week of the first
  post; then 10 to 20 a week. A weekly post of mostly silent rows gives little reason to come back.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The counter~~ **done** 2026-11-17. The counter: the owner creates the Umami Cloud site, gives its website ID (public) ~~and an API key (a secret, kept in `.env` as `FT_UMAMI_API_KEY`)~~; the tag goes into the template. *Amended 2026-11-17:* the share link's code instead of the key; the tag is the one in Technical details, its address and ID as Umami gives them for the site (built 2026-11-17; the look waits for the published page) | A test finds one Umami tag in the written page, with the ID, `data-do-not-track` and `data-domains`. *Amended 2026-11-17:* read by pageviews as well as visitors, since a browser already counted that month stays one visitor whatever it does. The published page, opened from a browser without the flag, adds one visitor and one pageview; opened from the same browser with the flag, and from a file on disk, adds no pageview; the browser's cookies after the visit hold none from Umami. Each look's time and counts, and the date, are written here |
| 2 | ~~`fortuneteller weekly-post`~~ **done** 2026-11-15 | Tests: a week with a graded call prints it as *right* or *wrong*; a pending call says *pending*; a week with none says *no call this week*; the record counts the calls' grades (*amended:* not `score`'s counts, which include rows leaning *too few*); a week across a month's first is asked in two parts and the larger kept; the last line is the disclaimer |
| 3 | The first post, after step 22's page is published | Its date and address are in the weeks file's row for its week, written the next Monday with the count |
| 4 | Every Monday to 2027-02-01: the week's row, and the next post | A row for each week of the window; on 2027-02-01, the verdict here against the bar |

**Step 1's look, 2026-11-17.** The tag reached the published page at 13:08 EET (PR #327, ahead
of the evening job). The owner's browser, flagged before the tag was live, opened the page, then a
private window of the same browser did. Umami's stats for 2026-11-17 from 00:00 UTC, read through
the share link at 13:56 EET: 1 visitor, 1 pageview, the visit at 11:55:46 UTC, Chrome on Linux;
the flagged visit added nothing. At 14:00 EET the private window showed no cookie for
diykorey.github.io, and a copy of the page saved and opened from disk left the count at 1 pageview.
Step 1 is done.

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
- **API:** Umami Cloud's website stats for `startAt` and `endAt` in milliseconds UTC; the reply's
  visitors. *Amended 2026-11-17:* the site is in Umami's EU region, `cloud.umami.is/analytics/eu/api`;
  `share/{code}` answers the site and a token, and the stats are asked with it in the
  `x-umami-share-token` header and `x-umami-share-context: 1`, as Umami's share page does. The
  code is `UMAMI_SHARE` in `__main__.py`; no secret. A failed ask prints the draft, then the error.
- **Command:** `weekly-post` in `__main__.py`, reading `study.read_calls`; it writes nothing. The
  owner or the session adds the week's row to the weeks file. Tests in `tests/test_scoreboard.py`.
- **File:** `docs/steps/be-seen-weeks.csv`: `week_start, unique_visitors, crosses_month, posted,
  post_date, post_url, reactions`. *Amended 2026-11-17:* `week_start` and `post_date` are
  `YYYY-MM-DD`, the week's Monday in UTC; `crosses_month` and `posted` are `yes` or `no`; a field
  with nothing to say is empty.
- **Docs:** this spec; the glossary (*unique visitor*, *Umami*, *disabled flag*, *seen*); the
  [scoreboard spec](scoreboard.md)'s "no per-visitor state", amended to say the page keeps none
  itself and Umami counts visits; `docs/status.md`, the changelog and roadmap row 23.
