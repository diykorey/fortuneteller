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
  `raw-move` 18 s, `surprise` 44 s, `predict` 17 s; about ten minutes for every flow.
- **Our numbers only.** The JSON holds verdicts, records and the calls already committed in
  `data/calls.csv`; no price or release series, the repository being public.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `fortuneteller scoreboard` writes `docs/scoreboard/data.json` (each flow's raw-move and surprise verdicts for every market, each link's walk-forward record, the live calls with their grades, the chance counts, the data's last day); `docs/scoreboard/index.html` renders it; `docs/.nojekyll` | On a test database the JSON's verdicts and records equal the lines `raw-move`, `surprise` and `predict` print; the page opened from a file shows every grid and call; a call row shows direction, counts, band and grade, and no `%` |
| 2 | The evening job runs it after `score`, in the score pull request; GitHub Pages enabled on `main`, `/docs` (a repository setting, by hand: not enabled as of 2026-10-23) | The published page shows the latest score pull request's numbers; the [Legend](../legend.md)'s *Release* entry rewritten |
| 3 | Results: the first release day on the page, the jobs report of 2026-11-06 | Its call rows equal `data/calls.csv` and `score`'s grades |

## Technical details

`scoreboard` in `__main__.py` calls what the reports call (`study.measure_raw_moves`, the surprise
verdicts, the walk-forward replay, `study.read_calls` and `study.score_calls`) and writes plain
dicts with `json.dumps`. The page is one file, plain JavaScript, that fetches `data.json` and
builds the tables: the calls, the links that hold, the event × market grids. `scripts/release-day.sh`
gets one line after `score`. No new unit, no daemon-reload.

## What this does not do

No history of earlier pages, no charts, no text that explains a number, no preview of a scheduled
statement (step 8), no per-visitor state, no probability.
