"""Alembic environment: FEVER_DATA/fever.sqlite3 with the project PRAGMAs, online only."""

from logging.config import fileConfig

from alembic import context

from fever.store.db import data_dir, make_engine
from fever.store.tables import metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

if context.is_offline_mode():
    raise SystemExit("Offline-Migrationen (--sql) werden nicht unterstützt.")

engine = make_engine(data_dir(), must_exist=False)
try:
    with engine.connect() as connection:
        # Batch mode: SQLite can alter tables only by copying them.
        context.configure(connection=connection, target_metadata=metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
