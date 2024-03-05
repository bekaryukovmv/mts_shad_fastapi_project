from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import icecream as ic
from src.configurations.database import get_async_session
from src.models.books import Book
from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, ReturnedSeller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.routers.v1 import books

# todo: Make connect with books __PS

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@sellers_router.post("/", response_model=ReturnedSeller,
                     status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
        seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password  # todo: encoding
    )
    session.add(new_seller)
    await session.commit()  # Фиксируем изменения в базе данных
    await session.refresh(new_seller)

    return_books = ReturnedAllBooks()
    # Добавляем книги продавца
    for incoming_book in seller.books:
        incoming_book.seller_id = new_seller.id
        return_books.books.append(await books.create_book(incoming_book, session))

    return_seller = ReturnedSeller(
        id=new_seller.id,
        first_name=new_seller.first_name,
        last_name=new_seller.last_name,
        email=new_seller.email,
        books=return_books
    )

    return return_seller


# Ручка, возвращающая все книги
@sellers_router.get("/", response_model=ReturnedAllBooks)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}
