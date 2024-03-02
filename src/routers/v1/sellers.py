from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.models.books import Book
from src.schemas.sellers import IncomingSeller, ReturnedSeller, ReturnedSellerSilent, ReturnedAllSellersSilent, SellerUpdate, ReturnedSellerBooksSilent
from src.schemas.books import ReturnedBookFromSeller


sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")


DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password
    )
    session.add(new_seller)
    await session.flush()
    
    return new_seller


# Получение продавца по ID без пароля
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerBooksSilent, status_code=status.HTTP_200_OK)
async def get_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if seller is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # Получение списка всех книг у продавца
    query = select(Book).filter(Book.seller_id==seller_id)
    books_from_db = await session.execute(query)
    books_from_db = books_from_db.scalars().all()

    # Прогон через специальную схему, которая не возвращает seller_id
    books_from_db = [ReturnedBookFromSeller(id=book.id,
                                            title=book.title,
                                            author=book.author,
                                            year=book.year,
                                            count_pages=book.count_pages) 
                          for book in books_from_db]

    seller_response = {
        "first_name": seller.first_name,
        "last_name": seller.last_name,
        "email": seller.email,
        "id": seller.id,
        "books": books_from_db
    }

    return seller_response


# Получение списка всех продавцов по ID без пароля
@sellers_router.get("/", response_model=ReturnedAllSellersSilent, status_code=status.HTTP_200_OK)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Обновление данных о продавце
@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: SellerUpdate, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email
        updated_seller.password = updated_seller.password
        updated_seller.id = updated_seller.id

        await session.flush()

        # return updated_seller
        return Response(status_code=status.HTTP_200_OK)

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)

    query = select(Book).filter(Book.seller_id==seller_id)
    books_from_db = await session.execute(query)
    books_from_db = books_from_db.scalars().all()
    
    if books_from_db:
        for book in books_from_db:
            await session.delete(book)

    if deleted_seller:
        await session.delete(deleted_seller)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)