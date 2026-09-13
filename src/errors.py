"""Доменные исключения и обработчики ошибок HTTP."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.schemas import ErrorResponse, ValidationErrorResponse

VALIDATION_ERROR_MESSAGE = "Validation failed"
BODY_LOCATION_PREFIX = "body"


class PersonNotFoundError(Exception):
    """Запись о человеке не найдена."""

    def __init__(self, person_id: int) -> None:
        self.person_id = person_id
        super().__init__(f"Person with id {person_id} not found")


def _field_name(location: tuple[str | int, ...]) -> str:
    """Собирает имя поля из location pydantic, отбрасывая префикс `body`."""
    parts = [str(part) for part in location if str(part) != BODY_LOCATION_PREFIX]
    return ".".join(parts) if parts else BODY_LOCATION_PREFIX


async def person_not_found_handler(
    _: Request, exc: PersonNotFoundError
) -> JSONResponse:
    """Возвращает 404 в формате ErrorResponse."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(message=str(exc)).model_dump(),
    )


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """Подменяет стандартный 422 FastAPI на 400 из контракта."""
    errors = {
        _field_name(error["loc"]): error["msg"] for error in exc.errors()
    }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(
            message=VALIDATION_ERROR_MESSAGE, errors=errors
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Подключает обработчики ошибок к приложению."""
    app.add_exception_handler(PersonNotFoundError, person_not_found_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
