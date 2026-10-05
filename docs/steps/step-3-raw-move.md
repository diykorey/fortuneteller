# MVP step 3 — Raw move

> Step 3 of the four in the [Roadmap](../roadmap.md); this document follows the step template in the
> [Legend](../legend.md). Unfamiliar acronym or term? See the [Glossary](../glossary.md). What this
> step simplifies, and the more precise way, is in [Precision](../precision.md).

## The goal

**In plain words:** do these five markets move more on CPI days than on ordinary days?

Step 2 recorded how much each instrument moved on every CPI release day. On its own that number
says nothing: the S&P 500 moved a median 0.55% on release days, but it moves about half a percent
on any day. This step puts the two side by side and gives each instrument a verdict, so we know
whether CPI matters at all, and for which instruments.

This is the first of the Legend's three must-be-true claims: **events move these instruments
measurably at all.** If no instrument moves, the project stops here. That outcome is allowed. For
an instrument that does move, step 4 asks whether the size of the move follows the size of the
surprise. An instrument that doesn't move gives step 4 nothing to explain.

The deliverable is one command, `uv run fortuneteller raw-move`. It reads what step 2 stored,
stores nothing, and prints a table: for each instrument, the typical move on CPI days and on
ordinary days, their ratio, how likely chance alone would give that ratio, and the verdict.

## The way to reach it

Three obstacles; how each is handled is in [Decisions](#decisions).

**A result can look like an effect when it isn't one.** Over 600 release days, some difference from
ordinary days always shows up. So the rule for "moves" is fixed in this document before the
verdicts are run: big enough to matter **and** unlikely to be chance. Changing it after seeing the
output means a new row in Decisions saying what changed and why.

**One wild day can decide an average.** The 1987 crash would move a mean by itself.

**Markets have loud and quiet years.** The effect may differ by era, but a verdict per era means 18
tests, and at p < 0.01 one lucky pass becomes likely.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`daily_moves` and `cpi_days`: every day's absolute move from `daily_bars`, and which days are CPI days~~ **done** | Tests pass; on live data the CPI-day moves equal `observations.ret_1d` release for release, and the counts are 649 / 648 / 649 / 312 / 440 |
| 2 | ~~`compare_moves`: medians, ratio, permutation `p`, verdict~~ **done** | The synthetic checks below pass; two runs give the same `p` |
| 3 | ~~`uv run fortuneteller raw-move` prints the verdict table, the era rows and the rule~~ **done** | Live run prints all five instruments; an empty database gives a one-line error |
| 4 | ~~Results: paste the live output into [Results](#results) and read the verdicts off it~~ **done** | Results answers "does CPI matter, and for which instruments?"; status and roadmap updated |

## How you know it is right

Each check below can fail.

- **Same moves as step 2.** Every CPI-day move this step computes must equal that release's
  `observations.ret_1d`, and the number of CPI days per instrument must equal step 2's: 649 / 648 /
  649 / 312 / 440. A mismatch means steps 2 and 3 pair different days.
- **A planted effect is found.** On synthetic data where CPI-day moves are twice the ordinary ones,
  the verdict is *moves*.
- **No effect is not invented.** On synthetic data where CPI days are drawn from the same
  distribution as other days, the verdict is not *moves*.
- **Repeatable.** Two runs print identical output; the random seed is fixed.
- **Sanity against step 2.** The S&P 500's CPI-day median must be the 0.55% step 2 measured.

## What this step does not do

- **No direction.** Only the size of the move counts here; up or down is step 4's question.
- **No surprise.** Step 4 relates the move to expected-vs-actual.
- **No new table.** Nothing is stored; `abn_ret_1d` in `observations` stays empty.
- **No events other than CPI**, and **no instruments beyond the five**.
- **No cleaner baseline.** Jobs-report and Fed days stay in the ordinary pile; see
  [Decisions](#decisions) and [Precision](../precision.md).

## Decisions

Each choice made while designing this step, the options turned down, and why.

| Decision | Chosen | Turned down | Why |
| --- | --- | --- | --- |
| What "ordinary day" means | Every trading day that is not a CPI day | Also removing jobs-report and Fed days; a window of 20 days around each release | Uses only stored data. Noisy days left in the baseline make the CPI effect look **smaller**, never larger, so this choice can miss an effect but not invent one. The other two are in [Precision](../precision.md), with when to build them |
| What counts as "moves" | Ratio ≥ 1.10 **and** p < 0.01; *unclear* if only one holds; *doesn't* if neither | p alone; ratio alone | p alone passes effects too small to warn about; ratio alone can be luck with 312 releases (gold). Both together means real and big enough. **Disclosure:** the bar was set after a rough look at era ratios (CPI days by release date, no gap rule), before any full-history ratio, `p` or verdict existed. Those rough ratios ranged 1.00–1.43 |
| How to measure "typical" | Median of absolute moves | Mean; mean of squared moves (volatility) | One crash day can decide a mean; the median ignores it |
| How to get `p` | Permutation test, 10,000 relabellings, fixed seed | t-test; adding numpy or scipy | No assumption that moves are normally distributed (they are not), and no new dependency. Takes about 4 s per instrument |
| How eras count | One verdict over all history; era rows show ratio and `n` only | A verdict per era; only 1990 onwards | 18 tests make a lucky pass likely; choosing 1990 after seeing the numbers would be fitting the rule to the data |
| Where results go | Printed only | A new table | Step 4 needs the release-day moves, which `observations` already holds, not these summaries |

## Technical details

**Data.** Everything comes from `daily_bars` and `event_instances`; nothing is fetched.

**Daily moves.** For one instrument, take its closes in date order. Each pair of consecutive closes
gives one move, computed with step 2's `release_move` (`pct` or `bps`), and the absolute value
is kept. A pair more than `MAX_CLOSE_GAP_DAYS` (4) apart is a hole in the data, not a day, and is
skipped. Across all five instruments only 29 pairs are skipped. One is a CPI day: UST 10Y's April
1978 release, which step 2 skips for the same reason.

**CPI days.** For each CPI release, `closing_price_before_after` gives the close it pairs with;
that close's date is a CPI day. These are exactly step 2's `t1` days. If two releases ever pair
with the same close, that day counts once (none do today).

**Ratio and `p`.** For one instrument, the CPI-day moves are `cpi` (size `n`), the rest `other`:

- `ratio = median(cpi) / median(other)`.
- 10,000 times: draw `n` moves at random from `cpi + other`, compute the same ratio of the drawn
  moves to the rest.
- `p = (1 + number of draws with a ratio ≥ the real one) / 10,001`, so its smallest value is
  0.0001.

The median of "the rest" is read from the sorted list of all moves, skipping the drawn positions,
so each draw costs about `n log n`, not a full sort.

**Eras.** 1970–1989, 1990–2007, 2008–2019, 2020–now, by the date of the move. For each: `n` and
ratio, or `—` when the instrument has no CPI day in it (VIX and gold before 1990).

**Output.** One verdict row per instrument, then one era row per instrument, then the rule:

```
instrument   CPI days  median CPI  median other  ratio  p       verdict
UST10Y / ZN       648      x.x bp        x.x bp   x.xx  0.xxxx  …
...
by era: ratio (CPI days)
instrument   1970-1989    1990-2007    2008-2019    2020-now
UST10Y / ZN  x.xx (nnn)   x.xx (nnn)   x.xx (nnn)   x.xx (nn)
...
moves = ratio >= 1.10 and p < 0.01; unclear = one of the two; doesn't = neither
```

**Errors.** No CPI events: `run fortuneteller load-releases first`. No `daily_bars` for an
instrument: `run fortuneteller load-prices first`. One line on stderr, exit code 1.

**Code.** Functions in `study.py` (no new module), the handler in `__main__.py`, tests in
`tests/test_study_raw_move.py`. The synthetic checks build closes in memory and call
`compare_moves` directly; they need no database.

## Results

**Answer: yes, CPI matters, for three of the five instruments.** On a CPI day the 10-year yield,
the dollar and VIX move 16–25% more than on an ordinary day, and chance alone would rarely give
that. The S&P 500 and gold do not, by the rule fixed above.

Live run on 2026-10-02, data loaded that day from FRED and Yahoo, repeated unchanged on 2026-10-05:

```
instrument   CPI days  median CPI  median other  ratio  p       verdict
SPY / ES          649       0.55%         0.51%   1.07  0.0997  doesn't
UST10Y / ZN       648      4.0 bp        3.2 bp   1.25  0.0007  moves
DXY               649       0.29%         0.25%   1.16  0.0032  moves
GC / XAU          312       0.57%         0.56%   1.02  0.4132  doesn't
VIX               440       4.21%         3.54%   1.19  0.0022  moves

by era: ratio (CPI days)
instrument   1970-1989    1990-2007    2008-2019    2020-now
SPY / ES     1.01 (209)   1.10 (216)   1.15 (144)   1.06 (80)
UST10Y / ZN  1.00 (208)   1.39 (216)   1.14 (144)   1.43 (80)
DXY          1.26 (209)   1.17 (216)   1.32 (144)   1.09 (80)
GC / XAU     —            1.03 (88)    1.01 (144)   1.02 (80)
VIX          —            1.12 (216)   1.14 (144)   1.29 (80)

moves = ratio >= 1.10 and p < 0.01; unclear = one of the two; doesn't = neither
```

**Per instrument:**

- **UST 10Y — moves.** The clearest effect: a typical CPI day moves 4.0 bp against 3.2 bp. The
  era rows show where it comes from: 1.39 in 1990–2007 and 1.43 since 2020, against 1.00 in
  1970–1989. That early 1.00 is weak evidence either way: those yields are rounded to whole basis
  points, and those release dates are not checked against BLS (both in
  [Precision](../precision.md)).
- **DXY — moves.** 1.16 overall and above 1.10 in three of four eras. The most recent era is the
  lowest, 1.09 on 80 releases.
- **VIX — moves.** 1.19 overall, and rising: 1.12, 1.14, then 1.29 since 2020.
- **S&P 500 — doesn't.** CPI days are 7% larger than other days, with p ≈ 0.10: a difference this
  size comes up by chance about one time in ten. It is the closest of the five to the line, and its
  era rows sit around it (1.01, 1.10, 1.15, 1.06).
- **Gold — doesn't.** 1.02 overall and 1.01–1.03 in every era. CPI days look like any other day.

**The checks.** All passed: CPI-day moves equal `observations.ret_1d` for every release, with 649
/ 648 / 649 / 312 / 440 CPI days (3.1); a planted effect is found and none is invented (3.2); two
runs print identical output (3.3); the S&P 500's CPI-day median is step 2's 0.55%.

**What it means for step 4.** Step 4 asks whether the size of the move follows the size of the
surprise. That question has an answer only where there is a move to explain, so step 4's claims
are about **UST 10Y, DXY and VIX**. The S&P 500 and gold stay in its output at no extra cost, as a
control: a strong surprise relationship there, with no extra move here, would be a reason to doubt
the measurement rather than a finding.

**Triggers in [Precision](../precision.md) this result touches.** The S&P 500 sitting near the line
is the trigger for a cleaner baseline (jobs-report and Fed days removed). It is not built now: it
needs the NFP and FOMC calendars, which ladder rung 1 loads anyway. No instrument came out
*unclear*, so the decision rule's trigger did not fire.
