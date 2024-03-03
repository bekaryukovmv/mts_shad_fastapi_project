from src.dao.base import BaseDAO
from src.models.books import Book
from src.schemas import ReturnedBook, IncomingBook


class BookDAO(BaseDAO):
    model = Book

    async def add_new_book(self, **data):
        new_book = self.model(**data)
        self.session.add(new_book)
        await self.session.flush()
        result_dto = ReturnedBook.model_validate(new_book, from_attributes=True)
        return result_dto

    async def update_book(self, book_id: int, new_data: IncomingBook):
        updated_book = await self.session.get(Book, book_id)
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages

        await self.session.flush()
        result_dto = ReturnedBook.model_validate(updated_book, from_attributes=True)
        return result_dto
