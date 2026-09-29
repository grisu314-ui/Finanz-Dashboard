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
    _Ranked, alarm_episodes, auc, block_weights, declines, fit_logit, fit_year, interval, labels_known_at, lead,
    level_episodes, level_labels, precision_recall, start_labels, validate as backtest, verdict, walk_forward_thresholds,
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


# --- estimated weights (M11, E-94) ----------------------------------------------------------------------


def features_of(scores, days, seed=7):
    """Blocks for the logit: volatility carries the constructed stress, the others are noise."""
    rng = np.random.default_rng(seed)
    n = len(days)
    return pd.DataFrame({"volatility": scores["stress"].to_numpy() + rng.normal(0, 5, n), "credit": rng.normal(50, 10, n),
                         "macro": rng.normal(50, 10, n)}, index=days)


def test_fit_logit_recovers_known_coefficients():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(20000, 2))
    true = np.array([-1.0, 1.5, -0.5])
    y = (rng.random(20000) < 1 / (1 + np.exp(-(true[0] + x @ true[1:])))).astype(float)
    assert np.allclose(fit_logit(x, y, 1e-6), true, atol=0.08)
    strong = fit_logit(x, y, 1e8)  # the ridge term pulls the slopes to zero, never the intercept
    assert np.all(np.abs(strong[1:]) < 1e-3) and strong[0] == pytest.approx(np.log(y.mean() / (1 - y.mean())), abs=1e-3)


def test_ewma_series_smooths_like_the_composite():
    from fever.scoring.composite import ewma_series
    alpha = 1 - 0.5 ** (1 / 2)
    assert ewma_series([10.0, None, 20.0, 30.0], 2) == [10.0, None, 20.0, pytest.approx(alpha * 30 + (1 - alpha) * 20)]


def test_labels_known_at_leave_a_decline_confirmed_later_open():
    prices = series([100, 110, 120, 115, 107, 100, 105, 99])  # high 120 on d2, -10 % first reached on d4
    d = list(prices.index)
    config = replace(CONFIG, drawdown_horizon=2)
    final = labels_known_at("drawdown", prices, prices, d[7] + timedelta(days=1), config)
    assert final.tolist()[:3] == [0.0, 1.0, 1.0]  # the decline begins on d3
    known = labels_known_at("drawdown", prices, prices, d[4], config)  # closes before d4: not a decline yet
    assert list(known.index) == d[:4] and known.iloc[0] == 0.0 and known.iloc[1:].isna().all()


def test_the_fit_of_a_year_ignores_later_data():
    """Mandatory test against look-ahead: the coefficients of 2000 are the same with and without the data from
    01.01.2000 on, although a decline begins in December 1999 and is confirmed only in January 2000."""
    days = business_days(date(1996, 1, 1), 1500)
    first_2000 = next(i for i, day in enumerate(days) if day.year == 2000)
    spx, vix, scores, _, days = constructed(peaks=(700, first_2000 - 3))
    config = replace(CONFIG, walk_forward_start=1997)
    years = np.array([day.year for day in days])
    x = features_of(scores, days).to_numpy()
    names = ("volatility", "credit", "macro")
    cutoff, before = date(2000, 1, 1), [day < date(2000, 1, 1) for day in days]
    known = labels_known_at("drawdown", spx, vix, cutoff, config).reindex(days).to_numpy()
    known_cut = labels_known_at("drawdown", spx[before], vix[before], cutoff, config).reindex(days).to_numpy()
    assert np.array_equal(known, known_cut, equal_nan=True)
    x_cut = x.copy()
    x_cut[years >= 2000] = np.nan
    full, cut = fit_year(2000, x, known, years, names, 1.0), fit_year(2000, x_cut, known_cut, years, names, 1.0)
    assert np.array_equal(full.beta, cut.beta) and np.array_equal(full.mean, cut.mean) and full.days == cut.days
    # the final outcomes know the decline of December 1999; the fit of 2000 must not
    final = labels_known_at("drawdown", spx, vix, date(2030, 1, 1), config).reindex(days).to_numpy()
    assert final[first_2000 - 10] == 1.0 and np.isnan(known[first_2000 - 10])


def test_report_with_estimated_weights():
    spx, vix, scores, vix_percentile, days = constructed()
    config = replace(CONFIG, walk_forward_start=1997, bootstrap_samples=50)
    report = backtest(spx, vix, scores, vix_percentile, config, 80.0, features_of(scores, days))
    json.dumps(report, allow_nan=False)
    fitted = report["events"]["drawdown"]["fitted"]
    assert set(fitted["auc"]) == {"fitted", "fitted_vulnerability", "equal", "stress", "vix"}
    assert set(fitted["auc_differences"]) == {"fitted-equal", "fitted_vulnerability-fitted", "fitted-stress", "fitted-vix"}
    assert {f["id"] for f in fitted["filters"]} == {"level1", "level2", "level3", "fitted1", "fitted2", "fitted3"}
    assert all("precision_difference" in f for f in fitted["filters"] if f["id"].startswith("fitted"))
    assert "occurrences" not in fitted and "periods" not in fitted  # only the M10 part lists them
    by_year = {entry["year"]: entry for entry in fitted["years"]}
    assert set(by_year) == {1997, 1998, 1999, 2000, 2001} and "fitted" not in by_year[1997]  # no event before 1997
    shares = by_year[2000]["fitted"]["shares"]
    assert shares["volatility"] > 50 and sum(abs(v) for v in shares.values()) == pytest.approx(100, abs=0.2)
    # the informative block carries the weight; the constant vulnerability adds nothing
    assert fitted["auc"]["fitted"]["value"] > 0.65 and by_year[2000]["fitted_vulnerability"]["shares"]["vulnerability"] == 0.0
    assert fitted["auc_differences"]["fitted_vulnerability-fitted"]["value"] == 0.0
    assert "fitted" in report["events"]["vix"] and "fitted" not in report["events"]["bear"]
    assert json.loads(json.dumps(report["config"]))["fit_blocks"] == ["volatility", "credit", "macro"]  # as stored
    assert "fitted" not in backtest(spx, vix, scores, vix_percentile, config, 80.0)["events"]["drawdown"]  # without blocks


def test_the_config_is_checked(tmp_path):
    from tests.test_config import SCORING, write
    assert (CONFIG.drawdown, CONFIG.drawdown_horizon, CONFIG.vix_level, CONFIG.vix_horizon) == (10, 63, 30, 21)  # report
    assert (CONFIG.bear, CONFIG.walk_forward_start, CONFIG.confidence) == (20, 2000, 90)
    assert CONFIG.fit_blocks == ("volatility", "credit", "macro")
    for old, new, message in (("bear = 20 ", "bear = 120 ", "bear: unter 100"),
                              ("walk_forward_start = 2000", "walk_forward_start = 20", "Jahreszahl"),
                              ("episode_gap = 5 ", "", "Parameter fehlen: episode_gap"),
                              ('fit_blocks = ["volatility", "credit", "macro"]', 'fit_blocks = ["volatility", "mood"]',
                               "unbekannte Blöcke mood"),
                              ('fit_blocks = ["volatility", "credit", "macro"]', 'fit_blocks = "volatility"', "Liste")):
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
