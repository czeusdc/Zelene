"""Alembic environment configuration for the Zelene intelligence platform.

This module configures Alembic to work with the async PostgreSQL database
used by the FastAPI backend. It supports both offline (SQL script) and
online (direct DB connection) migration modes.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context
from src.db.models import Base
from src.config import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Derive the sync-dialect URL from settings (Alembic needs psycopg2, not asyncpg)
settings = get_settings()
sync_url = settings.database_url.replace("+asyncpg", "").replace(
    "postgresql+asyncpg", "postgresql"
)
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without a live database)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against the configured PostgreSQL instance."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
