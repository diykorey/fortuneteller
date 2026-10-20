# The record, not a probability

> Follows [rung 3](rung-3-confidence.md#results), whose probabilities were not honest. Chosen
> 2026-10-20, before [rung 6](../roadmap.md#after-the-mvp--the-feature-ladder) (delivery). Terms
> are in the [Glossary](../glossary.md).

## The goal

**In plain words:** a call says what we can check (its direction, how often the link was right
before, where half its moves land) and no longer a percentage nobody can check.

Rung 3 printed each call's record as a probability ("67%"). The bands proved honest; the
probabilities did not: stated 68%, right 61–65%. The question here was whether a better-built
probability could prove honest instead. On today's history it cannot, whatever its method.

## Why no method can pass yet

Rung 3's check 2 asks a probability's Brier score to beat a coin's and the drift's, each with
p < 0.05. Measured 2026-10-20: calls planted right exactly as often as they state, graded with
`stats.sign_flip_p` as rung 3 does, 200 trials per row (seed 7).

| Right (= stated) | Drift | Calls | Passes coin | Passes drift | Passes both |
| --- | --- | --- | --- | --- | --- |
| 64% | 60% | 80 | 43% | 13% | 13% |
| 64% | 60% | 500 | 93% | 28% | 28% |
| 68% | 60% | 80 | 52% | 20% | 20% |
| 68% | 60% | 500 | 99% | 65% | 65% |
| 68% | 55% | 80 | 56% | 35% | 35% |
| 68% | 55% | 200 | 82% | 62% | 62% |

A link has 60–80 calls with a probability and gains about 12 a year. At that size a perfectly
honest probability passes one time in three to five; reaching 200 calls takes about ten years. A
new method designed now would also be designed after seeing rung 3's 68% against 63%, so only live
calls could grade it. Pooling the links would change rung 3's per-link rule, and same-day calls are
not independent.

## The rule

- **The call line drops the percentage.** It gives the direction, the link's walk-forward record
  as counts ("right on 39 of 60 calls before") and the 50% band, e.g.
  `DXY up closes up today: right on 39 of 60 calls before, +0.12% to +0.40%`. Before 20 calls it
  says "too few calls so far", as now.
- **Grading is unchanged.** `data/calls.csv` keeps its `probability` column (the smoothed record),
  and `predict` and `score` keep grading it by rung 3's rule. Should a link ever pass, the number
  can come back; nothing here is tuned on its result.
- **Rung 6's gate, restated** (*amended 2026-10-20*): a warning carries the direction, its
  walk-forward record and its band, never a stated probability, until a link's probability is
  honest by rung 3's rule.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | This spec, the power table, and rung 6's gate in the roadmap | Merged |
| 2 | `predict --actual`/`--fetch` print the record and band, no percentage | Tests: a call with 20 or more calls before prints counts and band and no `%` before them; the logged row still holds the probability |

## What this does not do

No new probability, pooling or fit; no change to rung 3's checks, to the band, to `score`'s tables
or to the jobs.
