"""
A router for working with books.
POST /books - method for creating a book entry in the database. Returns the created book.
GET /books - method that returns all books.
GET /books/{book_id} - method that returns a book by its ID.
DELETE /books/{book_id} - method that deletes a book by its ID.
PUT /books/{book_id} - method that updates the data about the book.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.configurations.security import validate_token

books_router = APIRouter(tags=["books"], prefix="/books")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(
        book: IncomingBook, session: DBSession, token: str = Depends(validate_token)
):
    new_book = Book(
        title=book.title,
        author=book.author,
        year=book.year,
        count_pages=book.count_pages,
        seller_id=book.seller_id
    )
    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get("/", response_model=ReturnedAllBooks, status_code=status.HTTP_200_OK)
async def get_all_books(session: DBSession):
    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()

    return {"books": books}


@books_router.get("/{book_id}", response_model=ReturnedBook, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, session: DBSession):
    res = await session.get(Book, book_id)

    if res:
        return res
    else:
        return Response(content="Book not found", status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}")
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)

    if deleted_book:
        await session.delete(deleted_book)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@books_router.put("/{book_id}", status_code=status.HTTP_200_OK)
async def update_book(book_id: int, new_data: ReturnedBook, session: DBSession, token: str = Depends(validate_token)):
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages

        await session.flush()

        return updated_book

    return Response(content="Book not found", status_code=status.HTTP_404_NOT_FOUND)
