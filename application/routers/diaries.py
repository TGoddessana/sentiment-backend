import json
from datetime import timedelta

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Query
from sqlalchemy import func, and_, exists, select
from starlette import status
from starlette.requests import Request

from application.constants import Emotion, MindContentType
from application.crud import get_model_or_404, get_model_or_403
from application.models import Diary, MindContent
from application.schemas import (
    DiaryResponse,
    DiaryCreateInput,
    DiaryListParams,
    DiaryCalendarResponse,
    MindContentRecommendationResponse,
    MindContentCreateRequest,
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
            Diary.date == request_formdata.diary_date,
        )
    )

    if db_session.query(stmt).scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해당 날짜에 일기가 존재합니다.",
        )

    diary = Diary(
        user_id=current_user.id,
        date=request_formdata.diary_date,
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
    response_model=dict[date, DiaryCalendarResponse],
    summary="일기 목록 조회",
    description="현재 로그인한 사용자가 작성한 일기 목록을 조회하는 API입니다. 사용자가 지금까지 작성한 모든 일기를 반환합니다. 반환 형식은 {'날짜': 일기}의 딕셔너리입니다.",
)
def read_diaries(
    request: Request,
    current_user: CurrentUser,
    params: Annotated[DiaryListParams, Query()],
    db_session: SessionDependency,
):
    stmt = (
        select(Diary)
        .where(
            Diary.user_id == current_user.id,
            func.extract("year", Diary.date) == params.year,
            func.extract("month", Diary.date) == params.month,
        )
        .order_by(Diary.date.desc())
    )
    diaries = db_session.execute(stmt).scalars().all()

    return {
        diary.date: DiaryCalendarResponse.from_diary(request=request, diary=diary)
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


@router.get(
    "/{diary_id}/mind-contents/level",
    summary="마음챙김 콘텐츠 레벨 조회",
    description="이번 주차의 일기 감정을 통해 레벨을 조회합니다. 레벨은 1, 2, 3 으로 나뉩니다.",
)
def read_mind_contents_level(
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    """
    - 부정적인 감정 30% 미만 - Level1 사진/글귀 랜덤 노출 (명상)
    - 부정적인 감정 30% 이상 50% 미만 - Level2 원인 분석
    - 부정적인 감정 50% 이상 - Level3 자신을 칭찬하는 문장 3개 받기 (Input)
    """

    negative_emotions = [
        Emotion.SAD.name,
        Emotion.ANXIOUS.name,
        Emotion.ANGRY.name,
        Emotion.TIRED.name,
        Emotion.LONELY.name,
        Emotion.BORED.name,
        Emotion.REGRETFUL.name,
        Emotion.JEALOUS.name,
        Emotion.CONFUSED.name,
    ]

    diary = get_model_or_404(
        model_pk=diary_id,
        db_session=db_session,
        model_class=Diary,
    )

    # 오늘이 화~일요일일 경우 -> 이번 주의 월요일~일기까지의 부정적인 감정 비율을 계산
    # 월요일부터 오늘까지의 일기만 조회
    start_date = diary.date - timedelta(days=diary.date.weekday())
    end_date = diary.date
    total_diaries_count = (
        db_session.query(Diary)
        .filter(
            Diary.user_id == current_user.id,
            Diary.date >= start_date,
            Diary.date <= end_date,
        )
        .count()
    )

    # 월요일부터 오늘까지의 일기에서 부정적인 감정 개수 조회
    stmt = select(func.count()).where(
        Diary.user_id == current_user.id,
        Diary.date >= start_date,
        Diary.date <= end_date,
        Diary.analyzed_emotion.in_(negative_emotions),
    )
    negative_emotion_count = db_session.execute(stmt).scalar_one_or_none() or 0
    negative_emotion_ratio = negative_emotion_count / total_diaries_count
    if (
        negative_emotion_ratio < 0.3
        or total_diaries_count == 0
        or date.today().weekday() == 0
    ):
        return MindContentRecommendationResponse.from_mind_content_type(
            mind_content_type=MindContentType.from_level(1)
        )
    elif negative_emotion_ratio < 0.5:
        return MindContentRecommendationResponse.from_mind_content_type(
            MindContentType.from_level(2)
        )
    else:
        return MindContentRecommendationResponse.from_mind_content_type(
            MindContentType.from_level(3)
        )


@router.post(
    "/{diary_id}/mind-contents",
    summary="마음챙김 콘텐츠 저장",
    description="해당 일기에 대한 마음챙김 콘텐츠를 저장합니다. 일기 작성자가 아닌 경우, 권한 오류를 반환합니다.",
)
def create_mind_content(
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
    mind_content_create_request: MindContentCreateRequest,
):
    diary = get_model_or_403(
        model_pk=diary_id,
        db_session=db_session,
        user_id=current_user.id,
        model_class=Diary,
    )

    content = (
        mind_content_create_request.level_1_content.model_dump_json()
        if mind_content_create_request.level == 1
        else (
            mind_content_create_request.level_2_content.model_dump_json()
            if mind_content_create_request.level == 2
            else mind_content_create_request.level_3_content.model_dump_json()
        )
    )

    stmt = select(MindContent).where(
        MindContent.diary_id == diary.id,
    )
    existing_mind_content = db_session.execute(stmt).scalar_one_or_none()
    if existing_mind_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해당 일기에 대한 마음챙김 콘텐츠가 존재합니다.",
        )

    mind_content = MindContent(
        diary_id=diary.id,
        level=mind_content_create_request.level,
        content=content,
    )
    db_session.add(mind_content)
    db_session.commit()
    db_session.refresh(mind_content)

    import json

    return json.loads(mind_content.content)


@router.get(
    "/{diary_id}/mind-contents",
    summary="마음챙김 콘텐츠 상세조회",
    description="해당 일기에 대한 마음챙김 콘텐츠를 저장합니다. 일기 작성자가 아닌 경우, 권한 오류를 반환합니다.",
)
def read_mind_content(
    diary_id: int,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    diary = get_model_or_403(
        model_pk=diary_id,
        db_session=db_session,
        user_id=current_user.id,
        model_class=Diary,
    )

    stmt = select(MindContent).where(
        MindContent.diary_id == diary.id,
    )
    mind_content = db_session.execute(stmt).scalar_one_or_none()
    if not mind_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 일기에 대한 마음챙김 콘텐츠가 존재하지 않습니다.",
        )

    return json.loads(mind_content.content)
