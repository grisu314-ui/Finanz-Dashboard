"""Backtest of the traffic light (M10, report 4.3 step 7, decisions E-89 and E-93).

Pure computation on pandas Series indexed by date: S&P 500 and VIX closes, the stored daily scores
and the stored VIX percentile. No database, no web. Nothing here feeds back into the scores
(CLAUDE.md: no thresholds optimised in a backtest), and nothing is a probability for today.

Events (report 4.3 step 7; parameters in scoring.toml [validation]):
  drawdown  a decline of the S&P 500 of at least `drawdown` percent begins within the next
            `drawdown_horizon` trading days
  vix       the VIX closes above `vix_level` on one of the next `vix_horizon` trading days
  bear      like drawdown with `bear` percent and `bear_horizon`
Declines follow Lunde and Timmermann (2004) with the same threshold in both directions: a decline
starts at a closing high once a close lies `threshold` percent below it and ends at the closing low
once a close lies `threshold` percent above that low; the next high counts from there. The event
begins on the first trading day after the high. A day whose horizon reaches past the data, or into
a decline that is not confirmed yet, has no outcome and is left out (censoring at the end).

Signals: the traffic light levels (fixed rules, never calibrated), the continuous stress,
vulnerability, level and VIX percentile. Benchmarks: a VIX percentile filter with the same share
of alarm days as a level, its threshold recalibrated every year from `walk_forward_start` with the
earlier years only (no outcomes needed, so no look-ahead); the VIX percentile above the "erhöht"
mark; "always alarm", i.e. the base rate. Confidence intervals: moving-block bootstrap.

Estimated weights (M11, E-94; evaluation only, the scores keep their equal weights): per year from
`walk_forward_start` a logit on the smoothed stress blocks `fit_blocks` (A) and on them plus the
vulnerability (B), fitted on the earlier days whose outcome was known at the start of the year, the
outcomes taken from the closes before that day. Compared with the equal-weight mean of the same
blocks, the stress and the VIX percentile, and at the alarm shares of the levels with the levels.
"""

import copy
import math
from dataclasses import asdict, dataclass
from datetime import date

import numpy as np
import pandas as pd

from fever.config import ValidationConfig

EVENTS = ("drawdown", "vix", "bear")
LEVELS = (1, 2, 3)  # at least yellow, at least orange, red
SIGNALS = ("stress", "vulnerability", "level", "vix")  # continuous; high = more stress
TRADING_DAYS_PER_YEAR = 252
ROC_POINTS = 150  # points of a stored ROC curve
SEED = 20260929  # fixed: the same data give the same intervals
FITTED_EVENTS = ("drawdown", "vix")  # bear markets: too few events to estimate weights (M11)
FITTED_SIGNALS = ("fitted", "fitted_vulnerability", "equal", "stress", "vix")
VULNERABILITY_FEATURE = "vulnerability"
NEWTON_STEPS = 50
# Comparisons: M10 stress against VIX percentile and each level against its VIX filter; M11 the estimated
# weights against equal weights, stress and VIX percentile, B against A, each fitted filter against its level.
M10_AUC_PAIRS = (("stress", "vix"),)
M10_PRECISION_PAIRS = {f"level{k}": f"vix{k}" for k in LEVELS}
FITTED_AUC_PAIRS = (("fitted", "equal"), ("fitted_vulnerability", "fitted"), ("fitted", "stress"), ("fitted", "vix"))
FITTED_PRECISION_PAIRS = {f"fitted{k}": f"level{k}" for k in LEVELS}


@dataclass(frozen=True)
class Decline:
    high: date  # closing high the decline starts from
    low: date  # closing low so far
    depth: float  # percent below the high at the low
    start: date  # first trading day after the high: the event begins
    ended: bool  # the low is confirmed by a rise of the same threshold


def declines(prices: pd.Series, threshold: float) -> tuple[list[Decline], date | None]:
    """Declines of at least `threshold` percent, oldest first, and the running high from which a
    decline could still begin (None while a decline is under way)."""
    values = prices.to_numpy(dtype=float)
    days = list(prices.index)
    found: list[Decline] = []
    high, low, falling = 0, 0, False
    for i in range(1, len(values)):
        if not falling:
            if values[i] > values[high]:
                high = i
            elif _change(values[high], values[i]) <= -threshold:
                falling, low = True, i
        elif values[i] < values[low]:
            low = i
        elif _change(values[low], values[i]) >= threshold:
            found.append(_decline(days, values, high, low, ended=True))
            falling, high = False, i  # the highest close since the low is this one
    if falling:
        found.append(_decline(days, values, high, low, ended=False))
        return found, None
    return found, (days[high] if days else None)


def _change(base: float, value: float) -> float:
    """Percent change, rounded so that float noise never decides a threshold."""
    return round(100.0 * (value / base - 1.0), 10)


def _decline(days, values, high, low, *, ended) -> Decline:
    return Decline(days[high], days[low], round(100.0 * (1.0 - values[low] / values[high]), 4), days[high + 1], ended)


def start_labels(days: list[date], starts: list[date], horizon: int, known_until: date | None) -> pd.Series:
    """1.0 if an event begins within the next `horizon` days of `days` (the day itself excluded),
    0.0 if not, NaN if the outcome is not known yet: the horizon reaches past `known_until`
    (the last day that cannot begin an unknown event) or past the data."""
    n = len(days)
    position = {day: i for i, day in enumerate(days)}
    marks = np.zeros(n)
    for start in starts:
        marks[position[start]] = 1.0
    cumulative = np.concatenate([[0.0], np.cumsum(marks)])
    index = np.arange(n)
    end = np.minimum(index + horizon, n - 1)
    labels = (cumulative[end + 1] - cumulative[index + 1] > 0).astype(float)
    last = n - 1 if known_until is None else position[known_until]
    labels[index + horizon > last] = np.nan
    return pd.Series(labels, index=days)


def level_labels(values: pd.Series, level: float, horizon: int) -> pd.Series:
    """1.0 if a close above `level` follows within the next `horizon` days, NaN at the end of the data."""
    ahead = values.rolling(horizon).max().shift(-horizon)
    return (ahead > level).astype(float).where(ahead.notna())


def level_episodes(values: pd.Series, level: float, horizon: int) -> list[tuple[date, date, float]]:
    """Closes above `level` as episodes (first day, last day, highest close); a new one begins only after
    at least `horizon` closes at or below the level."""
    days, closes = list(values.index), values.to_numpy(dtype=float)
    episodes: list[list] = []
    last_above = None
    for i, close in enumerate(closes):
        if close <= level:
            continue
        if last_above is None or i - last_above > horizon:
            episodes.append([days[i], days[i], close])
        else:
            episodes[-1][1], episodes[-1][2] = days[i], max(episodes[-1][2], close)
        last_above = i
    return [(first, last, high) for first, last, high in episodes]


def alarm_episodes(flags: np.ndarray, gap: int) -> list[tuple[int, int]]:
    """Alarm days as episodes (first, last position); alarm days at most `gap` positions apart share one."""
    episodes: list[list[int]] = []
    for i in np.flatnonzero(flags):
        if episodes and i - episodes[-1][1] <= gap:
            episodes[-1][1] = int(i)
        else:
            episodes.append([int(i), int(i)])
    return [(first, last) for first, last in episodes]


def lead(flags: np.ndarray, start: int, horizon: int) -> int | None:
    """Trading days from the first alarm among the `horizon` days before `start` to `start`; None if none."""
    first = max(0, start - horizon)
    on = np.flatnonzero(flags[first:start])
    return None if len(on) == 0 else int(start - (first + on[0]))


def walk_forward_thresholds(days: list[date], level: np.ndarray, vix: np.ndarray, first_year: int,
                            last_year: int) -> dict[int, dict[int, float]]:
    """Per year from `first_year`: for each traffic light level the VIX percentile at or above which the
    VIX filter gave the same share of alarm days as the level in all earlier years (days with both)."""
    years = np.array([day.year for day in days])
    valid = ~np.isnan(level) & ~np.isnan(vix)
    thresholds: dict[int, dict[int, float]] = {}
    for year in range(first_year, last_year + 1):
        past = valid & (years < year)
        thresholds[year] = {}
        for k in LEVELS:
            share = float(np.mean(level[past] >= k)) if past.any() else 0.0
            thresholds[year][k] = math.inf if share == 0.0 else float(np.quantile(vix[past], 1.0 - share))
    return thresholds


def labels_known_at(event: str, spx: pd.Series, vix: pd.Series, cutoff: date, config: ValidationConfig) -> pd.Series:
    """Outcomes of an event as they were known on `cutoff`: from the closes before it only, so a decline that
    reaches its threshold on or after the cutoff does not exist yet (its days stay without outcome)."""
    if event == "vix":
        return level_labels(vix[vix.index < cutoff], config.vix_level, config.vix_horizon)
    threshold, horizon = ((config.drawdown, config.drawdown_horizon) if event == "drawdown"
                          else (config.bear, config.bear_horizon))
    prices = spx[spx.index < cutoff]
    found, pending = declines(prices, threshold)
    return start_labels(list(prices.index), [d.start for d in found], horizon, pending)


def fit_logit(x: np.ndarray, y: np.ndarray, ridge: float) -> np.ndarray:
    """Logistic regression by Newton's method: intercept and slopes maximising the log-likelihood minus
    ridge / 2 times the sum of the squared slopes (x: days x features, y: 0/1 with both present)."""
    design = np.column_stack([np.ones(len(x)), x])
    penalty = np.full(design.shape[1], float(ridge))
    penalty[0] = 0.0
    beta = np.zeros(design.shape[1])
    for _ in range(NEWTON_STEPS):
        p = 0.5 * (1.0 + np.tanh(0.5 * (design @ beta)))  # the logistic function without overflow
        gradient = design.T @ (y - p) - penalty * beta
        hessian = (design * (p * (1.0 - p))[:, None]).T @ design + np.diag(penalty)
        step = np.linalg.solve(hessian, gradient)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    return beta


@dataclass(frozen=True)
class Fit:
    """The logit of one year: standardisation and coefficients from the earlier days only."""

    year: int
    features: tuple[str, ...]
    mean: np.ndarray
    scale: np.ndarray
    beta: np.ndarray  # intercept first, then one slope per standardised feature
    days: int  # training days
    positives: int  # of them followed by the event

    def weights(self) -> np.ndarray:
        """Weight of each feature on its own 0-100 scale, the absolute weights summing to 1 (equal weights:
        1 / number of features each); a negative weight means the feature counts against. NaN if all are 0."""
        raw = self.beta[1:] / self.scale
        total = float(np.abs(raw).sum())
        return raw / total if total else np.full(len(raw), np.nan)

    def signal(self, x: np.ndarray) -> np.ndarray:
        """The features weighted with these weights, on the 0-100 scale of the blocks like the stress. Without
        the intercept: it moves with every yearly fit and would mix the scales of the years; so the signal
        differs from the equal-weight mean in the weights alone. A ranking, never a probability (CLAUDE.md)."""
        return x @ self.weights()

    def shares(self) -> dict[str, float | None]:
        """The weights in percent."""
        return {name: _round(100.0 * w, 1) for name, w in zip(self.features, self.weights())}


def fit_year(year: int, x: np.ndarray, known: np.ndarray, years: np.ndarray, names: tuple[str, ...],
             ridge: float) -> Fit | None:
    """The logit for `year` from the days before it with every feature and a known outcome (`known`: the
    outcomes as known at the start of the year); None without both outcomes among them."""
    train = (years < year) & ~np.isnan(x).any(axis=1) & ~np.isnan(known)
    y = known[train]
    if not 0 < y.sum() < len(y):
        return None
    mean, scale = x[train].mean(axis=0), x[train].std(axis=0)
    scale = np.where(scale > 0, scale, 1.0)
    beta = fit_logit((x[train] - mean) / scale, y, ridge)
    return Fit(year, names, mean, scale, beta, int(train.sum()), int(y.sum()))


def _fitted(event, spx, vix, days, years, features: pd.DataFrame, level, config):
    """Walk-forward logits of one event: the signals A and B per day, the alarm flags of A at the alarm
    shares the levels had in the earlier years (like the VIX filter), and per year the fits."""
    variants = {"fitted": tuple(config.fit_blocks), "fitted_vulnerability": (*config.fit_blocks, VULNERABILITY_FEATURE)}
    n = len(days)
    signals = {key: np.full(n, np.nan) for key in variants}
    flags = {f"fitted{k}": np.zeros(n, dtype=bool) for k in LEVELS}
    per_year = []
    last_year = days[-1].year if days else config.walk_forward_start
    for year in range(config.walk_forward_start, last_year + 1):
        known = labels_known_at(event, spx, vix, date(year, 1, 1), config).reindex(days).to_numpy(dtype=float)
        entry = {"year": year}
        for key, names in variants.items():
            x = features[list(names)].to_numpy(dtype=float)
            fit = fit_year(year, x, known, years, names, config.fit_ridge)
            if fit is None:
                continue
            complete = ~np.isnan(x).any(axis=1)
            scored = (years == year) & complete
            signals[key][scored] = fit.signal(x[scored])
            entry[key] = {"shares": fit.shares(), "days": fit.days, "positives": fit.positives}
            if key == "fitted":
                reference = (years < year) & complete & ~np.isnan(level)
                past = fit.signal(x[reference])
                for k in LEVELS:
                    share = float(np.mean(level[reference] >= k)) if reference.any() else 0.0
                    threshold = math.inf if share == 0.0 else float(np.quantile(past, 1.0 - share))
                    flags[f"fitted{k}"][scored] = signals[key][scored] >= threshold
        per_year.append(entry)
    return signals, flags, per_year


class _Ranked:
    """AUC of one continuous signal against 0/1 outcomes, for any day weights (bootstrap).

    Mann-Whitney with ties counted half: sum over positive days of the weight of negative days with a
    lower value plus half the weight of those with the same value, over (positive weight x negative weight).
    """

    def __init__(self, values: np.ndarray, outcomes: np.ndarray):
        self.unique, self.group = np.unique(values, return_inverse=True)
        self.positive = outcomes == 1
        self.size = len(self.unique)

    def weights(self, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        positive = np.bincount(self.group, weights=w * self.positive, minlength=self.size)
        negative = np.bincount(self.group, weights=w * ~self.positive, minlength=self.size)
        return positive, negative

    def auc(self, w: np.ndarray) -> float:
        positive, negative = self.weights(w)
        total_p, total_n = positive.sum(), negative.sum()
        if total_p == 0 or total_n == 0:
            return math.nan
        below = np.cumsum(negative) - negative
        return float((positive * (below + 0.5 * negative)).sum() / (total_p * total_n))

    def roc(self, points: int = ROC_POINTS) -> tuple[list[float], list[float]]:
        """False and true positive rates for every threshold from the highest value down, thinned out."""
        positive, negative = self.weights(np.ones(len(self.group)))
        tpr = np.concatenate([[0.0], np.cumsum(positive[::-1]) / max(positive.sum(), 1.0)])
        fpr = np.concatenate([[0.0], np.cumsum(negative[::-1]) / max(negative.sum(), 1.0)])
        if len(fpr) > points:
            keep = np.unique(np.round(np.linspace(0, len(fpr) - 1, points)).astype(int))
            fpr, tpr = fpr[keep], tpr[keep]
        return [round(float(v), 4) for v in fpr], [round(float(v), 4) for v in tpr]


def auc(values, outcomes) -> float:
    """Unweighted AUC (see _Ranked)."""
    values, outcomes = np.asarray(values, dtype=float), np.asarray(outcomes, dtype=float)
    return _Ranked(values, outcomes).auc(np.ones(len(values)))


def precision_recall(flags: np.ndarray, outcomes: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """Weighted share of alarm days followed by the event, and of event days with an alarm."""
    positive = outcomes == 1
    hits = float(w @ (flags & positive))
    alarms = float(w @ flags)
    events = float(w @ positive)
    return (hits / alarms if alarms else math.nan), (hits / events if events else math.nan)


def block_weights(n: int, block: int, samples: int, seed: int = SEED):
    """Moving-block bootstrap: how often each of n days is drawn, per resample of n days."""
    rng = np.random.default_rng(seed)
    block = max(1, min(block, n))
    count = -(-n // block)
    for _ in range(samples):
        starts = rng.integers(0, n - block + 1, size=count)
        drawn = (starts[:, None] + np.arange(block)).ravel()[:n]
        yield np.bincount(drawn, minlength=n).astype(float)


def interval(values: list[float], estimate: float, confidence: float) -> dict:
    """Estimate with the percentile interval of the bootstrap values."""
    tail = (100.0 - confidence) / 2.0
    finite = np.asarray([v for v in values if not math.isnan(v)])
    low, high = (np.percentile(finite, [tail, 100.0 - tail]) if len(finite) else (math.nan, math.nan))
    return {"value": _round(estimate), "low": _round(low), "high": _round(high)}


def verdict(difference: dict) -> str:
    """'better' if the whole interval lies above zero, 'worse' if below, else 'same' (not distinguishable)."""
    if difference["low"] is not None and difference["low"] > 0:
        return "better"
    if difference["high"] is not None and difference["high"] < 0:
        return "worse"
    return "same"


def _round(value, digits: int = 4):
    value = float(value)
    return None if math.isnan(value) or math.isinf(value) else round(value, digits)


def validate(spx: pd.Series, vix: pd.Series, scores: pd.DataFrame, vix_percentile: pd.Series,
             config: ValidationConfig, elevated: float, blocks: pd.DataFrame | None = None) -> dict:
    """The report stored in validation_report (JSON-ready dict).

    scores: stored composite per score day, columns level, stress, vulnerability (NaN where missing);
    vix_percentile: stored percentile of the VIX indicator on the days it was valid;
    elevated: the "erhöht" mark (scoring.toml yellow_diffusion_percentile);
    blocks: the stress blocks `fit_blocks` smoothed like the composite, per score day (M11); None: no M11 part.
    """
    scores = scores.sort_index()
    days = list(scores.index)
    frame = scores.join(vix_percentile.rename("vix"), how="left")
    signals = {name: frame[name].to_numpy(dtype=float) for name in SIGNALS}
    level = signals["level"]
    years = np.array([day.year for day in days])
    last_year = days[-1].year if days else config.walk_forward_start
    thresholds = walk_forward_thresholds(days, level, signals["vix"], config.walk_forward_start, last_year)
    flags = _filters(years, level, signals["vix"], thresholds, elevated, config.walk_forward_start)
    events = {}
    for event in EVENTS:
        labels, occurrences, horizon = _event(event, spx, vix, days, config)
        result = _evaluate(days, years, signals, flags, labels, occurrences, horizon, config,
                           auc_pairs=M10_AUC_PAIRS, precision_pairs=M10_PRECISION_PAIRS)
        result["auc_difference"] = result.pop("auc_differences").get("stress-vix")
        if blocks is not None and event in FITTED_EVENTS:
            features = blocks.reindex(days).join(scores["vulnerability"].rename(VULNERABILITY_FEATURE))
            fitted, fitted_flags, per_year = _fitted(event, spx, vix, days, years, features, level, config)
            equal = features[list(config.fit_blocks)].mean(axis=1, skipna=False).to_numpy(dtype=float)
            result["fitted"] = _evaluate(
                days, years, {**fitted, "equal": equal, "stress": signals["stress"], "vix": signals["vix"]},
                {**{f"level{k}": flags[f"level{k}"] for k in LEVELS}, **fitted_flags}, labels,
                copy.deepcopy(occurrences), horizon, config, auc_pairs=FITTED_AUC_PAIRS,
                precision_pairs=FITTED_PRECISION_PAIRS, details=False)
            result["fitted"]["years"] = per_year
        events[event] = result
    return {
        "config": asdict(config),
        "elevated": elevated,
        "events": events,
        "thresholds": {str(year): {str(k): _round(v, 2) for k, v in by_level.items()} for year, by_level in thresholds.items()},
    }


def _event(event: str, spx: pd.Series, vix: pd.Series, days: list[date], config: ValidationConfig):
    """Outcome per score day and the occurrences (start, description) of one event."""
    if event == "vix":
        labels = level_labels(vix, config.vix_level, config.vix_horizon).reindex(days)
        occurrences = [{"start": first.isoformat(), "end": last.isoformat(), "max": _round(high, 2)}
                       for first, last, high in level_episodes(vix, config.vix_level, config.vix_horizon)]
        return labels.to_numpy(dtype=float), occurrences, config.vix_horizon
    threshold, horizon = ((config.drawdown, config.drawdown_horizon) if event == "drawdown"
                          else (config.bear, config.bear_horizon))
    found, pending = declines(spx, threshold)
    labels = start_labels(list(spx.index), [d.start for d in found], horizon, pending).reindex(days)
    occurrences = [{"start": d.start.isoformat(), "high": d.high.isoformat(), "low": d.low.isoformat(),
                    "depth": _round(d.depth, 1), "ended": d.ended} for d in found]
    return labels.to_numpy(dtype=float), occurrences, horizon


def _filters(years, level, vix, thresholds, elevated, first_year) -> dict[str, np.ndarray]:
    """Alarm flags per score day: the levels, the walk-forward VIX filters (from first_year), the fixed
    VIX filter above the "erhöht" mark and "always alarm"."""
    with np.errstate(invalid="ignore"):
        flags = {f"level{k}": level >= k for k in LEVELS}
        for k in LEVELS:
            limit = np.array([thresholds.get(year, {}).get(k, math.inf) for year in years])
            flags[f"vix{k}"] = (years >= first_year) & (vix >= limit)
        flags["vix_elevated"] = vix > elevated
    flags["always"] = np.ones(len(years), dtype=bool)
    return flags


def _evaluate(days, years, signals, flags, labels, occurrences, horizon, config, *, auc_pairs, precision_pairs,
              details=True) -> dict:
    """All metrics of one event over the days from walk_forward_start with a known outcome and every signal:
    AUC per signal and the AUC differences of `auc_pairs`; per alarm filter precision, recall, leads and
    false alarms, with the precision difference against its partner in `precision_pairs`. `details` adds
    the occurrences with their leads and the periods (M10 only)."""
    known = ~np.isnan(labels) & np.all([~np.isnan(values) for values in signals.values()], axis=0)
    mask = known & (years >= config.walk_forward_start)
    chosen = np.flatnonzero(mask)
    outcomes = labels[chosen]
    result = {"horizon": horizon, "days": int(len(chosen)), "positives": int(np.sum(outcomes == 1)),
              "first": days[chosen[0]].isoformat() if len(chosen) else None,
              "last": days[chosen[-1]].isoformat() if len(chosen) else None,
              "base_rate": _round(np.mean(outcomes == 1)) if len(chosen) else None}
    if len(chosen) == 0 or result["positives"] == 0 or result["positives"] == len(chosen):
        result.update(auc={}, roc={}, auc_differences={}, filters=[])
        if details:
            result.update(occurrences=occurrences, periods=[])
        return result

    ranked = {name: _Ranked(values[chosen], outcomes) for name, values in signals.items()}
    chosen_flags = {name: flag[chosen] for name, flag in flags.items()}
    ones = np.ones(len(chosen))
    estimates = {name: r.auc(ones) for name, r in ranked.items()}
    point = {name: precision_recall(flag, outcomes, ones) for name, flag in chosen_flags.items()}
    samples = {name: [] for name in ranked}
    samples_difference = {pair: [] for pair in auc_pairs}
    samples_pr = {name: ([], []) for name in chosen_flags}
    samples_precision_difference = {name: [] for name in precision_pairs}
    for w in block_weights(len(chosen), config.bootstrap_block, config.bootstrap_samples):
        aucs = {name: r.auc(w) for name, r in ranked.items()}
        for name, value in aucs.items():
            samples[name].append(value)
        for a, b in auc_pairs:
            samples_difference[(a, b)].append(aucs[a] - aucs[b])
        prs = {name: precision_recall(flag, outcomes, w) for name, flag in chosen_flags.items()}
        for name, (p, r) in prs.items():
            samples_pr[name][0].append(p)
            samples_pr[name][1].append(r)
        for name, other in precision_pairs.items():
            samples_precision_difference[name].append(prs[name][0] - prs[other][0])

    confidence = config.confidence
    differences = {}
    for a, b in auc_pairs:
        difference = interval(samples_difference[(a, b)], estimates[a] - estimates[b], confidence)
        difference["verdict"] = verdict(difference)
        differences[f"{a}-{b}"] = difference
    starts = _start_positions(days, occurrences)
    usable = [(i, s) for i, s in enumerate(starts) if s is not None and s - horizon >= chosen[0]]
    filters = []
    for name, flag in flags.items():
        precision_value, recall_value = point[name]
        leads = [lead(flag, s, horizon) for _, s in usable]
        false_alarms = [(first, last) for first, last in alarm_episodes(flag & mask, config.episode_gap)
                        if not np.any(labels[first:last + 1][mask[first:last + 1]] == 1)]
        entry = {
            "id": name, "share": _round(np.mean(chosen_flags[name])),
            "precision": interval(samples_pr[name][0], precision_value, confidence),
            "recall": interval(samples_pr[name][1], recall_value, confidence),
            "warned": sum(v is not None for v in leads), "events": len(leads),
            "leads": leads, "lead_median": _round(np.median([v for v in leads if v is not None]), 1)
            if any(v is not None for v in leads) else None,
            "false_alarms": [[days[first].isoformat(), days[last].isoformat()] for first, last in false_alarms],
            "false_per_year": _round(len(false_alarms) / (len(chosen) / TRADING_DAYS_PER_YEAR), 2),
        }
        if name in precision_pairs:
            other = precision_pairs[name]
            comparison = interval(samples_precision_difference[name], precision_value - point[other][0], confidence)
            comparison["verdict"] = verdict(comparison)
            entry["precision_difference"] = comparison
        filters.append(entry)
    result.update(
        auc={name: interval(samples[name], estimates[name], confidence) for name in ranked},
        roc={name: r.roc() for name, r in ranked.items()},
        auc_differences=differences,
        filters=filters,
    )
    if details:
        for position, (index, start) in enumerate(usable):
            occurrences[index]["leads"] = {entry["id"]: entry["leads"][position] for entry in filters}
        result.update(occurrences=occurrences,
                      periods=_periods(years, signals, labels, known, occurrences, config.walk_forward_start))
    return result


def _start_positions(days: list[date], occurrences: list[dict]) -> list[int | None]:
    """Position of each event start among the score days (the first score day on or after it)."""
    ordinals = np.array([day.toordinal() for day in days])
    positions = []
    for occurrence in occurrences:
        position = int(np.searchsorted(ordinals, date.fromisoformat(occurrence["start"]).toordinal()))
        positions.append(position if position < len(days) else None)
    return positions


def _periods(years, signals, labels, known, occurrences, first_year) -> list[dict]:
    """AUC of stress and VIX percentile per period (days with a known outcome and every signal), with the
    number of events beginning in it: the years before the walk-forward, then decades from it on. Without
    an event beginning in the period there is no AUC: its only positive days would be the last weeks
    before an event of the next period."""
    bounds = [(0, first_year - 1), (first_year, first_year + 9), (first_year + 10, first_year + 19), (first_year + 20, 9999)]
    starts = [date.fromisoformat(occurrence["start"]).year for occurrence in occurrences]
    periods = []
    for low, high in bounds:
        chosen = np.flatnonzero(known & (years >= low) & (years <= high))
        if len(chosen) == 0:
            continue
        outcomes = labels[chosen]
        first, last = int(years[chosen[0]]), int(years[chosen[-1]])
        period = {"from": first, "to": last, "days": int(len(chosen)),
                  "events": sum(first <= year <= last for year in starts), "auc_stress": None, "auc_vix": None}
        if period["events"] and 0 < np.sum(outcomes == 1) < len(chosen):
            period["auc_stress"] = _round(auc(signals["stress"][chosen], outcomes))
            period["auc_vix"] = _round(auc(signals["vix"][chosen], outcomes))
        periods.append(period)
    return periods
