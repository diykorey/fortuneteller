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
phrasing ("the unemployment rate has declined", "inflation remains elevated").

At the end: every Fed statement since 2000 has the paper's sentiment index, and the Fed flow has
a surprise rule with its verdict, unless this step's stop rule fires.

## The way to reach it

- **The dictionary is the paper's, copied whole before any statement is scored.** Tables A5–A10
  of the working paper's appendix go verbatim into `data/seed/fomc_sentiment_dictionary.csv`. Each
  row holds the table, the entry, its score and its topic. Where the paper's prose counts differ
  from its tables, the tables govern. The tables are:
  - A5: 33 keywords, in four topics (`inflation`, `labor`, `output`, `financial`);
  - A6: 88 modifiers, and A7: 98, each scored 1, 0 or −1 for one topic;
  - A8: 33 long phrases;
  - A9: 16 future-policy rules, topic `policy`;
  - A10: 14 rules for uninformative sentences, score 0, topic `uninformative`.

  The paper built the dictionary by reading the same statements, but never from market moves.
  That is why it may be used here.
- **The paper's own program is not published** ("available upon request"). So the choices below
  are this step's, written down now, before any statement is scored. None of them may change after.
  - **Text.**
    - A statement's paragraphs are joined into one line, so an inline tag cannot split a
      sentence.
    - It is lowercased. "U.S." becomes "us", and curly apostrophes become straight.
    - Sentences end at ".", "?" or ";" followed by a space, or at the text's end.
  - **Normal form.** In a sentence, every character that is not a letter, a digit or an
    apostrophe becomes a space. Runs of spaces become one, and one space is added at each end.
    - Each A5–A8 entry gets the same treatment, without the space at each end; "(space)" in an
      entry is a space there. So "moderate (space)" matches "moderate." but not "moderated", and
      "declin" matches "declined".
    - Hyphens become spaces on both sides, so "long-term" matches "long term".
    - "Soft (exclude software)" is "soft" not followed by "ware".
    - A **word** is a run between spaces in the normal form.
  - **Matches.** Every entry of A5, A6, A7 and A8 is found as a substring of the normal form that
    starts at the start of a word. So "unemployment" is never "employment", "decrease" is never
    "ease ", and "elaborate" is never "labor".
    - A match's **span** is its text without the spaces at its ends. Where two spans overlap, the
      longer is kept; at equal length, the one that starts first. So "job gains" is never also
      "gains", and "investment spending" never also "spending".
    - Matches with the same span are all kept, one per topic: " low" for output and "low" for
      labor and inflation are one stretch of text, scored in each topic.
    - A match's **position** is the index of the word it starts in.
  - **Pairs.** Each A5 keyword pairs with the closest A6/A7 modifier of its topic in the same
    sentence, before or after it, by the difference in positions. On a tie, the modifier after
    the keyword wins. The pair scores the keyword's score times the modifier's. A keyword with no
    modifier of its topic in its sentence scores nothing.
  - **A8 phrases stand alone.** Each scores its own score in its topic, because the phrase
    already holds its subject. Words inside it are matched by nothing else.
  - **A9 and A10 rules.**
    - A rule written as parenthesised parts joined by `)|(` is split there. Every part must
      match the sentence, each as a regular expression searched in the normal form, with its `|`
      meaning "or". A rule without parentheses is one part.
    - A rule is only lowercased, with its curly apostrophes made straight, so "today’s" matches
      and the regular expression stays whole.
    - A9: each rule that matches adds its score to `policy`, once per sentence.
    - A10: a sentence matching any rule is uninformative. It is left out of the four topics and
      of the word count, but not out of `policy`.
  - **The index.** Let N be the number of words in the informative sentences. Each of the five
    topics scores the sum of its scores over √N. The statement's sentiment is the sum of the five.
    With N = 0 there is no sentiment.
- **The surprise is the change; the paper uses the level.** The paper's footnote 32 turns down
  differencing the index and uses its level, with yields over 30 minutes. For the level it finds
  the 5-year yield significant and the 10-year not (Table 5). Here, as in step 13, the surprise
  is the change from the previous statement, because the market has read that one, and the move
  is the day's. So the paper's evidence is not borrowed for this test.
- **Reused from step 13:** the statements and their cut, the baseline (the decision just before;
  never reaching further back), holds, and shared days left out. A command of its own,
  `load-sentiment`, sits beside `load-tone`, which keeps printing step 13's counts. The evening
  job runs neither.

## The rule, fixed before any sentiment is measured

- **Rung 1's surprise test, unchanged:** *tracks* when the rank correlation has the expected sign
  at p < 0.01 and the hit rate on noticeable surprises is at least 60%; *unclear* when only one of
  the two holds.
- **The verdict:** sentiment on holds against the previous statement. Context, not graded:
  sentiment on every decision, and the twelve unsigned markets.
- **Expected signs, for a positive surprise:** a stronger economy or higher inflation, which
  points to tightening.
  - up: the 10-year yield, the 5-year yield, the dollar;
  - down: the euro.
  - The dollar and the euro count as one finding.
  - Stocks are unsigned. Good news about the economy and a tighter path pull them opposite ways,
    and the paper does not test them on statement days.
- **Noticeable:** the median of the non-zero absolute surprises on holds. It is computed in step 1
  from the sentiment alone, before any move is read, and written here.
- **Too few, not no:** a signed link under 40 holds with a non-zero surprise and a move is *too
  few*. If every link is under 40, step 1 stops.
- **Checks against the paper. Any one failing stops step 1, as a misreading of the dictionary:**
  - The paper's Figure 2 shows the overall index below zero at the end of 2008 and above zero
    in 2018. The index of 2008-12-16 must be below zero, and that of 2018-09-26 above zero.
  - Every statement's index lies between −1 and 1, as the paper's does.
  - The statements from 2000-02-02 to 2019-12-11 number within 10 of the paper's 166.
- **The hand read:** the five holds with the highest sentiment and the five with the lowest are
  printed with their pairs and read. It has one trigger, written now: if 3 or more of the 10 have
  a pair from text outside the statement's body, the cut is fixed, and the 10 are read once more.
  Nothing else the read finds changes the dictionary, the matching or the rule.
- **No live call; walk-forward graded only for a link that tracks.**
- **Chance, counted:** 4 signed links, 3 findings. At p < 0.01, about 0.04 *tracks* by chance.
- **Every other flow's scoreboard entry, the calls and *missed* stay identical.**
- **Expected outcome, written first:** the 10-year and 5-year yields are *unclear* at best, the
  dollar and the euro *doesn't*. The text arrives with the decision, the dots and, since 2011,
  the press conference, and a day's move holds all of them. The paper finds even the level
  insignificant for the 10-year yield over 30 minutes. No link tracks; no call.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The seed dictionary; `load-sentiment` scores each statement; the counts, `noticeable`, the three checks and the hand read written here; then, unless stopped, the stored measures and the Fed flow's surprise rule | The tests below pass; on a copy of the store every other flow's scoreboard entry, `score` and `missed` are identical |
| 2 | Results here and in [`mvp-results.md`](../mvp-results.md) | The verdicts against the expected outcome |

## How you know it is right

- **The paper's two worked examples, through `sentence_pairs(sentence)`:** "the unemployment
  rate has declined" gives one labor pair scoring +1, and "labor market conditions have
  deteriorated" gives one scoring −1.
- **Pairing:**
  - "inflation" with two inflation modifiers takes the nearer one, and the one after it on a tie.
  - "Software" is not "soft", "moderated" is not "moderate (space)", "unemployment" yields
    no "employment", and "decrease" no "ease ".
  - "The unemployment rate has remained low" gives a labor pair of +1 though " low" is also an
    output modifier.
  - An A8 phrase scores alone.
- **Rules:**
  - An A9 rule with parts scores a sentence only when every part matches, and "(complete|moderate)"
    matches either word.
  - "Be patient" is a one-part rule.
  - An A10 sentence is left out of the four topics and of N, but still scores `policy`.
  - "Long-term", "U.S." and a curly apostrophe match their entries.
- **The index:** the topics' sums over √N, and no index for N = 0.
- **The seed file:** 282 rows, 33, 88, 98, 33, 16 and 14 by table. Each score is −1, 0 or 1, and
  each topic is one of the six.

## What this step does not do

No dictionary of our own, no reweighting, no language model, no minutes or press conferences, no
live call, no change to the evening job.

## Technical details

- **Seed:** `data/seed/fomc_sentiment_dictionary.csv`, columns `table,entry,score,topic`. It is
  described in `docs/schema.md`'s seed list. The other seeds are database tables; this one is read
  by `expectations` alone.
- **Code:**
  - `expectations.sentence_pairs(sentence) -> list[tuple[str, int, str]]` gives each topic, score
    and matched text.
  - `expectations.statement_sentiment(text) -> tuple[float | None, list[str]]` gives the index
    and its pairs, each written "topic score: matched text".
  - `flows.fed_statements(api_key, cache_dir, con) -> tuple[list[Event], dict[int, str],
    set[int]]` is step 13's fetch, cut and holds since `TONE_FROM`: the events, each one's text,
    and the holds. `load_tone` and `load_sentiment` share it.
  - `flows.load_sentiment(api_key, cache_dir, con) -> SentimentLoad`, with the fields of
    `ToneLoad`: the surprises, each statement's index and pairs, and the holds.
  - `load-sentiment` prints as `load-tone` does: the counts, the signed links, `noticeable`, then
    each check with "pass" or "fail", then the 5 + 5 holds with their pairs.
- **Unless stopped:**
  - `surprises` gets the measures `sentiment` and `sentiment_holds`, against the baseline
    `previous_statement`. The actual is the index, the expected the previous index.
  - `load-sentiment` replaces `measure IN ('sentiment', 'sentiment_holds')`.
  - `load_surprises` skips the Fed flow and replaces `measure NOT IN ('sentiment',
    'sentiment_holds')`.
  - `PREVIOUS_STATEMENT` joins `EXPECTATION_SOURCES` with the label "the previous statement".
    Its `expectations` returns nothing.
  - `study._flow_pairs` reads the month from the event's day only when `detail` does not begin
    with a year and month (`YYYY-MM`), so no other flow changes, the weekly claims included.
  - `FED_FLOW` gets a `SurpriseRule` with `combinations=((SENTIMENT_HOLDS, PREVIOUS_STATEMENT),
    (SENTIMENT, PREVIOUS_STATEMENT))`, the four signs, `noticeable` from step 1 (`step` its value
    to two places), `alone=True` and `predicted_from=PREVIOUS_STATEMENT`.
- **Docs:** `docs/schema.md`, `docs/glossary.md` (sentiment index, keyword, modifier),
  `docs/status.md`, the roadmap's row.
