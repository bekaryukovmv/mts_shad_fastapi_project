from pydantic import BaseModel

__all__ = ["LoginSchema"]


class LoginSchema(BaseModel):
    email: str
    password: str
