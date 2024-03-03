"""
The model for the "Seller" entity. Contains information about seller.
id - seller id
first_name - seller's name
last_name - seller's last name
email - seller's email address
password - seller's password
books - the list of books that the seller sells
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .books import Book


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    books: Mapped[list["Book"]] = relationship("Book", cascade="all, delete-orphan")
