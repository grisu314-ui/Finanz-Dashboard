"""Transformations from raw series to indicator values (series.toml [indicator.*], E-49).

Every function gets the input series as pandas Series of floats indexed by observation date,
ascending, and returns the indicator per observation date. A value for date d uses only input
observations dated d or earlier. Windows count observations and come from scoring.toml
[transforms]. Undefined results (division by zero, too short a window) are left out.
"""

import numpy as np
import pandas as pd

from fever.config import Indicator, ScoringConfig

TRADING_DAYS_PER_YEAR = 252


def indicator_values(indicator: Indicator, inputs: list[pd.Series], config: ScoringConfig) -> pd.Series:
    function = _TRANSFORMS[indicator.transform]
    result = function(inputs, config)
    return result.replace([np.inf, -np.inf], np.nan).dropna().sort_index()


def _level(inputs, config):
    return inputs[0]


def _ratio(inputs, config):
    a, b = _aligned(inputs)
    return a / b.where(b != 0)


def _difference(inputs, config):
    a, b = _aligned(inputs)
    return a - b


def _vrp(inputs, config):
    """VIX minus the realised volatility of the S&P 500 in percent, annualised.

    Realised volatility = sqrt(252 * mean of the squared daily log returns) over the last
    `realized_vol_window` returns (zero mean, like the variance behind the VIX).
    """
    vix, spx = inputs
    returns = np.log(spx).diff()
    realized = 100 * np.sqrt(TRADING_DAYS_PER_YEAR * (returns**2).rolling(config.realized_vol_window).mean())
    vix, realized = _aligned([vix, realized.dropna()])
    return vix - realized


def _stock_bond_corr(inputs, config):
    """Correlation of S&P 500 log returns with the negative change of the 10-year yield.

    Both on the days with both values; -dy stands for the bond return, so a high value means
    stocks and bonds fall together (bonds no longer hedge).
    """
    spx, yield10 = _aligned(inputs)
    returns = np.log(spx).diff()
    bond = -yield10.diff()
    return returns.rolling(config.correlation_window).corr(bond)


def _above_low(inputs, config):
    """Value relative to its minimum over the last `low_window` observations (current included)."""
    series = inputs[0]
    low = series.rolling(config.low_window).min()
    return series / low.where(low > 0) - 1


def _fx_rate(inputs):
    """Cross rate from two reference rates against the euro: quote per EUR / base per EUR."""
    quote, base = _aligned(inputs)
    return quote / base.where(base != 0)


def _fx_change(inputs, config):
    """Appreciation of the quote currency (e.g. yen) over `fx_change_window` fixings, as -log change."""
    rate = np.log(_fx_rate(inputs))
    return -(rate - rate.shift(config.fx_change_window))


def _fx_vol(inputs, config):
    """Annualised volatility in percent: sqrt(252 * mean squared daily log change) over `fx_vol_window`."""
    changes = np.log(_fx_rate(inputs)).diff()
    return 100 * np.sqrt(TRADING_DAYS_PER_YEAR * (changes**2).rolling(config.fx_vol_window).mean())


def _yoy(inputs, config):
    """Change against the observation dated exactly one year earlier (quarterly and monthly series)."""
    series = inputs[0]
    earlier = pd.Series(
        [series.get(_one_year_before(day), np.nan) for day in series.index], index=series.index, dtype=float
    )
    return series / earlier.where(earlier != 0) - 1


def _cot_net_short(inputs, config):
    """(Short - long) of the non-commercials as a share of open interest."""
    short, long, open_interest = _aligned(inputs)
    return (short - long) / open_interest.where(open_interest > 0)


def _aligned(inputs):
    frame = pd.concat(inputs, axis=1, join="inner")
    return [frame.iloc[:, index] for index in range(frame.shape[1])]


def _one_year_before(day):
    try:
        return day.replace(year=day.year - 1)
    except ValueError:  # 29 February
        return day.replace(year=day.year - 1, day=28)


_TRANSFORMS = {
    "level": _level,
    "ratio": _ratio,
    "difference": _difference,
    "vrp": _vrp,
    "stock_bond_corr": _stock_bond_corr,
    "above_low": _above_low,
    "fx_change": _fx_change,
    "fx_vol": _fx_vol,
    "yoy": _yoy,
    "cot_net_short": _cot_net_short,
}
