# Earnings

> Step 31 of the [Roadmap](../roadmap.md#phase-5-the-kinds-the-news-brings), phase 5, chosen
> 2026-11-19 by the owner. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** after a big US company reports quarterly earnings above, as expected or below
the analysts' consensus, what does its share price do against the S&P 500, over the day, the week
and the month? Earnings are the kind of event the news brings most often, and a reader who brings
"X beat estimates" should be told what followed such beats before.

At the end: `follows --event earnings` prints the record per kind, measured as [step
20](ceo-scandals.md) measures a company against the S&P 500 (each company's excess move, against
its own base of the 504 closes before), against the rule below written first.

## The way to reach it

- **The companies: the Dow's members on the report's day.** The Dow Jones Industrial Average's 30,
  as its dated changes since 2008 list them (Wikipedia's *Historical components*, each change
  with its day), so nobody here picks the companies and none is chosen by how it did later. A
  former member is in for the days it was a member. Each member's ticker on Nasdaq and Yahoo is
  written beside it in `data/seed/dow.csv`, by hand from the change's announcement, with the
  company's current ticker where it was renamed.
- **The reports and the consensus: Nasdaq's earnings calendar**, one page a day, 2008-01-02 to
  2026-11-18: each report's reported EPS (`eps`, earnings per share as Nasdaq gives it), the
  consensus (`epsForecast`) and the surprise in % (`surprise`). Only the members of that day are
  kept. Five reports' consensus is checked by hand against Yahoo's earnings history (Microsoft
  2026-10-28, JPMorgan 2026-10-14, Apple 2026-10-30, Walmart 2025-11-20, Nike 2025-12-18): within
  $0.02 passes; a miss is written in the evidence and, at two or more, step 1 stops. *Amended
  2026-11-19, at step 3, recording step 1:* JPMorgan reported on 2026-10-13 and Apple on
  2026-11-02, on Nasdaq's calendar and their 8-Ks alike, so those two were checked on those days
  ([step 1's evidence](earnings-steps.txt)).
- **The kind, from Nasdaq's surprise:** *above* at +2% or more, *below* at −2% or less, *as
  expected* between (the releases' three kinds, keys `above`, `as expected`, `below`); no surprise
  given, no kind.
- **The minute: the company's 8-K with Item 2.02** (the form a company furnishes its results on),
  from the SEC's filing index (`data.sec.gov/submissions`, whose `acceptanceDateTime` is UTC): of
  those accepted within a day either side of the calendar's day, the nearest to it, ties the
  earliest. A pre-announcement weeks before falls outside the window. The event is placed at that
  minute, and its day is that minute's New York day. Before 16:00 New York it reacts on that
  day's close; after, on the next. The five reports above are also checked against their known
  release times (before the open, or after the close): every one on the right side of 16:00
  passes; one miss stops step 1.
- **Left out, counted:** a report with no kind, with no 8-K, of a company Yahoo has no closes for,
  with fewer than 504 closes before it, or whose ticker now names another company. A second
  report of one company inside the first's span is left out, as in step 20. Expected: under a
  tenth of the reports in all. Fewer than 300 reports kept stops step 1.
- **One event per report.** Today an event's id is its flow's code and its day, so a flow has one
  event a day; on a reporting day a dozen members can report. The id gains the report's place
  among that day's kept tickers in alphabetical order: code × 10⁸ + day + n × 10¹⁰, n from 0.
  `event_date` reads the day as now. Ids then no longer sort by date within earnings, so the store
  reads a flow's events by `event_ts`, then id; every other flow has one event a day, so its
  order is unchanged.
- **The code:** step 20's function for a company's excess spans (`study.follow_scandals`) is
  called by both flows, each kind's reports passed apart.
- **The flow:** `earnings`, code 34, event type `Earnings release` (already in
  `data/seed/event_types.csv`), the ticker in the detail, scheduled, lesser like the CEO flow:
  `raw-move` judges its lone days, while `follows` keeps every report. Members need no row in
  `data/seed/instruments.csv`: their closes are loaded by `load-prices --companies` as the CEO
  flow's are. History only in this step: no trigger, not on the page's ask. *Amended 2026-11-19,
  by the owner, at step 2:* the scoreboard's raw-move card takes the earnings, as every flow's
  history does (the floods' did at step 30).
  *Amended 2026-11-20:* the reports after 2026-11-18 come in weekly by [step 33](earnings-current.md).
- **The fetch:** Nasdaq's ~4,900 weekdays at one request a second and the SEC's pages at under
  ten, each cached in its own directory under `data/cache/earnings/`, read with `python -I`
  (Python isolated from the download's directory). Seen before writing this: Nasdaq's pages of
  2008-04-22, 2015-04-28 and 2026-10-28, and Microsoft's filing index.

## The rule, fixed before anything is shown

- The companies, the sources, the kind's ±2%, the minute and step 20's bars (an answer at p
  under 0.01 on 10 events or more; *holds* at 30 graded, 60% right, p under 0.01), unchanged by
  what the run shows. *Both runs*: `follows --event earnings` (from the close before) and with
  `--after-the-day` (from the reaction close).
- **Expected outcome, written first, every cell:**
  - The kinds' shares: *above* 55% to 80% of the reports with a kind, *below* under 25%.
  - From the close before, on the day, the week and the month: *above* → *up*, *below* →
    *down*, *as expected* → *can't say*. The day carries the news; the week and month contain it.
  - From the reaction close, on the day, the week and the month: *can't say* for every kind: the
    news is in the reaction close.
  - Walk-forward: *below*'s day *down* from the close before holds; *above*'s day *up* does not
    (beats are the rule, so a beat's day is less sure); nothing else holds.
  - In each run, the answers beyond the six named above no more than that run's chance line plus
    2. The chance line is `follows`' own (each answered cell's chance summed, as in
    [step 26](war.md)).
  - Every other flow's `follows` (both runs), `raw-move` and `scoreboard` output unchanged byte
    for byte on a copy of the store, the CEO flow's included after its code is shared. *Amended
    2026-11-19:* the scoreboard gains the earnings' event and raw-move cells, and nothing else.
- **Outside the rule, recorded:** `raw-move --event earnings`; the reports left out, by reason.

*Written 2026-11-19, before anything was fetched but the three calendar days and the one filing
index named above.*

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed: `data/seed/dow.csv` (`day,ticker,change`: in or out) and `data/seed/earnings.csv` (`day,time,ticker,eps,forecast,surprise,kind`, time in UTC) from the cached pages | The members test and the kind test pass; the ten hand checks pass as written above; the counts and the reports left out, by reason, in `docs/steps/earnings-steps.txt` |
| 2 | The ids and the flow: `follows --event earnings`; the members' closes by `load-prices --companies` | The minute test and the ids test pass; the outputs above unchanged on a copy of the store, in `docs/steps/earnings-steps.txt` |
| 3 | Results | Each bullet of the rule judged right or wrong, with its numbers and command; a goldfish review, each finding fixed or answered |

## How you know it is right

- **The members, by a test:** on 2013-09-23 Goldman Sachs, Visa and Nike are in and Alcoa, Bank of
  America and Hewlett-Packard out; on 2008-09-22 Kraft is in and AIG out.
- **The minute, by a test:** in summer, an 8-K accepted 19:55 UTC (15:55 New York) reacts that
  day and one at 20:04 UTC (Microsoft's of 2026-10-28) the next; in winter, 20:55 UTC (15:55)
  that day and 21:05 UTC (16:05) the next. Of two 8-Ks with Item 2.02, the one nearest the
  calendar's day is kept, and one 20 days before is not.
- **The ids, by a test:** two reports on one day are two events, each giving that day back, read
  in the order of their minutes.
- **The kind, by a test:** surprises of +2.0, +1.9, −2.0 give *above*, *as expected*, *below*.

## What this step does not do

- No trigger, no page, no revenue or guidance: the EPS surprise only.
- No company beyond the Dow's members, and no market but the company against the S&P 500.

## Technical details

- Scripts: `scripts/dow_members.py`, `scripts/nasdaq_earnings.py`, `scripts/sec_8k_times.py`.
- `flows.event_id` gains an optional `n`; `flows.stored_events` orders by `event_ts`, then
  `event_id`.
- Docs: `docs/schema.md` (the id and its order, code 34), `docs/glossary.md` (*EPS*, *8-K Item
  2.02*, *Dow member*), roadmap, status, decisions, changelog.

## Results

*2026-11-19.* Every line quoted is in [the evidence](earnings-results.txt): a copy of the real
store of 2026-11-19 16:08 with the earnings loaded by step 2's code and the members' closes by
`load-prices --companies`; the whole output of `follows --event earnings` (from the close before),
`follows --event earnings --after-the-day` (from the reaction close) and `raw-move --event
earnings`; and two one-off scripts, printed there in full, for what `follows` does not print: the
walk-forward chance of each cell and the reports left out, by reason.

**In plain words:** counted from the close before, a Dow company's shares fall behind the S&P 500
after a miss (169 of 235 down on the day) and **after a report in line with the consensus too**
(203 of 335 down), over the day, the week and the month. After a beat they run ahead over the week
and the month (692 of 1,491 up over the week); on the day too (788 of 1,498), but the placebo gives
the same *up* ten closes away, so the day is not shown to be the beat's. Three links hold
walk-forward: a miss's day (156 of 219 right) and week (145 of 217), and an in-line report's day
(183 of 303, 60.4%, just over the 60% bar). Counted from the reaction close, a miss's next day
still leans *down* (119 of 235) and nothing holds. The expected outcome missed the in-line
reports, a miss's week and a miss's next day.

- **The rule's first bullet:** the companies, the sources, the ±2%, the minute and the bars are
  step 1's and step 2's, unchanged by the run; JPMorgan's and Apple's hand checks ran on their
  real report days, amended above. Right.
- **The kinds' shares** (`scripts/nasdaq_earnings.py seed`, in [step 1's
  evidence](earnings-steps.txt)): *above* 1,513 of 2,092 (72.3%, bar 55% to 80%), *below* 242
  (11.6%, bar under 25%). Right.
- **From the close before** (`follows --event earnings`; header `2092 earnings reports
  2008-01-10 … 2026-11-17: 1513 above, 337 as expected, 242 below`), against *above* → *up*,
  *below* → *down*, *as expected* → *can't say*:
  - *above*'s day: *up* (788 up, 129 the same, 581 down of 1,498, chance 0.0000), **marked *the
    period*** by the placebo, so by step 17's rule it reads as the period, not the beat. **Wrong.**
  - *above*'s week *up* (692/246/553 of 1,491, 0.0000) and month *up* (570/418/485 of 1,473,
    0.0030). Right.
  - *below*: *down* on the day (44/22/169 of 235, 0.0000), the week (40/34/160 of 234, 0.0000) and
    the month (37/59/132 of 228, 0.0000). Right.
  - *as expected*: *down* on the day (95/37/203 of 335, 0.0000), the week (100/52/182 of 334,
    0.0000) and the month (102/77/151 of 330, 0.0049). **Wrong** on all three.
- **From the reaction close** (`follows --event earnings --after-the-day`), against *can't say*
  for every cell: *below*'s day *down* (74/42/119 of 235, chance 0.0037). **Wrong.** *above*'s
  month *about the same* (436/546/490 of 1,472, 0.0013) is marked *the period*, so it is not an
  answer of the kind. The other seven *can't say*. Right on eight of nine.
- **Walk-forward** (graded and right from `follows`; p from the one-off script, Follow's
  `walk_chance`; bar 30 graded, 60% right, 10 points over the base, p under 0.01):
  - From the close before, *below*'s day holds (219 graded, 156 right, 71%, p under 0.000001):
    right. *above*'s day does not (1,355, 707, 52%): right. **Wrong on "nothing else":**
    *below*'s week holds (217, 145, 67%, p under 0.000001) and *as expected*'s day holds (303,
    183, 60.4%, p under 0.000001).
  - From the reaction close nothing holds (*below*'s day 184, 85, 46%; *above*'s day 732, 280;
    *above*'s month 1,011, 368; the rest *too few*). Right.
- **Beyond the six named answers, against the chance line plus 2** (both runs of `follows` print
  chance about 0.3, so a bar of 2.3): from the close before **3**, the three *as expected* cells.
  **Wrong.** From the reaction close 1 (*below*'s day), or 2 counting the month marked *the
  period*. Right.
- **Every other flow's output** ([step 2's evidence](earnings-steps.txt): both runs of the 14
  flows `follows` takes, the 33 flows' `raw-move` and `scoreboard`, main's code against step 2's
  on copies of the store, compared byte for byte): unchanged, but for the scoreboard gaining the
  earnings' event and its 31 raw-move cells (887 → 918), as the owner's amendment of step 2 allows.
  Right as amended.
- **Left out, counted:** step 1 left out 132 of 2,224 (no kind 128, no 8-K 4,
  `scripts/nasdaq_earnings.py seed`). On the day from the close before (the left-out script), 24
  more: 7 of Dow Inc.'s first reports, under 504 closes before (`follows`' 5 *above* and 2 *as
  expected* holes); 16 of Alcoa's, filed under Howmet's ticker (HWM), whose Yahoo closes start
  2016-11-01; and Nvidia's of 2026-11-17, whose reaction close the copy did not hold. Alcoa's and
  Nvidia's count in neither of `follows`' *out* nor *hole* columns: a report with no reaction close
  is skipped there. From the reaction close, the 6 *above* holes are Dow Inc.'s 5 and one Merck day
  on a gap in its closes. 156 in all, 7.0%, under the expected tenth; 2,068 kept, over the 300 bar.
  Right.
- **The size of the move** (`raw-move --event earnings`, outside the rule, recorded): on the 882
  reporting days, homebuilders (ITB) *move* (ratio 1.17, p 0.0008); the S&P 500 (1.15, p 0.0115),
  the Nasdaq (1.13, 0.0153) and Allstate (1.11, 0.0175) *unclear*; the rest *doesn't*.

The expected outcome was **wrong on six counts**: *above*'s day reads as the period; *as expected*
is *down*, not *can't say*, on all three spans from the close before, and three answers beyond
the named six break the chance bar; a miss's week and an in-line report's day hold walk-forward;
a miss's next day is *down* from the reaction close. It was right on the kinds' shares, the
members' left-out count, a beat's week and month, a miss's three spans, the walk-forward of a
miss's day and a beat's day, nothing holding from the reaction close, and every other flow's
output.
