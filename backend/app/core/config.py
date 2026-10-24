"""Environment-based settings for the API process."""

from pathlib import Path

from pydantic import AnyHttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Settings loaded from environment variables or ``backend/.env``."""

    cors_allowed_origins: str = "http://localhost:5173"
    database_url: SecretStr | None = None
    openalex_base_url: AnyHttpUrl = "https://api.openalex.org"
    openalex_api_key: SecretStr | None = None

    @field_validator("openalex_api_key", mode="before")
    @classmethod
    def empty_openalex_key_is_unset(cls, value: object) -> object:
        """Allow the safe blank placeholder in `.env.example` to mean no key."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    @field_validator("openalex_base_url")
    @classmethod
    def require_secure_openalex_url(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        """Require TLS so a configured provider key is not sent over plaintext."""
        if value.scheme != "https":
            raise ValueError("The OpenAlex base URL must use HTTPS.")
        if value.username or value.password or value.query or value.fragment:
            raise ValueError(
                "The OpenAlex base URL must not contain credentials, query parameters, or a fragment."
            )
        return value

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="RESEARCH_X_",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Return configured origins as a normalized list."""
        return [
            origin.rstrip("/")
            for raw_origin in self.cors_allowed_origins.split(",")
            if (origin := raw_origin.strip())
        ]


settings = Settings()
