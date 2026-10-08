# Adding an event type or an expectation source

> How to plug something new in without touching what works. The design and why it is shaped this
> way: [event flows](steps/event-flows.md). Proved by `tests/test_event_flows.py`, which plugs in a
> made-up flow and source and runs every command on them.

## A new event type

Write one class in `src/fortuneteller/flows.py` and add it to `EVENT_FLOWS`.

```python
class GdpFlow:
    event_type = "Other macro data (GDP/PMI/PCE/retail/claims)"  # a row of data/seed/event_types.csv
    country = UNITED_STATES       # a row of data/seed/countries.csv: the origin country
    zone = NEW_YORK               # the release's time zone: release times and dates are read in it
    type_code = 4                 # the leading digit of its event ids; unique per flow
    cli_name = "gdp"              # --event gdp
    label = "GDP"                 # three letters keep the reports aligned
    surprise_rule = SurpriseRule(  # or None: the event gets prices and raw move, no surprise
        combinations=(("gdp", TREND_12M),),       # the first one gives the verdict
        expected_sign={"SPY / ES": 1, "UST10Y / ZN": 1, "DXY": 1, "GC / XAU": 0, "VIX": -1},
        noticeable=0.2,           # hit-rate cut-off and slope step, in the measure's unit
        step="0.2pp",
    )

    def events(self, api_key: str) -> EventBatch:
        """Fetch, parse and check the release history; refuse rather than return something wrong."""

    def actuals(self, events, api_key: str) -> list[Actual]:
        """Each stored event's first-published value per measure, with its unit."""
```

From there, with no other change:

- `load-releases` stores its events, all-or-nothing with the other flows.
- `load-prices` measures every instrument around them, and `raw-move --event gdp` compares those
  days with ordinary days, which now exclude GDP days too.
- `load-surprises` asks every expectation source about its actuals (the 12-month trend works on any
  measure), and `surprise --event gdp` gives its verdict.

Fetching and parsing the outside source go in `src/fortuneteller/sources.py`, as for the others.

The same event type from another country is another flow: the same `event_type`, its own
`country`, `zone`, `type_code` and `cli_name`. Its events are stored and read apart from the US's;
`EVENT_FLOWS` refuses two flows sharing a (type, country) pair, a type code or a name. Its 12-month
trend and its `surprise` report use its own events only, even with the same measure names as the
US's ([country-aware events](steps/country-aware-events.md)). A market outside New York gives its
`PriceSeries` its own close time and `zone`.

## A new expectation source

Write one class in `src/fortuneteller/expectations.py` and add it to `EXPECTATION_SOURCES`.

```python
class Consensus:
    name = "consensus"            # stored as surprises.baseline
    label = "the consensus"       # how reports name it

    def expectations(self, events, actuals, api_key: str) -> list[Expectation]:
        """One Expectation per actual it has a forecast for: same event, measure and unit, and
        known_at, naive UTC, when the forecast was made."""
```

Every expectation is checked before a surprise is computed: its event is stored and has a surprise,
an actual exists for its measure, the units match, and it was known strictly before the
announcement. One failure refuses the whole load and names it. A missing expectation is not a
failure; that event simply has no row from this source.

To give the new source the verdict for an event, put its combination first in that flow's
`surprise_rule`; anywhere else in the rule, it is shown as context.

## Checking the change

Run every report with `main`'s code and with the change on one database: anything already measured
must come out byte-identical. `docs/schema.md` gets the new `event_type`, measure or baseline value
in the same change.
