"""Step 48, stated forecasts (docs/steps/stated-forecasts.md): a market's own past, walk-forward."""

import random
from datetime import date, timedelta

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
