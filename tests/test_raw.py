import gzip
from datetime import datetime, timedelta, timezone

import pytest

from fever.store.raw import archive_raw

T0 = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)


def test_stores_only_changed_content(tmp_path):
    first = archive_raw(tmp_path, "cboe", "vix", b"DATE,CLOSE\n", T0)
    assert first is not None and first.parent == tmp_path / "raw" / "cboe" / "vix"
    assert gzip.decompress(first.read_bytes()) == b"DATE,CLOSE\n"

    assert archive_raw(tmp_path, "cboe", "vix", b"DATE,CLOSE\n", T0 + timedelta(minutes=15)) is None
    second = archive_raw(tmp_path, "cboe", "vix", b"DATE,CLOSE\n1\n", T0 + timedelta(minutes=30))
    third = archive_raw(tmp_path, "cboe", "vix", b"DATE,CLOSE\n", T0 + timedelta(minutes=45))
    assert second is not None and third is not None
    assert sorted(p.name for p in first.parent.iterdir()) == [first.name, second.name, third.name]


@pytest.mark.parametrize("source,key", [("../etc", "vix"), ("cboe", "a/b"), ("Cboe", "vix"), ("cboe", "")])
def test_rejects_names_that_could_leave_the_archive(tmp_path, source, key):
    with pytest.raises(ValueError, match="Ungültiger Name"):
        archive_raw(tmp_path, source, key, b"x", T0)


def test_rejects_naive_timestamps(tmp_path):
    with pytest.raises(ValueError, match="ohne Zeitzone"):
        archive_raw(tmp_path, "cboe", "vix", b"x", datetime(2026, 9, 25, 20, 0))
