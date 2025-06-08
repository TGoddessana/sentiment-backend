import datetime

from fastapi import APIRouter
from sqlalchemy import select

from application.constants import Emotion
from application.models import Diary, WeeklyReport
from application.ai import (
    analyze_diary_emotion,
    analyze_weekly_emotions,
)
from application.schemas import WeeklyReportRequest, MonthlyReportRequest
from config.dependencies import SessionDependency, CurrentUser

router = APIRouter()


@router.post(
    "/diary-mood/{diary_id}",
    summary="일기 감정 분석",
    description="일기의 아이디를 받아 해당 일기의 감정을 분석하는 API입니다.",
)
def analyze_mood(diary_id: int, db_session: SessionDependency):
    diary: Diary = db_session.query(Diary).get(diary_id)

    if diary.analyzed_emotion:
        emotion = diary.get_analyzed_emotion_enum()
        return {
            "name": emotion.name,
            "korean_name": emotion.korean_name,
            "emoji": emotion.emoji,
            "message": emotion.message,
        }

    analyzed_emotion: Emotion = analyze_diary_emotion(diary.content)
    diary.analyze_emotion(analyzed_emotion)

    return {
        "name": analyzed_emotion.name,
        "korean_name": analyzed_emotion.korean_name,
        "emoji": analyzed_emotion.emoji,
        "message": analyzed_emotion.message,
    }


@router.post(
    "/monthly-report",
    summary="월간 감정 분석",
    description="월간 감정 분석을 위한 API입니다. 4주치 감정 데이터와 주간 조언을 받아 종합적인 월간 리포트를 생성합니다.",
)
def analyze_monthly(
    monthly_report_request: MonthlyReportRequest,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    # 시작 날짜, 끝 날짜까지 일기 불러오기
    stmt = select(Diary).where(
        Diary.user_id == current_user.id,
        Diary.date >= monthly_report_request.start_date,
        Diary.date <= monthly_report_request.end_date,
    )
    diaries = db_session.execute(stmt).scalars().all()

    # 날짜: 감정 형태로 변환, 감정이 없을 경우 None으로 설정, 일기가 작성되지 않은 경우에도 날짜는 포함
    # {
    #     "week_1":
    #         ["null, "불안", "행복", "슬픔", "행복", "행복", "행복"],
    #     "week_2":
    #         ["행복", "행복", "행복", "행복", "행복", "행복", "행복"],
    #     // .. 4 혹은 "5주차"까지
    # }

    emotions = {}
    _start_date = monthly_report_request.start_date
    _end_date = monthly_report_request.end_date
    _week_number = 1
    _total_week = _start_date.isocalendar()[1] - _start_date.isocalendar()[1] + 1
    print(_start_date.isocalendar(), _end_date.isocalendar())
    print(f"Total weeks: {_total_week}")

    return emotions

    # 이미 월간 리포트가 존재하는지 확인
    # stmt = select(WeeklyReport).where(
    #     WeeklyReport.user_id == current_user.id,
    #     WeeklyReport.start_date == monthly_report_request.start_date,
    #     WeeklyReport.end_date == monthly_report_request.end_date,
    # )
    # existing_report = db_session.execute(stmt).scalar_one_or_none()
    # if existing_report:
    #     return {
    #         "start_date": existing_report.start_date,
    #         "end_date": existing_report.end_date,
    #         "emotion_timeline": emotion_timeline,
    #         "advice": existing_report.advice,
    #     }

    # weekly_reports = (
    #     db_session.query(WeeklyReport)
    #     .filter(
    #         WeeklyReport.user_id == current_user.id,
    #         WeeklyReport.start_date >= monthly_report_request.start_date,
    #         WeeklyReport.end_date <= monthly_report_request.end_date,
    #     )
    #     .all()
    # )
    #
    # # advice_list = [report.advice for report in weekly_reports]
    #
    # monthly_report = WeeklyReport(
    #     user_id=current_user.id,
    #     start_date=monthly_report_request.start_date,
    #     end_date=monthly_report_request.end_date,
    #     advice=analyze_weekly_emotions(emotion_timeline),
    # )
    # db_session.add(monthly_report)
    # db_session.commit()

    return {}


@router.post(
    "/weekly-report",
    summary="주간 감정 분석",
    description="주간 감정 분석을 위한 API입니다. 일주일 동안의 감정 데이터를 받아 종합적인 주간 리포트를 생성합니다.",
)
def analyze_weekly(
    weekly_report_request: WeeklyReportRequest,
    current_user: CurrentUser,
    db_session: SessionDependency,
):
    # 시작 날짜, 끝 날짜까지 일기 불러오기
    stmt = select(Diary).where(
        Diary.user_id == current_user.id,
        Diary.date >= weekly_report_request.start_date,
        Diary.date <= weekly_report_request.end_date,
    )
    diaries = db_session.execute(stmt).scalars().all()

    # 날짜: 감정 형태로 변환, 감정이 없을 경우 None으로 설정, 일기가 작성되지 않은 경우에도 날짜는 포함
    # 스파게티 코드 ...
    # "emotion_timeline": {
    #     "2025-06-02": null,
    #     "2025-06-03": null,
    #     "2025-06-04": null,
    #     "2025-06-05": null,
    #     "2025-06-06": null,
    #     "2025-06-07": "불안",
    #     "2025-06-08": null
    #   },
    emotion_timeline = {}
    _start_date, _end_date = (
        weekly_report_request.start_date,
        weekly_report_request.end_date,
    )
    while _start_date <= _end_date:
        emotion_timeline[_start_date] = None
        _start_date = _start_date + datetime.timedelta(days=1)

    for diary in diaries:
        emotion = diary.get_analyzed_emotion_enum()
        emotion_timeline[diary.date] = emotion.korean_name if emotion else None

    # 이미 주간 리포트가 존재하는지 확인
    stmt = select(WeeklyReport).where(
        WeeklyReport.user_id == current_user.id,
        WeeklyReport.start_date == weekly_report_request.start_date,
        WeeklyReport.end_date == weekly_report_request.end_date,
    )
    existing_report = db_session.execute(stmt).scalar_one_or_none()
    if existing_report:
        return {
            "start_date": existing_report.start_date,
            "end_date": existing_report.end_date,
            "emotion_timeline": emotion_timeline,
            "advice": existing_report.advice,
        }

    weekly_report = WeeklyReport(
        user_id=current_user.id,
        start_date=weekly_report_request.start_date,
        end_date=weekly_report_request.end_date,
        advice=analyze_weekly_emotions(emotion_timeline),
    )
    db_session.add(weekly_report)
    db_session.commit()

    return {
        "start_date": weekly_report.start_date,
        "end_date": weekly_report.end_date,
        "emotion_timeline": emotion_timeline,
        "advice": weekly_report.advice,
    }
