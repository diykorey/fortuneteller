# The signs

> Step 19, part 2c, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [the breakeven](breakeven.md) and [the scoreboard, faster](scoreboard-faster.md). Taken 2026-11-05
> on the owner's "merge and proceed". Row 19 is amended with this spec. Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** nine markets people feel can say that they move, but not which way a surprise
should push them, so no call can ever be made on them. This part writes down that way for the two
where economics gives one: utilities and homebuilders. Each is then tested like every other signed
market, and is called only if it passes.

At the end, `surprise` gives utilities and homebuilders real verdicts where they are signed,
`predict` replays them, and a link that holds is called by the morning job.

## The way to reach it

- **A sign comes from a reason, never from a result.** The rule from
  [more outcomes](more-outcomes.md) stands. Parts 1 to 2b have already shown which days these
  markets move, their `follows` answers and their unsigned correlations; no sign below rests on
  them. The signed `surprise` and `predict` are not run until this spec is merged.

| Market | Sign | On which rules | The reason |
| --- | --- | --- | --- |
| `XLU` utilities | The 10-year yield's, reversed | Every rule | Utilities are bought for their dividend, so they compete with bonds: yields up, utilities down. Stronger growth points the same way, as money leaves a defensive sector. So −1 on CPI, core PCE, the jobs report, retail sales, GDP, ISM and the Fed's statement; +1 on claims, whose signs are reversed; 0 where the yield has none (the euro-area flash, Germany's three) |
| `ITB` homebuilders | −1 | Inflation news only: CPI and core PCE | Hotter inflation means dearer mortgages, with nothing good to offset it. On growth news, higher rates and a stronger economy pull opposite ways, as [part 1](markets-people-feel.md) said, so 0 |
| `CORN`, `WEAT`, `SOYB`, `KC` | 0 | — | Weather and harvests set these prices; no agreed way, as gold has none |
| `UGA`, `UNG` | 0 | — | Unsigned as Brent and `XLE` are. Their days on the ISM survey are a result, not a reason |
| `T5YIE` the breakeven | 0, for now | — | See below |

- **The breakeven stays unsigned here.** It is the one with a link that holds in `follows`, but a
  call on it blocks the evening job for every market: FRED publishes its close a day late, so `score`
  prints `pending:` and the job stops before the triggers and the scoreboard
  ([the breakeven](breakeven.md)). No per-market exception is added for one market. Its sign lands
  with the next step, which teaches the evening grade to wait. That spec must not copy the 10-year
  yield's sign on the Fed's statement: a hawkish statement lifts yields and should lower expected
  inflation.
- **A guess follows the sign.** `score` accepts a guess only on a signed link of a flow `live` calls,
  so these markets become guessable on those eight links, not on ISM or the Fed's statement.
- **Ex-dividend days.** `XLU` drops about 0.7% on each one ([Precision](../precision.md)
  records it), which leans towards *down*, the way most of its signs point. If a link holds, step 2
  counts its graded calls on one, as a one-off with the dates from Yahoo's chart API (`events=div`);
  nothing stores them.

## The rule, fixed before anything is measured

- **Same tests, same bars:** step 4's *tracks* and rung 2's *holds*. A link that holds is called;
  no market gets a call by hand.
- **Every other cell unchanged.** On a copy of the real store, run each at the base commit and at
  this branch: `raw-move`, `surprise` and `predict` for every `--event`, `follows` for its four with
  and without `--after-the-day`, `score` and `scoreboard`. In the printed outputs drop `XLU`'s and
  `ITB`'s lines and the chance lines. In `data.json`, compared as JSON, remove the two markets' keys
  under each event's `surprise` and `walk_forward`, their entries in `ahead`, and `chance`,
  `written` and `watch`. Every diff must be empty. `raw-move` and `follows` use no sign, so
  theirs must be empty with those lines kept.
- **The merge waits.** The build merges only after the jobs report's evening run, 01:00 EET on
  2026-11-07, whatever it finds. Even a link that makes no call adds silent rows to the log, and that
  release is the first test of the euro and the 5-year yield.
- **Expected outcome, written first:**
  - `surprise`: `XLU` and `ITB` are at most *unclear* on CPI and core PCE against the verdict's baseline, and
    `XLU` *doesn't* on the growth releases, claims and the Fed's statement. Eight of the ten new links are on flows `live`
    calls; the other two are `XLU` on ISM and on the Fed's statement.
  - `predict`: no new link *holds*, so no new call, and at most one opens at all.
  - The rebuild stays under the 15-minute bar (270 s at #268).

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~The signs in `flows.py`; on a copy of the store, what each new link would do~~ **done** 2026-11-05 (PR #270) | The tests below pass; the procedure gives an empty diff; a table here lists each of the ten links, whether it opens, its record, and what `live` would log at that flow's next release (nothing for ISM and the Fed's statement); the rebuild time is here. Merged after 01:00 EET on 2026-11-07 |
| 2 | ~~Results here and in [MVP results](../mvp-results.md)~~ **done** 2026-11-05 (PR #271) | Each link's verdicts against the expected outcome; ex-dividend days counted if a link holds |

*Step 1, 2026-11-05 (PR #270), on a copy of the store of that morning, closes to 2026-11-04:*

| Link | Sign | Opens? | Record | `live` at its next release |
| --- | --- | --- | --- | --- |
| `XLU`, CPI | down | never | 0 calls | Silent, 2026-11-10 |
| `ITB`, CPI | down | never | 0 calls | Silent, 2026-11-10 |
| `XLU`, core PCE | down | never | 0 calls | Silent, unless it opens first |
| `ITB`, core PCE | down | never | 0 calls | Silent, unless it opens first |
| `XLU`, jobs report | down | never | 0 calls | Silent, 2026-11-06 |
| `XLU`, retail sales | down | never | 0 calls | Silent, unless it opens first |
| `XLU`, GDP | down | never | 0 calls | Silent, unless it opens first |
| `XLU`, claims | up | 2014-09-13, then closed | 1 of 2 | Silent, 2026-11-05 |
| `XLU`, ISM | down | never | 0 calls | Nothing; `live` does not call ISM |
| `XLU`, the Fed's statement | down | never | 0 calls | Nothing; `live` does not call the Fed |

- "Silent" with a date is `predict --actual` run with a throwaway log, on a surprise far from zero;
  the other three have no consensus for their next release yet.
- The procedure gave an empty diff on all 85 printed outputs and on `data.json`, but for one thing:
  `ahead`'s jobs-report consensus read 63 at the base's run and 65 at the branch's, a little later,
  with its two thresholds. That is Nasdaq's live calendar, which no sign reads. The walk-forward
  chance line goes from 70 cells to 80, 0.7 to 0.8 by chance.
- The scoreboard was rebuilt in 268 s alone, against 316 s at the base beside the test suite.

## Results

Measured 2026-11-05 on a copy of the store, closes to 2026-11-04, at PR #270.

**No new link holds, and none is open, so no new call.** Written down first, the signs fail by the
same bars every other market faces.

| Link | Against | `surprise` | Rank corr, p | Right on noticeable surprises |
| --- | --- | --- | --- | --- |
| `XLU`, CPI | The trend | *unclear* | 0.20, 0.0003 | 53% of 105 |
| `ITB`, CPI | The trend | *doesn't* | 0.09, 0.083 | 51% of 74 |
| `XLU`, core PCE | The consensus | *unclear* | −0.10, 0.90 | 60% of 15 |
| `ITB`, core PCE | The consensus | *doesn't* | −0.15, 0.97 | 53% of 15 |
| `XLU`, the jobs report | The trend | *doesn't* | 0.04, 0.22 | 48% of 201 |
| `XLU`, retail sales | The consensus | *doesn't* | −0.15, 0.98 | 45% of 91 |
| `XLU`, GDP | The consensus | *unclear* | −0.02, 0.54 | 62% of 13 |
| `XLU`, ISM | TradingView's forecast | *doesn't* | 0.09, 0.18 | 55% of 55 |
| `XLU`, claims | The consensus | *doesn't* | 0.00, 0.47 | 48% of 307 |
| `XLU`, the Fed's statement | The previous statement | *doesn't* | −0.02, 0.59 | 47% of 55 |

Against the expected outcome:

- **Met:** `XLU` and `ITB` at most *unclear* on CPI and core PCE; no link holds; one opens, `XLU` on
  claims in 2014, right on 1 of 2 and then closed; the rebuild, 268 s.
- **Wrong, one cell:** `XLU` on GDP is *unclear*, not *doesn't*, on a hit rate of 13 surprises and no
  correlation.

The nearest is `XLU` on CPI: a hotter print does go with weaker utilities, far beyond chance (p
0.0003), but the direction is right about as often as a coin. It is the same real but faint shape
the S&P 500 has. On retail sales utilities lean the other way, against the reason given for the sign;
a sign is not changed for that. With no link holding, the ex-dividend days are not counted.

In plain words: the reasons sound right and history does not back them enough to call. Utilities
and homebuilders stay what they were, markets whose moves are shown, and they join the links tested
at every release, so one can open later on its own record.

## How you know it is right

- A test pins every rule's signs for the two: `XLU` −1 in `EXPECTED_SIGN`, `NFP_EXPECTED_SIGN` and
  `FED_SENTIMENT_RULE`; +1 in `CLAIMS_EXPECTED_SIGN`; 0 in `EURO_EXPECTED_SIGN` and
  `GERMAN_SURVEY_EXPECTED_SIGN`. `ITB` −1 in `EXPECTED_SIGN` and 0 in all the others. A sign turned
  the wrong way would fail it, and would otherwise look like a market that doesn't track.
- The empty diff catches a sign leaking onto another market.
- `T5YIE` is 0 in every rule, pinned in the same test: a sign there would stop the evening job.

## What this part does not do

- No sign on the breakeven, the farm and fuel funds or coffee.
- No change to the evening job, to `live`, or to any bar. No new market or flow.

## Technical details

- **`flows.py`:** in `with_more_outcomes`, `"XLU": -signs["UST10Y / ZN"]`; its docstring gives the
  reason. `EXPECTED_SIGN = with_more_outcomes({...}) | {"ITB": -1}`, its comment saying why only
  there; `PCE_SURPRISE_RULE` and `CLAIMS_EXPECTED_SIGN` follow from the maps they already use.
- **`tests/test_event_flows.py`:** the signs test's `"XLU": 0` becomes the 10-year's sign reversed,
  its comment no longer says the markets people feel have no sign, and the test above is added.
- **Tests that count links:** each gains its flow's new links, not ten: CPI's fixtures two (11 → 13,
  `test_walk_forward.py`, `test_scoreboard.py` with its 0.13, `test_study_surprise.py`), retail's
  one, a silent `XLU` (`test_more_events.py`), with the exact lists in `test_walk_forward.py`.
  The other values in them are unchanged.
- **Docs:** this spec, row 19 (2c: utilities and homebuilders; the breakeven's sign moves to the next
  step), `docs/status.md`, and `docs/mvp-results.md` with step 2. The scoreboard as rebuilt, with the
  evening run after the merge.
