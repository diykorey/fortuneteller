# The Fed statement's tone

> Step 13 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-03 from its "later"
> list. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when the Fed's statement sounds more hawkish than the last one, do yields and
the dollar rise that day?

The Fed's decisions move six of seven markets ([MVP results](../mvp-results.md)), but they have
no surprise test, because there is no free record of what the market expected. The statement's
text is free, and its tone can change while the rate does not. This step gives the Fed flow a
surprise: the statement's tone against the previous statement's. It is the roadmap's "a
statement's text read for its direction", measured with a published word list instead of a
language model (*chosen by the owner 2026-11-03*).

At the end, every Fed statement since 2000 has a tone. The Fed flow has a surprise rule, and
rung 1's surprise test is run on it, with every bar unchanged. A *no* measures this word list,
not the Fed's tone.

## The way to reach it

Four things make this hard.

- **The word list must not be fitted to the texts.** It comes from Apel and Blix Grimaldi, *The
  Information Content of Central Bank Minutes*, Sveriges Riksbank Working Paper 261 (2012), its
  main specification and appendix. It is written here before any statement is fetched:
  - **Nouns:** inflation\*, price\*, wage\*, oil price\*, cyclical position\*, growth\*,
    development\*.
  - **Hawkish adjectives:** high\*, strong\*, increasing, increase\*, fast\*.
  - **Dovish adjectives:** low\*, weak\*, decreasing, decreas\*, slow\*.
  - *Amended 2026-11-03, before any statement was fetched:* the paper's extended nouns
    (employment, unemployment, recovery, cost) are left out, because "higher unemployment" is
    not hawkish. This is our own choice, not the paper's.
  - "Cyclical position" and "development" are the paper's translations of Swedish words. They are
    kept, although the Fed rarely writes them.
- **How a phrase is matched.**
  - The text is lowercased and split into words, which are runs of letters.
  - A phrase is an adjective word immediately followed by a noun word, with nothing but spaces or
    a hyphen between them. A comma or full stop breaks it.
  - `x*` matches a word that starts with `x`: `low*` matches "lower" but not "slow", and
    `inflation*` matches "inflationary". A word without `*` must match exactly.
  - "Oil price" is two words. "Higher oil prices" counts once, as oil price.
  - Every occurrence counts.
  - **The tone** is the paper's Net Index: `hawk / (hawk + dove) − dove / (hawk + dove) + 1`, from
    0 (all dovish) to 2 (all hawkish). A statement with no phrase has no tone.
  - The Fed often writes the noun first ("inflation remains elevated"), and "elevated" is not on
    the list. Those sentences are not read. This is the list's limit, and it is kept.
- **The expected value is the previous statement.** The market has read it, so the surprise is
  the tone minus the tone of the statement of the decision just before. If either has no tone,
  there is no surprise; the step never reaches further back. The baseline is called `the previous
  statement`.
- **The decision lands with the statement.** A cut and a dovish text come together, and the move
  may come from the cut. So the verdict is given on **holds** only. A hold is a decision after
  which the target rate (`TARGET_RATE_SERIES`, from FRED) on the decision day plus
  `TARGET_EFFECT_DAYS` equals the target on the day before. The 2008-12-16 decision moved the
  target from 1.00 to the range's top, 0.25, so it is a cut. Every decision is shown beside the
  holds, as context. Between 2008-12 and 2015-12 the rate sat at the floor, so every decision was a
  hold, and the news was often the balance sheet, which the list does not read.

## The rule, fixed before any tone is measured

- **Rung 1's surprise test, unchanged:** *tracks* when the rank correlation has the expected sign
  at p < 0.01 and the hit rate on noticeable surprises is at least 60%; *unclear* when only one of
  the two holds.
- **The verdict:** `tone on holds` against the previous statement. Context, not graded: `tone` on
  every decision, and the ten unsigned markets.
- **Expected signs, for a hawkish surprise:**
  - up: the 10-year yield, the 5-year yield, the dollar;
  - down: the S&P 500, the Nasdaq, the euro.
  - The yields and the dollar are the question. "Strong growth" scores hawkish but is also good
    news for stocks, so the stocks' sign is the policy reading only. A *no* on stocks beside a
    *tracks* on yields is read as the growth message, not as policy.
- **Noticeable:** the median of the non-zero absolute surprises on holds. It is computed in step 1
  from the tones alone, before any move is read, and written here. A zero surprise is never
  noticeable.
- **Shared days are left out,** as in step 4 (`alone`).
- **Stop rule.** Step 1 stops, with no rule given to the Fed flow and no step 2, if fewer than 40
  holds have a non-zero surprise. The count is written here.
- **The hand read.** In step 1, the five holds with the highest tone and the five with the lowest
  are printed with their phrases and read. The read can stop the step. It cannot change the list.
- **No live call.** The Fed is not in `CONSENSUS_ROWS`, so `live` never calls it. The walk-forward
  the scoreboard runs on every rule is shown, but it is graded only for a link that tracks.
- **Chance, counted:** 6 signed links. At p < 0.01, about 0.06 *tracks* by chance.
- **Every existing scoreboard entry stays identical.** The page gains the Fed's surprise row and
  walk-forward row.
- **Expected outcome, written first:** no link tracks. A count of a dozen phrases misses what the
  market reads in a statement: forward guidance, the balance sheet, the dots, the press
  conference.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `load-tone` fetches every statement since 2000, scores its tone and stores the two measures against the previous statement; the stop rule's count, `noticeable` and the hand read written here; then, unless stopped, the Fed flow gets its surprise rule | The tests below pass; on a copy of the store every existing scoreboard entry, `score` and `missed` are identical |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts against the expected outcome |

## How you know it is right

- A statement with "higher inflation", "slower growth" and "strong growth" has tone
  `2/3 − 1/3 + 1 = 4/3`. Two occurrences of "higher inflation" count twice. "Higher energy
  prices", "low. Growth" and "slow" read as "low" do not count.
- One page from each era is cut to the statement's body. The scored text holds no vote list, no
  navigation and no implementing note.
- A decision with no "Statement" link, or with two, stops the load.
- A statement whose previous one has no tone has no surprise.
- A cut, a hike and the 2008-12-16 decision are not holds, and an unchanged target is.
- `load-surprises` leaves the tone rows in place, and it never fetches a Fed page.

## What this step does not do

No language model, no word list of our own, no press conference or minutes text, no live call, no
change to the Fed flow's events or to any other flow, and no change to the evening job.

## Technical details

- **A command of its own: `load-tone`,** run by hand and not by the evening job. The nightly
  `load-surprises` would otherwise depend on federalreserve.gov, and Fed events carry no period.
  - `flows.load_surprises` skips `FED_FLOW`.
  - Its `replace_rows` filter keeps the rows whose measure is `tone` or `tone on holds`.
- **Source:**
  - `sources.parse_fomc_statement_links(page) -> dict[date, str]` reads the year pages (2000–2020)
    and the calendar. It takes the HTML link whose text is "Statement".
  - `sources.statement_text(page) -> str` keeps the release body and cuts at "Voting for" when it
    is there. Statements before 2002, and some unscheduled ones, have no vote line.
  - The statement pages are cached under `cache_dir/fed/`; the year pages and the calendar are not.
  - Every decision stored since 2000-02-02 must have exactly one link, or the load stops.
- **Tone:** `expectations.statement_tone(text) -> tuple[float | None, list[str]]` returns the tone
  and the phrases. The word lists are constants beside it, with the paper cited.
- **Holds:** `load-tone` fetches the target series as `load_fomc_decisions` does.
- **Rows:** in `surprises`, measures `tone` and `tone on holds`, baseline `previous statement`.
  The actual is the tone, the expected is the previous tone, and `known_at` is the previous
  decision's time.
  - `PREVIOUS_STATEMENT` joins `EXPECTATION_SOURCES` for its label. Its `expectations` returns
    nothing, because `load-tone` writes the rows.
- **The month:** `study._flow_pairs` reads a row's month from `detail`. A Fed decision's detail is
  "scheduled meeting" or "unscheduled", so the month is read from the event's day when `detail`
  is not a month.
- **Rule:** `FED_FLOW` gets a `SurpriseRule` with:
  - `combinations=((TONE_HOLDS, PREVIOUS_STATEMENT), (TONE, PREVIOUS_STATEMENT))`;
  - the six signs and `noticeable` from step 1, with `step` its value;
  - `alone=True`;
  - `predicted_from=PREVIOUS_STATEMENT`.
- **Docs:**
  - `docs/schema.md`: the measures and the baseline;
  - `docs/glossary.md`: tone, hold, Net Index;
  - `docs/extending.md`, if it lists the baselines;
  - `docs/status.md`.
