"""
A router for working with sellers.
POST /seller - method for creating a seller entry in the database. Returns the created seller.
GET /seller - method that returns all sellers.
GET /seller/{seller_id} - method that returns a seller by its ID.
DELETE /books/{seller_id} - method that deletes a seller by its ID.
PUT /books/{seller_id} - method that updates the data about the seller.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations.security import hashing_password, validate_token
from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks, BaseSeller

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
        seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=hashing_password(seller.password),
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


@sellers_router.get("/", response_model=ReturnedAllSellers, status_code=status.HTTP_200_OK)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()

    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks, status_code=status.HTTP_200_OK)
async def get_seller(seller_id: int, session: DBSession, token: str = Depends(validate_token)):
    query = (
        select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    )
    res = await session.execute(query)
    seller = res.scalar()

    if seller:
        return seller
    else:
        return Response(content="Seller not found", status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)

    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(content="Seller deleted successfully", status_code=status.HTTP_200_OK)


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: BaseSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(content="Seller not found", status_code=status.HTTP_404_NOT_FOUND)
