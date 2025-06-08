import json
from textwrap import dedent

from openai import OpenAI

from application.constants import Emotion
from config.settings import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def analyze_diary_emotion(diary_content: str) -> Emotion:
    prompt = dedent(
        f"""다음 일기 내용을 분석하여 감정을 분류해주세요. 감정은 다음 5가지 중 하나로 분류해주세요.
        
            - NEUTRAL
            - HAPPY
            - SAD
            - ANXIOUS
            - ANGRY
            - TIRED
            - LONELY
            - BORED
            - REGRETFUL
            - HOPEFUL
            - JEALOUS
            - CONFUSED
            - EMBARRASSED
        
            일기 내용:
            "{diary_content}"
            
            응답 형식:
            - 감정의 이름 (예: NEUTRAL, HAPPY 등)
    """
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "당신은 일기의 감정을 분석하는 전문가입니다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=150,
    )

    result = response.choices[0].message.content.strip()
    return Emotion.from_name(result)


def analyze_weekly_emotions(weekly_emotions: dict[str, str]) -> str:
    prompt = dedent(
        f"""
        사용자의 지난 일주일 동안의 감정 변화를 분석하고, **부드럽고 자연스러운 흐름으로 3문장으로 요약하여 조언을 제공하세요.**
    
        📌 **감정 변화 데이터:**  
        {", ".join(
            [f"{day}: {emotion}" for day, emotion in weekly_emotions.items()]
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
    )
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
    return result


# def analyze_monthly_content(monthly_emotions: dict[str, str]):
#     prompt = dedent(
#         f"""
#         한 달 동안의 감정 데이터와 주간 조언들을 종합적으로 분석하여 월간 리포트를 작성해주세요.
#
#         📌 **주차별 감정 데이터:**
#         {weekly_emotions_list}
#
#         📌 **주간 조언 요약:**
#         {weekly_summaries}
#
#         📌 **가이드라인:**
#         - 한 달 동안의 감정 변화 패턴을 분석해주세요.
#         - 주간 조언들을 참고하여 전체적인 감정 흐름을 파악해주세요.
#         - 가장 많이 나타난 감정과 그 의미를 설명해주세요.
#         - 한 달 동안의 감정 변화를 바탕으로 종합적인 조언을 제공해주세요.
#
#         📌 **출력 형식:**
#         1. 월간 감정 패턴: [한 달 동안의 감정 변화 패턴 설명]
#         2. 주요 감정: [가장 많이 나타난 감정과 그 의미]
#         3. 종합 조언: [이번 달의 감정을 바탕으로 한 종합적인 조언]
#         """
#     )
#
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "당신은 월간 감정 패턴을 분석하고 종합적인 조언을 제공하는 전문가입니다.",
#             },
#             {
#                 "role": "user",
#                 "content": prompt,
#             },
#         ],
#         temperature=0.7,
#         max_tokens=500,
#     )
#     result = response.choices[0].message.content.strip()
#
#     lines = result.split("\n")
#     monthly_pattern = lines[0].split(":")[1].strip()
#     main_emotion = lines[1].split(":")[1].strip()
#     comprehensive_advice = lines[2].split(":")[1].strip()
#
#     return {
#         "monthly_pattern": monthly_pattern,
#         "main_emotion": main_emotion,
#         "comprehensive_advice": comprehensive_advice,
#         "weekly_emotions": weekly_emotions_list,
#         "weekly_summaries": weekly_summaries,
#     }
