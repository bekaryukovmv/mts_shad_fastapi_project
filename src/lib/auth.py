from typing import Annotated

from fastapi import HTTPException, Depends

import bcrypt
from fastapi import Security

from src.configurations.settings import settings
from datetime import timedelta

from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer

from src.dao import SellerDAO
from src.models.books import Seller
from src.routers.dependency_stubs import SellerDAODep


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


class Auth:
    def __init__(self, auth, dao):
        self.auth: JwtAuthorizationCredentials = auth
        self.dao = dao

    async def seller_from_credentials(self) -> Seller | None:
        """
        Возвращает продавца, связанного с учетными данными.
        :param auth:
        :return:
        """
        seller = await self.dao.find_one_or_none(email=self.auth.subject["username"])
        return seller

    async def seller_from_token(self, token: str) -> Seller | None:
        """
        Получает продавца по токену.
        :param token:
        :return:
        """
        payload = access_security._decode(token)
        seller = await self.dao.find_one_or_none(email=payload["subject"]["username"])
        return seller


def hash_password(password: str) -> str:
    """
    Получает хэш-пароль для продавца.
    :param password:
    :return:
    """
    return bcrypt.hashpw(password.encode(), settings.salt_bytes).decode()


async def current_seller(auth: Annotated[JwtAuthorizationCredentials, Security(access_security)],
                         dao: SellerDAODep) -> Seller:
    """Получает текущую авторизацию продавца."""
    auth_obj = Auth(auth, dao)
    if not auth_obj.auth:
        raise HTTPException(401, "Вход не выполнен")
    seller = await auth_obj.seller_from_credentials()
    if seller is None:
        raise HTTPException(404, "Авторизованный продавец не найден")
    return seller
