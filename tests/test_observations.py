import math
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations, latest_values
from fever.store.tables import observation

UTC = timezone.utc
T0 = datetime(2026, 9, 25, 22, 30, tzinfo=UTC)
D1, D2, D3 = date(2026, 9, 22), date(2026, 9, 23), date(2026, 9, 24)


@pytest.fixture
def engine(migrated_dir):
    engine = make_engine(migrated_dir)
    yield engine
    engine.dispose()


def append(engine, rows, retrieved_at=T0, series="vix"):
    with engine.begin() as conn:
        return append_observations(conn, series, rows, retrieved_at=retrieved_at)


def row_count(engine):
    with engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(observation)).scalar()


def test_backfill_inserts_all_rows_with_estimated_vintage(engine):
    rows = [NewObservation(d, v, datetime.combine(d, datetime.min.time(), UTC) + timedelta(days=1), True)
            for d, v in [(D1, 20.5), (D2, 21.0)]]
    assert append(engine, rows) == 2
    with engine.connect() as conn:
        stored = latest_values(conn, "vix")
    assert [(s.obs_date, s.value, s.vintage_estimated) for s in stored] == [(D1, 20.5, True), (D2, 21.0, True)]
    assert all(s.retrieved_at == T0 and s.vintage.tzinfo is not None for s in stored)


def test_identical_value_adds_no_row(engine):
    append(engine, [NewObservation(D1, 20.5, T0, False)])
    later = T0 + timedelta(hours=1)
    assert append(engine, [NewObservation(D1, 20.5, later, False)], retrieved_at=later) == 0
    assert row_count(engine) == 1


def test_changed_value_adds_a_new_vintage_and_the_newest_counts(engine):
    append(engine, [NewObservation(D1, 20.5, T0, False)])
    later = T0 + timedelta(days=1)
    assert append(engine, [NewObservation(D1, 20.7, later, False)], retrieved_at=later) == 1
    assert row_count(engine) == 2
    with engine.connect() as conn:
        (stored,) = latest_values(conn, "vix")
    assert (stored.value, stored.vintage, stored.retrieved_at) == (20.7, later, later)


def test_new_date_is_appended_and_series_are_separate(engine):
    append(engine, [NewObservation(D1, 20.5, T0, False)])
    append(engine, [NewObservation(D1, 3.1, T0, False)], series="nfci")
    assert append(engine, [NewObservation(D1, 20.5, T0, False), NewObservation(D3, 19.0, T0, False)]) == 1
    with engine.connect() as conn:
        assert [s.value for s in latest_values(conn, "vix")] == [20.5, 19.0]
        assert [s.value for s in latest_values(conn, "nfci")] == [3.1]


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_values_are_rejected_and_nothing_is_stored(engine, bad):
    rows = [NewObservation(D1, 20.5, T0, False), NewObservation(D2, bad, T0, False)]
    with pytest.raises(ValueError, match="ungültiger Wert"):
        append(engine, rows)
    assert row_count(engine) == 0


def test_naive_timestamps_are_rejected(engine):
    naive = datetime(2026, 9, 25, 22, 30)
    with pytest.raises(ValueError, match="Stand ohne Zeitzone"):
        append(engine, [NewObservation(D1, 20.5, naive, False)])
    with pytest.raises(ValueError, match="Abrufzeit ohne Zeitzone"):
        append(engine, [NewObservation(D1, 20.5, T0, False)], retrieved_at=naive)


def test_duplicate_date_in_one_batch_is_rejected(engine):
    with pytest.raises(ValueError, match="doppelt"):
        append(engine, [NewObservation(D1, 20.5, T0, False), NewObservation(D1, 20.6, T0, False)])


def test_same_vintage_with_a_different_value_is_an_error(engine):
    append(engine, [NewObservation(D1, 20.5, T0, False)])
    with pytest.raises(IntegrityError):
        append(engine, [NewObservation(D1, 20.6, T0, False)])


def test_vintages_in_other_time_zones_are_stored_as_utc(engine):
    berlin = timezone(timedelta(hours=2))
    append(engine, [NewObservation(D1, 20.5, datetime(2026, 9, 26, 0, 30, tzinfo=berlin), False)])
    with engine.connect() as conn:
        (stored,) = latest_values(conn, "vix")
    assert stored.vintage == T0 and stored.vintage.utcoffset() == timedelta(0)
