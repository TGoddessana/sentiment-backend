import datetime

from fastapi import APIRouter
from sqlalchemy import select

from application.constants import Emotion
from application.models import Diary, WeeklyReport
from application.ai import analyze_diary_emotion, client, analyze_weekly_emotions
from application.schemas import MonthlyAnalysis, WeeklyReportRequest
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


def analyze_monthly_content(monthly_data: MonthlyAnalysis):
    # 주차별 감정 데이터 변환
    weekly_emotions_list = []
    for week_emotions in monthly_data.weekly_emotions:
        week_dict = {
            "월요일": f"{Emotion.from_name(week_emotions.monday).name} {Emotion.from_name(week_emotions.monday).emoji}",
            "화요일": f"{Emotion.from_name(week_emotions.tuesday).name} {Emotion.from_name(week_emotions.tuesday).emoji}",
            "수요일": f"{Emotion.from_name(week_emotions.wednesday).name} {Emotion.from_name(week_emotions.wednesday).emoji}",
            "목요일": f"{Emotion.from_name(week_emotions.thursday).name} {Emotion.from_name(week_emotions.thursday).emoji}",
            "금요일": f"{Emotion.from_name(week_emotions.friday).name} {Emotion.from_name(week_emotions.friday).emoji}",
            "토요일": f"{Emotion.from_name(week_emotions.saturday).name} {Emotion.from_name(week_emotions.saturday).emoji}",
            "일요일": f"{Emotion.from_name(week_emotions.sunday).name} {Emotion.from_name(week_emotions.sunday).emoji}",
        }
        weekly_emotions_list.append(week_dict)

    # 주간 조언 데이터 변환
    weekly_summaries = [summary.summary for summary in monthly_data.weekly_summaries]

    prompt = f"""
    한 달 동안의 감정 데이터와 주간 조언들을 종합적으로 분석하여 월간 리포트를 작성해주세요.

    📌 **주차별 감정 데이터:**
    {weekly_emotions_list}

    📌 **주간 조언 요약:**
    {weekly_summaries}

    📌 **가이드라인:**
    - 한 달 동안의 감정 변화 패턴을 분석해주세요.
    - 주간 조언들을 참고하여 전체적인 감정 흐름을 파악해주세요.
    - 가장 많이 나타난 감정과 그 의미를 설명해주세요.
    - 한 달 동안의 감정 변화를 바탕으로 종합적인 조언을 제공해주세요.

    📌 **출력 형식:**
    1. 월간 감정 패턴: [한 달 동안의 감정 변화 패턴 설명]
    2. 주요 감정: [가장 많이 나타난 감정과 그 의미]
    3. 종합 조언: [이번 달의 감정을 바탕으로 한 종합적인 조언]
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "당신은 월간 감정 패턴을 분석하고 종합적인 조언을 제공하는 전문가입니다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=500,
    )
    result = response.choices[0].message.content.strip()

    lines = result.split("\n")
    monthly_pattern = lines[0].split(":")[1].strip()
    main_emotion = lines[1].split(":")[1].strip()
    comprehensive_advice = lines[2].split(":")[1].strip()

    return {
        "monthly_pattern": monthly_pattern,
        "main_emotion": main_emotion,
        "comprehensive_advice": comprehensive_advice,
        "weekly_emotions": weekly_emotions_list,
        "weekly_summaries": weekly_summaries,
    }


@router.post(
    "/monthly-report",
    description="월간 감정 분석을 위한 API입니다. 4주치 감정 데이터와 주간 조언을 받아 종합적인 월간 리포트를 생성합니다.",
)
def analyze_monthly(monthly_data: MonthlyAnalysis):
    result = analyze_monthly_content(monthly_data)
    return result


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
        if diary.date.strftime("%Y-%m-%d") in emotion_timeline:
            emotion_timeline[diary.date.strftime("%Y-%m-%d")] = (
                diary.get_analyzed_emotion_enum().korean_name
                if diary.get_analyzed_emotion_enum()
                else None
            )

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
