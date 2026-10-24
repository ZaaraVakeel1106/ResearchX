"""Alembic migration environment using the configured PostgreSQL URL."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, make_url, pool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_database_url
from app import models  # noqa: F401 - register model metadata with Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Render SQL without opening a database connection."""
    configured_url = config.attributes.get("database_url") or get_database_url(settings)
    url = make_url(configured_url) if isinstance(configured_url, str) else configured_url
    context.configure(
        url=url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run a migration on the configured database or an injected test connection."""
    injected_connection = config.attributes.get("connection")
    if injected_connection is not None:
        context.configure(
            connection=injected_connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
        return

    url = get_database_url(settings)
    connectable = engine_from_config(
        {"sqlalchemy.url": url.render_as_string(hide_password=False)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
