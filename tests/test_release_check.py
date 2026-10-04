"""Publication times in operation (M3, step 9): classification of first retrievals and Cboe snapshots."""

import gzip
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fever import release_check
from fever.config import series_catalog
from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations

NY = ZoneInfo("America/New_York")
CATALOG = series_catalog()


def ny(year, month, day, hour, minute=0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=NY).astimezone(timezone.utc)


def store(engine, series_id, obs_date, retrieved, estimated=False):
    with engine.begin() as conn:
        append_observations(conn, series_id, [NewObservation(obs_date, 1.0 + retrieved.minute, retrieved, estimated)],
                            retrieved_at=retrieved)


def test_first_live_retrievals_are_classified_against_the_estimate(migrated_dir):
    engine = make_engine(migrated_dir)
    backfill = ny(2026, 9, 26, 7, 32)
    store(engine, "vix", date(2026, 9, 25), backfill, estimated=True)
    store(engine, "vix", date(2026, 9, 25), ny(2026, 9, 28, 22, 5))  # revision of a backfilled value: ignored
    store(engine, "vix", date(2026, 9, 29), ny(2026, 9, 29, 22, 10))  # VIX 22:00, same day: on time, +0:10
    store(engine, "vix", date(2026, 9, 30), ny(2026, 10, 1, 22, 5))  # a New York day later: late
    store(engine, "dgs10", date(2026, 9, 29), ny(2026, 9, 30, 12, 0))  # expected 30.09 16:30: early (one-off fetch)
    with engine.connect() as conn:
        rows = release_check.first_live(conn)
    engine.dispose()
    assert [(s, d) for s, d, _ in rows] == [("dgs10", date(2026, 9, 29)), ("vix", date(2026, 9, 29)), ("vix", date(2026, 9, 30))]
    summary = release_check.classify(rows, CATALOG)
    assert summary["vix"]["n"] == 2 and summary["vix"]["day"] == 1 and summary["vix"]["delay"] == timedelta(minutes=10)
    assert [obs for obs, *_ in summary["vix"]["late"]] == [date(2026, 9, 30)]
    assert [obs for obs, *_ in summary["dgs10"]["early"]] == [date(2026, 9, 29)]

    lines = release_check.report(rows, CATALOG, [])
    vix = next(line for line in lines if line.startswith("vix "))
    assert vix.split()[1:4] == ["täglich", "+0", "T,"] and vix.endswith("2       0       1       1  +0:10")
    assert "  vix                    Beobachtung 30.09.2026: erwartet Wed 30.09.2026 22:00, erster Abruf Thu 01.10.2026 22:05" in lines
    assert any(line.startswith("  dgs10") and "erwartet Wed 30.09.2026 16:30" in line for line in lines)
    quiet = next(line for line in lines if line.startswith("Ohne neuen Wert im Betrieb: "))
    assert "nfci" in quiet and "vix," not in quiet and not any(line.startswith("nfci ") for line in lines)


def test_cboe_files_from_trading_hours_show_whether_the_running_day_is_in(tmp_path):
    folder = tmp_path / "raw" / "cboe" / "vix"
    folder.mkdir(parents=True)

    def archived(moment, last_row):
        stamp = moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        (folder / f"{stamp}_abc.gz").write_bytes(gzip.compress(f"DATE,OPEN,HIGH,LOW,CLOSE\n{last_row},1,2,0.5,1.5\n".encode()))

    archived(ny(2026, 9, 28, 14, 33), "09/25/2026")  # trading hours, last row Friday
    archived(ny(2026, 9, 29, 11, 0), "09/29/2026")  # trading hours with a row of the running day
    archived(ny(2026, 9, 29, 22, 5), "09/29/2026")  # after the close: not a snapshot
    archived(ny(2026, 10, 3, 12, 0), "10/02/2026")  # Saturday
    (folder / "20260930T150000000000Z_bad.gz").write_bytes(b"not gzip")  # 11:00 New York, unreadable
    found = release_check.cboe_snapshots(tmp_path)
    assert [(group, last) for group, _, last in found] == [
        ("vix", date(2026, 9, 25)), ("vix", date(2026, 9, 29)), ("vix", None)]
    lines = release_check.report([], CATALOG, found)
    assert "Cboe-Indizes während der US-Handelszeit (09:30–16:15): 3 Rohdateien, 1 mit einer Zeile des laufenden Tages, 1 nicht lesbar" in lines
