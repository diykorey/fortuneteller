# The expert's brief

> Given, with the pack in [expert-pack/](expert-pack/), to the expert reader of
> [step 41](expert-hypotheses.md). Nothing else is given.

You are an economist and statistician. The files in the pack are the complete record of a
project that measures what followed past events of each kind in the markets, as it stood on
2019-12-31. Use only what is in the pack and what an expert knew on that day. Use no knowledge of
anything that happened after 2019-12-31: no event, price or study from 2020 on.

**The record.** For each flow (a family of events: Fed decisions, CPI releases, earnings reports
and so on) the pack has its events to 2019 and `follows`' answers: for each kind of event, each
market and each span (the day, the week and the month), what followed, from the close before
(`follows-FLOW.txt`) and from the reaction close (`follows-FLOW--after-the-day.txt`). An answer is
*up*, *down*, *about the same*, *can't say*, *too few* or *the period*, against the market's own
ordinary moves, with its counts and its chance. `kinds.txt` lists every flow, its kinds, and every
market with its unit.

**Your task.** Write 40 rules that you, as an expert, expect to hold from 2020 onward. They should
be richer than one kind against one market where you have a reason: a condition before the event
(the market's or the company's trend, another event just before), or an effect on a market
further along a chain. Rules that restate an answer already in the record are allowed, but count
against the 40. Each rule is tested once by code on 2020 onward, by these bars: at least 10
events; the stated direction at p < 0.01; not *the period*; and a condition must raise the share
of events in the stated direction over the same rule without it (p < 0.05). With 40 rules,
about 0.4 would pass by chance alone.

**The form.** One CSV row per rule, with these columns and only these values:

| Column | Values |
| --- | --- |
| `id` | 1 to 40 |
| `flow`, `kind` | a flow and one of its kinds, as in `kinds.txt` |
| `condition` | `none`, `move` or `event` |
| `on`, `closes`, `side`, `threshold` | for `move`: a market of `kinds.txt` or `company`; 21 or 63; `above` or `below`; a number in the market's unit (`pct`, percent, for a price or a company's shares; `bps`, basis points, for a yield or breakeven). Empty otherwise |
| `other_flow`, `other_kind` | for `event`: another flow and kind, met when one has its reaction close within the 21 closes before. Empty otherwise |
| `market` | a market of `kinds.txt`, or `company` (the event's own company, against the S&P 500) |
| `span` | `day`, `week` or `month`, from the close before |
| `direction` | `up` or `down` |
| `reasoning` | one or two sentences: why an expert would expect it |

A condition is read at the close before the event's reaction close. A row with any other value is
counted as untestable. Reply with the CSV only.
