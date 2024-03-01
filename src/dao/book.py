from src.configurations.database import get_async_session
from src.dao.base import BaseDAO
from src.models.books import Book
from src.schemas import ReturnedBook, IncomingBook


class BookDAO(BaseDAO):
    model = Book

    @classmethod
    async def add_new_book(cls, **data):
        async with get_async_session() as session:
            new_book = cls.model(**data)
            session.add(new_book)
            await session.flush()
            result_dto = ReturnedBook.model_validate(new_book, from_attributes=True)
            return result_dto

    @classmethod
    async def update_book(cls, book_id: int, new_data: IncomingBook):
        async with get_async_session() as session:
            updated_book = await session.get(Book, book_id)
            updated_book.author = new_data.author
            updated_book.title = new_data.title
            updated_book.year = new_data.year
            updated_book.count_pages = new_data.count_pages

            await session.flush()
            result_dto = ReturnedBook.model_validate(updated_book, from_attributes=True)
            return result_dto
