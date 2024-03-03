import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.configurations.security import hashing_password


# POST /books test
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivanov@ivanov.ru",
        password=hashing_password("123abc123")
    )
    seller_data_for_token = {
        "email": "ivanov@ivanov.ru",
        "password": "123abc123"
    }

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.post("/api/v1/token/", json=seller_data_for_token)

    assert response.status_code == status.HTTP_201_CREATED

    seller_token = response.json()["access_token"]

    book_data = {
        "title": "Wrong Code",
        "author": "Robert Martin",
        "pages": 104,
        "year": 2007,
        "seller_id": seller.id
    }

    response = await async_client.post("/api/v1/books/",
                                       json=book_data,
                                       headers={"Authorization": f"Bearer {seller_token}"})

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": seller.id
    }


# GET /books test
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivanov@ivanov.ru",
        password=hashing_password("123abc123")
    )

    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2

    assert response.json() == {
        "books": [
            {"title": "Eugeny Onegin",
             "author": "Pushkin",
             "year": 2001,
             "id": book.id,
             "count_pages": 104,
             "seller_id": seller.id},
            {"title": "Mziri",
             "author": "Lermontov",
             "year": 1997,
             "id": book_2.id,
             "count_pages": 104,
             "seller_id": seller.id},
        ]
    }


# GET /books/{book_id} test
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivanov@ivanov.ru",
        password=hashing_password("123abc123")
    )

    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": seller.id
    }
    response = await async_client.get(f"/api/v1/books/{book_2.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "title": "Mziri",
        "author": "Lermontov",
        "year": 1997,
        "id": book_2.id,
        "count_pages": 104,
        "seller_id": seller.id}


# DELETE /books/{book_id} test
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivanov@ivanov.ru",
        password=hashing_password("123abc123")
    )

    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# PUT /books/{book_id} test
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    seller = sellers.Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivanov@ivanov.ru",
        password=hashing_password("123abc123")
    )
    seller_data_for_token = {
        "email": "ivanov@ivanov.ru",
        "password": "123abc123"
    }

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.post("/api/v1/token/", json=seller_data_for_token)

    assert response.status_code == status.HTTP_201_CREATED

    seller_token = response.json()["access_token"]

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "id": book.id,
            "title": "Mziri",
            "author": "Lermontov",
            "count_pages": 100,
            "year": 2007,
            "seller_id": seller.id
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id
    assert res.seller_id == seller.id
