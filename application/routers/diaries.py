from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, and_, exists, select
from starlette import status

from application.models import Diary
from application.schemas import DiaryResponse, DiaryCreateInput, AnalyzedEmotion
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
    request_body: DiaryCreateInput,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    today = date.today()

    stmt = exists().where(
        and_(
            Diary.user_id == current_user.id,
            func.date(Diary.created_at) == today,
        )
    )

    if db_session.query(stmt).scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해당 날짜에 일기가 존재합니다.",
        )

    diary = Diary(
        user_id=current_user.id,
        weather=request_body.weather,
        title=request_body.title,
        content=request_body.content,
        image_urls=request_body.image_urls,
    )
    db_session.add(diary)
    db_session.flush()
    current_user.add_coin(100)
    db_session.refresh(diary)

    return diary


@router.get(
    "/",
    response_model=list[DiaryResponse],
    summary="일기 목록 조회",
    description="현재 로그인한 사용자가 작성한 일기 목록을 조회하는 API입니다. 사용자가 지금까지 작성한 모든 일기를 반환합니다.",
)
def read_diaries(
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diaries = db_session.query(Diary).filter(Diary.user_id == current_user.id).all()

    return [DiaryResponse.from_diary(diary) for diary in diaries]


@router.get(
    "/{diary_id}",
    response_model=DiaryResponse,
    summary="일기 상세 조회",
    description="일기 ID를 통해 특정 일기의 상세 정보를 조회하는 API입니다. 현재 로그인한 사용자의 일기만 조회할 수 있습니다.",
)
def read_diary_by_id(
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

    return DiaryResponse.from_diary(diary)


@router.delete(
    "/{diary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="일기 삭제",
    description="일기 ID를 통해 특정 일기를 삭제하는 API입니다. 현재 로그인한 사용자의 일기만 삭제할 수 있습니다.",
)
def delete_diary(
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

    db_session.delete(diary)

    return None
