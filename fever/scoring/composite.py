"""Day-by-day evaluation: indicator status, blocks, composite, vulnerability, traffic light.

Report 4.3 steps 2-5 with decisions E-47 to E-49. For every score day t (Cboe trading day) an
indicator counts with its newest observation published by the end of the New York day t
(estimated publication, E-14/E-49). Status per indicator and day:
  missing  no observation published yet
  stale    older than frequency plus tolerance after its expected publication (E-10)
  history  shorter history than min_history_years: shown, not scored
  ok       enters blocks, vulnerability, confidence and diffusion
Blocks: median of the ok stress indicators; the fast block is smoothed first. Composite: mean
of the available blocks if at least min_blocks. Smoothing: EWMA over score days; a missing value
leaves the smoothed value missing and the next one starts afresh. Traffic light: rules with
hysteresis (a rule ends only `hysteresis` points below its threshold); the highest active wins.
"""

import statistics
from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

import numpy as np

from fever.config import FREQUENCY_DAYS, STRESS_BLOCKS, VULNERABILITY, Indicator, ScoringConfig
from fever.release import NEW_YORK

OK, MISSING, STALE, HISTORY = "ok", "missing", "stale", "history"
GREEN, YELLOW, ORANGE, RED = 0, 1, 2, 3
VIX_RATIO_INDICATOR = "vix_vix3m"  # the red rule "VIX/VIX3M > 1 on 3 days in a row" reads this one
_RULE_LEVEL = {
    "red_stress": RED, "red_vix_ratio": RED,
    "orange_stress": ORANGE, "orange_stress_vulnerability": ORANGE,
    "yellow_vulnerability": YELLOW, "yellow_diffusion": YELLOW,
}


@dataclass(frozen=True)
class IndicatorHistory:
    """An indicator's values per observation date with publication time and percentiles."""

    indicator: Indicator
    dates: list[date]
    values: np.ndarray
    available: list[datetime]  # estimated publication (UTC), non-decreasing
    percentiles: np.ndarray  # oriented (high = more stress or vulnerability); NaN below min history
    display_percentiles: np.ndarray | None = None  # shorter display window (display_window = true)


@dataclass(frozen=True)
class IndicatorScore:
    score_date: date
    indicator_id: str
    status: str
    obs_date: date | None
    value: float | None
    percentile: float | None
    percentile_display: float | None


@dataclass(frozen=True)
class CompositeScore:
    score_date: date
    blocks: dict[str, float | None]  # median per stress block, unsmoothed
    fast_block_smoothed: float | None
    stress_raw: float | None
    stress: float | None
    vulnerability_raw: float | None
    vulnerability: float | None
    confidence: float
    diffusion: float | None
    level: int
    active_rules: tuple[str, ...]


def end_of_day(day: date) -> datetime:
    """Midnight after the New York day, in UTC: observations published before it count on `day`."""
    return datetime.combine(day + timedelta(days=1), time(0), tzinfo=NEW_YORK).astimezone(timezone.utc)


def indicator_score(history: IndicatorHistory, day: date) -> IndicatorScore:
    indicator = history.indicator
    count = bisect_left(history.available, end_of_day(day))
    if count == 0:
        return IndicatorScore(day, indicator.id, MISSING, None, None, None, None)
    index = count - 1
    obs_date = history.dates[index]
    percentile = _number(history.percentiles[index])
    display = None if history.display_percentiles is None else _number(history.display_percentiles[index])
    age = (day - (obs_date + timedelta(days=indicator.lag_days))).days
    if age > FREQUENCY_DAYS[indicator.frequency] + indicator.tolerance_days:
        status = STALE
    elif percentile is None:
        status = HISTORY
    else:
        status = OK
    return IndicatorScore(day, indicator.id, status, obs_date, float(history.values[index]), percentile, display)


def compute(
    score_days: list[date], histories: list[IndicatorHistory], config: ScoringConfig
) -> tuple[list[IndicatorScore], list[CompositeScore]]:
    """Scores for every score day from the first one with an ok indicator on, in date order."""
    total_weight = sum(history.indicator.v_score for history in histories)
    blocks_of = {history.indicator.id: history.indicator.block for history in histories}
    weights = {history.indicator.id: history.indicator.v_score for history in histories}
    fast = stress = vulnerability = None
    rules = _Rules(config)
    indicator_rows: list[IndicatorScore] = []
    composite_rows: list[CompositeScore] = []
    started = False
    for day in sorted(score_days):
        scores = [indicator_score(history, day) for history in histories]
        ok = [score for score in scores if score.status == OK]
        if not ok and not started:
            continue
        started = True
        indicator_rows.extend(scores)

        blocks = {
            block: _median([score.percentile for score in ok if blocks_of[score.indicator_id] == block])
            for block in STRESS_BLOCKS
        }
        fast = _ewma(fast, blocks[config.fast_block], config.fast_block_half_life)
        used = [fast if block == config.fast_block else blocks[block] for block in STRESS_BLOCKS]
        used = [value for value in used if value is not None]
        stress_raw = statistics.fmean(used) if len(used) >= config.min_blocks else None
        stress = _ewma(stress, stress_raw, config.stress_half_life)

        components = [score.percentile for score in ok if blocks_of[score.indicator_id] == VULNERABILITY]
        vulnerability_raw = statistics.fmean(components) if len(components) >= config.min_vulnerability else None
        vulnerability = _ewma(vulnerability, vulnerability_raw, config.vulnerability_half_life)

        confidence = 100.0 * sum(weights[score.indicator_id] for score in ok) / total_weight
        stress_ok = [score for score in ok if blocks_of[score.indicator_id] != VULNERABILITY]
        diffusion = (
            100.0 * sum(score.percentile > config.yellow_diffusion_percentile for score in stress_ok) / len(stress_ok)
            if stress_ok else None
        )
        ratio = next(
            (score.value for score in ok if score.indicator_id == VIX_RATIO_INDICATOR and score.obs_date == day), None
        )
        active = rules.update(stress, vulnerability, diffusion, ratio)
        level = max((_RULE_LEVEL[rule] for rule in active), default=GREEN)
        composite_rows.append(CompositeScore(
            day, blocks, fast, stress_raw, stress, vulnerability_raw, vulnerability,
            confidence, diffusion, level, active,
        ))
    return indicator_rows, composite_rows


class _Rules:
    """Traffic light rules of report 4.3 step 5 with hysteresis (E-48); state carries day to day."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.active: dict[str, bool] = dict.fromkeys(_RULE_LEVEL, False)
        self.days_above = self.days_below = 0

    def update(self, stress, vulnerability, diffusion, ratio) -> tuple[str, ...]:
        c = self.config
        previous = self.active
        now = {
            "red_stress": self._threshold(previous["red_stress"], stress, c.red_stress),
            "red_vix_ratio": self._vix_ratio(previous["red_vix_ratio"], ratio),
            "orange_stress": self._threshold(previous["orange_stress"], stress, c.orange_stress),
            "orange_stress_vulnerability": (
                self._threshold(previous["orange_stress_vulnerability"], stress, c.orange_stress_with_vulnerability)
                and self._threshold(previous["orange_stress_vulnerability"], vulnerability, c.orange_vulnerability)
            ),
            # report: vulnerability >= 80 "at stress < 75"; at stress >= 75 the orange rule applies anyway
            "yellow_vulnerability": self._threshold(previous["yellow_vulnerability"], vulnerability, c.yellow_vulnerability),
            "yellow_diffusion": self._threshold(previous["yellow_diffusion"], diffusion, c.yellow_diffusion_share),
        }
        self.active = now
        return tuple(rule for rule in _RULE_LEVEL if now[rule])

    def _threshold(self, was_active: bool, value: float | None, threshold: float) -> bool:
        if value is None:
            return False
        return value >= threshold or (was_active and value >= threshold - self.config.hysteresis)

    def _vix_ratio(self, was_active: bool, ratio: float | None) -> bool:
        """On after `red_vix_ratio_days` days above the threshold in a row, off after as many below (L-7).

        A day without a same-day ratio breaks both runs but does not end an active rule.
        """
        c = self.config
        if ratio is None:
            self.days_above = self.days_below = 0
            return was_active
        above, below = ratio > c.red_vix_ratio, ratio < c.red_vix_ratio
        self.days_above = self.days_above + 1 if above else 0
        self.days_below = self.days_below + 1 if below else 0
        if was_active:
            return self.days_below < c.red_vix_ratio_days
        return self.days_above >= c.red_vix_ratio_days


def _ewma(previous: float | None, value: float | None, half_life: float) -> float | None:
    """Exponentially weighted mean with the given half-life in score days; restarts after a gap."""
    if value is None:
        return None
    if previous is None:
        return value
    alpha = 1.0 - 0.5 ** (1.0 / half_life)
    return alpha * value + (1.0 - alpha) * previous


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _number(value) -> float | None:
    return None if value is None or np.isnan(value) else float(value)
