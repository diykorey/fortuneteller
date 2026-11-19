# Earnings

> Step 31 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** after a big US company reports quarterly earnings above, in line with or below
the analysts' consensus, what does its share price do against the S&P 500, over the day, the week
and the month? Earnings are the kind of event the news brings most often, and a reader who brings
"X beat estimates" should be told what followed such beats before.

At the end: `follows --event earnings` prints the record per kind, measured as [step
20](ceo-scandals.md) measures a company against the S&P 500, against the rule below written first.

## The way to reach it

- **The companies: the Dow's members on the report's day.** The Dow Jones Industrial Average's 30,
  as its dated changes since 2008 list them (Wikipedia's *Historical components*, each change
  with its day), so nobody here picks the companies and none is chosen by how it did later. A
  former member is in for the days it was a member. A company Yahoo has no closes for is a hole,
  counted, as in step 20.
- **The reports and the consensus: Nasdaq's earnings calendar**, one page a day, 2008-01-02 to
  2026-11-18: each report's reported EPS (`eps`), the consensus (`epsForecast`) and the surprise
  in % (`surprise`), as Nasdaq gives them. Only the Dow's members of that day are kept. The
  consensus is checked by hand against a second source on five reports, the differences written
  in step 1's evidence.
- **The kind, from Nasdaq's surprise:** *above* at +2% or more, *below* at −2% or less, *as
  expected* between; no surprise given, no kind.
- **The minute: the company's 8-K with Item 2.02**, from the SEC's filing index
  (`data.sec.gov/submissions`): the earliest accepted within a day either side of the calendar's
  day. It sets the reaction day: before 16:00 New York, that day's close; after, the next. A
  report with no such 8-K is left out and counted. Five reports whose release time is well known
  are checked by hand against their 8-K.
- **One event per report.** Today an event's id is its flow's code and its day, so a flow has one
  event a day; on a reporting day a dozen members can report. The id gains the report's place in
  its day: code × 10⁸ + day + n × 10¹⁰, n from 0 by ticker. `event_date` reads the day as now.
  The CEO flow's code reads its companies' excess spans and is called for both flows.
- **The flow:** `earnings`, code 34, event type `Earnings release`, the ticker in the detail,
  three kinds as the releases' (`above`, `as expected`, `below`), lesser, scheduled. History only
  in this step: no trigger, not on the page.
- **The fetch:** Nasdaq's ~4,900 weekdays at one request a second and the SEC's pages at under
  ten, each cached in its own directory under `data/cache/earnings/`, read with `python -I`.

## The rule, fixed before anything is shown

- The companies, the source, the kind's ±2%, the minute and step 20's bars, unchanged by what the
  run shows. *Both runs*: `follows --event earnings`, and with `--after-the-day`.
- **Expected outcome, written first:**
  - Counts are recorded, not predicted, but the kinds' shares are: *above* 55% to 80% of the
    reports with a kind, *below* under 25%.
  - From the close before, on the day: *above* → *up*, *below* → *down*. Over the week and the
    month from the reaction close: *can't say* for every kind: the news is in the day's price.
  - Walk-forward: *below*'s day *down* holds; *above*'s day *up* does not (beats are expected,
    so a beat's day is a coin with a lean).
  - On all history, no more answers than the chance line plus 2, but for the two day answers above.
  - Every other flow's output unchanged byte for byte on a copy of the store, the CEO flow's
    included after its code is shared.
- **Outside the rule, recorded:** `raw-move --event earnings`, and the reports left out: no
  kind, no 8-K, no closes.

*Written 2026-11-19, before anything was fetched but five calendar days and one company's filing
index, seen to check the sources answer.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed: `data/seed/dow.csv` (the members' changes) and `data/seed/earnings.csv` (`day,time,ticker,eps,forecast,surprise,kind`) from the cached pages | The seed tests below pass; the hand checks are in `docs/steps/earnings-steps.txt` |
| 2 | The ids and the flow: `follows --event earnings`; the members' closes by `load-prices --companies` | The flow tests pass; every other flow's output unchanged on a copy of the store |
| 3 | Results | Each bullet of the rule judged, with its numbers and command; a goldfish review |

## How you know it is right

- **The members, by a test:** on 2013-09-23 Goldman Sachs, Visa and Nike are in and Alcoa, Bank of
  America and Hewlett-Packard out; on 2008-09-22 Kraft is in and AIG out.
- **The minute, by a test:** Microsoft's report of 2026-10-28, its 8-K accepted 20:04 UTC, reacts
  on 2026-10-29; a report whose 8-K is accepted 11:30 UTC reacts that day.
- **The ids, by a test:** two reports on one day are two events, each giving that day back.
- **The kind, by a test:** surprises of +2.0, +1.9, −2.0 give *above*, *as expected*, *below*.

## What this step does not do

- No trigger, no page, no revenue or guidance: the EPS surprise only.
- No company beyond the Dow's members, and no market but the company against the S&P 500.

## Technical details

- Scripts: `scripts/dow_members.py`, `scripts/nasdaq_earnings.py`, `scripts/sec_8k_times.py`.
- `flows.event_id` gains an optional `n`; `study.follow_scandals` gains its kinds' split.
- Docs: `docs/schema.md` (the id, code 34), `docs/glossary.md` (*EPS*, *8-K Item 2.02*, *Dow
  member*), roadmap, status, decisions, changelog.
