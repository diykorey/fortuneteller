from datetime import date
from pathlib import Path

import pytest
from pydantic import SecretStr

from fortuneteller import db, expectations, flows, sources
from fortuneteller.__main__ import main
from fortuneteller.config import settings
from fortuneteller.sources import FedError, FomcDecision

YEAR_PAGE = b"""
<h5>January 31-February 1 Meeting - 2000</h5>
<p><a href="/boarddocs/press/general/2000/20000202/">Statement</a>
<a href="/fomc/minutes/20000202.htm">Minutes</a></p>
<h5>August 27 (notation vote) - 2000</h5>
<p><a href="/newsevents/pressreleases/monetary20000827a.htm">Statement on Longer-Run Goals</a></p>
<h5>March 21 Meeting - 2000</h5>
<p><a href="/boarddocs/press/general/2000/20000321/">Statement</a></p>
"""
CALENDAR = b"""
<div class="row fomc-meeting"><strong>Statement:</strong><br>
<a href="/monetarypolicy/files/monetary20250129a1.pdf">PDF</a> |
<a href="/newsevents/pressreleases/monetary20250129a.htm">HTML</a><br>
<a href="/newsevents/pressreleases/monetary20250129a1.htm">Implementation Note</a></div>
<div class="row fomc-meeting"><p>Meeting to come</p></div>
"""
OLD_PAGE = b"""<html><font>Release Date: February 2, 2000</font><p>
<font>For immediate release</font><p>
<p>The Committee remains concerned about <i>higher</i> inflation.</p>
<p>2000 Monetary policy</p><p>Home</p><b>Last update: February 2, 2000</b></html>"""
VOTE_PAGE = b"""<html><font>For immediate release</font>
<p>Slower growth is expected.</p>
<p>Voting for the FOMC monetary policy action were Alan Greenspan, Chairman; weak prices.</p>
<b>Last update: January 29, 2003</b></html>"""
NEW_PAGE = b"""<html><script>var lower = "inflation";</script><!-- higher inflation -->
<p>For release at 2:00 p.m. EST</p><p>Share</p>
<p>Inflation remains elevated. Growth is strong.</p>
<p>Voting against the action was a member who preferred higher rates.</p>
<p>For media inquiries, please email</p><p>Last Update: October 28, 2026</p></html>"""


def test_the_tone_counts_the_paper_s_phrases() -> None:
    # given statements written with the paper's adjectives and nouns
    worked = "Higher inflation, slower growth and strong growth."
    twice = "higher inflation and higher inflation"
    broken = "higher energy prices; the rate stays low. Growth eased, and slowly prices rose."
    oil = "Lower oil prices and high-inflation risk."

    # when each is scored
    tones = [expectations.statement_tone(text) for text in (worked, twice, broken, oil)]

    # then the worked example is 4/3, each occurrence counts, a word between or a full stop breaks
    # a phrase, "slowly" counts as slow*, oil price counts once, and no phrase is no tone
    assert tones[0] == (
        pytest.approx(4 / 3),
        ["higher inflation", "slower growth", "strong growth"],
    )
    assert tones[1] == (2.0, ["higher inflation", "higher inflation"])
    assert tones[2] == (0.0, ["slowly prices"])
    assert tones[3] == (1.0, ["lower oil prices", "high inflation"])


def test_each_decision_s_statement_link_is_found_by_its_text() -> None:
    # given a year page with another statement among the links, and the calendar's PDF and HTML
    # links

    # when the links are read
    year = sources.parse_fomc_statement_links(YEAR_PAGE)
    calendar = sources.parse_fomc_statement_links(CALENDAR)

    # then only a link whose whole text is "Statement" counts, and the calendar's is the HTML one
    site = "https://www.federalreserve.gov"
    assert year == {
        date(2000, 2, 2): f"{site}/boarddocs/press/general/2000/20000202/",
        date(2000, 3, 21): f"{site}/boarddocs/press/general/2000/20000321/",
    }
    assert calendar == {date(2025, 1, 29): f"{site}/newsevents/pressreleases/monetary20250129a.htm"}


def test_two_statements_on_one_day_stop_the_load() -> None:
    # given a year page with two different statements dated the same day
    page = YEAR_PAGE.replace(b"20000321/", b"20000202/again/")

    # when the links are read, then the page is refused
    with pytest.raises(FedError, match="two statements on 2000-02-02"):
        sources.parse_fomc_statement_links(page)


def test_a_statement_is_cut_to_its_body_in_every_era() -> None:
    # given an old page with a footer and no vote, one with a vote list, and a current one with a
    # script, a comment, a share line, a dissent and a media line

    # when each is cut
    old, vote, new = (sources.statement_text(page) for page in (OLD_PAGE, VOTE_PAGE, NEW_PAGE))

    # then only the statement's paragraphs are left
    assert old == "The Committee remains concerned about\nhigher\ninflation."
    assert vote == "Slower growth is expected."
    assert new == "Inflation remains elevated. Growth is strong."
    assert expectations.statement_tone(old) == (2.0, ["higher inflation"])


def test_a_hold_is_an_unchanged_target() -> None:
    # given the target before and after a hold, a cut, a hike, the 2008-12-16 switch to the range's
    # top, and a decision FRED has no later rate for
    rates = {
        date(2003, 1, 28): 1.25,
        date(2003, 2, 1): 1.25,
        date(2003, 6, 24): 1.25,
        date(2003, 6, 28): 1.0,
        date(2004, 6, 29): 1.0,
        date(2004, 7, 3): 1.25,
        date(2008, 12, 15): 1.0,
        date(2008, 12, 19): 0.25,
        date(2026, 10, 27): 4.0,
    }

    # when each decision is judged
    days = [date(2003, 1, 29), date(2003, 6, 25), date(2004, 6, 30), date(2008, 12, 16)]
    judged = [flows.is_hold(day, rates) for day in [*days, date(2026, 10, 28)]]

    # then only the unchanged target is a hold
    assert judged == [True, False, False, False, False]


def _fed_events(days: list[date]) -> list[int]:
    con = db.get_connection()
    flows.store_fomc_decisions([FomcDecision(day, True) for day in days], con=con)
    return [e.event_id for e in flows.stored_events(flows.FED_FLOW, con=con)]


def _pages(monkeypatch: pytest.MonkeyPatch, links: dict[date, str]) -> None:
    monkeypatch.setattr(sources, "fetch_fed_page", lambda url: url.encode())
    monkeypatch.setattr(sources, "parse_fomc_statement_links", lambda page: links)


def test_load_tone_scores_each_statement_against_the_one_before(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given five decisions since 2000: the second statement has no phrase, the fifth is a cut
    days = [date(2000, 2, 2), date(2000, 3, 21), date(2000, 5, 16), date(2000, 6, 28)]
    days.append(date(2000, 8, 22))
    first, _, third, fourth, fifth = _fed_events(days)
    texts = {
        days[0]: "higher inflation",
        days[1]: "nothing to count",
        days[2]: "lower inflation and higher inflation",
        days[3]: "weak growth",
        days[4]: "strong growth",
    }
    _pages(monkeypatch, {day: f"https://example.test/{day}" for day in days})
    monkeypatch.setattr(sources, "fetch_statement", lambda day, url, cache: texts[day].encode())
    monkeypatch.setattr(sources, "statement_text", lambda page: page.decode())
    rates = [(day, 6.0) for day in (date(2000, 2, 1), date(2000, 2, 5), date(2000, 5, 15))]
    rates += [(date(2000, 5, 19), 6.0), (date(2000, 6, 27), 6.0), (date(2000, 7, 1), 6.0)]
    rates += [(date(2000, 8, 21), 6.0), (date(2000, 8, 25), 5.75)]
    monkeypatch.setattr(flows, "target_rates", lambda api_key: rates)

    # when the tone is loaded
    load = flows.load_tone("key", tmp_path)

    # then the third has no surprise against a statement without a tone, the fourth and fifth have
    # theirs, the fourth a hold and the fifth a cut, and nothing is stored
    assert load.holds == {first, third, fourth}
    assert load.surprises == {fourth: -1.0, fifth: 2.0}
    assert load.tones[third] == (1.0, ["lower inflation", "higher inflation"])
    assert db.count_rows("surprises", con=db.get_connection()) == 0


def test_a_decision_without_a_statement_stops_the_load(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a stored decision since 2000 the pages hold no statement for
    _fed_events([date(1999, 12, 21), date(2000, 2, 2)])
    _pages(monkeypatch, {})

    # when the tone is loaded, then it stops, naming the decision; the one before 2000 is not asked
    with pytest.raises(ValueError, match="no statement for the Fed decision of 2000-02-02$"):
        flows.load_tone("key", tmp_path)


def test_two_pages_giving_one_decision_two_statements_stop_the_load(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a decision two pages each link a different statement for
    _fed_events([date(2000, 2, 2)])
    monkeypatch.setattr(sources, "fetch_fed_page", lambda url: url.encode())
    monkeypatch.setattr(
        sources,
        "parse_fomc_statement_links",
        lambda page: {date(2000, 2, 2): page.decode()},
    )

    # when the tone is loaded, then it stops
    with pytest.raises(ValueError, match="two statements for the Fed decision of 2000-02-02"):
        flows.load_tone("key", tmp_path)


def test_load_tone_reports_the_counts_before_any_move(
    tmp_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # given a load with two holds, one with a surprise and a move on the 10-year yield
    monkeypatch.setattr(settings, "fred_api_key", SecretStr("key"))
    first, second, third = _fed_events([date(2000, 2, 2), date(2000, 3, 21), date(2000, 5, 16)])
    tones = {
        first: (None, []),
        second: (1.5, ["higher prices"]),
        third: (2.0, ["higher inflation"]),
    }
    load = flows.ToneLoad({third: 0.5}, tones, {second, third})
    monkeypatch.setattr(flows, "load_tone", lambda api_key, cache_dir, con=None: load)
    db.get_connection().execute(
        "INSERT INTO observations (event_id, instrument, ret_unit, ret_1d) VALUES (?, ?, 'bps', 3)",
        [third, "UST10Y / ZN"],
    )

    # when the tone is loaded
    code = main(["load-tone"])

    # then the counts, the noticeable surprise and the holds' tones are printed
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[:3] == [
        "statements: 3 since 2000-02-02, 2 with a tone, 2 holds",
        "surprises: 1 on every decision, 1 on holds, 1 of them alone on their day",
        "signed links, holds with a non-zero surprise and a move:",
    ]
    assert "  UST10Y / ZN     1, smallest detectable -, too few" in out
    assert "  SPY / ES        0, smallest detectable -, too few" in out
    assert "noticeable: 0.5000" in out
    assert out[-3:] == [
        "holds with the highest tone:",
        "  2000-05-16 2.00: higher inflation",
        "  2000-03-21 1.50: higher prices",
    ]
