import importlib.util
from datetime import datetime
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "presidential_posts.py"


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("presidential_posts", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_truth_post_counts_unless_it_is_a_repost_a_quote_or_a_link() -> None:
    # given a tariff post, a repost, a quote, a link-only post and one before the second term
    dump = [
        {
            "created_at": "2025-04-09T17:18:30.000Z",
            "content": "Raising the Tariff to 125%, effective immediately",
        },
        {"created_at": "2025-04-10T12:00:00.000Z", "content": "RT: tariffs are working"},
        {"created_at": "2025-04-11T12:00:00.000Z", "content": "“The tariffs are a great success”"},
        {"created_at": "2025-04-12T12:00:00.000Z", "content": "https://example.com/tariff"},
        {"created_at": "2025-01-19T12:00:00.000Z", "content": "A trade deal soon"},
    ]

    # when the matching posts are picked
    found = _script().matching_truth_posts(dump)

    # then only the tariff post counts, at its New York minute, naming a rate
    assert found == [(datetime(2025, 4, 9, 13, 18, tzinfo=ZoneInfo("America/New_York")), True)]
