# News as a feed, part 1: the president's trade posts

> Step 11 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-03 after
> [summits](summits.md) closed step 10. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when the US president posts about tariffs or trade, do markets move more than
on an ordinary day, and is the move still there a week later?

The roadmap asks this of GDELT, to decide whether a news feed is worth building on. **Measured
first, 2026-11-03, GDELT cannot date these events honestly:**

- **Coverage follows the market.** The article search for the president and tariffs, on
  2019-05-05, a Sunday with his tariff tweet at 12:08 New York, matched 0.22% of all articles; on
  Friday 0.11%, on Monday, the market's reaction day, 1.03%. Days picked by coverage are picked
  partly by the move they would be tested on. The search starts in 2017 (a start in 2015 or 2016
  is refused) and allows about one request a minute.
- **No speaker.** The event files code the president as `GOV/PRESIDENT` with no country, the code
  of any country's president (export file of 2019-05-05 17:00 UTC); the article search has none.
- **No trade topic.** No CAMEO event code is about trade; the GKG's trade themes
  (`EPU_CATS_TRADE_POLICY`, `ECON_TRADE_DISPUTE`) tag articles, not who spoke.

What has a date, a time and the president as the speaker is his own posts. So this part measures
them; GDELT is not used. Part 2, his second term, waits for a committed record of those posts.

At the end: the days the president tweeted about trade in his first term, as one lesser flow, from
a seed file built by a committed script. It gets rung 1's test on the day and over the week.

## The events

- **Source, frozen:** the Trump Twitter Archive's full dump (56,571 tweets to the 2021-01-08 ban;
  `drive.usercontent.google.com/download?id=16wm-2NTKohhcA26w-kaWfhLIGwl_oX95&export=download&confirm=t`,
  md5 `073b99bfa3fc75a7757ac6edf5d0f767`, fetched 2026-11-03; fields `date`, naive UTC, `text`,
  `isRetweet` `t`/`f`), read once by `scripts/presidential_posts.py`; nothing is read at run time.
- **The rule, fixed before any price is looked at:** a tweet with `isRetweet` `f`, its text, unescaped and stripped of links, not
  starting `RT @`, `"` or `“`, deleted ones kept, posted at or after 2017-01-20 12:00
  New York through the archive's last tweet, whose text, HTML entities unescaped and links removed,
  matches `\btariff|\btrade[\s-]+war|\btrade[\s-]+deal` ignoring case. Only @realDonaldTrump is
  archived; @POTUS is not.
  A tweet *names a rate* if `\d\s*(%|percent)` matches within 60 characters either side of
  `tariff`, full stops included.
- **The day:** each New York calendar day with a matching tweet is one event, at its first
  matching tweet's New York time truncated to the minute, never rounded; each market reacts on its
  first close after it. A Saturday, a Sunday and a
  Monday-morning tweet are three events with one reaction day. Counted by the research on weekdays:
  about 169 reaction days, 16% of the term's; step 1 recounts both the seed's days and the S&P
  500's reaction days on the real calendar.
- **Ordinary days end with the term.** A new field, `DatedShockFlow.ordinary_until`, stops the
  flow's ordinary days at 2021-01-08, so the comparison stays inside the first term: no Biden
  year, no second-term post day counted as ordinary, no drift as prices keep loading.
- **Out:** Obama and Biden (no free archive with times); his second term (part 2); the text
  itself, which neither archive licenses: the seed keeps days, times and counts.
- **Stored as not scheduled.** Live detection of a post is rung 7.
- **Origin:** a new seed event type `Presidential post`, tier 4, polarity `both` (the tariff flow
  holds `Tariff / trade-war / sanctions` with `United States`, and a flow's pair must be unique);
  country `United States`.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, *too few* under
  ten days a cell. **Lesser:** each day stays ordinary for every other flow; the flow keeps its
  lone reaction days. Every existing scoreboard entry stays identical. No surprise, no call.
- **And over a week:** `raw-move --week`. Post days fall on one day in six, so many ordinary
  windows hold one: a week null is weak evidence. The last windows, from 2021-01-05, reach past
  the term; accepted.
- **Families:** a family *moves* if most of it does: three of the four European indices, both
  yields.
- **Three checks, not verdicts, outside the chance count, each with its expectation:**
  1. *The day before* each reaction day, as a placebo, leaving out days that are themselves
     reaction days: for each market whose day *moves*, the placebo ratio stays under 1.05. Above
     it, the posts cluster in loud weeks rather than move markets.
  2. *Outside the session:* only days whose first matching tweet came before 09:30 or from 16:00
     New York, or on a day New York is shut, on the S&P 500, the Nasdaq and VIX: each keeps a
     ratio above 1.10. Round-the-clock markets are not checked.
  3. *Naming a rate:* only days with a rate-naming tweet, at that tweet's time: a higher ratio
     than the full flow on at least four of the six US markets (both indices, VIX, both yields,
     the dollar).
- **Two counts in step 1, with a threshold:** the reaction days of later tweets the first-tweet
  rule drops, and the days shared with a tariff signing (on the signing's calendar day or its
  reaction day). If either exceeds 10% of the S&P 500's reaction days, a fourth check reruns the
  test with them out of the ordinary days.
- **Chance, counted:** 16 cells on the day, 0.16 *moves* by chance; over a week a lower bound.
- **Expected outcome, written down first, cell by cell, on the day:** *moves*: the S&P 500, the
  Nasdaq, VIX; *unclear*: the DAX, the Euro Stoxx 50, the STOXX 600, the dollar, the euro, Brent;
  *doesn't*: the FTSE 100, both yields, gold, defence, energy, bitcoin. Over a week: nothing
  *moves*. Graded cell by cell: met where the verdict matches, near where *unclear* stands for
  *moves* or *doesn't*, missed where *moves* and *doesn't* swap.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The script, the seed file, `ordinary_until`, the flow stored; each market's lone days, the days shared with a tariff signing and the later tweets the first-tweet rule drops counted~~ **done** | A test's seed rows (`2018-03-02,07:50,…` and `2019-05-04,13:00,…`) store events `2420180302` and `2420190504`, not scheduled, the first reacting that day on the S&P 500, the second on Monday 05-06 and on bitcoin that Saturday; a test of `ordinary_until` drops a later ordinary day; the seed test checks the header, days in order inside the term, the times, counts ≥ 1; every existing scoreboard entry identical on a copy of the store |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts, the three checks, against the expected outcome |

*Step 1, 2026-11-03:* the rule finds 265 tweets on 179 New York days, 2017-02-03 to 2020-11-21,
28 of them with a rate-naming tweet; on the S&P 500 they are 146 reaction days. On a copy of the
store every existing scoreboard entry is identical, and so are the calls and *missed*; the flow
adds 16 cells to the chance line (312 → 328). The build takes 14 minutes. Lone days by market:
103 on the S&P 500, the Nasdaq, gold, the DAX, the Euro Stoxx 50, the STOXX 600, Brent, defence
and energy, 104 on both yields, the dollar and VIX, 102 on the euro, 107 on the FTSE 100, 112 on
bitcoin; none *too few*. Left out as shared on the S&P 500: 51 tweet days, by lead flow ISM 16,
core PCE 9, retail sales 9, CPI 7, the euro-area flash 5, a jobs report 5, GDP 3, the ECB 2, the
Fed 1. The two counts: later tweets the first-tweet rule drops add 7 reaction days (5%); 2 (1%)
share a day with a tariff signing; both under 10%, so no fourth check.

## Technical details

`scripts/presidential_posts.py` reads the dump and writes `data/seed/presidential_posts.csv`:
`day,time,posts,rate_time`, one row per day in date order, `time` the first matching tweet in New
York time, `posts` the day's matching tweets, `rate_time` the first rate-naming one (empty if
none). `flows.POSTS_FLOW`: `DatedShockFlow` with event type constant `POST_EVENT_TYPE =
"Presidential post"`, country `United States`, zone `NEW_YORK`, type code 24, CLI name `posts`,
label `PST`, noun `tweet days`, day column `day`, time column `time`, detail column `posts`,
`scheduled=False`, `ordinary_until=date(2021, 1, 8)`; `quality` stays `hand_written`, the
schema saying this seed is built by a script from a hand-pinned dump. `study.measure_raw_moves` skips a dated
flow's days after its `ordinary_until`. The checks run as one-off scripts.

Tests in `tests/test_study_raw_move.py`, `tests/test_seed_data.py` (with the file in the expected
set) and `tests/test_study.py`'s load-releases test. Seed rows: `Presidential post,4,both` in `data/seed/event_types.csv`. Docs: `docs/schema.md`
(code 24, the type in the event-type paragraph and `event_type`, `event_ts`, `detail`,
`scheduled`, `quality`), `docs/precision.md` (the first-tweet time, the
keyword rule, GDELT's limits), `docs/legacy/data/README.md` (the file and the event-type row), `docs/status.md`.

## What this does not do

No text at run time, no sentiment or direction, no live feed, no GDELT data, no other speaker or
topic, no second term.
