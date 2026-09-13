"""Тесты нормализации строки подключения к БД."""
import pytest

from src.config import normalize_database_url


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "postgres://user:pass@host:5432/persons",
            "postgresql+psycopg://user:pass@host:5432/persons",
        ),
        (
            "postgresql://user:pass@host/persons?sslmode=require",
            "postgresql+psycopg://user:pass@host/persons?sslmode=require",
        ),
        (
            "postgresql+psycopg://user:pass@host/persons",
            "postgresql+psycopg://user:pass@host/persons",
        ),
    ],
)
def test_normalize_database_url(source, expected):
    # Act
    result = normalize_database_url(source)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "env_name",
    ["RENDER_GIT_COMMIT", "RAILWAY_GIT_COMMIT_SHA", "GIT_COMMIT"],
)
def test_git_commit_read_from_platform_env(monkeypatch, env_name):
    # Arrange
    from src.config import Settings

    for name in ("RENDER_GIT_COMMIT", "RAILWAY_GIT_COMMIT_SHA", "GIT_COMMIT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(env_name, "abc123")

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.git_commit == "abc123"
