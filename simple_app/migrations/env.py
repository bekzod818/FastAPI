import pathlib
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.database import Base

config = context.config

target_metadata = Base.metadata

config.set_main_option(
    "sqlalchemy.url", "postgresql://postgres:postgres@localhost/fast"
)


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline mode not supported")
else:
    run_migrations_online()
