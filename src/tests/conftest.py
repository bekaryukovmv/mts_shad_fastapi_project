"""
Module with fixtures for the pytest.
Fixtures are special functions that do not need to be imported explicitly.
The patent itself pulls them up by name from the file conftest.py
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

# Redefine the engine for running tests and connect it to the test database.
# This solves the problem of data security in the main database of the application.
# Test fixtures won't clean them up.
# and provides a clean environment for running tests. There will be no unnecessary entries in it.
async_test_engine = create_async_engine(
    settings.database_test_url,
    echo=True,
)

# Creating a session factory for the test engine.
async_test_session = async_sessionmaker(async_test_engine, expire_on_commit=False, autoflush=False)


# We get an event loop for the asynchronous task execution flow.
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    # loop = asyncio.new_event_loop() # На разных версиях питона и разных ОС срабатывает по разному
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables() -> None:
    """Create tables in DB."""
    async with async_test_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.drop_all)
        await connection.run_sync(BaseModel.metadata.create_all)


# Create session
@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with async_test_engine.connect() as connection:
        async with async_test_session(bind=connection) as session:
            yield session
            await session.rollback()


# Callback to redefine the session in the application
@pytest.fixture(scope="function")
def override_get_async_session(db_session):
    async def _override_get_async_session():
        yield db_session

    return _override_get_async_session


@pytest.fixture(scope="function")
def test_app(override_get_async_session):
    from src.configurations.database import get_async_session
    from src.main import app

    app.dependency_overrides[get_async_session] = override_get_async_session

    return app


# Creating an asynchronous client
@pytest_asyncio.fixture(scope="function")
async def async_client(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://127.0.0.1:8000") as test_client:
        yield test_client
