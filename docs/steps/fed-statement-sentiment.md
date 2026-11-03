# The Fed statement's sentiment

> Step 14 of the [Roadmap](../roadmap.md#next-steps-in-order), chosen by the owner 2026-11-03
> after [step 13](fed-statement-tone.md) stopped. Terms are in the [Glossary](../glossary.md).

## The goal

**In plain words:** step 13's question again, with a word list built for the Fed's own
statements. When the statement reads stronger than the last one, do yields and the dollar rise
that day?

Step 13's list was made for Swedish minutes. It found a phrase in 19 of 226 Fed statements, so the
test never ran. Gardner, Scotti and Vega built a dictionary from the FOMC's statements of
2000–2020: *Words Speak as Loudly as Actions*, Finance and Economics Discussion Series 2021-074,
Federal Reserve Board, later in the Journal of Econometrics 231(2), 2022. It reads the Fed's own
phrasing ("the unemployment rate has declined", "inflation remains elevated"). It gives a number
to every statement that says anything about the economy.

At the end: every Fed statement since 2000 has the paper's sentiment index, and the Fed flow has
a surprise rule with its verdict, unless this step's stop rule fires.

## The way to reach it

- **The dictionary is the paper's, copied whole before any statement is scored.** Tables A5–A10
  of the working paper's appendix go verbatim into `data/seed/fomc_sentiment_dictionary.csv`, one
  row per entry, with the table, the entry, its score and its topic. The tables are:
  - A5: 33 topic keywords with a score of 1 or −1, in four topics: inflation, labor, output and
    financial.
  - A6–A8: modifiers per topic, scored 1, 0 or −1, including A8's long phrases.
  - A9: 16 rules for future policy.
  - A10: 14 rules for uninformative sentences.

  The paper built its dictionary by reading the same statements, but never from market moves.
  That is why it may be used here: it is fixed before any move is read.
- **The paper's own program is not published** ("available upon request"). So the choices below
  are this step's, written down now, before any statement is scored:
  - The text is lowercased and split into sentences at ". ", "; " and line ends.
  - An entry matches as a substring of the sentence, so "declin" matches "declined". "(space)" in
    an entry is a literal space: "ease (space)" is "ease ". "Soft (exclude software)" is "soft"
    not followed by "ware".
  - **Pairs:** each keyword occurrence pairs with the closest modifier of its topic in the same
    sentence, before or after it. Distance is counted in words, from the keyword's first word to
    the modifier's first word. On a tie, the modifier after the keyword wins. An A8 phrase counts
    as one modifier at its first word. A modifier that sits inside a longer matched modifier or
    keyword is not counted on its own.
  - A keyword with no modifier of its topic in the sentence scores nothing.
  - **The pair's score** is the keyword's score times the modifier's.
  - **A9 rules:** a rule's parenthesised parts must all match the sentence, each as a regular
    expression. Each rule that matches adds its score once per sentence.
  - **A10 rules** work the same way. A sentence matching any of them is left out of the four
    topics, but not out of the future-policy score.
  - **The index:** for each of the five topics, the sum of its scores divided by the square root
    of the statement's word count, the uninformative sentences left out of that count. The
    statement's sentiment is the sum of the five.
- **Reused from step 13:** the statements and their cut (`load-tone`'s fetch, link and body
  rules), the baseline (the decision just before; never reaching further back), holds, shared
  days left out, and the separate command, which the evening job does not run.
- **The paper's sign.** A positive index means a stronger economy or higher inflation, which
  points to tightening. So a positive surprise is read as hawkish, as in step 13.

## The rule, fixed before any sentiment is measured

- **Rung 1's surprise test, unchanged:** *tracks* when the rank correlation has the expected sign
  at p < 0.01 and the hit rate on noticeable surprises is at least 60%; *unclear* when only one of
  the two holds.
- **The verdict:** sentiment on holds against the previous statement. Context, not graded:
  sentiment on every decision, and the ten unsigned markets.
- **Expected signs, for a positive surprise:**
  - up: the 10-year yield, the 5-year yield, the dollar;
  - down: the euro;
  - S&P 500 and Nasdaq: *also* up. The paper's index is good news about the economy, and its
    own result is that stocks respond to it. This differs from step 13, and is written down
    first.
  - The dollar and the euro count as one finding.
- **Noticeable:** the median of the non-zero absolute surprises on holds. It is computed in step 1
  from the sentiment alone, before any move is read, and written here.
- **Too few, not no:** a signed link under 40 holds with a non-zero surprise and a move is *too
  few*. If every link is under 40, step 1 stops.
- **The hand read:** the five holds with the highest sentiment and the five with the lowest are
  printed with their scored pairs and read. It has one trigger, written now: if 3 or more of the
  10 have a pair from text outside the statement's body, the cut is fixed, and the 10 are read once
  more. Nothing else the read finds changes the dictionary, the matching or the rule.
- **A check against the paper, not a verdict.** The paper's Figure 2 shows the overall index
  below zero at the end of 2008 and above zero through 2018. In step 1 the index is printed for
  2008-12-16 and 2018-09-26. If both come out with the opposite sign, the step stops, as a
  misreading of the dictionary.
- **No live call; walk-forward graded only for a link that tracks.**
- **Chance, counted:** 6 signed links. At p < 0.01, about 0.06 *tracks* by chance.
- **Every other flow's scoreboard entry, the calls and *missed* stay identical.**
- **Expected outcome, written first:** the 10-year and 5-year yields are *unclear* at best. A
  statement's text arrives with the decision, the dots and, since 2011, the press conference, and
  the market reads those first. No link tracks; no call.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed dictionary; `load-tone` scores each statement's sentiment and stores the two measures against the previous statement; the counts, `noticeable`, the two dates' signs and the hand read written here; unless stopped, the Fed flow gets its surprise rule | The tests below pass; on a copy of the store every other flow's scoreboard entry, `score` and `missed` are identical |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts against the expected outcome |

## How you know it is right

- The paper's two worked examples: "the unemployment rate has declined" scores +1, and "labor
  market conditions have deteriorated" scores −1.
- A sentence with "inflation" and two modifiers chooses the nearer one, and the one after it on a
  tie. "Software" is not "soft". "Moderated" is not "moderate (space)".
- An A9 rule scores a sentence only when every part matches. An A10 sentence is left out of the
  four topics and of the word count.
- The seed file has every row of Tables A5–A10, counted against the paper (A5: 33, A9: 16, A10:
  14). Each score is −1, 0 or 1, and each topic is one of the five.
- A statement's index is the sum of its topics over the square root of its informative words.

## What this step does not do

No dictionary of our own, no reweighting, no language model, no minutes or press conferences, no
live call, no change to the evening job.

## Technical details

- **Seed:** `data/seed/fomc_sentiment_dictionary.csv`, with columns `table,entry,score,topic`,
  documented in `docs/legacy/data/` style beside the other seeds and listed in `docs/schema.md`'s
  seed section.
- **Sentiment:** `expectations.statement_sentiment(text) -> tuple[float | None, list[str]]` returns
  the index and the scored pairs. It is `None` when the statement has no informative word.
- **Command:** `load-tone` scores with the sentiment in place of step 13's tone. The step 13 tone
  stays in the code, since its count is the record of that step.
- **Rows and rule, unless stopped:**
  - `surprises` gets the measures `sentiment` and `sentiment_holds`, against the baseline
    `previous_statement`, written by `load-tone`. `load_surprises` skips the Fed flow and keeps
    those rows.
  - `PREVIOUS_STATEMENT` joins `EXPECTATION_SOURCES` for its label.
  - `study._flow_pairs` reads a decision's month from its day.
  - `FED_FLOW` gets a `SurpriseRule` with `combinations=((SENTIMENT_HOLDS, PREVIOUS_STATEMENT),
    (SENTIMENT, PREVIOUS_STATEMENT))`, the six signs, `noticeable` from step 1, `alone=True` and
    `predicted_from=PREVIOUS_STATEMENT`.
- **Docs:** `docs/schema.md`, `docs/glossary.md` (sentiment index, keyword, modifier),
  `docs/status.md`, the roadmap's row.
