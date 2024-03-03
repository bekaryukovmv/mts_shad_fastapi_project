from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from email_validator import validate_email, EmailNotValidError

from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks", "BaseSeller"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

    @field_validator("email")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate(val: str):
        try:
            res = validate_email(val)
            email = res["email"]
            return val
        except EmailNotValidError as e:
            raise PydanticCustomError("Validation error", str(e))


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]
