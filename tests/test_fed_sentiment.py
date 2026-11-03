import csv
import math
from collections import Counter
from datetime import date
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, expectations, flows, study
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.expectations import PREVIOUS_STATEMENT, sentence_pairs, statement_topics
from fortuneteller.models import Surprise
from fortuneteller.sources import FomcDecision


def test_the_paper_s_worked_examples_score_one_pair_each() -> None:
    # given the paper's two worked phrases

    # when each is scored
    declined = sentence_pairs("The unemployment rate has declined.")
    deteriorated = sentence_pairs("Labor market conditions have deteriorated.")

    # then each is one labor pair, the first good news and the second bad
    assert declined == [("labor", 1, "unemployment ... declin")]
    assert deteriorated == [("labor", -1, "labor ... deteriorat")]


def test_a_keyword_pairs_with_the_closest_modifier_and_the_later_on_a_tie() -> None:
    # given inflation between two modifiers at different distances, then at the same distance

    # when each is scored
    nearer = sentence_pairs("Inflation has risen, though weak")
    tie = sentence_pairs("subdued inflation elevated")

    # then the nearer one, and on a tie the one after the keyword, is taken
    assert nearer == [("inflation", 1, "inflation ... risen")]
    assert tie == [("inflation", 1, "inflation ... elevat")]


def test_a_match_starts_at_a_word_and_honours_its_edges() -> None:
    # given words an entry sits inside, a stem followed by more, and a spelled-out exclusion
    sentences = (
        "Software spending was moderated.",
        "Inflation will moderate.",
        "Inflation moderated.",
        "Unemployment rose.",
        "Prices will decrease.",
    )

    # when each is scored
    scored = [sentence_pairs(sentence) for sentence in sentences]

    # then "software" is not "soft", "moderate " needs its space, "unemployment" holds no
    # "employment", and "decrease" no "ease "
    assert scored == [
        [("output", -1, "spending ... moderated")],
        [("inflation", 1, "inflation ... moderate")],
        [("inflation", -1, "inflation ... moderated")],
        [("labor", -1, "unemployment ... rose")],
        [],
    ]


def test_topics_keep_their_own_matches() -> None:
    # given "low", a modifier for labor and for output, and "remain moderate", output's phrase over
    # inflation's "moderate "

    # when each is scored
    low = sentence_pairs("The unemployment rate has remained low.")
    moderate = sentence_pairs("Inflation is expected to remain moderate.")

    # then labor keeps its pair, and inflation keeps "moderate " beside output's phrase
    assert low == [("labor", 1, "unemployment ... low")]
    assert moderate == [("inflation", 1, "inflation ... moderate")]


def test_one_modifier_pairs_with_several_keywords() -> None:
    # given two inflation keywords sharing one modifier

    # when scored
    pairs = sentence_pairs("Inflation and inflation expectations have declined.")

    # then each keyword makes its own pair
    assert pairs == [
        ("inflation", -1, "inflation ... declin"),
        ("inflation", -1, "inflation ... declin"),
    ]


def test_a_long_phrase_scores_alone() -> None:
    # given a sentence holding one of the paper's long phrases, a keyword and a modifier inside it

    # when scored
    pairs = sentence_pairs("Officials noted the risk of inflation becoming undesirably low.")

    # then only the phrase scores
    assert pairs == [("inflation", -1, "the risk of inflation becoming undesirably low")]


def test_a_future_policy_rule_needs_every_part() -> None:
    # given sentences matching all of a rule's parts, one part only, an alternative, and a rule
    # without parts
    sentences = (
        "Conditions will warrant gradual increases.",
        "Conditions will warrant patience.",
        "Purchases will be complete given improvement.",
        "The Committee can be patient.",
    )

    # when each is scored
    scored = [sentence_pairs(sentence) for sentence in sentences]

    # then a rule scores only when every part matches, and "complete" is one of its alternatives
    assert scored == [
        [("policy", 1, "(warrant)|(gradual increases)")],
        [],
        [("policy", 1, "(complete|moderate)|(purchase)|(improvement)")],
        [("policy", 0, "be patient")],
    ]


def test_an_uninformative_sentence_scores_only_policy_and_adds_no_words() -> None:
    # given a statement whose second sentence matches an uninformative rule and a policy rule
    text = (
        "Inflation has risen. The Committee will monitor rising inflation and will act as needed."
    )

    # when the statement is scored
    topics, pairs = statement_topics(text)

    # then only the first sentence's three words count, and the second scores only policy
    assert topics is not None
    assert topics["inflation"] == pytest.approx(1 / math.sqrt(3))
    assert topics["policy"] == pytest.approx(-1 / math.sqrt(3))
    assert pairs == ["inflation +1: inflation ... risen", "policy -1: (will act)|(as needed)"]


def test_text_is_normalised_before_matching() -> None:
    # given a hyphen, "U.S." and a curly apostrophe

    # when each is read
    hyphen = expectations.uninformative(
        "Long-term prospects are good as unusual forces holding down demand abate."
    )
    curly = expectations.uninformative("Today’s policy action will help.")
    us = statement_topics("U.S. inflation has risen.")

    # then each matches, and "U.S." does not end a sentence: one sentence of four words
    assert hyphen and curly
    topics, pairs = us
    assert topics is not None and topics["inflation"] == 0.5
    assert pairs == ["inflation +1: inflation ... risen"]


def test_no_informative_word_is_no_index() -> None:
    # given an empty statement and an uninformative one

    # when each is scored
    empty = expectations.statement_sentiment("")
    uninformative = expectations.statement_sentiment("We will monitor conditions as needed.")

    # then neither has an index
    assert empty == (None, [])
    assert uninformative == (None, [])


def test_the_seed_is_the_paper_s_tables_whole() -> None:
    # given the committed dictionary
    with (settings.seed_dir / expectations.SENTIMENT_DICTIONARY).open(newline="") as f:
        rows = list(csv.DictReader(f))

    # when its rows are counted by table

    # then each table has the paper's count, every score is -1, 0 or 1 and every topic is known
    assert Counter(row["table"] for row in rows) == {
        "A5": 33,
        "A6": 88,
        "A7": 98,
        "A8": 33,
        "A9": 16,
        "A10": 14,
    }
    assert {row["score"] for row in rows} == {"-1", "0", "1"}
    topics = {*expectations.SENTIMENT_TOPICS, expectations.POLICY, "uninformative"}
    assert {row["topic"] for row in rows} == topics


def _fed_events(days: list[date]) -> list[flows.EventInstance]:
    con = db.get_connection()
    flows.store_fomc_decisions([FomcDecision(day, True) for day in days], con=con)
    return flows.stored_events(flows.FED_FLOW, con=con)


def test_load_sentiment_gives_each_statement_its_surprise_and_rows(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given three decisions, the second and third holds, the second with no informative word
    events = _fed_events([date(2000, 2, 2), date(2000, 3, 21), date(2000, 5, 16)])
    first, second, third = (e.event_id for e in events)
    texts = {
        first: "Inflation has risen.",
        second: "We will monitor conditions as needed.",
        third: "Inflation has declined.",
    }
    monkeypatch.setattr(
        flows, "fed_statements", lambda api_key, cache_dir, con: (events, texts, {second, third})
    )

    # when the sentiment is loaded
    load = flows.load_sentiment("key", tmp_path)

    # then the second has no index, so the third has no surprise against it, and nothing is a row
    assert load.tones[first] == (
        pytest.approx(1 / math.sqrt(3)),
        ["inflation +1: inflation ... risen"],
    )
    assert load.tones[second] == (None, [])
    assert load.surprises == {}
    assert load.rows == []


def test_sentiment_rows_are_stored_beside_the_other_surprises(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a decision and two after it, the last a hold, and a surprise of another measure
    events = _fed_events([date(2000, 2, 2), date(2000, 3, 21), date(2000, 5, 16)])
    first, second, third = (e.event_id for e in events)
    texts = {
        first: "Inflation has risen.",
        second: "Inflation has declined.",
        third: "Inflation has declined.",
    }
    monkeypatch.setattr(
        flows, "fed_statements", lambda api_key, cache_dir, con: (events, texts, {third})
    )
    con = db.get_connection()
    other = Surprise(
        event_id=first,
        measure="core",
        baseline="trend_12m",
        actual_mom=0.3,
        expected_mom=0.2,
        surprise=0.1,
    )
    db.insert_models("surprises", [other], con=con)

    # when it is loaded and stored twice
    load = flows.load_sentiment("key", tmp_path, con=con)
    flows.store_sentiment(load, con=con)
    stored = flows.store_sentiment(load, con=con)

    # then every decision against the one before is a sentiment row, the hold a sentiment_holds row
    # too, and the other flow's row stays
    up, down = 1 / math.sqrt(3), -1 / math.sqrt(3)
    assert stored == 3
    rows = con.execute(
        "SELECT event_id, measure, baseline, actual_mom, expected_mom, surprise FROM surprises "
        "ORDER BY event_id, measure"
    ).fetchall()
    assert rows == [
        (first, "core", "trend_12m", 0.3, 0.2, pytest.approx(0.1)),
        (second, "sentiment", PREVIOUS_STATEMENT, down, up, pytest.approx(down - up)),
        (third, "sentiment", PREVIOUS_STATEMENT, down, down, 0.0),
        (third, "sentiment_holds", PREVIOUS_STATEMENT, down, down, 0.0),
    ]


def test_the_fed_s_month_is_its_day_s(tmp_db: Path) -> None:
    # given a stored Fed decision with a surprise and a move
    (event,) = _fed_events([date(2000, 3, 21)])
    con = db.get_connection()
    row = Surprise(
        event_id=event.event_id,
        measure="sentiment",
        baseline=PREVIOUS_STATEMENT,
        actual_mom=0.2,
        expected_mom=0.1,
        surprise=0.1,
    )
    db.insert_models("surprises", [row], con=con)
    con.execute(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'bps', 3)",
        [event.event_id, "UST10Y / ZN"],
    )

    # when its pairs are read
    pairs = study.surprise_pairs(flows.FED_FLOW, [("sentiment", PREVIOUS_STATEMENT)], con=con)

    # then the move is there, and the walk-forward month is the decision's
    assert pairs[("sentiment", PREVIOUS_STATEMENT)]["UST10Y / ZN"] == ([0.1], [3.0])
    assert study._month(event.event_id, "scheduled meeting") == "2000-03"
    assert study._month(event.event_id, "2000-02") == "2000-02"


@pytest.mark.parametrize(("passed", "code", "stored"), [(True, 0, 1), (False, 1, 0)])
def test_load_sentiment_stores_only_when_every_check_passes(
    tmp_db: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    passed: bool,
    code: int,
    stored: int,
) -> None:
    # given a load with one row, and the checks against the paper passing or one failing
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))
    first, second = (e.event_id for e in _fed_events([date(2000, 2, 2), date(2000, 3, 21)]))
    row = Surprise(
        event_id=second,
        measure="sentiment",
        baseline=PREVIOUS_STATEMENT,
        actual_mom=0.2,
        expected_mom=0.1,
        surprise=0.1,
    )
    tones = {first: (0.1, []), second: (0.2, [])}
    load = flows.SentimentLoad({second: 0.1}, tones, set(), {}, [row])
    monkeypatch.setattr(flows, "load_sentiment", lambda api_key, cache_dir, con=None: load)
    checks = [("every index between -1 and 1", True), ("the paper's example", passed)]
    monkeypatch.setattr(flows, "sentiment_checks", lambda load: checks)

    # when the sentiment is loaded
    result = main(["load-sentiment"])

    # then the checks are printed, and the row stored only when all pass
    out = capsys.readouterr().out
    assert result == code
    assert "check, pass: every index between -1 and 1" in out
    assert f"check, {'pass' if passed else 'fail'}: the paper's example" in out
    assert db.count_rows("surprises", con=db.get_connection()) == stored


def test_the_checks_against_the_paper(tmp_db: Path) -> None:
    # given a load where 2008-12-16 is below zero with the worked pair, 2018-09-26 above, and labor
    # quiet before 2010
    below = flows.event_id(flows.FED_FLOW, date(2008, 12, 16))
    above = flows.event_id(flows.FED_FLOW, date(2018, 9, 26))
    tones = {below: (-0.5, [flows.PAPER_WORKED_PAIR]), above: (0.5, [])}
    load = flows.SentimentLoad({}, tones, set(), {below: 0.01, above: 0.2}, [])

    # when it is checked
    checks = flows.sentiment_checks(load)

    # then all pass but the statement count, which is 2 against the paper's 166
    assert [passed for _, passed in checks] == [True, True, False, True, True]


def test_overlaps_are_settled_within_a_topic_and_a_long_phrase_blocks_every_topic() -> None:
    # given a two-word keyword over a one-word modifier and keyword, and an output phrase holding a
    # labor keyword
    gains = sentence_pairs("Job gains were solid.")
    spending = sentence_pairs("Investment spending rose.")
    phrase = sentence_pairs(
        "The recovery is continuing, though at a rate that has been insufficient to bring down "
        "unemployment."
    )

    # when each is scored

    # then the longer match wins in its topic, and the phrase leaves "unemployment" unscored
    assert gains == [("labor", 1, "job gains ... solid")]
    assert spending == [("output", 1, "investment spending ... rose")]
    assert phrase == [
        (
            "output",
            -1,
            "recovery is continuing though at a rate that has been insufficient to bring down "
            "unemployment",
        )
    ]


def test_the_index_sums_the_five_topics() -> None:
    # given a statement with an inflation, a labor, an output and a policy score
    text = "Inflation has risen. Unemployment has declined. Spending was weak. We can be patient."

    # when it is scored
    topics, _ = statement_topics(text)
    index, pairs = expectations.statement_sentiment(text)

    # then the index is their sum over the square root of the 13 words
    assert topics is not None
    assert index == pytest.approx(sum(topics.values())) == pytest.approx(1 / math.sqrt(13))
    assert len(pairs) == 4


def test_the_fed_s_surprise_asks_for_load_sentiment(
    tmp_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # given a stored Fed decision and a move, but no sentiment loaded
    (event,) = _fed_events([date(2000, 3, 21)])
    db.get_connection().execute(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'bps', 3)",
        [event.event_id, "UST10Y / ZN"],
    )

    # when the Fed's surprise is asked for
    code = main(["surprise", "--event", "fomc"])

    # then it names the command that loads it
    assert code == 1
    assert "run `fortuneteller load-sentiment` first" in capsys.readouterr().err
