from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedAllSellers", "CertainSeller"]

#Базовый класс "Продавцы"
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

#Класс для валидации входящих данных. Без id так как его присваивает БД и он фигурирует в исходящих
class IncomingSeller(BaseSeller):
    password: str

#Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[BaseSeller]

#Класс для возврата конкретной/подробной информации об одном продавце 
class CertainSeller(BaseSeller):
    id: int
    books: list[ReturnedBook] = []