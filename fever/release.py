"""Estimated publication of an observation (E-14) and when it is stale (E-10).

Shared by the fetch (vintage of backfilled values), the worker (expected observation), the
scoring (which observations count on day t, E-49) and the interface (stale marks); it imports
nothing from store/ or web/.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fever.config import FREQUENCY_DAYS, Series

NEW_YORK = ZoneInfo("America/New_York")


def estimated_release(obs_date: date, series: Series) -> datetime:
    """Observation date + lag_days, Saturday/Sunday moved to Monday, at release_time New York, in UTC.

    US holidays are not taken into account (E-14).
    """
    day = obs_date + timedelta(days=series.lag_days)
    if day.weekday() >= 5:
        day += timedelta(days=7 - day.weekday())
    return datetime.combine(day, series.release_time, tzinfo=NEW_YORK).astimezone(timezone.utc)


def is_stale(obs_date: date, lag_days: int, frequency: str, tolerance_days: int, day: date) -> bool:
    """E-10: stale once more calendar days than frequency plus tolerance have passed since the
    expected publication (observation date + lag), counted on the New York date `day`."""
    return (day - (obs_date + timedelta(days=lag_days))).days > FREQUENCY_DAYS[frequency] + tolerance_days
