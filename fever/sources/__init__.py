"""Data sources: one module per source that fetches and parses a raw series.

fever.sources.update checks the parsed rows and stores them. The source modules
import only from here, never from the update module.
"""

import math
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Row:
    """One observation as published by the source."""

    obs_date: date
    value: float


class SourceError(RuntimeError):
    """The response does not have the expected format; nothing from it is stored."""


def checked(rows: list[Row]) -> list[Row]:
    """Checks every parser applies: at least one value, finite values, each date once. Sorted by date."""
    if not rows:
        raise SourceError("keine Werte in der Antwort")
    seen: set[date] = set()
    for row in rows:
        if not math.isfinite(row.value):
            raise SourceError(f"{row.obs_date:%d.%m.%Y}: ungültiger Wert {row.value!r}")
        if row.obs_date in seen:
            raise SourceError(f"{row.obs_date:%d.%m.%Y}: Datum doppelt")
        seen.add(row.obs_date)
    return sorted(rows, key=lambda row: row.obs_date)
