"""Step 48, stated forecasts (docs/steps/stated-forecasts.md): a market's own past, walk-forward."""

import json
import random
import re
import shutil
import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest

import fortuneteller.__main__ as cli
from fortuneteller import study
from fortuneteller.sources import DailyClosingPrice


def _closes(prices: list[float]) -> list[DailyClosingPrice]:
    start = date(2000, 1, 3)
    return [DailyClosingPrice(start + timedelta(days=i), p) for i, p in enumerate(prices)]


def test_a_market_that_always_rises_holds_after_its_first_five_spans() -> None:
    # given 41 spans of 10 closes, every one rising
    closes = _closes([float(i) for i in range(411)])

    # when its long run is tested over 10 closes
    run = study.long_run(closes, 10)

    # then the first five give no forecast, the other 36 are right, and it holds, saying up
    assert (run.spans, run.called, run.right) == (41, 36, 36)
    assert run.verdict == "holds" and run.now == "up"


def test_spans_run_forward_from_the_first_close_and_leave_an_unfinished_one_out() -> None:
    # given 2,000 daily closes, rising except that the 7th year falls
    prices = [float(i) for i in range(2000)]
    prices[7 * 252] = 0.0
    closes = _closes(prices)

    # when tested over a 252-close year
    run = study.long_run(closes, 252)

    # then there are 7 whole years from the first close, the last of them down, and the 236
    # closes after them are not a span
    assert run.spans == 7 and (run.up, run.down) == (6, 1)
    assert run.called == run.spans - study.LONG_RUN_WARMUP
    assert run.first == closes[0].day


def test_a_coin_stays_a_coin() -> None:
    # given a seeded random walk of 2,000 days
    rng = random.Random(48)
    prices = [100.0]
    for _ in range(1999):
        prices.append(prices[-1] + rng.choice((-1.0, 1.0)))

    # when its next day is tested
    run = study.long_run(_closes(prices), 1)

    # then no day forecast holds
    assert run.called > 1900 and run.verdict != "holds"


def test_a_span_added_leaves_every_earlier_forecast_as_it_was() -> None:
    # given a random walk, and the same walk with one more span of 5 closes
    rng = random.Random(7)
    prices = [100.0]
    for _ in range(605):
        prices.append(prices[-1] + rng.choice((-1.0, 1.0)))

    # when each is tested over 5 closes
    before = study.long_run(_closes(prices[:601]), 5)
    after = study.long_run(_closes(prices), 5)

    # then the longer one has one span and at most one forecast more, and the same before it
    assert after.spans == before.spans + 1
    assert after.called - before.called in (0, 1)
    assert after.right - before.right in (0, 1)


def test_monthly_home_prices_count_years_in_months() -> None:
    # given 25 monthly values, rising
    months = _closes([float(i) for i in range(25)])

    # when tested over 12 months
    run = study.long_run(months, study.HOME_SPANS["year"])

    # then there are 2 year spans
    assert run.spans == 2 and run.verdict == "too few"


def _run(market: str, span: str, verdict: str = "holds", now: str = "up") -> dict[str, object]:
    return {
        "market": market,
        "span": span,
        "right": 402,
        "called": 666,
        "verdict": verdict,
        "now": now,
        "latest": "2026-09-01" if market == cli.HOME else None,
    }


def _ask_cell(span: str, until: str | None, **marks: object) -> dict[str, object]:
    cell: dict[str, object] = {
        "kind": "above",
        "span": span,
        "market": "UGA",
        "market_name": "Gasoline",
        "answer": "up",
        "right": 20,
        "graded": 31,
        "verdict": "holds",
        "kind_cell": False,
        "period": False,
        "open_until": until,
    }
    cell.update(marks)
    return cell


def _data(cells: list[dict[str, object]], runs: list[dict[str, object]]) -> dict[str, object]:
    return {
        "market_names": {},
        "ask": [{"name": "cpi", "latest": {"day": "2026-11-10", "kind": "above"}, "cells": cells}],
        "forecasts": runs,
    }


def test_a_holding_week_after_news_is_stated_to_its_last_day_and_not_after() -> None:
    # given a holding week cell of the latest CPI's kind, open until 2026-11-17
    data = _data([_ask_cell("week", "2026-11-17")], [])

    # when the page is written on its last day, and on the day after
    on = cli.stated(data, date(2026, 11, 17))
    after = cli.stated(data, date(2026, 11, 18))

    # then it is stated on the last day, outright, and not after
    assert [t["outcome"] for t in on] == [
        "US gasoline prices higher on Tue, Nov 17, 2026 than before the news"
    ]
    assert after == []


def test_a_day_cell_a_kind_cell_or_a_period_cell_is_never_stated() -> None:
    # given each open and holding, but a day cell, a kind cell and a period cell
    cells = [
        _ask_cell("day", "2026-11-30"),
        _ask_cell("week", "2026-11-30", kind_cell=True),
        _ask_cell("month", "2026-11-30", period=True),
    ]

    # when the page is written
    told = cli.stated(_data(cells, []), date(2026, 11, 17))

    # then none is stated
    assert told == []


def test_one_long_run_per_market_at_its_shortest_holding_span() -> None:
    # given the S&P 500 holding at a month and a year, gold not holding, and home prices at a year
    runs = [
        _run("SPY / ES", "week", "doesn't hold"),
        _run("SPY / ES", "month"),
        _run("SPY / ES", "year"),
        _run("GC / XAU", "month", "doesn't hold"),
        _run(cli.HOME, "year"),
    ]

    # when the page is written on Friday 2026-11-20
    told = cli.stated(_data([], runs), date(2026, 11, 20))

    # then the stock market's month and home prices' year are stated
    assert [(t["event"], t["outcome"]) for t in told] == [
        (
            "The US stock market, over the next month",
            "higher on Mon, Dec 21, 2026 than on Fri, Nov 20, 2026",
        ),
        (
            "US home prices, in the 12 months after September 2026",
            "higher in September 2027 than in September 2026",
        ),
    ]
    assert (
        told[0]["record"]
        == "Tested on 666 past months, one at a time, this held 402 times and failed 264 times."
    )


def test_the_file_keeps_one_long_run_until_its_span_ends() -> None:
    # given the S&P 500's month holding, the page written on ten evenings in a row
    data = _data([], [_run("SPY / ES", "month")])
    rows: list[dict[str, str]] = []
    day = date(2026, 11, 2)
    for _ in range(10):
        rows = cli.keep_forecasts(rows, cli.stated(data, day, rows), day)
        day += timedelta(days=1)

    # when it is written again the day after the kept span's last day
    last = date.fromisoformat(rows[0]["last"])
    again = cli.keep_forecasts(rows, cli.stated(data, last, rows), last)
    after = cli.keep_forecasts(
        rows, cli.stated(data, last + timedelta(days=1), rows), last + timedelta(days=1)
    )

    # then one row was kept over the ten evenings and on its last day, and a second the day after
    assert len(rows) == 1 and len(again) == 1 and len(after) == 2
    assert after[1]["first"] > rows[0]["last"]


def test_a_row_is_graded_when_its_last_close_is_in_and_not_before() -> None:
    # given a kept up forecast from Mon 2026-11-23 to Fri 2026-11-27, and closes to the 27th rising
    row = {f: "" for f in cli.FORECAST_FIELDS} | {
        "market": "SPY / ES",
        "direction": "up",
        "first": "2026-11-23",
        "last": "2026-11-27",
    }
    closes = _closes([100.0 + i for i in range(30)])
    start = date(2026, 11, 20)
    series = [DailyClosingPrice(start + timedelta(days=i), c.price) for i, c in enumerate(closes)]

    # when graded with the closes to the 26th, and to the 27th
    early = cli.grade_forecasts([row], lambda m: [c for c in series if c.day <= date(2026, 11, 26)])
    done = cli.grade_forecasts([row], lambda m: [c for c in series if c.day <= date(2026, 11, 27)])

    # then it is open before its last close and came true once it is in
    assert early[0]["grade"] == "" and done[0]["grade"] == "came true"
    assert cli.forecast_tally(done) == {"came_true": 1, "did_not": 0, "open": 0}


@pytest.mark.skipif(shutil.which("google-chrome") is None, reason="needs google-chrome")
def test_the_page_states_a_forecast_first_with_its_record(tmp_path: Path) -> None:
    # given a stated long run and one if-card, without the counter
    told = cli.stated(_data([], [_run("SPY / ES", "year")]), date(2026, 11, 20))
    page_data = {
        "written": "2026-11-20",
        "stated": [{k: v for k, v in t.items() if k != "row"} for t in told],
        "tally": {"came_true": 1, "did_not": 0, "open": 2},
        "kept_since": "2026-11-20",
        "predictions": [],
    }
    template = (Path(cli.__file__).parent / "predicts.html").read_text()
    template = re.sub(
        r'<script defer src="https://cloud\.umami\.is.*?</script>', "", template, flags=re.S
    )
    page = tmp_path / "index.html"
    page.write_text(template.replace(cli.PREDICTS_DATA_MARK, json.dumps(page_data)))

    # when Chrome renders it
    dom = subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--dump-dom",
            page.as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    ).stdout

    # then the forecast is stated with its record and the tally, and no if-arrow
    shown = dom[dom.index('<ol id="predictions">') : dom.index("</ol>")]
    assert "US stock market" in shown and "▲ Higher on" in shown and "Will be higher on" in shown
    assert "came true about 6 times in 10 (402 of 666 past years)" in shown
    assert "→" not in shown
    assert "Tested: 2 open · 1 right · 0 wrong" in dom


def test_a_page_written_on_a_saturday_counts_from_friday_s_close() -> None:
    # given the S&P 500's month holding
    data = _data([], [_run("SPY / ES", "month")])

    # when the page is written on Saturday 2026-11-21
    told = cli.stated(data, date(2026, 11, 21))

    # then it runs from Monday and is measured against Friday's close
    assert told[0]["outcome"] == "higher on Mon, Dec 21, 2026 than on Fri, Nov 20, 2026"
    assert (
        told[0]["when"] == "Stated Sat, Nov 21, 2026 · checked after the close on Mon, Dec 21, 2026"
    )
