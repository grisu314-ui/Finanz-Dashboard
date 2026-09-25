"""Raw source responses, gzip-compressed under raw/, stored only when the content changed."""

import gzip
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Lower-case names only, so a source or key can never leave the raw/ directory.
_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")


def archive_raw(
    directory: Path, source: str, key: str, content: bytes, retrieved_at: datetime
) -> Path | None:
    """Write raw/<source>/<key>/<UTC time>_<hash>.gz unless the newest file has the same content.

    Returns the new file, or None if the content was unchanged.
    """
    for name in (source, key):
        if not _NAME.fullmatch(name):
            raise ValueError(f"Ungültiger Name für das Rohdatenarchiv: {name!r}")
    if retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError(f"Abrufzeit ohne Zeitzone: {retrieved_at!r}")

    digest = hashlib.sha256(content).hexdigest()[:16]
    folder = directory / "raw" / source / key
    folder.mkdir(parents=True, exist_ok=True)
    existing = sorted(folder.glob("*.gz"))
    if existing and existing[-1].name.endswith(f"_{digest}.gz"):
        return None

    stamp = retrieved_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = folder / f"{stamp}_{digest}.gz"
    partial = folder / f"{target.name}.partial"
    with gzip.open(partial, "wb") as fh:
        fh.write(content)
    os.replace(partial, target)
    return target
