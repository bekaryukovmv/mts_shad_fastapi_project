from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook", "UpdatedBook"]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class IncomingBook(BaseBook):
    seller_id: int
    year: int = 2024
    count_pages: int = Field(
        alias="pages",
        default=300,
    )

    @field_validator("year")
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


class ReturnedBook(BaseBook):
    id: int
    count_pages: int
    seller_id: int


class UpdatedBook(BaseBook):
    id: int
    count_pages: int


class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]
