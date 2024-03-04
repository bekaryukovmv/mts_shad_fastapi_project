from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from src.lib.auth import Auth, current_seller, hash_password
from src.models.books import Seller
from src.routers.dependency_stubs import SellerDAODep
from src.schemas.seller import BaseSeller, SellerDTO, SellerReg, SellerUpdate

seller_router = APIRouter(tags=["seller"], prefix="/seller")

AuthenticatedSeller = Annotated[Seller, Depends(current_seller)]


@seller_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_seller(seller_auth: SellerReg, dao: SellerDAODep) -> BaseSeller:
    seller = await dao.find_one_or_none(email=seller_auth.email)
    if seller:
        # Пользователь существует
        raise HTTPException(status.HTTP_409_CONFLICT, "Продавец с таким email уже зарегистрирован")
    hashed_password = hash_password(seller_auth.password)
    new_seller = await dao.create_seller(email=seller_auth.email, password=hashed_password,
                                         first_name=seller_auth.first_name, last_name=seller_auth.last_name)
    return new_seller


@seller_router.get("/")
async def get_all_sellers(dao: SellerDAODep) -> List[BaseSeller]:
    all_sellers = await dao.find_all()
    return all_sellers


@seller_router.get("/{seller_id}")
async def get_seller_info(seller_id: int, dao: SellerDAODep, seller: AuthenticatedSeller) -> SellerDTO | None:
    seller_info = await dao.select_seller_with_books(seller_id)
    return seller_info


@seller_router.put("/{seller_id}")
async def update_seller_info(new_data: SellerUpdate, seller_id: int, dao: SellerDAODep) -> BaseSeller | None:
    seller_info = await dao.update_seller(seller_id, new_data)
    if not seller_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продавец с таким id не найден")
    return seller_info


@seller_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, dao: SellerDAODep) -> None:
    await dao.delete(id=seller_id)
