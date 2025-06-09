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
    # 레벨 1
    BREATHING_MEDITATION = (
        1,
        "호흡 명상",
        [
            "허리를 세우고 편한 자세를 갖춘 후 눈을 감은 채 호흡에 집중합니다. 다른 생각은 하지 말고 숨이 어떻게 나가고 들어오게 되는지에 집중해 보세요."
        ],
    )
    SELF_COMPASSION_MEDITATION = (
        1,
        "자기연민 명상",
        [
            "명상은 나를 다정히 안아주는 연습입니다. 스스로에게 따뜻하고 친절한 말을 반복하며 자신을 위로해주세요. “괜찮아, 실수할 수 있어"
        ],
    )
    MANTRA_MEDITATION = (
        1,
        "만트라 명상",
        [
            '명상은 마음의 소음을 잠재우는 주문입니다. 일정한 소리, 단어나 문장을 반복하며 집중을 유지해보세요 "옴(Om)", "나는 평화롭다."'
        ],
    )

    # 레벨 2
    CAUSE_ANALYSIS = (
        2,
        "부정적인 감정의 원인에 대한 고찰",
        [
            "문제를 감정 없이 명확히 적는다.",
            '표면적 원인과 근본 원인을 "왜?"를 반복해 파악한다.'
            "외부·내부 영향 요인을 정리한다.",
            "비슷한 사례가 있었는지 패턴을 찾아본다.",
            "핵심 원인 2~3개로 요약하고, 내 관점에서 성찰한다.",
        ],
    )

    # 레벨 3
    SELF_PRAISE = (
        3,
        "자기 칭찬",
        ["오늘 하루 감사했던 일을 3가지 작성해 보세요."],
    )

    def __init__(self, level, korean_name, instruction: list[str]):
        self.level = level
        self.korean_name = korean_name
        self.instruction = instruction

    @classmethod
    def from_level(cls, level: int) -> "MindContentType":
        import random

        if level == 1:
            candidates = [
                cls.BREATHING_MEDITATION,
                cls.SELF_COMPASSION_MEDITATION,
                cls.MANTRA_MEDITATION,
            ]
            return random.choice(candidates)
        for item in cls:
            if item.level == level:
                return item
        raise ValueError(f"해당 레벨의 MindContentType이 없습니다: {level}")
