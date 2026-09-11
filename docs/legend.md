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

## The idea

The bet, in one sentence:

> **Price moves on the gap between what was expected and what happened — and that gap's effect is
> stable enough, per event type and instrument, to estimate from history.**

The reasoning: anything the market already expects is in the price before the release. What is left
to react to is the **surprise**. If the same kind of surprise produces a similar-sized move each
time it occurs, that relationship is measurable, and what is measurable can be forecast.

Three things must be true for the product to exist. They are independent, testable, and ordered:

| # | Must be true | Tested by | If false |
| --- | --- | --- | --- |
| 1 | Events move these instruments measurably at all | MVP step 3 | Stop. There is nothing here. |
| 2 | The size of the move tracks the size of the surprise | MVP step 4 | The event matters but is not forecastable this way — rethink the signal. |
| 3 | That relationship holds for the *next* release, not just past ones | Ladder rungs 2–4 | It is a description of history, not a predictor. |

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
- **Release** — **does not exist yet.** Nothing is published or versioned for anyone else's use.
  When something is delivered to a person outside the repo, that is rung 6, and this entry gets
  rewritten then rather than guessed at now.

## What every step document must say

One document per step, named `step-N-<name>.md`, in this order. [Step 1](step-1-releases.md) is the
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
