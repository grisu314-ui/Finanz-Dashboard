import logging
import os
import signal
import threading
from datetime import date, datetime, timedelta, timezone

import pytest

import fever.worker as worker
from fever.backup import has_backup
from fever.config import series_catalog
from fever.sources.update import UpdateResult
from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations, latest_obs_date
from fever.store.status import read_heartbeat, read_status, record_heartbeat

CATALOG = series_catalog()
# Wednesday 30.09.2026, 08:50 New York (EDT): NFCI (08:45) and SOFR (08:15) are due.
WEDNESDAY = datetime(2026, 9, 30, 12, 50, tzinfo=timezone.utc)
KEY = "0123456789abcdef0123456789abcdef"


class Clock:
    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now


class FakeUpdate:
    """Stands in for update_group; returns planned results or raises planned exceptions."""

    def __init__(self, results=None):
        self.results = dict(results or {})
        self.calls = []

    def __call__(self, engine, directory, client, members, *, clock):
        group = members[0].group
        self.calls.append((group, clock()))
        result = self.results.get(group, UpdateResult(1, 0, None))
        if isinstance(result, Exception):
            raise result
        return [result for _ in members]


@pytest.fixture
def engine(migrated_dir):
    return make_engine(migrated_dir)


def cycle(engine, directory, catalog, states, clock, stop=None):
    worker.run_cycle(engine, directory, None, catalog, states, stop or threading.Event(), clock=clock)


def subset(*ids):
    return {series_id: CATALOG[series_id] for series_id in ids}


def test_cycle_writes_heartbeat_and_one_daily_backup_per_utc_day(engine, migrated_dir, monkeypatch):
    monkeypatch.setattr(worker, "update_group", FakeUpdate())
    clock = Clock(WEDNESDAY)
    cycle(engine, migrated_dir, {}, {}, clock)
    with engine.connect() as conn:
        assert read_heartbeat(conn, "worker") == WEDNESDAY
    clock.now += timedelta(minutes=15)
    cycle(engine, migrated_dir, {}, {}, clock)
    assert len(list((migrated_dir / "backup").glob("*-daily.sqlite3"))) == 1
    clock.now += timedelta(days=1)
    cycle(engine, migrated_dir, {}, {}, clock)
    assert len(list((migrated_dir / "backup").glob("*-daily.sqlite3"))) == 2
    assert has_backup(migrated_dir, "daily", date(2026, 10, 1))
    assert not has_backup(migrated_dir, "manual", date(2026, 10, 1))


def test_due_series_are_fetched_once_and_success_is_remembered(engine, migrated_dir, monkeypatch):
    fake = FakeUpdate()
    monkeypatch.setattr(worker, "update_group", fake)
    catalog = subset("nfci", "vix")  # VIX is not due before 22:00 New York
    states = {series_id: worker.SeriesState() for series_id in catalog}
    clock = Clock(WEDNESDAY)
    cycle(engine, migrated_dir, catalog, states, clock)
    assert [series_id for series_id, _ in fake.calls] == ["nfci"]
    assert states["nfci"].last_success_day == date(2026, 9, 30)
    clock.now += timedelta(minutes=15)
    cycle(engine, migrated_dir, catalog, states, clock)
    assert len(fake.calls) == 1  # weekly series: once per New York day


def test_failed_fetch_is_not_a_success_and_is_retried_an_hour_later(engine, migrated_dir, monkeypatch):
    fake = FakeUpdate({"nfci": UpdateResult(0, 0, "nfci: HTTP 503", fetched=False)})
    monkeypatch.setattr(worker, "update_group", fake)
    catalog = subset("nfci")
    states = {"nfci": worker.SeriesState()}
    clock = Clock(WEDNESDAY)
    cycle(engine, migrated_dir, catalog, states, clock)
    assert states["nfci"].last_success_day is None
    for minutes in (15, 30, 45):
        clock.now = WEDNESDAY + timedelta(minutes=minutes)
        cycle(engine, migrated_dir, catalog, states, clock)
    assert len(fake.calls) == 1
    clock.now = WEDNESDAY + timedelta(hours=1)
    cycle(engine, migrated_dir, catalog, states, clock)
    assert len(fake.calls) == 2


def test_dropped_values_still_count_as_fetched(engine, migrated_dir, monkeypatch):
    fake = FakeUpdate({"nfci": UpdateResult(5, 1, "nfci: 1 Wert(e) verworfen: …")})
    monkeypatch.setattr(worker, "update_group", fake)
    states = {"nfci": worker.SeriesState()}
    cycle(engine, migrated_dir, subset("nfci"), states, Clock(WEDNESDAY))
    assert states["nfci"].last_success_day == date(2026, 9, 30)


def test_unexpected_error_is_logged_recorded_masked_and_the_next_series_runs(engine, migrated_dir, monkeypatch, caplog):
    monkeypatch.setenv("FRED_API_KEY", KEY)
    fake = FakeUpdate({"sofr": RuntimeError(f"kaputt bei ?api_key={KEY}")})
    monkeypatch.setattr(worker, "update_group", fake)
    catalog = subset("sofr", "nfci")
    states = {series_id: worker.SeriesState() for series_id in catalog}
    with caplog.at_level(logging.ERROR):
        cycle(engine, migrated_dir, catalog, states, Clock(WEDNESDAY))
    assert [series_id for series_id, _ in fake.calls] == ["sofr", "nfci"]
    assert "Unerwarteter Fehler bei sofr" in caplog.text and "Traceback" in caplog.text
    with engine.connect() as conn:
        fred = next(row for row in read_status(conn) if row["source"] == "fred")
    assert fred["last_error_message"] == "sofr: interner Fehler: RuntimeError: kaputt bei ?api_key=***"
    assert states["sofr"].last_success_day is None


def test_stop_ends_the_cycle_and_serve_without_waiting(engine, migrated_dir, monkeypatch):
    stop = threading.Event()

    class StoppingUpdate(FakeUpdate):
        def __call__(self, *args, **kwargs):
            stop.set()  # e.g. SIGTERM during the first fetch
            return super().__call__(*args, **kwargs)

    fake = StoppingUpdate()
    monkeypatch.setattr(worker, "update_group", fake)
    worker.serve(engine, migrated_dir, None, subset("sofr", "nfci"), stop, clock=Clock(WEDNESDAY))
    assert [series_id for series_id, _ in fake.calls] == ["sofr"]  # returned instead of waiting 15 minutes


def test_sigterm_sets_the_stop_event():
    stop = threading.Event()
    previous = {signum: signal.getsignal(signum) for signum in (signal.SIGTERM, signal.SIGINT)}
    try:
        worker.install_stop_handlers(stop)
        os.kill(os.getpid(), signal.SIGTERM)
        assert stop.wait(timeout=5)
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def test_main_refuses_to_start_without_database(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("FEVER_DATA", str(tmp_path))
    monkeypatch.setattr(worker.log, "setup", lambda: None)
    monkeypatch.setattr(worker, "install_stop_handlers", lambda stop: None)
    with caplog.at_level(logging.ERROR):
        assert worker.main() == 2
    assert "Datenbank fehlt" in caplog.text
    assert list(tmp_path.iterdir()) == []  # nothing created


@pytest.mark.parametrize(
    "age, code, text",
    [(timedelta(minutes=1), 0, "gesund"), (timedelta(minutes=45), 0, "gesund"), (timedelta(minutes=46), 1, "ungesund")],
)
def test_healthcheck_uses_the_heartbeat_age(engine, age, code, text, capsys):
    with engine.begin() as conn:
        record_heartbeat(conn, "worker", WEDNESDAY)
    assert worker.healthcheck(WEDNESDAY + age) == code
    assert capsys.readouterr().out.startswith(text)


def test_healthcheck_without_heartbeat_or_database_is_unhealthy(migrated_dir, tmp_path, monkeypatch, capsys):
    assert worker.healthcheck(WEDNESDAY) == 1
    assert "noch kein Heartbeat" in capsys.readouterr().out
    monkeypatch.setenv("FEVER_DATA", str(tmp_path / "missing"))
    assert worker.healthcheck(WEDNESDAY) == 1


def test_heartbeat_is_overwritten_and_latest_obs_date_is_the_maximum(engine):
    with engine.begin() as conn:
        record_heartbeat(conn, "worker", WEDNESDAY)
        record_heartbeat(conn, "worker", WEDNESDAY + timedelta(minutes=15))
        assert latest_obs_date(conn, "nfci") is None
        rows = [NewObservation(date(2026, 9, day), 0.1, WEDNESDAY, True) for day in (11, 18, 4)]
        append_observations(conn, "nfci", rows, retrieved_at=WEDNESDAY)
    with engine.connect() as conn:
        assert read_heartbeat(conn, "worker") == WEDNESDAY + timedelta(minutes=15)
        assert latest_obs_date(conn, "nfci") == date(2026, 9, 18)


def test_a_download_group_is_fetched_once_per_cycle(engine, migrated_dir, monkeypatch):
    fake = FakeUpdate()
    monkeypatch.setattr(worker, "update_group", fake)
    catalog = subset("ofr_fsi", "ofr_fsi_credit", "ofr_fsi_funding")
    states = {"ofr_fsi": worker.SeriesState()}
    at = datetime(2026, 9, 30, 14, 45, tzinfo=timezone.utc)  # Wednesday 10:45 EDT, after 10:30
    cycle(engine, migrated_dir, catalog, states, Clock(at))
    assert [group for group, _ in fake.calls] == ["ofr_fsi"]
    assert states["ofr_fsi"].last_success_day == date(2026, 9, 30)


def test_the_oldest_member_decides_whether_a_group_is_followed_up(engine, migrated_dir, monkeypatch):
    fake = FakeUpdate()
    monkeypatch.setattr(worker, "update_group", fake)
    catalog = subset("ofr_fsi", "ofr_fsi_credit")
    # Wednesday 30.09.2026, 11:45 EDT: with lag 4 the value of Friday 25.09. is expected by now.
    now = datetime(2026, 9, 30, 15, 45, tzinfo=timezone.utc)
    with engine.begin() as conn:
        append_observations(conn, "ofr_fsi", [NewObservation(date(2026, 9, 25), 1.0, now, False)], retrieved_at=now)
        append_observations(conn, "ofr_fsi_credit", [NewObservation(date(2026, 9, 24), 1.0, now, False)], retrieved_at=now)
    states = {"ofr_fsi": worker.SeriesState(last_success_day=date(2026, 9, 30), last_attempt=now - timedelta(hours=1))}
    cycle(engine, migrated_dir, catalog, states, Clock(now))
    assert [group for group, _ in fake.calls] == ["ofr_fsi"]  # credit still lacks 25.09.
