"""Percentiles over an indicator's own history (report 4.3 step 1, decision E-47).

Mid-rank including the current value: p = 100 * (number smaller + 1/2 * number equal) / n, over
the observations dated after d - window_years and up to d. Below min_history_years since the
first observation there is no percentile (NaN). Only observations up to d are used.
"""

from datetime import date

import numpy as np


def mid_rank_percentiles(dates: list[date], values: np.ndarray, window_years: int, min_history_years: int) -> np.ndarray:
    """Percentile per observation, NaN while the history is shorter than min_history_years."""
    ordinals = np.array([day.toordinal() for day in dates])
    result = np.full(len(values), np.nan)
    if not dates:
        return result
    first = dates[0]
    for index, (day, value) in enumerate(zip(dates, values)):
        if years_before(day, min_history_years) < first:
            continue
        start = np.searchsorted(ordinals, years_before(day, window_years).toordinal(), side="right")
        window = values[start : index + 1]
        smaller = np.count_nonzero(window < value)
        equal = np.count_nonzero(window == value)
        result[index] = 100.0 * (smaller + 0.5 * equal) / len(window)
    return result


def years_before(day: date, years: int) -> date:
    """Same calendar day `years` earlier; 29 February becomes 28 February."""
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)
