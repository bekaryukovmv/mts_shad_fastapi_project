from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.lib.auth import hash_password, current_seller
from src.models.books import Seller
from src.dao import SellerDAO
from src.schemas.seller import SellerReg, BaseSeller

seller_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@seller_router.post("/")
async def register_seller(seller_auth: SellerReg):
    seller = await SellerDAO.find_one_or_none(email=seller_auth.email)
    if seller:
        # Пользователь существует
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким email уже зарегистрирован")
    hashed_password = hash_password(seller_auth.password)
    await SellerDAO.add(email=seller_auth.email, password=hashed_password,
                        first_name=seller_auth.first_name, last_name=seller_auth.last_name)
    return Response(status_code=status.HTTP_201_CREATED)


@seller_router.get("/", response_model=List[BaseSeller])
async def get_all_sellers():
    all_sellers = await SellerDAO.find_all()
    return all_sellers


@seller_router.get("/{seller_id}")
async def get_seller_info(seller_id: int, seller: Seller = Depends(current_seller)):
    seller_info = await SellerDAO.select_seller_with_books(seller_id)
    return seller_info
