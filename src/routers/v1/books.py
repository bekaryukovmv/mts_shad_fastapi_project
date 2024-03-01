from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.dao.book import BookDAO
from src.lib.auth import current_seller
from src.models.books import Book, Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook

books_router = APIRouter(tags=["books"], prefix="/books")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@books_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ReturnedBook,
)  # Прописываем модель ответа
async def create_book(book: IncomingBook, seller: Seller = Depends(current_seller)):
    new_book = await BookDAO.add_new_book(
        title=book.title,
        author=book.author,
        year=book.year,
        count_pages=book.count_pages,
        seller_id=seller.id,
    )
    return new_book


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    # Хотим видеть формат:
    # books: [{"id": 1, "title": "Blabla", ...}, {"id": 2, ...}]
    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()
    return {"books": books}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    res = await session.get(Book, book_id)
    return res


# Ручка для удаления книги
@books_router.delete("/{book_id}")
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_book:
        await session.delete(deleted_book)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(
    book_id: int,
    new_data: IncomingBook,
    seller: Seller = Depends(current_seller),
):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    book = await BookDAO.find_one_or_none(id=book_id)
    if book and book.seller_id == seller.id:
        updated_book = await BookDAO.update_book(book_id=book_id, new_data=new_data)

        return updated_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такая книга не существует")
