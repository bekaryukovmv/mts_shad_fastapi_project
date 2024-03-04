from typing import Annotated, Dict, Sequence

from fastapi import APIRouter, Depends, Response, status, HTTPException
from src.lib.auth import Auth, current_seller
from src.models.books import Book, Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.routers.dependency_stubs import BookDAODep


books_router = APIRouter(tags=["books"], prefix="/books")

AuthenticatedSeller = Annotated[Seller, Depends(current_seller)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@books_router.post(
    "/", status_code=status.HTTP_201_CREATED,
)  # Прописываем модель ответа
async def create_book(book: IncomingBook, dao: BookDAODep, seller: AuthenticatedSeller) -> ReturnedBook:
    new_book = await dao.add_new_book(
        title=book.title,
        author=book.author,
        year=book.year,
        count_pages=book.count_pages,
        seller_id=seller.id,
    )
    return new_book


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(dao: BookDAODep):
    # Хотим видеть формат:
    # books: [{"id": 1, "title": "Blabla", ...}, {"id": 2, ...}]
    res = await dao.find_all()
    # books = res.scalars().all()
    return {"books": res}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}")
async def get_book(book_id: int, dao: BookDAODep):
    res = await dao.find_one_or_none(id=book_id)
    return res


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, dao: BookDAODep):
    await dao.delete(id=book_id)


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(
    book_id: int,
    new_data: IncomingBook,
    dao: BookDAODep,
    seller: AuthenticatedSeller,
):
    book = await dao.find_one_or_none(id=book_id)
    if book and book.seller_id == seller.id:
        updated_book = await dao.update_book(book_id=book_id, new_data=new_data)

        return updated_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такая книга не существует")
