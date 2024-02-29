from datetime import timedelta

from pydantic import BaseModel

from src.lib.auth import ACCESS_EXPIRES, REFRESH_EXPIRES


class AccessToken(BaseModel):
    access_token: str
    access_token_expires: timedelta = ACCESS_EXPIRES


class RefreshToken(AccessToken):
    refresh_token: str
    refresh_token_expires: timedelta = REFRESH_EXPIRES
