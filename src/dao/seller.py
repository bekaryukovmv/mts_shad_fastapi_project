from src.dao.base import BaseDAO
from src.models.books import Seller


class SellerDAO(BaseDAO):
    model = Seller

