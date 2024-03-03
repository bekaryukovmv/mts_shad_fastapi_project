import pytest 
from fastapi import status
from sqlalchemy import select

from src.models import sellers, books

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Pupa",
        "last_name": "Pupkin",
        "email": "pupa42@mail.com",
        "password": "relpup99",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "Pupa",
        "last_name": "Pupkin",
        "email": "pupa42@mail.com",
    }

# Тест на ручку получения продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке. Руководствуемя логикой один тест - одно действие
    seller_1 = sellers.Seller(
        first_name = "Alex",
        last_name = "Tarletsky",
        email = "alexrut@gmail.com",
        password = "kjlkj",
    )
    seller_2 = sellers.Seller(
        first_name = "Kirill",
        last_name = "Andronov",
        email = "andron@mail.com",
        password = "9jlkj2i",
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "id": seller_1.id,
                "first_name": "Alex",
                "last_name": "Tarletsky",
                "email": "alexrut@gmail.com",
            },
            {
                "id": seller_2.id,
                "first_name": "Kirill",
                "last_name": "Andronov",
                "email": "andron@mail.com",
            },
        ]
    }

# Тест на ручку получение конкретной информации об одном продавце
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке. Руководствуемя логикой один тест - одно действие
    seller = sellers.Seller(
        first_name = "Alex",
        last_name = "Tarletsky",
        email = "alexrut@gmail.com",
        password = "kjlkj",
    )

    db_session.add(seller)
    await db_session.flush()

    # response = await async_client.get(f"/api/v1/sellers/{seller_1.id}")

    # assert response.states_code == status.HTTP_200_OK

    #Также сразу же создам книжку для этого продавца
    book = books.Book(
        seller_id = seller.id,
        author="Melville",
        title="Moby-Dick, or The Whale",
        year=1990,
        count_pages=242
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": seller.id,
        "first_name": "Alex",
        "last_name": "Tarletsky",
        "email": "alexrut@gmail.com",
        "books": [
            {   "id": book.id,
                "seller_id": seller.id,
                "author": "Melville",
                "title": "Moby-Dick, or The Whale",
                "year": 1990,
                "count_pages": 242,
            }
        ]
    }

# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке. Руководствуемя логикой один тест - одно действие
    seller = sellers.Seller(
        first_name = "Rosa",
        last_name = "Grinenko",
        email = "grinros@gmail.com",
        password = "afsda",
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке. Руководствуемя логикой один тест - одно действие
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan1666@mail.ru",
        password="ivanavi",
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json = {
            "id": seller.id,
            "first_name": "Danila",
            "last_name": "Zaruba",
            "email": "Zarub9@mail.com",
            "password": "9asfdlkj9",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "Danila"
    assert res.last_name == "Zaruba"
    assert res.email == "Zarub9@mail.com"


     





