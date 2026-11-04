# Legend

How to read this project: what we are ultimately building, why we think it can work, how we intend
to get there, and what every planning document must say.

This document covers the top of the chain: **what we are building, why it could work, and the way
we intend to get there.** It does not contain the plan — [`roadmap.md`](roadmap.md) does — and it
does not index the folder; [`README.md`](README.md) is the entry point and holds the full map of how
the documents connect.

It ends with the one thing that governs every future document: the template each step must follow.

## The target

Given an event, say which instruments move, by how much, in which direction — with confidence that
means something, in time to act on it.

A **warning** product, not a trading system. The latency budget is seconds to minutes, which means
we are never competing with HFT and never need to.

"Confidence that means something" is the hard part and the whole point. A system that says 70% must
be right about 70% of the time, or the number is decoration.

*Amended 2026-10-23.* **An entertainment tool with a realistic approach, not a financial one.** A
fortune teller who shows their record: each fortune is a direction with its graded history beside
it, or a measured reaction to a kind of event, never advice. That changes the surface, not the
method: every bar stays where it was fixed, nothing is tuned for a result, and a negative result is
still a result. It changes what counts as progress: more kinds of events and markets, a steadier
cadence, and being seen. A reaction record graded after the fact, and a preview before a scheduled
statement, count as fortunes; a direction right six times in ten is content when the four are
shown too.

*Amended 2026-11-04, by the owner.* **A headline, turned into what follows for the things a
reader pays for.** The reader reads the news ("the Fed cuts rates", later "floods in Colombia")
and wonders what comes next. The tool is to find the event in the news itself, name its kind, and
answer with what followed every past event of that kind, over spans from a day to a year (the
numbers are an illustration, not a measurement):

```
Fed cuts rates → EUR/USD
  next week    down       24 of 30 past cuts; all weeks: down 3,900 of 8,000
  next month   can't say  down 16 of 30; all months: down 3,800 of 8,000
```

- **The outcome is a market, not a shelf price:** each everyday thing through the traded market
  behind it, fuel through gasoline and Brent, mortgages through Treasury yields. "The coffee
  market rose" is enough.
- **Each span answers *up*, *down*, *about the same* or *can't say*,** against the **base rate**:
  how often the market went that way over every span of that length in the kind's own years,
  events or not. The rule from counts to answer, and its bars, are fixed in step 17's spec before
  measuring, and the answer is replayed walk-forward. *Can't say* is shown and counted, never
  graded as right.
- **The answer is arithmetic on history, never a model's opinion.** A model may read the news into
  a trigger and put figures into sentences; nothing paid is used, so a model runs on this
  machine. (The owner first proposed a model's guess, then chose this.)
- **Bare figures first.** Counts and base rates, never a percentage, until rung 3's honesty rule
  allows one; the words *most probably* (at 60%, above the base rate), *could* and *will not*
  wait for that.
- **Many countries, the US first.** The goal is readers and markets in different countries; the
  work starts with US events and US-traded markets, and widens one country at a time once the US
  answers hold (the euro area and Germany, already stored, next).
- **What has no past is never shown beside a record:** a what-if about a new technology is
  labelled as reasoning, if shown at all.

This retires one line of the 2026-10-23 decision, "for news the product is a graded reaction
record": an event that has happened is answered for the spans after it. A call is still never made
before its event, and the week ahead still gives no direction. Where an event has a surprise, the
method below is unchanged; where it has none, the direction is the fourth claim below.

## The idea

The bet, in one sentence:

> **Price moves on the gap between what was expected and what happened — and that gap's effect is
> stable enough, per event type and instrument, to estimate from history.**

The reasoning: anything the market already expects is in the price before the release. What is left
to react to is the **surprise**. If the same kind of surprise produces a similar-sized move each
time it occurs, that relationship is measurable, and what is measurable can be forecast.

Three things must be true for the product to exist. They are independent, testable, and ordered
(*amended 2026-11-04:* a fourth, for events without a surprise):

| # | Must be true | Tested by | If false |
| --- | --- | --- | --- |
| 1 | Events move these instruments measurably at all | MVP step 3 | Stop. There is nothing here. |
| 2 | The size of the move tracks the size of the surprise | MVP step 4 | The event matters but is not forecastable this way — rethink the signal. |
| 3 | That relationship holds for the *next* release, not just past ones | Ladder rungs 2–4 | It is a description of history, not a predictor. |
| 4 | *Added 2026-11-04.* After an event of a kind, a market goes one way more often than its base rate over the span | Roadmap step 17, walk-forward | Every span answers *can't say*; the page shows reaction records only. |

This is why the roadmap is shaped the way it is: **each early step tests one of those, cheaply,
before anything is built on top of it.** The MVP is not a small version of the product. It is the
experiment that decides whether the product is worth building.

## The way

Five principles. They are the residue of one failed attempt, not abstractions.

1. **Measure before predicting.** Numbers come from real data before any machinery consumes them.
   Predicting from placeholder values produces output that looks like a product and means nothing.
2. **Every step ends in a real number.** If you cannot run something and read a fact off it, the
   step is not finished and probably was not a step.
3. **Build the smallest thing that produces that number.** No package until a second caller needs
   it; no indirection for a single case; no plan doc longer than the code it specifies.
4. **A negative result is a result.** "No edge" ends the question honestly and early. A plan that
   can only succeed is not a plan.
5. **Say what you do not know.** Where data is missing or a claim is weaker than it looks, the
   output says so. Shrinking a claim is free; discovering it was hollow later is not.

## How the way becomes a plan

The vocabulary, so the words stay load-bearing:

- **Step** — one unit of MVP work. Ends in a runnable command printing a real number. There are
  four, and they are sequential: each one's output is the next one's input.
- **Rung** — one feature after the MVP, on the ladder in the roadmap. Ordered, and each is worth
  building *only because the one below it worked*.
- **Graduation trigger** — a named condition that must actually fire before a heavier piece of
  infrastructure is allowed (Postgres, a web service, a streaming bus). Listed in the roadmap.
- **Milestone** — **retired.** The old M0–M7 scheme planned seven milestones ahead of a single
  measurement, and most of it was discarded. M0 is kept as a historical label for what shipped.
  Do not reintroduce the scheme.
- **Release** — the [scoreboard](steps/scoreboard.md): the page in `docs/scoreboard/`, rewritten
  by the evening job on the days the score changes and served by GitHub Pages from `main` at
  <https://diykorey.github.io/fortuneteller/scoreboard/> (*rewritten 2026-10-26*, when the page and the
  job's line were built, the setting on since 2026-10-27; rung 6 had delivered a popup to one
  laptop first). Nothing is versioned or packaged for
  anyone else's use, and nothing is planned to be.

## What every step document must say

One document per step, named `step-N-<name>.md`, in this order. [Step 1](steps/step-1-releases.md) is the
worked example.

| Section | Must answer | Test of whether it is done |
| --- | --- | --- |
| **The goal** | What exists at the end that did not exist before — and why it matters to the steps after it | A reader can state the deliverable in one sentence |
| **The way to reach it** | What makes this hard, and the approach that handles it | The non-obvious obstacle is named, not assumed |
| **The steps** | The ordered sequence, each with a "done when" | Each row is checkable without judgement |
| **How you know it is right** | The checks that would catch a *plausible wrong answer*, not just a crash | At least one check could actually fail |
| **What this step does not do** | The boundary | Scope creep has a named edge to cross |
| **Technical details** | Sources, mappings, file placement, tests — last, because it changes most | Someone else could implement it |

Two rules about these documents:

- **Why before how.** If a reader cannot say why the step exists before reaching the technical
  section, the document is in the wrong order.
- **A document is written when something real needs it**, and deleted when it stops being true.
  The `legacy/` folder exists because the last corpus described code that did not exist. That is a
  liability, not an archive.
