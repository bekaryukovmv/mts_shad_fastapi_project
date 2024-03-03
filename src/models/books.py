from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Book(BaseModel):
    __tablename__ = "books_table"

    parent_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    count_pages: Mapped[int]