import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import BaseModel
from src.models.books import Book, Seller  # noqa F401

from .settings import settings

logger = logging.getLogger("__name__")


__all__ = ["get_async_engine", "create_db_and_tables", "delete_db_and_tables"]

SQLALCHEMY_DATABASE_URL = settings.database_url


async def get_async_engine() -> AsyncEngine:
    engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)  # TODO
    return engine


async def create_db_and_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def delete_db_and_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
