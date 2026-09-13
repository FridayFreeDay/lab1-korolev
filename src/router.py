"""HTTP-эндпоинты сущности Person."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src import repository
from src.database import get_db
from src.schemas import (
    ErrorResponse,
    PersonRequest,
    PersonResponse,
    PersonUpdateRequest,
    ValidationErrorResponse,
)

API_PREFIX = "/api/v1/persons"

router = APIRouter(prefix=API_PREFIX, tags=["Person REST API operations"])


@router.get("", response_model=list[PersonResponse], summary="Get all Persons")
def list_persons(session: Session = Depends(get_db)) -> list[PersonResponse]:
    """Возвращает список всех записей."""
    return [PersonResponse.model_validate(person) for person in repository.list_persons(session)]


@router.get(
    "/{person_id}",
    response_model=PersonResponse,
    summary="Get Person by ID",
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def get_person(person_id: int, session: Session = Depends(get_db)) -> PersonResponse:
    """Возвращает запись по идентификатору."""
    return PersonResponse.model_validate(repository.get_person(session, person_id))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create new Person",
    responses={
        status.HTTP_201_CREATED: {"description": "Created new Person"},
        status.HTTP_400_BAD_REQUEST: {"model": ValidationErrorResponse},
    },
)
def create_person(request: PersonRequest, session: Session = Depends(get_db)) -> Response:
    """Создаёт запись и отдаёт её адрес в заголовке Location."""
    person = repository.create_person(session, request)
    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{API_PREFIX}/{person.id}"},
    )


@router.patch(
    "/{person_id}",
    response_model=PersonResponse,
    summary="Update Person by ID",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ValidationErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
def update_person(
    person_id: int,
    request: PersonUpdateRequest,
    session: Session = Depends(get_db),
) -> PersonResponse:
    """Частично обновляет запись: незаполненные поля не изменяются."""
    return PersonResponse.model_validate(
        repository.update_person(session, person_id, request)
    )


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Person by ID",
)
def delete_person(person_id: int, session: Session = Depends(get_db)) -> Response:
    """Удаляет запись по идентификатору."""
    repository.delete_person(session, person_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
