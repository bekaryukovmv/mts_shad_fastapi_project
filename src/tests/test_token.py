from fastapi import status
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_new_access_token(db_session, async_client: AsyncClient, auth_seller_id):
    refresh_token = async_client.cookies.get("CSRF")
    async_client.headers["Authorization"] = "Bearer " + refresh_token
    response = await async_client.post(f"/api/v1/token/refresh")
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert "access_token" in res_json.keys()
