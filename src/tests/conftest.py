""" Это модуль с фикстурами для пайтеста.
Фикстуры - это особые функции, которые не надо импортировать явно.
Сам пайтест подтягивает их по имени из файла conftest.py
"""

import asyncio

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.configurations.settings import settings
from src.models import books  # noqa
from src.models.base import BaseModel
from src.models.books import Book  # noqa F401

# Переопределяем движок для запуска тестов и подключаем его к тестовой базе.
# Это решает проблему с сохранностью данных в основной базе приложения.
# Фикстуры тестов их не зачистят.
# и обеспечивает чистую среду для запуска тестов. В ней не будет лишних записей.
async_test_engine = create_async_engine(
    settings.database_test_url,
    echo=True,
)

# Создаем фабрику сессий для тестового движка.
async_test_session = async_sessionmaker(async_test_engine, expire_on_commit=False, autoflush=False)


# Получаем цикл событий для асинхорнного потока выполнения задач.
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    # loop = asyncio.new_event_loop() # На разных версиях питона и разных ОС срабатывает по разному
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# Создаем таблицы в тестовой БД. Предварительно удаляя старые.
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables() -> None:
    """Create tables in DB."""
    async with async_test_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.drop_all)
        await connection.run_sync(BaseModel.metadata.create_all)


# Создаем сессию для БД используемую для тестов
@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with async_test_engine.connect() as connection:
        async with async_test_session(bind=connection) as session:
            yield session
            await session.rollback()


# Коллбэк для переопределения сессии в приложении
@pytest.fixture(scope="function")
def override_get_async_session(db_session):
    async def _override_get_async_session():
        yield db_session

    return _override_get_async_session


# Мы не можем создать 2 приложения (app) - это приведет к ошибкам.
# Поэтому, на время запуска тестов мы подменяем там зависимость с сессией
@pytest.fixture(scope="function")
def test_app(override_get_async_session):
    from src.configurations.database import get_async_session
    from src.main import app

    app.dependency_overrides[get_async_session] = override_get_async_session

    return app


# создаем асинхронного клиента для ручек
@pytest_asyncio.fixture(scope="function")
async def async_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://127.0.0.1:8000") as test_client:
        yield test_client
