"""Data sources: one module per source that fetches and parses a raw series.

fever.sources.update checks the parsed rows and stores them. The source modules
import only from here, never from the update module.
"""

import csv
import io
import math
from dataclasses import dataclass
from datetime import date, datetime


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


def csv_column(content: bytes, date_header: str, date_format: str, column: str) -> list[Row]:
    """Rows of one named value column from a CSV whose first column holds the date.

    Empty cells are missing values and skipped. A changed first column, a missing value
    column or an unreadable cell is a SourceError, so a format change never goes unnoticed.
    """
    try:
        lines = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise SourceError(f"keine lesbare CSV-Datei: {exc}") from None
    if not lines or not lines[0] or lines[0][0].strip() != date_header:
        raise SourceError(f"unerwartete Kopfzeile: {str(lines[0] if lines else None)[:120]}")
    header = [name.strip() for name in lines[0]]
    if column not in header:
        raise SourceError(f"Spalte {column!r} fehlt in der Kopfzeile")
    index = header.index(column)
    rows = []
    for number, fields in enumerate(lines[1:], start=2):
        if not fields:
            continue
        if len(fields) != len(header):
            raise SourceError(f"Zeile {number}: {len(fields)} statt {len(header)} Felder")
        if fields[index].strip() == "":
            continue
        try:
            rows.append(Row(datetime.strptime(fields[0].strip(), date_format).date(), float(fields[index])))
        except ValueError:
            raise SourceError(f"Zeile {number}: unlesbar: {','.join(fields)[:120]}") from None
    return checked(rows)
