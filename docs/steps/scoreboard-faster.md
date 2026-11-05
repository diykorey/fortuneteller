# The scoreboard, faster

> Taken 2026-11-05 during the owner's "proceed with the project for the next 18 hours", before
> step 19's part 2c ([Roadmap](../roadmap.md#next-steps-in-order), row 19 amended). Terms are in
> the [Glossary](../glossary.md).

## The goal

**In plain words:** `fortuneteller scoreboard` takes 826 s alone at 25 markets, against the evening
job's bar of 15 minutes, and every market or sign added makes it slower. This step makes it about
three times faster without changing a single number anything prints.

## The way to reach it

- **Where the time goes:** 97% of a profile is permutation tests in pure Python, in `compare_moves`
  (the raw move), `track_pairs` (the surprise) and `is_open` (the walk-forward gate).
- **Each test is its own.** `stats.permutation_p` seeds a fresh generator per call, and each of the
  three depends only on its arguments and on module constants read in the worker (`MIN_EVENT_DAYS`,
  the `*_BAR`s, `GATE_PERMUTATIONS`). So they run on the machine's cores side by side and give the
  same numbers in the same order, on any number of cores. A test patching one of those constants
  would not reach the workers; none does today.
- **One pool, three loops.** `stats.parallel_map` maps a function over a process pool made once, in
  order, in batches of about a quarter of each core's share. Workers start fresh (`forkserver`)
  because the store runs threads; the pool takes every core. A pool that breaks (a worker killed)
  is dropped, so the next call makes a new one. The mapping stops at these three: a level up
  (`confident_calls`, `walk_forward` itself) would put pools inside pools, and `side_by_side`'s
  `track_pairs` stays serial.

## The rule, fixed before anything is measured

- **Every output as now**, on a copy of the store (`FT_DB_PATH`) with the main checkout's cache
  (`FT_CACHE_DIR`), base and branch run the same day: `raw-move` and `raw-move --week`,
  `surprise`, `follows` and `predict` for every flow, `score`, identical; the scoreboard's
  `data.json` identical but for `written`, `ahead` and `watch`, which are the day's and the
  network's.
- **`fortuneteller scoreboard` under 300 s** alone on this laptop (12 cores), timed with `time`.
  If it is not, the step stops and says so.
- **Expected outcome, written first** (from the prototype, 2026-11-04): every output identical,
  the scoreboard 271 s; `predict` for a flow at most a few seconds slower for starting the pool.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `stats.parallel_map` and the three loops | The tests pass unchanged, plus one that `parallel_map` keeps order and equals `map`; every output in the rule identical; the scoreboard under 300 s, its time and `predict`'s written here |

## What this step does not do

- No fewer permutations, no other generator, no numpy: each would change the p-values.
- No change to the evening job or its timeout.
