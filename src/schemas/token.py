"""
A model for validating the token data.
"""

from pydantic import BaseModel

__all__ = ["TokenInfo"]


class TokenInfo(BaseModel):
    access_token: str
    token_type: str