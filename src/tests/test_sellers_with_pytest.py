import pytest
from fastapi import status
from sqlalchemy import select

from src.models import tables

result = {
    "sellers": [
        {"first_name": "der", "last_name": "dur", "email": "bk@blank.ru", "password": "default", "id": 2},
        {"first_name": "dur", "last_name": "der", "email": "kb@blank.ru", "password": "default", "id": 1},
    ]
}


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "dur", "last_name": "der", "email": "kb@blank.ru", "password": "default"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "dur",
        "last_name": "der",
        "email": "kb@blank.ru",
        "password": "default",
        "id": 1,
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = tables.Seller(first_name= "dur", last_name= "der",email= "kb@blank.ru", password= "default")
    seller_2 = tables.Seller(first_name= "der", last_name= "dur", email="bk@blank.ru", password= "default")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "dur", "last_name": "der", "email":"kb@blank.ru","password=":"default","id": seller_1.id},
            {"first_name": "der", "last_name": "dur", "email": "bk@blank.ru","password":"default", "id": seller_2.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = tables.Seller(first_name= "dur", last_name= "der",email= "kb@blank.ru", password= "default")
    seller_2 = tables.Seller(first_name= "der", last_name= "dur", email="bk@blank.ru", password= "default")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "dur",
        "last_name": "der",
        "email": "kb@blank.ru",
        "password": "default",
        "id": seller_1.id,
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = tables.Seller(first_name= "dur", last_name= "der",email= "kb@blank.ru", password= "default")

    db_session.add(seller_1)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller_1.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(tables.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = tables.Seller(first_name= "dur", last_name= "der",email= "kb@blank.ru", password= "default")

    db_session.add(seller_1)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller_1.id}",
        json={"first_name": "dur", "last_name": "der", "email": "kb@blank.ru", "password": "default", "id": seller_1.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(tables.Seller,seller_1.id)
    assert res.first_name == "dur"
    assert res.last_name == "der"
    assert res.email == "kb@blank.ru"
    assert res.password == "default"
    assert res.id == seller_1.id
