import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tenk_business.py"


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("tenk_business", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_item_1_is_the_longest_stretch_past_the_table_of_contents() -> None:
    # given a 10-K's text with a contents entry and the section itself
    text = (
        "Table of contents Item 1. Business 3 Item 1A. Risk Factors 9 "
        "PART I Item 1. Business We make widgets for airlines and sell them worldwide. "
        "Item 1A. Risk Factors Widgets may fail."
    )

    # when its business section is taken
    found = _script().business(text)

    # then it is the section, not the contents entry
    assert found == "Business We make widgets for airlines and sell them worldwide."


def test_the_company_s_names_and_tickers_are_replaced() -> None:
    # given a text naming the company in full, without its suffix, and by ticker
    text = "Acme Widgets, Inc. (ACME) is a leader. Acme Widgets sells to ACMEX dealers."
    blind = _script().blind

    # when it is blinded
    found = blind(text, "ACME WIDGETS, INC.", ["ACME"])

    # then every name is gone, and a longer word holding the ticker is kept
    assert found == "the company (the company) is a leader. the company sells to ACMEX dealers."


def test_a_page_s_tags_and_entities_become_plain_text() -> None:
    # given a page with a style block, tags and entities
    page = "<style>p{}</style><p>Oil&nbsp;&amp; gas</p>\n<div>producer</div>"

    # when it is read as text
    # then only its words are left, single-spaced
    assert _script().plain(page) == "Oil & gas producer"


def test_a_combined_items_1_and_2_section_is_read_to_item_3() -> None:
    # given a 10-K whose business and properties share one section
    text = (
        "Contents Items 1 and 2. Business and Properties 5 Item 3. Legal 9 "
        "PART I Items 1 and 2. Business and Properties We refine crude oil into fuels. "
        "Item 3. Legal Proceedings None."
    )

    # when its business section is taken
    found = _script().business(text)

    # then it runs from the section's heading to Item 3
    assert found == "Business and Properties We refine crude oil into fuels."


def test_a_one_letter_ticker_is_replaced_only_where_it_is_plainly_the_ticker() -> None:
    # given a text with the word "A" and the one-letter ticker in brackets
    text = "A leader in tools (A) and gauges."

    # when it is blinded
    found = _script().blind(text, "Gauge Works Inc", ["A"])

    # then the word stays and the ticker goes
    assert found == "A leader in tools (the company) and gauges."


def test_the_blind_test_finds_a_late_filing_and_a_name_left_in(tmp_path: Path) -> None:
    # given a texts file with one clean row and one late, named row
    rows = [
        "id,ticker,cik,filed,sic,names,tickers,text",
        "M001,ACME,1,2019-02-01,3711,Acme Inc|Acme,ACME,the company makes cars",
        "M002,BETA,2,2020-02-01,3711,Beta Corp|Beta,BETA,Beta makes trucks",
    ]
    (tmp_path / "texts.csv").write_text("\n".join(rows) + "\n")

    # when the blind test runs
    found = _script().check(tmp_path)

    # then only the second row is found, for its date and its name
    assert found == ["M002 filed 2020-02-01", "M002 names Beta"]


def test_the_brand_word_goes_but_a_common_first_word_stays() -> None:
    # given texts naming a company by its brand word, and one whose name starts with a common word
    blind = _script().blind

    # when they are blinded
    brand = blind("Agilent leads in labs.", "AGILENT TECHNOLOGIES INC", [])
    common = blind("American roads are long.", "AMERICAN TOWER CORP", [])

    # then the brand word is replaced and the common word kept
    assert (brand, common) == ("the company leads in labs.", "American roads are long.")
