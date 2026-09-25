from datetime import datetime, timedelta, timezone

from fever.store.db import make_engine
from fever.store.status import MAX_MESSAGE_LENGTH, read_status, record_attempt, record_error, record_success

T0 = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)


def test_last_error_stays_visible_after_a_later_success(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:
        record_attempt(conn, "fred", T0)
        record_error(conn, "fred", T0, "HTTP 503 für Reihe NFCI")
        record_attempt(conn, "fred", T0 + timedelta(minutes=15))
        record_success(conn, "fred", T0 + timedelta(minutes=15))
        record_attempt(conn, "cboe", T0)
    with engine.connect() as conn:
        status = {row["source"]: row for row in read_status(conn)}
    engine.dispose()

    assert status["fred"]["last_attempt_at"] == T0 + timedelta(minutes=15)
    assert status["fred"]["last_success_at"] == T0 + timedelta(minutes=15)
    assert status["fred"]["last_error_at"] == T0
    assert status["fred"]["last_error_message"] == "HTTP 503 für Reihe NFCI"
    assert status["cboe"]["last_success_at"] is None and status["cboe"]["last_error_at"] is None


def test_long_error_messages_are_truncated(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:
        record_error(conn, "ofr", T0, "x" * (MAX_MESSAGE_LENGTH + 100))
    with engine.connect() as conn:
        (row,) = read_status(conn)
    engine.dispose()
    assert len(row["last_error_message"]) == MAX_MESSAGE_LENGTH
    assert row["last_error_message"].endswith("…")
