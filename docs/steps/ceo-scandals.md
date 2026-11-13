# News into triggers, part 1: a CEO's conduct in question

> Step 20, part 1, of the [Roadmap](../roadmap.md#next-steps-in-order), taken 2026-11-13 by the
> owner ahead of step 18's grades, with company news as its first kind. Terms are in the
> [Glossary](../glossary.md): *kind*, *span*, *base rate*, *excess move*, the four answers.

## The goal

**In plain words:** when a listed company's CEO is caught in a personal scandal, what did the
company's stock do next, against the market? Nvidia's CEO admitting an affair while the board
investigates foreign-spy claims (2026-11-08) is the news that asked for it.

The tool answers news with what followed past events of the same kind. Before it reads any
article, the kind has to be measured. That is this part. Reading the article (part 2) and a feed
(part 3) come after, each with its own spec.

At the end: `fortuneteller follows --event ceo` prints, for each span, the company's move against
the S&P 500 after past scandals, with part 1's counts, answer, placebo and walk-forward.

## The way to reach it

- **The events come from a list nobody picks.** Famous scandals were famous partly because the
  stock fell, so a list from memory would be picked by its moves (the [tariffs](tariffs.md)
  lesson). The source is the open *CEO dismissal* dataset of S&P 1500 firms (Gentry, Harrison,
  Quigley and Boivie, *Strategic Management Journal* 2021, open at
  [doi:10.5281/zenodo.4543893](https://doi.org/10.5281/zenodo.4543893)). It covers 2000 to 2018 and
  codes why each CEO left, with a description and sources for each departure. Every departure coded *dismissed for legal violations or concerns* is read, and kept when
  its notes name the CEO's own conduct:
  - a relationship, harassment, or other personal misconduct;
  - a misstated credential or expenses.

  Fraud at the company, antitrust and product cases are left out: they are another kind.

  *Amended 2026-11-13, in step 1, before any price was read:* the newer release (1992 to 2023,
  [doi:10.5281/zenodo.23328926](https://doi.org/10.5281/zenodo.23328926), November 2025) is the
  source. A row is kept only if its notes or a cited source tie the departure to the conduct; one
  the dataset codes on suspicion alone is left out. A company is left out with fewer than 504
  closes before its event, or when those closes are not its own (a blank-check shell before a
  merger, a ticker that now names another company).
- **The day is the first public word.** That is the earlier of the departure announcement and the
  first report of the conduct, from a source cited in the seed row, at its New York time.
  *Amended 2026-11-13:* the time is the latest the word is known to be out: a release's stamp, or
  else its 8-K's acceptance, which can follow the release. Where a source says only *before close*
  or *after close*, that is the time; *unknown* reacts at the next close. A word
  after 16:00 or on a closed day reacts at the next close, as every flow does
  (`first_reaction_day`).
- **The market is the company against the market.** The move is the company's span move less the
  S&P 500's over the same closes (the *excess move*, in percent), from Yahoo's daily closes. A
  company Yahoo no longer lists, because it was bought or delisted, is left out and counted. That
  biases the set toward companies that survived, and the results say by how many.
- **Each company's own base.** A company's excess moves are not another company's. Each event's
  cut and base rates come from that company's spans of the same length in the 504 closes before
  its close before, so nothing after the event is read. The answer is part 1's rule with a rate per
  event: *about the same* on all events, *up* and *down* on those that moved, each chance by
  `stats.poisson_binomial_tail`.
- **Part 1's spans, bars and placebo:** the day, week and month, from the close before and from the
  reaction close (`--after-the-day`, the move a trigger can be graded on). Bars at 0.01 and 10
  events, and the placebo on the company's own closes. A second event at one company inside the
  first's span is left out. The walk-forward answers each event from the earlier ones only.
- **Nvidia is not in the history.** The answer for 2026-11-08 is computed only from the events
  before it. Its week and month, graded when their closes are in, are its first live record.

## The rule, fixed before anything is shown

- The source, the coding rule, the day, the excess move, the base window and part 1's bars,
  unchanged by what the run shows.
- **Expected outcome, written first:**
  - Arithmetic, not a finding: with fewer than 40 events nothing reaches 30 graded walk-forward,
    so nothing can hold. The record is shown as counts.
  - Count: 20 to 40 events from 2000 to 2018, of which up to a third are left out with no Yahoo
    history. Nothing after 2018 is in the source, so the record ends there until a later release
    or a second source of the same kind is added, with a dated amendment.
  - On the day: the company *down* against the market. Over the week and the month: *can't say*.
  - From the reaction close: *can't say* on every span.
  - Every existing output unchanged.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The dataset read and coded by the rule; the seed `data/seed/ceo_scandals.csv` with each row's day, time, ticker, CEO, conduct and source; each company's closes loaded | Every kept row cites its source; the coding is listed row by row in this spec; the left-out rows are counted by reason~~ **done** 2026-11-13. *Amended:* the coding is in [`ceo-scandals-coding.csv`](ceo-scandals-coding.csv), not this spec, and the closes load in step 2 |
| 2 | `follows --event ceo` with the excess move and each company's base; `ceo` in `TRIGGER_KINDS` (kind `scandal`, with the company's ticker in the trigger) | Tests: the excess move of a stock that moves exactly as the index is zero; a base never reads a close after the event's close before; with ten events all down against a base of a third, the answer is *down* |
| 3 | Results here and in [MVP results](../mvp-results.md), checked against the expected outcome; the answer for Nvidia's 2026-11-08 printed beside them | Each span's answer and walk-forward recorded |

*Step 1, 2026-11-13:* of the dataset's 237 departures coded *legal*, 58 name the CEO's own
conduct and 26 are kept, 2005 to 2023. Left out: 179 not the CEO's own conduct; 19 with no Yahoo
history; 4 whose ticker now names another company; 1 whose history restarts after the event; 1
with under 504 closes before it; 1 a blank-check shell; and 6 that no source ties to the conduct
(Johnson Controls, MGM, ADP, Crocs, Unifi, Planet Fitness). Twenty-three keep a stamped time; three
say only *before close*, *after close* or *unknown*. The first public word was earlier than the
dataset's date for five: Horace Mann (the drunk-driving disclosure), Wynn (the WSJ report), Apollo
(the NYT report), F5 and Visteon (the dataset's date was wrong). No price was read.

If the dataset is not reachable, or gives fewer than 10 kept events, step 1 stops and says so.
A hand-made list is then the owner's call, labelled as picked.

## How you know it is right

- A stock that moves exactly as the S&P 500 has an excess move of zero on every span.
- An event's base comes from its own company and ends at its close before.
- An event announced on a Sunday reacts at Monday's close.
- A departure for fraud at the company, coded *legal*, is left out by the conduct rule.
- With ten events all down, at a same rate of a third and up half of the moved, the answer is
  *down*, chance 0.5^10. With nine events it is *too few*.

## What this part does not do

No reading of articles (part 2: a pasted article into a trigger, by rules first), no feed (part
3), and no other company kind (fraud, recalls, departures for health or retirement). No stock
outside the US and no index effect: Nvidia's weight in the Nasdaq is a later question. No live
call and no row in `data/calls.csv`.

## Technical details

- **Seed:** `data/seed/ceo_scandals.csv`, columns `day,time,ticker,company,ceo,conduct,source`,
  documented in `docs/legacy/data/`. `event_types.csv` already holds `Corporate scandal / fraud /
  bankruptcy`.
- **Flows:** a `DatedShockFlow`, `ceo`, unscheduled, with the row's time. Each event's ticker is
  read from its row.
- **Prices:** the companies' closes from Yahoo into `daily_bars` under their tickers, each a row in
  `data/seed/instruments.csv` (`asset_class` equity). They are not in `MVP_PRICE_SERIES`: they are
  not markets every event is measured on.
- **Study:** `excess_spans(stock, index, c)` and a per-event base, beside `follow_market`, which
  gains per-event rates. Part 1's other functions are reused unchanged.
- **Triggers:** a fourth column, `ticker`, read only for `ceo`. Every other flow's file is read as
  today.
- **Docs:** this spec, the glossary (*excess move*), `docs/schema.md` if a column is added,
  `docs/status.md`, and roadmap row 20.
