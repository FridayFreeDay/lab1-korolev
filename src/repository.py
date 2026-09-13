"""Работа с хранилищем записей о людях."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.errors import PersonNotFoundError
from src.models import Person
from src.schemas import PersonRequest, PersonUpdateRequest


def list_persons(session: Session) -> list[Person]:
    """Возвращает все записи, отсортированные по id."""
    return list(session.scalars(select(Person).order_by(Person.id)))


def get_person(session: Session, person_id: int) -> Person:
    """Возвращает запись по id или бросает PersonNotFoundError."""
    person = session.get(Person, person_id)
    if person is None:
        raise PersonNotFoundError(person_id)
    return person


def create_person(session: Session, request: PersonRequest) -> Person:
    """Создаёт новую запись и возвращает её с присвоенным id."""
    person = Person(**request.model_dump())
    session.add(person)
    session.commit()
    session.refresh(person)
    return person


def update_person(
    session: Session, person_id: int, request: PersonUpdateRequest
) -> Person:
    """Обновляет только переданные поля записи."""
    person = get_person(session, person_id)
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    session.commit()
    session.refresh(person)
    return person


def delete_person(session: Session, person_id: int) -> None:
    """Удаляет запись, если она существует."""
    person = session.get(Person, person_id)
    if person is None:
        return
    session.delete(person)
    session.commit()
