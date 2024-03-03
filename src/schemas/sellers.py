"""
A model for validating incoming and outgoing data of the "Seller" entity.
BaseSeller: the base class of "Sellers", which contains fields that are in all descendant classes.
IncomingSeller: a class for validating incoming data.
ReturnedSeller: a class validating outgoing data.
ReturnedAllSellers: a class for returning a list of sellers.
ReturnedSellerWithBooks: a class for returning the seller with the books he has.
"""

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from email_validator import validate_email, EmailNotValidError

from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks", "BaseSeller"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

    @field_validator("email")  # validate email
    @staticmethod
    def validate(val: str):
        try:
            res = validate_email(val)
            email = res["email"]
            return val
        except EmailNotValidError as e:
            raise PydanticCustomError("Validation error", str(e))


class IncomingSeller(BaseSeller):
    password: str


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]
