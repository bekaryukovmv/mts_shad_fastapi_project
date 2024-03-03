from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import IncomingSeller, ReturnedAllSellers, CertainSeller
from fastapi.responses import ORJSONResponse

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.models.books import Book

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

#Подключаемся к реальному хранилищу 
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

#Ручка для создания продавца, возвращает созданного продавца
@sellers_router.post("/",response_model=CertainSeller, status_code=status.HTTP_201_CREATED)
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
    res_seller = await session.get(Seller, seller_id)
    query_books = select(Book).where(Book.parent_id == seller_id)
    res_books = await session.execute(query_books)
    seller_books = res_books.scalars().all()
    
    seller_date = {
        "id": res_seller.id,
        "first_name": res_seller.first_name,
        "last_name": res_seller.last_name,
        "email": res_seller.email,
        "books": seller_books
    }

    return seller_date


#Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=CertainSeller)
async def update_seller(seller_id: int, seller: CertainSeller):
    if _ := fake_sellers.get(seller_id, None):
        fake_sellers[seller_id] = seller

    return fake_sellers[seller_id]

#Ручка для удаления продавцов
#TODO надо также при удаление продавца реализовать удаление соотвествующих книг
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int):
    deleted_seller = fake_sellers.pop(seller_id, -1)
    ic(deleted_seller)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
