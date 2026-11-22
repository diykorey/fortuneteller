"""Step 47, the predictions page (docs/steps/predicts.md): stated forecasts only, since 2026-11-22."""

import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli


def _runs() -> list[dict[str, object]]:
    def run(market: str, span: str, verdict: str = "holds") -> dict[str, object]:
        return {"market": market, "span": span, "right": 37, "called": 49, "verdict": verdict}

    rows = [
        run("SPY / ES", "tomorrow", "doesn't hold"),
        run("SPY / ES", "month"),
        run("SPY / ES", "year"),
        run("COMP", "month"),
        run("COMP", "year"),
        run("GC / XAU", "month", "doesn't hold"),
        run(cli.HOME, "year"),
    ]
    for r in rows:
        r["now"] = "up"
        r["latest"] = "2026-08-01" if r["market"] == cli.HOME else None
    return rows


def test_one_forecast_per_market_that_holds_and_no_other() -> None:
    # given five pairs that hold and two that do not
    data = {"market_names": {}, "ask": [], "forecasts": _runs()}

    # when the page's forecasts are chosen on Friday 2026-11-20
    told = cli.stated(data, date(2026, 11, 20))

    # then each market's shortest span that holds is stated, with no if and no percentage
    assert [t["event"] for t in told] == [
        "The US stock market, over the next month",
        "US tech stocks, over the next month",
        "US home prices, in the 12 months after August 2026",
    ]
    assert all("condition" not in t and "%" not in json.dumps(t) for t in told)


@pytest.mark.skipif(shutil.which("google-chrome") is None, reason="needs google-chrome")
@pytest.mark.parametrize("width", [420, 1280])
def test_the_page_shows_up_to_five_forecasts_without_a_sideways_scroll(
    tmp_path: Path, width: int
) -> None:
    # given the page with three stated forecasts, one of them past its span, and two guesses, without the
    # counter, reporting its widths
    told = cli.stated({"market_names": {}, "ask": [], "forecasts": _runs()}, date(2026, 11, 20))
    stated = [{k: v for k, v in t.items() if k != "row"} for t in told]
    stated[0]["until"] = "2001-01-05"
    stated[0]["event"] = "Long passed"
    row = {"stated": "2098-12-04", "market": "BRN", "span": "month", "direction": "down"}
    guess = cli.guess_card(row | {"first": "2098-12-07", "last": "2099-01-05", "reason": "A guess"})
    page_data = {
        "written": "2026-11-20",
        "stated": stated,
        "guesses": [guess, guess],
        "tally": None,
        "kept_since": None,
    }
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
        template.replace(cli.PREDICTS_DATA_MARK, json.dumps(page_data)).replace("</body>", probe)
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

    # then the headline is there, the passed one dropped, two tested and two guesses shown, no
    # if-arrow, no sideways scroll
    assert "Fortuneteller predicts:" in re.sub(r"<[^>]+>", "", dom)
    shown = dom[dom.index('<ol id="predictions">') : dom.index("</ol>")]
    assert "Long passed" not in shown and "→" not in shown
    assert shown.count("Why: A guess") == 2 and shown.count("Our guess · made") == 2
    match = re.search(r"<title>(\d+) (\d+) (\d+)</title>", dom)
    assert match is not None
    scroll, inner, cards = map(int, match.groups())
    assert cards == 4
    assert scroll <= inner
