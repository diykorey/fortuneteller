# The Fed statement's tone

> Step 13 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen 2026-11-03 from its "later"
> list. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** when the Fed's statement sounds more hawkish than the last one, do yields and
the dollar rise and stocks fall that day?

The Fed's decisions move six of seven markets ([MVP results](../mvp-results.md)), but they have
no surprise test, because there is no free record of what the market expected. The statement's
text is free, and its tone can change while the rate does not. This step gives the Fed flow a
surprise: the statement's tone against the previous statement's. It is the roadmap's "a
statement's text read for its direction", measured with a published word list instead of a
language model (*chosen by the owner 2026-11-03*).

At the end, every Fed statement since 2000 has a tone. The Fed flow has a surprise rule, and
rung 1's surprise test and rung 2's walk-forward are run on it, with every bar unchanged.

## The way to reach it

Four things make this hard.

- **The word list must not be fitted to the texts.** It is taken verbatim from Apel and Blix
  Grimaldi, *The Information Content of Central Bank Minutes*, Sveriges Riksbank Working Paper 261
  (2012). It is written here, before any statement is fetched:
  - **Nouns,** each with a wildcard for compounds (`inflation*` matches "inflation expectations"):
    inflation, price, wage, oil price, cyclical position, growth, development. These are the
    paper's main list. Its extended nouns (employment, unemployment, recovery, cost) are left out,
    since "higher unemployment" is not hawkish.
  - **Hawkish adjectives:** high\*, strong\*, increasing, increase\*, fast\*.
  - **Dovish adjectives:** low\*, weak\*, decreasing, decreas\*, slow\*.
  - **A phrase** is an adjective immediately before a noun, case ignored ("higher inflation",
    "slower growth", "strong price pressures"). This is English word order; the paper searched
    Swedish.
  - **The tone** is the paper's Net Index: `hawk / (hawk + dove) − dove / (hawk + dove) + 1`,
    from 0 (all dovish) to 2 (all hawkish). A statement with no phrase has no tone.
  - "Cyclical position" and "development" are the paper's translations of Swedish words. They are
    kept, although the Fed rarely writes them.
- **The expected value is the last statement.** The market has read the previous statement, so
  the surprise is the tone minus the tone of the last statement that had one. This is a naive
  baseline, as the 12-month trend is for the releases. The baseline is called `the previous
  statement`.
- **The decision lands with the statement.** A cut and a dovish text come together, and the move
  may come from the cut. So the verdict is given on **holds** only: decisions after which the
  target rate did not change within `TARGET_EFFECT_DAYS`. All decisions are shown beside it as
  context. Between 2008-12 and 2015-12 the rate sat at the floor, so every decision is a hold,
  and the news was often the balance sheet, which the word list does not read.
- **Four page eras.** Statement links take four forms since 2000:
  - `/boarddocs/press/general/<year>/<day>/` (2000–2002);
  - `/boarddocs/press/monetary/<year>/<day>/default.htm` (2003–2005);
  - `/newsevents/press/monetary/<day>[ab].htm` (2006–2011);
  - `/newsevents/pressreleases/monetary<day>a.htm` (since 2012).

  Each decision's statement is taken from the Fed's year page or calendar by its link's
  "Statement" text, never by building the address. Only the statement's paragraphs are read, up
  to the vote line ("Voting for"). The vote list, implementation notes and media lines are cut
  the same way in every era. A stored decision since 2000-02-02 without exactly one statement
  stops the load. The pages are final, so they are cached.

## The rule, fixed before any tone is measured

- **Rung 1's surprise test, unchanged:** *tracks* when the rank correlation has the expected sign
  at p < 0.01 and the hit rate on noticeable surprises is at least 60%; *unclear* when one of the
  two holds.
- **The verdict:** tone on holds against the previous statement. Context: tone on every decision
  against the previous statement.
- **Expected signs, a hawkish surprise:**
  - up: the 10-year yield, the 5-year yield, the dollar;
  - down: the S&P 500, the Nasdaq, the euro.
  - The other ten markets have no sign: "does it follow?" only.
- **Noticeable:** the median absolute tone change over every statement, computed in step 1 from
  the tones alone and written here before any move is read.
- **Shared days left out,** as in step 4 (`alone`).
- **Walk-forward:** rung 2's replay on each signed link, *holds* at its bar. No live call. The Fed
  is not in `CONSENSUS_ROWS`, so `live` never calls it and the evening job is unchanged.
- **Chance, counted:** 6 signed links. At p < 0.01, about 0.06 *tracks* by chance.
- **Every existing scoreboard entry stays identical.** The page gains the Fed's surprise row and
  walk-forward row.
- **Expected outcome, written first:** no link tracks. A count of a dozen phrases misses what the
  market reads in a statement: forward guidance, the balance sheet, the dots, the press
  conference. Many statements may have no phrase at all. If more than half of the holds have no
  tone, the step says so and stops at step 1.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | `load-surprises` fetches every statement since 2000, scores its tone and stores the two measures against the previous statement; the Fed flow gets its surprise rule; `noticeable` and the counts written here | The tests below pass; on a copy of the store every existing scoreboard entry, `score` and `missed` are identical |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts and walk-forward against the expected outcome |

## How you know it is right

- A statement with "higher inflation", "slower growth" and "strong growth" has tone
  `2/3 − 1/3 + 1 = 4/3`. Words split by another word ("higher energy prices") do not count, and
  case is ignored.
- One page from each era: the text is cut at "Voting for", and the scored text holds no vote list.
- A year page with a decision and no "Statement" link stops the load, and so does one with two.
- The surprise is the difference from the last statement with a tone. A statement with none
  is skipped.
- A hold is a decision with no target change within `TARGET_EFFECT_DAYS`. A cut is not stored as
  a hold.
- In step 1, the five holds with the highest and the lowest tone are printed with their phrases
  and read by hand, before any move is measured.

## What this step does not do

No language model, no word list of our own, no new nouns, no press conference or minutes text, no
live call, no change to the Fed flow's events or to any other flow.

## Technical details

- **Source:** `sources.parse_fomc_statement_links(page) -> dict[date, str]` (from the year pages
  and the calendar) and `sources.statement_text(page) -> str`. Pages are cached under
  `cache_dir/fed/`.
- **Tone:** `expectations.statement_tone(text) -> tuple[float | None, list[str]]`, the tone and
  the phrases. The two word lists are constants beside it, citing the paper.
- **Measures:** `tone` (every decision) and `tone on holds`, against the `previous statement`
  baseline. They are stored in `surprises` like the other measures; the actual is the tone and
  the expected is the previous tone.
- **Rule:** `FED_FLOW` gets a `SurpriseRule` with
  `combinations=((TONE_HOLDS, PREVIOUS_STATEMENT), (TONE, PREVIOUS_STATEMENT))`, the six signs,
  `alone=True` and `predicted_from=PREVIOUS_STATEMENT`.
- **Docs:** `docs/schema.md` (the measures and the baseline), `docs/glossary.md` (tone, hold,
  Net Index), `docs/extending.md` if it lists the baselines, `docs/status.md`.
