"""Scoring (M5): mandatory tests of CLAUDE.md plus transformations; decisions E-47 to E-49."""

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from fever.config import indicator_catalog, scoring_config
from fever.release import estimated_release
from fever.scoring import composite
from fever.scoring.composite import HISTORY, MISSING, OK, STALE, IndicatorHistory, compute, end_of_day, indicator_score
from fever.scoring.percentile import mid_rank_percentiles
from fever.scoring.pipeline import build_history, score
from fever.scoring.transforms import indicator_values

CONFIG = scoring_config()
INDICATORS = indicator_catalog()


def days(start, count, step=1):
    return [start + timedelta(days=step * index) for index in range(count)]


def trading_days(start, count):
    result, day = [], start
    while len(result) < count:
        if day.weekday() < 5:
            result.append(day)
        day += timedelta(days=1)
    return result


# --- percentile (mandatory: hand-calculated example with ties) ---------------------------------------


def test_mid_rank_percentile_with_ties_by_hand():
    dates = [date(2000 + year, 6, 1) for year in range(5)]
    values = np.array([1.0, 2.0, 2.0, 3.0, 2.0])
    result = mid_rank_percentiles(dates, values, window_years=10, min_history_years=0)
    # [1] -> 1/2; [1,2] -> (1 + 1/2)/2; [1,2,2] -> (1 + 2/2)/3; [1,2,2,3] -> (3 + 1/2)/4; [1,2,2,3,2] -> (1 + 3/2)/5
    assert result == pytest.approx([50.0, 75.0, 200 / 3, 87.5, 50.0])


def test_window_and_minimum_history():
    dates = [date(2000 + year, 6, 1) for year in range(5)]
    values = np.array([1.0, 2.0, 2.0, 3.0, 2.0])
    result = mid_rank_percentiles(dates, values, window_years=2, min_history_years=2)
    # 2000 and 2001 lack two years of history; the window starts after the same day two years back:
    # 2002 sees [2, 2] -> 1/2; 2003 sees [2, 3] -> (1 + 1/2)/2; 2004 sees [3, 2] -> (1/2)/2
    assert np.isnan(result[:2]).all()
    assert result[2:] == pytest.approx([50.0, 75.0, 25.0])


def test_low_orientation_is_the_complement():
    indicator = INDICATORS["ecy"]  # low = more vulnerability
    raw = pd.Series([3.0, 1.0, 2.0], index=[date(2005, 1, 1), date(2010, 1, 1), date(2014, 1, 1)])
    history = build_history(indicator, [raw], replace(CONFIG, min_history_years=1))
    # 2010: [3, 1] -> p(1) = 25; 2014: [3, 1, 2] -> p(2) = 50; low orientation -> 100 - p
    assert np.isnan(history.percentiles[0])
    assert history.percentiles[1:] == pytest.approx([75.0, 50.0])


# --- staleness, tolerance, publication (mandatory) --------------------------------------------------


def weekly_history(obs_dates, values=None):
    indicator = INDICATORS["nfci"]  # weekly, lag 6, tolerance 3, published 08:45 New York
    values = np.array(values if values is not None else [1.0] * len(obs_dates))
    available = [estimated_release(day, indicator.series[0]) for day in obs_dates]
    return IndicatorHistory(indicator, list(obs_dates), values, available, np.full(len(values), 60.0))


def test_an_observation_counts_from_its_publication_day_on():
    history = weekly_history([date(2026, 9, 18)])  # Friday, published Thursday 24.09. 08:45 (lag 6)
    assert indicator_score(history, date(2026, 9, 23)).status == MISSING
    assert indicator_score(history, date(2026, 9, 24)).status == OK


def test_stale_after_frequency_plus_tolerance():
    history = weekly_history([date(2026, 9, 18)])
    # expected publication 24.09.; weekly limit 7 + 3 = 10 days
    assert indicator_score(history, date(2026, 10, 4)).status == OK
    stale = indicator_score(history, date(2026, 10, 5))
    assert stale.status == STALE and stale.obs_date == date(2026, 9, 18) and stale.percentile == 60.0


def test_short_history_is_shown_but_not_scored():
    history = weekly_history([date(2026, 9, 18)])
    history = replace(history, percentiles=np.array([np.nan]))
    result = indicator_score(history, date(2026, 9, 25))
    assert result.status == HISTORY and result.value == 1.0 and result.percentile is None


def fixed(indicator_id, day_list, percentile, value=1.0):
    """History whose observations are published on their own day with a fixed percentile."""
    indicator = INDICATORS[indicator_id]
    available = [end_of_day(day) - timedelta(hours=1) for day in day_list]
    return IndicatorHistory(indicator, list(day_list), np.full(len(day_list), value), available, np.full(len(day_list), float(percentile)))


def test_confidence_is_the_v_weighted_share_of_ok_indicators():
    day = date(2026, 9, 25)
    ok = [fixed("vix", [day], 50), fixed("ebp", [day], 50)]  # V 1 + 4
    missing = [fixed("nfci", [day + timedelta(days=1)], 50)]  # V 3, not yet published
    _, rows = compute([day], ok + missing, CONFIG)
    assert rows[0].confidence == pytest.approx(100 * 5 / 8)


# --- blocks and composite (mandatory: block without valid indicator) --------------------------------


def test_block_without_valid_indicator_is_missing_and_composite_needs_three_blocks():
    day = date(2026, 9, 25)
    vol = fixed("vix", [day], 90)
    macro = fixed("nfci", [day], 70)
    stale_credit = fixed("ebp", [day - timedelta(days=200)], 99)
    _, rows = compute([day], [vol, macro, stale_credit], CONFIG)
    row = rows[0]
    assert row.blocks["credit"] is None and row.blocks["breadth"] is None
    assert row.stress_raw is None and row.stress is None  # 2 of 5 blocks < min_blocks 3

    credit = fixed("sofr_iorb", [day], 50)
    _, rows = compute([day], [vol, macro, credit], CONFIG)
    assert rows[0].stress_raw == pytest.approx((90 + 70 + 50) / 3)


def test_block_is_the_median_and_vulnerability_needs_two_components():
    day = date(2026, 9, 25)
    histories = [fixed("nfci", [day], 10), fixed("stlfsi4", [day], 20), fixed("ciss", [day], 90), fixed("ecy", [day], 80)]
    _, rows = compute([day], histories, CONFIG)
    assert rows[0].blocks["macro"] == 20
    assert rows[0].vulnerability_raw is None
    _, rows = compute([day], histories + [fixed("margin_yoy", [day], 60)], CONFIG)
    assert rows[0].vulnerability_raw == 70


def test_ewma_half_life_and_restart_after_a_gap():
    assert composite._ewma(None, 0.0, 3) == 0.0
    value = 0.0
    for _ in range(3):
        value = composite._ewma(value, 100.0, 3)
    assert value == pytest.approx(50.0)  # half-life 3: half of the step after 3 days
    assert composite._ewma(value, None, 3) is None
    assert composite._ewma(None, 80.0, 3) == 80.0


def test_diffusion_counts_stress_indicators_above_the_80th_percentile_only():
    day = date(2026, 9, 25)
    histories = [fixed("vix", [day], 81), fixed("nfci", [day], 80), fixed("ebp", [day], 95), fixed("ecy", [day], 99)]
    _, rows = compute([day], histories, CONFIG)
    assert rows[0].diffusion == pytest.approx(100 * 2 / 3)  # 80 is not above 80; ecy is vulnerability


# --- traffic light (mandatory: exactly on the threshold, hysteresis) -------------------------------


def run_rules(sequence, **overrides):
    rules = composite._Rules(replace(CONFIG, **overrides))
    return [rules.update(*step) for step in sequence]


def test_rules_fire_exactly_on_the_threshold():
    assert "red_stress" in run_rules([(90.0, None, None, None)])[0]
    assert "red_stress" not in run_rules([(89.999, None, None, None)])[0]
    assert run_rules([(80.0, None, None, None)])[0] == ("orange_stress",)
    assert run_rules([(75.0, 80.0, None, None)])[0] == ("orange_stress_vulnerability", "yellow_vulnerability")
    assert run_rules([(74.999, 80.0, None, None)])[0] == ("yellow_vulnerability",)
    assert run_rules([(None, None, 40.0, None)])[0] == ("yellow_diffusion",)
    assert run_rules([(None, None, 39.999, None)])[0] == ()


def test_hysteresis_ends_a_rule_only_five_points_below():
    result = run_rules([(90.0, None, None, None), (85.0, None, None, None), (84.999, None, None, None)])
    assert ["red_stress" in active for active in result] == [True, True, False]
    result = run_rules([(84.0, None, None, None), (86.0, None, None, None)])
    assert ["red_stress" in active for active in result] == [False, False]  # hysteresis only after firing
    combined = run_rules([(75, 80, None, None), (70, 75, None, None), (69.9, 75, None, None)])
    assert ["orange_stress_vulnerability" in active for active in combined] == [True, True, False]
    diffusion = run_rules([(None, None, 40, None), (None, None, 35, None), (None, None, 34.9, None)])
    assert ["yellow_diffusion" in active for active in diffusion] == [True, True, False]


def test_vix_ratio_rule_needs_three_days_above_and_three_below():
    above, below, equal, gap = (None, None, None, 1.01), (None, None, None, 0.99), (None, None, None, 1.0), (None,) * 4
    result = run_rules([above, above, equal, above, above, above, below, below, gap, below, below, below])
    fired = ["red_vix_ratio" in active for active in result]
    # 1.0 breaks the run; fires on the third day above in a row; a day without ratio keeps it on
    # but breaks the run below, so it ends on the third day below in a row after that gap
    assert fired == [False, False, False, False, False, True, True, True, True, True, True, False]


def test_level_is_the_highest_active_rule():
    day = date(2026, 9, 25)
    # three blocks at 95 -> stress 95 -> red; diffusion 100 -> yellow as well
    histories = [fixed("vix", [day], 95), fixed("nfci", [day], 95), fixed("ebp", [day], 95)]
    _, rows = compute([day], histories, CONFIG)
    assert rows[0].level == composite.RED and "yellow_diffusion" in rows[0].active_rules


# --- look-ahead (mandatory: same result for t with and without observations after t) --------------


def synthetic_raw(end):
    rng = np.random.default_rng(7)
    raw = {}
    for series_id, start, step, level in [
        ("vix", date(2008, 1, 1), 1, 20.0), ("vix3m", date(2008, 1, 1), 1, 22.0), ("vvix", date(2008, 1, 1), 1, 90.0),
        ("sp500", date(2008, 1, 1), 1, 1000.0), ("dgs10", date(2008, 1, 1), 1, 3.0),
        ("nfci", date(2008, 1, 4), 7, 0.0), ("fed_ebp", date(2008, 1, 1), 0, 0.5),
        ("sofr", date(2008, 1, 1), 1, 2.0), ("iorb", date(2008, 1, 1), 1, 2.0),
        ("shiller_ecy", date(2008, 1, 1), 0, 0.03), ("bogz1fl663067003q", date(2008, 1, 1), -1, 500.0),
    ]:
        if step == 0:  # monthly on the first
            index = pd.date_range(start, end, freq="MS").date
        elif step == -1:  # quarterly on the first
            index = pd.date_range(start, end, freq="QS").date
        elif step == 7:
            index = pd.date_range(start, end, freq="7D").date
        else:
            index = pd.bdate_range(start, end).date
        walk = level * np.exp(np.cumsum(rng.normal(0, 0.03, len(index))))
        raw[series_id] = pd.Series(walk, index=list(index))
    return raw


LOOKAHEAD_INDICATORS = ["vix", "vix_vix3m", "vvix", "vrp", "stock_bond_corr", "nfci", "ebp", "sofr_iorb", "ecy", "margin_yoy"]


def test_result_for_t_is_identical_with_and_without_later_observations():
    end = date(2020, 6, 30)
    raw = synthetic_raw(end)
    indicators = [INDICATORS[name] for name in LOOKAHEAD_INDICATORS]
    calendar = list(raw["vix"].index)
    full_rows, full_composites = score(raw, indicators, calendar, CONFIG)
    for t in (date(2014, 3, 12), date(2017, 11, 30), date(2019, 7, 1)):
        cut = {series_id: values[[day <= t for day in values.index]] for series_id, values in raw.items()}
        rows, composites = score(cut, indicators, [day for day in calendar if day <= t], CONFIG)
        assert [row for row in full_rows if row.score_date == t] == [row for row in rows if row.score_date == t]
        assert [row for row in full_composites if row.score_date == t] == [row for row in composites if row.score_date == t]
    assert any(row.level > 0 for row in full_composites) and any(row.stress is not None for row in full_composites)


# --- transformations -------------------------------------------------------------------------------


def series(values, start=date(2026, 1, 5)):
    return pd.Series(values, index=trading_days(start, len(values)), dtype=float)


def test_ratio_and_difference_use_common_dates():
    a = series([10.0, 20.0, 30.0])
    b = series([5.0, 0.0, 15.0])
    assert list(indicator_values(INDICATORS["vix_vix3m"], [a, b], CONFIG)) == [2.0, 2.0]  # division by 0 left out
    assert list(indicator_values(INDICATORS["sofr_iorb"], [a, b], CONFIG)) == [5.0, 20.0, 15.0]


def test_vrp_is_vix_minus_annualised_zero_mean_realised_vol():
    config = replace(CONFIG, realized_vol_window=2)
    spx = series([100.0, 110.0, 99.0, 99.0])
    vix = series([20.0, 20.0, 20.0, 20.0])
    result = indicator_values(INDICATORS["vrp"], [vix, spx], config)
    r = np.log([110 / 100, 99 / 110, 99 / 99])
    expected = [20 - 100 * np.sqrt(252 * np.mean(r[i - 1 : i + 1] ** 2)) for i in (1, 2)]
    assert list(result) == pytest.approx(expected)


def test_stock_bond_correlation_is_high_when_both_fall_together():
    config = replace(CONFIG, correlation_window=4)
    spx = series([100.0, 99.0, 101.0, 98.0, 102.0])
    yields = series([3.0, 3.1, 2.9, 3.2, 2.8])  # yields up when stocks fall -> bonds fall with stocks
    result = indicator_values(INDICATORS["stock_bond_corr"], [spx, yields], config)
    assert len(result) == 1 and result.iloc[0] > 0.9


def test_claims_against_their_low():
    config = replace(CONFIG, low_window=3)
    claims = pd.Series([200.0, 180.0, 220.0, 240.0], index=days(date(2026, 1, 3), 4, 7))
    assert list(indicator_values(INDICATORS["claims"], [claims], config)) == pytest.approx([220 / 180 - 1, 240 / 180 - 1])


def test_usdjpy_from_two_euro_rates():
    config = replace(CONFIG, fx_change_window=2, fx_vol_window=2)
    jpy = series([150.0, 160.0, 150.0, 140.0])
    usd = series([1.0, 1.0, 1.0, 1.0])
    change = indicator_values(INDICATORS["usdjpy_change"], [jpy, usd], config)
    assert list(change) == pytest.approx([-np.log(150 / 150), -np.log(140 / 160)])  # yen stronger -> positive
    vol = indicator_values(INDICATORS["usdjpy_vol"], [jpy, usd], config)
    r = np.diff(np.log([150, 160, 150, 140]))
    assert list(vol) == pytest.approx([100 * np.sqrt(252 * np.mean(r[i - 1 : i + 1] ** 2)) for i in (1, 2)])


def test_yoy_needs_the_observation_one_year_earlier():
    margin = pd.Series([100.0, 110.0, 150.0], index=[date(2024, 4, 1), date(2025, 1, 1), date(2025, 4, 1)])
    assert indicator_values(INDICATORS["margin_yoy"], [margin], CONFIG).to_dict() == {date(2025, 4, 1): pytest.approx(0.5)}


def test_cot_net_short_share():
    short, long, oi = series([300.0, 100.0]), series([100.0, 100.0]), series([1000.0, 0.0])
    assert list(indicator_values(INDICATORS["vx_cot_short"], [short, long, oi], CONFIG)) == [0.2]  # OI 0 left out


def test_display_window_percentile_for_cot():
    raw = [series([300.0] * 3, start=date(2000, 1, 3)) for _ in range(3)]
    history = build_history(INDICATORS["vx_cot_short"], raw, CONFIG)
    assert history.display_percentiles is not None
    assert build_history(INDICATORS["vix"], [series([20.0])], CONFIG).display_percentiles is None


def test_the_fast_block_enters_the_composite_smoothed():
    first, second = date(2026, 9, 24), date(2026, 9, 25)
    vol = IndicatorHistory(
        INDICATORS["vix"], [first, second], np.array([1.0, 1.0]),
        [end_of_day(first) - timedelta(hours=1), end_of_day(second) - timedelta(hours=1)], np.array([0.0, 100.0]),
    )
    others = [fixed("nfci", [first], 50), fixed("ebp", [first], 50)]
    _, rows = compute([first, second], [vol] + others, CONFIG)
    smoothed = 100 * (1 - 0.5 ** (1 / 3))  # one step of half-life 3 from 0 towards 100
    assert rows[1].blocks["volatility"] == 100 and rows[1].fast_block_smoothed == pytest.approx(smoothed)
    assert rows[1].stress_raw == pytest.approx((smoothed + 50 + 50) / 3)


def test_the_vix_ratio_rule_uses_same_day_values_only():
    days_ = trading_days(date(2026, 9, 21), 4)
    ratio = IndicatorHistory(
        INDICATORS["vix_vix3m"], days_[:3], np.array([1.1, 1.1, 1.1]),
        [end_of_day(day) - timedelta(hours=1) for day in days_[:3]], np.full(3, 50.0),
    )
    _, rows = compute(days_, [ratio], CONFIG)
    assert [row.level for row in rows] == [0, 0, composite.RED, composite.RED]  # 4th day: no new value, stays on
    assert "red_vix_ratio" in rows[3].active_rules
    # published one day late: on every score day the newest ratio is the one of the day before
    late = replace(ratio, available=[end_of_day(day) - timedelta(hours=1) for day in days_[1:4]])
    _, rows = compute(days_, [late], CONFIG)
    assert all(row.active_rules == () for row in rows)


def test_an_indicator_is_published_when_its_latest_input_is():
    indicator = INDICATORS["sofr_iorb"]  # SOFR: next day 08:15; IORB: same day 16:45
    day = date(2026, 9, 24)
    history = build_history(indicator, [series([4.0], start=day), series([4.1], start=day)], CONFIG)
    assert history.available == [estimated_release(day, indicator.series[0])]
    assert history.available[0] > end_of_day(day)
