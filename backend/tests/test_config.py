from app.core.config import Settings
from app.db.session import DatabaseConfigurationError, get_database_url
import pytest


def test_cors_origins_are_loaded_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "RESEARCH_X_CORS_ALLOWED_ORIGINS",
        " https://research.example/, http://localhost:5173 ",
    )
    config = Settings(_env_file=None)

    assert config.cors_origins == [
        "https://research.example",
        "http://localhost:5173",
    ]


def test_empty_cors_origin_configuration_disables_cross_origin_access() -> None:
    config = Settings(_env_file=None, cors_allowed_origins=" , ")

    assert config.cors_origins == []


def test_database_url_is_loaded_from_environment_and_masks_password(monkeypatch) -> None:
    monkeypatch.setenv(
        "RESEARCH_X_DATABASE_URL",
        "postgresql://research_x:example-only@localhost:5432/research_x",
    )

    url = get_database_url(Settings(_env_file=None))

    assert url.drivername == "postgresql+psycopg"
    assert url.database == "research_x"
    assert "example-only" not in str(url)
    assert "***" in str(url)


def test_database_url_requires_environment_configuration() -> None:
    with pytest.raises(DatabaseConfigurationError, match="RESEARCH_X_DATABASE_URL"):
        get_database_url(Settings(_env_file=None))


def test_database_url_rejects_non_postgresql_driver() -> None:
    with pytest.raises(DatabaseConfigurationError, match="PostgreSQL"):
        get_database_url(
            Settings(_env_file=None, database_url="sqlite:///not-allowed.db")
        )


def test_database_url_requires_database_name() -> None:
    with pytest.raises(DatabaseConfigurationError, match="database name"):
        get_database_url(
            Settings(_env_file=None, database_url="postgresql://localhost")
        )


def test_database_url_reports_malformed_url() -> None:
    with pytest.raises(DatabaseConfigurationError, match="valid SQLAlchemy URL"):
        get_database_url(Settings(_env_file=None, database_url="not a URL"))
