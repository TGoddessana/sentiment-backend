from enum import Enum
from typing import Dict, Any


class Emotion(Enum):
    NEUTRAL = (
        "평온",
        "😐",
        "오늘은 평온한 하루네요. 가끔은 이런 날도 필요한 것 같아요.",
    )
    HAPPY = (
        "행복",
        "😊",
        "오늘은 행복한 하루네요! 기분 좋은 일이 가득하길 바라요.",
    )
    SAD = (
        "슬픔",
        "🥲",
        "마음이 조금 무거운 하루예요. 괜찮아요, 이런 날도 있어요. 잠시 쉬어가는 것도 좋아요.",
    )
    ANXIOUS = (
        "불안",
        "😳",
        "뭔가 불안하고 걱정되는 기분이네요. 호흡을 가다듬고 천천히 생각해봐요. 당신은 잘하고 있어요.",
    )
    ANGRY = (
        "분노",
        "😠",
        "화가 나는 일이 있었군요. 감정을 억누르기보다 잘 다스려보세요. 마음이 조금은 편해질 거예요.",
    )
    TIRED = (
        "피곤",
        "😩",
        "오늘 많이 지치셨군요. 푹 쉬고 내일을 위한 에너지를 충전해보세요.",
    )
    LONELY = (
        "외로움",
        "😔",
        "혼자라고 느껴질 수 있어요. 당신의 존재는 소중하고, 누군가는 당신을 생각하고 있어요.",
    )
    BORED = (
        "지루함",
        "😑",
        "뭔가 심심한 하루였나요? 작은 변화로도 기분이 바뀔 수 있어요. 새로운 걸 시도해보는 건 어때요?",
    )
    REGRETFUL = (
        "후회",
        "😞",
        "되돌리고 싶은 일이 있나요? 누구나 실수해요. 중요한 건 그걸 통해 배우는 거예요.",
    )
    HOPEFUL = (
        "희망",
        "🤩",
        "그런 긍정적인 마음이 큰 힘이 돼요! 당신에게 큰 행운이 따르길 바라요.",
    )
    JEALOUS = (
        "질투",
        "😒",
        "누군가를 부러워할 수 있어요. 그 감정도 자연스러운 거예요. 당신의 속도대로 가도 괜찮아요.",
    )
    CONFUSED = (
        "혼란",
        "🤯",
        "생각이 많아지는 하루였나 봐요. 너무 서두르지 말고, 천천히 정리해보세요.",
    )
    EMBARRASSED = (
        "당황",
        "😳",
        "조금 부끄러운 일이 있었나요? 누구나 그런 순간이 있어요. 너무 오래 붙잡지 마세요.",
    )

    def __init__(self, korean_name: str, emoji: str, message: str):
        self.korean_name = korean_name
        self.emoji = emoji
        self.message = message

    @classmethod
    def from_name(cls, name: str) -> "Emotion":
        for emotion in cls:
            if emotion.name == name:
                return emotion
        raise ValueError(f"Invalid emotion code: {name}")

    @property
    def value_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "korean_name": self.korean_name,
            "emoji": self.emoji,
            "message": self.message,
        }


class MindContentType(Enum):
    MEDITATION = (1, "명상")
    CAUSE_ANALYSIS = (2, "원인 분석")
    SELF_PRAISE = (3, "자기 칭찬")

    def __init__(self, level, korean_name):
        self.level = level
        self.korean_name = korean_name
