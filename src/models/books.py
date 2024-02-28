import datetime

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    # Связь One To Many
    books: Mapped[list["Book"]] = relationship(back_populates="seller")


class Book(BaseModel):
    __tablename__ = "books_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    count_pages: Mapped[int]
    created_at: Mapped[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
    # Параметр ondelete=CASCADE для того, чтобы при удалении продавца все книги продавца удалялись автоматически
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id", ondelete="CASCADE"))

    seller: Mapped["Seller"] = relationship(back_populates="books")
