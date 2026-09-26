"""From raw values to scores: indicator histories, then the day-by-day evaluation."""

from datetime import date

import numpy as np
import pandas as pd

from fever.config import Indicator, ScoringConfig
from fever.release import estimated_release
from fever.scoring.composite import CompositeScore, IndicatorHistory, IndicatorScore, compute
from fever.scoring.percentile import mid_rank_percentiles
from fever.scoring.transforms import indicator_values


def build_history(indicator: Indicator, inputs: list[pd.Series], config: ScoringConfig) -> IndicatorHistory:
    """Indicator values with estimated publication (latest of its inputs) and oriented percentiles."""
    values = indicator_values(indicator, inputs, config)
    dates = [day for day in values.index]
    numbers = values.to_numpy(dtype=float)
    available = [max(estimated_release(day, series) for series in indicator.series) for day in dates]
    percentiles = _oriented(indicator, mid_rank_percentiles(dates, numbers, config.window_years, config.min_history_years))
    display = None
    if indicator.display_window:
        display = _oriented(
            indicator,
            mid_rank_percentiles(dates, numbers, config.display_window_years, config.display_window_years),
        )
    return IndicatorHistory(indicator, dates, numbers, available, percentiles, display)


def score(
    raw: dict[str, pd.Series], indicators: list[Indicator], score_days: list[date], config: ScoringConfig
) -> tuple[list[IndicatorScore], list[CompositeScore]]:
    """raw: newest value per observation date for every input series (float Series indexed by date)."""
    empty = pd.Series(dtype=float)
    histories = [
        build_history(indicator, [raw.get(series.id, empty) for series in indicator.series], config)
        for indicator in indicators
    ]
    return compute(score_days, histories, config)


def _oriented(indicator: Indicator, percentiles: np.ndarray) -> np.ndarray:
    """High = more stress or vulnerability; for "low" the mid-rank complement 100 - p."""
    return percentiles if indicator.orientation == "high" else 100.0 - percentiles
