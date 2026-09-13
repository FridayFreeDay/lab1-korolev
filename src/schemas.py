"""Схемы запросов и ответов (контракт person-service.yaml)."""
from pydantic import BaseModel, ConfigDict, Field

MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 255
MIN_AGE = 0
MAX_AGE = 150


class PersonRequest(BaseModel):
    """Тело запроса на создание записи."""

    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    age: int | None = Field(default=None, ge=MIN_AGE, le=MAX_AGE)
    address: str | None = None
    work: str | None = None


class PersonUpdateRequest(BaseModel):
    """Тело запроса на частичное обновление записи.

    Все поля опциональны: незаполненные поля не изменяются.
    """

    name: str | None = Field(default=None, min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    age: int | None = Field(default=None, ge=MIN_AGE, le=MAX_AGE)
    address: str | None = None
    work: str | None = None


class PersonResponse(BaseModel):
    """Представление записи о человеке."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int | None = None
    address: str | None = None
    work: str | None = None


class ErrorResponse(BaseModel):
    """Ответ с описанием ошибки."""

    message: str


class ValidationErrorResponse(BaseModel):
    """Ответ с описанием ошибок валидации по полям."""

    message: str
    errors: dict[str, str]
