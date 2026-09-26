"""Logging setup: stdout only (compose limits the log size), secrets masked."""

import logging
import os
import sys

# Environment variables whose values must never appear in logs or error messages.
SECRET_ENV_VARS = ("FRED_API_KEY",)
MASK = "***"


def mask(text: str) -> str:
    """Replace the values of known secrets in `text`."""
    for name in SECRET_ENV_VARS:
        secret = os.environ.get(name)
        if secret:
            text = text.replace(secret, MASK)
    return text


class MaskingFormatter(logging.Formatter):
    """Masks the fully formatted record, including tracebacks and third-party messages."""

    def format(self, record: logging.LogRecord) -> str:
        return mask(super().format(record))


def setup(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(MaskingFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    # force: replace handlers set earlier in the process (e.g. by Alembic).
    logging.basicConfig(level=level, handlers=[handler], force=True)
