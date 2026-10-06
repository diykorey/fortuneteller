# Event flows and expectation sources

> A refactor after [rung 1](rung-1-more-events.md), before the next rung; it follows the step
> template in the [Legend](../legend.md). Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** one standard way to plug in a new event type or a new source of "expected",
without touching what already works and without having to know how the rest fits together.

Rung 1 added the jobs report and the Fed next to CPI, and a second kind of expected value next to
the trend. Each was added in its own way: `RELEASE_SERIES`, `load_fomc_decisions`,
`payroll_surprises`, `MEASURE_SERIES`, `SURPRISE_RULES` and the CLI's `EVENTS` each know a little
about every event. The next steps (consensus forecasts, a jobs-report model, more events) would add
more of the same.

At the end: every event type is one **event flow**, every source of "expected" is one
**expectation source**, both talk in four common records, and one shared step validates every
expectation against the event before computing a surprise. Every report prints exactly what it
prints today.

## The way to reach it

**Three of each now exist,** so rule 2 (no indirection for a single case) allows the abstraction:
three event types (CPI, NFP, Fed) and three expected values (CPI's trend, the nowcast, the payroll
trend).

**What is specific stays inside its flow.** CPI's January fix and its cross-check with Cleveland's
published actuals, NFP's revision history and level guard, the Fed's calendar scraping and
target-rate cross-check: each is the flow's own business. A flow refuses to return anything if its
checks fail, as today.

**What is common is written once.** The 12-month trend works on any measure's past actuals, so one
source serves CPI core, CPI headline and payrolls. The checks that make a surprise trustworthy
(right event, right measure, same unit, known before the announcement) live in one function.

**The obstacle: proving nothing changed.** The refactor moves most of `study.py`. Every PR runs
every report and load with `main`'s code and its own on one database; the output must be
byte-identical and `surprises` identical row for row.

## The four records

| Record | Fields | Today |
| --- | --- | --- |
| `EventInstance` | event id, type, announcement time (UTC), country, detail, scheduled | unchanged: the `event_instances` row |
| `Actual` | event id, measure, value, unit | new; replaces `MonthlyChange` |
| `Expectation` | event id, measure, source, value, unit, `known_at` | new; replaces `trend_expectations`' and `nowcast_expectations`' dicts |
| `Surprise` | event id, measure, source, actual, expected, surprise | unchanged: the `surprises` row; `baseline` holds the source name |

## The two interfaces

```python
class EventFlow(Protocol):
    event_type: str
    cli_name: str                          # "cpi", "nfp", "fomc"
    label: str                             # "CPI", "NFP", "Fed": three letters keep reports aligned
    surprise_rule: SurpriseRule | None     # verdict combination, signs, cut-off; None: no surprise
    def events(self, keys: Settings) -> EventBatch: ...            # events + report lines
    def actuals(self, events: Sequence[EventInstance], keys: Settings) -> list[Actual]: ...

class ExpectationSource(Protocol):
    name: str                              # stored as surprises.baseline
    def expectations(
        self, events: Sequence[EventInstance], actuals: Sequence[Actual], keys: Settings
    ) -> list[Expectation]: ...

EVENT_FLOWS = [CpiFlow(), NfpFlow(), FedFlow()]
EXPECTATION_SOURCES = [Trend12m(), ClevelandNowcast()]
```

**The shared step,** `build_surprises(events, actuals, expectations)`, refuses the whole load,
naming source, event and check, if an expectation:

- names an event that is not stored, or whose flow has no surprise rule;
- has no `Actual` for its event and measure;
- has a different unit from the actual;
- was not known strictly before the announcement (a day-only `known_at` counts as the end of that
  day, so a nowcast from the release day is rejected, as today).

A missing expectation is not an error: the first year has no trend, and there is no nowcast before
2013.

**Adding later.** A new event type is one `EventFlow` and one line in `EVENT_FLOWS`; prices, raw
move, the trend and the surprise test then apply to it. A new source is one `ExpectationSource` and
one line in `EXPECTATION_SOURCES`; validation applies to it, and its rows sit next to the trend's.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `expectations.py`: `Expectation`, `ExpectationSource`, `Trend12m`, `ClevelandNowcast`, the validating `build_surprises`; `load-surprises` routed through it | Each validation failure has a test; every report byte-identical |
| 2 | `flows.py`: `Actual`, `EventFlow`, `CpiFlow`, `NfpFlow`, `FedFlow`; `load-releases` and `load-surprises` routed through `EVENT_FLOWS` | Every load and report byte-identical; `surprises` identical row for row |
| 3 | The CLI derives `--event` choices, labels and surprise rules from the flows; the old event-specific constants are deleted | No event type is named outside its flow; every report byte-identical |
| 4 | A short "adding an event type / an expectation source" recipe; schema.md, glossary, status | A toy flow and a toy source, registered only in a test, run end to end |

## How you know it is right

- **Byte-identical output.** `load-releases`, `load-surprises`, `raw-move` (all three events) and
  `surprise` (CPI, NFP), run with `main` and with the branch on one database.
- **`surprises` row for row.** Both tables exported and compared both ways.
- **Validation can fail.** One test per check, each fed an expectation that breaks only that
  check.
- **Plugging in touches nothing.** A toy event flow and a toy source, defined in a test, go through
  `load-surprises` and `surprise` with no change outside the test.
- **The 240 existing tests pass,** with only their imports changed.

## What this step does not do

No new event type, no new expectation source, no new numbers. No new table: actuals and
expectations live in memory during `load-surprises`, and only `surprises` is stored. No plugin
loading, no configuration file: the two lists are the registry.

## Technical details

| File | Holds after the refactor |
| --- | --- |
| `sources.py` | unchanged: fetching and parsing FRED, Yahoo, Cleveland, the Fed |
| `flows.py` | `Actual`, `EventBatch`, `EventFlow`, `SurpriseRule`, `event_id` / `event_date`, the three flows, `EVENT_FLOWS` |
| `expectations.py` | `Expectation`, `ExpectationSource`, `Trend12m`, `ClevelandNowcast`, `build_surprises`, `EXPECTATION_SOURCES` |
| `study.py` | measurement only: prices, observations, raw move, surprise tracking |
| `__main__.py` | commands, driven by the two lists |

`Actual` and `Expectation` are frozen dataclasses: they are never stored. `known_at` is a naive UTC
`datetime`, like `event_ts`. Two new modules and no new package, so rule 1 holds.

## Results

*Filled in by step 4.*
