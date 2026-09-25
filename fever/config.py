"""Load the TOML configuration in config/ and check its structure.

Only the top-level structure is checked here. Content rules for series,
indicators and scoring parameters are added with the milestones that use
them (M2, M5 in docs/umsetzungsplan.md).
"""

import tomllib
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
