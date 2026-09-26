"""Scoring run (fever.score) and its hook in the worker: storage, trigger, errors (E-50)."""

import shutil
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import func, select

import fever.worker as worker
from fever import score
from fever.config import CONFIG_DIR
from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations
from fever.store.status import read_status
from fever.store.tables import composite_score, indicator_score

AT = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def engine(migrated_dir):
    return make_engine(migrated_dir)


def store(engine, series_id, rows, at=AT):
    with engine.begin() as conn:
        append_observations(conn, series_id, [NewObservation(day, value, at, True) for day, value in rows], retrieved_at=at)


def weekdays(start, count):
    result, day = [], start
    while len(result) < count:
        if day.weekday() < 5:
            result.append(day)
        day += timedelta(days=1)
    return result


def test_run_stores_scores_and_records_success(engine):
    vix_days = weekdays(date(2015, 1, 1), 1600)  # a little over six years
    store(engine, "vix", [(day, 15.0 + (index % 20)) for index, day in enumerate(vix_days)])
    summary = score.run(engine, clock=lambda: AT)
    with engine.connect() as conn:
        days = conn.execute(select(func.count()).select_from(composite_score)).scalar()
        indicators = conn.execute(select(func.count(func.distinct(indicator_score.c.indicator_id)))).scalar()
        status = next(row for row in read_status(conn) if row["source"] == "scoring")
    assert summary.days == days > 0 and indicators == 19
    assert summary.first == date(2020, 1, 1)  # first VIX 01.01.2015: five years of history on 01.01.2020
    assert summary.last.stress is None  # one block only
    assert status["last_success_at"] == AT and status["last_error_at"] is None
    text = score.describe(summary)
    assert "Stress –, Fallhöhe –" in text and "zuletzt 17.02.2021" in text


def test_run_without_data_stores_nothing(engine):
    summary = score.run(engine, clock=lambda: AT)
    assert summary.days == 0 and summary.last is None
    assert "keine Tage" in score.describe(summary)


def test_needs_run_after_new_observations_or_a_changed_configuration(engine, tmp_path):
    digest = score.config_hash()
    assert score.needs_run(engine, digest)  # nothing stored yet
    store(engine, "vix", [(day, 20.0) for day in weekdays(date(2015, 1, 1), 1600)])
    score.run(engine, clock=lambda: AT + timedelta(minutes=1))
    assert not score.needs_run(engine, digest)
    store(engine, "vix", [(date(2026, 9, 25), 21.0)], at=AT + timedelta(minutes=2))
    assert score.needs_run(engine, digest)

    config_dir = tmp_path / "config"
    shutil.copytree(CONFIG_DIR, config_dir)
    assert score.config_hash(config_dir) == digest
    path = config_dir / "scoring.toml"
    path.write_text(path.read_text().replace("hysteresis = 5 ", "hysteresis = 4 "))
    assert score.config_hash(config_dir) != digest
    score.run(engine, clock=lambda: AT + timedelta(minutes=3))
    assert not score.needs_run(engine, digest) and score.needs_run(engine, score.config_hash(config_dir))


def test_the_worker_scores_after_the_cycle_and_survives_an_error(engine, migrated_dir, monkeypatch):
    calls = []
    monkeypatch.setattr(worker.score, "run", lambda engine, clock: calls.append(clock()) or score.Summary(0, None, None, 0.0))
    worker.run_cycle(engine, migrated_dir, None, {}, {}, threading.Event(), clock=lambda: AT)
    assert calls == [AT]

    def broken(engine, clock):
        raise ValueError("kaputt")

    monkeypatch.setattr(worker.score, "run", broken)
    worker.run_cycle(engine, migrated_dir, None, {}, {}, threading.Event(), clock=lambda: AT)
    with engine.connect() as conn:
        status = next(row for row in read_status(conn) if row["source"] == "scoring")
    assert status["last_error_message"] == "ValueError: kaputt"


def test_no_scoring_when_stopped(engine, migrated_dir, monkeypatch):
    monkeypatch.setattr(worker.score, "run", lambda engine, clock: pytest.fail("scoring must not run"))
    stop = threading.Event()
    stop.set()
    worker.run_cycle(engine, migrated_dir, None, {}, {}, stop, clock=lambda: AT)
