"""PostgreSQL engine and session creation from backend settings."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import URL, create_engine, make_url
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session

from app.core.config import Settings, settings


class DatabaseConfigurationError(RuntimeError):
    """Raised when PostgreSQL connection settings are missing or invalid."""


def get_database_url(config: Settings = settings) -> URL:
    """Return a validated synchronous PostgreSQL URL without exposing secrets."""
    if config.database_url is None:
        raise DatabaseConfigurationError(
            "RESEARCH_X_DATABASE_URL must be set before using the database."
        )

    try:
        url = make_url(config.database_url.get_secret_value())
    except (ArgumentError, TypeError, ValueError) as error:
        raise DatabaseConfigurationError(
            "RESEARCH_X_DATABASE_URL must be a valid SQLAlchemy URL."
        ) from error

    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    elif url.drivername != "postgresql+psycopg":
        raise DatabaseConfigurationError(
            "RESEARCH_X_DATABASE_URL must use PostgreSQL with the psycopg driver."
        )

    if not url.database:
        raise DatabaseConfigurationError(
            "RESEARCH_X_DATABASE_URL must include a database name."
        )

    return url


def create_database_engine(config: Settings = settings) -> Engine:
    """Create a PostgreSQL engine on demand; importing the app opens no connection."""
    return create_engine(get_database_url(config), pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_database_engine() -> Engine:
    """Return the process-wide lazy engine used by database dependencies."""
    return create_database_engine()


def get_session() -> Iterator[Session]:
    """Yield a short-lived database session for future API dependencies."""
    with Session(get_database_engine()) as session:
        yield session
