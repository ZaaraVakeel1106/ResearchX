from app.core.config import Settings
from app.db.session import DatabaseConfigurationError, get_database_url
import pytest
from pydantic import ValidationError


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


def test_openalex_configuration_is_environment_based_and_key_is_secret(monkeypatch) -> None:
    monkeypatch.setenv(
        "RESEARCH_X_OPENALEX_BASE_URL", "https://metadata.example.test/api"
    )
    monkeypatch.setenv("RESEARCH_X_OPENALEX_API_KEY", "test-only-key")

    config = Settings(_env_file=None)

    assert str(config.openalex_base_url) == "https://metadata.example.test/api"
    assert config.openalex_api_key is not None
    assert config.openalex_api_key.get_secret_value() == "test-only-key"
    assert "test-only-key" not in repr(config)


def test_blank_openalex_key_placeholder_means_no_key() -> None:
    config = Settings(_env_file=None, openalex_api_key=" ")

    assert config.openalex_api_key is None


def test_openalex_base_url_requires_https() -> None:
    with pytest.raises(ValidationError, match="must use HTTPS"):
        Settings(_env_file=None, openalex_base_url="http://api.openalex.org")


def test_openalex_base_url_rejects_embedded_credentials() -> None:
    with pytest.raises(ValidationError, match="must not contain credentials"):
        Settings(
            _env_file=None,
            openalex_base_url="https://user:secret@api.openalex.org?api_key=secret",
        )
