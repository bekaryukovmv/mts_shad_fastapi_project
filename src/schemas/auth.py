"""
A model for validating the data that the user pass to receive the token.
"""

from pydantic import BaseModel

__all__ = ["LoginSchema"]


class LoginSchema(BaseModel):
    email: str
    password: str
