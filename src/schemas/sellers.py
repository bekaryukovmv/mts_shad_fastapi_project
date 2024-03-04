from pydantic import BaseModel, Field

from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str = Field(pattern=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class IncomingSeller(BaseSeller):
    password: str = Field(min_length=8)


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]
