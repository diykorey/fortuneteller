# FortuneTeller documentation

Given an event, say which instruments move, by how much, in which direction — with confidence that
means something.

## Start here

| Document | What it is |
| --- | --- |
| **[Roadmap](roadmap.md)** | What we are building, in what order, and what "done" means. **Read first.** |
| **[Glossary](glossary.md)** | Every acronym, ticker, and piece of jargon, explained. Read alongside anything else. |

That is the whole current corpus, deliberately. Both were rewritten on 2026-09-11; everything
written before then lives in **[legacy/](legacy/README.md)** and is reference material, not
instructions. The one live exception there is `legacy/data/`, which documents the seed CSVs the code
actually loads.

## Where things are

| Path | Holds |
| --- | --- |
| `docs/` | The current, authoritative documents — the two above. |
| `docs/legacy/` | The pre-reset design corpus: architecture sketches, data-table documentation, old milestone plans. |
| `data/seed/` | The committed reference CSVs the code actually reads. |
| `schema.sql` | The table definitions, as plain SQL. |
| `src/fortuneteller/` | The package: config, models, store, seed loader, CLI. |

## How this folder grows

Flat until it needs not to be. A subfolder gets created when a *second* document of the same kind
exists — not in advance. The natural next splits, when they arrive:

- `concepts/` — one file per idea that needs explaining beyond a glossary line (surprise, abnormal
  return, calibration).
- `data/` — how each reference table is sourced, what is complete, what is a placeholder.
- `decisions/` — short records of choices that would otherwise be re-litigated.

A document is written when something real needs it. A document that describes code that does not
exist is a liability — the last corpus is in `legacy/` partly because it drifted into that.

## Current state

**M0 — the data spine — is shipped**: typed models, the DuckDB schema, the seed reference tables,
and a working `init | seed | query-demo` CLI. No prediction code exists yet. MVP step 1 is next; see
the [roadmap](roadmap.md).
