from pydantic import BaseModel, EmailStr


class SellerAuth(BaseModel):
    """
    Регистрация и аутентификация пользователя.
    """

    email: EmailStr
    password: str
