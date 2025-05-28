from datetime import date

from fastapi import APIRouter, HTTPException
from starlette import status

from application.models import Diary
from application.schemas import DiaryResponse, DiaryCreateInput
from config.dependencies import CurrentUser, SessionDependency


router = APIRouter()


@router.post(
    "/",
    response_model=DiaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_diary(
    request_body: DiaryCreateInput,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diary = Diary(
        user_id=current_user.id,
        date=date.fromisoformat(request_body.date),
        weather=request_body.weather,
        title=request_body.title,
        content=request_body.content,
        image_urls=request_body.image_urls,
    )

    db_session.add(diary)
    db_session.commit()
    db_session.refresh(diary)

    return diary


@router.get(
    "/",
    response_model=list[DiaryResponse],
)
def read_diaries(
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diaries = db_session.query(Diary).filter(Diary.user_id == current_user.id).all()
    return diaries


@router.get(
    "/{diary_id}",
    response_model=DiaryResponse,
)
def read_diary(
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diary = (
        db_session.query(Diary)
        .filter(
            Diary.id == diary_id,
            Diary.user_id == current_user.id,
        )
        .first()
    )

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다.",
        )

    return diary


@router.put(
    "/{diary_id}",
    response_model=DiaryResponse,
)
def update_diary(
    diary_id: int,
    request_body: DiaryCreateInput,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diary = (
        db_session.query(Diary)
        .filter(Diary.id == diary_id, Diary.user_id == current_user.id)
        .first()
    )

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다.",
        )

    diary.date = date.fromisoformat(request_body.date)
    diary.weather = request_body.weather
    diary.title = request_body.title
    diary.content = request_body.content
    diary.image_urls = request_body.image_urls

    db_session.commit()
    db_session.refresh(diary)

    return diary


@router.delete(
    "/{diary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_diary(
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diary = (
        db_session.query(Diary)
        .filter(Diary.id == diary_id, Diary.user_id == current_user.id)
        .first()
    )

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다.",
        )

    db_session.delete(diary)
    db_session.commit()

    return None
