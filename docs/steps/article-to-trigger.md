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
them), `a CEO's conduct, no departure: not measured yet` (*amended 2026-11-15:* followed by
the ticker, if the text gives one, as `(NVDA)`), or `not a measured kind`. It files
nothing: filing stays the owner's call
([trigger file](trigger-file.md)). Part 3, a feed, needs this to read correctly first.
*Amended 2026-11-15:* a *doesn't read* or *too few texts* is answered by a decisions entry before
part 3 starts; the roadmap's next try is a model on this machine, with its own test set.
*Added 2026-11-15:* the owner parked step 20 until the gate ([decisions](../decisions.md#2026-11-15-step-20-parked-until-the-gate-by-the-owner)).

## The way to reach it

- **Rules first, no model.** A text is the kind when it names a chief executive leaving and ties
  the departure to the executive's own conduct, as part 1's coding rule reads the dataset's notes.
  The rules are word lists and patterns in one function, written on the dev set only.
- **The test set nobody picks.** Part 1's dataset already says which departures are the kind.
  Every row, positive or negative, is read from the same place: the first address in the
  dataset's `sources` column, else in its `eight_ks` column, the departure as the dataset found
  it. Its expected day is the row's `date_departure_announced`.
  - *Amended 2026-11-15:* that first address does not always report the departure (a page on
    the CEO's death years later, a proxy statement, a profile page). Such a positive lowers the
    reading for a reason the rules do not cause; the rule stands, and the results name each test
    positive missed and whether its text reports the departure at all.
  - *Amended 2026-11-15, in step 1, before any text is fetched:* an address that is a library's
    login (`login?url=`, `idm.oclc.org`, `ezproxy`, `lp.hscl.`) cannot be fetched by anyone
    outside that library, so a row is read from its first address that is not one, else that
    login, which counts out. Two test positives and 26 negatives move to their next address; two
    negatives have only a login. And the dataset leaves `date_departure_announced` blank on 12 of
    the 26 positives and 198 of the negatives: a blank stays blank as the expected day, and the
    day is reported on the positives with one (6 dev, 8 test). The split's order uses
    `left_ceo_office` where the announcement is blank. The expected day can differ from part 1's
    seed day by design: part 1 took the first public word, here it is the departure.
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
  - *Amended 2026-11-15, in step 1, before any test address is fetched:* the fetch is
    `scripts/article_texts.py fetch`, the same for both sets. A first dev pass sent every site the
    contact `User-Agent` EDGAR asks for; most news sites refused it (HTTP 401 and 403), leaving 4 of
    the 13 dev positives with a text. So news sites get an ordinary browser's `User-Agent`, and an
    address that is counted out for any reason but a library login gets one more try: its first
    capture with status 200 in the Internet Archive's Wayback Machine, fetched raw. EDGAR and the
    archive get the contact `User-Agent`: the archive answers a browser's name from a script with
    HTTP 429 on every try. A 429 means *later*, not *no text*: a run asks again up to three times,
    and a row whose last answer is still 429 is fetched by the next run until it has another. The
    markup's `head`, scripts and styles are dropped with their contents. Every pass is in the fetch
    log, by its `via` column and time; the dev counts are each row's last answer. The method is
    changed this once: no other source of a text is sought, so a row is never read from a text
    someone looked for.
- **The obstacle: the genre.** The sources are mostly filings (an 8-K and its exhibit 99) and press
  releases, not the news an owner pastes. What this measures holds for that genre only; the
  results say so, and the one news text checked is the 2026-11-08 Nvidia article.
  - *Amended 2026-11-15, in step 1, by the addresses alone, before any rule:* the sources are
    mostly news. Of the 305 addresses, by their hosts (filings: `sec.gov`, `sec.report`; press
    releases: `businesswire`, `prnewswire`, `globenewswire`, a host starting `ir.` or holding
    `investor`, `newsroom` or `press`; reference: `wikipedia`, `fundinguniverse`, `macroaxis`,
    profile pages), 38 are filings (EDGAR or a mirror of it),
    29 press releases or investor pages, 7 reference pages (an encyclopedia, a company history)
    and 231 others, nearly all news sites. So the measure is nearer the news an owner pastes than feared,
    though most of the news is about the departure on its day, and some pages are written later.
- **The ticker comes from the text:** `(NYSE: BA)`, `(Nasdaq: NVDA)`, `NYSE:BA`. There is no
  table from names to tickers. A text with none prints an empty ticker, and the owner fills it.
- **The day** is the first date the text gives as its own (a dateline, an 8-K's date of report).
  Word out at or after 16:00 New York is filed under the next trading day; *amended
  2026-11-15:* that is part 1's rule ([CEO scandals](ceo-scandals.md), `first_reaction_day`), and
  a trading day is one with an S&P 500 close in the store, so a weekend or holiday dateline also
  moves to the next. When the text gives a time, the printed day follows that rule, and when it
  gives none, the line says *time not given: check it*.
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
  - *Amended 2026-11-15, before any rule is written:* so that doubtful texts cannot be sent to the
    second kind to pass, a negative read as either kind counts toward the 5% bar.
- **The ticker and the day** are reported on the positives read, not barred: a ticker right, empty
  or wrong; a day right or not (on the positives with one, *amended 2026-11-15*), right being `date_departure_announced`, or the trading day after it
  (a day with an S&P 500 close) when the text gives a time at or after 16:00 New York. A wrong ticker on any positive is
  said plainly: it would file a trigger on the wrong company. *Amended 2026-11-15:* a ticker is
  right when it is the set's or the one the company traded under on the text's day (Priceline's
  `PCLN`, now `BKNG`), checked by hand against the company's filings and said so.
- Nothing is tuned after the test set is read. A changed rule needs a new test set, and none is
  left in the dataset: it would be news texts the owner labels before they are read, with a dated
  amendment.
- **Expected outcome, written first.** The verdict is the expectation; the numbers are a guess
  beside it, not a bar:
  - *Doesn't read*, on the negatives. The positives pass, about 11 of 13: departures for conduct
    say so ("violated the code of conduct", "a consensual relationship"). The negatives miss the
    5% bar, about 8%: the company-fraud departures are worded in the same legal terms.
  - The ticker empty in about a third of the positives read, and never wrong; the day right on
    most (*amended 2026-11-15:* about 6 of the 8 test positives with a day, if all are read).
  - *Amended 2026-11-14, before anything is fetched:* the 2026-11-08 Nvidia article: *a CEO's conduct, no departure: not measured yet*, ticker
    `NVDA`.
  - The second kind fires on none of the positives, which all name a departure, and on a few
    negatives, about 3%: departures whose texts say the conduct in words the departure rules
    miss.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The sets: every row listed in `docs/steps/article-to-trigger-set.csv` (id, address, split, expected kind, ticker where part 1 has one, day); the dev texts fetched and counted out by reason; the test texts not fetched | Every row the sets above name is listed; each fetch is a row in the committed `docs/steps/article-to-trigger-fetch.csv` (address, UTC time, words, reason if counted out); no text is committed~~ **done** 2026-11-15, [below](#results) |
| 2 | ~~The rules on the dev set, and their dev counts written here; then frozen by a commit whose hash is written here (*amended 2026-11-15, rewritten the same day before the freeze from "`read_article` and every function it calls":* frozen means the block of `study.py` from the comment `# Step 20, part 2` to the end of `article_day`: `CONDUCT_NO_DEPARTURE`, the patterns and tables `_CHIEF`, `_LEAVES`, `_CONDUCT`, `_TICKER`, `_MONTHS`, `_DATE`, `_CLOCK`, `_ZONES`, `_HEDGE`, the reaches `_NEAR_*`, `Reading`, `_near`, `_departures`, `_own_day`, `read_article` and `article_day`, with the values they read from outside it, `STOCK.close` and `NEW_YORK`; and the scorer, `scripts/article_texts.py read`. At step 3's results the block is byte for byte the frozen commit's. The tests check the rules work as written; the dev counts are the measure) | Tests: a conduct departure reads; conduct with no departure reads as the second kind; a fraud departure and a retirement do not; `(NYSE: BA)` gives `BA`; an after-close time moves the day. The dev counts (the kind on the dev positives and negatives, the second kind's count, the ticker and day counts) are recorded before the hash~~ **done** 2026-11-15, [below](#results) |
| 3 | ~~The test texts fetched and read once; the Nvidia article read; `read-article` | Results here: the kind against both bars, the ticker and day counts, the second kind's count, and Nvidia's line~~ **done** 2026-11-15, [below](#results): *doesn't read* |

## Results

**Step 1, 2026-11-15.** `scripts/article_texts.py sets` lists the 305 rows, 13 positives and 140
negatives in the dev set, 13 and 139 in the test set; run again, it rewrites the file unchanged.
`scripts/article_texts.py fetch dev` fetched the dev texts in five passes, each in the log by
its time and `via` (`generic`: the contact `User-Agent` for every site; `browser`: a news site
asked as a browser; `archive`: the Wayback Machine; `none`: a library login, not asked). Pass 1
(08:45 UTC) was the first method; passes 2 (08:56) and 3 (09:09), over all 153 rows, were the
committed script before it resumed, and met the archive's 429; passes 4 (13:23, 29 rows) and 5
(16:13, 19 rows) resumed them, the last with the archive asked by the contact name. The test set
will be fetched by the committed script in full, then resumed. By each row's last answer, as
`scripts/article_texts.py count dev` prints it:

| Dev rows | With a text | Counted out |
| --- | --- | --- |
| 13 positives | 12 (4 from the page, 8 from the archive) | 1: the page gone and no capture (F5 Networks) |
| 140 negatives | 103 (69 from the page, 34 from the archive) | 37: 33 no capture, 2 under 100 words, 1 refused by the archive (HTTP 403), 1 a library login with no other address |

The texts are in `data/cache/articles/dev/`, not committed. The test texts are not fetched.
Row 3398 had a text in passes 1 and 2 and an HTTP 503 in pass 3, its last answer, so it is counted
out; the 34 rows with no capture were asked again by the contact name and still have none.

**Step 2, 2026-11-15.** The rules (the frozen block above) were written on the dev texts alone,
reading them by `scripts/article_texts.py read dev data/cache/articles/dev data/fortuneteller.duckdb`,
which prints:

- The kind: **9 of the 12 dev positives with a text** read as `ceo`, exactly 75%, no slack; **0 of
  the 103 dev negatives** read as either kind. The three not read: Interface's text is a page on
  CEO departures in general; Equinix's calls the resignation mysterious and gives no reason; Wynn's
  is a story from before he left, read as the second kind, rightly for its words.
- One read is on the wrong company: the Rambus row's text (eetimes) is about Texas Instruments'
  CEO, so it reads for a reason that is not Rambus's.
- The second kind: 1 positive (Wynn's) and 0 negatives.
- The ticker, on the 9 read: 1 right (TrueBlue's), 8 empty, 0 wrong.
- The day, on the 5 read with a set day: 4 right; Orthofix's text is dated the day after the
  departure, its only date.
- One guard was added from the spec's own risk, not from dev: a word of leaving after *called
  for*, *refuses*, *no plans to* and the like is not a departure, so a story about a CEO who stays
  is not read as one. Dev's counts did not move.

**The frozen commit: `fe7048d3f5106ca017647fbb764cc0aeb50e05b0`**, written here before any test address is fetched.

**Step 3, 2026-11-15: *doesn't read*.** The test texts were fetched once by
`scripts/article_texts.py fetch test`, the first at 17:29 UTC by the fetch log's `fetched_at`,
after the frozen commit (17:21 UTC by `git log -1 --format=%cI fe7048d`);
no row was left at the archive's rate limit. They were read once by
`scripts/article_texts.py read test data/cache/articles/test data/fortuneteller.duckdb`; its
output, the fetch counts and Nvidia's line are in [the evidence](article-to-trigger-test.txt).
The frozen block of `study.py` is byte for byte the frozen commit's. The 12 test positives with a
text are 8 news pages, 2 filings and 2 press releases by the hosts rule above; the 99 negatives 76,
15, 7 and 1 reference page. So this measures news and filings together, not news alone.

- **The kind, against the bars:** 5 of the 12 test positives with a text read as `ceo`, 42%
  against 75%; 6 of the 99 test negatives with a text read as either kind, 6.1% against 5% (5 as
  `ceo`, 1 as the second kind). Both bars missed: *doesn't read*. The expected verdict was right
  for the wrong half: the negatives were expected to miss, about 8%, but the positives were
  expected to pass, about 11 of 13.
- **The seven positives not read, and whether their text reports the departure:**
  - It does, with the conduct out of reach: Texas Instruments ("Crutcher resigned due to
    violations of the company's code of conduct", his surname with no title, so no departure is
    found there, and the one found is 400 characters from the conduct); Intel (the "consensual
    relationship" 780 characters after the departure found); Apollo ("steps down ... in wake of
    Epstein scandal", a scandal the word lists do not name); Red Robin ("ousted ... for misusing
    funds", a story of his death 13 years on, with words the lists do not name). The distances are
    the character offsets of the frozen patterns' matches in the text, measured by hand.
  - It does not say why: Visteon's story names no conduct.
  - It does not report the departure: HP's address is an 8-K of 2011 electing a director;
    McDonald's is its 2020 proxy statement, 48,342 words by the fetch log.
- **The six negatives read:** an employment agreement's "Termination" beside "Code of Conduct"
  (Manhattan Associates); a CEO stepping down beside a drug for "sexual" desire (Amag); a lawyer
  saying the CEO "did not engage in any intentional misconduct" (ACS, options backdating); a story
  naming other CEOs' scandals beside Restoration Hardware's (Hurd's "sexual harassment"); an
  activist's letter alleging conduct "inappropriate" (Tessera); and, as the second kind, a proxy
  statement's "Code of Ethics" beside its chief executive.
- **The second kind:** 0 positives, 1 negative (above).
- **The ticker, on the 5 read:** as the scorer prints it, 2 right (Stryker, Ingevity), 2 empty, 1
  wrong: Priceline's `PCLN` against the set's `BKNG`. By the 2026-11-15 amendment, a ticker of
  the time is right, so 3 right and 0 wrong, checked by hand: Priceline Group's stock traded on
  Nasdaq as `PCLN` until it was renamed Booking Holdings in February 2018. That amendment's
  example is this test row, whose set ticker was in view when it was written, before any test
  text was fetched; the scorer's count is the one that stands on its own.
- **Against the expected outcome:** the ticker was expected empty on about a third and never
  wrong; it was empty on 2 of 5 and wrong on 1 by the scorer, 0 by the amendment. The day was
  expected right on about 6 of the 8 positives with a day; only 3 were read, and all 3 were
  right. The second kind was expected on about 3% of negatives; it fired on 1 of 99.
- **The day, on the 3 read with a set day:** 3 right.
- **Nvidia's article:** `not a measured kind`, where *a CEO's conduct, no departure: not measured
  yet*, `NVDA`, was expected. A general sentence, "corporate boards historically tend to oust
  chief executives caught having extramarital affairs", reads as a departure, and a text naming a
  departure is never the second kind; the text gives no exchange ticker. Beside that sentence
  "affairs" is plural, which `\baffair\b` misses; had it matched, the article would have read as
  a `ceo` departure, a worse error.

**In plain words:** the word rules miss both bars. They read 5 of the 12 test texts of a CEO
leaving over conduct: half of the 10 that report the departure, 5 of the 9 that give the conduct.
They misread 6 of 99 other departures. Of the 7 missed, 2 give the reason sentences after the
departure, out of the rules' reach; 2 name it in words the lists lack; 1 gives no reason; 2 are
not about the departure. And the one news article that matters, Nvidia's, is not read as what it
is. By the spec, this is answered by a decisions entry before part 3; the roadmap's next try is a
model on this machine, with its own test set.

## How you know it is right

- A text that names a CEO leaving for "personal reasons", and nothing else, is not the kind.
- A text about a company's fraud that names its CEO is not the kind unless it ties the departure to
  the CEO's own conduct.
- The dev and test sets share no row, and no test address has a row in the fetch log timed before
  the frozen commit.
- A text about an inquiry into the company in which its CEO stays, and nothing ties the CEO's own
  conduct to it, is neither kind.
- A press release stamped 16:05 New York prints the next trading day.
- `read-article` on an article dated before an event in the history answers without that event,
  and (*added 2026-11-15*) without an earlier event whose span had not ended by the article's day.

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
  `answer_triggers`' path for `ceo`. Tests in `tests/test_ceo_scandals.py`. The sets and the
  fetch: `scripts/article_texts.py` (*added 2026-11-15*), a script, since only this step calls it.
- **Docs:** this spec, the glossary (*dev set*, *test set*, *8-K*, *EDGAR*, *reads*, *Wayback Machine*), `docs/status.md`, the changelog and
  roadmap row 20.
