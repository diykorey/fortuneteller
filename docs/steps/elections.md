# Dated shocks, part 1: elections

> Step 10 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-02 after
> [Germany's calendar](germany-calendar.md). It is the first part of four: elections first, then
> tariff announcements, debt-ceiling deadlines and summits, each with its own spec. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** do markets move when a big country votes, and is the move still there a week
later?

Every flow so far is a number published on a calendar. An election is the taxonomy's other half: a
dated event with no forecast to beat, which the market prices in advance through polls. It is the
easiest of the four kinds of shock to date honestly. The vote day is fixed weeks ahead, and its
result lands at a known hour. Tariffs and summits need a judgement about which ones count, so
they come later.

At the end: national elections from five electorates, loaded as event flows from a hand-written
seed file. Each gets rung 1's test on the day after the polls close, and the same test over the
week after.

## The events

- **Source:** `data/seed/elections.csv`, one row per national vote day, written by hand. Each date
  is checked against the electorate's official record (the FEC, the House of Commons Library, the
  Federal Returning Officer, the Conseil constitutionnel, the European Parliament).

  | Flow | Votes | Since | Count | Result known (polls close) |
  | --- | --- | --- | --- | --- |
  | `uselect` | every federal general election, presidential and midterm | 1970 | 28 | Tuesday 20:00 New York |
  | `ukelect` | every general election, snap ones included | 1970 | 15 | Thursday 22:00 London |
  | `deelect` | every Bundestag election | 1972 | 15 | Sunday 18:00 Frankfurt |
  | `frelect` | both rounds of every presidential election | 1974 | 18 | Sunday 20:00 Paris |
  | `euelect` | every European Parliament election, the last day of voting | 1979 | 10 | Sunday 23:00 Brussels |

- **Time:** polls close after every market's close, so the reaction is the next trading day's
  close: Wednesday for the US, Friday for the UK, Monday for the rest. A vote whose polls have not
  closed is not an event yet: the US midterm of 2026-11-03 makes the 29th from that Wednesday.
- **Left out:** referendums (Brexit's among them), state, regional and local votes, primaries,
  and France's legislative elections (2024's snap one among them). France's presidential vote
  counts both rounds: the first picks the two in the second.
- **Origin:** a new seed event type `National election`, and a new seed country `European Union`
  for the European Parliament.

## The rule, fixed before any move is measured

- **Rung 1's test, unchanged:** a ratio ≥ 1.10 at p < 0.01, all sixteen markets, ordinary days from
  each flow's own years.
- **Lesser, as claims.** An election day remains an ordinary day for every other flow and is no
  other flow's shared day, so every existing output stays identical. Each election flow keeps only
  its lone days, **judged on the reaction day**, not the vote day: a UK vote's Friday is often a
  jobs report's. Counted 2026-11-02: 8 of the 15 UK Fridays hold a US release (six jobs reports),
  2 US Wednesdays a Fed decision, 1 European Parliament Monday retail sales; the UK keeps 7 votes,
  the US 26.
- **Too few under ten.** A cell with fewer than ten event days gets no verdict, only *too few*: a
  median of a handful of days is one or two days' moves. Chosen, not derived. Every existing cell
  has at least 49, so none changes; here it empties the UK's cells and the younger markets' (the
  Euro Stoxx 50 has five European Parliament votes, bitcoin three or fewer anywhere).
- **No surprise and no call.** An election has no forecast on any free calendar, and the polls'
  margin is not an expected value this project can grade. None of the five has a sign, a surprise
  table or a walk-forward.
- **And over a week:** the same test on five-day moves, from the close before the reaction day to
  the fifth close from it. The event's windows are compared with the five-day windows that start on
  an ordinary day. Overlapping windows make p optimistic; the [precision](../precision.md) doc
  records it.
- **Chance, counted:** five flows × sixteen markets = 80 *does it move?* cells, at most 0.8
  *moves* by chance, fewer once the cells with *too few* are out; as many again over a week.
- **Expected outcome, written down first:** US elections move VIX and the S&P 500 on the day. No
  European vote moves a market at the bar; the UK's cells are all *too few*. After a week no ratio reaches the bar in any flow.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed file with the 86 vote days, the five flows, lone days on the reaction day, *too few* under ten, `raw-move --week` | A test's seed rows store a Sunday vote at its polls' close, with a Monday reaction; a Thursday vote whose Friday holds a jobs report is left out; a vote whose polls close after now is not stored; a five-day window around a known week gives its move; every existing output identical on a copy of the store; the days left out named |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The five flows' verdicts on the day and over a week, against the expected outcome |

## Technical details

One `ElectionFlow` class beside `StatementFlow`, `lesser = True`, `surprise_rule = None`, reading
the seed file's rows for its country straight from the CSV, as `load-releases` runs: no new table,
`schema.sql` unchanged. Five instances, type codes 16–20. The polls' close is a
column of the file, not a rule in code. `raw-move --week` adds `study.weekly_moves` beside
`daily_moves`, and a `--week` flag that switches between them; the scoreboard is unchanged but
for *too few* in a cell, which none shows today. The reaction-day check is a lesser flow's: the
election flows' days are compared with the lead flows' first reaction days on each market.
`docs/schema.md` gets the type and the country, `docs/legacy/data/` the seed file.

## What this does not do

It adds no poll margins or betting odds as a surprise, no preview of an election morning, and no
week measure on the scoreboard. It covers no other country's vote and no other kind of dated
shock.
