from src.configurations.database import get_async_session
from src.dao.base import BaseDAO

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.books import Seller
from src.schemas.seller import SellerDTO, SellerUpdate, BaseSeller


class SellerDAO(BaseDAO):
    model = Seller

    @staticmethod
    async def select_seller_with_books(seller_id: int):
        async with get_async_session() as session:
            query = (
                select(Seller).where(Seller.id == seller_id)
                .options(joinedload(Seller.books))
            )

            res = await session.execute(query)
            result_orm = res.unique().scalars().one_or_none()

            if result_orm:
                result_dto = SellerDTO.model_validate(result_orm, from_attributes=True)
                return result_dto

    @classmethod
    async def update_seller(cls, seller_id: int, new_data: SellerUpdate) -> BaseSeller:
        async with get_async_session() as session:
            if updated_seller := await session.get(cls.model, seller_id):
                updated_seller.first_name = new_data.first_name
                updated_seller.last_name = new_data.last_name
                updated_seller.email = new_data.email

                await session.flush()
                result_dto = BaseSeller.model_validate(updated_seller, from_attributes=True)
                return result_dto
