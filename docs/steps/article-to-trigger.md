# News into triggers, part 2: a pasted article read into a trigger

> Step 20, part 2, of the [Roadmap](../roadmap.md#next-steps-in-order). Part 1,
> [a CEO's conduct in question](ceo-scandals.md), measured the kind; this part reads it out of a
> text. Terms are in the [Glossary](../glossary.md): *trigger*, *kind*, *dev set*, *test set*.

## The goal

**In plain words:** the owner pastes an article and the tool says whether it reports a kind of
event already measured. If it does, the tool prints the trigger row the owner could file and the
answer part 1 gives. If it does not, it says *not a measured kind*.

At the end, `fortuneteller read-article FILE` prints either
`trigger: ceo,<day>,scandal,<ticker>` with `follows --event ceo`'s answers, or
`not a measured kind`. It files nothing: filing stays the owner's call
([trigger file](trigger-file.md)). Part 3, a feed, needs this to read correctly first.

## The way to reach it

- **Rules first, no model.** A text is the kind when it names a chief executive leaving and ties
  the departure to the executive's own conduct, as part 1's coding rule reads the dataset's notes.
  The rules are word lists and patterns in one function, written on the dev set only.
- **The test set nobody picks.** Part 1's dataset already says which departures are the kind:
  - Positives: the 26 kept events, each read from the source its seed row cites.
  - Negatives, by a rule fixed here: the 179 departures coded *legal* that are not the CEO's own
    conduct (fraud at the company, antitrust), and 100 departures drawn with seed 20261114 from the
    dataset's other codes that give a reason (died, ill, dismissed for performance, retired, a new
    job), each read from the first source the dataset lists.
  - A row whose source cannot be fetched, or holds no text, is left out and counted.
- **The split, fixed here:** the positives and the negatives each in order of their announced day
  (ties by `dismissal_dataset_id`), alternately dev and test, the first to dev: 13 positives each.
  The rules are frozen by a commit before the test set's texts are read once;
  that commit's hash is recorded here.
- **The obstacle: the genre.** Most sources are filings and press releases (an 8-K, its
  exhibit 99), not the news an owner pastes. What this measures holds for that genre only; a news
  article is a later check, said so in the results.
- **The ticker comes from the text:** `(NYSE: BA)`, `(Nasdaq: NVDA)`, `NYSE:BA`. No table from
  names to tickers. A text with none prints the row with an empty ticker and says so.
- **The day** is the first date the text gives as its own (a dateline, or an 8-K's date of
  report). It is graded against the seed row's day.
- **Nvidia is not the kind.** Its CEO has not left; part 1's events are all departures. A rule that
  reads the kind correctly says *not a measured kind* to the 2026-11-08 article. Whether conduct
  without a departure becomes a kind is the owner's question, not this part's.

## The rule, fixed before any text is read

- **Reads:** on the test set, the kind on at least 10 of its positives in 13, with the ticker and
  the day right on each it reads; and the kind on at most 1 in 20 of its negatives (5%). Both, or
  *doesn't read*. With fewer than 10 test positives fetched, *too few*.
- Nothing is tuned after the test set is read. A changed rule is a new frozen commit and a new test
  set, with a dated amendment.
- **Expected outcome, written first:**
  - The positives pass: departures for conduct say so ("violated the code of conduct", "a
    consensual relationship"), about 11 of 13 read.
  - The negatives fail the 5% bar: the company-fraud departures are the look-alikes, worded in the
    same legal terms; about 8% read as the kind.
  - The ticker is missing in about a third of the texts read: 8-Ks seldom print it.
  - The 2026-11-08 Nvidia article: *not a measured kind*.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The sets: each row's source fetched by the rule above, its text extracted; `docs/steps/article-to-trigger-set.csv` lists id, source, split, expected kind, ticker and day, and each text's hash | Every row of the rule is listed or counted out by reason; no text is committed |
| 2 | The rules on the dev set, frozen by a commit whose hash is written here | Tests: a conduct departure reads; a fraud departure and a retirement do not; a text with `(NYSE: BA)` gives `BA` |
| 3 | The test set read once; `read-article` | Results here, each verdict against the bars above |

## How you know it is right

- A text that names a CEO leaving for "personal reasons", and nothing else, is not the kind.
- A text about a company's fraud that names its CEO is not the kind unless it ties the departure to
  the CEO's own conduct.
- The dev and test sets share no row; a test text's hash is unchanged between step 1 and step 3.
- Run on the same file twice, `read-article` prints the same line.

## What this part does not do

No model and no feed (part 3). No kind but `ceo`. No news article in the test set, and no filing of
triggers. No conduct without a departure (Nvidia's case) unless the owner adds it with a dated
amendment.

## Technical details

- **Sources:** the dataset's `sources` and `eight_ks` columns, release of 2025-11-26
  (doi:10.5281/zenodo.23328926). SEC's EDGAR asks automated clients for a contact `User-Agent`; a
  generic one is used, and if EDGAR refuses it, step 1 stops and says so. Downloads go to their own
  directory under `data/cache/`, read with Python's isolated mode.
- **Code:** `read_article(text) -> Reading | None` in `study.py`, beside `follow_ceo`; the command
  in `__main__.py`. Tests in `tests/test_ceo_scandals.py`.
- **Docs:** this spec, the glossary (*dev set*, *test set*), `docs/status.md`, the changelog and
  roadmap row 20.
