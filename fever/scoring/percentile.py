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


BAND_QUANTILES = (0.1, 0.5, 0.9)  # percentile bands 10/50/90 (report 6.3, view 7; E-64)


def window_quantiles(dates: list[date], values: np.ndarray, window_years: int, min_history_years: int,
                     quantiles: tuple[float, ...] = BAND_QUANTILES) -> np.ndarray:
    """Quantiles of the same window as the percentile, one row per observation (E-64).

    Raw values, not oriented; linear interpolation between the order statistics (numpy "linear",
    Hyndman-Fan type 7). NaN while the history is shorter than min_history_years; only
    observations up to d are used.
    """
    ordinals = np.array([day.toordinal() for day in dates])
    result = np.full((len(values), len(quantiles)), np.nan)
    if not dates:
        return result
    first = dates[0]
    for index, day in enumerate(dates):
        if years_before(day, min_history_years) < first:
            continue
        start = np.searchsorted(ordinals, years_before(day, window_years).toordinal(), side="right")
        result[index] = np.quantile(values[start : index + 1], quantiles, method="linear")
    return result


def years_before(day: date, years: int) -> date:
    """Same calendar day `years` earlier; 29 February becomes 28 February."""
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)
