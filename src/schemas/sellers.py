from typing import List

from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core import PydanticCustomError
from .books import IncomingBook, ReturnedAllBooks

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    books: List[IncomingBook]
    password: str

    # todo:  просмотреть, что таких в базе данных нет.
    # @field_validator("books")
    # @staticmethod
    # def books(books: List[IncomingBook]) -> List[IncomingBook]:
    #     for book in books:
    #         raise PydanticCustomError("Validation error", f"{book} already in store!")
    #     return books

    # @field_validator("password")
    # @staticmethod
    # def books(passw: str) -> str:
    #     if passw is None or len(passw) == 0:
    #         raise PydanticCustomError("Validation error", f"password can't be empty.")
    #     return passw


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    books: ReturnedAllBooks


# Класс для возврата массива объектов "Книга"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
