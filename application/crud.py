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
            detail="찾을 수 없는 리소스입니다.",
        )
    return instance


def get_model_or_403(
    model_pk: int,
    db_session: SessionDependency,
    user_id: int,
    model_class: Type[T],
) -> T:
    """
    주어진 ID로 객체를 조회하고, 객체가 없거나 사용자 ID가 일치하지 않으면 403 에러를 발생시킵니다.
    model_class 는 user_id 필드를 가지고 있다고 가정합니다.
    """
    if not hasattr(model_class, "user_id"):
        raise ValueError("model_class must have a user_id attribute")

    instance = get_model_or_404(
        model_pk=model_pk,
        db_session=db_session,
        model_class=model_class,
    )
    if instance.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없는 리소스입니다.",
        )
    return instance
