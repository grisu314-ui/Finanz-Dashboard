"""Test-wide fixtures. Tests never touch the network; sources are tested against fixtures."""

import socket
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise RuntimeError("Network access in tests is not allowed; use tests/fixtures/")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture
def alembic_config(tmp_path, monkeypatch):
    """Alembic config pointing at an empty data directory in tmp_path."""
    monkeypatch.setenv("FEVER_DATA", str(tmp_path))
    return Config(str(REPO / "alembic.ini"))


@pytest.fixture
def migrated_dir(alembic_config, tmp_path):
    """Data directory with a database migrated to head."""
    command.upgrade(alembic_config, "head")
    return tmp_path
