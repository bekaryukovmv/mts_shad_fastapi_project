from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.tables import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая все книги
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат:
    # books: [{"id": 1, "title": "Blabla", ...}, {"id": 2, ...}]
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}



# Ручка для получения книги по ее ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.get(Seller, seller_id)
    return res


# Ручка для удаления книги
@sellers_router.delete("/{seller_id}")
async def delete_selller(seller_id: int, session: DBSession):
    delete_selller = await session.get(Seller, seller_id)
    ic(delete_selller)  # Красивая и информативная замена для print. Полезна при отладке.
    if delete_selller:
        await session.delete(delete_selller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о книге
@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email
        updated_seller.password = new_data.password

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
