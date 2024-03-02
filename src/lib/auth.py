from fastapi import HTTPException

import bcrypt
from fastapi import Security

from src.configurations.settings import settings
from datetime import timedelta

from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer

from src.dao import SellerDAO
from src.models.books import Seller


def hash_password(password: str) -> str:
    """
    Получает хэш-пароль для пользователя.
    :param password:
    :return:
    """
    return bcrypt.hashpw(password.encode(), settings.salt_bytes).decode()


# Время действия access и refresh токенов
ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)

access_security = JwtAccessBearer(
    settings.secret_key,
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
    auto_error=False,
)

refresh_security = JwtRefreshBearer(
    settings.secret_key,
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
    auto_error=False,
)


async def seller_from_credentials(auth: JwtAuthorizationCredentials) -> Seller | None:
    """
    Возвращает пользователя, связанного с учетными данными.
    :param auth:
    :return:
    """
    seller = await SellerDAO.find_one_or_none(email=auth.subject["username"])
    return seller


async def seller_from_token(token: str) -> Seller | None:
    """
    Получает пользователя по токену.
    :param token:
    :return:
    """
    payload = access_security._decode(token)
    seller = await SellerDAO.find_one_or_none(email=payload["subject"]["username"])
    return seller


async def current_seller(auth: JwtAuthorizationCredentials = Security(access_security)) -> Seller:
    """Получает текущую авторизацию пользователя."""
    if not auth:
        raise HTTPException(401, "Вход не выполнен")
    seller = await seller_from_credentials(auth)
    if seller is None:
        raise HTTPException(404, "Авторизованный продавец не найден")
    return seller
