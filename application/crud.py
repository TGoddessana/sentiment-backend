from typing import TypeVar, Type

from fastapi import status, HTTPException
from sqlalchemy import select

from application.models import IdModel
from config.dependencies import SessionDependency

T = TypeVar("T", bound=IdModel)


def get_model_or_404(
    model_pk: int,
    db_session: SessionDependency,
    model_class: type[T],
) -> T:
    """
    주어진 ID로 객체를 조회하고, 객체가 없으면 404 에러를 발생시킵니다.
    """
    stmt = select(model_class).where(model_class.id == model_pk)  # type: ignore
    instance = db_session.scalar(stmt)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상점 아이템을 찾을 수 없습니다.",
        )
    return instance
