import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.configurations.settings import settings
from src.main import create_app
from src.models import books  # noqa
from src.models.base import BaseModel
from src.models.books import Book, Seller  # noqa F401
from src.routers import dependency_stubs as stubs


@pytest_asyncio.fixture(scope="session")
async def engine():
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
    app = create_app()
    app.lifespan = None

    app.dependency_overrides[stubs.get_session] = override_get_async_session
    return app


# Создаем асинхронного клиента для ручек
@pytest_asyncio.fixture()
async def async_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as test_client:
        yield test_client


# Создание авторизованного клиента
@pytest_asyncio.fixture()
async def auth_seller_id(async_client: AsyncClient):
    # Данные для аутентификации
    test_email = "test@example.com"
    test_password = "test_password"

    # Регистрация нового продавца
    res = await async_client.post("/api/v1/seller/", json={
        "email": test_email,
        "password": test_password,
        "first_name": "Имя",
        "last_name": "Фамилия"
    })

    # Получение ID пользователя
    res_json = res.json()
    seller_id = res_json["id"]

    # Аутентификация - получение токенов
    res = await async_client.post("/api/v1/token/", json={
          "email": test_email,
          "password": test_password
    })

    res_json = res.json()

    # Добавление токена в заголовок клиента
    access_token = res_json["access_token"]
    async_client.headers["Authorization"] = "Bearer " + access_token

    # Сохранение refresh токена в куки клиента
    refresh_token = res_json["refresh_token"]
    async_client.cookies["CSRF"] = refresh_token
    yield seller_id
