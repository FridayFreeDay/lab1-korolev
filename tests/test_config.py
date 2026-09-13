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
