from fastapi import status
import pytest
from src.models.books import Seller


@pytest.mark.asyncio
async def test_get_seller_by_id(db_session, async_client, auth_seller_id):
    response = await async_client.get(f"/api/v1/seller/{auth_seller_id}")
    res_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert {"id", "first_name", "last_name", "email", "books"} == res_json.keys()


@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client, auth_seller_id):
    new_sellers = list()
    for _id in range(5):
        seller = Seller(
            email=f"test{_id}@gmail.com",
            password="pass",
            first_name="Test name",
            last_name="Test last name",
        )
        new_sellers.append(seller)
    db_session.add_all(new_sellers)
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert len(res_json) == 6


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client, auth_seller_id):
    response = await async_client.put(
        f"/api/v1/seller/{auth_seller_id}",
        json={"first_name": "Test name", "last_name": "Test last name", "email": "new@example.com"},
    )
    res_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert (
        res_json["id"] == auth_seller_id
        and {"first_name", "last_name", "email", "id"} == res_json.keys()
    )


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client, auth_seller_id):
    response = await async_client.delete(f"/api/v1/seller/{auth_seller_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    seller = await db_session.get(Seller, auth_seller_id)
    assert seller is None
