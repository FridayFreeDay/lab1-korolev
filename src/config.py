"""Конфигурация приложения из переменных окружения."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://program:test@localhost:5432/persons"
DEFAULT_PORT = 8080
UNKNOWN_COMMIT = "unknown"
POSTGRES_SCHEME_PREFIXES = ("postgres://", "postgresql://")
PSYCOPG_SCHEME = "postgresql+psycopg://"


def normalize_database_url(url: str) -> str:
    """Приводит URL облачного провайдера (postgres://...) к драйверу psycopg3.

    Render и Railway отдают DATABASE_URL со схемой `postgres://`, которую
    SQLAlchemy 2.0 не понимает без явного указания драйвера.
    """
    for prefix in POSTGRES_SCHEME_PREFIXES:
        if url.startswith(prefix):
            return PSYCOPG_SCHEME + url[len(prefix):]
    return url


class Settings(BaseSettings):
    """Настройки сервиса."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = DEFAULT_DATABASE_URL
    port: int = DEFAULT_PORT
    # Railway прокидывает sha выкаченного коммита в RAILWAY_GIT_COMMIT_SHA.
    # CI по нему понимает, что поднялась именно текущая версия, а не предыдущая.
    git_commit: str = Field(
        default=UNKNOWN_COMMIT, validation_alias="RAILWAY_GIT_COMMIT_SHA"
    )

    @field_validator("database_url")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return normalize_database_url(value)


settings = Settings()
