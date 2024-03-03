from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, insert, delete

from src.models.base import BaseModel


class BaseDAO:
    model: BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, **filter_by):
        query = select(self.model.__table__.columns).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.mappings().one_or_none()

    async def find_all(self, **filter_by):
        query = select(self.model.__table__.columns).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.mappings().all()

    async def delete(self, **filter_by):
        query = delete(self.model).filter_by(**filter_by)
        await self.session.execute(query)

    async def add(self, **data):
        query = insert(self.model).values(**data)
        await self.session.execute(query)
