from sqlalchemy import select

from src.configurations import get_async_session
from src.dao.base import BaseDAO
from src.models.books import Seller


class SellerDAO(BaseDAO):
    model = Seller

