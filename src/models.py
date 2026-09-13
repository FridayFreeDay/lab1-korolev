"""ORM-модели предметной области."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base

MAX_NAME_LENGTH = 255
MAX_ADDRESS_LENGTH = 255
MAX_WORK_LENGTH = 255


class Person(Base):
    """Запись о человеке."""

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(MAX_ADDRESS_LENGTH), nullable=True)
    work: Mapped[str | None] = mapped_column(String(MAX_WORK_LENGTH), nullable=True)
