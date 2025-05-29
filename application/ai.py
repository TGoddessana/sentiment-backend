import json
from textwrap import dedent

from openai import OpenAI

from application.constants import Emotion
from config.settings import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def analyze_diary_content(diary_content) -> Emotion:
    prompt = dedent(
        f"""다음 일기 내용을 분석하여 감정을 분류해주세요. 감정은 다음 5가지 중 하나로 분류해주세요.
            - NEUTRAL
            - HAPPY
            - SAD
            - ANXIOUS
            - ANGRY
        
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
