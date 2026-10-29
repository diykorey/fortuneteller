# The scoreboard

> Step 5 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-10-23 with the
> [plan update](../legend.md#the-target) that made the project an entertainment tool with a
> realistic approach. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** anyone with the link sees what the fortune teller has said and how it fared.

Everything measured so far reaches one person, through a popup on one laptop. At the end: a page
with every live call and its grade, every link's walk-forward record, every event's verdicts for
every market, and how many *moves* chance alone would give at these counts, rewritten by the
evening job. The first thing delivered beyond this laptop.

## The rule, fixed before anything is shown

- **The same numbers.** The page shows what the commands print, from the same functions: each
  verdict with its ratio and p, each record as counts, each band. A number the commands do not
  print does not exist on the page, with one exception below. The bars stay where they are.
- **The chance count.** Beside each grid: the cells tested, and how many would pass by chance at
  the bar (cells × 0.01 for p < 0.01). A fixed statement about the grid, never a correction of a
  verdict.
- **A call** shows its direction, its record as counts, its band and its grade (right, wrong,
  missed, silent); never a probability ([rung 6's gate](rung-6-delivery.md#the-rule-fixed-before-anything-is-delivered)).
- **Static.** One JSON file written by `fortuneteller scoreboard` and one HTML page that renders it
  in the browser: no server, no build, no framework, no state. Served by GitHub Pages from `docs/`
  on `main`, so the roadmap's script → web-service trigger stays unfired.
- **Written by the evening job**, after `score`, in the same pull request and only when `score` has
  something to commit: the page changes on the days the calls do. Measured 2026-10-23 on one flow:
  `raw-move` 18 s, `surprise` 44 s, `predict` 17 s; about ten minutes for every flow (*amended
  2026-10-23:* the whole command took 193 s for eight events, the ordinary days being counted once
  per flow rather than once per command).
- **Our numbers only.** The JSON holds verdicts, records and the calls already committed in
  `data/calls.csv`; no price or release series, the repository being public.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~`fortuneteller scoreboard` writes `docs/scoreboard/data.json` (each flow's raw-move and surprise verdicts for every market, each link's walk-forward record, the live calls with their grades, the chance counts, the data's last day); `docs/scoreboard/index.html` renders it; `docs/.nojekyll`~~ **done** 2026-10-23: on a copy of the real store, eight events (ISM not loaded yet) and six call rows in 193 s; the page checked in a browser, every grid and call shown; the first page committed from that run | On a test database the JSON's verdicts and records equal the lines `raw-move`, `surprise` and `predict` print; the page opened from a file shows every grid and call; a call row shows direction, counts, band and grade, and no `%` (*amended 2026-10-23:* no probability; a price market's band keeps its percent unit, as the popup prints it) |
| 2 | ~~The evening job runs it after `score`, in the score pull request~~ **built** 2026-10-26: `scripts/release-day.sh` runs `scoreboard` when `score`'s file differs and commits both; the tail run by hand in a scratch clone; GitHub Pages enabled on `main`, `/docs` (a repository setting, by hand: enabled 2026-10-27; the page answers at <https://diykorey.github.io/fortuneteller/scoreboard/>, and `docs/index.html` sends the bare address there) | The published page shows the latest score pull request's numbers; the [Legend](../legend.md)'s *Release* entry rewritten |
| 3 | Results: the first release day on the page, the jobs report of 2026-11-06 | Its call rows equal `data/calls.csv` and `score`'s grades |

## Technical details

`scoreboard` in `__main__.py` calls what the reports call (`study.measure_raw_moves`, the surprise
verdicts, the walk-forward replay, `study.read_calls` and `study.score_calls`) and writes plain
dicts with `json.dumps`. The page is one file, plain JavaScript, that builds the tables from the
data: the calls, newest day first, with the missed releases among them; then the walk-forward,
surprise and raw-move grids, one row per event and one column per market, the chance count and
the rule under each. *Amended 2026-10-23:* a browser will not fetch a file beside a page opened
from disk, so the command writes the page too, from the template `scoreboard.html` in the package
with the JSON embedded; `data.json` beside it is the same data for anyone else. A call's record is
the replay's calls before its day, which is what the popup counted. `FT_SCOREBOARD_DIR` moves the
output, for tests. `scripts/release-day.sh` gets one line after `score`. No new unit, no
daemon-reload.

## What this does not do

No history of earlier pages, no charts, no text that explains a number, no preview of a scheduled
statement (step 8), no per-visitor state, no probability.
