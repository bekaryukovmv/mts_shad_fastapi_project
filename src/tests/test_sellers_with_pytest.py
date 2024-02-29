import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Ivan", "last_name": "Ivanov", "email": "iivanov@mail.ru", "password": "123"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "iivanov@mail.ru",
        "id": result_data["id"]
    }

# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@mail.ru", password="123"
    )
    seller_2 = sellers.Seller(
        first_name="Vasya", last_name="Petrov", email="vpetrov@mail.ru", password="321"
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        "sellers": [
            {
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "email": "iivanov@mail.ru",
                "id": seller_1.id
            },

            {
                "first_name": "Vasya",
                "last_name": "Petrov",
                "email": "vpetrov@mail.ru",
                "id": seller_2.id,
            }
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@mail.ru", password="123"
    )

    db_session.add_all([seller_1])
    await db_session.flush()

    book = books.Book(author="Mark Twen", title="Tom Soyer", year=1997, count_pages=200, seller_id=seller_1.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "iivanov@mail.ru",
        "books": [
                    {
                        "author": "Mark Twen",
                        "title": "Tom Soyer",
                        "year": 1997,
                        "count_pages": 200,
                        "id": book.id,
                    }

        ]
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@mail.ru", password="123"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления данных о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@mail.ru", password="123"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"id": seller.id, "first_name": "Petr", "last_name": "Petrov", "email": "petrov@mail.ru", "password": "321"},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "Petr"
    assert res.last_name == "Petrov"
    assert res.email == "petrov@mail.ru"