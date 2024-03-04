from typing import Annotated

from fastapi import Depends

from src.dao import BookDAO, SellerDAO


def get_session():
    raise NotImplementedError


def get_seller_dao() -> SellerDAO:
    raise NotImplementedError


def get_book_dao() -> BookDAO:
    raise NotImplementedError


SellerDAODep = Annotated[SellerDAO, Depends(get_seller_dao)]
BookDAODep = Annotated[BookDAO, Depends(get_book_dao)]


__all__ = ["get_session", "get_seller_dao", "get_book_dao", "SellerDAODep", "BookDAODep"]
