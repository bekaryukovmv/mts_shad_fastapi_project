from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Security, Depends
from fastapi_jwt import JwtAuthorizationCredentials

from src.lib.auth import Auth, hash_password, access_security, refresh_security
from src.dao import SellerDAO
from src.schemas.seller import SellerAuth
from src.schemas.token import RefreshToken, AccessToken

token_router = APIRouter(tags=["token"], prefix="/token")


def get_seller_dao() -> SellerDAO:
    raise NotImplementedError


SellerDAODep = Annotated[SellerDAO, Depends(get_seller_dao)]


@token_router.post("/")
async def get_seller_tokens(seller_auth: SellerAuth, dao: SellerDAODep) -> RefreshToken:
    user = await dao.find_one_or_none(email=seller_auth.email)
    if user is None or hash_password(seller_auth.password) != user.password:
        # Пользователь ввёл неверные данные для аутентификации
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    # По желанию тут можно добавить подтверждение почты продавца
    # access_token = access_security.create_access_token({"username": user.email})
    access_token = "token 1"
    # refresh_token = refresh_security.create_refresh_token({"username": user.email})
    refresh_token = "token 1"
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)


@token_router.post("/refresh")
async def get_access_token(auth: JwtAuthorizationCredentials = Security(refresh_security)) -> AccessToken:
    access_token = access_security.create_access_token(subject=auth.subject)
    return AccessToken(access_token=access_token)
