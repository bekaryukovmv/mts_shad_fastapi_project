import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Sasha", "last_name": "Ivanova", "email": "ivanova@mail.ru", "password": "Qwe123123"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data["first_name"] == "Sasha"
    assert result_data["last_name"] == "Ivanova"
    assert result_data["email"] == "ivanova@mail.ru"


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = sellers.Seller(first_name="Sasha", last_name="Ivanova", email="ivanova@mail.ru", password="Qwe123123")
    seller_2 = sellers.Seller(first_name="Alex", last_name="Bronov", email="abronov@mail.ru", password="qwerty2002")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {"first_name": "Sasha", "last_name": "Ivanova", "email": "ivanova@mail.ru", "id": seller.id},
            {"first_name": "Alex", "last_name": "Bronov", "email": "abronov@mail.ru", "id": seller_2.id},
        ]
    }


@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Sasha", last_name="Ivanova", email="ivanova@mail.ru", password="Qwe123123")
    seller_2 = sellers.Seller(first_name="Alex", last_name="Bronov", email="abronov@mail.ru", password="qwerty2002")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "first_name": "Sasha",
        "last_name": "Ivanova",
        "email": "ivanova@mail.ru",
        "id": seller.id,
        "books": [],
    }


@pytest.mark.asyncio
async def test_get_single_seller_with_books(db_session, async_client):
    seller = sellers.Seller(first_name="Sasha", last_name="Ivanova", email="ivanova@mail.ru", password="Qwe123123")

    db_session.add_all([seller])
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "first_name": "Sasha",
        "last_name": "Ivanova",
        "email": "ivanova@mail.ru",
        "id": seller.id,
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "count_pages": 104,
                "seller_id": seller.id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "count_pages": 104,
                "seller_id": seller.id,
            },
        ],
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Sasha", last_name="Ivanova", email="ivanova@mail.ru", password="Qwe123123")

    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    books_by_seller = await db_session.execute(select(books.Book).filter(books.Book.seller_id == seller.id))
    res = books_by_seller.scalars().all()
    assert len(res) == 0

    seller = await db_session.execute(select(sellers.Seller).filter(sellers.Seller.id == seller.id))
    res = seller.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Sasha", last_name="Ivanova", email="ivanova@mail.ru", password="Qwe123123")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "first_name": "Alex",
            "last_name": "Bronov",
            "email": "abronov@mail.ru",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Alex"
    assert res.last_name == "Bronov"
    assert res.email == "abronov@mail.ru"
