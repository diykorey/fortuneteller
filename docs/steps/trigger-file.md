# A trigger arrives

> Step 18, part 2, of the [Roadmap](../roadmap.md#next-steps-in-order), after
> [part 1](after-the-day.md), whose spec fixed what this part must do. Taken 2026-11-04 during the
> owner's "proceed with the project for the next 18 hours". Terms are in the
> [Glossary](../glossary.md).

## The goal

**In plain words:** the owner reads that the Fed cut, or that the jobs report beat the consensus,
and writes it into a file. The tool answers with what followed every past event of that kind from
the close of the reaction day: on each market, over the next day, week and month, *up*, *down*,
*about the same* or *can't say*, with the counts. It logs the answer and grades it when the span
ends.

It is the [Legend](../legend.md#the-target)'s headline answered, with a file standing in for the
news (step 20 reads the news later). Part 1 found that nothing holds from the next close, so most
answers will be *can't say*. They are shown and counted all the same; this part builds the way an
answer is dated, logged and graded, which any later answer needs.

At the end: `fortuneteller triggers` reads `data/triggers/`, prints each trigger's answers and
grades, and keeps them in `data/trigger-log.csv`.

## The way to reach it

- **The file.** A CSV under `data/triggers/`, any name ending `.csv`, header `flow,day,kind`, one
  row per trigger:
  - `flow`: `fomc`, `nfp`, `retail` or `cpi`, the flows `follows` answers;
  - `day`: the event's day in New York, `YYYY-MM-DD`;
  - `kind`: `cut`, `hold` or `hike` for the Fed, `above`, `as expected` or `below` for a release.

  Each row is dated by GitHub's `merged_at` for the pull request that added its file, found as a
  guess's is (`guess_files`, `merged_at`); a file edited later is read as it was added. A file that
  cannot be read, or has another header, voids its own rows only, as `read_guesses` does.
- **The event and its kind come from the store.** A trigger is matched to the flow's stored event
  whose `release_date` is its day. Its kind is read as part 1 reads it: `release_kinds` for a
  release; `fed_kinds` with FRED's target rate for the Fed, asked only when an `fomc` trigger
  exists. With no FRED key then, `triggers` prints `_fred_key`'s message and exits 1; a FRED or
  GitHub failure stops the run, so an outage never voids a trigger. A trigger is:
  - *void*, with the reason, if its flow is not one of the four; its kind is not one of its flow's;
    it repeats a flow and day already filed (the earliest merged counts, then by path and line);
    its file reached `main` without a pull request; the flow has no event that day though a later
    one is stored; or the stored kind differs (`the stored kind is above, not below`);
  - *waiting* while the event or its kind is not stored (FRED has the Fed's new rate three days on,
    a release's kind waits for `load-surprises`).
- **The deadline, per market.** A trigger counts on a market only if merged before
  `datetime.combine(first_reaction_day(event, series), series.close, tzinfo=series.zone)`. After a
  14:00 New York Fed decision it is 16:00 New York that day for the S&P 500, and the next day for
  gold and the DAX. For EUR/USD (00:00 London) a US event on day *D* has *D*+1 at 00:00 London;
  for bitcoin, *D* at 23:59 UTC. A reaction day with no close only makes the rule stricter. Merged
  at or after it: *late*, void on that market, printed with the merge time, not answered.
- **The answer, as part 1 replays it.** Once the reaction close is stored, each span is answered as
  part 1's walk-forward answers that event (`after=True` always): from the flow's earlier events of
  the same kind whose span from their reaction close ended on or before this reaction close, and
  the base spans ended by then. *Too few* under 10 earlier events.
- **Left out, as in part 1.** The non-overlap walk runs over the flow's events oldest first,
  counting an earlier event whose span is still open as kept, ending at its *c*-th close after its
  reaction close. If the last event kept before the trigger ends after the trigger's reaction
  close, the trigger is *left out*. For `follows` this changes nothing: an event after an open span
  has an open span too, and neither is counted. One case can differ from the later replay: an open
  span that turns out to have a hole would not have been kept. [Precision](../precision.md) records
  it.
- **The log.** `data/trigger-log.csv`, header
  `file,line,flow,day,kind,market,span,merged_at,answer,chance,up,same,down,cut,outcome,result`:
  - one row per trigger, market and span answered (*up*, *about the same*, *down*, *can't say*,
    *too few* or *left out*); void, late and waiting are printed, not logged;
  - `line` the trigger's line in its file; `merged_at` UTC, ISO 8601; `chance` empty when there is
    none; `up`, `same`, `down` the earlier events' counts and `cut` the base's cut in the market's
    unit, all empty for *too few* and *left out*;
  - `outcome` (`up`, `about the same`, `down`, or `hole`) filled when the span's last close is
    stored, by the cut in the row; `result` `right` or `wrong` for an answer of the three, else
    empty;
  - a row is added only for a (`file`, `line`, `market`, `span`) not yet in the log, and a run
    fills only empty `outcome` and `result` fields: a filled field is never changed;
  - rows in the order of files by path, then line, then `MVP_PRICE_SERIES`, then `SPANS`.
- **The events not filed.** For each flow, the events whose `release_date` is on or after the
  earliest day among its triggers that are answered on some market, less those a trigger answers on
  some market. Each is printed `not filed: <flow> <day>`. Void, late and waiting triggers neither
  start the window nor file an event.
- **Why a file.** Roadmap row 18 asks for one, standing in for the news that step 20 reads into the
  same rows, and the unscheduled flows have no calendar. Every scheduled release could be graded
  with no file, which would remove the owner's choice of what to file. The file stays, and the
  events not filed show that choice.

## The rule, fixed before any trigger is graded

- Part 1's kinds, spans, cut, bars and answer, unchanged. The deadline, the void reasons and the log
  rules above, unchanged by what any trigger shows.
- **Expected outcome, written first:** most answers *can't say* or *too few*; on the Fed, whose
  cuts and hikes have few events, *too few* on most markets.
- No trigger is committed under `data/triggers/` by this work: the first is the owner's.
- `triggers` prints no line starting `pending:`, which the evening job reads.
- Every existing output is unchanged: `score`, `data/calls.csv`, the scoreboard, `follows`.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `triggers`: read, void, wait, answer, log, grade | The tests below pass. On a copy of the store, `answer_triggers` given a trigger for the jobs report of 2026-10-02, merged 2026-10-02 at 12:00 UTC, returns 48 rows, 16 markets by 3 spans, every one graded or *can't say*, *too few* or *left out* |
| 2 | The evening job runs `triggers`, and commits the log when it or the score changed | A run of the job on a copy commits the log |
| 3 | Results: the first triggers graded, recorded here and in [MVP results](../mvp-results.md) | Waits for the owner's first trigger and its spans to end |

## How you know it is right

- A trigger merged one minute before the S&P 500's reaction close is answered there; one merged at
  that close is *late* there, and answered on gold, which reacts the next day.
- A trigger whose kind differs from the stored kind is void with both kinds named; one whose kind
  is not stored yet is *waiting*; a repeat merged later is void.
- For every past event on made-up closes, the answer logged equals part 1's walk-forward answer at
  that event, on every span, and *left out* exactly where part 1 leaves the event out, including a
  month whose previous span was still open at the reaction close.
- Changing every close after the reaction close changes no answer. A later run fills the outcome
  and changes no other field; a run after a close is revised changes nothing filled; a span with a
  hole is logged `hole` and not graded.
- `follows` prints the same lines as before (`test_the_fed_table_is_unchanged` and the `follows`
  tests).
- An event of the flow after its first answered trigger, with none of its own, is listed not filed.

## What this part does not do

- No news is read (step 20); no new flow, market or span; no page (later, once triggers exist).
- `live`, `score` and `data/calls.csv` are unchanged; a trigger is not a call.
- The owner sees the reaction day before filing, and on a half-day the deadline is the usual close.
  [Precision](../precision.md) records both, with step 20 as the trigger.

## Technical details

- **`study.py`:**
  - `kept_keys(decisions, closes, c, after) -> (kept, overlapped, holes, reacted)`: part 1's
    non-overlap walk in close indices, `kept` the (kind, reaction close index) of each kept event,
    open spans included. `follow_market` uses it and counts only the kept whose span is complete,
    so its output is byte for byte as now.
  - `answer_as_of(earlier, before, spans, by_end, first)`, the answer and base from the spans of
    `earlier` ended on or before `before`; `answer_before` calls it with its own arguments.
  - `Trigger`, `read_triggers(files)`, and `answer_triggers(triggers, merged, events, kinds, closes,
    log) -> (rows, printed lines)`, pure, beside the guesses' functions.
- **`__main__.py`:** `triggers` reads the store and FRED, calls `answer_triggers`, prints, and
  rewrites the log. `config.py` gains `triggers_dir` and `trigger_log_path`.
- **Tests:** `tests/test_triggers.py`, with the merge time passed in, as the guesses' tests do.
- **Docs:** this spec, `docs/precision.md`, the glossary (*trigger*), `docs/status.md`, and row 18.
