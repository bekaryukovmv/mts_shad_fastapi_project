from pydantic import BaseModel, EmailStr


__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks", "BaseSeller"]

from src.schemas import ReturnedBookWithoutSellerId


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    


class IncomingSeller(BaseSeller):
    password: str

  

class ReturnedSeller(BaseSeller):
    id: int



class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]



class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBookWithoutSellerId]
