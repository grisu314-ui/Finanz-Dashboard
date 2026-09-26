"""Estimated publication time of an observation (decision E-14).

Shared by the fetch (vintage of backfilled values), the worker (expected observation) and the
scoring (which observations count on day t, E-49); it imports nothing from store/ or web/.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fever.config import Series

NEW_YORK = ZoneInfo("America/New_York")


def estimated_release(obs_date: date, series: Series) -> datetime:
    """Observation date + lag_days, Saturday/Sunday moved to Monday, at release_time New York, in UTC.

    US holidays are not taken into account (E-14).
    """
    day = obs_date + timedelta(days=series.lag_days)
    if day.weekday() >= 5:
        day += timedelta(days=7 - day.weekday())
    return datetime.combine(day, series.release_time, tzinfo=NEW_YORK).astimezone(timezone.utc)
