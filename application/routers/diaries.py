import os
from datetime import date
from typing import Annotated, Dict

from fastapi import APIRouter, HTTPException, Form, UploadFile
from sqlalchemy import func, and_, exists, select
from starlette import status
from starlette.requests import Request

from application.models import Diary
from application.schemas import (
    DiaryResponse,
    DiaryListResponse,
    DiaryCreateInput,
    AnalyzedEmotion,
)
from application.utils import write_file
from config.dependencies import CurrentUser, SessionDependency

router = APIRouter()


@router.post(
    "/",
    response_model=DiaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="일기 작성",
    description="현재 로그인한 사용자가 일기를 작성하는 API입니다. 오늘 날짜에 이미 작성된 일기가 있는 경우, 오류를 반환합니다.",
)
def create_diary(
    request: Request,
    request_formdata: Annotated[
        DiaryCreateInput, Form(media_type="multipart/form-data")
    ],
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    stmt = exists().where(
        and_(
            Diary.user_id == current_user.id,
            func.date(Diary.created_at) == date.today(),
        )
    )

    if db_session.query(stmt).scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해당 날짜에 일기가 존재합니다.",
        )

    diary = Diary(
        user_id=current_user.id,
        weather=request_formdata.weather,
        title=request_formdata.title,
        content=request_formdata.content,
        image_urls=[
            write_file(current_user.login_id, file)
            for file in request_formdata.image_files
        ],
    )
    db_session.add(diary)
    db_session.flush()
    current_user.add_coin(100)
    db_session.refresh(diary)

    return DiaryResponse.from_diary(request=request, diary=diary)


@router.get(
    "/",
    response_model=Dict[str, DiaryListResponse],
    summary="일기 목록 조회",
    description="현재 로그인한 사용자가 작성한 일기 목록을 조회하는 API입니다. 사용자가 지금까지 작성한 모든 일기를 반환합니다. 반환 형식은 {'날짜': 일기}의 딕셔너리입니다.",
)
def read_diaries(
    request: Request,
    current_user: CurrentUser,
    month: int,
    db_session: SessionDependency,
):
    stmt = select(Diary).where(
        Diary.user_id == current_user.id,
        func.extract("month", Diary.created_at) == month,
    )

    diaries = db_session.execute(stmt).scalars().all()

    return {
        diary.created_at.strftime("%Y-%m-%d"): DiaryListResponse.from_diary(
            request=request, diary=diary
        )
        for diary in diaries
    }


@router.get(
    "/{diary_id}",
    response_model=DiaryResponse,
    summary="일기 상세 조회",
    description="일기 ID를 통해 특정 일기의 상세 정보를 조회하는 API입니다. 현재 로그인한 사용자의 일기만 조회할 수 있습니다.",
)
def read_diary_by_id(
    request: Request,
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    stmt = select(Diary).where(
        Diary.id == diary_id,
        Diary.user_id == current_user.id,
    )
    result = db_session.execute(stmt)
    diary = result.scalar_one_or_none()

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다.",
        )

    return DiaryResponse.from_diary(request=request, diary=diary)
