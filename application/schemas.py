from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
import re
from application.models import Diary


class UserCreateInput(BaseModel):
    login_id: str
    password: str
    nickname: str


class LoginInput(BaseModel):
    login_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class DiaryCreateInput(BaseModel):
    weather: str = Field(..., description="날씨")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="일기 본문")
    image_urls: Optional[List[str]] = Field(
        default=[], description="첨부 이미지 URL들 (최대 5장)"
    )

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("이미지는 최대 5개까지만 첨부할 수 있습니다.")
        return v


class AnalyzedEmotion(BaseModel):
    name: str
    korean_name: str
    emoji: str
    message: str


class DiaryResponse(BaseModel):
    id: int
    user_id: int
    weather: str
    title: str
    content: str
    image_urls: list[str]
    created_at: datetime
    updated_at: datetime

    analyzed_emotion: AnalyzedEmotion | None = None

    @classmethod
    def from_diary(cls, diary: Diary) -> "DiaryResponse":
        return cls(
            id=diary.id,
            user_id=diary.user_id,
            weather=diary.weather,
            title=diary.title,
            content=diary.content,
            image_urls=diary.image_urls,
            created_at=diary.created_at,
            updated_at=diary.updated_at,
            analyzed_emotion=(
                AnalyzedEmotion(
                    name=(
                        diary.get_analyzed_emotion_enum().name
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    korean_name=(
                        diary.get_analyzed_emotion_enum().korean_name
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    emoji=(
                        diary.get_analyzed_emotion_enum().emoji
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    message=(
                        diary.get_analyzed_emotion_enum().message
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                )
                if diary.get_analyzed_emotion_enum()
                else None
            ),
        )

    @property
    class Config:
        from_attributes = True


class DiaryContent(BaseModel):
    content: str


class WeeklySummary(BaseModel):
    week_number: int
    summary: str


class MonthlyAnalysis(BaseModel):
    weekly_emotions: list
    weekly_summaries: list[WeeklySummary]  # 4주치 주간 조언
