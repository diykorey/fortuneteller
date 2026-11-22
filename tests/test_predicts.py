"""Step 47, the predictions page (docs/steps/predicts.md): stated forecasts only, since 2026-11-22."""

import functools
import http.server
import json
import re
import shutil
import subprocess
import threading
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
    # given the page with three stated forecasts, one of them past its span, and front.csv with two
    # open guesses worded with a comma and a quote and one past its end date, served over a local
    # server, without the counter, reporting its widths once the guesses are read
    told = cli.stated({"market_names": {}, "ask": [], "forecasts": _runs()}, date(2026, 11, 20))
    stated = [{k: v for k, v in t.items() if k != "row"} for t in told]
    stated[0]["until"] = "2001-01-05"
    stated[0]["event"] = "Long passed"
    guess = {
        "stated": "2098-12-04",
        "market": "BRN",
        "direction": "down",
        "last": "2099-01-05",
        "statement": 'Oil, we think, will be "lower" on Jan 5.',
        "why": "A guess, made\nover two lines. Then more.",
        "source": "https://example.com/opec",
    }
    gone = guess | {"last": "2001-01-05", "statement": "Gone by now."}
    cli._write_rows(tmp_path / "front.csv", cli.FRONT_FIELDS, [guess, guess, gone])
    page_data = {"written": "2026-11-20", "stated": stated, "tally": None, "kept_since": None}
    template = (Path(cli.__file__).parent / "predicts.html").read_text()
    template = re.sub(
        r'<script defer src="https://cloud\.umami\.is.*?</script>', "", template, flags=re.S
    )
    probe = (
        "<script>setTimeout(() => { document.title = [document.documentElement.scrollWidth,"
        " innerWidth, document.querySelectorAll('li.card').length].join(' ') }, 2000)</script></body>"
    )
    (tmp_path / "index.html").write_text(
        template.replace(cli.PREDICTS_DATA_MARK, json.dumps(page_data)).replace("</body>", probe)
    )
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # when Chrome renders it at the width
    try:
        dom = subprocess.run(
            [
                "google-chrome",
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--virtual-time-budget=10000",
                f"--window-size={width},900",
                "--dump-dom",
                f"http://127.0.0.1:{server.server_address[1]}/index.html",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        ).stdout
    finally:
        server.shutdown()

    # then the headline is there, the passed ones dropped, two tested and two guesses shown with
    # their words whole, no if-arrow, no sideways scroll
    assert "Fortuneteller predicts:" in re.sub(r"<[^>]+>", "", dom)
    shown = dom[dom.index('<ol id="predictions">') : dom.index("</ol>")]
    assert "Long passed" not in shown and "Gone by now" not in shown and "→" not in shown
    assert shown.count('Oil, we think, will be "lower" on Jan 5.') == 2
    assert shown.count("Why: A guess, made\nover two lines.") == 2
    assert shown.count("Our guess · made") == 2
    match = re.search(r"<title>(\d+) (\d+) (\d+)</title>", dom)
    assert match is not None
    scroll, inner, cards = map(int, match.groups())
    assert cards == 4
    assert scroll <= inner
