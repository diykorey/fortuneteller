# News as a feed, part 2: the president's trade posts, second term

> Step 11 of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1](presidential-posts.md), chosen 2026-11-03. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** part 1 found that no market *moves* on a first-term trade tweet. Does that
hold for his Truth Social posts since 2025-01-20, the term in which tariffs were announced in
posts?

Part 1 left this part waiting for a committed record of the posts. *Decided 2026-11-03:* the record
is the seed file this part commits, built by a committed script from one frozen snapshot of CNN's
archive whose md5 is written below. The live archive grows every few minutes, so a new fetch will
not match the md5. It rebuilds the same seed unless a post before the cutoff has been deleted.

At the end: the second term's trade-post days as one lesser flow, apart from part 1's, tested on
the day and over the week inside the term.

## The events

- **Source, frozen:** CNN's Truth Social archive, `ix.cnn.io/data/truth-social/truth_archive.json`
  (37,808 posts, 2022-02-14 to 2026-11-03 03:16 UTC, md5 `6488dfe42b9bc97142bb508a7d1cab22`,
  fetched 2026-11-03; fields `created_at`, UTC ending `Z`, and `content`, plain text). It is read
  once by `scripts/presidential_posts.py`, which then writes both seeds; part 1's seed comes out
  byte-identical.
- **The rule is part 1's.** The topic regex, the rate rule, unescaping and link stripping are
  unchanged. Only the repost test is adapted: a post is out if its content starts `RT @` or `RT:`,
  or if its text starts `"` or `“`, or if it is empty once links are removed. The window runs from
  2025-01-20 12:00 New York up to, but not including, 2026-10-31 00:00. The research count is 322
  posts on 220 New York days, 174 of them weekdays.
- **The day:** as in part 1, each New York day is one event at its first matching post's minute.
- **Density.** About 37% of the term's weekdays hold a post, against about 16% in part 1. Ordinary
  days are correspondingly fewer: about 250, and step 1 gives the exact count.
- **Ordinary days:** from the flow's first reaction day to `ordinary_until` 2026-10-30.
- **Shared days.** Counted by the research on calendar days: 63 post days fall on a major flow's
  release (a jobs report 13, CPI 11, core PCE 9, the euro-area flash 9, retail sales 5, the Fed 5,
  the ECB 5, ISM 4, GDP 2). These are dropped as not lone, as always. A further 22 (10%) fall on a
  tariff signing and are kept. So this part measures posts on days with no major release, and it
  includes the announcement days.
- **Origin:** a new seed event type, `Presidential post, second term` (tier 4, `both`), because a
  flow's (type, country) pair must be unique. The country is `United States`, the type code 25, the
  CLI name `posts2`, the seed `data/seed/presidential_posts_2.csv` with part 1's columns. It is
  stored as not scheduled.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged**, on all sixteen markets, on the day and with `--week`. The flow is
  lesser and every existing scoreboard entry stays identical. There is no surprise and no call.
  With posts on one day in three, almost every ordinary week holds a post, so a week null is weak
  evidence.
- **Three checks, not verdicts, outside the chance count:**
  1. *The day before*, the placebo of part 1. For each market that *moves*, it stays under 1.05.
  2. *Without April 2025* (20 post days in the tariff crash): each market that *moves* keeps a
     ratio of at least 1.10.
  3. *Without tariff signings*, which leaves out post days sharing a signing's calendar day or
     reaction day. Each market that *moves* keeps a ratio of at least 1.10.
  Each year, 2025 and 2026, is also reported with its ratio only, with no p value and no verdict.
- **Chance:** 16 more cells on the day (328 → 344), 0.16 *moves* expected by chance.
- **Expected outcome, written first, cell by cell, on the day:**
  - *moves*: the S&P 500, the Nasdaq, VIX.
  - *unclear*: the DAX, the Euro Stoxx 50, the STOXX 600, both yields, the dollar, Brent.
  - *doesn't*: the FTSE 100, the euro, gold, defence, energy, bitcoin.
  - Over a week, nothing *moves*.
  - The checks: the placebo holds; without April 2025, the ratios fall below 1.10.
  - Graded as in part 1: met, near or missed.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The script reads both archives, the second seed, the flow stored; lone days, ordinary days and the two shared counts recounted on the real calendar | The script's test: a Truth post `RT: …` and one starting `“` are out, and a 2025-04-09 tariff post is in; a seed test checks the header, that days are in order inside the window and counts ≥ 1; part 1's seed is unchanged; every existing scoreboard entry is identical on a copy of the store |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts, the three checks and the years, against the expected outcome |
