from sqlalchemy import String, Integer, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Book(BaseModel):
    __tablename__ = "books_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    count_pages: Mapped[int]
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("sellers_table.id"))
    seller = relationship("Seller", back_populates="books")
