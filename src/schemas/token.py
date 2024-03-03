from pydantic import BaseModel

__all__ = ["TokenInfo"]


class TokenInfo(BaseModel):
    access_token: str
    token_type: str