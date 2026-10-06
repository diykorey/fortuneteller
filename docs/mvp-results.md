# MVP results

> The MVP's outcome in plain words. The detail, the numbers and how they were checked are in the
> step documents: [1 Releases](steps/step-1-releases.md), [2 Prices](steps/step-2-prices.md),
> [3 Raw move](steps/step-3-raw-move.md), [4 Surprise](steps/step-4-surprise.md). Terms are in
> the [Glossary](glossary.md). Measured on data loaded 2026-10-05; the rung 1 section on
> 2026-10-06, with [its own document](steps/rung-1-more-events.md).

## What we set out to prove

FortuneTeller is meant to warn which markets will move, and how, when an event happens. That only
works if three things are true, in this order (see the [Legend](legend.md)):

1. **The event moves markets at all.**
2. **The size of the move follows the size of the surprise:** how far the number landed from what
   was expected.
3. **That relationship holds for the next event**, not only for past ones.

The MVP tested the first two, on one event and five markets, before building anything that
predicts: every US CPI release since 1972, and the S&P 500, the 10-year Treasury yield, the dollar
index, gold and the VIX, from free data only.

## What we found

**1. CPI moves three of the five markets. True for three.**
On a CPI day the 10-year yield moves 25% more than on an ordinary day, VIX 19% more and the dollar
16% more, and chance alone would rarely give that. The S&P 500 and gold move no more than usual.

**2. The move follows the surprise for the 10-year yield, weakly. True for one.**
When core CPI comes in hotter than its recent trend, the 10-year yield rises that day, by about
1 bp for every 0.1 percentage point of surprise, and it goes the expected way about 62% of the
time. The link is real but weak: the surprise explains only a small part of the day's move. For
the dollar the evidence is mixed (a real link, but the direction is right only about half the
time). For VIX, the S&P 500 and gold, the move does not follow the surprise by the rule we fixed
in advance.

**3. Whether it holds for the next release: not tested yet.** That needs predictions made before
releases and graded after them: rungs 2–4 of the [roadmap](roadmap.md).

| Market | Moves more on CPI days? | Move follows the surprise? |
| --- | --- | --- |
| 10-year yield | Yes | **Yes, weakly** |
| Dollar index | Yes | Unclear |
| VIX | Yes | No |
| S&P 500 | No | No |
| Gold | No | No |

## What it means

**The project's bet holds in one place, and only weakly so far.** CPI matters to three markets,
and for the 10-year yield the size of the surprise says something about the move. That is a
signal. It is not yet a product: a direction that is right 62% of the time is wrong 38% of the
time, and a warning built on it today would mostly be noise with a confident face, which is the
failure the project exists to avoid.

**The weakness may be in the measurement as much as in the market.** Two shortcuts, listed in
[Precision](precision.md), probably hide part of the effect:

- **The window is a whole day.** A move from yesterday's close to today's close carries every other
  piece of news that day. Prices from just before and after 08:30 would isolate the release.
- **"Expected" is a trend, not the market's forecast.** There is no free history of what
  economists expected for core CPI; the free model forecast (the Cleveland Fed's) turned out to be
  almost the same as the trend. A surprise against the real forecast would be cleaner.

On the 155 releases since 2013 the 10-year yield's link is stronger (right 71% of the time), but
that rests on 49 releases and was not a planned test, so it is a lead, not a result.

**What it does not mean.** Nothing here predicts a future release, and nothing should be used to
trade or to warn. The numbers describe the past.

## Rung 1 — more events

Measured 2026-10-06. Detail and checks in [rung 1](steps/rung-1-more-events.md).

The same steps ran on two more events: the monthly jobs report (NFP, 1955 on) and the Fed's rate
decisions (1994 on, including 14 unscheduled ones). Two fixes came with them:

- **A cleaner baseline.** "Ordinary days" now leave out every CPI, jobs-report and Fed day.
- **The right close for each market.** A move starts at the last close before the event. Gold
  settles at 13:30, before the Fed's 14:00 statement, so on Fed days it reacts the next day.

**1. Do the events move markets? Yes, all three; the jobs report most.**

| Market | CPI | Jobs report | Fed decision |
| --- | --- | --- | --- |
| 10-year yield | Yes (+33%) | **Yes (+67%)** | Unclear (+23%) |
| Dollar index | Yes (+18%) | Yes (+25%) | Yes, borderline (+22%) |
| VIX | Yes (+22%) | Yes (+31%) | Yes (+25%) |
| S&P 500 | No | Yes (+19%) | Yes (+30%) |
| Gold | No | Yes (+27%) | **Yes (+81%)** |

The percentages say how much bigger the median move is than on an ordinary day. CPI's answers did
not change with the cleaner baseline; its numbers rose a little.

**2. Does the move follow the jobs-report surprise? Clearly related, but not reliable enough.**
When payrolls beat their 12-month trend, the 10-year yield and the dollar tend to rise. The link
is far beyond chance (p 0.0001 over about 670 reports) and stronger than CPI's. But the direction
is right only 58% (yield) and 56% (dollar) of the time, under the 60% bar fixed in advance, so
neither passes. The other three markets have no agreed direction for good jobs news, and do not
pass either. The Fed gets no surprise test: there is no free record of what the market expected.

| Market | CPI surprise | Jobs-report surprise |
| --- | --- | --- |
| 10-year yield | **Yes, weakly** (right 62%) | Unclear (right 58%) |
| Dollar index | Unclear (right 53%) | Unclear (right 56%) |
| VIX, S&P 500 | No | No |
| Gold | No | Unclear (no agreed direction) |

**What it means.** The method works beyond CPI: the jobs report and the Fed move markets clearly,
and every check on the data held. The surprise link is still the weak point. For the jobs report
it is real but misses the bar, which again points at the measurement rather than the market: the
"expected" value is a trend, not the forecast economists published.

## What comes next

A decision, not yet made. The options:

| Option | What it is | Cost | What it would tell us |
| --- | --- | --- | --- |
| ~~**More events**~~ (roadmap rung 1) | ~~Add the jobs report (NFP) and Fed decisions~~ **done**, above | — | — |
| **Sharper measurement** | Economists' consensus forecasts for CPI and payrolls, and intraday prices around the release | Paid data | Whether the yield's and the dollar's jobs-report link passes the bar against a real forecast; for CPI, whether the weak link is the market or our daily window |
| **A better free forecast** | A model of each jobs report from what is published before it (weekly jobless claims, the ADP report) | Free | The same question as above, without paying, but with a model in place of the market's view |
| **Predict the next release** (rung 2) | Forecast the 10-year yield's direction before each CPI release, and grade it after | Free | Claim 3, for the one link that passes; but on a 62% signal |

Rung 1 strengthened the case for better expected values before predicting: two links (the yield
and the dollar on jobs reports) are clearly real but sit just under the bar, and the expected value
is the known shortcut.
