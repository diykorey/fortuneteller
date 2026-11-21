import importlib.util
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from types import ModuleType

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _script() -> ModuleType:
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("eightk_text", SCRIPTS / "eightk_text.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _at(hour: int) -> datetime:
    return datetime(2021, 5, 4, hour, tzinfo=UTC)


def test_a_day_with_a_results_filing_is_left_out() -> None:
    # given a day with an 8.01 filing and a separate results filing
    day = [(_at(12), "a", "a.htm", "8.01"), (_at(20), "b", "b.htm", "2.02,9.01")]

    # when its filing is picked
    # then there is none
    assert _script().pick(day) is None


def test_the_first_filed_of_the_five_items_is_picked() -> None:
    # given a day with a 9.01-only filing first, then two of the five items
    day = [
        (_at(15), "c", "c.htm", "5.02"),
        (_at(11), "a", "a.htm", "9.01"),
        (_at(13), "b", "b.htm", "7.01,9.01"),
    ]

    # when its filing is picked
    found = _script().pick(day)

    # then it is the first filed carrying one of the five, not the 9.01 alone
    assert found is not None and found[1] == "b"


def test_the_text_starts_at_its_first_item_heading() -> None:
    # given a filing's text with a cover page
    text = (
        "FORM 8-K Commission File Number 1-234 Item 2.05 Costs Associated with Exit We will close."
    )

    # when it is cut
    # then the cover page is gone
    assert _script().from_item(text) == "Item 2.05 Costs Associated with Exit We will close."


def test_the_first_exhibit_99_is_found_in_the_index() -> None:
    # given an index page with an exhibit 10 and an exhibit 99.1
    row = '<tr><td>{n}</td><td>d</td><td><a href="/Archives/x/{f}">{f}</a></td><td>{t}</td></tr>'
    page = row.format(n=1, f="ex10.htm", t="EX-10.1") + row.format(n=2, f="pr.htm", t="EX-99.1")

    # when its exhibit is found
    # then it is the press release
    assert _script().exhibit(page) == "pr.htm"


def test_every_2_05_and_3_02_day_is_drawn_and_the_draw_repeats() -> None:
    # given 2 restructuring days among 500 others
    script = _script()
    found = [
        script.Filing(date(2021, 1, 1 + i % 28), f"T{i:03d}", i, "a", "d", "8.01", "")
        for i in range(500)
    ]
    found += [
        script.Filing(date(2022, 1, 3), "R1", 9001, "a", "d", "2.05,9.01", ""),
        script.Filing(date(2023, 1, 3), "R2", 9002, "a", "d", "3.02", ""),
    ]

    # when the sample is drawn twice
    first, second = script.draw(found), script.draw(found)

    # then it is 400, holds both, is sorted, and is the same each time
    assert len(first) == 400 and {"R1", "R2"} <= {f.ticker for f in first}
    assert first == sorted(first, key=lambda f: (f.day, f.ticker)) and first == second


def test_a_name_left_in_a_text_is_found() -> None:
    # given one clean and one leaking text
    clean = {"names": "Acme Inc|Acme", "tickers": "ACME", "text": "the company closed a plant"}
    leaking = {"names": "Acme Inc|Acme", "tickers": "ACME", "text": "Acme closed a plant"}

    # when each is tested
    leaks = _script().leaks

    # then only the second leaks
    assert (leaks(clean), leaks(leaking)) == (False, True)
