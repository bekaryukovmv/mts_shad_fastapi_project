"""
A model for validating incoming and outgoing data of the "Book" entity.
BaseBook: the base class of "Books", which contains fields that are in all descendant classes.
IncomingBook: a class for validating incoming data.
ReturnedBook: a class validating outgoing data.
ReturnedAllBooks: a class for returning a list of books.
"""

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook"]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int


class IncomingBook(BaseBook):
    year: int = 2024
    count_pages: int = Field(
        alias="pages",
        default=300,
    )

    @field_validator("year")  # validate that the date is not too early
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


class ReturnedBook(BaseBook):
    id: int
    count_pages: int


class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]
