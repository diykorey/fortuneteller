# News into triggers, part 2: a pasted article read into a trigger

> Step 20, part 2, of the [Roadmap](../roadmap.md#next-steps-in-order). Part 1,
> [a CEO's conduct in question](ceo-scandals.md), measured the kind; this part reads it out of a
> text. Terms are in the [Glossary](../glossary.md): *trigger*, *kind*, *dev set*, *test set*.

## The goal

**In plain words:** the owner pastes an article and the tool says whether it reports a kind of
event already measured. If it does, the tool prints the trigger row the owner could file and the
answer part 1 gives. If it reports a CEO's conduct coming out while the CEO stays, the second kind
the owner chose (Nvidia's case), it says so, with no trigger until that kind is measured. Otherwise
it says *not a measured kind*.

At the end, `fortuneteller read-article FILE` prints either
`trigger: ceo,<day>,scandal,<ticker>` with the answers a trigger on that day would get (part 1's
spans from the reaction close, from the events whose spans ended by then, as `triggers` answers
them), `a CEO's conduct, no departure: not measured yet`, or `not a measured kind`. It files
nothing: filing stays the owner's call
([trigger file](trigger-file.md)). Part 3, a feed, needs this to read correctly first.

## The way to reach it

- **Rules first, no model.** A text is the kind when it names a chief executive leaving and ties
  the departure to the executive's own conduct, as part 1's coding rule reads the dataset's notes.
  The rules are word lists and patterns in one function, written on the dev set only.
- **The test set nobody picks.** Part 1's dataset already says which departures are the kind.
  Every row, positive or negative, is read from the same place: the first address in the
  dataset's `sources` column, else in its `eight_ks` column, the departure as the dataset found
  it. Its expected day is the row's `date_departure_announced`.
  - Positives: the 26 events part 1 kept. (Part 1 dated five of them from an earlier report of the
    conduct; that report is not used here, because it may not name a departure.)
  - Negatives: the 179 departures coded 4 (*legal violations or concerns*) that part 1 found were
    not the CEO's own conduct, and 100 drawn from the departures with codes 1 (*death*), 2
    (*illness*), 3 (*job performance*), 5 (*retirement*) and 6 (*new opportunity*) that have an
    address: in order of `dismissal_dataset_id`, `random.Random(20261114).sample(pool, 100)`.
- **The split, fixed here, before anything is fetched:** the positives and the negatives each in
  order of `date_departure_announced` (ties by `dismissal_dataset_id`), alternately dev and test,
  the first to dev: 13 positives each, 140 negatives in the dev set and 139 in the test set.
- **The test texts are fetched only after the rules are frozen.** Step 1 fetches the dev set alone
  and lists the test set's addresses. The frozen commit's hash is written here before step 3
  fetches a test text.
- **A text** is the page's words after the markup is stripped. One under 100 words (an index
  page, a paywall, a scan) is counted out as *no text*, as is one that cannot be fetched.
- **The obstacle: the genre.** The sources are mostly filings (an 8-K and its exhibit 99) and press
  releases, not the news an owner pastes. What this measures holds for that genre only; the
  results say so, and the one news text checked is the 2026-11-08 Nvidia article.
- **The ticker comes from the text:** `(NYSE: BA)`, `(Nasdaq: NVDA)`, `NYSE:BA`. There is no
  table from names to tickers. A text with none prints an empty ticker, and the owner fills it.
- **The day** is the first date the text gives as its own (a dateline, an 8-K's date of report).
  Word out at or after 16:00 New York is filed under the next trading day
  ([trigger file](trigger-file.md)); when the text gives a time, the printed day follows that
  rule, and when it gives none, the line says *time not given: check it*.
- **Two kinds, one measured.** *Amended 2026-11-14, by the owner:* both a departure for the CEO's
  conduct (`ceo`, measured in part 1) and the CEO's conduct coming out with no departure are kinds
  ([decisions](../decisions.md#2026-11-14-a-ceos-conduct-without-a-departure-is-a-kind-too-by-the-owner)).
  The second has no history yet: a text read as it prints *not measured yet* and no trigger until
  [part 1b](../roadmap.md#next-steps-in-order) measures it. The departure is read first: a text
  naming the departure is never the second kind. Nvidia's 2026-11-08 article is the second kind:
  its CEO has not left.

## The rule, fixed before any text is read

- **The kind:** read on at least 75% of the test positives with a text (at least 10 of 13 if all
  13 have one), and on at most 5% of the test negatives with a text. Both: *reads*; else *doesn't
  read*. With fewer than 10 test positives with a text: *too few texts*.
- **The second kind** has no test set: the dataset holds departures only. Its reading is reported,
  not barred: on the Nvidia article, and how many dev and test texts it fires on (a text naming a
  departure must not). Every dataset text is a departure, so a second-kind reading on one is a
  departure the rules missed: on a positive it is not *read*, on a negative it is not counted
  toward the 5% bar but reported beside it. Its bars come with part 1b's history.
- **The ticker and the day** are reported on the positives read, not barred: a ticker right, empty
  or wrong; a day right or not, right being `date_departure_announced`, or the trading day after it
  (the NYSE calendar) when the text gives a time at or after 16:00 New York. A wrong ticker on any positive is
  said plainly: it would file a trigger on the wrong company.
- Nothing is tuned after the test set is read. A changed rule needs a new test set, and none is
  left in the dataset: it would be news texts the owner labels before they are read, with a dated
  amendment.
- **Expected outcome, written first.** The verdict is the expectation; the numbers are a guess
  beside it, not a bar:
  - *Doesn't read*, on the negatives. The positives pass, about 11 of 13: departures for conduct
    say so ("violated the code of conduct", "a consensual relationship"). The negatives miss the
    5% bar, about 8%: the company-fraud departures are worded in the same legal terms.
  - The ticker empty in about a third of the positives read, and never wrong; the day right on
    most.
  - *Amended 2026-11-14, before anything is fetched:* the 2026-11-08 Nvidia article: *a CEO's conduct, no departure: not measured yet*, ticker
    `NVDA`.
  - The second kind fires on none of the positives, which all name a departure, and on a few
    negatives, about 3%: departures whose texts say the conduct in words the departure rules
    miss.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The sets: every row listed in `docs/steps/article-to-trigger-set.csv` (id, address, split, expected kind, ticker where part 1 has one, day); the dev texts fetched and counted out by reason; the test texts not fetched | Every row the sets above name is listed; each fetch is a row in the committed `docs/steps/article-to-trigger-fetch.csv` (address, UTC time, words, reason if counted out); no text is committed |
| 2 | The rules on the dev set, and their dev counts written here; then frozen by a commit whose hash is written here | Tests: a conduct departure reads; conduct with no departure reads as the second kind; a fraud departure and a retirement do not; `(NYSE: BA)` gives `BA`; an after-close time moves the day. The dev counts (the kind on the dev positives and negatives, the second kind's count, the ticker and day counts) are recorded before the hash |
| 3 | The test texts fetched and read once; the Nvidia article read; `read-article` | Results here: the kind against both bars, the ticker and day counts, the second kind's count, and Nvidia's line |

## How you know it is right

- A text that names a CEO leaving for "personal reasons", and nothing else, is not the kind.
- A text about a company's fraud that names its CEO is not the kind unless it ties the departure to
  the CEO's own conduct.
- The dev and test sets share no row, and no test address has a row in the fetch log timed before
  the frozen commit.
- A text about an inquiry into the company in which its CEO stays, and nothing ties the CEO's own
  conduct to it, is neither kind.
- A press release stamped 16:05 New York prints the next trading day.
- `read-article` on an article dated before an event in the history answers without that event.

## What this part does not do

No model and no feed (part 3). No measured kind but `ceo`: the second kind is read, never answered,
until part 1b. No news article in the test set beyond Nvidia's, and no filing of triggers.

## Technical details

- **Sources:** the dataset's `sources` and `eight_ks` columns, release of 2025-11-26
  (doi:10.5281/zenodo.23328926). SEC's EDGAR asks automated clients for a contact `User-Agent`; a
  generic one is used, and if EDGAR refuses it, step 1 stops and says so. Downloads go to their own
  directory under `data/cache/`, read with Python's isolated mode.
- **The Nvidia article:** the text the owner pasted on 2026-11-13 (CNN, 2026-11-08), saved as
  `data/cache/articles/nvidia-2026-11-08.txt`, not committed.
- **Code:** `read_article(text) -> Reading | None` in `study.py`, beside `follow_ceo`, a `Reading`
  being the kind (`ceo` or the second), the day, the time if given, and the ticker; the command in `__main__.py`, answering through
  `answer_triggers`' path for `ceo`. Tests in `tests/test_ceo_scandals.py`.
- **Docs:** this spec, the glossary (*dev set*, *test set*, *8-K*, *EDGAR*, *reads*), `docs/status.md`, the changelog and
  roadmap row 20.
