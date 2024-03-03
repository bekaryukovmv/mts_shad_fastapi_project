from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import LoginSchema, TokenInfo

from src.configurations.security import validate_password, encode_jwt

token_router = APIRouter(tags=["token"], prefix="/token")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для получения JWT-токена по email и password
@token_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TokenInfo)
async def auth_user(user: LoginSchema, session: DBSession):
    query = (
        select(Seller).where(Seller.email == user.email)
    )
    res = await session.execute(query)
    res = res.scalar()

    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not validate_password(user.password, res.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    jwt_payload = {
        "email": user.email
    }

    token = encode_jwt(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type='Bearer',
    )
