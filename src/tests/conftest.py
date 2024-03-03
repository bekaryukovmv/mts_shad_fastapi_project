""" Это модуль с фикстурами для пайтеста.
Фикстуры - это особые функции, которые не надо импортировать явно.
Сам пайтест подтягивает их по имени из файла conftest.py
"""

import asyncio

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from src.configurations import global_init
from src.configurations.settings import settings, Settings
from src.models import books  # noqa
from src.models.base import BaseModel
from src.models.books import Book, Seller  # noqa F401


# Получаем цикл событий для асинхронного потока выполнения задач
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an instance of the default event loop for each test case."""
#     # loop = asyncio.get_event_loop_policy().new_event_loop()  # TODO
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    global_init()
    engine = create_async_engine(
        settings.database_test_url,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(engine: AsyncEngine):
    async with AsyncSession(engine, expire_on_commit=False) as _session, _session.begin():
        yield _session
        await _session.rollback()


# Callback для переопределения сессии в приложении
@pytest.fixture()
def override_get_async_session(db_session):
    async def _override_get_async_session():
        yield db_session

    return _override_get_async_session


# Мы не можем создать 2 приложения (app) - это приведет к ошибкам.
# Поэтому, на время запуска тестов мы подменяем там зависимость с сессией
@pytest.fixture()
def test_app(override_get_async_session):
    from src.configurations.database import get_async_session
    from src.main import app

    app.dependency_overrides[get_async_session] = override_get_async_session

    return app


# Создаем асинхронного клиента для ручек
@pytest_asyncio.fixture()
async def async_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as test_client:
        yield test_client


# Создание авторизованного клиента для тестов
@pytest_asyncio.fixture()
async def async_authenticated_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as test_client:
        # Данные для аутентификации
        test_email = "test@example.com"
        test_password = "test_password"

        # Регистрация нового продавца
        await test_client.post("/api/v1/seller/", json={
            "email": test_email,
            "password": test_password,
            "first_name": "Имя",
            "last_name": "Фамилия"
        })

        # Аутентификация - получение токенов
        res = await test_client.post("/api/v1/token/", json={
              "email": test_email,
              "password": test_password
        })

        res_json = res.json()

        # Добавление токена в заголовок клиента
        access_token = res_json["access_token"]
        test_client.headers["Authorization"] = "Bearer " + access_token

        # Сохранение refresh токена в куки клиента
        refresh_token = res_json["refresh_token"]
        test_client.cookies["CSRF"] = refresh_token
        yield test_client
