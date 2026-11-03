import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "presidential_posts.py"


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("presidential_posts", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _post(created_at: str, content: str | None) -> dict[str, str | None]:
    return {"created_at": created_at, "content": content}


def test_a_truth_post_counts_unless_it_is_a_repost_a_quote_a_link_or_off_topic() -> None:
    # given a tariff post, two reposts, a quote, a link-only post, an empty one and an off-topic one
    dump = [
        _post("2025-04-09T17:18:30.000Z", "Raising the Tariff to 125%, effective immediately"),
        _post("2025-04-10T12:00:00.000Z", "RT: tariffs are working"),
        _post("2025-04-10T13:00:00.000Z", "RT @WhiteHouse a trade deal with Japan"),
        _post("2025-04-11T12:00:00.000Z", "“The tariffs are a great success”"),
        _post("2025-04-12T12:00:00.000Z", "https://example.com/tariff"),
        _post("2025-04-12T13:00:00.000Z", None),
        _post("2025-04-12T14:00:00.000Z", "Happy Easter to all"),
    ]

    # when the matching posts are picked
    found = _script().matching_truth_posts(dump)

    # then only the tariff post counts, at its New York day and minute, naming a rate
    assert [(f"{posted:%Y-%m-%d %H:%M %z}", rate) for posted, rate in found] == [
        ("2025-04-09 13:18 -0400", True)
    ]


def test_a_truth_post_is_dated_by_new_york_inside_the_window() -> None:
    # given trade posts either side of 2025-01-20 12:00 and 2026-10-31 00:00 New York, and one
    # after 20:00 New York, a day later in UTC
    dump = [
        _post("2025-01-20T16:59:00.000Z", "A trade deal soon"),
        _post("2025-01-20T17:00:00.000Z", "A trade deal soon"),
        _post("2025-04-10T01:30:00.000Z", "Tariffs on China"),
        _post("2026-10-31T03:59:00.000Z", "A trade deal soon"),
        _post("2026-10-31T04:00:00.000Z", "A trade deal soon"),
    ]

    # when the matching posts are picked
    found = _script().matching_truth_posts(dump)

    # then the window's bounds and the day are New York's
    assert [f"{posted:%Y-%m-%d %H:%M}" for posted, _rate in found] == [
        "2025-01-20 12:00",
        "2025-04-09 21:30",
        "2026-10-30 23:59",
    ]
