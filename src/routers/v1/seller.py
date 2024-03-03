from typing import List, Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from src.lib.auth import current_seller, Auth, hash_password
from src.models.books import Seller
from src.dao import SellerDAO
from src.schemas.seller import SellerReg, BaseSeller, SellerUpdate, SellerDTO

seller_router = APIRouter(tags=["seller"], prefix="/seller")


def get_seller_dao() -> SellerDAO:
    raise NotImplementedError


SellerDAODep = Annotated[SellerDAO, Depends(get_seller_dao)]
AuthenticatedSeller = Annotated[Seller, Depends(current_seller)]


@seller_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_seller(seller_auth: SellerReg, dao: SellerDAODep) -> None:
    seller = await dao.find_one_or_none(email=seller_auth.email)
    if seller:
        # Пользователь существует
        raise HTTPException(status.HTTP_409_CONFLICT, "Продавец с таким email уже зарегистрирован")
    hashed_password = hash_password(seller_auth.password)
    await dao.add(email=seller_auth.email, password=hashed_password,
                  first_name=seller_auth.first_name, last_name=seller_auth.last_name)


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


@seller_router.delete("/{seller_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_seller(seller_id: int, dao: SellerDAODep) -> None:
    await dao.delete(id=seller_id)
