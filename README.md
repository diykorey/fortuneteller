# FortuneTeller

A fortune teller who shows their record. You read a headline, such as "the Fed cuts rates", and
FortuneTeller answers with what followed every past event of that kind, for the markets behind what
people pay for, over spans from a day to a year. It is an entertainment tool with a realistic
approach, not financial advice ([Legend](docs/legend.md#the-target)).

```
Fed cuts rates → EUR/USD
  next week    down       24 of 30 past cuts; all weeks: down 3,900 of 8,000
  next month   can't say  down 16 of 30; all months: down 3,800 of 8,000
```

(An illustration of the shape, not a measurement.)

## The rules every answer follows

- **Arithmetic on history, never a model's opinion.** Each span answers up, down, about the same,
  or can't say, against the base rate: how often that market went that way over every span of
  that length, events or not.
- **Counts, never a percentage.** A call shows its record as counts and its band until one proves
  honest by rung 3's rule ([the record, not a probability](docs/steps/record-not-probability.md)).
- **A call is made from the actual once it lands, never before it.** A statement nobody scheduled
  is never called before it happens.
- **Measured before shown.** Every number comes from free, real data and is graded walk-forward.
  "No edge" is a result, and the page shows it.
- **The US first, then one country at a time.** The euro area and Germany are already stored.

## How it works

Every event flow (an event type from one country) is loaded from its history and joined to daily
market closes. Then four questions are asked in order, each tested before the next is built on it:

1. Do markets move on the event's days more than on ordinary days? (raw-move)
2. Does the move follow the surprise, the gap between the actual and the expected? (surprise)
3. Does that hold for the next release, replayed walk-forward? (predict)
4. After an event of a kind, does a market go one way more often than its base rate? (follows)

What holds is called live on release days and graded each evening on the
[scoreboard](https://diykorey.github.io/fortuneteller/scoreboard/). Why it is built in this order
is in the [Legend](docs/legend.md); what comes next is in the [Roadmap](docs/roadmap.md).

## New here?

Start at **[docs/README.md](docs/README.md)**. It gives a reading path of five documents, three
commands to run, and one spec to study, and maps every other document.

## Repository layout

```
docs/            # legend + roadmap + step docs + glossary — start at docs/README.md
docs/legacy/     # the pre-2026-09-11 design corpus, kept for reference
data/seed/       # committed seed CSVs the embedded store loads
src/fortuneteller/  # the package: config, models, db helper, seed loader, CLI
tests/           # pytest suite (ruff + mypy --strict + pytest is the gate)
```

## Status

Bootstrapping, **measurable-spine first**. M0 (the data spine), the MVP and ladder rungs 1–6 are
complete; the [roadmap](docs/roadmap.md) marks each later step done or in progress. The repo holds
the US releases (CPI, the jobs report, retail sales, core PCE, GDP, the ISM survey, weekly jobless
claims), Fed and ECB decisions, the euro area's and Germany's releases, the Fed chair's and the ECB
president's scheduled statements, and dated shocks (elections, tariff actions, the debt limit,
summits), against these markets (the S&P 500, the Nasdaq, the 10-year and 5-year yields, the dollar index
and the euro, gold, Brent, VIX, the DAX, the Euro Stoxx 50, the FTSE 100 and the STOXX 600,
bitcoin, a defence and an energy ETF, the funds holding corn, wheat, soybean, gasoline and natural gas futures, utilities and homebuilders, coffee, and the 5-year breakeven inflation), 1972 to today, from free sources: each market's measured move around every
release, how it relates to each surprise, and a walk-forward replay of every link.

```bash
uv sync
uv run fortuneteller --help                 # every command and what it prints
uv run fortuneteller load-releases          # every event, from FRED, the Fed and TradingView (needs FT_FRED_API_KEY)
uv run fortuneteller load-prices            # daily closes from Yahoo and FRED and the move around each release (needs FT_FRED_API_KEY)
uv run fortuneteller load-surprises         # each surprise against its expected values
uv run fortuneteller raw-move --event cpi   # do release days move more than ordinary days?
uv run fortuneteller surprise --event nfp   # does the move follow the surprise?
uv run fortuneteller predict --event nfp    # the walk-forward replay, and a call for the next release
uv run fortuneteller score                  # the live calls, graded
uv run fortuneteller scoreboard             # the page: every call graded, every verdict and record
```

**What it predicts:** the direction of the 10-year and 5-year yields, the dollar index and the euro
on the six links that hold walk-forward at 08:30 (the jobs report's dollar and euro, its two
yields, retail sales' two yields; ISM's 5-year yield holds too, but ISM lands at 10:00, after the
morning job), each printed with its record as counts and its band, never a probability: none has
proved honest yet. On release days the calls are made, graded and delivered as a desktop popup
unattended ([the release-day job](docs/steps/release-day-job.md), [the evening
score](docs/steps/evening-score.md)), and the [scoreboard](https://diykorey.github.io/fortuneteller/scoreboard/) shows
every call graded, every verdict and every record, rewritten by the evening job. Stocks, gold and
VIX follow no surprise by direction; the Fed, the ECB, euro-area inflation, ISM and jobless claims
give no call. [MVP results](docs/mvp-results.md) has the findings in plain words, the
[roadmap](docs/roadmap.md) what comes next, and [status](docs/status.md) the task in hand.

> **Data provenance:** the seed reference tables are partial (read-only Notion export limits) and
> the effect-size values in them are illustrative placeholders, not measurements. Every number the
> commands print comes from the loaded history, never from these tables. Each table states its own completeness; see
> [docs/legacy/data/README.md](docs/legacy/data/README.md).
