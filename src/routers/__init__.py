from fastapi import APIRouter

from .v1.books import books_router
from .v1.sellers import sellers_router
from .v1.token import token_router

v1_router = APIRouter(tags=["v1"], prefix="/api/v1")

v1_router.include_router(books_router)
v1_router.include_router(sellers_router)
v1_router.include_router(token_router)
