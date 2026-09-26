"""Schedule rule E-31, planned in America/New_York (docs/umsetzungsplan.md, M3)."""

from datetime import date, datetime, timedelta, timezone

import pytest

from fever.config import series_catalog
from fever.worker import RETRY_AFTER, SeriesState, expected_obs_date, is_due

CATALOG = series_catalog()
DGS10 = CATALOG["dgs10"]  # daily, lag 1, 16:30 New York
NFCI = CATALOG["nfci"]  # weekly, 08:45 New York
VIX = CATALOG["vix"]  # daily, lag 0, 22:00 New York
ICE = CATALOG["bamlh0a0hym2"]  # daily, lag 1, 10:15 New York


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


FRESH = SeriesState()  # after a (re)start nothing counts as fetched today


@pytest.mark.parametrize(
    "now, due",
    [
        # Friday 30.10.2026, still EDT (UTC-4): 16:30 New York = 20:30 UTC
        (utc(2026, 10, 30, 20, 29), False),
        (utc(2026, 10, 30, 20, 30), True),
        # Monday 02.11.2026, EST since 01.11. (UTC-5): 16:30 New York = 21:30 UTC
        (utc(2026, 11, 2, 20, 30), False),
        (utc(2026, 11, 2, 21, 29), False),
        (utc(2026, 11, 2, 21, 30), True),
    ],
)
def test_release_time_follows_new_york_across_the_us_dst_change(now, due):
    assert is_due(DGS10, FRESH, now, None) is due


def test_the_eu_dst_change_does_not_move_the_schedule():
    # Europe leaves summer time on 25.10.2026, New York only on 01.11.: 20:30 UTC on both sides.
    for day in (23, 26):  # Friday before, Monday after the EU change
        assert not is_due(DGS10, FRESH, utc(2026, 10, day, 20, 29), None)
        assert is_due(DGS10, FRESH, utc(2026, 10, day, 20, 30), None)


def test_weekends_are_never_due():
    for now in (utc(2026, 10, 31, 23, 0), utc(2026, 11, 1, 23, 0)):  # Saturday, Sunday
        assert not is_due(VIX, FRESH, now, None)
        assert not is_due(NFCI, FRESH, now, None)


def test_weekly_series_once_per_new_york_day():
    now = utc(2026, 9, 30, 12, 50)  # Wednesday 08:50 EDT, NFCI release day
    assert is_due(NFCI, FRESH, now, date(2026, 9, 18))
    done = SeriesState(last_success_day=date(2026, 9, 30), last_attempt=now)
    assert not is_due(NFCI, done, now + timedelta(hours=5), date(2026, 9, 25))
    # Next New York day, again from the release time on
    assert not is_due(NFCI, done, utc(2026, 10, 1, 12, 44), date(2026, 9, 25))
    assert is_due(NFCI, done, utc(2026, 10, 1, 12, 45), date(2026, 9, 25))


def test_failed_fetch_is_retried_after_one_hour():
    failed_at = utc(2026, 9, 30, 12, 50)
    state = SeriesState(last_success_day=date(2026, 9, 29), last_attempt=failed_at)
    assert not is_due(NFCI, state, failed_at + RETRY_AFTER - timedelta(minutes=1), None)
    assert is_due(NFCI, state, failed_at + RETRY_AFTER, None)


def test_daily_series_are_followed_up_hourly_while_the_expected_value_is_missing():
    fetched_at = utc(2026, 9, 26, 2, 15)  # Friday 25.09. 22:15 EDT
    state = SeriesState(last_success_day=date(2026, 9, 25), last_attempt=fetched_at)
    missing = date(2026, 9, 24)  # Friday's close not yet in the file
    assert not is_due(VIX, state, fetched_at + timedelta(minutes=59), missing)
    assert is_due(VIX, state, fetched_at + RETRY_AFTER, missing)
    assert not is_due(VIX, state, fetched_at + RETRY_AFTER, date(2026, 9, 25))  # value arrived
    # The New York day ends at midnight; Saturday is not a fetch day.
    assert not is_due(VIX, state, utc(2026, 9, 26, 4, 30), missing)


def test_weekly_series_are_not_followed_up():
    fetched_at = utc(2026, 9, 30, 12, 50)
    state = SeriesState(last_success_day=date(2026, 9, 30), last_attempt=fetched_at)
    assert not is_due(NFCI, state, fetched_at + timedelta(hours=3), date(2026, 9, 18))


def test_holiday_leads_to_hourly_follow_ups_only():
    # Thanksgiving 26.11.2026: no close is published, the follow-ups find nothing new (no error).
    fetched_at = utc(2026, 11, 27, 3, 15)  # Thursday 22:15 EST
    state = SeriesState(last_success_day=date(2026, 11, 26), last_attempt=fetched_at)
    assert is_due(VIX, state, fetched_at + RETRY_AFTER, date(2026, 11, 25))


@pytest.mark.parametrize(
    "series, now, expected",
    [
        (ICE, utc(2026, 9, 28, 14, 30), date(2026, 9, 25)),  # Monday 10:30 EDT: Friday's value
        (ICE, utc(2026, 9, 28, 14, 0), date(2026, 9, 24)),  # before 10:15: still Thursday's
        (DGS10, utc(2026, 9, 28, 20, 45), date(2026, 9, 25)),  # Monday 16:45 EDT
        (VIX, utc(2026, 9, 26, 2, 15), date(2026, 9, 25)),  # Friday 22:15 EDT: same day
        (VIX, utc(2026, 9, 27, 15, 0), date(2026, 9, 25)),  # Sunday: last weekday
    ],
)
def test_expected_observation_date(series, now, expected):
    assert expected_obs_date(series, now) == expected
