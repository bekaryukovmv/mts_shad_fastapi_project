from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.lib.auth import hash_password, current_seller
from src.models.books import Book
from src.models.seller import Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.dao import SellerDAO
from src.schemas.seller import SellerAuth

seller_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@seller_router.post("/")
async def register_seller(seller_auth: SellerAuth):
    seller = await SellerDAO.find_one_or_none(email=seller_auth.email)
    if seller:
        # Пользователь существует
        raise HTTPException(409, "Пользователь с таким email уже зарегистрирован")
    hashed_password = hash_password(seller_auth.password)
    await SellerAuth.add(email=seller_auth.email, password=hashed_password)
    return Response(status_code=status.HTTP_201_CREATED)


@seller_router.get("/")
async def get_all_sellers(seller: Seller = Depends(current_seller)):
    sellers = await SellerDAO.find_all()
    return sellers

