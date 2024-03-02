import pytest
from fastapi import status
from sqlalchemy import select

from src.models import sellers, books

### 1. POST /seller

# 1.1. Создание продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Joe",
        "last_name": "Peachy", 
        "email": "JoePeachy@email.com",
        "password": "pass"
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data["first_name"] == data["first_name"]
    assert result_data["last_name"] == data["last_name"]
    assert result_data["email"] == data["email"]
    assert result_data["password"] == data["password"]


### 2. GET /seller/seller_1

# 2.1. Проверка продавца и двух книг
@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Joe", last_name="Peachy", email="JoePeachy@email.com", password="pass")

    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")
    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()
    assert result_data["first_name"] == seller.first_name
    assert result_data["last_name"] == seller.last_name
    assert result_data["email"] == seller.email
    assert result_data["id"] == seller.id
    assert result_data["books"] == [
            {"id": book_1.id, "author": "Pushkin", "title": "Eugeny Onegin", "year": 2001, "count_pages": 104},
            {"id": book_2.id, "author": "Lermontov", "title": "Mziri", "year": 1997, "count_pages": 104}
        ]


### 3. GET /seller
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller_1 = sellers.Seller(first_name="Joe", last_name="Peachy", email="JoePeachy@email.com", password="pass")
    seller_2 = sellers.Seller(first_name="Eugin", last_name="Arrow", email="BabyStep@email.com", password="pass")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "sellers": [
            {"first_name": "Joe", "last_name": "Peachy", "email": "JoePeachy@email.com", "id": seller_1.id},
            {"first_name": "Eugin", "last_name": "Arrow", "email": "BabyStep@email.com", "id": seller_2.id}
        ]
    }


### 4. PUT /seller/seller_id

# 4.1. Создание двух продавцов и книг
@pytest.mark.asyncio
async def test_put_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Joe", last_name="Peachy", email="JoePeachy@email.com", password="pass")

    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()
    
    response = await async_client.put(f"/api/v1/sellers/{seller.id}",
                                      json={"first_name": "Eugin", "last_name": "Arrow", "email": "BabyStep@email.com"})
    


    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "Eugin"
    assert res.last_name == "Arrow"
    assert res.email == "BabyStep@email.com"


### 5. DELETE /seller/seller_id
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Joe", last_name="Peachy", email="JoePeachy@email.com", password="pass")

    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    # Проверка на то, что нет продавцов
    seller = await db_session.execute(select(sellers.Seller, seller.id))
    res = seller.scalars().all()
    assert len(res) == 0

    # Проверка на то, что нет книг
    for book_id in [book_1.id, book_2.id]:
        book = await db_session.execute(select(books.Book, book_id))
        res = book.scalars().all()
        assert len(res) == 0
