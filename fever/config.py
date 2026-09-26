"""Load the TOML configuration in config/ and check it.

load() checks the top-level structure of any file; series_catalog() also checks
the content of the raw series in series.toml (milestone M2). Rules for
indicators and scoring parameters follow in M5 (docs/umsetzungsplan.md).
"""

import math
import re
import tomllib
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

# Allowed top-level tables per file; anything else is an error (typo protection).
# scoring.toml stays empty until the open domain gaps L-1 to L-13 are decided (M5).
_ALLOWED_TABLES = {
    "series": {"series", "indicator"},
    "scoring": set(),
}


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
        for entry_id, entry in data[table].items():
            if not isinstance(entry, dict):
                raise ConfigError(f"'{table}.{entry_id}' in {path} muss eine Tabelle sein")
    return data


# Decision E-10: tolerance in calendar days on top of the frequency; other values need a reason.
STANDARD_TOLERANCE_DAYS = {"daily": 3, "weekly": 3, "monthly": 10}
SOURCES = ("cboe", "fred")

_REQUIRED = {
    "source", "source_id", "name", "unit", "frequency",
    "release_time", "lag_days", "tolerance_days", "bounds",
}
_OPTIONAL = {"tolerance_reason", "license", "start", "lead_days"}
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


def series_catalog(config_dir: Path = CONFIG_DIR) -> dict[str, Series]:
    """All raw series from series.toml, checked; any error names the entry."""
    data = load("series", config_dir)
    # The id is the source identifier in lower case (E-16), so a duplicate source identifier
    # would be a duplicate TOML key, which tomllib already rejects.
    return {series_id: _series(series_id, entry) for series_id, entry in data.get("series", {}).items()}


def _series(series_id: str, entry: dict) -> Series:
    def fail(message: str) -> ConfigError:
        return ConfigError(f"series.{series_id}: {message}")

    missing = sorted(_REQUIRED - set(entry))
    if missing:
        raise fail(f"Pflichtfelder fehlen: {', '.join(missing)}")
    unknown = sorted(set(entry) - _REQUIRED - _OPTIONAL)
    if unknown:
        raise fail(f"unbekannte Felder: {', '.join(unknown)}")

    for field in ("source_id", "name", "unit", "tolerance_reason", "license"):
        if field in entry and not (isinstance(entry[field], str) and entry[field].strip()):
            raise fail(f"'{field}' muss ein nicht leerer Text sein")
    if not _SERIES_ID.fullmatch(series_id):
        raise fail("die ID darf nur Kleinbuchstaben, Ziffern, '_' und '-' enthalten")
    # Decision E-16: the id is the source's own identifier in lower case.
    if series_id != entry["source_id"].lower():
        raise fail(f"die ID muss der Quellkennung in Kleinbuchstaben entsprechen ({entry['source_id'].lower()})")
    if entry["source"] not in SOURCES:
        raise fail(f"unbekannte Quelle {entry['source']!r} (erlaubt: {', '.join(SOURCES)})")
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
    )


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
