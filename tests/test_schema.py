"""Migration check (E-70): entry points refuse to run and the web shows a banner on an outdated database."""

import logging

import pytest
from alembic import command
from sqlalchemy import text

from fever import score, worker
from fever.sources import update
from fever.store import schema
from fever.store.db import make_engine
from fever.store.status import read_heartbeat
from fever.web import db as web_db

REPO_VERSIONS = schema.MIGRATIONS / "versions"


@pytest.fixture
def outdated_dir(alembic_config, tmp_path):
    """Data directory whose database stopped one migration before head (like TrueNAS on 27.09.2026)."""
    command.upgrade(alembic_config, "0002")
    return tmp_path


def _problem(directory):
    engine = make_engine(directory)
    try:
        with engine.connect() as conn:
            return schema.problem(conn)
    finally:
        engine.dispose()


def test_expected_revision_is_the_newest_migration_file():
    newest = max(path.name.split("_")[0] for path in REPO_VERSIONS.glob("[0-9]*.py"))
    assert schema.expected_revision() == newest


def test_database_on_head_has_no_problem(migrated_dir):
    assert _problem(migrated_dir) is None


def test_outdated_database_names_both_revisions(outdated_dir):
    message = _problem(outdated_dir)
    assert message.startswith("Migration fehlt")
    assert "0002" in message and schema.expected_revision() in message and "alembic upgrade head" in message


def test_database_without_any_migration(tmp_path):
    engine = make_engine(tmp_path, must_exist=False)
    with engine.connect() as conn:
        assert "keiner Migration" in schema.problem(conn)
    engine.dispose()


def test_database_newer_than_the_code(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:
        conn.execute(text("UPDATE alembic_version SET version_num = '9999'"))
    engine.dispose()
    assert "nicht kennt" in _problem(migrated_dir)


def test_require_current_raises_with_the_message(outdated_dir):
    engine = make_engine(outdated_dir)
    with engine.connect() as conn, pytest.raises(schema.SchemaError, match="Migration fehlt"):
        schema.require_current(conn)
    engine.dispose()


def test_worker_does_not_start_on_an_outdated_database(outdated_dir, monkeypatch, caplog):
    monkeypatch.setattr(worker.log, "setup", lambda: None)
    monkeypatch.setattr(worker, "install_stop_handlers", lambda stop: None)
    with caplog.at_level(logging.ERROR):
        assert worker.main() == 2
    assert "Worker nicht gestartet: Migration fehlt" in caplog.text
    engine = make_engine(outdated_dir)
    with engine.connect() as conn:
        assert read_heartbeat(conn, worker.COMPONENT) is None  # nothing written
    engine.dispose()


@pytest.mark.parametrize("module, prefix", [(score, "Scoring nicht gestartet"), (update, "Abruf nicht gestartet")])
def test_one_off_commands_refuse_an_outdated_database(outdated_dir, monkeypatch, caplog, module, prefix):
    monkeypatch.setattr(module.log, "setup", lambda: None)
    with caplog.at_level(logging.ERROR):
        assert module.main() == 2
    assert f"{prefix}: Migration fehlt" in caplog.text


@pytest.fixture
def outdated_web(outdated_dir, monkeypatch):
    monkeypatch.setenv("FEVER_DATA", str(outdated_dir))
    web_db.engine.cache_clear()
    yield outdated_dir
    web_db.engine.cache_clear()


def test_health_fails_on_an_outdated_database(outdated_web):
    from fever.web.app import server
    response = server.test_client().get("/health")
    assert response.status_code == 503
    assert response.get_json()["message"].startswith("Migration fehlt")


def test_status_banner_names_the_missing_migration(outdated_web):
    from fever.web.app import status
    _line, banners = status(0, "/")
    texts = [banner.children for banner in banners]
    assert texts[0].startswith("Migration fehlt")
    assert any(text.startswith("Worker ohne Lebenszeichen") for text in texts)
