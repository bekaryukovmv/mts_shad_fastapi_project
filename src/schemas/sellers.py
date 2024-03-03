from pydantic import BaseModel, EmailStr
from pydantic_core import PydanticCustomError

from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "CertainSeller"]

#Базовый класс "Продавцы"
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

#Класс для валидации входящих данных. Без id так как его присваивает БД и он фигурирует в исходящих
class IncomingSeller(BaseSeller):
    password: str

# Класс для валидации исходящих данных. Уже содержит id
class ReturnedSeller(BaseSeller):
    id: int

#Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]

#Класс для возврата конкретной/подробной информации об одном продавце 
class CertainSeller(BaseSeller):
    id: int
    books: list[ReturnedBook] = []