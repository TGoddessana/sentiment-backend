from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.requests import Request

from application.models import StoreItem
from application.schemas import StoreItemResponse
from config.dependencies import SessionDependency

router = APIRouter()


def _get_item_or_404(item_id: int, db_session: SessionDependency) -> StoreItem:
    """
    주어진 ID로 상점 아이템을 조회하고, 없으면 404 에러를 발생시킵니다.
    """
    stmt = select(StoreItem).where(StoreItem.id == item_id)
    item = db_session.scalar(stmt)
    if not item:
        raise HTTPException(status_code=404, detail="상점 아이템을 찾을 수 없습니다.")
    return item


@router.get(
    "/items",
    response_model=list[StoreItemResponse],
    summary="상점 아이템 목록 조회",
    description="상점에 등록된 모든 아이템의 목록을 조회합니다.",
)
def get_store_items(
    request: Request,
    db_session: SessionDependency,
):
    """
    상점 아이템 목록을 조회합니다.
    """
    stmt = select(StoreItem).order_by(StoreItem.id)
    items = db_session.scalars(stmt).all()

    return [StoreItemResponse.from_store_item(item, request) for item in items]


@router.get(
    "/items/{item_id}",
    response_model=StoreItemResponse,
    summary="상점 아이템 상세 조회",
    description="주어진 ID로 상점 아이템의 상세 정보를 조회합니다.",
)
def get_store_item(
    item_id: int,
    request: Request,
    db_session: SessionDependency,
):
    """
    주어진 ID로 상점 아이템의 상세 정보를 조회합니다.
    """
    item = _get_item_or_404(item_id, db_session)
    return StoreItemResponse.from_store_item(item, request)
