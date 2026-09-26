"""Load the TOML configuration in config/ and check it.

load() checks the top-level structure of any file; series_catalog() checks the raw
series in series.toml (M2), indicator_catalog() the derived indicators and
scoring_config() the parameters in scoring.toml (M5, docs/umsetzungsplan.md).
"""

import math
import re
import tomllib
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

# Allowed top-level tables per file; anything else is an error (typo protection).
_ALLOWED_TABLES = {
    "series": {"series", "indicator"},
    "scoring": {"percentile", "transforms", "composite", "smoothing", "rules"},
}
# Files whose tables hold one sub-table per entry ([series.vix]); the others hold values.
_NESTED = {"series"}


class ConfigError(Exception):
    """Configuration file missing, unreadable or structurally invalid."""


def load(name: str, config_dir: Path = CONFIG_DIR) -> dict:
    """Read config/<name>.toml and check its top-level structure."""
    if name not in _ALLOWED_TABLES:
        raise ConfigError(f"Unbekannte Konfigurationsdatei: {name}.toml")
    path = config_dir / f"{name}.toml"
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError:
        raise ConfigError(f"Konfigurationsdatei fehlt: {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Ungültiges TOML in {path}: {exc}") from exc

    allowed = _ALLOWED_TABLES[name]
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ConfigError(f"Unbekannte Einträge in {path}: {', '.join(unknown)}")
    for table in allowed & set(data):
        if not isinstance(data[table], dict):
            raise ConfigError(f"'{table}' in {path} muss eine Tabelle sein")
        if name not in _NESTED:
            continue
        for entry_id, entry in data[table].items():
            if not isinstance(entry, dict):
                raise ConfigError(f"'{table}.{entry_id}' in {path} muss eine Tabelle sein")
    return data


# Decision E-10: tolerance in calendar days on top of the frequency; other values need a reason.
# Quarterly added with M4c (E-44).
STANDARD_TOLERANCE_DAYS = {"daily": 3, "weekly": 3, "monthly": 10, "quarterly": 10}
# Sources whose own identifiers are simple enough to be series ids (E-16); the others use
# "<source>_<short name>" with the exact identifier in source_id (E-35).
SOURCES = ("cboe", "fred", "ecb", "ofr", "fed", "cftc", "shiller", "cfe")
_OWN_ID_SOURCES = ("cboe", "fred")

_REQUIRED = {
    "source", "source_id", "name", "unit", "frequency",
    "release_time", "lag_days", "tolerance_days", "bounds",
}
_OPTIONAL = {"tolerance_reason", "license", "start", "lead_days", "group"}
# Series sharing one download (E-36) must share everything that decides when it is fetched.
_GROUP_FIELDS = ("source", "frequency", "release_time", "lag_days")
# Same rule as the raw archive (fever/store/raw.py), so every series id is a valid folder name.
_SERIES_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
_RELEASE_TIME = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])")


@dataclass(frozen=True)
class Series:
    """One raw series from series.toml; see the comment at the top of that file."""

    id: str
    source: str
    source_id: str
    name: str
    unit: str
    frequency: str
    release_time: time  # America/New_York
    lag_days: int
    tolerance_days: int
    lower: float
    upper: float
    tolerance_reason: str | None = None
    license: str | None = None
    start: date | None = None
    lead_days: int = 0
    group: str = ""  # download shared with other series (E-36); the series id if alone


def series_catalog(config_dir: Path = CONFIG_DIR) -> dict[str, Series]:
    """All raw series from series.toml, checked; any error names the entry."""
    data = load("series", config_dir)
    catalog = {series_id: _series(series_id, entry) for series_id, entry in data.get("series", {}).items()}
    for group, members in group_members(catalog).items():
        first = members[0]
        for series in members[1:]:
            for field in _GROUP_FIELDS:
                if getattr(series, field) != getattr(first, field):
                    raise ConfigError(
                        f"series.{series.id}: '{field}' weicht in Gruppe {group} von series.{first.id} ab"
                    )
        if group in catalog and catalog[group].group != group:
            raise ConfigError(f"Gruppe {group} heißt wie series.{group}, die zu einer anderen Gruppe gehört")
    seen: dict[tuple[str, str], str] = {}
    for series in catalog.values():
        key = (series.source, series.source_id)
        if key in seen:
            raise ConfigError(f"series.{series.id}: {key[0]}/{key[1]} ist schon als series.{seen[key]} eingetragen")
        seen[key] = series.id
    return catalog


def group_members(catalog: dict[str, Series]) -> dict[str, list[Series]]:
    """Series per download group, in catalogue order."""
    groups: dict[str, list[Series]] = {}
    for series in catalog.values():
        groups.setdefault(series.group, []).append(series)
    return groups


def _series(series_id: str, entry: dict) -> Series:
    def fail(message: str) -> ConfigError:
        return ConfigError(f"series.{series_id}: {message}")

    missing = sorted(_REQUIRED - set(entry))
    if missing:
        raise fail(f"Pflichtfelder fehlen: {', '.join(missing)}")
    unknown = sorted(set(entry) - _REQUIRED - _OPTIONAL)
    if unknown:
        raise fail(f"unbekannte Felder: {', '.join(unknown)}")

    for field in ("source_id", "name", "unit", "tolerance_reason", "license", "group"):
        if field in entry and not (isinstance(entry[field], str) and entry[field].strip()):
            raise fail(f"'{field}' muss ein nicht leerer Text sein")
    if not _SERIES_ID.fullmatch(series_id):
        raise fail("die ID darf nur Kleinbuchstaben, Ziffern, '_' und '-' enthalten")
    if entry["source"] not in SOURCES:
        raise fail(f"unbekannte Quelle {entry['source']!r} (erlaubt: {', '.join(SOURCES)})")
    if entry["source"] in _OWN_ID_SOURCES:
        # Decision E-16: the id is the source's own identifier in lower case.
        if series_id != entry["source_id"].lower():
            raise fail(f"die ID muss der Quellkennung in Kleinbuchstaben entsprechen ({entry['source_id'].lower()})")
    elif not series_id.startswith(f"{entry['source']}_"):
        raise fail(f"die ID muss mit '{entry['source']}_' beginnen (E-35)")
    if "group" in entry and not _SERIES_ID.fullmatch(entry["group"]):
        raise fail("'group' darf nur Kleinbuchstaben, Ziffern, '_' und '-' enthalten")
    if entry["frequency"] not in STANDARD_TOLERANCE_DAYS:
        raise fail(f"unbekannte Frequenz {entry['frequency']!r} (erlaubt: {', '.join(STANDARD_TOLERANCE_DAYS)})")

    match = _RELEASE_TIME.fullmatch(str(entry["release_time"]))
    if not isinstance(entry["release_time"], str) or not match:
        raise fail("'release_time' muss eine Uhrzeit \"HH:MM\" sein (America/New_York)")
    for field in ("lag_days", "tolerance_days", "lead_days"):
        if field in entry and not (_is_int(entry[field]) and entry[field] >= 0):
            raise fail(f"'{field}' muss eine ganze Zahl >= 0 sein")

    standard = STANDARD_TOLERANCE_DAYS[entry["frequency"]]
    if entry["tolerance_days"] != standard and "tolerance_reason" not in entry:
        raise fail(f"Toleranz weicht vom Standard {standard} ab (E-10); 'tolerance_reason' fehlt")
    if entry["tolerance_days"] == standard and "tolerance_reason" in entry:
        raise fail(f"'tolerance_reason' ohne Abweichung vom Standard {standard}")

    bounds = entry["bounds"]
    if not (
        isinstance(bounds, list)
        and len(bounds) == 2
        and all(isinstance(b, (int, float)) and not isinstance(b, bool) and math.isfinite(b) for b in bounds)
        and bounds[0] < bounds[1]
    ):
        raise fail("'bounds' muss [untere, obere] Grenze mit untere < obere sein")
    if "start" in entry and type(entry["start"]) is not date:
        raise fail("'start' muss ein Datum JJJJ-MM-TT ohne Uhrzeit sein")

    return Series(
        id=series_id,
        source=entry["source"],
        source_id=entry["source_id"],
        name=entry["name"],
        unit=entry["unit"],
        frequency=entry["frequency"],
        release_time=time(int(match.group(1)), int(match.group(2))),
        lag_days=entry["lag_days"],
        tolerance_days=entry["tolerance_days"],
        lower=float(bounds[0]),
        upper=float(bounds[1]),
        tolerance_reason=entry.get("tolerance_reason"),
        license=entry.get("license"),
        start=entry.get("start"),
        lead_days=entry.get("lead_days", 0),
        group=entry.get("group", series_id),
    )


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


# --- derived indicators (M5) ---------------------------------------------------------------------

# Transformation -> number of input series (definitions in fever/scoring/transforms.py).
TRANSFORMS = {
    "level": 1, "ratio": 2, "difference": 2, "vrp": 2, "stock_bond_corr": 2,
    "above_low": 1, "fx_change": 2, "fx_vol": 2, "yoy": 1, "cot_net_short": 3,
}
STRESS_BLOCKS = ("volatility", "credit", "macro", "breadth", "positioning")  # report 4.3, step 2
VULNERABILITY = "vulnerability"
# Calendar days per period; with the tolerance this gives E-10's limits 4 / 10 / 41 (quarterly 102).
FREQUENCY_DAYS = {"daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92}
_INDICATOR_REQUIRED = {"name", "series", "transform", "orientation", "block", "v_score"}
_INDICATOR_OPTIONAL = {"display_window"}


@dataclass(frozen=True)
class Indicator:
    """One derived indicator from series.toml; see the comment above [indicator.*] there."""

    id: str
    name: str
    series: tuple[Series, ...]
    transform: str
    orientation: str  # "high" or "low"
    block: str  # a stress block or VULNERABILITY
    v_score: int
    display_window: bool = False

    @property
    def frequency(self) -> str:
        return self.series[0].frequency

    @property
    def lag_days(self) -> int:
        return max(series.lag_days for series in self.series)

    @property
    def tolerance_days(self) -> int:
        return max(series.tolerance_days for series in self.series)


def indicator_catalog(config_dir: Path = CONFIG_DIR) -> dict[str, Indicator]:
    """All derived indicators from series.toml, checked against the raw series."""
    catalog = series_catalog(config_dir)
    entries = load("series", config_dir).get("indicator", {})
    return {indicator_id: _indicator(indicator_id, entry, catalog) for indicator_id, entry in entries.items()}


def _indicator(indicator_id: str, entry: dict, catalog: dict[str, Series]) -> Indicator:
    def fail(message: str) -> ConfigError:
        return ConfigError(f"indicator.{indicator_id}: {message}")

    missing = sorted(_INDICATOR_REQUIRED - set(entry))
    if missing:
        raise fail(f"Pflichtfelder fehlen: {', '.join(missing)}")
    unknown = sorted(set(entry) - _INDICATOR_REQUIRED - _INDICATOR_OPTIONAL)
    if unknown:
        raise fail(f"unbekannte Felder: {', '.join(unknown)}")
    if not _SERIES_ID.fullmatch(indicator_id):
        raise fail("die ID darf nur Kleinbuchstaben, Ziffern, '_' und '-' enthalten")
    if not (isinstance(entry["name"], str) and entry["name"].strip()):
        raise fail("'name' muss ein nicht leerer Text sein")
    if entry["transform"] not in TRANSFORMS:
        raise fail(f"unbekannte Transformation {entry['transform']!r} (erlaubt: {', '.join(TRANSFORMS)})")
    inputs = entry["series"]
    if not (isinstance(inputs, list) and all(isinstance(series_id, str) for series_id in inputs)):
        raise fail("'series' muss eine Liste von Reihen-IDs sein")
    if len(inputs) != TRANSFORMS[entry["transform"]]:
        raise fail(f"'{entry['transform']}' braucht {TRANSFORMS[entry['transform']]} Reihe(n), nicht {len(inputs)}")
    unknown_series = [series_id for series_id in inputs if series_id not in catalog]
    if unknown_series:
        raise fail(f"unbekannte Reihe(n): {', '.join(unknown_series)}")
    series = tuple(catalog[series_id] for series_id in inputs)
    if len({s.frequency for s in series}) != 1:
        raise fail("alle Reihen eines Indikators müssen dieselbe Frequenz haben")
    if entry["orientation"] not in ("high", "low"):
        raise fail("'orientation' muss \"high\" oder \"low\" sein")
    if entry["block"] not in (*STRESS_BLOCKS, VULNERABILITY):
        raise fail(f"unbekannter Block {entry['block']!r} (erlaubt: {', '.join((*STRESS_BLOCKS, VULNERABILITY))})")
    if not (_is_int(entry["v_score"]) and 1 <= entry["v_score"] <= 5):
        raise fail("'v_score' muss eine ganze Zahl von 1 bis 5 sein (Bericht, Tabelle 2)")
    if "display_window" in entry and not isinstance(entry["display_window"], bool):
        raise fail("'display_window' muss true oder false sein")
    return Indicator(
        id=indicator_id,
        name=entry["name"],
        series=series,
        transform=entry["transform"],
        orientation=entry["orientation"],
        block=entry["block"],
        v_score=entry["v_score"],
        display_window=entry.get("display_window", False),
    )


# --- scoring parameters (M5) ---------------------------------------------------------------------

# Every parameter of scoring.toml: table -> {key: type}. All are required; nothing has a default,
# so a missing or misspelt parameter is an error instead of a silent guess.
_SCORING_KEYS = {
    "percentile": {"window_years": int, "min_history_years": int, "display_window_years": int},
    "transforms": {
        "realized_vol_window": int, "correlation_window": int, "low_window": int,
        "fx_change_window": int, "fx_vol_window": int,
    },
    "composite": {"min_blocks": int, "min_vulnerability": int},
    "smoothing": {
        "fast_block": str, "fast_block_half_life": float, "stress_half_life": float,
        "vulnerability_half_life": float,
    },
    "rules": {
        "red_stress": float, "red_vix_ratio": float, "red_vix_ratio_days": int, "orange_stress": float,
        "orange_stress_with_vulnerability": float, "orange_vulnerability": float,
        "yellow_vulnerability": float, "yellow_diffusion_share": float, "yellow_diffusion_percentile": float,
        "hysteresis": float,
    },
}


@dataclass(frozen=True)
class ScoringConfig:
    """Parameters from scoring.toml; the key names are unique across its tables."""

    window_years: int
    min_history_years: int
    display_window_years: int
    realized_vol_window: int
    correlation_window: int
    low_window: int
    fx_change_window: int
    fx_vol_window: int
    min_blocks: int
    min_vulnerability: int
    fast_block: str
    fast_block_half_life: float
    stress_half_life: float
    vulnerability_half_life: float
    red_stress: float
    red_vix_ratio: float
    red_vix_ratio_days: int
    orange_stress: float
    orange_stress_with_vulnerability: float
    orange_vulnerability: float
    yellow_vulnerability: float
    yellow_diffusion_share: float
    yellow_diffusion_percentile: float
    hysteresis: float


def scoring_config(config_dir: Path = CONFIG_DIR) -> ScoringConfig:
    """All parameters from scoring.toml, checked for completeness, type and range."""
    data = load("scoring", config_dir)
    values = {}
    for table, keys in _SCORING_KEYS.items():
        entries = data.get(table, {})
        missing = sorted(set(keys) - set(entries))
        if missing:
            raise ConfigError(f"scoring.{table}: Parameter fehlen: {', '.join(missing)}")
        unknown = sorted(set(entries) - set(keys))
        if unknown:
            raise ConfigError(f"scoring.{table}: unbekannte Parameter: {', '.join(unknown)}")
        for key, kind in keys.items():
            value = entries[key]
            if kind is str:
                ok = isinstance(value, str)
            elif kind is int:
                ok = _is_int(value) and value > 0
            else:
                ok = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0
            if not ok:
                expected = {str: "ein Text", int: "eine ganze Zahl > 0", float: "eine Zahl > 0"}[kind]
                raise ConfigError(f"scoring.{table}.{key} muss {expected} sein")
            values[key] = float(value) if kind is float else value
    config = ScoringConfig(**values)
    if config.fast_block not in STRESS_BLOCKS:
        raise ConfigError(f"scoring.smoothing.fast_block: unbekannter Block {config.fast_block!r}")
    if not config.display_window_years < config.min_history_years <= config.window_years:
        raise ConfigError("scoring.percentile: erwartet display_window_years < min_history_years <= window_years")
    if config.min_blocks > len(STRESS_BLOCKS):
        raise ConfigError(f"scoring.composite.min_blocks: höchstens {len(STRESS_BLOCKS)} Blöcke")
    for key in ("red_stress", "orange_stress", "orange_stress_with_vulnerability", "orange_vulnerability",
                "yellow_vulnerability", "yellow_diffusion_share", "yellow_diffusion_percentile", "hysteresis"):
        if getattr(config, key) > 100:
            raise ConfigError(f"scoring.rules.{key}: höchstens 100 (Perzentilskala)")
    return config
