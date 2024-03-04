from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations import get_async_engine
from src.configurations.database import create_db_and_tables, delete_db_and_tables
from src.routers import v1_router

from src.routers.dependencies import get_seller_dao, get_book_dao
from src.routers import dependency_stubs as stubs


@asynccontextmanager
async def lifespan(app: FastAPI):  # Рекомендуется теперь вместо @app.on_event()
    engine = await get_async_engine()

    # Создание таблиц
    await create_db_and_tables(engine)

    # Получение сессии
    async def get_session():
        async with AsyncSession(
            engine, expire_on_commit=False
        ) as session, session.begin():
            yield session
            await session.commit()

    app.dependency_overrides[stubs.get_session] = get_session

    yield

    # Удаление таблиц
    await delete_db_and_tables(engine)

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="New Book Library App",
        description="Доработанное учебное приложение для группы MTS Shad",
        version="0.1.0",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор
        lifespan=lifespan,
    )

    app.include_router(v1_router)
    app.dependency_overrides[stubs.get_seller_dao] = get_seller_dao
    app.dependency_overrides[stubs.get_book_dao] = get_book_dao

    return app
