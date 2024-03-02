from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from src.lib.auth import hash_password, current_seller
from src.models.books import Seller
from src.dao import SellerDAO
from src.schemas.seller import SellerReg, BaseSeller, SellerUpdate, SellerDTO

seller_router = APIRouter(tags=["seller"], prefix="/seller")


@seller_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_seller(seller_auth: SellerReg) -> None:
    seller = await SellerDAO.find_one_or_none(email=seller_auth.email)
    if seller:
        # Пользователь существует
        raise HTTPException(status.HTTP_409_CONFLICT, "Продавец с таким email уже зарегистрирован")
    hashed_password = hash_password(seller_auth.password)
    await SellerDAO.add(email=seller_auth.email, password=hashed_password,
                        first_name=seller_auth.first_name, last_name=seller_auth.last_name)


@seller_router.get("/")
async def get_all_sellers() -> List[BaseSeller]:
    all_sellers = await SellerDAO.find_all()
    return all_sellers


@seller_router.get("/{seller_id}")
async def get_seller_info(seller_id: int, seller: Seller = Depends(current_seller)) -> SellerDTO | None:
    seller_info = await SellerDAO.select_seller_with_books(seller_id)
    return seller_info


@seller_router.put("/{seller_id}")
async def update_seller_info(new_data: SellerUpdate, seller_id: int) -> BaseSeller | None:
    seller_info = await SellerDAO.update_seller(seller_id, new_data)
    if not seller_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продавец с таким id не найден")
    return seller_info


@seller_router.delete("/{seller_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_seller(seller_id: int) -> None:
    await SellerDAO.delete(id=seller_id)
