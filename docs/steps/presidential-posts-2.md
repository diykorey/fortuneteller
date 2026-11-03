# News as a feed, part 2: the president's trade posts, second term

> Step 11 of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1](presidential-posts.md), chosen 2026-11-03. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** part 1 found no market *moves* on a first-term trade tweet. Does that hold
for his Truth Social posts since 2025-01-20, the term in which tariffs were announced in posts?

**What closes step 11, written first.** A news feed is worth building on only if one of the three
US markets (the S&P 500, the Nasdaq, VIX) *moves* on the day and reaches the last row of the
readings below. A lone *moves* elsewhere, at 0.16 expected by chance, is not enough. Otherwise step
11 closes with no, and rung 7 waits for another reason.

Part 1 left this part waiting for a committed record of the posts. *Decided 2026-11-03:* the record
is the seed file this part commits, built by a committed script from one frozen snapshot of CNN's
archive. Its md5 is recorded below. The copy holds full post text, so it is not committed; it is
kept on the maintainer's machine, and only there can the md5 be checked. A later fetch will not
match the md5. Filtered at the cutoff, it is expected to rebuild the same seed, and step 1 records
the difference.

## The events

- **Source, frozen:** CNN's Truth Social archive, `ix.cnn.io/data/truth-social/truth_archive.json`.
  - 37,808 posts, 2022-02-14 to 2026-11-03 03:16 UTC.
  - md5 `6488dfe42b9bc97142bb508a7d1cab22`, fetched 2026-11-03.
  - Fields: `created_at`, ISO UTC ending in `Z`; `content`, plain text.
  - Posts deleted before the fetch are missing, while part 1 kept deleted tweets.
- **The rule is part 1's topic regex and rate rule.** The post's text is
  `LINK.sub("", html.unescape(content)).strip()`. A post is out if its text is empty (link- or
  image-only) or starts with `RT @`, `RT:`, `"` or `“`. Its time is `created_at` converted to New
  York time. It is in if 2025-01-20 12:00 ≤ time < 2026-10-31 00:00, both New York time.
  - The research count is 322 posts on 220 New York days, 174 of them weekdays; step 1 records the
    seed's actual count.
  - Step 1 also counts the empty-text posts in the window. Image-only announcements, such as the
    July 2025 letters, are missed.
- **The day:** as in part 1, each New York day is one event at its first matching post's minute.
- **Density and ordinary days:**
  - Posts fall on about 37% of the term's weekdays, against 16% in part 1.
  - The window has about 445 trading days. About 190 are post reaction days, and about 105 more are
    taken by a major release.
  - That leaves about **150 ordinary days** and about 125 lone post days on the S&P 500. Under 100
    ordinary days, a market's verdict is reported as context only.
- **Ordinary days** run from the flow's first reaction day to `ordinary_until` 2026-10-30. A post
  after Friday's close reacts on Monday 11-02 and falls out; this is accepted.
- **Shared days, a calendar estimate:**
  - 63 post days fall on a major release (a jobs report 13, CPI 11, core PCE 9, the euro-area flash
    9, retail sales 5, the Fed 5, the ECB 5, ISM 4, GDP 2). They are dropped as not lone.
  - 22 fall on a tariff signing (`data/seed/tariffs.csv` runs to 2026-10-23) and are kept.
  - So the flow measures posts on days with no major release, announcement days included.
- **Origin:** a new event type `Presidential post (second term)`, because a flow's (type, country)
  pair must be unique. Country `United States`, type code 25, not scheduled.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged,** on all sixteen markets, with part 1's families. The flow is lesser,
  so every existing scoreboard entry stays identical. No surprise, no call.
- **Chance:** 16 more cells on the day, less any *too few* or context-only cell; at most 328 → 344.
- **The week is context, not graded.** Step 1 counts the share of ordinary week windows that hold a
  post reaction day. With posts on about 40% of closes, it is near nine in ten.
- **Four checks, not verdicts, outside the chance count.**
  - Each runs as a one-off script on all sixteen markets.
  - Each is graded on the S&P 500, the Nasdaq and VIX, plus any market that *moves*.
  - A cell is met where the expectation holds and missed where it does not; there is no near.
  1. **The day before** each reaction day, itself no reaction day, as in part 1.
     - Expected: at or above 1.05 on the S&P 500 and VIX, as in part 1 (1.47 and 1.42).
     - At 37% density this day is often the day after another post, and step 1 counts it per
       market. Under ten days, the cell is not graded.
  2. **Without tariff signings:** a post day leaves the event days if its calendar day is a
     signing's day, or its reaction day is a signing's reaction day. Every signing reaction day
     also leaves the ordinary days.
     - Expected: under 1.10 on at least two of the three US markets.
  3. **Without April 2025:** that month's reaction days leave both sides.
     - Expected: under 1.10 on at least two of the three US markets.
  4. **Outside the session:** days whose first post came before 09:30 or from 16:00 New York, or on
     a day New York is shut; the three US markets only.
     - Expected: each keeps a ratio of at least 1.10, as in part 1, where the Nasdaq missed.
  - Naming a rate is dropped: part 1 found nothing. The seed keeps `rate_time`.
- **Readings, written first, for a market that *moves*:** an ordered decision, in which the first
  row that applies wins.

  | # | Outcome | Reading |
  | --- | --- | --- |
  | 1 | Under 1.10 in check 2 | The signings carry it |
  | 2 | Under 1.10 in check 3 | April 2025 carries it |
  | 3 | Placebo at or above 1.05 | Clustering not excluded |
  | 4 | Under 1.10 in check 4 (US markets) | Reverse timing not excluded |
  | 5 | None of the above | The posts move it: step 11's yes |

- **Expected outcome, written first, cell by cell, on the day:**
  - *moves*: the S&P 500, the Nasdaq and VIX, because announcements are inside;
  - *unclear*: the DAX, the Euro Stoxx 50, the STOXX 600, the dollar and Brent;
  - also *unclear*, both yields: in April 2025 they sold off with stocks;
  - *doesn't*: the FTSE 100, gold, defence, energy and bitcoin;
  - also *doesn't*, the euro: it was 0.81 in part 1.

  It is graded as in part 1: met, near or missed. Step 11's verdict, expected: no, because check
  2's expectation is that the signings carry the move.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The script reads either archive; the second seed and flow are stored. Counted on the real calendar: posts, days, empty-text posts, lone and ordinary days per market, placebo days, the two kinds of shared day on the S&P 500 by reaction day, later posts the first-post rule drops, and the week windows holding a post~~ **done** | Tests below pass; part 1's seed is rebuilt byte-identical from its dump; a fetch on step 1's day, cut at 2026-10-31, rebuilds the seed with its difference recorded; every existing scoreboard entry is identical on a copy of the store |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts, the four checks, the reading and step 11's answer, against the expected outcome |

*Step 1, 2026-11-03:*
- **The seed:** the rule finds 322 posts on 220 New York days, 2025-01-22 to 2026-10-19, 174 of
  them weekdays. 55 days hold a rate-naming post.
- **The rebuilds:** part 1's seed comes out byte-identical. A fetch the same day (37,811 posts, md5
  `2694f9affa742b77ddf94d8199e418d0`), cut at the window, rebuilds the seed with no difference.
- **Empty text:** 4,923 posts in the window have no text once links are removed.
- **The scoreboard:** on a copy of the store every existing entry is identical; the flow adds 16
  cells to the chance line (328 → 344).
- **On the S&P 500:**
  - 179 reaction days.
  - 57 shared with a major flow: a jobs report 10, CPI 9, core PCE 9, the euro-area flash 9, ISM 8,
    the ECB 5, retail sales 4, the Fed 2, GDP 1.
  - 122 lone, 14 of them (11%) shared with a tariff signing.
  - Later posts the first-post rule drops add 8 reaction days (4%).
- **Lone and ordinary days by market:**
  - 122 and 192 on the S&P 500, the Nasdaq, both yields, defence and energy;
  - 123 and 192 on the dollar; 122 and 194 on VIX; 121 and 194 on Brent; 121 and 204 on the euro;
  - 115 and 204 on gold; 115 and 209 on the DAX; 113 and 206 on the Euro Stoxx 50 and the STOXX
    600; 112 and 209 on the FTSE 100; 124 and 206 on bitcoin.
  - None under 100 ordinary days, none *too few*.
- **Placebo days:** 47 to 49 a market, 58 on bitcoin.
- **Week windows:** 80% to 83% of ordinary week windows hold a post reaction day.

## Technical details

- **The script.** `scripts/presidential_posts.py <dump>` reads one archive per run and picks the
  reader by its fields:
  - `isRetweet`: the existing `matching_tweets`, unchanged, writing `presidential_posts.csv`;
  - `created_at`: a new `matching_truth_posts(dump: list[dict[str, str]]) -> list[tuple[datetime,
    bool]]`, writing `presidential_posts_2.csv`.

  Both seeds have the same columns, `day,time,posts,rate_time`.
- **The flow.** `flows.POST_2_EVENT_TYPE = "Presidential post (second term)"`, and
  `flows.POSTS_2_FLOW = DatedShockFlow(POST_2_EVENT_TYPE, UNITED_STATES, NEW_YORK, 25, "posts2",
  "PS2", seed_file="presidential_posts_2.csv", noun="post days", day_column="day",
  detail_column="posts", time_column="time", scheduled=False, ordinary_until=date(2026, 10, 30))`,
  after `POSTS_FLOW` in `EVENT_FLOWS`.
- **Seed row:** `Presidential post (second term),4,both` in `data/seed/event_types.csv`.
- **Tests:**
  - a new `tests/test_presidential_posts_script.py`, which loads the script with
    `importlib.util.spec_from_file_location`. A `RT: …` post, one starting `“` and a link-only post
    are out; a 2025-04-09 tariff post is in, at its New York minute.
  - `tests/test_seed_data.py`: the new file in the expected set, plus a seed test (header; days
    sorted, unique and inside the window; times; `posts` ≥ 1).
  - `tests/test_study.py`: the load-releases fixture, a new report line, the count 36 → 37.
  - `tests/test_study_raw_move.py`: a load test, with event id `2520250409`, not scheduled.
- **Docs:**
  - `docs/schema.md`: code 25, the event-type paragraph, `event_type`, `event_ts`, `detail` and the
    source;
  - `docs/precision.md`: the snapshot, the missing deleted posts, the image-only posts, the
    first-post time, the week windows past 2026-10-30;
  - `docs/legacy/data/README.md`: the file and the event-type row;
  - `docs/glossary.md` and `docs/status.md`.

## What this does not do

No text kept, no sentiment or direction, no live feed, no other account (X, the White House), no
change to part 1.
