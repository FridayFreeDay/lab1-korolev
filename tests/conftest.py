"""Общая настройка тестов: изолированная in-memory БД на каждый тест."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
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
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


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
