# Legacy documentation

Everything in this folder was written **before 2026-09-11**, when the current documents were
rewritten. It is kept for reference and for the research in it. **None of it is authoritative** —
with one exception, `data/`, noted below.

The current documents are [`docs/roadmap.md`](../roadmap.md) and
[`docs/glossary.md`](../glossary.md). Where this folder and those disagree, those win.

## Why it was set aside

Two things went wrong with this corpus:

1. **It described code that did not exist.** Much of it specifies a replay harness, an episode
   format, and prediction modules that were built, judged over-engineered for the stage, and removed
   in the 2026-08-05 reset (see the reset note in [CLAUDE.md](../../CLAUDE.md)). Those documents now
   read as instructions for a plan that was abandoned.
2. **It planned far ahead of what was proven.** A full M0–M7 milestone scheme, a 31-event taxonomy,
   55 instruments, and 132 platforms were documented before a single real market measurement
   existed.

## What is still worth reading

| Document | Still useful for |
| --- | --- |
| **[`data/`](data/README.md)** — **still live** | The exception in this folder. It documents the seed CSVs the code **actually loads today**: event taxonomy, instruments, effect-size seeds, news sources, and how complete each table is. Trust it about the data; it sits here only because it moved with the rest. |
| [`calibration-dataset.md`](calibration-dataset.md) | The event-study methodology: data model, the calibration query, and the statistical pitfalls. Directly relevant to the MVP measurement. |
| [`detection-and-calibration.md`](detection-and-calibration.md) | How to turn a noisy feed into trustworthy events, and how to make a stated probability mean something. Relevant much later, on feature-ladder rungs 3 and 7. |
| [`standardized-surprise.md`](standardized-surprise.md) | Why surprise rather than headline tone drives magnitude. The concept behind MVP step 4. |
| [`news-source-stack.md`](news-source-stack.md), [`news-source-coverage-and-gaps.md`](news-source-coverage-and-gaps.md) | Ranked news sources and their coverage gaps. For detection, far out. |
| [`event-polarity-and-classifier-prompts.md`](event-polarity-and-classifier-prompts.md) | Per-event-type polarity and draft LLM classifier prompts. For detection, far out. |
| [`tech-stack.md`](tech-stack.md) | Why Python, why DuckDB, why no ORM. The reasoning still holds. |
| [`type_of_financial_markets.md`](type_of_financial_markets.md) | Background on market structure. |

## What is superseded

| Document | Superseded by |
| --- | --- |
| [`roadmap.md`](roadmap.md) | [`docs/roadmap.md`](../roadmap.md) — the M0–M7 scheme is replaced by the MVP plus a feature ladder. |
| [`mvp-architecture.md`](mvp-architecture.md) | Partly. Its decisions (Python-first, single process, DuckDB, narrow scope, free data) still hold; the replay-harness mechanism it describes does not. Carries a banner saying so. |
| [`m0-tickets.md`](m0-tickets.md) | Nothing — M0 shipped. Kept as the record of what was built. |
| [`architecture.md`](architecture.md) | Nothing yet. A north-star sketch of a Java/Kafka production system; no trigger for it has fired, and none is close. |
| [`old-docs-index.md`](old-docs-index.md) | [`docs/README.md`](../README.md) — the previous docs index, kept as a record of how the corpus was organized. |

The M0-R and M1 ticket sets that used to sit here were deleted in the cleanup; they survive in git
history and on the `main_05082026` branch.
