import re
from datetime import date
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "docs" / "steps" / "expert-pack"
LAST = date(2019, 12, 31)


def test_the_expert_pack_holds_no_date_after_2019() -> None:
    # given every file of step 41's pack
    files = sorted(PACK.iterdir())

    # when every date written in them is read
    late = [
        (f.name, day)
        for f in files
        for day in re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", f.read_text())
        if date.fromisoformat(day) > LAST
    ]

    # then there are files, and none names a day after 2019-12-31
    assert files
    assert late == []
