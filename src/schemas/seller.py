from pydantic import BaseModel, EmailStr
from src.schemas.books import ReturnedBook


class SellerAuth(BaseModel):
    email: EmailStr
    password: str


class SellerReg(SellerAuth):
    first_name: str
    last_name: str


class BaseSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr


class SellerDTO(BaseSeller):
    books: list["ReturnedBook"]


class SellerUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
