from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.dao import SellerDAO
from src.schemas.seller import SellerAuth

seller_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@seller_router.post("/")
async def register_seller(seller_data: SellerAuth):
    user = await SellerDAO.find_one_or_none(email=seller_data.email)
    if user:
        # Пользователь существует
        raise HTTPException(409, "Пользователь с таким email уже зарегистрирован")
    hashed_password = get_password_hash(seller_data.password)
