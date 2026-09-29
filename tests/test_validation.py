"""Validation (M10, report 4.3 step 7, E-93): events, metrics, walk-forward and the run in the worker."""

import json
import math
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from fever import score, validate
from fever.config import ConfigError, validation_config
from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations
from fever.store.status import read_status
from fever.store.validation import read_report
from fever.validation import (
    _Ranked, alarm_episodes, auc, block_weights, declines, interval, lead, level_episodes, level_labels,
    precision_recall, start_labels, validate as backtest, verdict, walk_forward_thresholds,
)

CONFIG = validation_config()
AT = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


def business_days(start, count):
    return list(pd.bdate_range(start, periods=count).date)


def series(values, start=date(2026, 1, 5)):
    return pd.Series(values, index=business_days(start, len(values)), dtype=float)


# --- events ------------------------------------------------------------------------------------------


def test_declines_by_hand_exactly_on_the_thresholds():
    prices = series([100, 110, 99, 105, 120, 108, 96, 106, 110])
    d = list(prices.index)
    found, pending = declines(prices, 10)
    # 110 -> 99 is exactly -10 %: a decline; 99 -> 120 confirms its low; 120 -> 108 (-10 %) -> 96, then +10,4 %
    assert [(x.high, x.low, x.depth, x.start, x.ended) for x in found] == [
        (d[1], d[2], 10.0, d[2], True), (d[4], d[6], 20.0, d[5], True)]
    assert pending == d[8]  # a new decline could begin after the running high


def test_a_decline_under_way_has_no_pending_high():
    prices = series([100, 90, 85, 88])
    found, pending = declines(prices, 10)
    assert pending is None and found[0].ended is False and found[0].depth == 15.0
    assert declines(series([100, 91, 99, 120]), 10) == ([], series([100, 91, 99, 120]).index[3])  # -9 % is no decline


def test_start_labels_look_ahead_and_are_censored_at_the_end():
    d = business_days(date(2026, 1, 5), 9)
    labels = start_labels(d, [d[2], d[5]], 2, None)
    # an event beginning in (t, t+2]; the last two days have no outcome yet
    assert labels.tolist()[:7] == [1, 1, 0, 1, 1, 0, 0] and np.isnan(labels.tolist()[7:]).all()
    pending = start_labels(d, [d[2]], 2, d[5])  # a decline could still begin after the high on d5
    assert pending.tolist()[:4] == [1, 1, 0, 0] and np.isnan(pending.tolist()[4:]).all()


def test_vix_labels_and_episodes():
    values = series([10, 31, 20, 20, 40])
    labels = level_labels(values, 30, 2)
    assert labels.tolist()[:3] == [1, 0, 1] and np.isnan(labels.tolist()[3:]).all()  # strictly above 30
    days = series([31, 20, 32, 10, 10, 10, 35]).index
    assert level_episodes(series([31, 20, 32, 10, 10, 10, 35]), 30, 2) == [(days[0], days[2], 32.0), (days[6], days[6], 35.0)]


# --- metrics -----------------------------------------------------------------------------------------


def test_auc_by_hand_with_ties_and_weights():
    assert auc([1, 2, 2, 3], [0, 1, 0, 1]) == pytest.approx(3.5 / 4)  # the tie 2 vs 2 counts half
    weighted = _Ranked(np.array([1.0, 2, 2, 3]), np.array([0, 1, 0, 1])).auc(np.array([2.0, 1, 1, 1]))
    assert weighted == pytest.approx(auc([1, 1, 2, 2, 3], [0, 0, 1, 0, 1]))  # weight 2 = the day drawn twice
    assert math.isnan(auc([1, 2], [1, 1]))
    fpr, tpr = _Ranked(np.array([1.0, 2, 2, 3]), np.array([0, 1, 0, 1])).roc()
    assert (fpr, tpr) == ([0.0, 0.0, 0.5, 1.0], [0.0, 0.5, 1.0, 1.0])


def test_precision_recall_leads_and_alarm_episodes_by_hand():
    flags, outcomes = np.array([True, True, False, False]), np.array([1.0, 0, 1, 0])
    assert precision_recall(flags, outcomes, np.ones(4)) == (0.5, 0.5)
    assert precision_recall(flags, outcomes, np.array([3.0, 1, 1, 1])) == (0.75, 0.75)
    alarms = np.array([0, 1, 0, 1, 0, 0], dtype=bool)
    assert lead(alarms, 5, 3) == 2 and lead(alarms, 5, 4) == 4 and lead(alarms, 1, 1) is None
    assert alarm_episodes(np.array([1, 1, 0, 0, 1, 0, 0, 0, 0, 1], dtype=bool), 2) == [(0, 1), (4, 4), (9, 9)]


def test_block_bootstrap_draws_n_days_reproducibly():
    first = list(block_weights(10, 4, 3))
    assert all(w.sum() == 10 for w in first) and all((a == b).all() for a, b in zip(first, block_weights(10, 4, 3)))
    assert all((w == 1).all() for w in block_weights(5, 9, 2))  # one block of all days
    assert interval([0.1, 0.2, 0.3, math.nan], 0.2, 90)["value"] == 0.2
    assert [verdict({"low": lo, "high": hi}) for lo, hi in ((0.01, 0.2), (-0.1, 0.2), (-0.3, -0.01), (None, None))] == [
        "better", "same", "worse", "same"]


def test_walk_forward_thresholds_use_earlier_years_only():
    days = [date(1998, 6, 1), date(1998, 7, 1), date(1999, 6, 1), date(1999, 7, 1), date(2000, 6, 1), date(2001, 6, 1)]
    level = np.array([0.0, 1, 0, 1, 3, 0])
    vix = np.array([10.0, 20, 30, 40, 99, 50])
    thresholds = walk_forward_thresholds(days, level, vix, 2000, 2001)
    # 2000 sees 1998-1999: half the days at least yellow -> the median VIX percentile 25; red never -> no alarm
    assert thresholds[2000][1] == pytest.approx(25.0) and thresholds[2000][3] == math.inf
    cut = walk_forward_thresholds(days[:4], level[:4], vix[:4], 2000, 2000)
    assert cut[2000] == thresholds[2000]  # the same without the later years (no look-ahead)


def test_periods_show_an_auc_only_with_an_event_beginning_in_them():
    from fever.validation import _periods
    years = np.array([1999] * 4 + [2000] * 4)
    signals = {"stress": np.array([1.0, 2, 3, 4, 1, 2, 3, 4]), "vix": np.array([4.0, 3, 2, 1, 1, 2, 3, 4])}
    labels = np.array([0.0, 0, 1, 1, 0, 1, 0, 1])  # the positives of 1999 lead into an event of 2000
    periods = _periods(years, signals, labels, np.ones(8, dtype=bool), [{"start": "2000-03-01"}, {"start": "2000-09-01"}], 2000)
    assert [(p["from"], p["events"], p["auc_stress"]) for p in periods] == [(1999, 0, None), (2000, 2, 0.75)]
    assert periods[1]["auc_vix"] == 0.75 and periods[0]["auc_vix"] is None


# --- the whole report on a constructed history ----------------------------------------------------------


def constructed(n=1500, peaks=(700, 1100)):
    """Rising prices with two declines of about 14 %: stress (and orange) during the 30 days before each."""
    days = business_days(date(1996, 1, 1), n)
    prices, stress, vix = [100.0], np.full(n, 10.0), np.full(n, 15.0)
    for i in range(1, n):
        factor = 1.0005
        for p in peaks:
            if p <= i < p + 10:
                factor, vix[i] = 0.985, 35.0
            elif p + 10 <= i < p + 30:
                factor = 1.012
        prices.append(prices[-1] * factor)
    for p in peaks:
        stress[p - 30:p] = 90.0
    scores = pd.DataFrame({"level": np.where(stress > 50, 2.0, 0.0), "stress": stress, "vulnerability": 50.0}, index=days)
    return (pd.Series(prices, index=days), pd.Series(vix, index=days), scores,
            pd.Series(50.0, index=days), days)


def test_report_on_a_constructed_history():
    spx, vix, scores, vix_percentile, days = constructed()
    config = replace(CONFIG, walk_forward_start=1997, bootstrap_samples=100)
    report = backtest(spx, vix, scores, vix_percentile, config, 80.0)
    json.dumps(report, allow_nan=False)  # stored as plain JSON
    drawdown = report["events"]["drawdown"]
    assert drawdown["first"] == "1997-01-01" and drawdown["positives"] == 2 * config.drawdown_horizon
    assert drawdown["auc"]["stress"]["value"] > 0.7 and drawdown["auc"]["vix"]["value"] == 0.5
    assert drawdown["auc_difference"]["verdict"] == "better"
    filters = {f["id"]: f for f in drawdown["filters"]}
    orange = filters["level2"]
    assert orange["precision"]["value"] == 1.0 and orange["leads"] == [30, 30] and orange["false_alarms"] == []
    assert filters["always"]["precision"]["value"] == drawdown["base_rate"] and filters["always"]["recall"]["value"] == 1.0
    assert [o["leads"]["level2"] for o in drawdown["occurrences"]] == [30, 30]
    assert [o["start"] for o in drawdown["occurrences"]] == [days[700].isoformat(), days[1100].isoformat()]
    spikes = report["events"]["vix"]
    assert [o["start"] for o in spikes["occurrences"]] == [days[700].isoformat(), days[1100].isoformat()]
    assert report["events"]["bear"]["positives"] == 0 and report["events"]["bear"]["filters"] == []  # 14 % is no bear
    assert set(report["thresholds"]) == {str(year) for year in range(1997, days[-1].year + 1)}


def test_the_config_is_checked(tmp_path):
    from tests.test_config import SCORING, write
    assert (CONFIG.drawdown, CONFIG.drawdown_horizon, CONFIG.vix_level, CONFIG.vix_horizon) == (10, 63, 30, 21)  # report
    assert (CONFIG.bear, CONFIG.walk_forward_start, CONFIG.confidence) == (20, 2000, 90)
    for old, new, message in (("bear = 20 ", "bear = 120 ", "bear: unter 100"),
                              ("walk_forward_start = 2000", "walk_forward_start = 20", "Jahreszahl"),
                              ("episode_gap = 5 ", "", "Parameter fehlen: episode_gap")):
        assert SCORING.count(old) == 1
        with pytest.raises(ConfigError, match=message):
            validation_config(write(tmp_path, "scoring", SCORING.replace(old, new)))


# --- the run -------------------------------------------------------------------------------------------


def test_run_stores_the_report_and_runs_again_only_when_needed(migrated_dir):
    engine = make_engine(migrated_dir)
    spx, vix, _, _, days = constructed(n=2600, peaks=(1900, 2300))
    with engine.begin() as conn:
        for series_id, values in (("spx", spx), ("vix", vix)):
            append_observations(conn, series_id, [NewObservation(d, float(v), AT, True) for d, v in values.items()],
                                retrieved_at=AT)
    assert not validate.needs_run(engine, validate.config_hash())  # no scores yet
    score.run(engine, clock=lambda: AT)
    digest = validate.config_hash()
    assert validate.needs_run(engine, digest)
    summary = validate.run(engine, clock=lambda: AT + timedelta(minutes=1))
    assert "Validierung berechnet" in validate.describe(summary)
    with engine.connect() as conn:
        stored = read_report(conn)
        status = next(row for row in read_status(conn) if row["source"] == "validation")
    # only the volatility block has data here, so there is no stress composite and no day to evaluate
    assert stored.score_computed_at == AT and set(stored.content["events"]) == {"drawdown", "vix", "bear"}
    assert stored.content["events"]["drawdown"]["days"] == 0 and "keine auswertbaren Tage" in validate.describe(summary)
    assert status["last_success_at"] == AT + timedelta(minutes=1)
    assert not validate.needs_run(engine, digest) and validate.needs_run(engine, "another")
    score.run(engine, clock=lambda: AT + timedelta(hours=1))  # new scores: the report is out of date
    assert validate.needs_run(engine, digest)


def test_the_worker_validates_after_scoring_and_records_errors(migrated_dir, monkeypatch):
    import fever.worker as worker
    engine = make_engine(migrated_dir)
    calls = []
    monkeypatch.setattr(validate, "needs_run", lambda engine, digest: True)
    monkeypatch.setattr(validate, "run", lambda engine, clock: calls.append(clock()) or validate.Summary({"events": {}}, 0.1))
    worker._validate(engine, lambda: AT)
    assert calls == [AT]

    def broken(engine, clock):
        raise ValueError("kaputt")

    monkeypatch.setattr(validate, "run", broken)
    worker._validate(engine, lambda: AT)
    with engine.connect() as conn:
        status = next(row for row in read_status(conn) if row["source"] == "validation")
    assert status["last_error_at"] == AT and "ValueError: kaputt" in status["last_error_message"]
