"""Environment-based settings for the API process."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Settings loaded from environment variables or ``backend/.env``."""

    cors_allowed_origins: str = "http://localhost:5173"
    database_url: SecretStr | None = None

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
