"""Step 47, the predictions page (docs/steps/predicts.md): dated if-then cards from what holds."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import study


def _cell(kind: str, verdict: str = "holds", **marks: object) -> dict[str, object]:
    cell: dict[str, object] = {
        "kind": kind,
        "span": "day",
        "market": study.EXCESS_MARKET,
        "market_name": "the company against the S&P 500",
        "answer": "down",
        "right": 2506,
        "graded": 3798,
        "verdict": verdict,
        "kind_cell": False,
        "period": False,
    }
    cell.update(marks)
    return cell


def _group(name: str, cells: list[dict[str, object]]) -> dict[str, object]:
    kinds = [
        {"kind": k, "label": f"{name} {k}", "events": 1} for k in ("above", "as expected", "below")
    ]
    return {"name": name, "kinds": kinds, "cells": cells}


def _link(verdict: str, above: str | None, predictions: int) -> dict[str, object]:
    return {
        "above": above,
        "below": None,
        "right": 39,
        "predictions": predictions,
        "verdict": verdict,
    }


def _data() -> dict[str, object]:
    return {
        "written": "2026-11-27",
        "market_names": {"UST10Y / ZN": "US Treasury 10Y", "UST5Y / ZF": "US Treasury 5Y"},
        "ahead": [
            {
                "day": "2026-12-04",
                "time": "08:30",
                "event": "nfp",
                "label": "NFP",
                "consensus": 50.0,
                "above": 100.0,
                "links": {
                    "UST5Y / ZF": _link("holds", "up", 40),
                    "UST10Y / ZN": _link("holds", "up", 58),
                    "DXY": _link("doesn't hold", "up", 90),
                },
            },
            {
                "day": "2026-12-01",
                "time": "08:30",
                "event": "cpi",
                "label": "CPI",
                "consensus": 0.3,
                "above": 0.4,
                "links": {"SPY / ES": _link("too few", None, 3)},
            },
        ],
        "earnings_ahead": {
            "lines": [],
            "days": [
                {
                    "day": "2026-12-02",
                    "reports": [
                        {"symbol": "S", "name": "Small", "time": "before the open", "cap": 1.0},
                        {
                            "symbol": "CRM",
                            "name": "Salesforce",
                            "time": "after the close",
                            "cap": 9.0,
                        },
                    ],
                }
            ],
        },
        "ask": [
            _group(
                "earnings500",
                [_cell("above", "doesn't hold", answer="up"), _cell("below")],
            ),
            _group(
                "nfp",
                [
                    _cell(
                        "above", market="UST10Y / ZN", market_name="US Treasury 10Y", answer="up"
                    ),
                    _cell(
                        "below", market="UST10Y / ZN", market_name="US Treasury 10Y", answer="up"
                    ),
                ],
            ),
            _group(
                "cpi",
                [_cell("above", market="T5YIE", market_name="US 5-year breakeven", answer="up")],
            ),
        ],
    }


def test_the_cards_come_from_what_holds_soonest_first() -> None:
    # given a week with a jobs report whose links hold, a CPI whose link does not, a day of
    # reports where the miss holds and the beat does not, and answers that hold
    data = _data()

    # when the predictions are chosen
    cards = cli.predictions(data)

    # then the largest company's miss comes first, then the jobs report on its longest-replayed
    # link, then undated answers to make three, none repeating a kind already shown
    assert [(c["day"], c["event"], c["condition"], c["outcome"]) for c in cards] == [
        (
            "2026-12-02",
            "Salesforce announces its profit for the last three months",
            "If its profit is lower than Wall Street analysts predicted",
            "its stock falls behind the average big US stock the next day the market is open:"
            " it may fall, or rise less",
        ),
        (
            "2026-12-04",
            "The US jobs report",
            "If the government's monthly count shows more than 100,000 jobs added (economists"
            " predict about 50,000; the rule waits for a clear surprise)",
            "the interest the US government pays to borrow money for 10 years goes up that day",
        ),
        (
            None,
            "When the US jobs report shows fewer new jobs than economists expected",
            "Then",
            "the interest the US government pays to borrow money for 10 years goes up that day",
        ),
        (
            None,
            "When US prices rise faster than economists expected",
            "Then",
            "the inflation investors expect over the next 5 years goes up that day",
        ),
    ]
    assert cards[1]["right"] == 39 and cards[1]["graded"] == 58
    assert cards[0]["record"] == (
        "Across 3,798 profit announcements by many big US companies (not just Salesforce),"
        " this held 2,506 times and failed 1,292 times."
    )
    assert cards[1]["record"] == "In 58 past jobs reports, this held 39 times and failed 19 times."
    assert [c["link"] for c in cards].count("#ask/earnings500/below") == 1
    assert all("%" not in json.dumps(c) for c in cards)


def test_a_kind_cell_or_a_period_cell_gives_no_card() -> None:
    # given nothing ahead, and answers that say holds but are a kind cell and a period cell
    data = _data()
    data["ahead"], data["earnings_ahead"] = [], None
    data["ask"] = [_group("opec", [_cell("above", kind_cell=True), _cell("below", period=True)])]

    # when the predictions are chosen
    cards = cli.predictions(data)

    # then there are none
    assert cards == []


def test_a_week_with_nothing_ahead_still_gives_three() -> None:
    # given no release and no report ahead
    data = _data()
    data["ahead"], data["earnings_ahead"] = [], None

    # when the predictions are chosen
    cards = cli.predictions(data)

    # then three undated answers that hold are shown
    assert len(cards) == 3 and all(c["day"] is None for c in cards)


@pytest.mark.skipif(shutil.which("google-chrome") is None, reason="needs google-chrome")
@pytest.mark.parametrize("width", [420, 1280])
def test_the_page_shows_up_to_five_cards_without_a_sideways_scroll(
    tmp_path: Path, width: int
) -> None:
    # given the page with a passed card, two far ahead and four undated, without the counter,
    # reporting its widths
    cards = cli.predictions(_data())
    ahead = cards[0] | {"day": "2099-01-05", "event": "Far ahead"}
    passed = cards[0] | {"day": "2001-01-05", "event": "Long passed"}
    undated = [c for c in cards if c["day"] is None]
    told = {"written": "2026-11-27", "predictions": [passed, ahead, ahead, *undated, *undated]}
    template = (Path(cli.__file__).parent / "predicts.html").read_text()
    template = re.sub(
        r'<script defer src="https://cloud\.umami\.is.*?</script>', "", template, flags=re.S
    )
    probe = (
        "<script>document.title = [document.documentElement.scrollWidth, innerWidth,"
        " document.querySelectorAll('li.card').length].join(' ')</script></body>"
    )
    page = tmp_path / "index.html"
    page.write_text(
        template.replace(cli.PREDICTS_DATA_MARK, json.dumps(told)).replace("</body>", probe)
    )

    # when Chrome renders it at the width
    dom = subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--window-size={width},900",
            "--dump-dom",
            page.as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    ).stdout

    # then the headline is there, the passed card dropped, the two ahead first and undated after
    # them to five, and the page is no wider than the window
    assert "Fortuneteller predicts:" in dom
    shown = dom[dom.index('<ol id="predictions">') : dom.index("</ol>")]
    assert "Long passed" not in shown and shown.count("Far ahead") == 2
    match = re.search(r"<title>(\d+) (\d+) (\d+)</title>", dom)
    assert match is not None
    scroll, inner, cards = map(int, match.groups())
    assert cards == 5
    assert scroll <= inner
