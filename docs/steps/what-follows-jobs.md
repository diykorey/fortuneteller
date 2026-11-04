# What follows a jobs report, over spans

> Step 17, part 1b, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1](what-follows.md); proposed 2026-11-04 before part 2, whose quarter and year would answer
> few Fed cycles (about ten cutting and ten hiking since 1994), and taken on the owner's "go ahead".
> Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when the jobs report comes in above what was expected, as expected, or below,
what did each market do over the next day, week and month? It is the headline a news reader sees
on the first Friday of a month ("more jobs than expected"); the reader learns the kind, not the
number.

The jobs report has a surprise, so this widens step 17 beyond the flows without one (roadmap row
17, amended with this spec). Its surprise holds on the day on the most markets (the 5-year yield,
the dollar index and EUR/USD, [more outcomes](more-outcomes.md)); no step has asked whether the
day's move is still there a week or a month on, or what an *as expected* report does. The day
cells for *above* and *below* are a check against those links; the week, the month and *as
expected* are the question.

At the end: `fortuneteller follows --event nfp` prints part 1's table for the jobs report.

## The way to reach it

- **The kind, from the consensus.** The `surprises` row whose measure is the rule's first
  combination's (payrolls) and baseline its `predicted_from` (Nasdaq's consensus, with
  TradingView's where Nasdaq has none): *above* at +50k or more (the rule's `noticeable`, in
  thousands as stored), *below* at −50k or less, *as expected* between. A report with no such row,
  or a NULL surprise, has no kind and is in no walk. On the store of 2026-11-04: 222 reports,
  2008-03-07 … 2026-10-02, 68 above, 104 as expected, 50 below. The actual is the first print, the
  headline; revisions to earlier months are not read.
- **Part 1's method, unchanged:** the spans, the non-overlap rule, the base and its cut, the answer
  with direction apart from size, the placebo a span away, the walk-forward and its bars, the
  chance lines. A report's 08:30 New York release reacts the same day on every market but EUR/USD,
  the next day, as in `raw-move`.
- **The month holds the next report.** A month span runs about to the next report's reaction close,
  so it usually contains that report's day move, and that report is left out for overlap. A week
  or month answer includes the day's own move: it says the move was not undone, not that it went
  on. The results count how many counted month spans contain another report.
- **The release or the kind.** A jobs-report day may move a market whatever the report says (part
  1's VIX fell on hold days). An answer that the opposite kind also gives, or *as expected* gives
  too, is recorded as the release, not the kind. On the day and the week the placebo ten closes
  away is usually a Friday too, so there *the period* reads "the period or the weekday".

## The rule, fixed before anything is shown

- Part 1's bars, the kinds above and the release rule, unchanged by what the run shows.
- **Expected outcome, written first.**
  - Arithmetic, not a finding: over the month about half of each kind is left out for overlap,
    about 34 *above* and 25 *below* counted, so neither can hold there; *below* has at most 40
    graded on the day.
  - On the day, on all history: *above* answers the 10-year and 5-year yields and the dollar index
    *up* and EUR/USD *down*, *below* at least two of their reverses; at least 5 answers between
    them on these four markets, against about 1.4 by chance for a span's 48 cells.
  - Walk-forward on the day: *above* holds on the 5-year yield, the dollar index and EUR/USD; nothing
    else holds anywhere.
  - Over the week: *above*'s day answers stay on the 5-year yield and the dollar index; over the
    month at most 2 answers in all.
  - *As expected*: no answer, on any span.
  - Left out: about half of each market's reports over the month for overlap; the FTSE 100 and the
    DAX lose more month spans to holes.
- Every existing output, the Fed's `follows` table included, is unchanged byte for byte.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`release_kinds`; the kinds passed through; `follows --event nfp`~~ **done** 2026-11-04 (PR #242) | The tests below pass; on a copy of the store the header reads `follows: 222 jobs reports 2008-03-07 … 2026-10-02: 68 above, 104 as expected, 50 below` and 144 cells print |
| 2 | ~~Results here and in [MVP results](../mvp-results.md), the expected outcome checked, the roadmap row; each answer's counts also without 2020-03 … 2021-12, as a reading aid~~ **done** 2026-11-04, [below](#results) | Each kind's answers, release marks and walk-forward records recorded against the expected outcome |

*Step 1, 2026-11-04 (PR #242):* on a copy of the store the header reads as written above and 144
cells print; the Fed's table is byte for byte the one part 1 recorded. The header now counts the
decisions with a kind only: the same 276 today, one fewer in the days after a meeting before FRED
has the new rate; with none, `follows` says so and exits 1.

## Results

Measured 2026-11-04 on a copy of the store: 222 reports, 68 above, 104 as expected, 50 below.

**Two answers hold walk-forward: after a report above the consensus, the 10-year and the 5-year
yields rise on the day**, right on 38 and 37 of 57 graded (67% and 65%). Nothing else holds: the
dollar index (27 of 53), EUR/USD (18 of 45), VIX (24 of 49) and the defence ETF (22 of 50) after
*above*, VIX after *as expected* (41 of 72) and the 5-year yield after *below* (15 of 30) are
*doesn't*.

**On all history, 13 answers**, against about 4.3 by chance for the 144 cells:

| Kind | Span | Market | Up / same / down | Answer | Chance | Without 2020-03 … 2021-12 | Read as |
| --- | --- | --- | --- | --- | --- | --- | --- |
| above | day | UST10Y / ZN | 47 / 8 / 13 | up | under 0.0001 | up, 43 / 6 / 10 | the kind; **holds** |
| above | day | UST5Y / ZF | 47 / 6 / 15 | up | 0.0001 | up, 44 / 3 / 12 | the kind; **holds** |
| above | day | DXY | 39 / 16 / 13 | up | 0.0005 | up | the kind |
| above | day | EURUSD | 10 / 24 / 34 | down | 0.0003 | down | *the period or the weekday* |
| above | day | VIX | 14 / 17 / 37 | down | 0.0068 | down | the release: *as expected* answers it too |
| above | day | ITA | 36 / 19 / 13 | up | 0.0047 | *can't say* | the kind, gone without 2020–21 |
| above | week | UST10Y / ZN | 37 / 14 / 17 | up | 0.0056 | up | the kind |
| above | week | UST5Y / ZF | 35 / 18 / 15 | up | 0.0051 | up | the kind |
| as expected | day | VIX | 19 / 26 / 59 | down | 0.0001 | down | the release |
| below | day | DXY | 12 / 9 / 29 | down | 0.0032 | down | the kind |
| below | day | GC / XAU | 30 / 12 / 8 | up | 0.0011 | up | the kind |
| below | day | UST5Y / ZF | 11 / 9 / 30 | down | 0.0014 | down | the kind |
| below | week | GC / XAU | 28 / 14 / 8 | up | 0.0044 | up | the kind |

Over the month nothing answers. Of the 134 month spans kept on the 10-year yield, 88 hold the next
report's reaction close; a month answer would have carried it.

**Against the expected outcome, written first:**

- Arithmetic: neither *above* nor *below* holds over the month (39 and 29 counted, none graded to
  30): **right**.
- On the day, *above* answers both yields and the dollar *up* and EUR/USD *down*; *below* at least
  two reverses (the dollar and the 5-year yield); at least 5 answers on these four markets (6):
  **right**.
- Walk-forward, *above* holds on the 5-year yield: **right**; on the dollar index and EUR/USD:
  **wrong**; nothing else holds: **wrong**, the 10-year yield holds too.
- Over the week, *above* stays on the 5-year yield: **right**; on the dollar index: **wrong**
  (*can't say*; the 10-year yield instead). Over the month at most 2 answers: **right** (none).
- *As expected* answers nothing: **wrong**, VIX falls, as on every report's day: the release.
- Left out over the month about half for overlap (29 of 68 above): **right**; the FTSE 100 and
  the DAX losing more to holes (13 and 14): **right**.

**What it means.** A reader told "more jobs than expected" can be told, with a record, that
Treasury yields most probably rise that day: right on two in three replayed reports. The rise
mostly stays for the week on all history, though not graded to 30 there. A miss lowers the dollar
and the 5-year yield and lifts gold on the day, without a record yet. Whatever the report says,
VIX tends to fall on its day, as on a Fed hold: a scheduled release lifts uncertainty off the
market.

## How you know it is right

- Surprises of +50, +49.9, −50 and −49.9 are *above*, *as expected*, *below*, *as expected*; a
  report with only a trend surprise of +200 has no kind.
- On made-up closes where every report day falls 3% whatever its kind, all three kinds answer
  *down* on the day, and the results rule reads it as the release.
- The Fed's `follows` header and first row on made-up data equal the lines printed before this
  change, pasted into the test as literals.
- With no key set, three reports at +60, 0 and −60 and one market's closes, `follows --event nfp`
  exits 0, prints the header literal for them and an *above* row; with no surprise stored it prints
  `follows: no surprises for nfp yet; run \`fortuneteller load-surprises\` first` and exits 1.

## What this part does not do

No other release (each its own part), no quarter or year (part 2), no page, no trigger file (step
18). Nothing is stored. Reports in one regime are not independent; the chance says more than it
should, as in part 1.

## Technical details

- `study.py`: `ABOVE, AS_EXPECTED, BELOW = "above", "as expected", "below"`; `SURPRISE_KINDS` in
  that order; `release_kinds(flow, con) -> dict[int, str]` by event id;
  `follow_market(decisions, closes, unit, c, order=KINDS)`; `follow_decisions(flow, kinds, order,
  con) -> (events, cells)`, `events` the stored ones with a kind, oldest first.
- `__main__.py`: `describe_follows(events, kinds, cells, order, noun)`; the kind column as wide as
  the longest kind in the order, at least 5, so the Fed's table is unchanged. The header's counts
  read `{n} {kind}s` for the Fed, as before, and `{n} {kind}` for the release kinds. `_follows`
  checks stored events (`load-releases`), then daily_bars (`load-prices`), then for `nfp` the
  surprises; FRED and its key for `fomc` only, nouns "Fed decisions" and "jobs reports". Help:
  "what each market did over a day, a week and a month after each kind of event", `--event`
  choices `fomc` (default) and `nfp`.
- Tests in `tests/test_what_follows.py`.
- **Docs:** this spec's results, `docs/mvp-results.md`, the roadmap's row 17 (amended), the
  glossary (*above*, *as expected*, *below* as kinds), `docs/status.md`.
