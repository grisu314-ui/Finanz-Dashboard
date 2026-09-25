"""Logging setup: stdout only; compose limits the log size."""

import logging
import sys


def setup(level: int = logging.INFO) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,  # replace handlers set earlier in the process (e.g. by Alembic)
    )
