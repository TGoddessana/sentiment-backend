from enum import Enum
from typing import Dict, Any


class Emotion(Enum):
    NEUTRAL = (
        "중립",
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
        "😢",
        "마음이 조금 무거운 하루예요. 괜찮아요, 이런 날도 있어요. 잠시 쉬어가는 것도 좋아요.",
    )
    ANXIOUS = (
        "불안",
        "😰",
        "뭔가 불안하고 걱정되는 기분이네요. 호흡을 가다듬고 천천히 생각해봐요.당신은 잘하고 있어요.",
    )
    ANGRY = (
        "분노",
        "😠",
        "화가 나는 일이 있었군요.감정을 억누르기보다 잘 다스려보세요. 마음이 조금은 편해질 거예요.",
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
