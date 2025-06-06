from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from starlette.requests import Request

from application.models import StoreItem, ItemCategory
from application.crud import get_model_or_404
from application.schemas import (
    StoreItemResponse,
    UserItemResponse,
)
from config.dependencies import SessionDependency, CurrentUser

router = APIRouter()


@router.get(
    "/items",
    response_model=list[StoreItemResponse],
    summary="상점 아이템 목록 조회",
    description="상점에 등록된 모든 아이템의 목록을 조회합니다.",
)
def get_store_items(
    request: Request,
    category: ItemCategory,
    db_session: SessionDependency,
    current_user: CurrentUser,
):
    """
    상점 아이템 목록을 조회합니다.
    """
    stmt = (
        select(StoreItem).where(StoreItem.category == category).order_by(StoreItem.id)
    )
    store_items = db_session.scalars(stmt).all()

    return [
        StoreItemResponse.from_store_item(
            request=request,
            store_item=store_item,
            current_user=current_user,
        )
        for store_item in store_items
    ]


@router.get(
    "/items/{item_id}",
    response_model=StoreItemResponse,
    summary="상점 아이템 상세 조회",
    description="주어진 ID로 상점 아이템의 상세 정보를 조회합니다.",
)
def get_store_item(
    item_id: int,
    request: Request,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    """
    주어진 ID로 상점 아이템의 상세 정보를 조회합니다.
    """
    store_item = get_model_or_404(item_id, db_session, StoreItem)
    return StoreItemResponse.from_store_item(
        request=request,
        store_item=store_item,
        current_user=current_user,
    )


@router.post(
    "/items/{item_id}/purchase",
    response_model=UserItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="아이템 구매",
    description="상점에서 아이템을 구매합니다.",
)
def purchase_item(
    item_id: int,
    request: Request,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    """
    상점에서 아이템을 구매합니다.
    """
    store_item = get_model_or_404(item_id, db_session, StoreItem)

    try:
        user_item = current_user.purchase_item(store_item)
        db_session.add(user_item)
        db_session.commit()
        db_session.refresh(user_item)

        return UserItemResponse(
            id=user_item.id,
            item=StoreItemResponse.from_store_item(
                request=request,
                store_item=store_item,
                current_user=current_user,
            ),
            purchased_at=user_item.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/items/{item_id}/equip",
    status_code=status.HTTP_200_OK,
    summary="아이템 장착",
    description="구매한 아이템을 장착합니다.",
)
def equip_item(
    item_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    """
    구매한 아이템을 장착합니다.
    """
    store_item = get_model_or_404(item_id, db_session, StoreItem)

    try:
        current_user.equip_item(store_item)
        db_session.commit()
        return {"message": f"{store_item.category} 아이템이 장착되었습니다."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/items/{item_id}/unequip",
    status_code=status.HTTP_200_OK,
    summary="아이템 장착해제",
    description="구매한 아이템을 장착해제합니다.",
)
def equip_item(
    item_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    """
    구매한 아이템을 장착 해제합니다.
    """
    store_item = get_model_or_404(item_id, db_session, StoreItem)

    try:
        current_user.unequip_item(store_item)
        db_session.commit()
        return {"message": f"{store_item.name} 아이템이 장착 해제되었습니다."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
