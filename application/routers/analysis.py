from fastapi import APIRouter
from pydantic import BaseModel, Field

from application.constants import Emotion
from application.models import Diary
from application.ai import analyze_diary_content, client
from application.schemas import MonthlyAnalysis
from config.dependencies import SessionDependency

router = APIRouter()


@router.post(
    "/diary-mood/{diary_id}",
    description="일기의 아이디를 받아 해당 일기의 감정을 분석하는 API입니다.",
)
def analyze_mood(diary_id: int, db_session: SessionDependency):

    diary: Diary = db_session.query(Diary).get(diary_id)
    analyzed_emotion: Emotion = analyze_diary_content(diary.content)
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


class WeeklyEmotionTimeline(BaseModel):
    monday: str = Field(description="월요일의 감정")
    tuesday: str = Field(description="화요일의 감정")
    wednesday: str = Field(description="수요일의 감정")
    thursday: str = Field(description="목요일의 감정")
    friday: str = Field(description="금요일의 감정")
    saturday: str = Field(description="토요일의 감정")
    sunday: str = Field(description="일요일의 감정")


def analyze_weekly_content(weekly_emotions: WeeklyEmotionTimeline):
    emotion_timeline = {
        "월요일": Emotion.from_name(weekly_emotions.monday),
        "화요일": Emotion.from_name(weekly_emotions.tuesday),
        "수요일": Emotion.from_name(weekly_emotions.wednesday),
        "목요일": Emotion.from_name(weekly_emotions.thursday),
        "금요일": Emotion.from_name(weekly_emotions.friday),
        "토요일": Emotion.from_name(weekly_emotions.saturday),
        "일요일": Emotion.from_name(weekly_emotions.sunday),
    }

    prompt = f"""
    사용자의 지난 일주일 동안의 감정 변화를 분석하고, **부드럽고 자연스러운 흐름으로 3문장으로 요약하여 조언을 제공하세요.**

    📌 **감정 변화 데이터:**  
    {", ".join(
        [f"{day}: {emotion}" for day, emotion in emotion_timeline.items()]
    )}

    📌 **가이드라인:**  
    - 감정의 흐름을 분석하여 사용자가 한 주 동안 어떻게 느꼈는지 서사적으로 표현하세요.  
    - 감정을 나열하는 방식이 아니라, 감정의 변화가 자연스럽게 연결되도록 표현하세요.  
    - 행복이 많다면, 따뜻한 응원을 보내고, 힘든 감정이 많다면 부드럽게 위로해 주세요.  
    - 감정을 평가하지 말고, 사용자가 자신의 감정을 자연스럽게 받아들일 수 있도록 돕는 톤을 유지하세요.  

    📌 **출력 형식:**  
    - **딱 3문장만 작성하세요.**  
    - 감정이 단순히 나열되지 않고, 자연스럽게 흐르도록 서술하세요.  
    - 감정을 받아들이는 방법을 부드럽게 제시하세요.  
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "당신은 주간 감정 패턴을 분석하고 조언을 제공하는 전문가입니다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=300,
    )
    result = response.choices[0].message.content.strip()

    return {"weekly_analysis": result}


@router.post(
    "/weekly-report",
    description="주간 감정 분석을 위한 API입니다. 일주일 동안의 감정 데이터를 받아 종합적인 주간 리포트를 생성합니다.",
)
async def analyze_weekly(emotions: WeeklyEmotionTimeline):
    result = analyze_weekly_content(emotions)
    return result
