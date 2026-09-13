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


def test_git_commit_read_from_railway_env(monkeypatch):
    # Arrange
    from src.config import Settings

    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "abc123")

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.git_commit == "abc123"


def test_git_commit_defaults_to_unknown(monkeypatch):
    # Arrange
    from src.config import UNKNOWN_COMMIT, Settings

    monkeypatch.delenv("RAILWAY_GIT_COMMIT_SHA", raising=False)

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.git_commit == UNKNOWN_COMMIT
