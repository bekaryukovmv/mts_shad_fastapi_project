from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.configurations.database import create_db_and_tables, delete_db_and_tables, global_init
from src.routers import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # Рекомендуется теперь вместо @app.on_event()
    # Запускается при старте приложения
    global_init()
    await create_db_and_tables()
    yield
    # Запускается при остановке приложения
    await delete_db_and_tables()


def create_application():
    return FastAPI(
        title="New Book Library App",
        description="Доработанное учебное приложение для группы MTS Shad",
        version="0.1.0",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор,
        lifespan=lifespan,
    )


app = create_application()


def _configure():
    app.include_router(v1_router)


_configure()
