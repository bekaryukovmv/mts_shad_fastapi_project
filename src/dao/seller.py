from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.dao.base import BaseDAO
from src.models.books import Seller
from src.schemas.seller import BaseSeller, SellerDTO, SellerUpdate


class SellerDAO(BaseDAO):
    model = Seller

    async def create_seller(self, **data):
        new_seller = self.model(**data)
        self.session.add(new_seller)
        await self.session.flush()
        result_dto = BaseSeller.model_validate(new_seller, from_attributes=True)
        return result_dto

    async def select_seller_with_books(self, seller_id: int):
        query = (
            select(Seller).where(Seller.id == seller_id)
            .options(joinedload(Seller.books))
        )

        res = await self.session.execute(query)
        result_orm = res.unique().scalars().one_or_none()

        if not result_orm:
            return None

        result_dto = SellerDTO.model_validate(result_orm, from_attributes=True)
        return result_dto

    async def update_seller(self, seller_id: int, new_data: SellerUpdate) -> BaseSeller | None:
        updated_seller = await self.session.get(self.model, seller_id)
        if not updated_seller:
            return None

        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await self.session.flush()
        result_dto = BaseSeller.model_validate(updated_seller, from_attributes=True)
        return result_dto
