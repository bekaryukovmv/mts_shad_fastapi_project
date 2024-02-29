from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.lib.auth import hash_password, access_security, refresh_security
from src.models.books import Book
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.dao import SellerDAO
from src.schemas.seller import SellerAuth
from src.schemas.token import RefreshToken, AccessToken

token_router = APIRouter(tags=["token"], prefix="/token")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/")
async def get_seller_tokens(seller_auth: SellerAuth):
    user = await SellerDAO.find_one_or_none(email=seller_auth.email)
    if user is None or hash_password(user.password) != user.password:
        # Пользователь ввёл неверные данные для аутентификации
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    # По желанию тут можно добавить проверку подтверждения почты.
    access_token = access_security.create_access_token({"username": user.email})
    refresh_token = refresh_security.create_refresh_token({"username": user.email})
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)


@token_router.post("/refresh")
async def get_access_token(auth: JwtAuthorizationCredentials = Security(refresh_security)) -> AccessToken:
    access_token = access_security.create_access_token(subject=auth.subject)
    return AccessToken(access_token=access_token)
