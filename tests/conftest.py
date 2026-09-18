"""Общая настройка тестов: изолированная БД Postgres."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.config import normalize_database_url
from src.database import Base, get_db
from src.main import app

DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://program:test@localhost:5432/persons"
TRUNCATE_PERSONS = "TRUNCATE TABLE persons RESTART IDENTITY CASCADE"


@pytest.fixture(scope="session")
def engine():
    """Движок на тестовую БД: схема создаётся один раз на весь прогон."""
    url = normalize_database_url(
        os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
    )
    engine = create_engine(url, pool_pre_ping=True, future=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def client(engine):
    """Приложение поверх пустой таблицы: данные и счётчик id сбрасываются."""
    with engine.begin() as connection:
        connection.execute(text(TRUNCATE_PERSONS))

    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def person_payload():
    return {
        "name": "Ivan Ivanov",
        "age": 31,
        "address": "Baumanskaya 5",
        "work": "BMSTU",
    }


@pytest.fixture()
def created_person_id(client, person_payload):
    response = client.post("/api/v1/persons", json=person_payload)
    return int(response.headers["Location"].split("/")[-1])
