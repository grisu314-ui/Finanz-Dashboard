"""German display formats: decimal comma, DD.MM.YYYY, Europe/Berlin with MEZ/MESZ, relative age."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")
DASH = "–"
_ZONE = {"CET": "MEZ", "CEST": "MESZ"}


def number(value: float | None, decimals: int = 1) -> str:
    """1234.5 -> '1.234,5'; None -> '–'."""
    if value is None:
        return DASH
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def day(value: date | None) -> str:
    return DASH if value is None else f"{value:%d.%m.%Y}"


def berlin(value: datetime | None) -> str:
    """UTC timestamp -> '26.09.2026, 14:47 MESZ'."""
    if value is None:
        return DASH
    local = value.astimezone(BERLIN)
    return f"{local:%d.%m.%Y, %H:%M} {_ZONE.get(local.tzname(), local.tzname())}"


def age(value: datetime | None, now: datetime) -> str:
    """Relative age in German: 'vor 5 Min.', 'vor 3 Std.', 'vor 2 Tagen'."""
    if value is None:
        return DASH
    seconds = (now - value).total_seconds()
    if seconds < 60:
        return "gerade eben"
    if seconds < 3600:
        return f"vor {int(seconds // 60)} Min."
    if seconds < 2 * 86400:
        return f"vor {int(seconds // 3600)} Std."
    return f"vor {int(seconds // 86400)} Tagen"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
