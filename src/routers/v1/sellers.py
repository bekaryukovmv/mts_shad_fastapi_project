from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.schemas import IncomingSeller,ReturnedSeller, ReturnedAllSellers, CertainSeller
from fastapi.responses import ORJSONResponse

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.models.books import Book

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

#Подключаемся к реальному хранилищу 
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

#Ручка для создания продавца, возвращает созданного продавца
@sellers_router.post("/",response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
    seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password
    )
    session.add(new_seller)
    await session.flush()

    return new_seller

#Ручка для получения списка всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}

#Ручка для получения конrретного продавца
@sellers_router.get("/{seller_id}", response_model=CertainSeller)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.execute(
        select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    )
    seller = res.scalar_one_or_none()
    return seller



#Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: ReturnedSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = seller_data.first_name
        updated_seller.last_name = seller_data.last_name
        updated_seller.email = seller_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)

#Ручка для удаления продавцов
#TODO надо также при удаление продавца реализовать удаление соотвествующих книг
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
