from pydantic import BaseModel
from .books import ReturnedBookFromSeller

class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class IncomingSeller(BaseSeller):
    pass


class ReturnedSeller(BaseSeller):
    id: int 


# Модель содержащая данные продавца без его пароля
class ReturnedSellerSilent(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellersSilent(BaseModel):
    sellers: list[ReturnedSellerSilent]


class ReturnedSellerBooksSilent(ReturnedSellerSilent):
    books: list[ReturnedBookFromSeller]


class SellerUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str